"""
Telemetry helpers for v10.7.

This module provides a unified event envelope for:
 - LLM metrics
 - tool execution metrics
 - cache events (exact + semantic)
 - agent routing decisions
 - pruning outcomes
 - MCP-integrated telemetry streams

All telemetry events are emitted via MCP (if present) and mirrored to local logs.
Existing calls to log_event(...) continue to work unchanged.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, Optional

from mcp import emit_event

logger = logging.getLogger("telemetry_v10_7")


def check_langgraph() -> Dict[str, Any]:
    """Capability-based LangGraph health check used by diagnostics."""

    try:
        from langgraph.graph import StateGraph  # noqa: F401

        return {"ok": True, "info": "StateGraph import succeeded"}
    except Exception as exc:  # pragma: no cover - best-effort diagnostic
        return {"ok": False, "error": str(exc)}


# ---------------------------------------------------------------------------
# Unified Telemetry Envelope
# ---------------------------------------------------------------------------

def _build_envelope(
    agent: str,
    event: str,
    payload: Dict[str, Any],
    *,
    workflow_id: Optional[str] = None,
    node: Optional[str] = None,
    category: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Build a standardized telemetry envelope for v10.7.
    This allows all components (LLM, Tools, Agents, Cache, Meta Learning)
    to produce consistent MCP-compatible events.
    """

    envelope = {
        "timestamp": datetime.utcnow().isoformat(),
        "agent": agent,
        "event": event,
        "category": category or "runtime",
        "workflow_id": workflow_id,
        "node": node,
        "payload": payload or {},
    }

    # Remove None values for compactness
    return {k: v for k, v in envelope.items() if v is not None}


# ---------------------------------------------------------------------------
# Public API (backwards-compatible)
# ---------------------------------------------------------------------------

def log_event(
    agent: str,
    event: str,
    data: Optional[Dict[str, Any]] = None,
    *,
    workflow_id: Optional[str] = None,
    node: Optional[str] = None,
    category: Optional[str] = None,
) -> None:
    """
    Emit a telemetry event via MCP and local logging.
    Fully backwards compatible with earlier versions, but now supports:

        log_event(
            agent="StrategyStack",
            event="branch_selected",
            data={"branch_id": 3},
            workflow_id=context.workflow_id,
            node="STRATEGY_TOT_VOTE",
            category="decision"
        )

    Parameters:
      agent      - Logical agent/tool name
      event      - Event type (e.g. "cache_hit", "latency_fallback")
      data       - Free-form metadata
      workflow_id - Optional workflow identifier
      node        - Optional graph node emitting the event
      category    - Optional event category for grouping
    """

    data = data or {}
    env = _build_envelope(
        agent=agent,
        event=event,
        payload=data,
        workflow_id=workflow_id,
        node=node,
        category=category,
    )

    try:
        # Emit to MCP stream
        emit_event(env)
        logger.debug("Telemetry emitted: %s", env)

    except Exception as exc:
        # MCP failures should never crash the workflow
        logger.warning(f"Failed to emit MCP telemetry: {exc}")
        logger.debug("Failed payload was: %s", env)


__all__ = ["log_event", "check_langgraph"]
