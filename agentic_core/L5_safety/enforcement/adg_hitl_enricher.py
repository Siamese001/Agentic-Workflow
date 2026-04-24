"""ADG-backed enrichment for runtime HITL (ADR-023) packets.

This is a *pure-read* helper used by L5 exit-control when assembling a
packet for a human reviewer. It adds structural context to the packet so
the reviewer sees:

- the symbol's **archetype** (CENTRAL_DEPENDENCY / ORCHESTRATOR / STATE_NODE
  / SAFETY_GATEKEEPER) per ADG canonical invariants §5,
- the top-N **upstream callers** whose traffic depends on the decision,
- which of the **5 ADG Surfaces** (Execution / Write / Security / State /
  Observability) the decision touches,
- whether there are any **swallow sites** that could silently hide a
  downstream failure, and
- the **snapshot provenance** stamp so the reviewer can gauge freshness.

This is distinct from the developer-loop Author-Gate (see
``.windsurf/rules/author-gate-enforcement.md``). Runtime HITL is v30 step
[5] per ADR-023; this helper only enriches the packet — it does not make
decisions.

Failure mode: every helper is fail-soft — if the ADG is unavailable, the
returned packet fragment just lacks the enrichment fields. The caller
must never block on ADG availability.
"""

from __future__ import annotations

import logging
from typing import Any

try:
    from tools.adg.runtime_query import RuntimeADGQuery, get_default_query
except ImportError as exc:  # pragma: no cover - import hygiene
    logging.getLogger(__name__).warning(
        "ADG runtime_query unavailable: %s; HITL enrichment will be empty", exc
    )
    RuntimeADGQuery = None  # type: ignore[assignment,misc]
    get_default_query = lambda: None  # type: ignore[assignment]

logger = logging.getLogger(__name__)

# 5 ADG Surfaces — inferred from layer + file_path patterns.
_SURFACE_PATTERNS: dict[str, tuple[str, ...]] = {
    "Execution": ("L2_execution", "execution_adapter", "executor", "runner"),
    "Write": ("write_gateway", "canonical_store", "writes_to", "uwg"),
    "Security": ("L5_safety", "guardrail", "policy", "auth", "credential"),
    "State": ("L4_state", "cache", "memory", "checkpoint"),
    "Observability": ("L6_observability", "otel", "audit", "trace", "evidence"),
}


def _classify_surfaces(file_path: str | None, layer: str | None) -> list[str]:
    """Return the ADG Surfaces a node intersects."""
    if not file_path and not layer:
        return []
    hay = ((file_path or "") + " " + (layer or "")).lower()
    return [surface for surface, pats in _SURFACE_PATTERNS.items() if any(p in hay for p in pats)]


def enrich_hitl_packet(
    packet: dict[str, Any],
    target_identifier: str,
    *,
    max_callers: int = 3,
    swallow_depth: int = 3,
) -> dict[str, Any]:
    """Return ``packet`` with an ``adg_context`` block appended.

    Does not mutate the original packet. Safe to call inline — never raises,
    never blocks longer than a single SQLite read.

    Args:
        packet: existing HITL packet (any shape — we only add a new key).
        target_identifier: the ``adg_name`` or ``node_id`` the decision is
            about (e.g. the function/module the pending action will touch).
        max_callers: cap on upstream callers attached to the packet.
        swallow_depth: BFS depth for backward flows_to traversal.

    Returns:
        A shallow copy of ``packet`` with a new ``"adg_context"`` key, or
        with ``"adg_context": {"available": False, "reason": "<why>"}``
        when enrichment is not possible.
    """
    enriched: dict[str, Any] = dict(packet)
    q = get_default_query()
    if q is None:
        enriched["adg_context"] = {"available": False, "reason": "no_snapshot"}
        return enriched
    try:
        env = q.blast_radius(target_identifier)
        node_id = env.node_id
        surfaces = _classify_surfaces(env.file_path, env.layer)
        callers: list[dict[str, Any]] = []
        swallow_sites: list[dict[str, Any]] = []
        centrality: dict[str, Any] = {}
        if node_id is not None:
            callers = q.upstream_callers(node_id, k=max_callers, relation_type="imports")
            swallow_sites = q.swallow_sites_reaching(node_id, depth=swallow_depth, max_hits=5)
            centrality = q.hotspot_info(target_identifier)
        enriched["adg_context"] = {
            "available": env.error != "node_not_found",
            "target": {
                "node_id": env.node_id,
                "adg_name": env.adg_name,
                "file_path": env.file_path,
                "layer": env.layer,
            },
            "archetype": env.archetype,
            "risk_band": env.risk_band,
            "impact_score": env.impact_score,
            "fan_in": env.fan_in,
            "fan_out": env.fan_out,
            "surfaces": surfaces,
            "top_upstream_callers": callers,
            "swallow_sites_reaching": swallow_sites,
            "centrality": {
                k: centrality.get(k)
                for k in (
                    "betweenness_approx",
                    "degree_centrality",
                    "criticality_score",
                    "violation_count",
                    "cross_layer_edges",
                )
                if centrality.get(k) is not None
            },
            "provenance": q.provenance(),
        }
    except (AttributeError, TypeError, ValueError) as exc:
        logger.warning("enrich_hitl_packet(%s) failed: %s", target_identifier, exc)
        enriched["adg_context"] = {"available": False, "reason": f"error:{exc!s}"}
    return enriched


def hitl_priority_hint(packet: dict[str, Any]) -> str:
    """Derive a simple priority hint (``URGENT`` / ``HIGH`` / ``NORMAL``) from
    the enrichment block.

    This is intentionally small — the human reviewer makes the real call.
    The hint is computed ONLY from already-enriched fields; it does not hit
    the ADG again.
    """
    ctx = (packet or {}).get("adg_context") or {}
    if not ctx.get("available"):
        return "NORMAL"
    band = ctx.get("risk_band", "LOW")
    archetype = ctx.get("archetype", "UNKNOWN")
    surfaces = set(ctx.get("surfaces") or [])
    swallows = len(ctx.get("swallow_sites_reaching") or [])
    if "Security" in surfaces or archetype == "SAFETY_GATEKEEPER":
        return "URGENT"
    if band == "HIGH" and ("Write" in surfaces or archetype == "CENTRAL_DEPENDENCY"):
        return "URGENT"
    if band == "HIGH" or swallows >= 2:
        return "HIGH"
    if band == "MEDIUM":
        return "HIGH" if "Write" in surfaces else "NORMAL"
    return "NORMAL"


__all__ = ["enrich_hitl_packet", "hitl_priority_hint"]
