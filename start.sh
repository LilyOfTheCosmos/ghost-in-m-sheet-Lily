#!/bin/bash

# Start script for Ghost in M'Sheet
# This script builds the story and opens it in the default browser

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

OUTPUT_FILE="ghost-in-msheet.html"
STORY_INIT="passages/StoryInit.tw"

# Optional first argument: override the ImagePath used by the story.
# When provided, temporarily rewrite StoryInit.tw and restore it on exit.
IMAGE_PATH_OVERRIDE="${1:-}"
if [ -n "$IMAGE_PATH_OVERRIDE" ]; then
    if [ ! -f "$STORY_INIT" ]; then
        echo -e "${RED}Error: $STORY_INIT not found; cannot override ImagePath.${NC}"
        exit 1
    fi
    cp "$STORY_INIT" "$STORY_INIT.bak"
    trap 'mv "$STORY_INIT.bak" "$STORY_INIT"' EXIT
    sed -i "s|setup.ImagePath = \"[^\"]*\"|setup.ImagePath = \"$IMAGE_PATH_OVERRIDE\"|" "$STORY_INIT"
    echo -e "${YELLOW}Using ImagePath override: $IMAGE_PATH_OVERRIDE${NC}"
fi

# Build the story first
echo -e "${YELLOW}Building story...${NC}"
if ! ./build.sh; then
    echo -e "${RED}Error: Build failed.${NC}"
    exit 1
fi

# Open the file in the default browser
echo -e "${GREEN}Opening $OUTPUT_FILE in browser...${NC}"
if command -v xdg-open >/dev/null 2>&1; then
    xdg-open "$SCRIPT_DIR/$OUTPUT_FILE"
elif command -v open >/dev/null 2>&1; then
    open "$SCRIPT_DIR/$OUTPUT_FILE"
else
    echo -e "${YELLOW}Could not detect a browser opener. Open this file manually:${NC}"
    echo -e "${YELLOW}  $SCRIPT_DIR/$OUTPUT_FILE${NC}"
fi
