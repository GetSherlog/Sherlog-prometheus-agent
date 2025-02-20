from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from ..core.agent import ObservabilityAgent, QueryResult
from ..core.backends.factory import ObservabilityBackendFactory
from ..core.llm import llm_manager

router = APIRouter()

class ChatRequest(BaseModel):
    """Model for chat requests."""
    query: str
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    """Model for chat responses."""
    query: str
    result: Dict[str, Any]
    thought_process: str

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Handle chat interactions with the observability agent."""
    try:
        # Create backend
        backend = ObservabilityBackendFactory.create_backend(
            "prometheus-loki",
            llm_manager,
            {
                "prometheus_url": "http://localhost:9090",
                "loki_url": "http://localhost:3100"
            }
        )
        
        # Create agent
        agent = ObservabilityAgent(backend)
        
        # Process query
        result = await agent.process_query(request.query, request.context)
        
        return ChatResponse(
            query=result.query,
            result=result.result,
            thought_process=result.thought_process
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Chat processing failed: {str(e)}"
        ) 