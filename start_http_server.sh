#!/bin/bash
# Start script for Zettelkasten MCP HTTP Server

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting Zettelkasten MCP HTTP Server${NC}"
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${RED}❌ Virtual environment not found!${NC}"
    echo "Please run: uv venv && uv sync"
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found, creating from .env.example${NC}"
    cp .env.example .env
fi

# Activate virtual environment
echo -e "${GREEN}✓ Activating virtual environment${NC}"
source .venv/bin/activate

# Create data directories if they don't exist
echo -e "${GREEN}✓ Ensuring data directories exist${NC}"
mkdir -p data/notes data/db

# Start the server
echo -e "${GREEN}✓ Starting HTTP server${NC}"
echo ""
echo -e "${YELLOW}Server will be available at: http://127.0.0.1:8080${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
echo ""

python -m zettelkasten_mcp.http_server
