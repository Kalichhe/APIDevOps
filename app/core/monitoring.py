"""
Módulo de monitoreo y observabilidad.
Integración con Prometheus (métricas) y logging local estándar.
"""

import logging
import time
from collections import defaultdict

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from prometheus_client import Counter, Histogram, Gauge

# ── Métricas Prometheus ──
REQUEST_COUNT = Counter(
    "apidevops_requests_total",
    "Total de requests procesados",
    ["method", "endpoint", "status"],
)

REQUEST_DURATION = Histogram(
    "apidevops_request_duration_seconds",
    "Duración de requests en segundos",
    ["method", "endpoint"],
)

DB_CONNECTIONS = Gauge(
    "apidevops_db_connections_active",
    "Conexiones activas a la base de datos",
)

REQUEST_ERRORS = Counter(
    "apidevops_requests_errors_total",
    "Total de errores en requests",
    ["method", "endpoint", "error_type"],
)

# ── Logger estándar ──
logger = logging.getLogger(__name__)

TRACKED_PATH_PREFIXES = ("/api/v1", "/api/v2")

# Paths commonly used by internet scanners and exploit bots.
NOISE_PATH_KEYWORDS = (
    "/.env",
    "/wp-",
    "/wordpress",
    "/phpmyadmin",
    "/vendor/phpunit",
    "/autodiscover",
    "/boaform",
    "/cgi-bin",
    "/actuator",
    "/sdk",
)


def _is_noise_path(path: str) -> bool:
    lowered = path.lower()
    if any(keyword in lowered for keyword in NOISE_PATH_KEYWORDS):
        return True

    # Most bots probe PHP endpoints against non-PHP APIs.
    if lowered.endswith(".php") or ".php?" in lowered:
        return True

    return False


def _get_endpoint_label(request: Request) -> str:
    route = request.scope.get("route")
    if route is not None and getattr(route, "path", None):
        return route.path
    return request.url.path


def _is_internal_path(path: str) -> bool:
    return path in {"/", "/docs", "/openapi.json", "/metrics", "/metrics-summary"}


def _is_business_api_path(path: str) -> bool:
    return any(path.startswith(prefix) for prefix in TRACKED_PATH_PREFIXES)


def setup_logging():
    """Configura logging estándar de la aplicación."""
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s - %(name)s - %(message)s",
    )


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware para recolectar métricas Prometheus."""

    async def dispatch(self, request: Request, call_next):
        # Inicia timer
        start_time = time.time()

        # Procesa request
        response = await call_next(request)

        # Calcula duración
        duration = time.time() - start_time

        # Registra métricas
        endpoint = _get_endpoint_label(request)
        method = request.method
        status = response.status_code

        # Only track business API routes to keep metrics clean.
        if not _is_business_api_path(endpoint):
            return response

        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status).inc()

        REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)

        if status >= 400:
            error_type = "client_error" if status < 500 else "server_error"
            REQUEST_ERRORS.labels(
                method=method, endpoint=endpoint, error_type=error_type
            ).inc()

        logger.debug(
            f"{method} {endpoint} - Status: {status} - Duration: {duration:.3f}s"
        )

        return response


def log_event(event_name: str, details: dict = None):
    """Registra un evento en logs con detalles contextuales."""
    message = f"Event: {event_name}"
    if details:
        message += f" | {details}"
    logger.info(message)


def log_error(error_name: str, error_details: str, context: dict = None):
    """Registra un error en logs."""
    message = f"ERROR: {error_name} - {error_details}"
    if context:
        message += f" | Context: {context}"
    logger.error(message)


def get_metrics_snapshot() -> dict:
    """Resume métricas clave en formato JSON para dashboards rápidos."""
    total_requests = 0.0
    total_errors = 0.0
    filtered_total_requests = 0.0
    filtered_total_errors = 0.0
    status_breakdown = defaultdict(float)
    endpoint_breakdown = defaultdict(float)
    filtered_status_breakdown = defaultdict(float)
    filtered_endpoint_breakdown = defaultdict(float)
    avg_duration_by_endpoint = {}
    filtered_avg_duration_by_endpoint = {}

    duration_sum = defaultdict(float)
    duration_count = defaultdict(float)

    for metric in REQUEST_COUNT.collect():
        for sample in metric.samples:
            if sample.name.endswith("_total"):
                value = float(sample.value)
                total_requests += value
                status = str(sample.labels.get("status", "unknown"))
                endpoint = str(sample.labels.get("endpoint", "unknown"))
                status_breakdown[status] += value
                endpoint_breakdown[endpoint] += value

                if _is_business_api_path(endpoint):
                    filtered_total_requests += value
                    filtered_status_breakdown[status] += value
                    filtered_endpoint_breakdown[endpoint] += value

    for metric in REQUEST_ERRORS.collect():
        for sample in metric.samples:
            if sample.name.endswith("_total"):
                value = float(sample.value)
                total_errors += value
                endpoint = str(sample.labels.get("endpoint", "unknown"))
                if _is_business_api_path(endpoint):
                    filtered_total_errors += value

    for metric in REQUEST_DURATION.collect():
        for sample in metric.samples:
            endpoint = str(sample.labels.get("endpoint", "unknown"))
            if sample.name.endswith("_sum"):
                duration_sum[endpoint] += float(sample.value)
            elif sample.name.endswith("_count"):
                duration_count[endpoint] += float(sample.value)

    for endpoint, total in duration_sum.items():
        count = duration_count.get(endpoint, 0.0)
        avg_duration_by_endpoint[endpoint] = (
            round(total / count, 6) if count > 0 else 0.0
        )
        if _is_business_api_path(endpoint):
            filtered_avg_duration_by_endpoint[endpoint] = avg_duration_by_endpoint[
                endpoint
            ]

    error_rate = (
        round((total_errors / total_requests) * 100, 2) if total_requests > 0 else 0.0
    )
    filtered_error_rate = (
        round((filtered_total_errors / filtered_total_requests) * 100, 2)
        if filtered_total_requests > 0
        else 0.0
    )

    top_endpoints = sorted(
        endpoint_breakdown.items(), key=lambda item: item[1], reverse=True
    )[:5]
    filtered_top_endpoints = sorted(
        filtered_endpoint_breakdown.items(), key=lambda item: item[1], reverse=True
    )[:5]

    return {
        "total_requests": int(filtered_total_requests),
        "total_errors": int(filtered_total_errors),
        "error_rate_percent": filtered_error_rate,
        "status_breakdown": dict(sorted(filtered_status_breakdown.items())),
        "top_endpoints": [
            {"endpoint": endpoint, "requests": int(count)}
            for endpoint, count in filtered_top_endpoints
        ],
        "avg_duration_seconds_by_endpoint": filtered_avg_duration_by_endpoint,
        "raw_summary": {
            "total_requests": int(total_requests),
            "total_errors": int(total_errors),
            "error_rate_percent": error_rate,
            "status_breakdown": dict(sorted(status_breakdown.items())),
            "top_endpoints": [
                {"endpoint": endpoint, "requests": int(count)}
                for endpoint, count in top_endpoints
            ],
            "avg_duration_seconds_by_endpoint": avg_duration_by_endpoint,
        },
    }
