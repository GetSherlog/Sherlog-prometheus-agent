"""
LLM-powered agent for interacting with observability backends using PydanticAI.
"""

from typing import Dict, Any, Optional
from pydantic_ai.agent import Agent
from pydantic_ai.models import KnownModelName, Model

from .models.observability import ObservabilityContext, QueryResult
from .backends.base import ObservabilityBackend
from .tools.observability import setup_observability_tools
from .tools.logai_tools import setup_logai_tools
from .prompts import OBSERVABILITY_SYSTEM_PROMPT

class ObservabilityAgent:
    """
    LLM-powered agent for interacting with observability systems.
    Uses PydanticAI's agent and tools.
    """
    
    def __init__(self, backend: ObservabilityBackend, model: Optional[KnownModelName | Model] = None):
        """
        Initialize the observability agent.
        
        Args:
            backend: The observability backend to use
            model: The AI model to use (default: None, will use pydantic_ai's default)
        """
        self.backend = backend
        self.agent = Agent(
            model,
            deps_type=ObservabilityContext,
            system_prompt=OBSERVABILITY_SYSTEM_PROMPT
        )
        # Set up both tool sets
        setup_observability_tools(self.agent)
        setup_logai_tools(self.agent)
    
    async def process_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> QueryResult:
        """
        Process a natural language query using the agent.
        
        Args:
            query: The natural language query
            context: Optional context information
            
        Returns:
            The agent's response with results and analysis
        """
        # Create context
        obs_context = ObservabilityContext(
            backend=self.backend,
            time_range=context.get("time_range") if context else None,
            service=context.get("service") if context else None,
            metrics=context.get("metrics") if context else None
        )
        
        # Run the agent
        result = await self.agent.run(query, deps=obs_context)
        
        return QueryResult(
            query=query,
            result={"response": str(result)},
            thought_process=""
        )