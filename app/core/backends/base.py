"""
Base classes for observability backends.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class MetricLabel(BaseModel):
    """Model for metric labels."""
    name: str
    labels: Dict[str, str]

class MetricValue(BaseModel):
    """Model for a single metric value."""
    timestamp: datetime
    value: float

class MetricResult(BaseModel):
    """Model for a single metric result."""
    metric: MetricLabel
    values: List[MetricValue] = Field(..., description="List of values for this metric")

class MetricsResponse(BaseModel):
    """Model for metrics query response."""
    type: str = Field(..., description="Type of result (vector/matrix)")
    results: List[MetricResult] = Field(..., description="List of metric results")

class LogStream(BaseModel):
    """Model for a single log stream."""
    stream: Dict[str, str]
    values: List[List[Union[str, datetime]]]

class LogsResponse(BaseModel):
    """Model for logs query response."""
    type: str = Field(..., description="Type of result (streams)")
    results: List[LogStream] = Field(..., description="List of log streams")
    logs: List[str] = Field(..., description="Raw log messages")
    timestamps: List[datetime] = Field(..., description="Timestamps for each log message")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")

class QueryEngine(BaseModel, ABC):
    """Abstract base class for query engines."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    @abstractmethod
    def build_query(self, **kwargs) -> str:
        """Build a query string from parameters."""
        pass

class MetricsBackend(BaseModel, ABC):
    """Abstract base class for metrics backends."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    @abstractmethod
    async def query(self, query: str) -> MetricsResponse:
        """Execute a metrics query."""
        pass
        
    @abstractmethod
    async def query_range(
        self, query: str, start: datetime, end: datetime, step: str = "15s"
    ) -> MetricsResponse:
        """Execute a metrics query over a time range."""
        pass

class LogsBackend(BaseModel, ABC):
    """Abstract base class for logs backends."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    @abstractmethod
    async def query(self, query: str) -> LogsResponse:
        """Execute a logs query."""
        pass
        
    @abstractmethod
    async def query_range(
        self, query: str, start: datetime, end: datetime
    ) -> LogsResponse:
        """Execute a logs query over a time range."""
        pass

class ObservabilityBackend(BaseModel, ABC):
    """Abstract base class for complete observability backends."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
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