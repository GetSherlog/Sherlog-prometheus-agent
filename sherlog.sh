#!/usr/bin/env bash

# Ensure we're running in bash
if [ -z "${BASH_VERSION:-}" ]; then
    echo "This script requires bash" 1>&2
    exec /bin/bash "$0" "$@"
fi

set -euo pipefail

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Enable Docker BuildKit
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

# Default values
BUILD_ARGS=""  # Initialize build args with empty default
GEMINI_API_KEY=${GEMINI_API_KEY:-""}
LLM_PROVIDER=${LLM_PROVIDER:-"gemini"}
PROMETHEUS_URL=${PROMETHEUS_URL:-"http://localhost:9090"}
CACHE_TYPE=${CACHE_TYPE:-"memory"}
LOGGING_LEVEL=${LOGGING_LEVEL:-"INFO"}
FORCE_REBUILD=${FORCE_REBUILD:-"false"}

# List of containers to monitor
CONTAINERS="app redis prometheus loki promtail grafana node-exporter sample-app"

# Function to verify directory structure
verify_directories() {
    echo -e "${BLUE}Verifying repository structure...${NC}"
    echo -e "${BLUE}Current directory: $(pwd)${NC}"
    
    # List of required directories and files
    local required=(
        "app:dir"                     # Main application code
        "frontend:dir"               # Frontend application
        "docker-compose.yml:file"     # Main compose file
        "docker-compose.demo.yml:file" # Demo compose file
        "Dockerfile:file"             # Main Dockerfile
    )
    
    # Check each required directory/file
    local missing=()
    for item in "${required[@]}"; do
        # Split item into path and type
        local path="${item%%:*}"
        local type="${item##*:}"
        
        echo -e "${BLUE}Checking for ${path} (${type})...${NC}"
        
        if [ "$type" = "dir" ]; then
            # Check directory
            if [ ! -d "$path" ]; then
                echo -e "${RED}Directory not found: ${path}${NC}"
                missing+=("$path")
            else
                echo -e "${GREEN}Directory found: ${path}${NC}"
            fi
        else
            # Check file
            if [ ! -f "$path" ]; then
                echo -e "${RED}File not found: ${path}${NC}"
                missing+=("$path")
            else
                echo -e "${GREEN}File found: ${path}${NC}"
            fi
        fi
    done
    
    # If any items are missing, show error and exit
    if [ ${#missing[@]} -ne 0 ]; then
        echo -e "${RED}Error: Required files/directories are missing:${NC}"
        printf "${RED}  - %s${NC}\n" "${missing[@]}"
        echo -e "${RED}Please ensure you are running this script from the root of the sherlog repository.${NC}"
        exit 1
    fi
    
    # Create runtime directories if they don't exist
    mkdir -p logs
    mkdir -p app/demo/prometheus
    mkdir -p app/demo/grafana/provisioning
    mkdir -p demo/promtail
}

# Function to check if rebuild is needed
check_rebuild_needed() {
    local app_container="sherlog-prometheus-agent-app"
    local rebuild_needed="false"
    
    # Check if container exists and is running
    if ! docker ps -q -f name=$app_container | grep -q .; then
        echo -e "${YELLOW}Main app container not running - rebuild needed${NC}"
        rebuild_needed="true"
    else
        # Try to check container logs for missing dependency errors
        if docker logs $app_container 2>&1 | grep -q "ModuleNotFoundError: No module named"; then
            echo -e "${YELLOW}Missing dependencies detected - rebuild needed${NC}"
            rebuild_needed="true"
        fi
    fi
    
    echo "$rebuild_needed"
}

# Function to rebuild containers
rebuild_containers() {
    echo -e "${BLUE}Rebuilding containers with updated dependencies...${NC}"
    
    # Verify repository structure
    verify_directories
    
    # Navigate to demo directory and rebuild
    cd demo || {
        echo -e "${RED}Failed to navigate to demo directory${NC}"
        exit 1
    }
    echo -e "${BLUE}Stopping existing containers...${NC}"
    docker compose down --remove-orphans
    echo -e "${BLUE}Building containers with no cache...${NC}"
    docker compose build --no-cache
    echo -e "${BLUE}Starting containers...${NC}"
    docker compose up -d
    cd ..
}

# Function to check container status
get_container_status() {
    local container="$1"
    local prefix="sherlog-prometheus-agent-"
    local status=$(docker ps -a --filter "name=${prefix}${container}" --format "{{.Status}}" 2>/dev/null)
    if [ -z "$status" ]; then
        echo "not created"
    elif [[ $status == *"Up"* ]]; then
        echo "running"
    else
        echo "stopped"
    fi
}

# Function to show container status
show_container_status() {
    echo -e "\n${BLUE}Container Status:${NC}"
    for container in $CONTAINERS; do
        local status=$(get_container_status "$container")
        case $status in
            "running")
                echo -e "${container}: ${GREEN}Running${NC}"
                ;;
            "stopped")
                echo -e "${container}: ${RED}Stopped${NC}"
                ;;
            "not created")
                echo -e "${container}: ${YELLOW}Not Created${NC}"
                ;;
        esac
    done
}

