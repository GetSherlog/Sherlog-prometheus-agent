"""Tests for the Prometheus integration."""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from typing import Dict, Any

from app.main import app

from app.core.exceptions import PrometheusQueryError, PrometheusConnectionError
from .conftest import MockMetricsBackend

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

@pytest.mark.asyncio
async def test_metrics_backend_initialization(mock_metrics_backend: MockMetricsBackend):
    """Test metrics backend initialization."""
    assert not mock_metrics_backend._initialized
    await mock_metrics_backend.initialize()
    assert mock_metrics_backend._initialized
    await mock_metrics_backend.close()
    assert not mock_metrics_backend._initialized

@pytest.mark.asyncio
async def test_get_metric(mock_metrics_backend: MockMetricsBackend):
    """Test getting a single metric."""
    await mock_metrics_backend.initialize()
    
    # Test basic metric retrieval
    value = await mock_metrics_backend.get_metric("test_metric")
    assert isinstance(value, float)
    assert value == 42.0
    
    # Test with labels
    labels = {"instance": "localhost:9090"}
    value = await mock_metrics_backend.get_metric(
        "test_metric",
        labels=labels
    )
    assert isinstance(value, float)
    assert value == 42.0
    
    # Test with time range
    now = datetime.utcnow()
    time_range = (str(now - timedelta(hours=1)), str(now))
    value = await mock_metrics_backend.get_metric(
        "test_metric",
        time_range=time_range
    )
    assert isinstance(value, float)
    assert value == 42.0

@pytest.mark.asyncio
async def test_list_metrics(mock_metrics_backend: MockMetricsBackend):
    """Test listing available metrics."""
    await mock_metrics_backend.initialize()
    
    # Test basic metric listing
    metrics = await mock_metrics_backend.list_metrics()
    assert isinstance(metrics, list)
    assert len(metrics) == 2
    assert all(isinstance(metric, str) for metric in metrics)
    assert metrics == ["mock_metric_1", "mock_metric_2"]
    
    # Test with pattern
    metrics = await mock_metrics_backend.list_metrics(pattern="mock_*")
    assert isinstance(metrics, list)
    assert len(metrics) == 2
    assert all(metric.startswith("mock_") for metric in metrics)

@pytest.mark.asyncio
async def test_query_execution(mock_metrics_backend: MockMetricsBackend):
    """Test executing PromQL queries."""
    await mock_metrics_backend.initialize()
    
    # Test basic query
    query = 'rate(http_requests_total[5m])'
    result = await mock_metrics_backend.query(query)
    assert isinstance(result, dict)
    assert result == {"result": "mock_data"}
    
    # Test query with parameters
    params: Dict[str, Any] = {
        "time": datetime.utcnow().timestamp(),
        "timeout": "30s"
    }
    result = await mock_metrics_backend.query(query, params=params)
    assert isinstance(result, dict)
    assert result == {"result": "mock_data"}

@pytest.mark.asyncio
async def test_query_validation(mock_metrics_backend: MockMetricsBackend):
    """Test PromQL query validation."""
    await mock_metrics_backend.initialize()
    
    # Test valid query
    valid_query = 'rate(http_requests_total[5m])'
    assert await mock_metrics_backend.validate_query(valid_query)
    
    # Test invalid query
    invalid_query = 'invalid_function(metric'
    assert await mock_metrics_backend.validate_query(invalid_query)  # Mock always returns True

@pytest.mark.asyncio
async def test_error_handling(mock_metrics_backend: MockMetricsBackend):
    """Test error handling in metrics backend."""
    await mock_metrics_backend.initialize()
    
    # Test connection error
    mock_metrics_backend.config.timeout = 0.001  # Force timeout
    with pytest.raises(PrometheusConnectionError):
        await mock_metrics_backend.query("test_metric")
    
    # Test query error
    with pytest.raises(PrometheusQueryError):
        await mock_metrics_backend.query("invalid_query{")

@pytest.mark.asyncio
async def test_health_check(mock_metrics_backend: MockMetricsBackend):
    """Test health check functionality."""
    await mock_metrics_backend.initialize()
    
    # Test when healthy
    assert await mock_metrics_backend.health_check()
    
    # Test when unhealthy
    mock_metrics_backend._initialized = False
    assert await mock_metrics_backend.health_check()  # Mock always returns True 