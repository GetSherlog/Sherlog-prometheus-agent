#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Setting up Sherlog Prometheus Agent Demo${NC}"
echo "----------------------------------------"

# Create .env file
echo -e "${GREEN}Creating .env file...${NC}"
cat > .env << EOL
# Choose your LLM provider
LLM_PROVIDER=openai  # Options: openai, ollama

# If using OpenAI
OPENAI_API_KEY=your-key-here

# If using Ollama (local LLM)
OLLAMA_HOST=http://localhost:11434

# Prometheus Configuration
# Use the local demo Prometheus by default
PROMETHEUS_URL=http://prometheus:9090

# For demo mode, we don't need real Slack credentials
SLACK_BOT_TOKEN=demo-mode
SLACK_APP_TOKEN=demo-mode

# Redis Configuration
REDIS_URL=redis://redis:6379/0

# Application Configuration
DEBUG=true
ENVIRONMENT=development
EOL

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo -e "${GREEN}Starting demo environment...${NC}"
docker-compose -f docker-compose.demo.yml up -d

echo -e "${BLUE}Demo environment is ready!${NC}"
echo "----------------------------------------"
echo "The following services are available:"
echo "- Sherlog API: http://localhost:8000"
echo "- Prometheus: http://localhost:9090"
echo "- Sample App: http://localhost:8080"
echo ""
echo "Sample queries you can try:"
echo "1. Show me the total number of requests to the sample app"
echo "2. What's the average request latency for the API endpoints?"
echo "3. Show me the error rate in the last 5 minutes"
echo "4. Graph the request count by endpoint for the last hour"
echo ""
echo -e "${GREEN}To stop the demo:${NC}"
echo "docker-compose -f docker-compose.demo.yml down"
echo ""
echo -e "${BLUE}Enjoy using Sherlog Prometheus Agent!${NC}" 