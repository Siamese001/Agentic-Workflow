"""L4/UWG durable-write OTEL spans — emission helpers + in-memory recorder.

Maps to: docs/reference/00B_L4_State_Archive_and_UWG/00B.7a_L4_UWG_Durable_Write_Context_Invariant.md
Phase 5 OTEL CONTRACT.

Span vocabulary:
  uwg.write.context.frozen   — emitted when DurableWriteContext freezes
  uwg.write.stage.emit       — emitted by each stage as it confirms its digest
  uwg.write.compare          — emitted when the chain is checked
  uwg.write.committed        — emitted on full match (or successful idempotency replay)
  uwg.write.blocked          — emitted on mismatch; carries decisive_rule_id

Tests inspect `recorded_spans()` / `clear_recorded_spans()`. Production code
calls only the `emit_*_span` functions.
"""

from __future__ import annotations

# OTel GenAI semconv opt-out: this module emits OTel spans that are
# infrastructure / governance / state-write events, not GenAI agent /
# workflow / tool / model invocations. GenAI semconv attributes do
# not apply. Plan: three-bucket-gap-remediation-069806 (W3).
__non_genai_emitter__ = "L4 UWG state-write spans — durable write attestation, not GenAI invocations"

import threading
from dataclasses import dataclass, field
from typing import Any

try:  # pragma: no cover
    from opentelemetry import trace as _otel_trace  # type: ignore[import-not-found]

    _OTEL_TRACER = _otel_trace.get_tracer("agentic_core.L4_state.uwg")
except ImportError:  # pragma: no cover
    _OTEL_TRACER = None  # type: ignore[assignment]


_LOCK = threading.Lock()
_RECORDED: list[RecordedSpan] = []


@dataclass(frozen=True)
class RecordedSpan:
    """Frozen recording of one emitted UWG durable-write span."""

    name: str
    attributes: dict[str, Any] = field(default_factory=dict)


def _record(name: str, attributes: dict[str, Any]) -> None:
    snapshot = RecordedSpan(name=name, attributes=dict(attributes))
    with _LOCK:
        _RECORDED.append(snapshot)
    if _OTEL_TRACER is not None:
        try:  # pragma: no cover
            with _OTEL_TRACER.start_as_current_span(name) as span:
                for key, value in attributes.items():
                    if value is None:
                        continue
                    span.set_attribute(key, value)
        except (RuntimeError, ValueError, TypeError):  # guardian: allow-silent-swallow -- OTEL bridge is best-effort observability; never break UWG control flow
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
    durable_write_digest: str,
    request_id: str,
    run_id: str,
    trace_id: str,
    tenant_id: str,
    principal_id: str,
    exit_disposition_id: str,
    commit_request_id: str,
    target_store_id: str,
    target_object_ref: str,
    mutation_intent_class: str,
    state_diff_candidate_hash: str,
    before_snapshot_hash: str,
    after_candidate_hash: str,
    schema_hash: str,
    policy_hash: str,
    blueprint_hash: str,
    capability_scope_hash: str,
    sandbox_envelope_hash: str,
    l5_certification_packet_hash: str,
    replay_key: str,
    idempotency_key: str,
    write_lock_id: str,
    transaction_id: str,
) -> None:
    """Emit `uwg.write.context.frozen` span (one per attempt)."""
    _record(
        "uwg.write.context.frozen",
        {
            "request_id": request_id,
            "run_id": run_id,
            "trace_id": trace_id,
            "tenant_id": tenant_id,
            "principal_id": principal_id,
            "exit_disposition_id": exit_disposition_id,
            "commit_request_id": commit_request_id,
            "target_store_id": target_store_id,
            "target_object_ref": target_object_ref,
            "mutation_intent_class": mutation_intent_class,
            "state_diff_candidate_hash": state_diff_candidate_hash,
            "before_snapshot_hash": before_snapshot_hash,
            "after_candidate_hash": after_candidate_hash,
            "schema_hash": schema_hash,
            "policy_hash": policy_hash,
            "blueprint_hash": blueprint_hash,
            "capability_scope_hash": capability_scope_hash,
            "sandbox_envelope_hash": sandbox_envelope_hash,
            "l5_certification_packet_hash": l5_certification_packet_hash,
            "replay_key": replay_key,
            "idempotency_key": idempotency_key,
            "write_lock_id": write_lock_id,
            "transaction_id": transaction_id,
            "durable_write_digest": durable_write_digest,
        },
    )


def emit_stage_emit_span(
    *,
    stage_name: str,
    stage_digest_alias: str,
    durable_write_digest: str,
    stage_emitted_digest: str,
    trace_id: str,
) -> None:
    """Emit `uwg.write.stage.emit` span (one per stage that emits)."""
    _record(
        "uwg.write.stage.emit",
        {
            "stage_name": stage_name,
            "stage_digest_alias": stage_digest_alias,
            "durable_write_digest": durable_write_digest,
            "stage_emitted_digest": stage_emitted_digest,
            "trace_id": trace_id,
        },
    )


def emit_compare_span(
    *,
    chain_complete: bool,
    all_match: bool,
    first_mismatched_stage: str,
    trace_id: str,
    decision_id: str = "",
) -> None:
    """Emit `uwg.write.compare` span — pure compare result."""
    _record(
        "uwg.write.compare",
        {
            "chain_complete": chain_complete,
            "all_match": all_match,
            "first_mismatched_stage": first_mismatched_stage,
            "trace_id": trace_id,
            "decision_id": decision_id,
        },
    )


def emit_committed_span(
    *,
    l4_state_receipt_digest: str,
    audit_ledger_digest: str,
    replay_snapshot_digest: str,
    retrieval_cache_invalidation_digest: str,
    trace_id: str,
    transaction_id: str,
    idempotency_key: str,
    terminal_class: str,
    idempotency_replay: bool = False,
) -> None:
    """Emit `uwg.write.committed` span — fired on full match.

    `idempotency_replay=True` indicates the span is for a deduplicated
    no-op replay (no actual write happened this attempt).
    """
    _record(
        "uwg.write.committed",
        {
            "l4_state_receipt_digest": l4_state_receipt_digest,
            "audit_ledger_digest": audit_ledger_digest,
            "replay_snapshot_digest": replay_snapshot_digest,
            "retrieval_cache_invalidation_digest": retrieval_cache_invalidation_digest,
            "trace_id": trace_id,
            "transaction_id": transaction_id,
            "idempotency_key": idempotency_key,
            "terminal_class": terminal_class,
            "idempotency_replay": idempotency_replay,
        },
    )


def emit_blocked_span(
    *,
    decisive_rule_id: str,
    first_mismatched_stage: str,
    trace_id: str,
    sealed_receipt_id: str,
    terminal_class: str,
    rollback_required: bool,
) -> None:
    """Emit `uwg.write.blocked` span — fired on mismatch only."""
    _record(
        "uwg.write.blocked",
        {
            "decisive_rule_id": decisive_rule_id,
            "first_mismatched_stage": first_mismatched_stage,
            "trace_id": trace_id,
            "sealed_receipt_id": sealed_receipt_id,
            "terminal_class": terminal_class,
            "rollback_required": rollback_required,
        },
    )


__all__ = [
    "RecordedSpan",
    "clear_recorded_spans",
    "emit_blocked_span",
    "emit_committed_span",
    "emit_compare_span",
    "emit_context_frozen_span",
    "emit_stage_emit_span",
    "recorded_spans",
]
