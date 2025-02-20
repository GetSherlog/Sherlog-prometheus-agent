"""Exception hierarchy for the Sherlog Prometheus Agent.

This module defines all custom exceptions used throughout the application.
"""

from typing import Optional, Any, Dict
from http import HTTPStatus

class SherlogError(Exception):
    """Base exception for all Sherlog-specific errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize the exception.
        
        Args:
            message: Human-readable error message
            status_code: Optional HTTP status code
            error_code: Optional internal error code
            details: Optional dictionary with additional error details
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code or HTTPStatus.INTERNAL_SERVER_ERROR
        self.error_code = error_code
        self.details = details or {}

class ConfigurationError(SherlogError):
    """Raised when there is an error in the configuration."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """Initialize the configuration error.
        
        Args:
            message: Human-readable error message
            details: Optional dictionary with additional error details
        """
        super().__init__(
            message=message,
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            error_code="CONFIG_ERROR",
            details=details
        )

class PrometheusError(SherlogError):
    """Base class for Prometheus-related errors."""
    pass

class PrometheusConnectionError(PrometheusError):
    """Raised when there is an error connecting to Prometheus."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """Initialize the Prometheus connection error.
        
        Args:
            message: Human-readable error message
            details: Optional dictionary with additional error details
        """
        super().__init__(
            message=message,
            status_code=HTTPStatus.SERVICE_UNAVAILABLE,
            error_code="PROMETHEUS_CONNECTION_ERROR",
            details=details
        )

class PrometheusQueryError(PrometheusError):
    """Raised when there is an error executing a Prometheus query."""

    def __init__(self, message: str, query: str, details: Optional[Dict[str, Any]] = None):
        """Initialize the Prometheus query error.
        
        Args:
            message: Human-readable error message
            query: The PromQL query that failed
            details: Optional dictionary with additional error details
        """
        error_details = details or {}
        error_details["query"] = query
        super().__init__(
            message=message,
            status_code=HTTPStatus.BAD_REQUEST,
            error_code="PROMETHEUS_QUERY_ERROR",
            details=error_details
        )

class SlackError(SherlogError):
    """Base class for Slack-related errors."""
    pass

class SlackAPIError(SlackError):
    """Raised when there is an error calling the Slack API."""

    def __init__(self, message: str, api_method: str, details: Optional[Dict[str, Any]] = None):
        """Initialize the Slack API error.
        
        Args:
            message: Human-readable error message
            api_method: The Slack API method that failed
            details: Optional dictionary with additional error details
        """
        error_details = details or {}
        error_details["api_method"] = api_method
        super().__init__(
            message=message,
            status_code=HTTPStatus.BAD_GATEWAY,
            error_code="SLACK_API_ERROR",
            details=error_details
        )

class LLMError(SherlogError):
    """Base class for LLM-related errors."""
    pass

class LLMAPIError(LLMError):
    """Raised when there is an error calling the LLM API."""

    def __init__(self, message: str, provider: str, details: Optional[Dict[str, Any]] = None):
        """Initialize the LLM API error.
        
        Args:
            message: Human-readable error message
            provider: The LLM provider (e.g., 'openai', 'ollama')
            details: Optional dictionary with additional error details
        """
        error_details = details or {}
        error_details["provider"] = provider
        super().__init__(
            message=message,
            status_code=HTTPStatus.BAD_GATEWAY,
            error_code="LLM_API_ERROR",
            details=error_details
        )

class ValidationError(SherlogError):
    """Raised when there is a validation error."""

    def __init__(self, message: str, field: str, details: Optional[Dict[str, Any]] = None):
        """Initialize the validation error.
        
        Args:
            message: Human-readable error message
            field: The field that failed validation
            details: Optional dictionary with additional error details
        """
        error_details = details or {}
        error_details["field"] = field
        super().__init__(
            message=message,
            status_code=HTTPStatus.BAD_REQUEST,
            error_code="VALIDATION_ERROR",
            details=error_details
        )

class RetryError(SherlogError):
    """Raised when maximum retries are exceeded."""

    def __init__(
        self,
        message: str,
        operation: str,
        attempts: int,
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize the retry error.
        
        Args:
            message: Human-readable error message
            operation: The operation that was being retried
            attempts: Number of attempts made
            details: Optional dictionary with additional error details
        """
        error_details = details or {}
        error_details.update({
            "operation": operation,
            "attempts": attempts
        })
        super().__init__(
            message=message,
            status_code=HTTPStatus.SERVICE_UNAVAILABLE,
            error_code="RETRY_ERROR",
            details=error_details
        ) 