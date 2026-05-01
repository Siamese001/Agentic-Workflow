"""Metrics Server — HTTP endpoint for Prometheus scraping.

Wave 0: Instrumentation Prerequisites
Provides start_http_server wrapper for exposing agentic-workflow metrics
to Prometheus for operational monitoring.

Design:
- Configurable port (default: 8000)
- Serves /metrics endpoint with Prometheus format
- Graceful shutdown handling
- Thread-safe metric updates

Usage:
    from agentic_core.L6_observability import start_metrics_server

    # Start metrics server on default port
    server = start_metrics_server(port=8000)

    # Run your application...

    # Stop metrics server
    stop_metrics_server(server)
"""

from __future__ import annotations

import ipaddress
import logging
import threading
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_records_execution_trace,
    emit_determinism_digest,
    emit_replay_key,
)

# Deferred import for graceful degradation
try:
    from prometheus_client import CollectorRegistry
    from prometheus_client import start_http_server as _prom_start_server

    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    _prom_start_server = None
    CollectorRegistry = None

from agentic_core.L6_observability.utils.metrics.prometheus_metrics import AGENTIC_REGISTRY

logger = logging.getLogger(__name__)

# Track running servers for cleanup
_running_servers: dict[tuple[str, int], Any] = {}
_server_lock = threading.Lock()


def _validate_bind(addr: str, port: int) -> tuple[str, int]:
    if not isinstance(port, int) or not (1 <= port <= 65535):
        raise ValueError(f"invalid metrics port: {port}")
    ipaddress.ip_address(addr)
    return addr, port


# Bootstrap ADG edge emission
emit_replay_key("metrics_server", "L6")
emit_determinism_digest("metrics_server", "metrics_server_digest")


def _coerce_server_handle(httpd_tuple: Any, addr: str, port: int) -> dict[str, Any]:
    """Normalize prometheus_client return value into a consistent handle."""
    if isinstance(httpd_tuple, tuple):
        server_obj, thread_obj = httpd_tuple
    else:
        server_obj, thread_obj = httpd_tuple, None

    return {
        "server": server_obj,
        "thread": thread_obj,
        "addr": addr,
        "port": port,
    }


def _find_bind_key_for_server(server: Any) -> tuple[str, int] | None:
    """Resolve a tracked bind key for a server handle."""
    if isinstance(server, dict):
        addr = server.get("addr")
        port = server.get("port")
        if isinstance(addr, str) and isinstance(port, int):
            bind_key = (addr, port)
            if bind_key in _running_servers:
                return bind_key

    for bind_key, srv in _running_servers.items():
        if srv is server:
            return bind_key

    return None


def start_metrics_server(
    port: int = 8000,
    addr: str = "127.0.0.1",
    registry: CollectorRegistry | None = None,
) -> Any:
    """Start HTTP server for Prometheus metrics scraping.

    Args:
        port: Port to listen on (default: 8000)
        addr: Address to bind to (default: 0.0.0.0 for all interfaces)
        registry: Custom registry to use (default: AGENTIC_REGISTRY)

    Returns:
        Server handle for shutdown, or None if Prometheus unavailable

    Example:
        >>> server = start_metrics_server(port=8000)
        >>> # ... run application ...
        >>> stop_metrics_server(server)
    """
    if not PROMETHEUS_AVAILABLE:
        logger.warning(
            "prometheus_client not available, metrics server not started. "
            "Install with: pip install prometheus-client",
        )
        return None

    if registry is None:
        registry = AGENTIC_REGISTRY

    try:
        bind_key = _validate_bind(addr, port)
        with _server_lock:
            if bind_key in _running_servers:
                logger.info("Metrics server already running on %s:%s", addr, port)
                return _running_servers[bind_key]

            # Start the server using prometheus_client's built-in server while holding the
            # lock so concurrent callers cannot race into a double bind on the same socket.
            httpd_tuple = _prom_start_server(port=port, addr=addr, registry=registry)
            handle = _coerce_server_handle(httpd_tuple, addr, port)
            _running_servers[bind_key] = handle

        logger.info(
            "metrics_server_started port=%s addr=%s endpoint=%s",
            port,
            addr,
            get_metrics_endpoint_url(port=port, addr=addr),
        )

        _emit_records_execution_trace(
            "metrics_server_start",
            "L6_OBSERVABILITY",
            "metrics_server",
        )

        return handle

    except (AttributeError, OSError, RuntimeError, TypeError, ValueError) as e:  # guardian: allow-return-none-swallow -- metrics server start failure: non-fatal; None signals server unavailable to caller
        logger.error(
            "metrics_server_start_failed",
            extra={"port": port, "addr": addr, "error": str(e)},
            exc_info=True,
        )
        return None


