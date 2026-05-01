"""
L6 execution observability recorder — real governed implementation.

Produces deterministic ObservabilityRecord instances that capture:
  - Full execution context (request_id, status, duration_ms, target)
  - Observability context (run_id, trace_id, policy_hash, guardrail_decision_id)
  - Failure/block metadata where applicable
  - Replay linkage key ("rpl-{sha256[:16]}") for future-run correlation
  - BUS T publication for async learning / exit analysis
  - evaluate_and_attach() registration in the L6 EvaluationIndex

Deterministic IDs:
  execution_observability_id = "obs-" + sha256(req_id:status:run_id:trace_id)[:16]
  replay_key                 = "rpl-" + sha256(req_id:run_id:policy_hash)[:16]
"""

from __future__ import annotations

import hashlib
import logging
import time
import uuid as _uuid_mod
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from agentic_core.runtime.prove_requirements.otel_emitter import (
        RuntimeSpanEmitter,
    )

_log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Enums (public — re-exported for callers)
# ---------------------------------------------------------------------------


class ExecutionStatus(str, Enum):
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    BLOCKED_BY_POLICY = "BLOCKED_BY_POLICY"
    UNKNOWN = "UNKNOWN"


class FailureClassification(str, Enum):
    TOOL_ERROR = "TOOL_ERROR"
    UNKNOWN_FAILURE = "UNKNOWN_FAILURE"
    POLICY_VIOLATION = "POLICY_VIOLATION"


# ---------------------------------------------------------------------------
# Input context objects (mutable — passed in by callers)
# ---------------------------------------------------------------------------


@dataclass
class ExecutionContext:
    """Observability execution context for timing and status."""

    execution_request_id: str = ""
    execution_start_tick: float = 0.0
    execution_end_tick: float = 0.0
    execution_status: ExecutionStatus = ExecutionStatus.UNKNOWN

    @classmethod
    def create(
        cls,
        *,
        execution_request_id: str = "",
        execution_start_tick: float = 0.0,
        execution_end_tick: float = 0.0,
        execution_status: ExecutionStatus = ExecutionStatus.UNKNOWN,
    ) -> ExecutionContext:
        return cls(
            execution_request_id=execution_request_id,
            execution_start_tick=execution_start_tick,
            execution_end_tick=execution_end_tick,
            execution_status=execution_status,
        )


