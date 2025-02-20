# Getting Started

This guide will help you get up and running with Sherlog quickly.

## Prerequisites

- Python 3.8 or higher
- Docker and Docker Compose (for running Prometheus and Loki)
- OpenAI API key (for query translation)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/sherlog.git
cd sherlog
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

## Quick Start

1. Start the observability stack:
```bash
docker-compose up -d
```

This will start:
- Prometheus (metrics collection)
- Loki (log aggregation)
- Promtail (log collection)
- Node Exporter (system metrics)

2. Start the Sherlog API server:
```bash
python -m app.main
```

3. Test the setup:
```bash
curl http://localhost:8000/health
```

## Basic Usage

### Query Metrics

```python
from app.core.backends.factory import ObservabilityBackendFactory
from app.core.llm import LLMManager

# Initialize the LLM manager
llm_manager = LLMManager()

# Create a backend
backend = ObservabilityBackendFactory.create_backend(
    "prometheus-loki",
    llm_manager,
    {
        "prometheus_url": "http://localhost:9090",
        "loki_url": "http://localhost:3100"
    }
)

# Query metrics
async def get_cpu_usage():
    query = "Show me CPU usage for the last hour"
    metrics = backend.get_metrics_backend()
    query_engine = backend.get_metrics_query_engine()
    
    # Translate the query
    promql = await query_engine.translate_query(query)
    
    # Execute the query
    result = await metrics.query(promql)
    
    # Format the results
    return metrics.format_result(result)
```

### Query Logs

```python
# Query logs
async def get_error_logs():
    query = "Show me error logs from the last 30 minutes"
    logs = backend.get_logs_backend()
    query_engine = backend.get_logs_query_engine()
    
    # Translate the query
    logql = await query_engine.translate_query(query)
    
    # Execute the query
    result = await logs.query(logql)
    
    # Format the results
    return logs.format_result(result)
```

### Combined Query

```python
# Query both metrics and logs
async def analyze_service_performance(service_name: str):
    # Get backends and query engines
    metrics = backend.get_metrics_backend()
    logs = backend.get_logs_backend()
    metrics_engine = backend.get_metrics_query_engine()
    logs_engine = backend.get_logs_query_engine()
    
    # Prepare queries
    metrics_query = f"Show me latency for {service_name}"
    logs_query = f"Show me error logs for {service_name}"
    
    # Translate queries
    promql = await metrics_engine.translate_query(metrics_query)
    logql = await logs_engine.translate_query(logs_query)
    
    # Execute queries
    metrics_result = await metrics.query(promql)
    logs_result = await logs.query(logql)
    
    # Return combined results
    return {
        "metrics": metrics.format_result(metrics_result),
        "logs": logs.format_result(logs_result)
    }
```

## Web Interface

The Sherlog API provides a web interface for querying metrics and logs:

1. Open your browser and navigate to `http://localhost:8000/docs`
2. Try out the API endpoints:
   - `/query/metrics` - Query metrics
   - `/query/logs` - Query logs
   - `/query/combined` - Query both metrics and logs

Example request:
```bash
curl -X POST http://localhost:8000/query/combined \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Show me CPU usage and error logs for the web service",
    "timeRange": "1h"
  }'
```

## Docker Deployment

1. Build the Docker image:
```bash
docker build -t sherlog .
```

2. Run with Docker Compose:
```yaml
version: '3'
services:
  sherlog:
    image: sherlog
    ports:
      - "8000:8000"
    environment:
      - PROMETHEUS_URL=http://prometheus:9090
      - LOKI_URL=http://loki:3100
      - OPENAI_API_KEY=your_api_key
    depends_on:
      - prometheus
      - loki

  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  loki:
    image: grafana/loki
    ports:
      - "3100:3100"
    volumes:
      - ./loki.yml:/etc/loki/local-config.yaml

  promtail:
    image: grafana/promtail
    volumes:
      - ./promtail.yml:/etc/promtail/config.yml
      - /var/log:/var/log
    depends_on:
      - loki
```

## Next Steps

1. Configure your observability stack:
   - Set up Prometheus scrape targets
   - Configure Loki log sources
   - Customize query translation

2. Integrate with your application:
   - Add metrics instrumentation
   - Set up structured logging
   - Create custom dashboards

3. Explore advanced features:
   - Custom query engines
   - Backend caching
   - Result visualization

For more information, check out:
- [API Documentation](api.md)
- [Configuration Guide](configuration.md)
- [Examples](examples.md) 