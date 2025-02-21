"""
Settings configuration using Pydantic BaseSettings.
Handles all environment variables and configuration for the application.
"""

from typing import Optional, Literal, List
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import validator, HttpUrl

class PrometheusSettings(BaseSettings):
    """Prometheus configuration settings"""
    url: str = "http://localhost:9090"
    timeout: int = 30
    max_retries: int = 3
    retry_backoff: float = 1.5
    
    model_config = SettingsConfigDict(
        env_prefix="PROMETHEUS__",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    @validator("url")
    def validate_url(cls, v: str) -> str:
        """Ensure URL is valid"""
        if not v:
            return "http://localhost:9090"
        return v

class LLMSettings(BaseSettings):
    """LLM-specific settings"""
    provider: Literal["gemini", "openai", "ollama"] = "gemini"
    gemini_api_key: Optional[str] = None
    gemini_model: str = "gemini-2.0-flash"
    openai_api_key: Optional[str] = None
    ollama_host: Optional[str] = "http://localhost:11434"
    
    model_config = SettingsConfigDict(
        env_prefix="LLM__",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_nested_delimiter="__"
    )
    
    @validator("gemini_api_key", pre=True)
    def validate_gemini_key(cls, v: Optional[str], values: dict) -> Optional[str]:
        """Validate Gemini API key is present when provider is gemini"""
        if values.get("provider") == "gemini":
            # Try to get from GEMINI_API_KEY env var if not set in LLM__ prefixed vars
            if not v:
                import os
                v = os.getenv("GEMINI_API_KEY")
            if not v:
                raise ValueError("GEMINI_API_KEY is required when using Gemini provider")
        return v

    @validator("openai_api_key", pre=True)
    def validate_openai_key(cls, v: Optional[str], values: dict) -> Optional[str]:
        """Validate OpenAI API key is present only when OpenAI is selected"""
        if values.get("provider") == "openai":
            # Try to get from OPENAI_API_KEY env var if not set in LLM__ prefixed vars
            if not v:
                import os
                v = os.getenv("OPENAI_API_KEY")
            if not v:
                raise ValueError("OPENAI_API_KEY is required when using OpenAI provider")
        return v

    @validator("ollama_host", pre=True)
    def validate_ollama_host(cls, v: Optional[str], values: dict) -> Optional[str]:
        """Validate Ollama host is present only when Ollama is selected"""
        if values.get("provider") == "ollama" and not v:
            raise ValueError("OLLAMA_HOST is required when using Ollama provider")
        return v

class SlackSettings(BaseSettings):
    """Optional Slack integration settings"""
    enabled: bool = False
    bot_token: Optional[str] = None
    app_token: Optional[str] = None
    default_channel: str = "monitoring"
    
    model_config = SettingsConfigDict(
        env_prefix="SLACK__",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    @validator("bot_token", "app_token")
    def validate_tokens(cls, v: Optional[str], values: dict) -> Optional[str]:
        """Validate Slack tokens are present when Slack is enabled"""
        if values.get("enabled", False) and not v:
            raise ValueError("Slack tokens are required when Slack integration is enabled")
        return v

class Settings(BaseSettings):
    """Main application settings"""
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = False
    
    # Optional integrations
    notifications: List[Literal["slack", "email", "webhook"]] = []
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

@lru_cache()
def get_llm_settings() -> LLMSettings:
    """Get cached LLM settings instance"""
    return LLMSettings()

@lru_cache()
def get_prometheus_settings() -> PrometheusSettings:
    """Get cached Prometheus settings instance"""
    return PrometheusSettings()

@lru_cache()
def get_slack_settings() -> SlackSettings:
    """Get cached Slack settings instance"""
    return SlackSettings()

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

# Create global settings instances
settings = get_settings()
llm_settings = get_llm_settings()
slack_settings = get_slack_settings()
prometheus_settings = get_prometheus_settings() 