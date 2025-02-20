from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings."""
    
    # Slack Configuration
    SLACK_BOT_TOKEN: str
    SLACK_APP_TOKEN: str
    
    # Prometheus Configuration
    PROMETHEUS_URL: str
    
    # LLM Configuration
    LLM_PROVIDER: str = "openai"  # Options: "openai", "ollama"
    OPENAI_API_KEY: Optional[str] = None
    OLLAMA_HOST: str = "http://localhost:11434"
    
    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Application Configuration
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

# Create a global settings instance
settings = get_settings() 