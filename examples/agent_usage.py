"""
Example usage of the PydanticAI-powered ObservabilityAgent.
"""

import asyncio
from app.core.agent import ObservabilityAgent, QueryResult
from app.core.backends.factory import ObservabilityBackendFactory
from app.core.llm import LLMManager
from app.core.backends.base import MetricsResponse, LogsResponse

async def print_metrics_response(metrics: MetricsResponse):
    """Print metrics response in a readable format."""
    print(f"\nMetrics ({metrics.type}):")
    for result in metrics.results:
        print(f"\nMetric: {result.metric.name}")
        print("Labels:", result.metric.labels)
        print("Values:")
        for value in result.values[:5]:  # Show first 5 values
            print(f"  {value.timestamp}: {value.value}")
        if len(result.values) > 5:
            print(f"  ... and {len(result.values) - 5} more values")

async def print_logs_response(logs: LogsResponse):
    """Print logs response in a readable format."""
    print(f"\nLogs ({logs.type}):")
    for stream in logs.results:
        print("\nStream Labels:", stream.labels)
        print("Entries:")
        for entry in stream.entries[:5]:  # Show first 5 entries
            print(f"  {entry.timestamp}: {entry.message}")
        if len(stream.entries) > 5:
            print(f"  ... and {len(stream.entries) - 5} more entries")

async def main():
    # Initialize components
    llm_manager = LLMManager()
    backend = ObservabilityBackendFactory.create_backend(
        "prometheus-loki",
        llm_manager,
        {
            "prometheus_url": "http://localhost:9090",
            "loki_url": "http://localhost:3100"
        }
    )
    agent = ObservabilityAgent(backend)
    
    # Example queries
    queries = [
        # Simple metrics query
        {
            "query": "What's the CPU usage of the web service in the last hour?",
            "context": {
                "service": "web-service",
                "time_range": "1h"
            }
        },
        # Combined metrics and logs
        {
            "query": "Show me any errors in the web service and corresponding CPU spikes",
            "context": {
                "service": "web-service",
                "time_range": "30m"
            }
        },
        # Complex analysis
        {
            "query": "Analyze database performance and find any anomalies",
            "context": {
                "service": "database",
                "time_range": "24h",
                "metrics": ["latency", "connections", "errors"]
            }
        }
    ]
    
    # Process each query
    for i, q in enumerate(queries, 1):
        print(f"\nQuery {i}: {q['query']}")
        print("-" * 50)
        
        # Get results with thought process
        result: QueryResult = await agent.process_query(q["query"], q["context"])
        
        # Print thought process
        print("\nThought Process:")
        print(result.thought_process)
        
        # Print results based on type
        if isinstance(result.result, MetricsResponse):
            await print_metrics_response(result.result)
        elif isinstance(result.result, LogsResponse):
            await print_logs_response(result.result)
        elif isinstance(result.result, dict) and "metrics" in result.result:
            # Handle combined results
            print("\nCombined Results:")
            if "metrics" in result.result:
                await print_metrics_response(result.result["metrics"])
            if "logs" in result.result:
                await print_logs_response(result.result["logs"])
            if "analysis" in result.result:
                print("\nAnalysis:")
                print(result.result["analysis"])
            if "correlations" in result.result:
                print("\nCorrelations:")
                print(result.result["correlations"])
        
        print("\n" + "=" * 80 + "\n")

if __name__ == "__main__":
    asyncio.run(main()) 