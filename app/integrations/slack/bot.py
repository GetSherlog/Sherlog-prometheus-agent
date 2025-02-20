from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.fastapi.async_handler import AsyncSlackRequestHandler
from typing import Dict, Any, Callable
import re

from ...config import settings
from ...core.agent import ObservabilityAgent
from ...core.backends.factory import ObservabilityBackendFactory

class SlackBot:
    """Slack bot for handling Prometheus queries."""
    
    def __init__(self):
        self.app = AsyncApp(
            token=settings.slack.bot_token.get_secret_value(),
            signing_secret=settings.slack.app_token.get_secret_value()
        )
        self.handler = AsyncSlackRequestHandler(self.app)
        backend = ObservabilityBackendFactory.create_backend("prometheus", None)
        self.agent = ObservabilityAgent(backend)
        self._setup_event_handlers()
    
    def _setup_event_handlers(self):
        """Set up event handlers for the Slack bot."""
        @self.app.event("app_mention")
        async def handle_mention(event: Dict[str, Any], say: Callable[..., Any]):
            """Handle when the bot is mentioned in a channel."""
            try:
                # Extract the actual message (remove the bot mention)
                message = re.sub(r'<@[A-Z0-9]+>', '', event['text']).strip()
                response = await self._handle_query(message)
                await say(response)
            except Exception as e:
                error_message = f"Sorry, I encountered an error: {str(e)}"
                await say(error_message)

        @self.app.event("message")
        async def handle_direct_message(event: Dict[str, Any], say: Callable[..., Any]):
            """Handle direct messages to the bot."""
            try:
                if event.get('channel_type') == 'im':
                    response = await self._handle_query(event['text'])
                    await say(response)
            except Exception as e:
                error_message = f"Sorry, I encountered an error: {str(e)}"
                await say(error_message)
    
    async def _handle_query(self, query: str) -> str:
        """Handle a natural language query and return formatted results."""
        try:
            # Process query through the agent
            result = await self.agent.process_query(query)
            
            # Format the response
            response_parts = []
            
            # Add the query and thought process
            response_parts.append(f"*Your Query:* {result.query}")
            if result.thought_process:
                response_parts.append(f"*Analysis:*\n{result.thought_process}")
                
            # Add any visualizations if present
            if "visualizations" in result.result:
                response_parts.append("*Visualizations:*")
                for viz in result.result["visualizations"]:
                    if viz.graph:
                        response_parts.append(f"• {viz.title} (Graph generated)")
                        
            # Add any metrics analysis if present
            if "analysis" in result.result:
                analysis = result.result["analysis"]
                if "trends" in analysis:
                    response_parts.append("*Trends:*")
                    for trend in analysis["trends"]:
                        response_parts.append(f"• {trend}")
                if "anomalies" in analysis:
                    response_parts.append("*Anomalies:*")
                    for anomaly in analysis["anomalies"]:
                        response_parts.append(f"• {anomaly}")
                if "insights" in analysis:
                    response_parts.append("*Insights:*")
                    for insight in analysis["insights"]:
                        response_parts.append(f"• {insight}")
            
            return "\n".join(response_parts)
                
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}"
    
    async def handle_event(self, request):
        """Handle incoming Slack events."""
        return await self.handler.handle(request)

# Create a global instance of the Slack bot
_slack_bot = None

async def initialize_slack_bot():
    """Initialize the Slack bot singleton."""
    global _slack_bot
    if _slack_bot is None:
        _slack_bot = SlackBot()
    return _slack_bot

async def handle_slack_event(request):
    """Handle incoming Slack events using the bot singleton."""
    if _slack_bot is None:
        raise RuntimeError("Slack bot not initialized")
    return await _slack_bot.handle_event(request) 