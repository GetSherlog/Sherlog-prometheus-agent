"""
LLM-powered agent for interacting with observability backends using PydanticAI.
"""

from typing import Dict, Any, Optional
from pydantic_ai import Agent

from .models.observability import ObservabilityContext, QueryResult
from .backends.base import ObservabilityBackend
from .tools.observability import setup_observability_tools

class ObservabilityAgent:
    """
    LLM-powered agent for interacting with observability systems.
    Uses PydanticAI's agent and tools.
    """
    
    def __init__(self, backend: ObservabilityBackend):
        self.backend = backend
        self.agent = Agent(
            'openai:gpt-4',  # or your chosen model
            deps_type=ObservabilityContext,
            system_prompt="""You are an expert at querying and analyzing observability data.
            Use the available tools to gather metrics and logs, analyze patterns,
            and provide insights about system behavior.
            
            Always consider:
            1. Time ranges in the query
            2. Service names and contexts
            3. Related metrics and logs
            4. Potential correlations
            """
        )
        setup_observability_tools(self.agent)
    
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