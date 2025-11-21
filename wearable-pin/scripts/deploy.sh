#!/bin/bash
#
# Deployment script for Mac - pushes code to GitHub
# Optionally triggers immediate update on Raspberry Pi via SSH
#

set -e

# Configuration
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BRANCH="main"
PI_HOST="${PI_HOST:-raspberrypi.local}"
PI_USER="${PI_USER:-pi}"
SSH_KEY="${SSH_KEY:-}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Change to repository directory
cd "$REPO_DIR" || {
    echo -e "${RED}ERROR: Failed to change to repository directory${NC}"
    exit 1
}

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}ERROR: Not a git repository${NC}"
    exit 1
fi

# Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo -e "${YELLOW}Warning: You have uncommitted changes${NC}"
    git status --short
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Get commit message
if [ -z "$1" ]; then
    read -p "Enter commit message: " COMMIT_MSG
else
    COMMIT_MSG="$1"
fi

if [ -z "$COMMIT_MSG" ]; then
    COMMIT_MSG="Auto-deploy: $(date '+%Y-%m-%d %H:%M:%S')"
fi

# Stage all changes
echo -e "${GREEN}Staging changes...${NC}"
git add -A

# Check if there are changes to commit
if git diff --staged --quiet; then
    echo -e "${YELLOW}No changes to commit${NC}"
else
    # Commit changes
    echo -e "${GREEN}Committing changes...${NC}"
    git commit -m "$COMMIT_MSG"
fi

# Push to GitHub
echo -e "${GREEN}Pushing to GitHub...${NC}"
if git push origin "$BRANCH"; then
    echo -e "${GREEN}Successfully pushed to GitHub${NC}"
else
    echo -e "${RED}ERROR: Failed to push to GitHub${NC}"
    exit 1
fi

# Ask if user wants to trigger immediate update on Pi
echo ""
read -p "Trigger immediate update on Raspberry Pi? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Build SSH command
    SSH_CMD="ssh"
    if [ -n "$SSH_KEY" ]; then
        SSH_CMD="$SSH_CMD -i $SSH_KEY"
    fi
    SSH_CMD="$SSH_CMD $PI_USER@$PI_HOST"
    
    echo -e "${GREEN}Triggering update on Raspberry Pi...${NC}"
    if $SSH_CMD "sudo systemctl start update.service"; then
        echo -e "${GREEN}Update triggered successfully${NC}"
        echo "Check logs with: ssh $PI_USER@$PI_HOST 'sudo journalctl -u update.service -n 20'"
    else
        echo -e "${YELLOW}Warning: Failed to trigger update on Pi${NC}"
        echo "Pi will pick up changes on next scheduled update (every 2 minutes)"
    fi
else
    echo "Pi will pick up changes on next scheduled update (every 2 minutes)"
fi

echo ""
echo -e "${GREEN}Deployment completed!${NC}"

