from fastapi import APIRouter, Request, HTTPException
from ..integrations.slack import handle_slack_event

router = APIRouter()

@router.post("/events")
async def slack_events(request: Request):
    """Handle incoming Slack events."""
    try:
        return await handle_slack_event(request)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process Slack event: {str(e)}"
        )

@router.post("/interactive")
async def slack_interactive(request: Request):
    """Handle interactive components from Slack."""
    try:
        # Get the form data
        form_data = await request.form()
        
        # TODO: Implement interactive component handling
        # This would handle button clicks, modal submissions, etc.
        
        return {"message": "Interactive component processed"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process interactive component: {str(e)}"
        ) 