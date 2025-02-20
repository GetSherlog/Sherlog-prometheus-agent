import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from app.main import app
from app.core.llm import llm_manager
from app.core.prometheus import prometheus_client

client = TestClient(app)

@pytest.mark.asyncio
async def test_translate_query():
    """Test the query translation endpoint."""
    response = client.get("/api/v1/prometheus/translate", params={
        "query": "Show me the CPU usage"
    })
    assert response.status_code == 200
    data = response.json()
    assert "promql" in data
    assert "natural_query" in data

@pytest.mark.asyncio
async def test_query_metrics():
    """Test the metrics query endpoint."""
    request_data = {
        "query": "Show me the CPU usage",
        "context": None,
        "start_time": None,
        "end_time": None
    }
    response = client.post("/api/v1/prometheus/query", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert "promql" in data
    assert "result" in data

@pytest.mark.asyncio
async def test_range_query():
    """Test range query functionality."""
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=1)
    
    request_data = {
        "query": "Show me the CPU usage for the last hour",
        "context": None,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "step": "5m"
    }
    response = client.post("/api/v1/prometheus/query", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert "promql" in data
    assert "result" in data
    assert "graph_html" in data

@pytest.mark.asyncio
async def test_explain_query():
    """Test the PromQL explanation endpoint."""
    response = client.get("/api/v1/prometheus/explain", params={
        "query": 'rate(http_requests_total{job="api-server"}[5m])'
    })
    assert response.status_code == 200
    data = response.json()
    assert "promql" in data
    assert "explanation" in data 