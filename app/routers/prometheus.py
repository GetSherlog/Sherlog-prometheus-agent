"""FastAPI router for Prometheus endpoints."""

from fastapi import APIRouter, HTTPException, Query, Request, Depends
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel
from ..core.agent import ObservabilityAgent
from ..core.exceptions import SherlogError

router = APIRouter()

class QueryRequest(BaseModel):
    """Model for natural language query requests."""
    query: str
    context: Optional[Dict[str, Any]] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    step: Optional[str] = "15s"

class QueryResponse(BaseModel):
    """Model for query responses."""
    natural_query: str
    promql: str
    result: Dict[str, Any]
    graph_html: Optional[str] = None

async def get_agent(request: Request) -> ObservabilityAgent:
    """Get the ObservabilityAgent from application state."""
    agent = request.app.state.agent
    if not agent:
        raise HTTPException(
            status_code=503,
            detail="ObservabilityAgent not initialized"
        )
    return agent

@router.post("/query", response_model=QueryResponse)
async def query_metrics(request: QueryRequest, agent: ObservabilityAgent = Depends(get_agent)):
    """
    Execute a natural language query against Prometheus.
    
    The query will be translated to PromQL and executed. If a time range is specified,
    a range query will be performed instead of an instant query.
    """
    try:
        # Add time range to context if specified
        context = request.context or {}
        if request.start_time and request.end_time:
            context.update({
                "time_range": f"{int((request.end_time - request.start_time).total_seconds())}s",
                "start_time": request.start_time.isoformat(),
                "end_time": request.end_time.isoformat(),
                "step": request.step
            })
        
        # Process query using agent
        result = await agent.process_query(request.query, context)
        
        return QueryResponse(
            natural_query=request.query,
            promql=result.result.get("promql", ""),
            result=result.result,
            graph_html=result.result.get("graph_html")
        )
    
    except SherlogError as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Query execution failed: {str(e)}"
        )

@router.get("/translate")
async def translate_query(
    query: str = Query(..., description="Natural language query to translate"),
    context: Optional[str] = Query(None, description="Additional context for translation"),
    agent: ObservabilityAgent = Depends(get_agent)
):
    """Translate a natural language query to PromQL without executing it."""
    try:
        context_dict = {"additional_info": context} if context else None
        result = await agent.process_query(query, context_dict)
        return {
            "natural_query": query,
            "promql": result.result.get("promql", "")
        }
    except SherlogError as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Translation failed: {str(e)}"
        )

@router.get("/explain")
async def explain_query(
    query: str = Query(..., description="PromQL query to explain"),
    agent: ObservabilityAgent = Depends(get_agent)
):
    """Generate a natural language explanation of a PromQL query."""
    try:
        result = await agent.process_query(f"Explain this PromQL query: {query}")
        return {
            "promql": query,
            "explanation": result.result.get("explanation", "")
        }
    except SherlogError as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Explanation failed: {str(e)}"
        ) 