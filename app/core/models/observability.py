"""
Models for observability-related data structures.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from ..backends.base import ObservabilityBackend, MetricResult

class ObservabilityContext(BaseModel):
    """Context for observability queries."""
    backend: ObservabilityBackend
    time_range: Optional[str] = None
    service: Optional[str] = None
    metrics: Optional[List[str]] = None

class MetricsQuery(BaseModel):
    """Model for metrics query parameters."""
    query: str = Field(..., description="The PromQL query to execute")
    time_range: Optional[str] = Field(None, description="Time range for the query")

class LogsQuery(BaseModel):
    """Model for logs query parameters."""
    query: str = Field(..., description="The LogQL query to execute")
    time_range: Optional[str] = Field(None, description="Time range for the query")

class MetricsAnalysis(BaseModel):
    """Model for metrics analysis results."""
    trends: List[str] = Field(..., description="Identified trends in the data")
    anomalies: List[Dict[str, Any]] = Field(..., description="Detected anomalies")
    statistics: Dict[str, float] = Field(..., description="Key statistics")

class Correlation(BaseModel):
    """Model for correlation results."""
    correlations: List[Dict[str, Any]] = Field(..., description="Found correlations")
    patterns: List[str] = Field(..., description="Identified patterns")
    insights: List[str] = Field(..., description="Key insights")

class DashboardVisualization(BaseModel):
    """Model for dashboard visualization."""
    metric: MetricResult
    graph: Optional[str] = None
    title: str = Field(..., description="Title for the visualization")

class Dashboard(BaseModel):
    """Model for dashboard results."""
    title: str
    visualizations: List[DashboardVisualization]
    combined_view: Optional[str] = None

class QueryResult(BaseModel):
    """Model for query results."""
    query: str
    result: Dict[str, Any]
    thought_process: str 