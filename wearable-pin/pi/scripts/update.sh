#!/bin/bash
#
# Auto-update script for Raspberry Pi wearable-pin project
# Pulls latest code from GitHub and restarts service if changes detected
#

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Find git repository root by going up from script directory
REPO_DIR="$SCRIPT_DIR"
while [ "$REPO_DIR" != "/" ] && [ ! -d "$REPO_DIR/.git" ]; do
    REPO_DIR="$(dirname "$REPO_DIR")"
done

SERVICE_NAME="camera.service"
BRANCH="main"
LOG_TAG="wearable-pin-update"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | systemd-cat -t "$LOG_TAG" -p info
    echo "$1"
}

log_error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1" | systemd-cat -t "$LOG_TAG" -p err
    echo "ERROR: $1" >&2
}

# Change to repository directory
cd "$REPO_DIR" || {
    log_error "Failed to change to repository directory: $REPO_DIR"
    exit 1
}

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    log_error "Not a git repository: $REPO_DIR"
    exit 1
fi

# Get current commit hash before pull
OLD_COMMIT=$(git rev-parse HEAD)

# Fetch latest changes
log "Fetching latest changes from origin..."
if ! git fetch origin "$BRANCH" 2>&1 | while IFS= read -r line; do log "$line"; done; then
    log_error "Failed to fetch from origin"
    exit 1
fi

# Check if there are updates
if [ "$OLD_COMMIT" = "$(git rev-parse origin/$BRANCH)" ]; then
    log "No updates available. Already at latest commit."
    exit 0
fi

# Pull latest changes
log "Pulling latest changes..."
if ! git pull origin "$BRANCH" 2>&1 | while IFS= read -r line; do log "$line"; done; then
    log_error "Failed to pull from origin"
    exit 1
fi

# Get new commit hash
NEW_COMMIT=$(git rev-parse HEAD)
log "Updated from $OLD_COMMIT to $NEW_COMMIT"

# Check if camera service is running and restart it
if systemctl is-active --quiet "$SERVICE_NAME"; then
    log "Restarting $SERVICE_NAME..."
    if systemctl restart "$SERVICE_NAME"; then
        log "Successfully restarted $SERVICE_NAME"
    else
        log_error "Failed to restart $SERVICE_NAME"
        exit 1
    fi
elif systemctl is-enabled --quiet "$SERVICE_NAME"; then
    log "$SERVICE_NAME is enabled but not running. Starting it..."
    if systemctl start "$SERVICE_NAME"; then
        log "Successfully started $SERVICE_NAME"
    else
        log_error "Failed to start $SERVICE_NAME"
        exit 1
    fi
else
    log "$SERVICE_NAME is not enabled. Skipping service restart."
fi

log "Update completed successfully"

