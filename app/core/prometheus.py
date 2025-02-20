from typing import Dict, Any, Optional, List
import aiohttp
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
from ..config import settings

class PrometheusClient:
    """Client for interacting with Prometheus API."""
    
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or settings.PROMETHEUS_URL
        if not self.base_url:
            raise ValueError("Prometheus URL is required")
    
    async def query(self, query: str) -> Dict[str, Any]:
        """Execute an instant query against Prometheus."""
        async with aiohttp.ClientSession() as session:
            params = {'query': query}
            async with session.get(f"{self.base_url}/api/v1/query", params=params) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Prometheus query failed: {error_text}")
                return await response.json()

    async def query_range(self, 
                         query: str, 
                         start_time: datetime,
                         end_time: datetime,
                         step: str = "15s") -> Dict[str, Any]:
        """Execute a range query against Prometheus."""
        async with aiohttp.ClientSession() as session:
            params = {
                'query': query,
                'start': start_time.timestamp(),
                'end': end_time.timestamp(),
                'step': step
            }
            async with session.get(f"{self.base_url}/api/v1/query_range", params=params) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Prometheus range query failed: {error_text}")
                return await response.json()

    def format_result(self, result: Dict[str, Any], query_type: str = "instant") -> Dict[str, Any]:
        """Format Prometheus query results into a more usable structure."""
        if result.get("status") != "success":
            raise Exception(f"Query failed: {result.get('error', 'Unknown error')}")

        data = result.get("data", {})
        result_type = data.get("resultType")
        
        if result_type == "vector":
            return self._format_vector_result(data.get("result", []))
        elif result_type == "matrix":
            return self._format_matrix_result(data.get("result", []))
        else:
            return {"error": f"Unsupported result type: {result_type}"}

    def _format_vector_result(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Format instant query results."""
        formatted_results = []
        for result in results:
            metric = result.get("metric", {})
            value = result.get("value", [None, None])
            formatted_results.append({
                "metric": metric,
                "timestamp": value[0],
                "value": float(value[1]) if value[1] is not None else None
            })
        return {"type": "vector", "results": formatted_results}

    def _format_matrix_result(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Format range query results."""
        formatted_results = []
        for result in results:
            metric = result.get("metric", {})
            values = result.get("values", [])
            formatted_values = [
                {"timestamp": value[0], "value": float(value[1])}
                for value in values
            ]
            formatted_results.append({
                "metric": metric,
                "values": formatted_values
            })
        return {"type": "matrix", "results": formatted_results}

    def generate_graph(self, 
                      data: Dict[str, Any], 
                      title: str = "Prometheus Metrics") -> Optional[str]:
        """Generate a Plotly graph from Prometheus data."""
        if data["type"] == "matrix":
            # Prepare data for plotting
            plot_data = []
            for result in data["results"]:
                metric_name = "_".join(f"{k}={v}" for k, v in result["metric"].items())
                for value in result["values"]:
                    plot_data.append({
                        "metric": metric_name,
                        "timestamp": datetime.fromtimestamp(value["timestamp"]),
                        "value": value["value"]
                    })
            
            if not plot_data:
                return None
            
            df = pd.DataFrame(plot_data)
            fig = px.line(df, 
                         x="timestamp", 
                         y="value", 
                         color="metric",
                         title=title)
            
            return fig.to_html(full_html=False, include_plotlyjs='cdn')
        
        return None

# Create a global Prometheus client instance
prometheus_client = PrometheusClient() 