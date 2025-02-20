"""Test configuration and fixtures for the Sherlog Prometheus Agent."""

import asyncio
from typing import AsyncGenerator, Generator, Dict, Any, Optional
import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient
from redis.asyncio import Redis
from pydantic import BaseModel, AnyHttpUrl

from app.config import Settings, Environment, PrometheusSettings, RedisSettings

class BackendConfig(BaseModel):
    """Configuration for a backend."""
    name: str

class MockQueryBackend:
    """Mock query backend for testing."""
    
    def __init__(self, config: BackendConfig):
        self.config = config
        self._initialized = False
    
    async def initialize(self) -> None:
        self._initialized = True
    
    async def health_check(self) -> bool:
        return True
    
    async def close(self) -> None:
        self._initialized = False
    
    async def query(self, query: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {"result": "mock_data"}
    
    async def validate_query(self, query: str) -> bool:
        return True

class MockNotificationBackend:
    """Mock notification backend for testing."""
    
    def __init__(self, config: BackendConfig):
        self.config = config
        self._initialized = False
    
    async def initialize(self) -> None:
        self._initialized = True
    
    async def health_check(self) -> bool:
        return True
    
    async def close(self) -> None:
        self._initialized = False
    
    async def send_notification(self, payload: str, target: Optional[str] = None, **kwargs) -> bool:
        return True
    
    async def validate_payload(self, payload: str) -> bool:
        return True

class MockMetricsBackend:
    """Mock metrics backend for testing."""
    
    def __init__(self, config: BackendConfig):
        self.config = config
        self._initialized = False
    
    async def initialize(self) -> None:
        self._initialized = True
    
    async def health_check(self) -> bool:
        return True
    
    async def close(self) -> None:
        self._initialized = False
    
    async def get_metric(self, metric_name: str, labels: Optional[Dict[str, str]] = None, 
                        time_range: Optional[tuple[str, str]] = None) -> float:
        return 42.0
    
    async def list_metrics(self, pattern: Optional[str] = None) -> list[str]:
        return ["mock_metric_1", "mock_metric_2"]

    async def query(self, query: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {"result": "mock_data"}
    
    async def validate_query(self, query: str) -> bool:
        return True

class MockLLMBackend:
    """Mock LLM backend for testing."""
    
    def __init__(self, config: BackendConfig):
        self.config = config
        self._initialized = False
    
    async def initialize(self) -> None:
        self._initialized = True
    
    async def health_check(self) -> bool:
        return True
    
    async def close(self) -> None:
        self._initialized = False
    
    async def generate(self, prompt: str, max_tokens: Optional[int] = None,
                      temperature: float = 0.7, **kwargs) -> str:
        return "Mock LLM response"
    
    async def embed(self, text: str | list[str]) -> list[list[float]]:
        return [[0.1, 0.2, 0.3]]

@pytest.fixture(scope="session")
def settings() -> Settings:
    """Get test settings with overridden values."""
    settings = Settings()
    settings.environment = Environment.DEVELOPMENT
    settings.debug = True
    return settings

@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an event loop for testing."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="session")
async def redis_client(settings: Settings) -> AsyncGenerator[Redis, None]:
    """Create a Redis client for testing."""
    client = Redis.from_url(settings.redis.url)
    try:
        await client.ping()
    except Exception as e:
        pytest.skip(f"Redis not available: {e}")
    
    yield client
    await client.close()

@pytest_asyncio.fixture
async def clear_redis(redis_client: Redis) -> AsyncGenerator[None, None]:
    """Clear Redis before and after each test."""
    await redis_client.flushdb()
    yield
    await redis_client.flushdb()

@pytest.fixture
def mock_query_backend() -> MockQueryBackend:
    """Create a mock query backend."""
    return MockQueryBackend(BackendConfig(name="mock_query"))

@pytest.fixture
def mock_notification_backend() -> MockNotificationBackend:
    """Create a mock notification backend."""
    return MockNotificationBackend(BackendConfig(name="mock_notification"))

@pytest.fixture
def mock_metrics_backend() -> MockMetricsBackend:
    """Create a mock metrics backend."""
    return MockMetricsBackend(BackendConfig(name="mock_metrics"))

@pytest.fixture
def mock_llm_backend() -> MockLLMBackend:
    """Create a mock LLM backend."""
    return MockLLMBackend(BackendConfig(name="mock_llm"))

@pytest_asyncio.fixture
async def test_app(
    settings: Settings,
    mock_query_backend: MockQueryBackend,
    mock_notification_backend: MockNotificationBackend,
    mock_metrics_backend: MockMetricsBackend,
    mock_llm_backend: MockLLMBackend
) -> AsyncGenerator[FastAPI, None]:
    """Create a test FastAPI application."""
    app = FastAPI()
    app.state.settings = settings
    app.state.query_backend = mock_query_backend
    app.state.notification_backend = mock_notification_backend
    app.state.metrics_backend = mock_metrics_backend
    app.state.llm_backend = mock_llm_backend
    
    yield app

@pytest_asyncio.fixture
async def test_client(test_app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client for the FastAPI application."""
    async with AsyncClient(app=test_app, base_url="http://test") as client:
        yield client 