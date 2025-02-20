"""
Visualization utilities for metrics data.
"""

from typing import List
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from ..backends.base import MetricsResponse

class MetricsVisualization:
    """Helper class for creating metrics visualizations."""
    
    @staticmethod
    def create_time_series(metrics: MetricsResponse, title: str = "") -> str:
        """Create a time series plot for metrics data."""
        if metrics.type != "matrix":
            return ""
            
        # Prepare data for plotting
        plot_data = []
        for result in metrics.results:
            metric_name = result.metric.name
            labels = "_".join(f"{k}={v}" for k, v in result.metric.labels.items())
            
            for value in result.values:
                plot_data.append({
                    "metric": f"{metric_name}{' ' + labels if labels else ''}",
                    "timestamp": value.timestamp,
                    "value": value.value
                })
        
        if not plot_data:
            return ""
        
        df = pd.DataFrame(plot_data)
        fig = px.line(df, 
                     x="timestamp", 
                     y="value", 
                     color="metric",
                     title=title,
                     template="plotly_white")
        
        # Customize layout
        fig.update_layout(
            xaxis_title="Time",
            yaxis_title="Value",
            hovermode="x unified",
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            )
        )
        
        return fig.to_html(full_html=False, include_plotlyjs=False)
    
    @staticmethod
    def create_dashboard(metrics_list: List[MetricsResponse], titles: List[str]) -> str:
        """Create a dashboard with multiple metrics visualizations."""
        n_metrics = len(metrics_list)
        if n_metrics == 0:
            return ""
            
        # Calculate grid layout
        n_cols = min(2, n_metrics)
        n_rows = (n_metrics + 1) // 2
        
        # Create subplot figure
        fig = make_subplots(
            rows=n_rows,
            cols=n_cols,
            subplot_titles=titles,
            vertical_spacing=0.12
        )
        
        # Add each metric to the dashboard
        for i, (metrics, title) in enumerate(zip(metrics_list, titles)):
            row = (i // n_cols) + 1
            col = (i % n_cols) + 1
            
            if metrics.type == "matrix":
                for result in metrics.results:
                    metric_name = result.metric.name
                    labels = "_".join(f"{k}={v}" for k, v in result.metric.labels.items())
                    name = f"{metric_name}{' ' + labels if labels else ''}"
                    
                    timestamps = [v.timestamp for v in result.values]
                    values = [v.value for v in result.values]
                    
                    fig.add_trace(
                        go.Scatter(
                            x=timestamps,
                            y=values,
                            name=name,
                            mode="lines"
                        ),
                        row=row,
                        col=col
                    )
        
        # Update layout
        fig.update_layout(
            height=300 * n_rows,
            showlegend=True,
            template="plotly_white",
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            )
        )
        
        return fig.to_html(full_html=False, include_plotlyjs=False) 