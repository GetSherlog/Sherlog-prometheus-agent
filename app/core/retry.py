"""Retry utilities for the Sherlog Prometheus Agent.

This module provides retry functionality with exponential backoff for HTTP calls
and other operations that may need retrying.
"""

import asyncio
import functools
import random
from typing import (
    TypeVar, Callable, Optional, Type, Union, Tuple, Any,
    Awaitable, Coroutine
)
from .exceptions import RetryError
from .logging import StructuredLogger

logger = StructuredLogger(__name__)

T = TypeVar('T')

def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    exceptions: Union[Type[Exception], Tuple[Type[Exception], ...]] = Exception,
    on_retry: Optional[Callable[[Exception, int], None]] = None
) -> Callable[[Callable[..., Awaitable[T]]], Callable[..., Awaitable[T]]]:
    """Decorator for retrying operations with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        backoff_factor: Multiplier for the delay after each retry
        exceptions: Exception or tuple of exceptions to catch and retry on
        on_retry: Optional callback function called after each retry attempt
        
    Returns:
        Decorator function that adds retry behavior
        
    Example:
        @retry_with_backoff(max_retries=3, exceptions=(ConnectionError, TimeoutError))
        async def fetch_data():
            # ... code that might fail ...
    """
    def decorator(
        func: Callable[..., Awaitable[T]]
    ) -> Callable[..., Awaitable[T]]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            delay = initial_delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        logger.error(
                            f"Max retries ({max_retries}) exceeded for {func.__name__}",
                            extra={
                                "function": func.__name__,
                                "max_retries": max_retries,
                                "exception": str(e)
                            }
                        )
                        raise RetryError(
                            message=f"Operation failed after {max_retries} retries",
                            operation=func.__name__,
                            attempts=max_retries + 1,
                            details={"last_error": str(e)}
                        ) from e
                    
                    # Calculate next delay with jitter
                    jitter = random.uniform(0.8, 1.2)
                    next_delay = min(delay * backoff_factor * jitter, max_delay)
                    
                    logger.warning(
                        f"Retry attempt {attempt + 1}/{max_retries} for {func.__name__}",
                        extra={
                            "function": func.__name__,
                            "attempt": attempt + 1,
                            "max_retries": max_retries,
                            "delay": next_delay,
                            "exception": str(e)
                        }
                    )
                    
                    if on_retry:
                        on_retry(e, attempt)
                    
                    await asyncio.sleep(next_delay)
                    delay = next_delay
            
            # This should never be reached due to the raise in the loop
            raise RuntimeError("Unexpected end of retry loop")
        
        return wrapper
    
    return decorator

def on_retry_log(exception: Exception, attempt: int) -> None:
    """Default retry callback that logs retry attempts.
    
    Args:
        exception: The exception that triggered the retry
        attempt: The current retry attempt number
    """
    logger.info(
        f"Retry callback executed",
        extra={
            "attempt": attempt,
            "exception_type": type(exception).__name__,
            "exception_message": str(exception)
        }
    ) 