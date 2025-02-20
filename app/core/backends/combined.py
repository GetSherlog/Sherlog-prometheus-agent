from typing import Optional
from .base import ObservabilityBackend, MetricsBackend, LogsBackend, QueryEngine
from .prometheus import PrometheusBackend, PromQLQueryEngine
from .loki import LokiBackend, LogQLQueryEngine

class PrometheusLokiBackend(ObservabilityBackend):
    """Combined Prometheus and Loki observability backend."""
    
    def __init__(self, 
                 llm_manager,
                 prometheus_url: Optional[str] = None,
                 loki_url: Optional[str] = None):
        """Initialize the combined backend."""
        self.metrics_backend = PrometheusBackend(prometheus_url)
        self.metrics_query_engine = PromQLQueryEngine(llm_manager)
        
        if loki_url:
            self.logs_backend = LokiBackend(loki_url)
            self.logs_query_engine = LogQLQueryEngine(llm_manager)
        else:
            self.logs_backend = None
            self.logs_query_engine = None
    
    def get_metrics_backend(self) -> MetricsBackend:
        """Get the Prometheus metrics backend."""
        return self.metrics_backend
    
    def get_logs_backend(self) -> Optional[LogsBackend]:
        """Get the Loki logs backend if configured."""
        return self.logs_backend
    
    def get_metrics_query_engine(self) -> QueryEngine:
        """Get the PromQL query engine."""
        return self.metrics_query_engine
    
    def get_logs_query_engine(self) -> Optional[QueryEngine]:
        """Get the LogQL query engine if configured."""
        return self.logs_query_engine 