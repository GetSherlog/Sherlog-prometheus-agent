#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Starting Sherlog Demo...${NC}"

# Create necessary environment files
echo -e "${BLUE}Setting up environment files...${NC}"
if [ ! -f "frontend/.env.local" ]; then
    echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > frontend/.env.local
fi

# Start the demo stack in the background
echo -e "${BLUE}Starting demo stack (Prometheus, Loki, Grafana, etc.)...${NC}"
cd app/demo
docker-compose up --build -d

# Wait for services to be ready
echo -e "${BLUE}Waiting for services to be ready...${NC}"
sleep 10

# Start the frontend
echo -e "${BLUE}Starting Next.js frontend...${NC}"
cd ../../frontend
npm install
npm run dev &

# Wait for frontend to start
sleep 5

echo -e "${GREEN}🚀 Demo is ready! Access the following services:${NC}"
echo -e "${GREEN}📊 Main Dashboard: http://localhost:3000${NC}"
echo -e "${GREEN}🔍 Demo App: http://localhost:8000${NC}"
echo -e "${GREEN}📈 Grafana: http://localhost:3000 (login: admin/admin)${NC}"
echo -e "${GREEN}📊 Prometheus: http://localhost:9090${NC}"

echo -e "\n${BLUE}Example queries you can try:${NC}"
echo "- Show me the error rate in the last hour"
echo "- What's the current CPU and memory usage?"
echo "- Show me all failed orders in the last 30 minutes"
echo "- What's the average request latency by endpoint?"

echo -e "\n${BLUE}To stop the demo, run: ./stop_demo.sh${NC}" 