# 🔍 Sherlog Prometheus Agent

> 🤖 An LLM-powered agent for querying and analyzing observability data using natural language.

## ✨ Features

- 💬 Natural language queries for Prometheus metrics and Loki logs
- 🧠 Automated analysis and correlation of metrics and logs
- 📊 Integration with Grafana for visualization
- 🔌 Support for custom backends and query engines

## 🚀 Getting Started

### Production Setup

For production deployment, use the standard docker-compose file:

```bash
docker compose up --build
```

This starts the core services:
- 🤖 Sherlog Agent (port 8000)
- 📝 Redis for caching

### Demo Environment

For testing and development, we provide a full demo environment with monitoring stack:

```bash
# Option 1: Using demo scripts (Recommended)
./start_demo.sh  # Start the complete demo environment
./stop_demo.sh   # Stop all demo services

# Option 2: Using docker-compose directly
docker compose -f docker-compose.demo.yml up --build
```

#### Demo Script Options

The `start_demo.sh` script supports various configuration options:

```bash
Usage: ./start_demo.sh [options]

Options:
  -h, --help                 Show this help message
  --llm-provider VALUE       Set LLM provider (gemini, openai, ollama)
  --gemini-key VALUE         Set Gemini API key
  --openai-key VALUE         Set OpenAI API key
  --prometheus-url VALUE     Set Prometheus URL
  --cache-type VALUE         Set cache type (memory, redis)
  --logging-level VALUE      Set logging level (INFO, DEBUG, etc.)
```

Example usages:

1. Basic usage with Gemini:
```bash
./start_demo.sh --gemini-key your-key
```

2. Use OpenAI instead:
```bash
./start_demo.sh --llm-provider openai --openai-key your-key
```

3. Custom configuration:
```bash
./start_demo.sh \
  --llm-provider gemini \
  --gemini-key your-key \
  --prometheus-url http://custom-prometheus:9090 \
  --cache-type redis \
  --logging-level DEBUG
```

4. Using environment variables:
```bash
export GEMINI_API_KEY=your-key
./start_demo.sh
```

The demo scripts provide a convenient way to manage the demo environment:

#### `start_demo.sh`
- 🚀 Automatically sets up required environment files
- 📦 Starts all demo services (Prometheus, Loki, Grafana, etc.)
- 🌐 Launches the Next.js frontend
- 📝 Provides helpful information about available services and example queries
- 🔗 Access URLs after startup:
  - Main Dashboard: http://localhost:3000
  - Demo App: http://localhost:8000
  - Grafana: http://localhost:3000 (login: admin/admin)
  - Prometheus: http://localhost:9090

#### `stop_demo.sh`
- 🛑 Gracefully stops the Next.js frontend
- 🧹 Shuts down all demo services
- 🗑️ Cleans up Docker resources

The demo environment includes:
- 🤖 Sherlog Agent (port 8000)
- 📝 Redis for caching
- 📊 Prometheus (port 9090)
- 📝 Loki (port 3100)
- 📈 Grafana (port 3000)
- 📡 Promtail for log collection
- 📊 Node Exporter for system metrics
- 🌟 Sample Application (port 8080)

All services in the demo environment are configured with:
- Pre-configured monitoring
- Log aggregation via Loki
- Metrics collection via Prometheus
- Ready-to-use Grafana dashboards

For detailed information about the demo environment, see [DEMO.md](docs/DEMO.md)

## 🎮 Demo Application

The project includes a demo application that simulates a real-world service with:

- 👥 Active user metrics
- 🛒 Order processing statistics
- 📈 System performance metrics (CPU, Memory)
- 📝 Various log levels (INFO, WARNING, ERROR)
- 🌐 HTTP request metrics

### 🚀 Running the Demo

1. Start the demo stack:
```bash
# Navigate to demo directory and start services
cd app/demo
docker-compose up --build
```

This will start:
- 🌟 Demo FastAPI application (`port 8000`)
- 📊 Prometheus (`port 9090`)
- 📝 Loki (`port 3100`)
- 📈 Grafana (`port 3000`)
- 📡 Promtail for log collection
- 🤖 Observability Agent (`port 5000`)

2. Try example queries:
```bash
# Run the demo script
cd app/demo
python agent_demo.py
```

### 💡 Example Queries

```text
📊 "Show me the error rate in the last hour"
💻 "What's the current CPU and memory usage?"
❌ "Show me all failed orders in the last 30 minutes"
⏱️ "What's the average request latency by endpoint?"
🚨 "Are there any system performance issues?"
🔍 "Show me the correlation between high CPU usage and error rates"
```

### 📊 Demo Metrics and Logs

The demo application generates:

