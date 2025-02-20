from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

class MetricLabel(BaseModel):
    """Model for metric labels."""
    name: str = Field(..., description="Name of the metric")
    labels: Dict[str, str] = Field(default_factory=dict, description="Metric labels")

class MetricValue(BaseModel):
    """Model for metric values."""
    timestamp: datetime = Field(..., description="Timestamp of the value")
    value: float = Field(..., description="Metric value")

class MetricResult(BaseModel):
    """Model for a single metric result."""
    metric: MetricLabel
    values: List[MetricValue] = Field(..., description="List of values for this metric")

class MetricsResponse(BaseModel):
    """Model for metrics query response."""
    type: str = Field(..., description="Type of result (vector or matrix)")
    results: List[MetricResult] = Field(..., description="List of metric results")

class LogEntry(BaseModel):
    """Model for a single log entry."""
    timestamp: datetime = Field(..., description="Timestamp of the log entry")
    message: str = Field(..., description="Log message")
    labels: Dict[str, str] = Field(default_factory=dict, description="Log labels")

class LogStream(BaseModel):
    """Model for a log stream."""
    labels: Dict[str, str] = Field(default_factory=dict, description="Stream labels")
    entries: List[LogEntry] = Field(..., description="List of log entries")

class LogsResponse(BaseModel):
    """Model for logs query response."""
    type: str = Field(..., description="Type of result (streams)")
    results: List[LogStream] = Field(..., description="List of log streams")

class MetricsBackend(ABC):
    """Abstract base class for metrics backends (e.g., Prometheus, Datadog)."""
    
    @abstractmethod
    async def query(self, query: str) -> MetricsResponse:
        """Execute an instant query."""
        pass
    
    @abstractmethod
    async def query_range(self, query: str, start_time: datetime, end_time: datetime, step: str) -> MetricsResponse:
        """Execute a range query."""
        pass
    
    @abstractmethod
    def format_result(self, result: Dict[str, Any], query_type: str = "instant") -> MetricsResponse:
        """Format query results into a standard format."""
        pass
    
    @abstractmethod
    def generate_graph(self, data: MetricsResponse, title: str = "") -> Optional[str]:
        """Generate a visualization of the data."""
        pass

class LogsBackend(ABC):
    """Abstract base class for logs backends (e.g., Loki, Elasticsearch)."""
    
    @abstractmethod
    async def query(self, query: str) -> LogsResponse:
        """Execute a log query."""
        pass
    
    @abstractmethod
    async def query_range(self, query: str, start_time: datetime, end_time: datetime) -> LogsResponse:
        """Execute a range query for logs."""
        pass
    
    @abstractmethod
    def format_result(self, result: Dict[str, Any]) -> LogsResponse:
        """Format log results into a standard format."""
        pass

class QueryEngine(ABC):
    """Abstract base class for query engines (e.g., PromQL, LogQL)."""
    
    @abstractmethod
    async def translate_query(self, natural_query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Translate natural language to the specific query language."""
        pass
    
    @abstractmethod
    async def explain_query(self, query: str) -> str:
        """Explain a query in natural language."""
        pass

class ObservabilityBackend(ABC):
    """Abstract base class for complete observability backends."""
    
    @abstractmethod
    def get_metrics_backend(self) -> MetricsBackend:
        """Get the metrics backend implementation."""
        pass
    
    @abstractmethod
    def get_logs_backend(self) -> Optional[LogsBackend]:
        """Get the logs backend implementation (if available)."""
        pass
    
    @abstractmethod
    def get_metrics_query_engine(self) -> QueryEngine:
        """Get the metrics query engine."""
        pass
    
    @abstractmethod
    def get_logs_query_engine(self) -> Optional[QueryEngine]:
        """Get the logs query engine (if available)."""
        pass 