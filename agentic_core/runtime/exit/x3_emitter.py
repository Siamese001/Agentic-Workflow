"""AG-5 X3 emitter — single ExitDispositionReceipt (no durable writes)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

from agentic_core.L3_orchestration.exit_eval.v6.types import ExitReviewPacket
from agentic_core.runtime.contracts.x1_checkout_result import X1CheckoutResult
from agentic_core.runtime.exit.exit_disposition import (
    EXIT_DISPOSITION_SCHEMA_VERSION,
    ExitDispositionReceipt,
    X3A_DENY_REROUTE,
    X3B_ESCALATE_HITL,
    X3D_ALLOW_FINISH,
)
from agentic_core.runtime.exit.x2_aggregation_result import X2AggregationResult


class AG5ExitEmitError(RuntimeError):
    """Raised when AG-5 cannot emit a disposition receipt safely."""


def emit_ag5_exit_disposition_receipt(
    *,
    packet: ExitReviewPacket,
    x1: X1CheckoutResult,
    x2: X2AggregationResult,
    supplementary_refs: Mapping[str, Any],
) -> ExitDispositionReceipt:
    """Emit exactly one X3-shaped receipt — observer-only; no L4 writes."""
    if any(str(x) == "L6_CURRENT_RUN_RESCUE" for x in packet.anomaly_flags):
        raise AG5ExitEmitError("L6_CURRENT_RUN_RESCUE blocked at Exit boundary")

    code = x2.disposition_candidate

    if code == X3D_ALLOW_FINISH and getattr(x2, "deterministic_blocked", False):
        raise AG5ExitEmitError("deterministic_blocked=True cannot authorize ALLOW_FINISH")

    if code == X3D_ALLOW_FINISH:
        if not str(supplementary_refs.get("user_visible_response_ref") or "").strip():
            raise AG5ExitEmitError("ALLOW_FINISH requires user_visible_response_ref")
        if not str(supplementary_refs.get("deterministic_digest") or "").strip():
            raise AG5ExitEmitError("ALLOW_FINISH requires deterministic_digest")

    now = datetime.now(timezone.utc).isoformat()

    return ExitDispositionReceipt(
        request_id=packet.request_id,
        run_id=packet.run_id,
        trace_root=packet.trace_root,
        app_id=packet.app_id,
        task_class=packet.task_class,
        x3_code=code,
        decisive_reason=f"ag5_emit:{code}",
        decisive_blocker_gate_ids=(),
        gate_mesh_result_ref=str(supplementary_refs.get("gate_mesh_result_ref") or ""),
        required_gates_passed=x1.is_overall_pass(),
        policy_hash=packet.policy_hash,
        deterministic_digest=str(supplementary_refs.get("deterministic_digest") or ""),
        created_at=now,
        schema_version=EXIT_DISPOSITION_SCHEMA_VERSION,
    )


__all__ = ["AG5ExitEmitError", "emit_ag5_exit_disposition_receipt"]
