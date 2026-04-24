"""L0 Router ADG risk-signal adapter.

Exposes a narrow, synchronous helper for the routing hot path that turns
a symbol / file / adg_name into a structured risk envelope derived from
the current ADG snapshot.

Usage (safe at module scope)::

    from agentic_core.L0_routing.utils.adg_risk_signal import (
        risk_signal_for,
        is_safety_critical,
    )

    envelope = risk_signal_for("agentic_core.L5_safety.guardrail")
    if envelope["risk_band"] == "HIGH":
        router.prefer_synchronous_path(envelope["adg_name"])

Design invariants (see plan ``runtime-adg-acceleration-b4f2a1``):
    1. Pure-read, no MCP dependency — direct SQLite via ``RuntimeADGQuery``.
    2. Fail-soft — if ADG is unavailable, every helper returns a neutral
       envelope with ``"available": False`` so routers can branch cleanly.
    3. Sub-10ms typical. The adapter caches the singleton query instance.
    4. No cross-layer leakage: this module imports from ``tools.adg`` only
       because tools is the canonical location for the runtime library
       (see MCP Registry doctrine — tools/ hosts the SSOT for ADG access).
"""

from __future__ import annotations

import logging
from typing import Any

try:
    from tools.adg.runtime_query import RiskEnvelope, get_default_query
except ImportError as exc:  # pragma: no cover - import hygiene
    logging.getLogger(__name__).warning(
        "ADG runtime_query unavailable: %s; risk signals will be neutral", exc
    )
    RiskEnvelope = None  # type: ignore[assignment,misc]
    get_default_query = lambda: None  # type: ignore[assignment]

logger = logging.getLogger(__name__)

NEUTRAL_ENVELOPE: dict[str, Any] = {
    "available": False,
    "node_id": None,
    "adg_name": None,
    "file_path": None,
    "layer": None,
    "fan_in": 0,
    "fan_out": 0,
    "archetype": "UNKNOWN",
    "risk_band": "LOW",
    "impact_score": 0.0,
    "snapshot_id": None,
}


def _envelope_dict(env: Any) -> dict[str, Any]:
    """Convert ``RiskEnvelope`` to a router-friendly dict with ``available``."""
    if env is None:
        return dict(NEUTRAL_ENVELOPE)
    as_dict: dict[str, Any] = dict(env.to_dict())
    as_dict["available"] = env.error != "node_not_found"
    return as_dict


def risk_signal_for(identifier: str) -> dict[str, Any]:
    """Return a risk envelope for a symbol name or node id.

    Safe to call on router hot paths. Never raises.

    Args:
        identifier: ``adg_name`` (e.g. ``"agentic_core.L5_safety.guardrail"``)
            or a raw ``node_id``.

    Returns:
        dict with stable schema: ``node_id``, ``adg_name``, ``file_path``,
        ``layer``, ``fan_in``, ``fan_out``, ``archetype``, ``risk_band``
        (``HIGH``/``MEDIUM``/``LOW``), ``impact_score``, ``snapshot_id``,
        and ``available`` (``False`` when ADG is unavailable OR the node
        does not exist in the graph).
    """
    q = get_default_query()
    if q is None:
        return dict(NEUTRAL_ENVELOPE)
    try:
        env = q.blast_radius(identifier)
    except (AttributeError, TypeError, ValueError) as exc:
        logger.warning("risk_signal_for(%s) failed: %s", identifier, exc)
        return dict(NEUTRAL_ENVELOPE)
    return _envelope_dict(env)


def is_safety_critical(identifier: str) -> bool:
    """Return True if the symbol is on the L5 safety plane or a gatekeeper."""
    env = risk_signal_for(identifier)
    return env.get("archetype") == "SAFETY_GATEKEEPER" or (env.get("layer") or "").startswith("L5")


def is_central_dependency(identifier: str, min_fan_in: int = 20) -> bool:
    """Return True if the symbol has high fan-in (central dependency).

    Used by routers to decide whether to pin traffic to a canary or require
    stricter validation before routing requests that touch this module.
    """
    env = risk_signal_for(identifier)
    if not env.get("available"):
        return False
    return (env.get("fan_in") or 0) >= min_fan_in


def route_policy_hint(identifier: str) -> dict[str, Any]:
    """Derive a small policy hint dict for a router.

    Encodes the current heuristic in one place so routers stay simple.
    Fields:
        - ``prefer_canary``: tighten traffic shaping for high-impact nodes
        - ``require_hitl``: high-risk safety or central dependency → surface
          to runtime HITL (per ADR-023) instead of auto-executing
        - ``circuit_breaker_armed``: near-critical path — arm breaker early
        - ``rationale``: short string explaining the hint
    """
    env = risk_signal_for(identifier)
    available = env.get("available", False)
    band = env.get("risk_band", "LOW")
    archetype = env.get("archetype", "UNKNOWN")

    prefer_canary = available and band == "HIGH"
    require_hitl = available and (
        archetype == "SAFETY_GATEKEEPER" or (band == "HIGH" and archetype == "CENTRAL_DEPENDENCY")
    )
    circuit_breaker_armed = available and band in ("HIGH", "MEDIUM")

    parts: list[str] = []
    if not available:
        parts.append("ADG unavailable; defaulting to neutral policy")
    if require_hitl:
        parts.append(f"require_hitl ({archetype})")
    if prefer_canary:
        parts.append("prefer_canary (HIGH risk band)")
    if circuit_breaker_armed:
        parts.append("arm_breaker")

    return {
        "prefer_canary": prefer_canary,
        "require_hitl": require_hitl,
        "circuit_breaker_armed": circuit_breaker_armed,
        "rationale": "; ".join(parts) or "low-risk default",
        "envelope": env,
    }


__all__ = [
    "risk_signal_for",
    "is_safety_critical",
    "is_central_dependency",
    "route_policy_hint",
    "NEUTRAL_ENVELOPE",
]