def stop_metrics_server(server: Any) -> bool:
    """Stop a running metrics server.

    Args:
        server: Server handle returned by start_metrics_server()

    Returns:
        True if server stopped successfully, False otherwise
    """
    if server is None:
        return False

    try:
        with _server_lock:
            bind_key = _find_bind_key_for_server(server)

        # Shutdown the server
        server_obj = server.get("server") if isinstance(server, dict) else server
        thread_obj = server.get("thread") if isinstance(server, dict) else None
        if hasattr(server_obj, "shutdown"):
            server_obj.shutdown()
        if hasattr(server_obj, "server_close"):
            server_obj.server_close()
        if thread_obj is not None and hasattr(thread_obj, "join") and thread_obj.is_alive():
            thread_obj.join(timeout=5.0)

        if bind_key is not None:
            with _server_lock:
                _running_servers.pop(bind_key, None)

        logger.info("metrics_server_stopped")
        _emit_records_execution_trace(
            "metrics_server_stop",
            "L6_OBSERVABILITY",
            "metrics_server",
        )

        return True

    except (AttributeError, OSError, RuntimeError, TypeError, ValueError) as e:
        logger.error(
            "metrics_server_stop_failed",
            extra={"error": str(e)},
            exc_info=True,
        )
        return False


def get_metrics_endpoint_url(port: int = 8000, addr: str = "127.0.0.1") -> str:
    """Get the URL for the metrics endpoint.

    Args:
        port: Port the metrics server is running on
        addr: Address the metrics server is bound to

    Returns:
        Full URL to the metrics endpoint
    """
    return f"http://{addr}:{port}/metrics"


def is_metrics_server_running(port: int = 8000) -> bool:
    """Check if a metrics server is running on the given port.

    Args:
        port: Port to check

    Returns:
        True if server is running, False otherwise
    """
    with _server_lock:
        return any(bound_port == port for _, bound_port in _running_servers.keys())


def get_running_server_ports() -> list[int]:
    """Get list of ports where metrics servers are running.

    Returns:
        List of port numbers
    """
    with _server_lock:
        return sorted({port for _, port in _running_servers.keys()})


class MetricsServerContext:
    """Context manager for metrics server lifecycle.

    Usage:
        with MetricsServerContext(port=8000) as server:
            # Metrics server is running
            run_application()
        # Metrics server is stopped
    """

    def __init__(self, port: int = 8000, addr: str = "127.0.0.1"):
        self.port = port
        self.addr = addr
        self.server: Any = None

    def __enter__(self) -> Any:
        self.server = start_metrics_server(port=self.port, addr=self.addr)
        return self.server

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if self.server:
            stop_metrics_server(self.server)


def get_server_status() -> dict[str, Any]:
    """Get status of metrics servers.

    Returns:
        Dictionary with server status information
    """
    with _server_lock:
        return {
            "prometheus_available": PROMETHEUS_AVAILABLE,
            "running_servers": len(_running_servers),
            "bindings": [{"addr": addr, "port": port} for addr, port in _running_servers.keys()],
            "metrics_endpoint_template": "http://localhost:{port}/metrics",
        }
