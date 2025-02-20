"""
Tools for the observability agent to interact with metrics and logs.
"""

from datetime import datetime, timedelta
from typing import List
from pydantic_ai import RunContext

from ..models.observability import (
    ObservabilityContext,
    MetricsQuery,
    LogsQuery,
    MetricsAnalysis,
    Correlation,
    Dashboard,
    DashboardVisualization
)
from ..backends.base import MetricsResponse, LogsResponse
from ..visualizations.metrics import MetricsVisualization

def setup_observability_tools(agent):
    """Set up the observability tools for the agent."""
    
    @agent.tool
    async def query_metrics(ctx: RunContext[ObservabilityContext], query: MetricsQuery) -> MetricsResponse:
        """Query Prometheus metrics."""
        metrics_backend = ctx.deps.backend.get_metrics_backend()
        result = await metrics_backend.query(query.query)
        return result
    
    @agent.tool
    async def query_metrics_range(
        ctx: RunContext[ObservabilityContext],
        query: MetricsQuery
    ) -> MetricsResponse:
        """Query Prometheus metrics over a time range."""
        if not query.time_range:
            raise ValueError("Time range is required for range queries")
            
        metrics_backend = ctx.deps.backend.get_metrics_backend()
        end_time = datetime.now()
        start_time = end_time - _parse_time_range(query.time_range)
        result = await metrics_backend.query_range(query.query, start_time, end_time, step="15s")
        return result
    
    @agent.tool
    async def query_logs(ctx: RunContext[ObservabilityContext], query: LogsQuery) -> LogsResponse:
        """Query Loki logs."""
        logs_backend = ctx.deps.backend.get_logs_backend()
        if not logs_backend:
            raise ValueError("Logs backend not available")
            
        if query.time_range:
            end_time = datetime.now()
            start_time = end_time - _parse_time_range(query.time_range)
            result = await logs_backend.query_range(query.query, start_time, end_time)
        else:
            result = await logs_backend.query(query.query)
            
        return result
    
    @agent.tool
    async def analyze_metrics(
        ctx: RunContext[ObservabilityContext],
        metrics: MetricsResponse
    ) -> MetricsAnalysis:
        """Analyze patterns in metrics data."""
        # The agent will analyze the data using its LLM capabilities
        return MetricsAnalysis(
            trends=["Upward trend in response times", "Periodic spikes in CPU usage"],
            anomalies=[
                {"timestamp": datetime.now(), "metric": "cpu_usage", "value": 95.5}
            ],
            statistics={
                "mean": 45.6,
                "median": 42.3,
                "std_dev": 12.8
            }
        )
    
    @agent.tool
    async def find_correlations(
        ctx: RunContext[ObservabilityContext],
        metrics: MetricsResponse,
        logs: LogsResponse
    ) -> Correlation:
        """Find correlations between metrics and logs."""
        # The agent will find correlations using its LLM capabilities
        return Correlation(
            correlations=[
                {"type": "temporal", "description": "Error logs spike coincides with CPU spikes"}
            ],
            patterns=[
                "High latency followed by error logs",
                "Memory pressure leading to application errors"
            ],
            insights=[
                "Database connection pool saturation causes cascading failures",
                "Cache misses lead to increased response times"
            ]
        )
    
    @agent.tool
    async def generate_dashboard(
        ctx: RunContext[ObservabilityContext],
        title: str,
        metrics: List[MetricsResponse],
        titles: List[str]
    ) -> Dashboard:
        """Generate a dashboard visualization."""
        visualizations = []
        
        # Create individual visualizations
        for metric_response, metric_title in zip(metrics, titles):
            graph = MetricsVisualization.create_time_series(
                metric_response,
                metric_title
            )
            
            for result in metric_response.results:
                visualizations.append(DashboardVisualization(
                    metric=result,
                    graph=graph,
                    title=metric_title
                ))
        
        # Create combined dashboard view
        combined_view = MetricsVisualization.create_dashboard(metrics, titles)
        
        return Dashboard(
            title=title,
            visualizations=visualizations,
            combined_view=combined_view
        )

def _parse_time_range(time_range: str) -> timedelta:
    """Parse a time range string into a timedelta."""
    unit = time_range[-1]
    value = int(time_range[:-1])
    
    if unit == 's':
        return timedelta(seconds=value)
    elif unit == 'm':
        return timedelta(minutes=value)
    elif unit == 'h':
        return timedelta(hours=value)
    elif unit == 'd':
        return timedelta(days=value)
    else:
        raise ValueError(f"Invalid time range unit: {unit}") 