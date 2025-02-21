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
docker compose -f docker-compose.demo.yml up --build
```

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

2. Run the setup script:
```bash
chmod +x setup.sh
./setup.sh
```

3. Start both frontend and backend:
```bash
cd frontend
npm run dev:all
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

3. Create necessary environment files:
```bash
# In the root directory
cp .env.example .env

# In the frontend directory
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
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