# Function to check container logs for errors
check_container_logs() {
    local prefix="sherlog-prometheus-agent-"
    for container in $CONTAINERS; do
        local status=$(get_container_status "$container")
        if [ "$status" = "stopped" ]; then
            echo -e "\n${RED}Errors in ${container}:${NC}"
            docker logs "${prefix}${container}" 2>&1 | grep -i "error" | tail -n 5
        fi
    done
}

# Function to check if any containers are stopped
any_containers_stopped() {
    for container in $CONTAINERS; do
        if [ "$(get_container_status "$container")" = "stopped" ]; then
            return 0
        fi
    done
    return 1
}

# Function to stop all services
cleanup() {
    echo -e "\n${BLUE}Stopping demo services...${NC}"
    
    # Kill the frontend process if running
    if [ ! -z "${FRONTEND_PID:-}" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    
    # Stop docker compose services
    cd demo
    docker compose down --remove-orphans
    cd ..
    
    # Final status check
    show_container_status
    
    echo -e "\n${GREEN}Demo stopped successfully${NC}"
    exit 0
}

# Set up trap for Ctrl+C
trap cleanup SIGINT SIGTERM

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
    echo "  --force-rebuild            Force rebuild of all containers"
    echo
    echo "Example:"
    echo "  ./start_demo.sh --llm-provider gemini --gemini-key your-key"
    exit 0
}

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
        --force-rebuild)
            FORCE_REBUILD="true"
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
    echo -e "${RED}Error: GEMINI_API_KEY not set. Please provide it using --gemini-key${NC}"
    exit 1
fi

if [ "$LLM__PROVIDER" = "openai" ] && [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${RED}Error: OPENAI_API_KEY not set. Please provide it using --openai-key${NC}"
    exit 1
fi

# Create necessary environment files
echo -e "${BLUE}Setting up environment files...${NC}"

# Verify repository structure
verify_directories

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
cd demo

# Check if rebuild is needed
if [ "$FORCE_REBUILD" = "true" ] || [ "$(check_rebuild_needed)" = "true" ]; then
    rebuild_containers
else
    docker compose up --build ${BUILD_ARGS} -d
fi

# Initial status check
sleep 5
show_container_status

# Check for any stopped containers and show their logs
check_container_logs

# Start the frontend
if [ "$(get_container_status app)" = "running" ]; then
    echo -e "\n${BLUE}Starting Next.js frontend...${NC}"
    cd ../../frontend
    npm install
    npm run dev &
    FRONTEND_PID=$!
else
    echo -e "\n${RED}Main app container failed to start. Not starting frontend.${NC}"
fi

# Show access information if services are running
if [ "$(get_container_status app)" = "running" ]; then
    echo -e "\n${GREEN}🚀 Demo is ready! Access the following services:${NC}"
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
fi

echo -e "\n${BLUE}Press Ctrl+C to stop the demo${NC}"

# Keep script running and periodically check container status
while true; do
    sleep 30
    show_container_status
    # Only show status if something changed
    if any_containers_stopped; then
        echo -e "\n${RED}Containers have stopped unexpectedly${NC}"
        show_container_status
        check_container_logs
        break
    fi
done 