"""L5 Governance OTEL spans — emission helpers + in-memory test recorder.

Maps to: docs/reference/00A_L5_Governance_Safety/00A.7a_L5_Governance_Context_Invariant.md
Phase 5 OTEL CONTRACT.

Span vocabulary:
  l5.governance.context.frozen   — emitted when L5GovernanceContext freezes
  l5.governance.child.emit       — emitted by each per-child certifier
  l5.governance.compare          — emitted at aggregator entry; all_match attr
  l5.governance.aggregate        — emitted on success only
  l5.governance.blocked          — emitted on mismatch; carries decisive_rule_id

This module:
  - Always records spans into a process-local in-memory recorder so tests
    can assert against real recorded spans (NOT logs).
  - Optionally bridges to opentelemetry.trace if available, but the test
    surface does not depend on opentelemetry being installed.

Tests inspect `recorded_spans()` / `clear_recorded_spans()`. Production code
calls only the `emit_*_span` functions.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import Any

# Best-effort OTEL bridge. Failing import or runtime error must never break
# L5 control flow — emission is observability, not enforcement.
try:  # pragma: no cover
    from opentelemetry import trace as _otel_trace  # type: ignore[import-not-found]

    _OTEL_TRACER = _otel_trace.get_tracer("agentic_core.L5_safety.governance")
except ImportError:  # pragma: no cover
    _OTEL_TRACER = None  # type: ignore[assignment]


_LOCK = threading.Lock()
_RECORDED: list[RecordedSpan] = []


@dataclass(frozen=True)
class RecordedSpan:
    """Frozen recording of one emitted L5 governance span."""

    name: str
    attributes: dict[str, Any] = field(default_factory=dict)


def _record(name: str, attributes: dict[str, Any]) -> None:
    snapshot = RecordedSpan(name=name, attributes=dict(attributes))
    with _LOCK:
        _RECORDED.append(snapshot)
    if _OTEL_TRACER is not None:
        try:  # pragma: no cover - thin OTEL bridge
            with _OTEL_TRACER.start_as_current_span(name) as span:
                for key, value in attributes.items():
                    if value is None:
                        continue
                    span.set_attribute(key, value)
        except (RuntimeError, ValueError, TypeError):  # guardian: allow-silent-swallow -- OTEL bridge is best-effort observability; never break L5 control flow
            pass


def recorded_spans() -> tuple[RecordedSpan, ...]:
    """Return all spans recorded since the last `clear_recorded_spans()`."""
    with _LOCK:
        return tuple(_RECORDED)


def clear_recorded_spans() -> None:
    """Reset the in-memory recorder. Tests call this in fixtures."""
    with _LOCK:
        _RECORDED.clear()


def emit_context_frozen_span(
    *,
    canonical_context_digest: str,
    request_id: str,
    run_id: str,
    trace_id: str,
    tenant_id: str,
    principal_id: str,
    route_id: str,
    step_id: str,
    execution_form: str,
    risk_tier: str,
    side_effect_class: str,
    policy_hash: str,
    blueprint_hash: str,
    registry_snapshot_hash: str,
    agent_profile_hash: str,
    capability_scope_hash: str,
    sandbox_envelope_hash: str,
    origin_trust_manifest_hash: str,
    egress_profile_hash: str,
    hitl_packet_hash: str,
    reclearance_hash: str,
    replay_envelope_hash: str,
    audit_manifest_hash: str,
    static_governance_snapshot_hash: str,
) -> None:
    """Emit `l5.governance.context.frozen` span (one per packet)."""
    _record(
        "l5.governance.context.frozen",
        {
            "request_id": request_id,
            "run_id": run_id,
            "trace_id": trace_id,
            "tenant_id": tenant_id,
            "principal_id": principal_id,
            "route_id": route_id,
            "step_id": step_id,
            "execution_form": execution_form,
            "risk_tier": risk_tier,
            "side_effect_class": side_effect_class,
            "policy_hash": policy_hash,
            "blueprint_hash": blueprint_hash,
            "registry_snapshot_hash": registry_snapshot_hash,
            "agent_profile_hash": agent_profile_hash,
            "capability_scope_hash": capability_scope_hash,
            "sandbox_envelope_hash": sandbox_envelope_hash,
            "origin_trust_manifest_hash": origin_trust_manifest_hash,
            "egress_profile_hash": egress_profile_hash,
            "hitl_packet_hash": hitl_packet_hash,
            "reclearance_hash": reclearance_hash,
            "replay_envelope_hash": replay_envelope_hash,
            "audit_manifest_hash": audit_manifest_hash,
            "static_governance_snapshot_hash": static_governance_snapshot_hash,
            "l5_context_digest": canonical_context_digest,
        },
    )


def emit_child_emit_span(
    *,
    certifier_id: str,
    certifier_version: str,
    certification_scope: str,
    canonical_context_digest: str,
    child_digest_alias: str,
    stage_emitted_digest: str,
    trace_id: str,
) -> None:
    """Emit `l5.governance.child.emit` span (one per participating child)."""
    _record(
        "l5.governance.child.emit",
        {
            "certifier_id": certifier_id,
            "certifier_version": certifier_version,
            "certification_scope": certification_scope,
            "l5_context_digest": canonical_context_digest,
            "child_digest_alias": child_digest_alias,
            "stage_emitted_digest": stage_emitted_digest,
            "trace_id": trace_id,
        },
    )


def emit_compare_span(
    *,
    required_digests_seen: int,
    conditional_digests_seen: int,
    all_required_match: bool,
    conditional_match: bool,
    first_mismatched_field: str,
    trace_id: str,
    decision_id: str = "",
) -> None:
    """Emit `l5.governance.compare` span — pure compare result."""
    _record(
        "l5.governance.compare",
        {
            "required_digests_seen": required_digests_seen,
            "conditional_digests_seen": conditional_digests_seen,
            "all_required_match": all_required_match,
            "conditional_match": conditional_match,
            "first_mismatched_field": first_mismatched_field,
            "trace_id": trace_id,
            "decision_id": decision_id,
        },
    )


def emit_aggregate_span(
    *,
    aggregate_governance_digest: str,
    all_match: bool,
    trace_id: str,
    certified: bool,
    terminal_class: str,
) -> None:
    """Emit `l5.governance.aggregate` span — fired on full match only."""
    _record(
        "l5.governance.aggregate",
        {
            "aggregate_governance_digest": aggregate_governance_digest,
            "all_match": all_match,
            "trace_id": trace_id,
            "certified": certified,
            "terminal_class": terminal_class,
        },
    )


def emit_blocked_span(
    *,
    decisive_rule_id: str,
    first_mismatched_field: str,
    trace_id: str,
    sealed_evidence_id: str,
    terminal_class: str,
) -> None:
    """Emit `l5.governance.blocked` span — fired on mismatch only."""
    _record(
        "l5.governance.blocked",
        {
            "decisive_rule_id": decisive_rule_id,
            "first_mismatched_field": first_mismatched_field,
            "trace_id": trace_id,
            "sealed_evidence_id": sealed_evidence_id,
            "terminal_class": terminal_class,
        },
    )


__all__ = [
    "RecordedSpan",
    "clear_recorded_spans",
    "emit_aggregate_span",
    "emit_blocked_span",
    "emit_child_emit_span",
    "emit_compare_span",
    "emit_context_frozen_span",
    "recorded_spans",
]
