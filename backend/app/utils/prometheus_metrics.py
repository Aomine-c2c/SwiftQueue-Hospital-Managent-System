from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
import time
from functools import wraps

# Request metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

# Queue metrics
queue_length = Gauge(
    'queue_length_total',
    'Total number of patients in queue',
    ['status']
)

queue_wait_time_seconds = Histogram(
    'queue_wait_time_seconds',
    'Patient wait time in seconds',
    ['priority']
)

# Database metrics
db_query_duration_seconds = Histogram(
    'db_query_duration_seconds',
    'Database query duration in seconds',
    ['query_type']
)

db_connection_pool_size = Gauge(
    'db_connection_pool_size',
    'Database connection pool size'
)

db_connection_pool_available = Gauge(
    'db_connection_pool_available',
    'Available database connections'
)

# API errors
api_errors_total = Counter(
    'api_errors_total',
    'Total API errors',
    ['endpoint', 'error_type']
)

# Authentication metrics
auth_attempts_total = Counter(
    'auth_attempts_total',
    'Total authentication attempts',
    ['status']
)

# WebSocket metrics
websocket_connections_active = Gauge(
    'websocket_connections_active',
    'Active WebSocket connections'
)

websocket_messages_total = Counter(
    'websocket_messages_total',
    'Total WebSocket messages',
    ['direction']
)

# Cache metrics
cache_hits_total = Counter(
    'cache_hits_total',
    'Total cache hits'
)

cache_misses_total = Counter(
    'cache_misses_total',
    'Total cache misses'
)


def track_request_metrics(method: str, endpoint: str, status: int, duration: float):
    """Track HTTP request metrics"""
    http_requests_total.labels(method=method, endpoint=endpoint, status=status).inc()
    http_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(duration)


def track_queue_metrics(queues: list):
    """Track queue metrics"""
    status_counts = {}
    for queue in queues:
        status = queue.get('status', 'unknown')
        status_counts[status] = status_counts.get(status, 0) + 1
    
    for status, count in status_counts.items():
        queue_length.labels(status=status).set(count)


def track_wait_time(priority: str, wait_time_seconds: float):
    """Track patient wait time"""
    queue_wait_time_seconds.labels(priority=priority).observe(wait_time_seconds)


def track_db_query(query_type: str, duration: float):
    """Track database query metrics"""
    db_query_duration_seconds.labels(query_type=query_type).observe(duration)


def track_error(endpoint: str, error_type: str):
    """Track API errors"""
    api_errors_total.labels(endpoint=endpoint, error_type=error_type).inc()


def track_auth_attempt(success: bool):
    """Track authentication attempts"""
    status = 'success' if success else 'failure'
    auth_attempts_total.labels(status=status).inc()


def track_cache_hit():
    """Track cache hit"""
    cache_hits_total.inc()


def track_cache_miss():
    """Track cache miss"""
    cache_misses_total.inc()


def metrics_endpoint():
    """Metrics endpoint for Prometheus"""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


def monitor_performance(metric_name: str):
    """Decorator to monitor function performance"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                track_db_query(metric_name, duration)
                return result
            except Exception as e:
                duration = time.time() - start_time
                track_error(metric_name, type(e).__name__)
                raise
        return wrapper
    return decorator
