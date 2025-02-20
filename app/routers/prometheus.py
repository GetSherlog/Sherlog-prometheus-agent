from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel
from ..core.prometheus import prometheus_client
from ..core.llm import llm_manager

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

@router.post("/query", response_model=QueryResponse)
async def query_metrics(request: QueryRequest):
    """
    Execute a natural language query against Prometheus.
    
    The query will be translated to PromQL and executed. If a time range is specified,
    a range query will be performed instead of an instant query.
    """
    try:
        # Translate natural language to PromQL
        promql = await llm_manager.translate_to_promql(
            request.query,
            context=request.context
        )
        
        # Execute the query
        if request.start_time and request.end_time:
            result = await prometheus_client.query_range(
                query=promql,
                start_time=request.start_time,
                end_time=request.end_time,
                step=request.step
            )
        else:
            result = await prometheus_client.query(promql)
        
        # Format the results
        formatted_result = prometheus_client.format_result(
            result,
            query_type="range" if request.start_time else "instant"
        )
        
        # Generate graph for range queries
        graph_html = None
        if request.start_time and formatted_result["type"] == "matrix":
            graph_html = prometheus_client.generate_graph(
                formatted_result,
                title=request.query
            )
        
        return QueryResponse(
            natural_query=request.query,
            promql=promql,
            result=formatted_result,
            graph_html=graph_html
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Query execution failed: {str(e)}"
        )

@router.get("/translate")
async def translate_query(
    query: str = Query(..., description="Natural language query to translate"),
    context: Optional[str] = Query(None, description="Additional context for translation")
):
    """Translate a natural language query to PromQL without executing it."""
    try:
        context_dict = {"additional_info": context} if context else None
        promql = await llm_manager.translate_to_promql(query, context=context_dict)
        return {
            "natural_query": query,
            "promql": promql
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Translation failed: {str(e)}"
        )

@router.get("/explain")
async def explain_query(
    query: str = Query(..., description="PromQL query to explain")
):
    """Generate a natural language explanation of a PromQL query."""
    try:
        explanation = await llm_manager.explain_promql(query)
        return {
            "promql": query,
            "explanation": explanation
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Explanation failed: {str(e)}"
        ) 