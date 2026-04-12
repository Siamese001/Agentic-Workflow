"""
L5 safety-audit emitter — real governed implementation.

Produces deterministic SafetyAuditRecord instances with full governance fields:
  - Stable safety_audit_id derived from key inputs via SHA-256 ("aud-{16hex}")
  - All evaluated input/output captured as content-addressed hashes
  - Wall-clock audit timestamp for replay correlation
  - BUS T publication for async learning / future-run grading

Layer rule: L5 may import from L0-L4 only.  No L6 imports here.
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from dataclasses import dataclass
from typing import Any

_log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# SafetyAuditMissingError
# ---------------------------------------------------------------------------


class SafetyAuditMissingError(Exception):
    """Raised when a required safety audit record cannot be created or retrieved."""


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _sha256_hex(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _hash_payload(d: dict[str, Any] | None) -> str:
    """Deterministic content-address hash for audit payload dicts (first 16 hex chars)."""
    if d is None:
        return _sha256_hex("null")[:16]
    try:
        raw = json.dumps(d, sort_keys=True, default=str).encode("utf-8")
    except (TypeError, ValueError):
        raw = str(d).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def _compute_audit_id(
    *,
    run_id: str,
    trace_id: str,
    policy_hash: str,
    decision_outcome: str,
    actor_id: str,
    action_class: str,
) -> str:
    """Deterministic audit ID — same inputs always produce the same ID."""
    raw = ":".join([run_id, trace_id, policy_hash, decision_outcome, actor_id, action_class])
    return "aud-" + _sha256_hex(raw)[:16]


# ---------------------------------------------------------------------------
# SafetyAuditRecord — immutable, deterministic
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SafetyAuditRecord:
    """Immutable L5 safety audit record with full governance fields.

    Fields:
        safety_audit_id:       Deterministic ID = "aud-" + sha256(key fields)[:16]
        run_id:                Execution run identifier.
        trace_id:              OpenTelemetry / execution trace ID.
        policy_hash:           SHA-256 of the governing policy at evaluation time.
        decision_outcome:      "allow", "deny", "error", "require_review", etc.
        actor_id:              Emitting component identity.
        action_class:          ActionClass value or "safety_plane_validation".
        reason:                Human-readable rationale for the decision.
        evaluated_input_hash:  SHA-256[:16] of the evaluated_input dict.
        evaluated_output_hash: SHA-256[:16] of the evaluated_output dict.
        audit_timestamp:       Wall-clock time.time() at record creation.
    """

    safety_audit_id: str
    run_id: str
    trace_id: str
    policy_hash: str
    decision_outcome: str
    actor_id: str
    action_class: str
    reason: str
    evaluated_input_hash: str
    evaluated_output_hash: str
    audit_timestamp: float


# ---------------------------------------------------------------------------
# BUS T publication (L2 telemetry_bus — downward import OK from L5)
# ---------------------------------------------------------------------------


def _publish_to_bus_t(record: SafetyAuditRecord, signal_type: str) -> None:
    """Publish audit record to BUS T for async learning and future-run grading."""
    try:
        from agentic_core.L2_execution.audit.telemetry_bus import (  # noqa: PLC0415
            BusType,
            get_telemetry_bus,
        )

        get_telemetry_bus().publish(
            bus_type=BusType.TELEMETRY,
            signal_type=signal_type,
            payload={
                "safety_audit_id": record.safety_audit_id,
                "run_id": record.run_id,
                "trace_id": record.trace_id,
                "policy_hash": record.policy_hash,
                "decision_outcome": record.decision_outcome,
                "actor_id": record.actor_id,
                "action_class": record.action_class,
                "reason": record.reason,
                "evaluated_input_hash": record.evaluated_input_hash,
                "evaluated_output_hash": record.evaluated_output_hash,
                "audit_timestamp": record.audit_timestamp,
            },
            trace_id=record.trace_id or record.run_id or "unknown",
        )
    except (ImportError, RuntimeError, ValueError, AttributeError, KeyError, TypeError) as _exc:
        _log.debug("SAFETY_AUDIT_BUS_T_SKIP signal=%s: %s", signal_type, _exc)


# ---------------------------------------------------------------------------
# Public emitters
# ---------------------------------------------------------------------------


def emit_guardrail_audit(
    *,
    run_id: str = "",
    trace_id: str = "",
    policy_hash: str = "",
    decision_outcome: str = "",
    evaluated_input: dict[str, Any] | None = None,
    evaluated_output: dict[str, Any] | None = None,
    reason: str = "",
    actor_id: str = "",
    action_class: str = "",
) -> SafetyAuditRecord:
    """Emit a deterministic guardrail audit record and publish to BUS T.

    Returns an immutable SafetyAuditRecord with a stable safety_audit_id derived
    from the key governance fields, making records idempotent for replays.
    """
    record = SafetyAuditRecord(
        safety_audit_id=_compute_audit_id(
            run_id=run_id,
            trace_id=trace_id,
            policy_hash=policy_hash,
            decision_outcome=decision_outcome,
            actor_id=actor_id,
            action_class=action_class,
        ),
        run_id=run_id,
        trace_id=trace_id,
        policy_hash=policy_hash,
        decision_outcome=decision_outcome,
        actor_id=actor_id,
        action_class=action_class,
        reason=reason,
        evaluated_input_hash=_hash_payload(evaluated_input),
        evaluated_output_hash=_hash_payload(evaluated_output),
        audit_timestamp=time.time(),
    )
    _publish_to_bus_t(record, "guardrail_audit")
    _log.debug(
        "SAFETY_AUDIT_EMITTED audit_id=%s run=%s outcome=%s actor=%s",
        record.safety_audit_id,
        record.run_id[:12] if record.run_id else "",
        record.decision_outcome,
        record.actor_id,
    )
    return record


def emit_safety_plane_validation_audit(
    *,
    run_id: str = "",
    trace_id: str = "",
    policy_hash: str = "",
    decision_outcome: str = "",
    evaluated_input: dict[str, Any] | None = None,
    reason: str = "",
    actor_id: str = "",
    **kwargs: Any,
) -> SafetyAuditRecord:
    """Emit a deterministic safety-plane validation audit record and publish to BUS T."""
    record = SafetyAuditRecord(
        safety_audit_id=_compute_audit_id(
            run_id=run_id,
            trace_id=trace_id,
            policy_hash=policy_hash or "safety_plane",
            decision_outcome=decision_outcome,
            actor_id=actor_id,
            action_class="safety_plane_validation",
        ),
        run_id=run_id,
        trace_id=trace_id,
        policy_hash=policy_hash,
        decision_outcome=decision_outcome,
        actor_id=actor_id,
        action_class="safety_plane_validation",
        reason=reason,
        evaluated_input_hash=_hash_payload(evaluated_input),
        evaluated_output_hash=_hash_payload(None),
        audit_timestamp=time.time(),
    )
    _publish_to_bus_t(record, "safety_plane_validation_audit")
    _log.debug(
        "SAFETY_PLANE_VALIDATION_AUDIT_EMITTED audit_id=%s run=%s outcome=%s",
        record.safety_audit_id,
        record.run_id[:12] if record.run_id else "",
        record.decision_outcome,
    )
    return record
