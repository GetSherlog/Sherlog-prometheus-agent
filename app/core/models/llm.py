"""
LLM model factory and provider implementations.
"""

from abc import ABC, abstractmethod
from typing import Optional
from pydantic_ai.models import Model
from pydantic_ai.models.gemini import GeminiModel

from ..settings import LLMSettings

class ModelProvider(ABC):
    """Abstract base class for model providers"""
    
    @abstractmethod
    def create_model(self, settings: LLMSettings) -> Optional[Model]:
        """Create and configure a model instance"""
        pass
    
    @abstractmethod
    def is_configured(self, settings: LLMSettings) -> bool:
        """Check if this provider is properly configured"""
        pass

class GeminiModelProvider(ModelProvider):
    """Provider for Gemini models"""
    
    def create_model(self, settings: LLMSettings) -> Optional[Model]:
        if not self.is_configured(settings):
            return None
        return GeminiModel(
            settings.gemini_model,
            api_key=settings.gemini_api_key
        )
    
    def is_configured(self, settings: LLMSettings) -> bool:
        return (
            settings.provider == "gemini" and 
            settings.gemini_api_key is not None and
            settings.gemini_model is not None
        )

class OpenAIModelProvider(ModelProvider):
    """Provider for OpenAI models"""
    
    def create_model(self, settings: LLMSettings) -> Optional[Model]:
        if not self.is_configured(settings):
            return None
        # TODO: Implement OpenAI model creation when needed
        return None
    
    def is_configured(self, settings: LLMSettings) -> bool:
        return (
            settings.provider == "openai" and 
            settings.openai_api_key is not None
        )

class OllamaModelProvider(ModelProvider):
    """Provider for Ollama models"""
    
    def create_model(self, settings: LLMSettings) -> Optional[Model]:
        if not self.is_configured(settings):
            return None
        # TODO: Implement Ollama model creation when needed
        return None
    
    def is_configured(self, settings: LLMSettings) -> bool:
        return (
            settings.provider == "ollama" and 
            settings.ollama_host is not None
        )

class ModelFactory:
    """Factory for creating LLM model instances"""
    
    def __init__(self):
        self.providers = {
            "gemini": GeminiModelProvider(),
            "openai": OpenAIModelProvider(),
            "ollama": OllamaModelProvider(),
        }
    
    def create_model(self, settings: LLMSettings) -> Optional[Model]:
        """
        Create a model instance based on settings
        
        Args:
            settings: LLM configuration settings
            
        Returns:
            Configured model instance or None if provider not found/configured
        """
        provider = self.providers.get(settings.provider)
        if provider and provider.is_configured(settings):
            return provider.create_model(settings)
        return None

# Global factory instance
model_factory = ModelFactory() 