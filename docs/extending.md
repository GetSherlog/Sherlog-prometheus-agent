# Extending Sherlog

This guide explains how to extend Sherlog with new backends and capabilities.

## Adding a New Metrics Backend

To add support for a new metrics system (e.g., Datadog), create a new class implementing the `MetricsBackend` interface:

```python
from typing import Dict, Any, Optional
from datetime import datetime
from app.core.backends.base import MetricsBackend

class DatadogBackend(MetricsBackend):
    def __init__(self, api_key: str, app_key: str):
        self.api_key = api_key
        self.app_key = app_key
        # Initialize Datadog client
        
    async def query(self, query: str) -> Dict[str, Any]:
        # Implement query logic
        pass
        
    async def query_range(self, 
                         query: str,
                         start_time: datetime,
                         end_time: datetime,
                         step: str) -> Dict[str, Any]:
        # Implement range query logic
        pass
        
    def format_result(self, 
                     result: Dict[str, Any],
                     query_type: str = "instant") -> Dict[str, Any]:
        # Format results to match standard format
        pass
        
    def generate_graph(self,
                      data: Dict[str, Any],
                      title: str = "") -> Optional[str]:
        # Generate visualization
        pass
```

## Adding a New Logs Backend

To add support for a new logging system (e.g., Elasticsearch), implement the `LogsBackend` interface:

```python
from app.core.backends.base import LogsBackend

class ElasticsearchBackend(LogsBackend):
    def __init__(self, hosts: list, **kwargs):
        # Initialize Elasticsearch client
        pass
        
    async def query(self, query: str) -> Dict[str, Any]:
        # Implement query logic
        pass
        
    async def query_range(self,
                         query: str,
                         start_time: datetime,
                         end_time: datetime) -> Dict[str, Any]:
        # Implement range query logic
        pass
        
    def format_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        # Format results to match standard format
        pass
```

## Adding a New Query Engine

To support a new query language, implement the `QueryEngine` interface:

```python
from app.core.backends.base import QueryEngine

class ElasticsearchQueryEngine(QueryEngine):
    def __init__(self, llm_manager):
        self.llm_manager = llm_manager
        
    async def translate_query(self,
                            natural_query: str,
                            context: Optional[Dict[str, Any]] = None) -> str:
        # Translate natural language to Elasticsearch query
        pass
        
    async def explain_query(self, query: str) -> str:
        # Explain Elasticsearch query in natural language
        pass
```

## Creating a Combined Backend

To create a new combined backend (e.g., Datadog + Elasticsearch):

```python
from app.core.backends.base import ObservabilityBackend

class DatadogElasticsearchBackend(ObservabilityBackend):
    def __init__(self,
                 llm_manager,
                 datadog_config: Dict[str, Any],
                 elasticsearch_config: Dict[str, Any]):
        self.metrics_backend = DatadogBackend(**datadog_config)
        self.logs_backend = ElasticsearchBackend(**elasticsearch_config)
        self.metrics_query_engine = DatadogQueryEngine(llm_manager)
        self.logs_query_engine = ElasticsearchQueryEngine(llm_manager)
    
    def get_metrics_backend(self) -> MetricsBackend:
        return self.metrics_backend
    
    def get_logs_backend(self) -> Optional[LogsBackend]:
        return self.logs_backend
    
    def get_metrics_query_engine(self) -> QueryEngine:
        return self.metrics_query_engine
    
    def get_logs_query_engine(self) -> Optional[QueryEngine]:
        return self.logs_query_engine
```

## Registering New Backends

Add your new backend to the factory:

```python
class ObservabilityBackendFactory:
    @staticmethod
    def create_backend(backend_type: str,
                      llm_manager,
                      config: Optional[Dict[str, Any]] = None) -> ObservabilityBackend:
        if backend_type == "datadog-elasticsearch":
            return DatadogElasticsearchBackend(
                llm_manager=llm_manager,
                datadog_config=config.get('datadog', {}),
                elasticsearch_config=config.get('elasticsearch', {})
            )
        # ... existing backends ...
```

## Standard Formats

### Metrics Result Format
```python
{
    "type": "vector|matrix",
    "results": [
        {
            "metric": {"label1": "value1", ...},
            "timestamp": timestamp,
            "value": float_value
        }
        # or for matrix:
        {
            "metric": {"label1": "value1", ...},
            "values": [
                {"timestamp": ts1, "value": val1},
                {"timestamp": ts2, "value": val2}
            ]
        }
    ]
}
```

### Logs Result Format
```python
{
    "type": "streams",
    "results": [
        {
            "labels": {"label1": "value1", ...},
            "entries": [
                {
                    "timestamp": "iso8601_timestamp",
                    "message": "log message"
                }
            ]
        }
    ]
}
```

## Best Practices

1. **Error Handling**: Implement robust error handling and provide clear error messages
2. **Timeouts**: Add configurable timeouts for all API calls
3. **Rate Limiting**: Respect API rate limits of the backend service
4. **Caching**: Implement caching where appropriate
5. **Testing**: Write comprehensive tests for your backend
6. **Documentation**: Document all configuration options and limitations 