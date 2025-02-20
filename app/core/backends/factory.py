from typing import Optional, Dict, Any
from .base import ObservabilityBackend
from .prometheus import PrometheusObservabilityBackend
from .combined import PrometheusLokiBackend
from ...config import settings

class ObservabilityBackendFactory:
    """Factory for creating observability backends."""
    
    @staticmethod
    def create_backend(
        backend_type: str,
        llm_manager,
        config: Optional[Dict[str, Any]] = None
    ) -> ObservabilityBackend:
        """
        Create an observability backend based on type and configuration.
        
        Args:
            backend_type: Type of backend to create ('prometheus', 'prometheus-loki')
            llm_manager: LLM manager instance for query translation
            config: Optional configuration overrides
        
        Returns:
            An instance of ObservabilityBackend
        """
        config = config or {}
        
        if backend_type == "prometheus":
            return PrometheusObservabilityBackend(
                llm_manager=llm_manager,
                base_url=config.get('prometheus_url', settings.PROMETHEUS_URL)
            )
        
        elif backend_type == "prometheus-loki":
            return PrometheusLokiBackend(
                llm_manager=llm_manager,
                prometheus_url=config.get('prometheus_url', settings.PROMETHEUS_URL),
                loki_url=config.get('loki_url', settings.LOKI_URL)
            )
        
        else:
            raise ValueError(f"Unsupported backend type: {backend_type}")

    @staticmethod
    def get_available_backends() -> Dict[str, str]:
        """Get a dictionary of available backend types and their descriptions."""
        return {
            "prometheus": "Prometheus metrics only",
            "prometheus-loki": "Combined Prometheus metrics and Loki logs"
        } 