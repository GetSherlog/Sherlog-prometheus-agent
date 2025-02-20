# Sherlog Prometheus Agent

An LLM-powered agent for querying and analyzing observability data using natural language.

## Features

- Natural language queries for Prometheus metrics and Loki logs
- Automated analysis and correlation of metrics and logs
- Integration with Grafana for visualization
- Support for custom backends and query engines

## Demo Application

The project includes a demo application that simulates a real-world service with:

- Active user metrics
- Order processing statistics
- System performance metrics (CPU, Memory)
- Various log levels (INFO, WARNING, ERROR)
- HTTP request metrics

### Running the Demo

1. Start the demo stack:
```bash
cd app/demo
docker-compose up --build
```

This will start:
- Demo FastAPI application (port 8000)
- Prometheus (port 9090)
- Loki (port 3100)
- Grafana (port 3000)
- Promtail for log collection
- Observability Agent (port 5000)

2. Try example queries:
```bash
cd app/demo
python agent_demo.py
```

Example queries you can try:
- "Show me the error rate in the last hour"
- "What's the current CPU and memory usage?"
- "Show me all failed orders in the last 30 minutes"
- "What's the average request latency by endpoint?"
- "Are there any system performance issues?"
- "Show me the correlation between high CPU usage and error rates"

### Demo Metrics and Logs

The demo application generates:

1. Metrics:
   - `active_users`: Number of active users (50-200 range)
   - `orders_processed`: Order processing counter with status labels
   - `cpu_usage_percent`: Simulated CPU usage (20-80%)
   - `memory_usage_percent`: Simulated memory usage (30-90%)
   - `http_requests_total`: HTTP request counter
   - `http_request_duration_seconds`: Request latency histogram

2. Logs:
   - INFO: Active user counts and successful orders
   - WARNING: High CPU/memory usage alerts
   - ERROR: Failed orders and system errors
   - Various error scenarios (DB timeouts, API issues, etc.)

### Accessing Services

- Demo App: http://localhost:8000
  - `/` - Root endpoint
  - `/metrics` - Prometheus metrics
  - `/error` - Test error endpoint

- Prometheus: http://localhost:9090
  - View raw metrics
  - Execute PromQL queries
  - Check targets status

- Grafana: http://localhost:3000 (admin/admin)
  - Pre-configured datasources for Prometheus and Loki
  - Create dashboards for metrics and logs
  - View query results

## Development Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run tests:
```bash
pytest tests/
```

## Project Structure

```
app/
├── core/                 # Core agent functionality
│   ├── agent.py         # Main agent implementation
│   ├── backends/        # Backend implementations
│   ├── models/          # Data models
│   ├── tools/           # Agent tools
│   └── visualizations/  # Visualization utilities
├── demo/                # Demo application
│   ├── main.py         # FastAPI demo app
│   ├── agent_demo.py   # Demo script
│   └── docker-compose.yml
└── tests/              # Test suite
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details 