"""
Slack integration package for Sherlog-prometheus-agent.
"""

from .bot import initialize_slack_bot, handle_slack_event

__all__ = ['initialize_slack_bot', 'handle_slack_event'] 