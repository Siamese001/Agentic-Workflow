"""Orchestration Handshake Utility - Deterministic agent discovery and delegation.

This module provides deterministic handshake functionality previously
implemented in OrchestrationHandshakeAgent. Converted from agent to utility script
as part of SCRIPT agent conversion (Micro-wave 5).

Usage:
    from agentic_core.L3_orchestration.utils.orchestration_handshake_util import (
        discover_capable_agents, delegate_task, HandshakeResult
    )

    # Discover agents
    capable = discover_capable_agents(registry, "task_description", min_confidence=0.85)
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass
from typing import Any

Logger = logging.getLogger(__name__)


@dataclass
class HandshakeResult:
    """Result of a handshake delegation."""

    status: str
    agent_class: str | None
    method: str | None
    confidence: float
    message: str


def discover_capable_agents(
    registry: Any,
    task: str,
    min_confidence: float = 0.85,
    top_k: int = 10,
    use_cache: bool = True,
    redis_client: Any | None = None,
) -> list[dict[str, Any]]:
    """Discover agents/methods capable of handling a task.

    Args:
        registry: Agent registry to search
        task: Task description to match
        min_confidence: Minimum confidence threshold
        top_k: Maximum number of results
        use_cache: Whether to use Redis caching
        redis_client: Optional Redis client for caching

    Returns:
        List of capable agents with metadata, sorted by confidence
    """
    cache_key = None
    if use_cache and redis_client:
        cache_key = f"handshake_discover:{hashlib.sha256((task + str(min_confidence)).encode()).hexdigest()}"
        cached = redis_client.get(cache_key)
        if cached:
            return json.loads(cached)

    # Search registry for capable methods
    results = registry.find_method(task, top_k=top_k) if hasattr(registry, 'find_method') else []

    capable = []
    for r in results:
        score = r.get("score", 0.0)
        if score >= min_confidence:
            meta = r.get("metadata", {})
            capable.append({
                "agent_class": meta.get("agent_class", "Unknown"),
                "method": meta.get("method", "unknown"),
                "confidence": score,
                "docstring": meta.get("docstring", "")[:200],
            })

    # Sort by confidence descending
    capable.sort(key=lambda x: x["confidence"], reverse=True)

    # Cache results if enabled
    if use_cache and redis_client and capable and cache_key:
        try:
            redis_client.set(cache_key, json.dumps(capable), ex=3600)
        except Exception as e:

            import logging; logging.getLogger(__name__).debug("orchestration_handshake_util: Exception swallowed at L88: %s", e)

    return capable


def delegate_task(
    registry: Any,
    task: str,
    args: dict | None = None,
    kwargs: dict | None = None,
    min_confidence: float = 0.85,
) -> HandshakeResult:
    """Delegate a task to the most capable agent.

    Args:
        registry: Agent registry
        task: Task description
        args: Positional arguments for the task
        kwargs: Keyword arguments for the task
        min_confidence: Minimum confidence threshold

    Returns:
        HandshakeResult with delegation status
    """
    args = args or {}
    kwargs = kwargs or {}

    capable = discover_capable_agents(registry, task, min_confidence)

    if not capable:
        return HandshakeResult(
            status="no_capable_agent",
            agent_class=None,
            method=None,
            confidence=0.0,
            message=f"No agent found for task: {task[:50]}...",
        )

    best = capable[0]

    return HandshakeResult(
        status="delegated",
        agent_class=best["agent_class"],
        method=best["method"],
        confidence=best["confidence"],
        message=f"{best['agent_class']}.{best['method']} ({best['confidence']:.2f})",
    )


def build_handshake_artifact(
    trace_id: str,
    chosen: dict[str, Any],
    candidates: list[dict[str, Any]],
) -> dict[str, Any]:
    """Build a handshake routing decision artifact.

    Args:
        trace_id: Unique trace identifier
        chosen: Selected agent/method
        candidates: All capable agents found

    Returns:
        Artifact dictionary for telemetry
    """
    return {
        "trace_id": trace_id,
        "chosen_agent": chosen.get("agent_class"),
        "chosen_method": chosen.get("method"),
        "confidence": chosen.get("confidence"),
        "candidate_count": len(candidates),
        "candidates": candidates,
        "timestamp": None,  # Set by caller if needed
    }
