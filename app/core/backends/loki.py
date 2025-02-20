from typing import Dict, Any, Optional
from datetime import datetime
import aiohttp
from .base import LogsBackend, QueryEngine
from ...config import settings

class LokiBackend(LogsBackend):
    """Loki implementation of the logs backend."""
    
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or settings.LOKI_URL
        if not self.base_url:
            raise ValueError("Loki URL is required")
    
    async def query(self, query: str) -> Dict[str, Any]:
        """Execute an instant query against Loki."""
        async with aiohttp.ClientSession() as session:
            params = {'query': query}
            async with session.get(f"{self.base_url}/loki/api/v1/query", params=params) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Loki query failed: {error_text}")
                return await response.json()

    async def query_range(self, 
                         query: str, 
                         start_time: datetime,
                         end_time: datetime) -> Dict[str, Any]:
        """Execute a range query against Loki."""
        async with aiohttp.ClientSession() as session:
            params = {
                'query': query,
                'start': str(int(start_time.timestamp() * 1e9)),  # Loki expects nanoseconds
                'end': str(int(end_time.timestamp() * 1e9))
            }
            async with session.get(f"{self.base_url}/loki/api/v1/query_range", params=params) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Loki range query failed: {error_text}")
                return await response.json()

    def format_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Format Loki query results into a standard format."""
        if result.get("status") != "success":
            raise Exception(f"Query failed: {result.get('error', 'Unknown error')}")

        data = result.get("data", {})
        result_type = data.get("resultType")
        
        if result_type == "streams":
            return self._format_streams_result(data.get("result", []))
        elif result_type == "matrix":
            return self._format_matrix_result(data.get("result", []))
        else:
            return {"error": f"Unsupported result type: {result_type}"}

    def _format_streams_result(self, results: list) -> Dict[str, Any]:
        """Format log stream results."""
        formatted_results = []
        for result in results:
            stream = result.get("stream", {})
            values = result.get("values", [])
            formatted_values = [
                {
                    "timestamp": datetime.fromtimestamp(int(ts) / 1e9).isoformat(),
                    "message": message
                }
                for ts, message in values
            ]
            formatted_results.append({
                "labels": stream,
                "entries": formatted_values
            })
        return {"type": "streams", "results": formatted_results}

    def _format_matrix_result(self, results: list) -> Dict[str, Any]:
        """Format metric query results."""
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

class LogQLQueryEngine(QueryEngine):
    """LogQL implementation of the query engine."""
    
    def __init__(self, llm_manager):
        self.llm_manager = llm_manager
    
    async def translate_query(self, natural_query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Translate natural language to LogQL."""
        return await self.llm_manager.translate_to_logql(natural_query, context)
    
    async def explain_query(self, query: str) -> str:
        """Explain a LogQL query in natural language."""
        return await self.llm_manager.explain_logql(query) 