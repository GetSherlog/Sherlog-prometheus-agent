# Configuration Guide

This guide explains how to configure and customize the Sherlog system.

## Environment Variables

The following environment variables can be used to configure the system:

```bash
# Core Settings
SHERLOG_ENV=development|staging|production
SHERLOG_LOG_LEVEL=debug|info|warning|error

# Prometheus Configuration
PROMETHEUS_URL=http://localhost:9090
PROMETHEUS_TIMEOUT=30
PROMETHEUS_MAX_RETRIES=3

# Loki Configuration
LOKI_URL=http://localhost:3100
LOKI_TIMEOUT=30
LOKI_MAX_RETRIES=3

# LLM Configuration
OPENAI_API_KEY=your_api_key
LLM_MODEL=gpt-4-turbo-preview
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=2000

# Web Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
SERVER_WORKERS=4

# Cache Configuration
CACHE_TYPE=memory|redis
REDIS_URL=redis://localhost:6379
CACHE_TTL=3600
```

## Configuration Files

### Prometheus Configuration

Example `prometheus.yml`:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'sample-app'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['localhost:9100']
```

### Loki Configuration

Example `loki.yml`:

```yaml
auth_enabled: false

server:
  http_listen_port: 3100

ingester:
  lifecycler:
    address: 127.0.0.1
    ring:
      kvstore:
        store: inmemory
      replication_factor: 1
  chunk_idle_period: 5m
  chunk_retain_period: 30s

schema_config:
  configs:
    - from: 2020-05-15
      store: boltdb
      object_store: filesystem
      schema: v11
      index:
        prefix: index_
        period: 168h

storage_config:
  boltdb:
    directory: /tmp/loki/index

  filesystem:
    directory: /tmp/loki/chunks

limits_config:
  enforce_metric_name: false
  reject_old_samples: true
  reject_old_samples_max_age: 168h
```

### Promtail Configuration

Example `promtail.yml`:

```yaml
server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  - job_name: docker
    static_configs:
      - targets:
          - localhost
        labels:
          job: docker
          __path__: /var/lib/docker/containers/*/*-json.log
    pipeline_stages:
      - json:
          expressions:
            output: log
            stream: stream
            timestamp: time
      - timestamp:
          source: timestamp
          format: RFC3339Nano
      - labels:
          stream:
      - output:
          source: output

  - job_name: system
    static_configs:
      - targets:
          - localhost
        labels:
          job: system
          __path__: /var/log/*log
    pipeline_stages:
      - regex:
          expression: '^(?P<timestamp>\w+\s+\d+\s+\d+:\d+:\d+)\s+(?P<host>\w+)\s+(?P<application>[\w\-]+)(?:\[(?P<pid>\d+)\])?\:\s+(?P<message>.*)$'
      - timestamp:
          source: timestamp
          format: MMM DD HH:mm:ss
      - labels:
          host:
          application:
          pid:
      - output:
          source: message

  - job_name: sample-app
    static_configs:
      - targets:
          - localhost
        labels:
          job: sample-app
          __path__: /var/log/sample-app/*.log
    pipeline_stages:
      - json:
          expressions:
            level: level
            message: message
            timestamp: timestamp
      - timestamp:
          source: timestamp
          format: RFC3339Nano
      - labels:
          level:
      - output:
          source: message
```

## Backend Configuration

### Metrics Backend

Configure the Prometheus backend with custom settings:

```python
from app.core.backends.factory import ObservabilityBackendFactory

backend = ObservabilityBackendFactory.create_backend(
    "prometheus",
    config={
        "prometheus_url": "http://prometheus:9090",
        "timeout": 30,
        "max_retries": 3,
        "cache_ttl": 60
    }
)
```

### Logs Backend

Configure the Loki backend with custom settings:

```python
backend = ObservabilityBackendFactory.create_backend(
    "prometheus-loki",
    config={
        "prometheus_url": "http://prometheus:9090",
        "loki_url": "http://loki:3100",
        "timeout": 30,
        "max_retries": 3,
        "cache_ttl": 60
    }
)
```

## Query Engine Configuration

### LLM Configuration

Configure the LLM manager for query translation:

```python
from app.core.llm import LLMManager

llm_manager = LLMManager(
    model="gpt-4-turbo-preview",
    temperature=0.7,
    max_tokens=2000,
    system_prompt="You are an expert in observability...",
    api_key="your_api_key"
)
```

### Custom Query Engine

Create a custom query engine:

```python
from app.core.query import QueryEngine
from typing import Optional, Dict, Any

class CustomQueryEngine(QueryEngine):
    def __init__(self, llm_manager: LLMManager):
        self.llm_manager = llm_manager
        
    async def translate_query(self,
                            query: str,
                            context: Optional[Dict[str, Any]] = None) -> str:
        # Custom translation logic
        pass
        
    async def explain_query(self, query: str) -> str:
        # Custom explanation logic
        pass
```

## Cache Configuration

### Memory Cache

Configure in-memory caching:

```python
from app.core.cache import MemoryCache

cache = MemoryCache(ttl=3600)
backend.set_cache(cache)
```

### Redis Cache

Configure Redis caching:

```python
from app.core.cache import RedisCache

cache = RedisCache(
    url="redis://localhost:6379",
    ttl=3600,
    prefix="sherlog:"
)
backend.set_cache(cache)
```

## Logging Configuration

### File Logging

Configure file logging:

```python
import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger("sherlog")
handler = RotatingFileHandler(
    "logs/sherlog.log",
    maxBytes=10000000,
    backupCount=5
)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)
```

### Structured Logging

Configure structured JSON logging:

```python
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        return json.dumps(log_data)

logger = logging.getLogger("sherlog")
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
```

## Web Server Configuration

### FastAPI Configuration

Configure the FastAPI server:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Sherlog API",
    description="API for querying metrics and logs",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
```

### ASGI Server Configuration

Configure Uvicorn with custom settings:

```python
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        workers=4,
        log_level="info",
        reload=True
    )
``` 