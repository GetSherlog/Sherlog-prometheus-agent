#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Setting up Sherlog development environment...${NC}"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${BLUE}Creating Python virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
echo -e "${BLUE}Installing Python dependencies...${NC}"
pip install -r requirements.txt

# Install frontend dependencies
echo -e "${BLUE}Installing frontend dependencies...${NC}"
cd frontend
npm install

# Create uploads directory if it doesn't exist
mkdir -p uploads

# Create .env.local if it doesn't exist
if [ ! -f .env.local ]; then
    echo -e "${BLUE}Creating frontend .env.local...${NC}"
    echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
fi

cd ..

echo -e "${GREEN}Setup complete!${NC}"
echo -e "${BLUE}To start the development servers:${NC}"
echo -e "1. In one terminal: ${GREEN}source venv/bin/activate && python -m uvicorn app.main:app --reload${NC}"
echo -e "2. In another terminal: ${GREEN}cd frontend && npm run dev${NC}" 