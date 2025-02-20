from flask import Flask, Response, request
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import random
import time
from threading import Thread
import logging
import json
import sys
from datetime import datetime

app = Flask(__name__)

# Configure JSON logging
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name
        }
        if hasattr(record, 'path'):
            log_obj['path'] = record.path
        if hasattr(record, 'method'):
            log_obj['method'] = record.method
        if hasattr(record, 'status'):
            log_obj['status'] = record.status
        if hasattr(record, 'latency'):
            log_obj['latency'] = record.latency
        return json.dumps(log_obj)

logger = logging.getLogger("sample-app")
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Define metrics
REQUEST_COUNT = Counter(
    'sample_app_requests_total',
    'Total number of requests to the sample app',
    ['endpoint', 'method']
)

REQUEST_LATENCY = Histogram(
    'sample_app_request_latency_seconds',
    'Request latency in seconds',
    ['endpoint']
)

ERROR_COUNT = Counter(
    'sample_app_errors_total',
    'Total number of errors in the sample app',
    ['type']
)

# Simulate some background metrics and logs
def background_metrics():
    while True:
        # Simulate requests
        for endpoint in ['/api/users', '/api/orders']:
            # Simulate request count
            method = 'GET' if endpoint == '/api/users' else 'POST'
            req_count = random.randint(1, 5)
            REQUEST_COUNT.labels(endpoint=endpoint, method=method).inc(req_count)
            
            # Simulate latency
            latency = random.uniform(0.1, 2.0)
            REQUEST_LATENCY.labels(endpoint=endpoint).observe(latency)
            
            # Log the simulated requests
            logger.info(
                f"Processed {req_count} requests",
                extra={
                    'path': endpoint,
                    'method': method,
                    'latency': latency
                }
            )
        
        # Simulate errors
        if random.random() < 0.1:  # 10% chance of error
            error_type = 'database_timeout'
            ERROR_COUNT.labels(type=error_type).inc()
            logger.error(
                "Database connection timeout",
                extra={
                    'path': '/api/users',
                    'method': 'GET',
                    'status': 500
                }
            )
            
        if random.random() < 0.05:  # 5% chance of error
            error_type = 'validation_error'
            ERROR_COUNT.labels(type=error_type).inc()
            logger.warning(
                "Request validation failed",
                extra={
                    'path': '/api/orders',
                    'method': 'POST',
                    'status': 400
                }
            )
            
        time.sleep(5)

@app.route('/')
def home():
    REQUEST_COUNT.labels(endpoint='/', method='GET').inc()
    logger.info(
        "Home page accessed",
        extra={
            'path': '/',
            'method': 'GET',
            'status': 200
        }
    )
    return 'Sample App - Check /metrics for Prometheus metrics'

@app.route('/metrics')
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

@app.before_request
def log_request():
    request.start_time = time.time()

@app.after_request
def log_response(response):
    if hasattr(request, 'start_time'):
        latency = time.time() - request.start_time
        logger.info(
            f"Request processed",
            extra={
                'path': request.path,
                'method': request.method,
                'status': response.status_code,
                'latency': latency
            }
        )
    return response

if __name__ == '__main__':
    # Start background metrics generation
    Thread(target=background_metrics, daemon=True).start()
    app.run(host='0.0.0.0', port=8080) 