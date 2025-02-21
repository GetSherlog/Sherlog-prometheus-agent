#!/bin/bash

# Colors for output
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${RED}Stopping Sherlog Demo...${NC}"

# Stop the frontend
echo -e "${RED}Stopping Next.js frontend...${NC}"
pkill -f "next"

# Stop the demo stack
echo -e "${RED}Stopping demo stack...${NC}"
cd app/demo
docker-compose down

echo -e "${RED}Demo stopped successfully!${NC}" 