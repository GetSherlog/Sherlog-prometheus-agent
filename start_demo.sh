#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Enable Docker BuildKit
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

# Default values
GEMINI_API_KEY=${GEMINI_API_KEY:-""}
LLM_PROVIDER=${LLM_PROVIDER:-"gemini"}
PROMETHEUS_URL=${PROMETHEUS_URL:-"http://localhost:9090"}
CACHE_TYPE=${CACHE_TYPE:-"memory"}
LOGGING_LEVEL=${LOGGING_LEVEL:-"INFO"}

# Help function
show_help() {
    echo "Usage: ./start_demo.sh [options]"
    echo
    echo "Options:"
    echo "  -h, --help                 Show this help message"
    echo "  --llm-provider VALUE       Set LLM provider (gemini, openai, ollama)"
    echo "  --gemini-key VALUE         Set Gemini API key"
    echo "  --openai-key VALUE         Set OpenAI API key"
    echo "  --prometheus-url VALUE     Set Prometheus URL"
    echo "  --cache-type VALUE         Set cache type (memory, redis)"
    echo "  --logging-level VALUE      Set logging level (INFO, DEBUG, etc.)"
    echo "  --no-cache                 Disable Docker build cache"
    echo
    echo "Example:"
    echo "  ./start_demo.sh --llm-provider gemini --gemini-key your-key"
    exit 0
}

# Additional build arguments
BUILD_ARGS=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            ;;
        --llm-provider)
            LLM_PROVIDER="$2"
            shift 2
            ;;
        --gemini-key)
            GEMINI_API_KEY="$2"
            shift 2
            ;;
        --openai-key)
            OPENAI_API_KEY="$2"
            shift 2
            ;;
        --prometheus-url)
            PROMETHEUS_URL="$2"
            shift 2
            ;;
        --cache-type)
            CACHE_TYPE="$2"
            shift 2
            ;;
        --logging-level)
            LOGGING_LEVEL="$2"
            shift 2
            ;;
        --no-cache)
            BUILD_ARGS="--no-cache"
            shift
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            ;;
    esac
done

echo -e "${BLUE}Starting Sherlog Demo...${NC}"
echo -e "${BLUE}Docker BuildKit is enabled for optimized builds${NC}"

# Export variables with proper prefixes
export LLM__PROVIDER=${LLM_PROVIDER}
export GEMINI_API_KEY=${GEMINI_API_KEY}
export OPENAI_API_KEY=${OPENAI_API_KEY:-""}
export LLM__OLLAMA_HOST=${LLM__OLLAMA_HOST:-""}
export PROMETHEUS__URL=${PROMETHEUS_URL}
export CACHE__TYPE=${CACHE_TYPE}
export LOGGING__LEVEL=${LOGGING_LEVEL}

# Disable Slack by default
export SLACK__ENABLED=false
export SLACK__BOT_TOKEN=""
export SLACK__APP_TOKEN=""
export SLACK__DEFAULT_CHANNEL="monitoring"

# Validate required settings
if [ "$LLM__PROVIDER" = "gemini" ] && [ -z "$GEMINI_API_KEY" ]; then
    echo -e "${YELLOW}Warning: GEMINI_API_KEY not set. Please provide it using --gemini-key${NC}"
    exit 1
fi

if [ "$LLM__PROVIDER" = "openai" ] && [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${YELLOW}Warning: OPENAI_API_KEY not set. Please provide it using --openai-key${NC}"
    exit 1
fi

# Create necessary environment files
echo -e "${BLUE}Setting up environment files...${NC}"

# Create .env file with provided settings
cat > .env << EOF
# Application Environment
ENVIRONMENT=development
DEBUG=true

# LLM Configuration
LLM__PROVIDER=${LLM__PROVIDER}

# Provider-specific settings
GEMINI_API_KEY=${GEMINI_API_KEY}
LLM__GEMINI_MODEL=gemini-2.0-flash

# Prometheus Configuration
PROMETHEUS__URL=${PROMETHEUS__URL}
PROMETHEUS__TIMEOUT=30
PROMETHEUS__MAX_RETRIES=3
PROMETHEUS__RETRY_BACKOFF=1.5

# Cache Configuration
CACHE__TYPE=${CACHE__TYPE}
CACHE__TTL=3600

# Logging Configuration
LOGGING__LEVEL=${LOGGING__LEVEL}
LOGGING__FORMAT=json
LOGGING__FILE_PATH=logs/agent.log
LOGGING__ROTATION_SIZE=10MB
LOGGING__BACKUP_COUNT=5
LOGGING__CORRELATION_ENABLED=true

# Optional Integrations
SLACK__ENABLED=false
SLACK__BOT_TOKEN=
SLACK__APP_TOKEN=
SLACK__DEFAULT_CHANNEL=monitoring
EOF

# Create frontend env file
if [ ! -f "frontend/.env.local" ]; then
    echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > frontend/.env.local
fi

# Start the demo stack in the background with BuildKit enabled
echo -e "${BLUE}Starting demo stack (Prometheus, Loki, Grafana, etc.)...${NC}"
cd app/demo
docker compose up --build ${BUILD_ARGS} -d

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

echo -e "\n${BLUE}Current Configuration:${NC}"
echo -e "LLM Provider: ${GREEN}${LLM__PROVIDER}${NC}"
echo -e "Cache Type: ${GREEN}${CACHE__TYPE}${NC}"
echo -e "Logging Level: ${GREEN}${LOGGING__LEVEL}${NC}"
echo -e "BuildKit: ${GREEN}Enabled${NC}"

echo -e "\n${BLUE}Example queries you can try:${NC}"
echo "- Show me the error rate in the last hour"
echo "- What's the current CPU and memory usage?"
echo "- Show me all failed orders in the last 30 minutes"
echo "- What's the average request latency by endpoint?"

echo -e "\n${BLUE}To stop the demo, run: ./stop_demo.sh${NC}" 