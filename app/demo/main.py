"""
Demo FastAPI application with Prometheus metrics and logging.
"""

import logging
import time
import random
import asyncio
from typing import Dict
from fastapi import FastAPI, Request
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("/opt/logs/app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="Demo Observability App")

# Define Prometheus metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency in seconds',
    ['method', 'endpoint']
)

# Add some business metrics
ACTIVE_USERS = Gauge('active_users', 'Number of active users')
ORDER_PROCESSING = Counter('orders_processed', 'Number of orders processed', ['status'])
CPU_USAGE = Gauge('cpu_usage_percent', 'Simulated CPU usage percentage')
MEMORY_USAGE = Gauge('memory_usage_percent', 'Simulated memory usage percentage')

# Simulated error scenarios
ERROR_SCENARIOS = [
    "Database connection timeout",
    "Payment processing failed",
    "Third-party API unavailable",
    "Cache miss",
    "Rate limit exceeded",
    "Invalid authentication token",
    "Resource not found",
    "Service unavailable"
]

async def generate_random_metrics():
    """Background task to generate random metrics and logs."""
    while True:
        try:
            # Simulate active users (random fluctuation)
            users = random.randint(50, 200)
            ACTIVE_USERS.set(users)
            logger.info(f"Active users: {users}")

            # Simulate order processing
            status = random.choice(['success', 'failed', 'pending'])
            ORDER_PROCESSING.labels(status=status).inc()
            if status == 'failed':
                error = random.choice(ERROR_SCENARIOS)
                logger.error(f"Order processing failed: {error}")
            else:
                logger.info(f"Order processed with status: {status}")

            # Simulate system metrics with some randomness but trending
            cpu = random.uniform(20, 80)
            memory = random.uniform(30, 90)
            CPU_USAGE.set(cpu)
            MEMORY_USAGE.set(memory)

            if cpu > 70:
                logger.warning(f"High CPU usage detected: {cpu}%")
            if memory > 80:
                logger.warning(f"High memory usage detected: {memory}%")

            # Random errors and warnings
            if random.random() < 0.1:  # 10% chance of error
                error_msg = random.choice(ERROR_SCENARIOS)
                logger.error(f"System error: {error_msg}")
            elif random.random() < 0.2:  # 20% chance of warning
                logger.warning("System performance degraded")

        except Exception as e:
            logger.error(f"Error in metrics generation: {str(e)}")

        # Random sleep interval between 1 and 5 seconds
        await asyncio.sleep(random.uniform(1, 5))

@app.on_event("startup")
async def startup_event():
    """Start background tasks on application startup."""
    asyncio.create_task(generate_random_metrics())

# Middleware to track metrics
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)
    
    return response

@app.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint."""
    logger.info("Received request to root endpoint")
    return {"message": "Hello World"}

@app.get("/metrics")
async def metrics():
    """Endpoint for Prometheus metrics."""
    return Response(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )

@app.get("/error")
async def error():
    """Endpoint that generates an error."""
    logger.error("This is a test error")
    return {"error": "This is a test error"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 