"""Logging configuration for the Sherlog Prometheus Agent.

This module sets up structured logging with rotation and correlation IDs.
It provides a consistent logging pattern across the application.
"""

import logging
import logging.handlers
import sys
import json
import uuid
from pathlib import Path
from typing import Optional, Dict, Any
from contextvars import ContextVar
from functools import wraps

from ..config import settings

# Context variable to store correlation ID
correlation_id: ContextVar[str] = ContextVar('correlation_id', default='')

class StructuredLogFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def __init__(self, **kwargs):
        """Initialize the formatter with optional fields."""
        self.extra_fields = kwargs
        super().__init__()

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record as a JSON string."""
        log_data = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'name': record.name,
            'message': record.getMessage(),
            'correlation_id': correlation_id.get(''),
        }

        # Add extra fields from record
        if record.__dict__.get('extra'):
            log_data.update(record.__dict__['extra'])

        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)

        # Add extra configured fields
        log_data.update(self.extra_fields)

        return json.dumps(log_data)

def setup_logging() -> None:
    """Configure application-wide logging.
    
    Sets up logging handlers, formatters, and log rotation based on configuration.
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.logging.level)

    # Clear existing handlers
    root_logger.handlers.clear()

    # Create formatters
    json_formatter = StructuredLogFormatter(
        app_name="sherlog-agent",
        environment=settings.environment
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(json_formatter)
    root_logger.addHandler(console_handler)

    # File handler with rotation if path is configured
    if settings.logging.file_path:
        log_path = Path(settings.logging.file_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            filename=str(log_path),
            maxBytes=parse_size(settings.logging.rotation_size),
            backupCount=settings.logging.backup_count
        )
        file_handler.setFormatter(json_formatter)
        root_logger.addHandler(file_handler)

def parse_size(size_str: str) -> int:
    """Convert size string (e.g., '10MB') to bytes.
    
    Args:
        size_str: String representing size with unit (e.g., '10MB', '1GB')
        
    Returns:
        int: Size in bytes
        
    Raises:
        ValueError: If the size string format is invalid
    """
    units = {
        'B': 1,
        'KB': 1024,
        'MB': 1024 * 1024,
        'GB': 1024 * 1024 * 1024
    }
    
    size_str = size_str.strip().upper()
    for unit, multiplier in units.items():
        if size_str.endswith(unit):
            try:
                number = float(size_str[:-len(unit)])
                return int(number * multiplier)
            except ValueError:
                raise ValueError(f"Invalid size format: {size_str}")
    
    raise ValueError(f"Invalid size unit in: {size_str}")

def with_correlation_id(func):
    """Decorator to add correlation ID to the context.
    
    Args:
        func: Function to wrap
        
    Returns:
        Wrapped function with correlation ID context
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        token = correlation_id.set(str(uuid.uuid4()))
        try:
            return await func(*args, **kwargs)
        finally:
            correlation_id.reset(token)
    return wrapper

class StructuredLogger:
    """Logger class that adds structured context to log messages."""

    def __init__(self, name: str):
        """Initialize the logger with a name.
        
        Args:
            name: Logger name, typically __name__ of the module
        """
        self.logger = logging.getLogger(name)

    def _log(self, level: int, msg: str, extra: Optional[Dict[str, Any]] = None, **kwargs):
        """Internal logging method with context.
        
        Args:
            level: Logging level
            msg: Log message
            extra: Additional fields for structured logging
            **kwargs: Additional logging arguments
        """
        extra_fields = extra or {}
        extra_fields['correlation_id'] = correlation_id.get('')
        self.logger.log(level, msg, extra={'extra_fields': extra_fields}, **kwargs)

    def info(self, msg: str, extra: Optional[Dict[str, Any]] = None, **kwargs):
        """Log at INFO level.
        
        Args:
            msg: Log message
            extra: Additional fields for structured logging
            **kwargs: Additional logging arguments
        """
        self._log(logging.INFO, msg, extra, **kwargs)

    def error(self, msg: str, extra: Optional[Dict[str, Any]] = None, **kwargs):
        """Log at ERROR level.
        
        Args:
            msg: Log message
            extra: Additional fields for structured logging
            **kwargs: Additional logging arguments
        """
        self._log(logging.ERROR, msg, extra, **kwargs)

    def warning(self, msg: str, extra: Optional[Dict[str, Any]] = None, **kwargs):
        """Log at WARNING level.
        
        Args:
            msg: Log message
            extra: Additional fields for structured logging
            **kwargs: Additional logging arguments
        """
        self._log(logging.WARNING, msg, extra, **kwargs)

    def debug(self, msg: str, extra: Optional[Dict[str, Any]] = None, **kwargs):
        """Log at DEBUG level.
        
        Args:
            msg: Log message
            extra: Additional fields for structured logging
            **kwargs: Additional logging arguments
        """
        self._log(logging.DEBUG, msg, extra, **kwargs)

# Initialize logging on module import
setup_logging() 