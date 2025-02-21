# 🎮 Sherlog Demo Environment

This document provides detailed information about the Sherlog demo environment, which includes a full observability stack and sample application for testing and development.

## 🚀 Quick Start

```bash
# Start the demo environment
docker compose -f docker-compose.demo.yml up --build
```

## 🔧 Components

### 1. Sherlog Agent (port 8000)
- Main application interface
- Natural language processing for queries
- API endpoints for metrics and logs analysis
- Environment variables:
  - `SLACK_BOT_TOKEN`: Set to "demo-mode" by default
  - `PROMETHEUS_URL`: http://prometheus:9090
  - `LOKI_URL`: http://loki:3100
  - `REDIS_URL`: redis://redis:6379/0

### 2. Redis (port 6379)
- Caching layer
- Session management
- Query result caching

### 3. Prometheus (port 9090)
- Metrics collection and storage
- PromQL query interface
- Pre-configured with targets:
  - Node Exporter
  - Sample Application
  - Sherlog Agent

### 4. Loki (port 3100)
- Log aggregation system
- LogQL query interface
- Centralized logging for all services

### 5. Grafana (port 3000)
- Visualization platform
- Pre-configured datasources:
  - Prometheus
  - Loki
- Anonymous access enabled (Admin role)
- Access at http://localhost:3000

### 6. Promtail
- Log collection agent
- Configured to collect logs from:
  - Docker containers
  - System logs
  - Application logs

### 7. Node Exporter (port 9100)
- System metrics collection
- Hardware and OS metrics
- Resource usage statistics

### 8. Sample Application (port 8080)
- Demo application generating:
  - Metrics
  - Logs
  - Errors
  - Performance data

## 📊 Available Metrics

### System Metrics
- CPU usage
- Memory utilization
- Disk I/O
- Network statistics

### Application Metrics
- Request counters
- Response times
- Error rates
- Custom business metrics

### Log Types
- Application logs
- System logs
- Access logs
- Error logs

## 🔍 Example Queries

### Metrics Queries
```text
"Show me the CPU usage for the last hour"
"What's the error rate in the sample application?"
"Display memory usage across all services"
"Show me the slowest API endpoints"
```

### Log Queries
```text
"Find all error logs from the sample application"
"Show me logs related to high CPU usage"
"Display authentication failures"
"List all logs with severity level ERROR"
```

## 🔧 Configuration

### Directory Structure
```
demo/
├── prometheus/
│   └── prometheus.yml    # Prometheus configuration
├── loki/
│   └── local-config.yaml # Loki configuration
├── promtail/
│   └── config.yml        # Promtail configuration
├── grafana/
│   └── datasources/      # Grafana datasource configs
└── sample-app/
    └── Dockerfile        # Sample application
```

### Network Configuration
- All services are connected via `sherlog-network`
- Internal DNS resolution between services
- Exposed ports for external access

### Volume Mounts
- Prometheus data persistence
- Log collection paths
- Configuration files

## 🔒 Security Notes

For the demo environment:
- Authentication is disabled for easy testing
- Ports are exposed for local access
- Grafana anonymous access is enabled
- Default credentials are used

⚠️ **Note**: These settings are for demonstration purposes only. For production deployment, refer to the main documentation and use `docker-compose.yml`.

## 🛠️ Troubleshooting

### Common Issues

1. **Services not starting**
   ```bash
   # Check service logs
   docker compose -f docker-compose.demo.yml logs [service_name]
   ```

2. **Missing metrics/logs**
   - Verify Prometheus targets at http://localhost:9090/targets
   - Check Loki logs for ingestion issues
   - Verify Promtail configuration

3. **Grafana access issues**
   - Clear browser cache
   - Verify port 3000 is not in use
   - Check Grafana container logs

### Resetting the Environment
```bash
# Stop and remove containers
docker compose -f docker-compose.demo.yml down

# Remove volumes
docker compose -f docker-compose.demo.yml down -v

# Rebuild and start
docker compose -f docker-compose.demo.yml up --build
```

## 📚 Additional Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Loki Documentation](https://grafana.com/docs/loki/latest/)
- [Grafana Documentation](https://grafana.com/docs/grafana/latest/) 