# Sherlog-prometheus-agent 🔍

A natural language interface for Prometheus metrics, powered by AI and delivered through Slack.

## Overview

Sherlog-prometheus-agent enables teams to query Prometheus metrics using natural language through Slack. It translates everyday language into PromQL queries, making observability data more accessible to everyone on your team.

### Key Features

- 🤖 **Natural Language Interface**: Query Prometheus metrics using plain English
- 💬 **Slack Integration**: Get metrics directly in your team's Slack channels
- 🔒 **Flexible LLM Support**: Use local LLMs (via Ollama/llama-cpp-python) or OpenAI
- ⚡ **FastAPI Backend**: High-performance API with async support
- 🐳 **Easy Deployment**: Quick setup with Docker Compose
- 🔄 **Context-Aware**: Supports multi-turn conversations and follow-up questions

## Quick Demo

Want to try Sherlog without setting up Slack or a production Prometheus instance? We've got you covered!

### Demo Prerequisites

- Docker and Docker Compose
- OpenAI API key (optional - you can use local LLM with Ollama instead)

### Running the Demo

1. Clone the repository:
```bash
git clone https://github.com/yourusername/sherlog-prometheus-agent.git
cd sherlog-prometheus-agent
```

2. Run the setup script:
```bash
chmod +x demo/setup.sh
./demo/setup.sh
```

3. The script will:
   - Create a `.env` file with demo settings
   - Start a local Prometheus instance
   - Launch a sample application that generates metrics
   - Start the Sherlog API

4. Visit http://localhost:8000/docs to try out the API directly
   - Try natural language queries like:
     - "Show me the total number of requests to the sample app"
     - "What's the average request latency for the API endpoints?"
     - "Show me the error rate in the last 5 minutes"
     - "Graph the request count by endpoint for the last hour"

5. To stop the demo:
```bash
docker-compose -f docker-compose.demo.yml down
```

## Production Setup

### Prerequisites

- Docker and Docker Compose
- A Slack workspace with bot permissions
- A Prometheus instance
- (Optional) OpenAI API key or local LLM setup

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/sherlog-prometheus-agent.git
cd sherlog-prometheus-agent
```

2. Copy the example environment file:
```bash
cp .env.example .env
```

3. Configure your environment variables in `.env`:
```
SLACK_BOT_TOKEN=xoxb-your-token
SLACK_APP_TOKEN=xapp-your-token
PROMETHEUS_URL=http://your-prometheus:9090
LLM_PROVIDER=openai  # or 'ollama' for local LLM
OPENAI_API_KEY=your-key  # if using OpenAI
```

4. Start the application:
```bash
docker-compose up -d
```

### Usage Examples

Ask questions in your Slack channel like:

- "What's the CPU usage of the authentication service in the last hour?"
- "Show me error rates for the payment service"
- "What's the memory consumption of all pods in the production namespace?"
- "Graph the latency of the API gateway for the last 24 hours"

## Architecture

The project consists of several key components:

- **FastAPI Backend**: Handles request processing and API endpoints
- **LLM Integration**: Translates natural language to PromQL using LangChain
- **Prometheus Client**: Executes PromQL queries and retrieves metrics
- **Slack Bot**: Manages Slack interactions and message handling

## Development

### Local Development Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the development server:
```bash
uvicorn app.main:app --reload
```

### Running Tests

```bash
pytest
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📚 [Documentation](docs/)
- 🐛 [Issue Tracker](../../issues)
- 💬 [Discussions](../../discussions)

## Acknowledgments

- The Prometheus team for their excellent monitoring solution
- The LangChain community for their LLM tools
- The FastAPI team for their modern web framework 