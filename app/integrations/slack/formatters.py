from typing import Dict, Any
from ...core.prometheus import prometheus_client

def format_response(query: str, 
                   promql: str, 
                   result: Dict[str, Any], 
                   is_range: bool) -> str:
    """Format the query results into a Slack message."""
    # Start with the PromQL translation
    response = [f"*Translated Query:*\n```{promql}```"]
    
    # Add the results
    if result["type"] == "vector":
        response.append("*Results:*")
        for r in result["results"]:
            metric_str = format_metric_labels(r["metric"])
            response.append(f"• {metric_str}: {format_value(r['value'])}")
    
    elif result["type"] == "matrix":
        # For range queries, we'll generate a graph
        graph_html = prometheus_client.generate_graph(result, title=query)
        if graph_html:
            # In a real implementation, you would need to host this HTML somewhere
            # and provide a link to it, or use Slack's block kit to show the graph
            response.append("*Results:* (Graph generated)")
            for r in result["results"][:3]:  # Show first few results as text
                metric_str = format_metric_labels(r["metric"])
                response.append(f"• {metric_str}: {len(r['values'])} data points")
    
    return "\n".join(response)

def format_metric_labels(metric: Dict[str, str]) -> str:
    """Format metric labels into a readable string."""
    return ", ".join(f"{k}={v}" for k, v in metric.items())

def format_value(value: float) -> str:
    """Format a metric value for display."""
    if abs(value) >= 1000000:
        return f"{value/1000000:.2f}M"
    elif abs(value) >= 1000:
        return f"{value/1000:.2f}K"
    else:
        return f"{value:.2f}" 