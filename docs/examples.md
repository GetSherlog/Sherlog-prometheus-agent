# Usage Examples

This guide provides examples of common use cases and how to implement them.

## Basic Usage

### Creating a Backend

```python
from app.core.backends.factory import ObservabilityBackendFactory
from app.core.llm import llm_manager

# Create a Prometheus-only backend
backend = ObservabilityBackendFactory.create_backend(
    "prometheus",
    llm_manager
)

# Create a combined Prometheus+Loki backend
backend = ObservabilityBackendFactory.create_backend(
    "prometheus-loki",
    llm_manager,
    {
        "prometheus_url": "http://prometheus:9090",
        "loki_url": "http://loki:3100"
    }
)
```

### Querying Metrics

```python
# Get the metrics backend
metrics = backend.get_metrics_backend()

# Get the query engine
query_engine = backend.get_metrics_query_engine()

# Translate and execute a query
query = "Show me CPU usage for the last hour"
promql = await query_engine.translate_query(query)
result = await metrics.query(promql)

# Format the results
formatted = metrics.format_result(result)
```

### Querying Logs

```python
# Get the logs backend
logs = backend.get_logs_backend()

# Get the query engine
query_engine = backend.get_logs_query_engine()

# Translate and execute a query
query = "Show me error logs from the last 30 minutes"
logql = await query_engine.translate_query(query)
result = await logs.query(logql)

# Format the results
formatted = logs.format_result(result)
```

## Advanced Usage

### Combined Metrics and Logs Query

```python
async def analyze_service_issues(backend, service_name: str):
    """Analyze service issues using both metrics and logs."""
    
    # Get the backends
    metrics = backend.get_metrics_backend()
    logs = backend.get_logs_backend()
    
    # Get the query engines
    metrics_engine = backend.get_metrics_query_engine()
    logs_engine = backend.get_logs_query_engine()
    
    # Prepare context
    context = {"service": service_name}
    
    # Translate queries
    error_rate_query = await metrics_engine.translate_query(
        f"Show me error rate for {service_name} in the last 15 minutes",
        context
    )
    
    error_logs_query = await logs_engine.translate_query(
        f"Show me error logs for {service_name} in the last 15 minutes",
        context
    )
    
    # Execute queries in parallel
    error_rate_result, error_logs_result = await asyncio.gather(
        metrics.query(error_rate_query),
        logs.query(error_logs_query)
    )
    
    # Format results
    return {
        "metrics": metrics.format_result(error_rate_result),
        "logs": logs.format_result(error_logs_result)
    }
```

### Custom Visualization

```python
def create_custom_dashboard(metrics_data: Dict[str, Any]) -> str:
    """Create a custom dashboard with multiple metrics."""
    
    # Create a plotly figure
    fig = make_subplots(rows=2, cols=2)
    
    # Add CPU usage
    cpu_data = prepare_metric_data(metrics_data["cpu"])
    fig.add_trace(
        go.Scatter(x=cpu_data["timestamps"], y=cpu_data["values"]),
        row=1, col=1
    )
    
    # Add memory usage
    memory_data = prepare_metric_data(metrics_data["memory"])
    fig.add_trace(
        go.Scatter(x=memory_data["timestamps"], y=memory_data["values"]),
        row=1, col=2
    )
    
    # Add error rate
    error_data = prepare_metric_data(metrics_data["errors"])
    fig.add_trace(
        go.Scatter(x=error_data["timestamps"], y=error_data["values"]),
        row=2, col=1
    )
    
    # Return as HTML
    return fig.to_html(full_html=False, include_plotlyjs='cdn')
```

### Caching Results

```python
from functools import lru_cache
from datetime import datetime, timedelta

class CachedMetricsBackend:
    def __init__(self, backend: MetricsBackend, cache_ttl: int = 60):
        self.backend = backend
        self.cache_ttl = cache_ttl
    
    @lru_cache(maxsize=100)
    async def query(self, query: str) -> Dict[str, Any]:
        return await self.backend.query(query)
    
    async def query_range(self,
                         query: str,
                         start_time: datetime,
                         end_time: datetime,
                         step: str) -> Dict[str, Any]:
        cache_key = f"{query}:{start_time}:{end_time}:{step}"
        if cache_key in self._range_cache:
            cached_result, cached_time = self._range_cache[cache_key]
            if datetime.now() - cached_time < timedelta(seconds=self.cache_ttl):
                return cached_result
        
        result = await self.backend.query_range(query, start_time, end_time, step)
        self._range_cache[cache_key] = (result, datetime.now())
        return result
```

### Error Handling

```python
async def safe_query_execution(backend, query: str) -> Dict[str, Any]:
    """Execute a query with proper error handling."""
    try:
        # Translate the query
        promql = await backend.get_metrics_query_engine().translate_query(query)
        
        try:
            # Execute the query
            result = await backend.get_metrics_backend().query(promql)
            return {
                "status": "success",
                "data": backend.get_metrics_backend().format_result(result)
            }
        except Exception as e:
            return {
                "status": "error",
                "error": f"Query execution failed: {str(e)}",
                "query": promql
            }
            
    except Exception as e:
        return {
            "status": "error",
            "error": f"Query translation failed: {str(e)}",
            "query": query
        }
```

## Integration Examples

### FastAPI Endpoint

```python
from fastapi import FastAPI, HTTPException
from typing import Optional

app = FastAPI()

@app.post("/query")
async def query_metrics(
    query: str,
    backend_type: str = "prometheus-loki",
    context: Optional[Dict[str, Any]] = None
):
    try:
        # Create backend
        backend = ObservabilityBackendFactory.create_backend(
            backend_type,
            llm_manager
        )
        
        # Execute query
        result = await safe_query_execution(backend, query)
        
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["error"])
            
        return result["data"]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Slack Bot Integration

```python
from slack_bolt.async_app import AsyncApp

app = AsyncApp(token=settings.SLACK_BOT_TOKEN)

@app.event("app_mention")
async def handle_mention(event, say):
    query = event["text"].replace(f"<@{event['user']}>", "").strip()
    
    try:
        # Create backend
        backend = ObservabilityBackendFactory.create_backend(
            "prometheus-loki",
            llm_manager
        )
        
        # Execute query
        result = await safe_query_execution(backend, query)
        
        if result["status"] == "error":
            await say(f"Error: {result['error']}")
            return
            
        # Format for Slack
        blocks = format_result_for_slack(result["data"])
        await say(blocks=blocks)
        
    except Exception as e:
        await say(f"Sorry, something went wrong: {str(e)}") 