#### 1. Metrics
| Metric | Description | Range |
|--------|-------------|-------|
| `active_users` | Number of active users | 50-200 |
| `orders_processed` | Order processing counter | - |
| `cpu_usage_percent` | Simulated CPU usage | 20-80% |
| `memory_usage_percent` | Simulated memory usage | 30-90% |
| `http_requests_total` | HTTP request counter | - |
| `http_request_duration_seconds` | Request latency histogram | - |

#### 2. Logs
- ℹ️ **INFO**: Active user counts and successful orders
- ⚠️ **WARNING**: High CPU/memory usage alerts
- ❌ **ERROR**: Failed orders and system errors
- 🔄 Various error scenarios:
  - Database connection timeouts
  - Payment processing failures
  - API availability issues
  - Cache misses
  - Rate limit violations

### 🔗 Accessing Services

#### 🌟 Demo App: `http://localhost:8000`
```text
GET /          - Root endpoint
GET /metrics   - Prometheus metrics
GET /error     - Test error endpoint
```

#### 📊 Prometheus: `http://localhost:9090`
- View raw metrics
- Execute PromQL queries
- Check targets status

#### 📈 Grafana: `http://localhost:3000`
> 🔑 Credentials: `admin`/`admin`
- Pre-configured datasources
- Create dashboards
- View query results

## 👩‍💻 Development Setup

1. Create virtual environment:
```bash
# Create and activate virtual environment
python -m venv venv

# On Unix/macOS:
source venv/bin/activate

# On Windows:
.\venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run tests:
```bash
pytest tests/
```

## 📁 Project Structure

```
app/
├── core/                 # 🎯 Core agent functionality
│   ├── agent.py         # 🤖 Main agent implementation
│   ├── backends/        # 🔌 Backend implementations
│   ├── models/          # 📊 Data models
│   ├── tools/           # 🔧 Agent tools
│   └── visualizations/  # 📈 Visualization utilities
├── demo/                # 🎮 Demo application
│   ├── main.py         # 🌟 FastAPI demo app
│   ├── agent_demo.py   # 🤖 Demo script
│   └── docker-compose.yml
└── tests/              # ✅ Test suite
```

## 🤝 Contributing

1. 🍴 Fork the repository
2. 🌿 Create a feature branch
3. ✨ Make your changes
4. 🧪 Run tests
5. 📤 Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

---
<div align="center">
Made with ❤️ for the observability community
</div>

# Sherlog

A powerful log analysis and metrics monitoring tool with an AI-powered chat interface.

## Quick Start

### Easy Setup (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/yourusername/sherlog.git
cd sherlog
```

2. Run the setup script with your API key:
```bash
chmod +x setup.sh start_demo.sh stop_demo.sh
./start_demo.sh --gemini-key your-api-key
```

You can customize the setup using various options:
```bash
# Show all available options
./start_demo.sh --help

# Example: Use OpenAI instead of Gemini
./start_demo.sh --llm-provider openai --openai-key your-openai-key

# Example: Configure caching and logging
./start_demo.sh --gemini-key your-key --cache-type redis --logging-level DEBUG
```

The application will be available at http://localhost:3000

### Manual Setup

If you prefer to set up manually:

1. Set up the Python environment:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Set up the frontend:
```bash
cd frontend
npm install
```

3. Configure environment:

Option 1: Using environment variables:
```bash
# Required: Set LLM provider and API key
export LLM__PROVIDER=gemini
export GEMINI_API_KEY=your-api-key

# Optional: Configure other settings
export CACHE__TYPE=memory
export LOGGING__LEVEL=INFO
```

Option 2: Create .env file:
```bash
# Copy example configuration
cp .env.example .env

# Edit .env file with your settings
# Required settings:
LLM__PROVIDER=gemini
GEMINI_API_KEY=your-api-key

# Optional settings:
CACHE__TYPE=memory
LOGGING__LEVEL=INFO
```

4. Start the servers:
```bash
# In one terminal (backend)
source venv/bin/activate
python -m uvicorn app.main:app --reload

# In another terminal (frontend)
cd frontend
npm run dev
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Project Structure

```
sherlog/
├── app/                 # Backend application
│   ├── core/           # Core functionality
│   ├── routers/        # API routes
│   └── main.py         # Main application entry
├── frontend/           # Next.js frontend
│   ├── app/           # Frontend pages
│   ├── components/    # React components
│   └── lib/          # Frontend utilities
├── tests/             # Test suite
└── docs/              # Documentation
```

## Features

- 🤖 AI-powered log analysis
- 📊 Prometheus/Loki/Grafana integration
- 📝 Natural language queries
- 📈 Real-time metrics monitoring
- 🎨 Modern web interface
- 🔄 Real-time streaming responses

## Development

- Backend API: http://localhost:8000
- Frontend: http://localhost:3000
- API Documentation: http://localhost:8000/docs

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 