"""Configuration management for the Sherlog Prometheus Agent.

This module handles all configuration settings for the application, including
environment variables, secrets, and validation. It uses Pydantic for type checking
and validation.
"""

from enum import Enum
from typing import Optional
from pydantic import (
    Field,
    field_validator,
    ValidationError,
    HttpUrl,
)
from pydantic_settings import BaseSettings
from functools import lru_cache
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class Environment(str, Enum):
    """Valid environment options."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

class LLMProvider(str, Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    OLLAMA = "ollama"
    GEMINI = "gemini"

class PrometheusSettings(BaseSettings):
    """Prometheus-specific configuration."""
    url: str = Field(default="http://localhost:9090", description="Prometheus server URL")
    timeout: int = Field(default=30, description="Request timeout in seconds")
    max_retries: int = Field(default=3, description="Maximum number of retry attempts")
    retry_backoff: float = Field(default=1.5, description="Exponential backoff factor")

    @field_validator('url')
    @classmethod
    def validate_url(cls, v):
        """Validate URL format."""
        try:
            HttpUrl(v)
            return v
        except ValidationError:
            raise ValueError("Invalid URL format")

class SlackSettings(BaseSettings):
    """Slack integration configuration."""
    bot_token: Optional[str] = Field(default="", description="Slack bot user OAuth token")
    app_token: Optional[str] = Field(default="", description="Slack app-level token")
    default_channel: str = Field(default="monitoring", description="Default channel for notifications")
    enabled: bool = Field(default=False, description="Whether Slack integration is enabled")

    model_config = {
        "extra": "allow"
    }

class LLMSettings(BaseSettings):
    """Language Model configuration."""
    provider: LLMProvider = Field(default=LLMProvider.GEMINI, description="LLM provider selection")
    openai_api_key: Optional[str] = Field(default="", description="OpenAI API key")
    gemini_api_key: Optional[str] = Field(default="", description="Google Gemini API key")
    gemini_model: Optional[str] = Field(default="gemini-2.0-flash", description="Gemini model name")
    ollama_host: str = Field(default="http://localhost:11434", description="Ollama host URL")

    @field_validator('ollama_host')
    @classmethod
    def validate_ollama_url(cls, v):
        """Validate URL format."""
        try:
            HttpUrl(v)
            return v
        except ValidationError:
            raise ValueError("Invalid URL format")

    model_config = {
        "extra": "allow"
    }

    @field_validator('openai_api_key')
    @classmethod
    def validate_openai_key(cls, v, info):
        """Ensure OpenAI key is present when OpenAI is selected."""
        if info.data.get('provider') == LLMProvider.OPENAI and not v:
            raise ValueError("OpenAI API key is required when using OpenAI provider")
        return v

    @field_validator('gemini_api_key')
    @classmethod
    def validate_gemini_key(cls, v, info):
        """Ensure Gemini key is present when Gemini is selected."""
        if info.data.get('provider') == LLMProvider.GEMINI and not v:
            raise ValueError("Gemini API key is required when using Gemini provider")
        return v

class RedisSettings(BaseSettings):
    """Redis configuration."""
    url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL"
    )
    max_connections: int = Field(default=10, description="Maximum connection pool size")
    timeout: int = Field(default=5, description="Connection timeout in seconds")

    model_config = {
        "extra": "allow"
    }

class LoggingSettings(BaseSettings):
    """Logging configuration."""
    level: str = Field(default="INFO", description="Logging level")
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format string"
    )
    file_path: Optional[Path] = Field(default=None, description="Log file path")
    rotation_size: str = Field(default="10MB", description="Log rotation size")
    backup_count: int = Field(default=5, description="Number of backup files to keep")
    correlation_enabled: bool = Field(default=True, description="Enable correlation ID in logs")

    model_config = {
        "extra": "allow"
    }

class Settings(BaseSettings):
    """Main application settings."""
    environment: Environment = Field(
        default=Environment.DEVELOPMENT,
        description="Application environment"
    )
    debug: bool = Field(default=False, description="Debug mode flag")
    
    # Component-specific settings
    prometheus: PrometheusSettings = Field(default_factory=lambda: PrometheusSettings())
    slack: SlackSettings = Field(default_factory=lambda: SlackSettings())
    llm: LLMSettings = Field(default_factory=lambda: LLMSettings())
    redis: RedisSettings = Field(default_factory=lambda: RedisSettings())
    logging: LoggingSettings = Field(default_factory=lambda: LoggingSettings())

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "env_nested_delimiter": "__",
        "extra": "allow",
        "validate_default": True
    }

    @field_validator('environment')
    @classmethod
    def validate_production_settings(cls, v, info):
        """Additional validation for production environment."""
        if v == Environment.PRODUCTION:
            if info.data.get('debug'):
                raise ValueError("Debug mode cannot be enabled in production")
        return v

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance.
    
    Returns:
        Settings: Application settings instance
        
    Raises:
        ValidationError: If environment variables are invalid
    """
    try:
        return Settings()
    except ValidationError as e:
        logger.error(f"Configuration validation failed: {e}")
        raise

# Create a global settings instance
settings = get_settings() 