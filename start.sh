#!/bin/bash

# Start script for The Ghost Hunter Fork
# This script builds the story and starts a local development server

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting development server...${NC}"

# Build the story first
echo -e "${YELLOW}Building story...${NC}"
if ! ./build.sh; then
    echo -e "${RED}Error: Build failed. Server not started.${NC}"
    exit 1
fi

# Check if serve is available
if command -v serve >/dev/null 2>&1; then
    echo -e "${GREEN}Starting local server...${NC}"
    echo -e "${YELLOW}Open http://localhost:3000 in your browser${NC}"
    serve -l 3000 tgh-fork.html
elif command -v python3 >/dev/null 2>&1; then
    echo -e "${GREEN}Starting Python HTTP server...${NC}"
    echo -e "${YELLOW}Open http://localhost:8000 in your browser${NC}"
    python3 -m http.server 8000
elif command -v php >/dev/null 2>&1; then
    echo -e "${GREEN}Starting PHP development server...${NC}"
    echo -e "${YELLOW}Open http://localhost:8000 in your browser${NC}"
    php -S localhost:8000
else
    echo -e "${RED}Error: No HTTP server found (serve, python3, python, or php)${NC}"
    echo -e "${YELLOW}Please install one of the following:${NC}"
    echo -e "${YELLOW}  npm install -g serve${NC}"
    echo -e "${YELLOW}  python3 -m http.server${NC}"
    echo -e "${YELLOW}  php -S localhost:8000${NC}"
    exit 1
fi
