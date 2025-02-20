from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .config import Settings
from .routers import prometheus, slack, health, chat
from .integrations.slack import initialize_slack_bot

app = FastAPI(
    title="Sherlog Prometheus Agent",
    description="Natural language interface for Prometheus metrics",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include routers
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(prometheus.router, prefix="/api/v1/prometheus", tags=["prometheus"])
app.include_router(slack.router, prefix="/api/v1/slack", tags=["slack"])
app.include_router(chat.router, prefix="/api", tags=["chat"])

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    try:
        # Initialize Slack bot
        await initialize_slack_bot()
    except Exception as e:
        print(f"Error during startup: {e}")
        raise HTTPException(status_code=500, detail="Failed to initialize services")

@app.get("/")
async def root():
    """Serve the chat interface."""
    return StaticFiles(directory="app/static").get_response("index.html") 