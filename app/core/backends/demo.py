"""
Demo backend implementation for Prometheus and Loki.
"""

from datetime import datetime
import aiohttp
from typing import List, Optional
from .base import (
    ObservabilityBackend,
    MetricsBackend,
    LogsBackend,
    MetricsResponse,
    LogsResponse,
    MetricResult,
    LogStream,
    Metric,
    Value
)

class DemoMetricsBackend(MetricsBackend):
    """Demo implementation of metrics backend using Prometheus."""
    
    def __init__(self, prometheus_url: str = "http://prometheus:9090"):
        self.base_url = prometheus_url
        
    async def query(self, query: str) -> MetricsResponse:
        """Execute an instant query."""
        async with aiohttp.ClientSession() as session:
            params = {"query": query}
            async with session.get(f"{self.base_url}/api/v1/query", params=params) as response:
                data = await response.json()
                return self._parse_response(data)
    
    async def query_range(
        self,
        query: str,
        start: datetime,
        end: datetime,
        step: str = "15s"
    ) -> MetricsResponse:
        """Execute a range query."""
        async with aiohttp.ClientSession() as session:
            params = {
                "query": query,
                "start": start.timestamp(),
                "end": end.timestamp(),
                "step": step
            }
            async with session.get(f"{self.base_url}/api/v1/query_range", params=params) as response:
                data = await response.json()
                return self._parse_response(data)
    
    def _parse_response(self, data: dict) -> MetricsResponse:
        """Parse Prometheus response into our model."""
        if data["status"] != "success":
            raise ValueError(f"Query failed: {data.get('error', 'Unknown error')}")
            
        result_type = data["data"]["resultType"]
        results = []
        
        for result in data["data"]["result"]:
            metric = Metric(
                name=result["metric"].get("__name__", ""),
                labels={k: v for k, v in result["metric"].items() if k != "__name__"}
            )
            
            if result_type == "vector":
                values = [Value(timestamp=result["value"][0], value=float(result["value"][1]))]
            else:  # matrix
                values = [Value(timestamp=v[0], value=float(v[1])) for v in result["values"]]
            
            results.append(MetricResult(metric=metric, values=values))
        
        return MetricsResponse(type=result_type, results=results)

class DemoLogsBackend(LogsBackend):
    """Demo implementation of logs backend using Loki."""
    
    def __init__(self, loki_url: str = "http://loki:3100"):
        self.base_url = loki_url
    
    async def query(self, query: str) -> LogsResponse:
        """Execute an instant LogQL query."""
        async with aiohttp.ClientSession() as session:
            params = {"query": query}
            async with session.get(f"{self.base_url}/loki/api/v1/query", params=params) as response:
                data = await response.json()
                return self._parse_response(data)
    
    async def query_range(
        self,
        query: str,
        start: datetime,
        end: datetime
    ) -> LogsResponse:
        """Execute a range LogQL query."""
        async with aiohttp.ClientSession() as session:
            params = {
                "query": query,
                "start": start.timestamp() * 1e9,  # Loki expects nanoseconds
                "end": end.timestamp() * 1e9
            }
            async with session.get(f"{self.base_url}/loki/api/v1/query_range", params=params) as response:
                data = await response.json()
                return self._parse_response(data)
    
    def _parse_response(self, data: dict) -> LogsResponse:
        """Parse Loki response into our model."""
        if "error" in data:
            raise ValueError(f"Query failed: {data['error']}")
            
        streams = []
        for stream in data.get("data", {}).get("result", []):
            labels = stream.get("stream", {})
            values = [(entry[0], entry[1]) for entry in stream.get("values", [])]
            streams.append(LogStream(labels=labels, entries=values))
        
        return LogsResponse(streams=streams)

class DemoBackend(ObservabilityBackend):
    """Demo implementation combining Prometheus and Loki backends."""
    
    def __init__(
        self,
        prometheus_url: str = "http://prometheus:9090",
        loki_url: str = "http://loki:3100"
    ):
        self._metrics = DemoMetricsBackend(prometheus_url)
        self._logs = DemoLogsBackend(loki_url)
    
    def get_metrics_backend(self) -> Optional[MetricsBackend]:
        """Get the metrics backend."""
        return self._metrics
    
    def get_logs_backend(self) -> Optional[LogsBackend]:
        """Get the logs backend."""
        return self._logs 