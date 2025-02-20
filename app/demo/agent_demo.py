"""
Demo script showing how to use the observability agent with our demo app.
"""

import asyncio
from core.agent import ObservabilityAgent
from core.backends.demo import DemoBackend

async def main():
    # Initialize the backend and agent
    backend = DemoBackend(
        prometheus_url="http://localhost:9090",
        loki_url="http://localhost:3100"
    )
    agent = ObservabilityAgent(backend)
    
    # Example queries to try
    queries = [
        "Show me the error rate in the last hour",
        "What's the current CPU and memory usage?",
        "Show me all failed orders in the last 30 minutes",
        "What's the average request latency by endpoint?",
        "Are there any system performance issues?",
        "Show me the correlation between high CPU usage and error rates",
    ]
    
    # Process each query
    for query in queries:
        print(f"\nProcessing query: {query}")
        result = await agent.process_query(
            query,
            context={"time_range": "1h"}  # Default time range
        )
        print(f"Response: {result.result['response']}")
        print("-" * 80)

if __name__ == "__main__":
    asyncio.run(main()) 