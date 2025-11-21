#!/bin/bash
#
# Quick deployment script - simplified one-command deployment
# Usage: ./quick-deploy.sh [commit-message]
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOY_SCRIPT="$SCRIPT_DIR/deploy.sh"

# If commit message provided as argument, pass it through
if [ -n "$1" ]; then
    "$DEPLOY_SCRIPT" "$1"
else
    "$DEPLOY_SCRIPT"
fi

