#!/bin/bash

set -e

# CONFIG - make sure this matches your install script
REPO_DIR="$HOME/.Python-IDE"
STARTER_LINK="/usr/local/bin/Python-IDE"

echo "Uninstalling MyApp..."

# Remove symlink
if [ -L "$STARTER_LINK" ]; then
    echo "Removing launcher symlink at $STARTER_LINK"
    sudo rm "$STARTER_LINK"
fi

# Remove repo directory
if [ -d "$REPO_DIR" ]; then
    echo "Deleting installed files at $REPO_DIR"
    rm -rf "$REPO_DIR"
fi

echo "Uninstallation complete."
