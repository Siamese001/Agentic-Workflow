"""REQ Evidence Emitter — explicit binding from runtime call sites to REQ_IDs.

Companion to ``lifecycle_trace_contract`` and ``otel_lifecycle_bridge``. Lets
code paths declare which requirements they satisfy at runtime by emitting a
specially-formatted DEBUG record on a dedicated ``adg.req_evidence`` logger.

Why a separate emitter?
-----------------------
``lifecycle_trace_contract`` has 60+ ``_emit_*`` functions, each with its own
positional signature (root_trace_id, layer, operation, ...). Threading
``req_ids`` through every one would touch every call site. Instead, this module
provides a single function that callers invoke once at a strategic point to
declare "this code path satisfies REQ-X, REQ-Y."

The ``otel_lifecycle_bridge`` parses ``req_ids=`` from the message text and
promotes it to ``attributes["agentic.req.ids"]`` (OTel-namespaced custom
attribute). The downstream coverage ledger writer then records one row per
(req_id, trace_id, layer, edge_kind) tuple.

Industry references
-------------------
* Pact-style **consumer-driven contracts**: the requirement is declared where
  the consumer expectation lives (the call site), not where the producer is
  defined.
* OpenTelemetry **custom attribute namespacing**: ``agentic.req.*`` follows
  reverse-domain naming and avoids collision with OTel reserved namespaces.
* ISO 26262 **bidirectional traceability**: forward (REQ → code) and backward
  (code → REQ) links are both encoded in the emitted span.
"""

from __future__ import annotations

import logging
from typing import Iterable

def _logger_for(edge_kind: str) -> logging.Logger:
    """Return the ``adg.<edge_kind>`` logger.

    The bridge reads ``record.name[len('adg.'):]`` to derive the edge_kind,
    so we emit on a per-edge_kind logger to preserve the semantic name in
    the captured span (rather than collapsing every REQ emission under
    a single ``adg.req_evidence`` channel).
    """
    return logging.getLogger(f"adg.{edge_kind}")


def emit_req_evidence(
    req_ids: Iterable[str],
    *,
    layer: str,
    edge_kind: str,
    op: str = "",
    root_trace_id: str = "",
) -> None:
    """Emit a runtime evidence marker tying the current code path to REQ_IDs.

    Emits on ``adg.<edge_kind>`` (dynamic), so the bridge captures the
    semantic edge_kind in the span attributes. Bridge regex pulls
    ``req_ids=...`` from the message body and promotes to
    ``attributes["agentic.req.ids"]``.

    Parameters
    ----------
    req_ids
        REQ identifiers this code path satisfies. Must be an iterable of
        strings matching the pattern ``REQ-<LAYER>-<TOKEN>-<NNN>``.
        Empty iterables are silently no-op'd.
    layer
        Architecture layer. One of L0_ROUTING, L1_REASONING, L2_EXECUTION,
        L3_ORCHESTRATION, L4_STATE, L5_POLICY, L6_OBSERVABILITY, U0_INPUT,
        C0_RETRIEVAL_PLAN, PA_BOM_RESOLUTION.
    edge_kind
        Logical edge kind for ADG indexing (e.g. ``anti_bypass_observation``,
        ``route_contract_telemetry``, ``audit_replay_consistency``).
    op
        Optional human-readable operation tag (e.g. function or call-site).
    root_trace_id
        Optional caller-provided trace id. If empty, the bridge supplies one.

    Examples
    --------
    >>> emit_req_evidence(
    ...     ("REQ-L6-OBS-ANTI-BYPASS-001",),
    ...     layer="L6_OBSERVABILITY",
    ...     edge_kind="anti_bypass_observation",
    ...     op="apps_rg.scripts.generate_resume.main",
    ... )
    """
    req_id_tuple = tuple(r for r in (req_ids or ()) if r)
    if not req_id_tuple:
        return  # nothing to record
    # Comma-separated, no spaces — the bridge regex requires this format.
    req_ids_str = ",".join(req_id_tuple)
    _logger_for(edge_kind).debug(
        "req_evidence root_trace_id=%s layer=%s edge_kind=%s op=%s req_ids=%s",
        root_trace_id or "auto",
        layer,
        edge_kind,
        op or "unknown",
        req_ids_str,
    )


# ── Convenience wrappers for the 6 priority REQs ────────────────────────────


def emit_anti_bypass_observation(op: str, root_trace_id: str = "") -> None:
    """REQ-L6-OBS-ANTI-BYPASS-001: anti-bypass observation captured."""
    emit_req_evidence(
        ("REQ-L6-OBS-ANTI-BYPASS-001",),
        layer="L6_OBSERVABILITY",
        edge_kind="anti_bypass_observation",
        op=op,
        root_trace_id=root_trace_id,
    )


def emit_outcome_trajectory(op: str, root_trace_id: str = "") -> None:
    """REQ-L6-OUTCOME-TRAJECTORY-001: outcome trajectory recorded."""
    emit_req_evidence(
        ("REQ-L6-OUTCOME-TRAJECTORY-001",),
        layer="L6_OBSERVABILITY",
        edge_kind="outcome_trajectory",
        op=op,
        root_trace_id=root_trace_id,
    )


def emit_proposal_admission(op: str, root_trace_id: str = "") -> None:
    """REQ-L6-PROPOSAL-ADMISSION-001: proposal admitted/recorded."""
    emit_req_evidence(
        ("REQ-L6-PROPOSAL-ADMISSION-001",),
        layer="L6_OBSERVABILITY",
        edge_kind="proposal_admission",
        op=op,
        root_trace_id=root_trace_id,
    )


def emit_memory_promotion(op: str, root_trace_id: str = "") -> None:
    """REQ-L6-MEMORY-PROMOTION-IFACE-001: memory promotion via the canonical iface."""
    emit_req_evidence(
        ("REQ-L6-MEMORY-PROMOTION-IFACE-001",),
        layer="L6_OBSERVABILITY",
        edge_kind="memory_promotion",
        op=op,
        root_trace_id=root_trace_id,
    )


def emit_route_contract_telemetry(op: str, root_trace_id: str = "") -> None:
    """REQ-L0-ROUTECONTRACT-TELEMETRY-001: L0 route contract telemetry emitted."""
    emit_req_evidence(
        ("REQ-L0-ROUTECONTRACT-TELEMETRY-001",),
        layer="L0_ROUTING",
        edge_kind="route_contract_telemetry",
        op=op,
        root_trace_id=root_trace_id,
    )


def emit_audit_replay_consistency(op: str, root_trace_id: str = "") -> None:
    """REQ-UWG-AUDIT-REPLAY-CONSISTENCY-001: UWG audit/replay consistency observed."""
    emit_req_evidence(
        ("REQ-UWG-AUDIT-REPLAY-CONSISTENCY-001",),
        layer="L4_STATE",
        edge_kind="audit_replay_consistency",
        op=op,
        root_trace_id=root_trace_id,
    )


__all__ = [
    "emit_req_evidence",
    "emit_anti_bypass_observation",
    "emit_outcome_trajectory",
    "emit_proposal_admission",
    "emit_memory_promotion",
    "emit_route_contract_telemetry",
    "emit_audit_replay_consistency",
]
