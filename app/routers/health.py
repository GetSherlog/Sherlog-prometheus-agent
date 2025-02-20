from fastapi import APIRouter, HTTPException
from ..core.prometheus import prometheus_client
from ..core.llm import llm_manager

router = APIRouter()

@router.get("/")
async def health_check():
    """Basic health check endpoint."""
    return {"status": "healthy"}

@router.get("/readiness")
async def readiness_check():
    """Check if all required services are available."""
    try:
        # Check Prometheus connection
        await prometheus_client.query("up")
        
        # Check LLM service
        test_query = "Show me the CPU usage"
        await llm_manager.translate_to_promql(test_query)
        
        return {
            "status": "ready",
            "services": {
                "prometheus": "healthy",
                "llm": "healthy"
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Service not ready: {str(e)}"
        ) 