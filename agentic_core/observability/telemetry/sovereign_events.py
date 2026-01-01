"""
Sovereign Event Emission for MCP Observability

Provides centralized event emission for all MCP integrations:
- Connection events (start, success, fail, timeout)
- CRITIQUE events for exhausted retries
- Structured logging with timestamps

Events are logged and can be forwarded to external systems (Redis pub/sub, etc.)
"""
import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional

logger: Any = logging.getLogger(__name__)

_event_handlers: list = []


def register_handler(handler: callable) -> None:
    """
    Register an external event handler.

    Args:
        handler: Callable that receives (event_type, event_data)
    """
    _event_handlers.append(handler)


def emit_event(
    event_type: str,
    data: Dict[str, Any],
    source: str = "mcp_integration",
) -> None:
    """
    Emit sovereign event for MCP observability.

    Events are logged and forwarded to any registered handlers.

    Args:
        event_type: Type of event (MCP_CALL_START, MCP_CALL_SUCCESS, etc.)
        data: Event data dictionary
        source: Source identifier (default: mcp_integration)
    """
    event: Dict[str, Any] = {
        "timestamp": datetime.utcnow().isoformat(),
        "type": event_type,
        "data": data,
        "source": source,
    }

    logger.info(f"[SOVEREIGN_EVENT] {json.dumps(event)}")

    for handler in _event_handlers:
        try:
            handler(event_type, event)
        except Exception as e:
            logger.warning(f"[SOVEREIGN_EVENT] Handler failed: {e}")


def emit_mcp_connect(
    client_name: str,
    status: str,
    details: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Emit MCP connection event.

    Args:
        client_name: Name of the MCP client
        status: Connection status (connected, failed, degraded)
        details: Optional additional details
    """
    emit_event(
        "MCP_CONNECT",
        {
            "client": client_name,
            "status": status,
            **(details or {}),
        },
    )


def emit_mcp_health(
    client_name: str,
    healthy: bool,
    metrics: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Emit MCP health check event.

    Args:
        client_name: Name of the MCP client
        healthy: Whether the client is healthy
        metrics: Optional health metrics
    """
    emit_event(
        "MCP_HEALTH",
        {
            "client": client_name,
            "healthy": healthy,
            **(metrics or {}),
        },
    )