@dataclass
class ExecutionObservabilityContext:
    """Context linking execution to run and trace for observability records."""

    observability_id: str = field(default_factory=lambda: str(_uuid_mod.uuid4()))
    run_id: str = ""
    trace_id: str = ""
    execution_target: str = ""
    guardrail_decision_id: str = ""
    policy_hash: str = ""

    @classmethod
    def create(
        cls,
        *,
        run_id: str = "",
        trace_id: str = "",
        execution_target: str = "",
        guardrail_decision_id: str = "",
        policy_hash: str = "",
    ) -> ExecutionObservabilityContext:
        return cls(
            run_id=run_id,
            trace_id=trace_id,
            execution_target=execution_target,
            guardrail_decision_id=guardrail_decision_id,
            policy_hash=policy_hash,
        )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _sha256_hex(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _compute_obs_id(
    execution_request_id: str,
    execution_status: str,
    run_id: str,
    trace_id: str,
) -> str:
    """Deterministic observability ID — same inputs → same ID (replay-stable)."""
    raw = ":".join([execution_request_id, execution_status, run_id, trace_id])
    return "obs-" + _sha256_hex(raw)[:16]


def _compute_replay_key(
    execution_request_id: str,
    run_id: str,
    policy_hash: str,
) -> str:
    """Deterministic replay linkage key for future-run correlation."""
    raw = ":".join([execution_request_id, run_id, policy_hash])
    return "rpl-" + _sha256_hex(raw)[:16]


def _duration_ms(start: float, end: float) -> float:
    """Wall-clock execution duration in milliseconds."""
    if end > 0.0 and start > 0.0 and end >= start:
        return (end - start) * 1000.0
    return 0.0


def _status_value(status: Any) -> str:
    if isinstance(status, ExecutionStatus):
        return status.value
    return str(status)


def _failure_class_value(fc: Any) -> str:
    if isinstance(fc, FailureClassification):
        return fc.value
    return str(fc) if fc else ""


# ---------------------------------------------------------------------------
# ObservabilityRecord — immutable, deterministic
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ObservabilityRecord:
    """Immutable execution observability record with full governance fields.

    Fields:
        execution_observability_id: Deterministic ID = "obs-" + sha256(...)[:16].
        record_id:                  Alias for execution_observability_id (backward compat).
        execution_request_id:       From ExecutionContext.execution_request_id.
        run_id:                     From ExecutionObservabilityContext.run_id.
        trace_id:                   From ExecutionObservabilityContext.trace_id.
        execution_target:           From ExecutionObservabilityContext.execution_target.
        execution_status:           SUCCEEDED / FAILED / BLOCKED_BY_POLICY / UNKNOWN.
        duration_ms:                Wall-clock execution time (end_tick - start_tick)*1000.
        guardrail_decision_id:      From ExecutionObservabilityContext.guardrail_decision_id.
        policy_hash:                From ExecutionObservabilityContext.policy_hash.
        failure_classification:     FailureClassification.value or "" on success.
        failure_reason:             Human-readable failure detail or "" on success.
        block_reason:               Policy block rationale or "" if not blocked.
        replay_key:                 "rpl-" + sha256(req_id:run_id:policy_hash)[:16].
        created_tick:               Wall-clock time.time() at record creation.
    """

    execution_observability_id: str
    record_id: str
    execution_request_id: str
    run_id: str
    trace_id: str
    execution_target: str
    execution_status: str
    duration_ms: float
    guardrail_decision_id: str
    policy_hash: str
    failure_classification: str
    failure_reason: str
    block_reason: str
    replay_key: str
    created_tick: float


# ---------------------------------------------------------------------------
# Record builder
# ---------------------------------------------------------------------------


def _build_record(
    exec_ctx: ExecutionContext,
    obs_ctx: ExecutionObservabilityContext,
    *,
    failure_classification: str = "",
    failure_reason: str = "",
    block_reason: str = "",
) -> ObservabilityRecord:
    status = _status_value(exec_ctx.execution_status)
    obs_id = _compute_obs_id(
        exec_ctx.execution_request_id,
        status,
        obs_ctx.run_id,
        obs_ctx.trace_id,
    )
    return ObservabilityRecord(
        execution_observability_id=obs_id,
        record_id=obs_id,
        execution_request_id=exec_ctx.execution_request_id,
        run_id=obs_ctx.run_id,
        trace_id=obs_ctx.trace_id,
        execution_target=obs_ctx.execution_target,
        execution_status=status,
        duration_ms=_duration_ms(exec_ctx.execution_start_tick, exec_ctx.execution_end_tick),
        guardrail_decision_id=obs_ctx.guardrail_decision_id,
        policy_hash=obs_ctx.policy_hash,
        failure_classification=failure_classification,
        failure_reason=failure_reason,
        block_reason=block_reason,
        replay_key=_compute_replay_key(
            exec_ctx.execution_request_id,
            obs_ctx.run_id,
            obs_ctx.policy_hash,
        ),
        created_tick=time.time(),
    )


# ---------------------------------------------------------------------------
# BUS T publication
# ---------------------------------------------------------------------------


def _publish_to_bus_t(record: ObservabilityRecord, signal_type: str) -> None:
    """Publish observability record to BUS T for async learning and exit analysis."""
    try:
        from agentic_core.L2_execution.audit.telemetry_bus import (  # noqa: PLC0415  # guardian: allow-layer-violation -- L6 observability module uses L2 execution type; intentional cross-layer instrumentation dependency
            BusType,
            get_telemetry_bus,
        )

        get_telemetry_bus().publish(
            bus_type=BusType.TELEMETRY,
            signal_type=signal_type,
            payload={
                "execution_observability_id": record.execution_observability_id,
                "execution_request_id": record.execution_request_id,
                "run_id": record.run_id,
                "trace_id": record.trace_id,
                "execution_target": record.execution_target,
                "execution_status": record.execution_status,
                "duration_ms": record.duration_ms,
                "guardrail_decision_id": record.guardrail_decision_id,
                "policy_hash": record.policy_hash,
                "failure_classification": record.failure_classification,
                "failure_reason": record.failure_reason,
                "block_reason": record.block_reason,
                "replay_key": record.replay_key,
                "created_tick": record.created_tick,
            },
            trace_id=record.trace_id or record.run_id or "unknown",
        )
    except (ImportError, RuntimeError, ValueError, AttributeError, KeyError, TypeError) as _exc:  # guardian: allow-log-and-swallow -- obs bus emission optional: non-fatal, recording continues
        _log.debug("OBS_BUS_T_SKIP signal=%s: %s", signal_type, _exc)


# ---------------------------------------------------------------------------
# L6 EvaluationIndex registration
# ---------------------------------------------------------------------------


def _register_in_eval_index(record: ObservabilityRecord) -> None:
    """Register observability record in the L6 EvaluationIndex via evaluate_and_attach."""
    try:
        from agentic_core.L6_observability.utils.evaluation.evaluation_record import (  # noqa: PLC0415
            EvaluationStage,
            evaluate_and_attach,
        )

        evaluate_and_attach(
            evaluated_artifact={
                "execution_observability_id": record.execution_observability_id,
                "execution_target": record.execution_target,
                "execution_status": record.execution_status,
            },
            rubric={"type": "execution_observability", "version": "v1"},
            evaluator_id="observability_recorder",
            score_payload={
                "execution_status": record.execution_status,
                "duration_ms": record.duration_ms,
                "failure_classification": record.failure_classification,
                "replay_key": record.replay_key,
            },
            evaluated_stage=EvaluationStage.EXECUTION_TRACE,
            run_id=record.run_id,
            trace_id=record.trace_id,
            policy_hash=record.policy_hash,
            policy_sensitive=True,
        )
    except (ImportError, RuntimeError, ValueError, TypeError, AttributeError) as _exc:  # guardian: allow-log-and-swallow -- eval index update optional: non-fatal, recording continues
        _log.debug("OBS_EVAL_INDEX_SKIP: %s", _exc)


# ---------------------------------------------------------------------------
# Public recording functions
# ---------------------------------------------------------------------------


def record_execution_observability(
    execution_context: ExecutionContext,
    observability_context: ExecutionObservabilityContext,
    *,
    emitter: Optional["RuntimeSpanEmitter"] = None,
    **kwargs: Any,
) -> ObservabilityRecord:
    """Record successful execution with full governance fields.

    Builds a deterministic ObservabilityRecord, publishes to BUS T, and
    registers in the L6 EvaluationIndex for exit analysis and replay linkage.

    W9 live wire-up: when ``emitter`` is provided, emits ``l6.ingest`` >
    ``l6.evaluate`` spans tying this record to the proof-OTEL contract.
    """
    if emitter is None:
        record = _build_record(
            execution_context,
            observability_context,
            failure_classification="",
            failure_reason="",
            block_reason="",
        )
        _publish_to_bus_t(record, "execution_observability")
        _register_in_eval_index(record)
        _log.debug(
            "EXECUTION_OBSERVABILITY_RECORDED obs_id=%s req=%s target=%s status=%s dur=%.2fms",
            record.execution_observability_id,
            record.execution_request_id[:12] if record.execution_request_id else "",
            record.execution_target,
            record.execution_status,
            record.duration_ms,
        )
        return record

    with emitter.span(
        "l6.ingest",
        reason_codes=["execution_observability"],
        replay_key=None,  # filled below once record is built
    ):
        record = _build_record(
            execution_context,
            observability_context,
            failure_classification="",
            failure_reason="",
            block_reason="",
        )
        _publish_to_bus_t(record, "execution_observability")
        with emitter.span(
            "l6.evaluate",
            reason_codes=["clean_execution_observed"],
            replay_key=record.replay_key,
            policy_hash=record.policy_hash or None,
        ):
            _register_in_eval_index(record)
        return record


def record_execution_failure(
    execution_context: ExecutionContext,
    observability_context: ExecutionObservabilityContext,
    failure_classification: FailureClassification = FailureClassification.UNKNOWN_FAILURE,
    failure_reason: str = "",
    *,
    emitter: Optional["RuntimeSpanEmitter"] = None,
    **kwargs: Any,
) -> ObservabilityRecord:
    """Record execution failure with full governance fields.

    W9 live wire-up: when ``emitter`` is provided, emits ``l6.ingest`` >
    ``l6.evaluate`` > ``l6.rca_or_proposal`` because a failure event always
    triggers root-cause-analysis regardless of disposition.
    """
    if emitter is None:
        record = _build_record(
            execution_context,
            observability_context,
            failure_classification=_failure_class_value(failure_classification),
            failure_reason=failure_reason,
            block_reason="",
        )
        _publish_to_bus_t(record, "execution_failure")
        _register_in_eval_index(record)
        return record

    fc_value = _failure_class_value(failure_classification)
    with emitter.span(
        "l6.ingest",
        reason_codes=["execution_failure", fc_value],
    ):
        record = _build_record(
            execution_context,
            observability_context,
            failure_classification=fc_value,
            failure_reason=failure_reason,
            block_reason="",
        )
        _publish_to_bus_t(record, "execution_failure")
        with emitter.span(
            "l6.evaluate",
            reason_codes=["failure_observed", fc_value],
            replay_key=record.replay_key,
            policy_hash=record.policy_hash or None,
        ):
            _register_in_eval_index(record)
            with emitter.span(
                "l6.rca_or_proposal",
                reason_codes=["rca_pending", fc_value],
            ):
                # RCA span is emitted as a marker; downstream tooling
                # picks up the failure_classification and reasons from
                # the record itself.
                pass
        return record


def record_policy_block(
    execution_context: ExecutionContext,
    observability_context: ExecutionObservabilityContext,
    block_reason: str = "",
    *,
    emitter: Optional["RuntimeSpanEmitter"] = None,
    **kwargs: Any,
) -> ObservabilityRecord:
    """Record policy block observability with full governance fields.

    W9 live wire-up: when ``emitter`` is provided, emits ``l6.ingest`` >
    ``l6.evaluate`` with a ``policy_block`` reason. RCA is NOT emitted
    here because policy blocks are governance decisions, not failures
    requiring root-cause analysis.
    """
    if emitter is None:
        record = _build_record(
            execution_context,
            observability_context,
            failure_classification="",
            failure_reason="",
            block_reason=block_reason,
        )
        _publish_to_bus_t(record, "policy_block")
        _register_in_eval_index(record)
        return record

    with emitter.span(
        "l6.ingest",
        reason_codes=["policy_block"],
    ):
        record = _build_record(
            execution_context,
            observability_context,
            failure_classification="",
            failure_reason="",
            block_reason=block_reason,
        )
        _publish_to_bus_t(record, "policy_block")
        with emitter.span(
            "l6.evaluate",
            reason_codes=["policy_block_observed"],
            replay_key=record.replay_key,
            policy_hash=record.policy_hash or None,
        ):
            _register_in_eval_index(record)
        return record
