# API Documentation

This document provides detailed information about the core APIs and interfaces in the Sherlog system.

## Core Interfaces

### MetricsBackend

Abstract base class for metrics backends (e.g., Prometheus).

```python
class MetricsBackend(ABC):
    @abstractmethod
    async def query(self, query: str) -> Dict[str, Any]:
        """Execute an instant query."""
        pass
        
    @abstractmethod
    async def query_range(self,
                         query: str,
                         start_time: datetime,
                         end_time: datetime,
                         step: str) -> Dict[str, Any]:
        """Execute a range query."""
        pass
        
    @abstractmethod
    def format_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Format query results into a standardized structure."""
        pass
        
    @abstractmethod
    def generate_graph(self, data: Dict[str, Any]) -> str:
        """Generate a visualization of the metrics data."""
        pass
```

### LogsBackend

Abstract base class for logs backends (e.g., Loki).

```python
class LogsBackend(ABC):
    @abstractmethod
    async def query(self, query: str) -> Dict[str, Any]:
        """Execute an instant log query."""
        pass
        
    @abstractmethod
    async def query_range(self,
                         query: str,
                         start_time: datetime,
                         end_time: datetime) -> Dict[str, Any]:
        """Execute a range log query."""
        pass
        
    @abstractmethod
    def format_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Format log query results into a standardized structure."""
        pass
```

### QueryEngine

Abstract base class for query engines that translate natural language to backend-specific queries.

```python
class QueryEngine(ABC):
    @abstractmethod
    async def translate_query(self,
                            query: str,
                            context: Optional[Dict[str, Any]] = None) -> str:
        """Translate a natural language query to a backend-specific query."""
        pass
        
    @abstractmethod
    async def explain_query(self, query: str) -> str:
        """Provide a natural language explanation of a backend-specific query."""
        pass
```

### ObservabilityBackend

Abstract base class that combines metrics and logs backends with their respective query engines.

```python
class ObservabilityBackend(ABC):
    @abstractmethod
    def get_metrics_backend(self) -> Optional[MetricsBackend]:
        """Get the metrics backend if available."""
        pass
        
    @abstractmethod
    def get_logs_backend(self) -> Optional[LogsBackend]:
        """Get the logs backend if available."""
        pass
        
    @abstractmethod
    def get_metrics_query_engine(self) -> Optional[QueryEngine]:
        """Get the metrics query engine if available."""
        pass
        
    @abstractmethod
    def get_logs_query_engine(self) -> Optional[QueryEngine]:
        """Get the logs query engine if available."""
        pass
```

## Concrete Implementations

### PrometheusBackend

Implementation of `MetricsBackend` for Prometheus.

```python
class PrometheusBackend(MetricsBackend):
    def __init__(self, url: str):
        """
        Initialize the Prometheus backend.
        
        Args:
            url: The URL of the Prometheus server
        """
        self.url = url
        self.client = AsyncClient()
        
    async def query(self, query: str) -> Dict[str, Any]:
        """
        Execute an instant Prometheus query.
        
        Args:
            query: A valid PromQL query
            
        Returns:
            Dict containing query result data
            
        Raises:
            QueryError: If the query fails
        """
        # Implementation details...
```

### LokiBackend

Implementation of `LogsBackend` for Loki.

```python
class LokiBackend(LogsBackend):
    def __init__(self, url: str):
        """
        Initialize the Loki backend.
        
        Args:
            url: The URL of the Loki server
        """
        self.url = url
        self.client = AsyncClient()
        
    async def query(self, query: str) -> Dict[str, Any]:
        """
        Execute an instant Loki query.
        
        Args:
            query: A valid LogQL query
            
        Returns:
            Dict containing log entries and metadata
            
        Raises:
            QueryError: If the query fails
        """
        # Implementation details...
```

### PrometheusLokiBackend

Implementation of `ObservabilityBackend` that combines Prometheus and Loki.

```python
class PrometheusLokiBackend(ObservabilityBackend):
    def __init__(self,
                 prometheus_url: str,
                 loki_url: Optional[str] = None,
                 llm_manager: Optional[LLMManager] = None):
        """
        Initialize the combined backend.
        
        Args:
            prometheus_url: URL of the Prometheus server
            loki_url: Optional URL of the Loki server
            llm_manager: Optional LLM manager for query translation
        """
        self.prometheus = PrometheusBackend(prometheus_url)
        self.loki = LokiBackend(loki_url) if loki_url else None
        self.llm_manager = llm_manager
        
        if llm_manager:
            self.prometheus_query_engine = PromQLQueryEngine(llm_manager)
            self.loki_query_engine = LogQLQueryEngine(llm_manager) if loki_url else None
```

## Factory

### ObservabilityBackendFactory

Factory class for creating observability backends.

```python
class ObservabilityBackendFactory:
    @staticmethod
    def create_backend(backend_type: str,
                      llm_manager: Optional[LLMManager] = None,
                      config: Optional[Dict[str, Any]] = None) -> ObservabilityBackend:
        """
        Create an observability backend.
        
        Args:
            backend_type: Type of backend to create ("prometheus" or "prometheus-loki")
            llm_manager: Optional LLM manager for query translation
            config: Optional configuration dictionary
            
        Returns:
            An instance of ObservabilityBackend
            
        Raises:
            ValueError: If the backend type is not supported
        """
        if backend_type == "prometheus":
            return PrometheusBackend(
                config.get("prometheus_url", "http://localhost:9090")
            )
        elif backend_type == "prometheus-loki":
            return PrometheusLokiBackend(
                prometheus_url=config.get("prometheus_url", "http://localhost:9090"),
                loki_url=config.get("loki_url"),
                llm_manager=llm_manager
            )
        else:
            raise ValueError(f"Unsupported backend type: {backend_type}")
```

## Result Formats

### Metrics Result Format

Standard format for metrics query results:

```python
{
    "type": "vector" | "matrix",
    "data": [
        {
            "metric": {
                "name": str,
                "labels": Dict[str, str]
            },
            "values": List[Tuple[float, float]]  # timestamp, value pairs
        }
    ]
}
```

### Logs Result Format

Standard format for log query results:

```python
{
    "type": "streams" | "matrix",
    "data": [
        {
            "stream": {
                "labels": Dict[str, str]
            },
            "values": List[Tuple[str, str]]  # timestamp, log line pairs
        }
    ]
}
```

## Error Handling

### QueryError

Base exception class for query-related errors.

```python
class QueryError(Exception):
    def __init__(self, message: str, query: str, backend: str):
        self.message = message
        self.query = query
        self.backend = backend
        super().__init__(f"{backend} query failed: {message} (query: {query})")
```

### BackendError

Base exception class for backend-related errors.

```python
class BackendError(Exception):
    def __init__(self, message: str, backend: str):
        self.message = message
        self.backend = backend
        super().__init__(f"{backend} backend error: {message}")
``` 