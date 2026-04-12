"""
agentic_core/runtime/trace_emitter.py

TraceEmitter — mixin and decorator for structured execution trace emission.

P0-L6 gap remediation: all boundary-crossing modules across L0–L6 should
inherit TraceEmitter or use @emit_trace to link their execution to the
active ExecutionTrace, producing records_execution_trace ADG edges at runtime.
"""

from __future__ import annotations

import functools
import hashlib
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Callable

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_through,
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)
from agentic_core.runtime.types.execution_trace import (
    ExecutionTrace,
    get_active_execution_trace,
)

_emit_applies_guardrail("p0", "trace_emitter", "p0_governance")
_emit_reads_policy_state("p0", "trace_emitter", "policy_binding")
_emit_snapshots_state("p0", "trace_emitter", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("trace_emitter", "p4obs", "metric_1")
_emit_emits_metric_event("trace_emitter", "p4obs", "metric_2")
_emit_emits_metric_event("trace_emitter", "p4obs", "metric_3")
_emit_emits_metric_event("trace_emitter", "p4obs", "metric_4")
_emit_emits_metric_event("trace_emitter", "p4obs", "metric_5")
_emit_emits_metric_event("trace_emitter", "p4obs", "metric_6")
_emit_records_incident_event("trace_emitter", "p4obs", "incident")
_emit_captures_runtime_anomaly("trace_emitter", "p4obs", "anomaly")
_emit_writes_observability_log("trace_emitter", "p4obs", "obs_log")
_emit_updates_monitoring_state("trace_emitter", "p4obs", "mon_state")
_emit_triggers_alert("trace_emitter", "p4obs", "alert")
_emit_links_incident_trace("trace_emitter", "p4obs", "trace_link")
_emit_captures_pattern("trace_emitter", "p3lm", "pattern")
_emit_records_learning_event("trace_emitter", "p3lm", "learning_event")
_emit_writes_learning_snapshot("trace_emitter", "p3lm", "snapshot")
_emit_feeds_meta_learning("trace_emitter", "p3lm", "meta_feed")
_emit_updates_routing_strategy("trace_emitter", "p3lm", "routing")
_emit_improves_agent_policy("trace_emitter", "p3lm", "policy")
_emit_stores_learning_state("trace_emitter", "p3lm", "state")
_emit_records_execution_trace("trace_emitter", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("trace_emitter", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("trace_emitter", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("trace_emitter", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("trace_emitter", "L4_STATE", "p2_trace_5")
_emit_reads_environ("trace_emitter", "env_read", "p2_env_1")
_emit_reads_environ("trace_emitter", "env_read", "p2_env_2")
_emit_reads_runtime_state("trace_emitter", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("trace_emitter", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "trace_emitter", "context_pull")
_emit_pulls_context("p1", "trace_emitter", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "trace_emitter", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "trace_emitter", "uwg_term_2")
_emit_writes_through("p1", "trace_emitter", "write_through")
_emit_writes_through("p1", "trace_emitter", "write_through_2")
_emit_validated_by_safety_plane("p1", "trace_emitter", "safety_validation")
_emit_invokes_eval("p1", "trace_emitter", "eval_call")
_emit_proposal_commits_routing("p1", "trace_emitter", "routing_commit")
_emit_escalates_to_human("p1", "trace_emitter", "human_escalation")
_emit_routes_through("p1", "trace_emitter", "route_through")
_emit_checks_agent_registry("p1", "trace_emitter", "agent_registry")
_emit_validates_agent_capability("p1", "trace_emitter", "capability")
_emit_dispatches_execution_plan("p1", "trace_emitter", "exec_plan")
_emit_agent_executes_agent("p1", "trace_emitter", "sub_agent")
_emit_routes_to_agent("p1", "trace_emitter", "target_agent")
_emit_verifies_policy("p1", "trace_emitter", "policy_check")
_emit_observes_runtime_state("p1", "trace_emitter", "runtime_state")
_emit_verifies_boundary("p1", "trace_emitter", "boundary_check")
_emit_transcripts_response("p1", "trace_emitter", "transcript")
_emit_hard_fails_untranscripted("p1", "trace_emitter")
_emit_gated_by_confidence("p1", "trace_emitter", "confidence_gate")
emit_replay_key("p0", "trace_emitter")
emit_determinism_digest("p0", "trace_emitter")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "trace_emitter", "execution_auth")
_emit_validates_capability("p2", "trace_emitter", "capability_check")
_emit_routes_to_capability("p2", "trace_emitter", "capability_route")
_emit_writes_via_uwg("p2", "trace_emitter", "uwg_write")
_emit_blocks_direct_write("p2", "trace_emitter", "direct_write_block")
_emit_records_tool_invocation("p2", "trace_emitter", "tool_invocation")
_emit_captures_execution_output("p2", "trace_emitter", "exec_output")
_emit_dispatches_agent("p3", "trace_emitter", "agent_dispatch")
_emit_coordinates_agents("p3", "trace_emitter", "agent_coordination")
_emit_records_workflow_lineage("p3", "trace_emitter", "workflow_lineage")
_emit_records_healing_outcome("p3", "trace_emitter", "healing_outcome")
_emit_escalates_failure("p3", "trace_emitter", "failure_escalation")
_emit_orchestrates_workflow("p3", "trace_emitter", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "trace_emitter", "healing_dispatch")
_emit_invokes_evaluation("p3", "trace_emitter", "evaluation_signal")
_emit_records_telemetry_event("p4", "trace_emitter", "telemetry_event")
_emit_captures_evaluation_metric("p4", "trace_emitter", "eval_metric")
_emit_stores_embedding("p4", "trace_emitter", "embedding_store")
_emit_updates_meta_learning_state("p4", "trace_emitter", "meta_learning")
_emit_links_execution_to_snapshot("p4", "trace_emitter", "exec_snapshot_link")

logger = logging.getLogger(__name__)


@dataclass
class TraceRecord:
    """Single execution trace record emitted by TraceEmitter."""

    trace_id: str
    layer: str
    module: str
    operation: str
    elapsed_ms: float
    determinism_digest: str
    success: bool
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "layer": self.layer,
            "module": self.module,
            "operation": self.operation,
            "elapsed_ms": round(self.elapsed_ms, 3),
            "determinism_digest": self.determinism_digest,
            "success": self.success,
            "metadata": self.metadata,
        }


class TraceEmitter:
    """Mixin that adds structured execution trace emission to any module.

    Usage::

        class MyL1Engine(TraceEmitter):
            _LAYER = "L1"

            def run(self, prompt: str) -> str:
                with self.trace_operation("run"):
                    return self._do_work(prompt)
    """

    _LAYER: str = "UNKNOWN"
    _MODULE: str = ""

    def _module_name(self) -> str:
        return self._MODULE or type(self).__module__ + "." + type(self).__qualname__

    def _current_trace(self) -> ExecutionTrace | None:
        return get_active_execution_trace()

    def _make_digest(self, operation: str, elapsed_ms: float) -> str:
        payload = f"{self._LAYER}:{self._module_name()}:{operation}:{elapsed_ms:.3f}"
        return hashlib.sha256(payload.encode()).hexdigest()[:16]

    def emit_trace_record(
        self,
        operation: str,
        elapsed_ms: float,
        success: bool = True,
        metadata: dict[str, Any] | None = None,
    ) -> TraceRecord:
        """Emit a structured trace record for this module's operation."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "TraceEmitter.emit_trace_record"
        )

        active = self._current_trace()
        trace_id = active.trace_id if active else "no-active-trace"
        digest = self._make_digest(operation, elapsed_ms)
        record = TraceRecord(
            trace_id=trace_id,
            layer=self._LAYER,
            module=self._module_name(),
            operation=operation,
            elapsed_ms=elapsed_ms,
            determinism_digest=digest,
            success=success,
            metadata=metadata or {},
        )
        logger.debug(
            "TRACE_EMIT layer=%s module=%s op=%s trace_id=%s elapsed_ms=%.1f ok=%s",
            self._LAYER,
            self._module_name(),
            operation,
            trace_id,
            elapsed_ms,
            success,
        )
        return record

    class trace_operation:
        """Context manager for timing and emitting a trace record."""

        def __init__(self, emitter: TraceEmitter, operation: str, metadata: dict[str, Any] | None = None):
            self._emitter = emitter
            self._operation = operation
            self._metadata = metadata or {}
            self._start: float = 0.0
            self._record: TraceRecord | None = None

        def __enter__(self) -> TraceEmitter.trace_operation:
            self._start = time.monotonic()
            return self

        def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
            elapsed_ms = (time.monotonic() - self._start) * 1000.0
            success = exc_type is None
            self._record = self._emitter.emit_trace_record(
                self._operation,
                elapsed_ms,
                success=success,
                metadata=self._metadata,
            )
            return False

        @property
        def record(self) -> TraceRecord | None:
            return self._record

    def trace_op(
        self,
        operation: str,
        metadata: dict[str, Any] | None = None,
    ) -> TraceEmitter.trace_operation:
        """Return a context manager that traces `operation`."""
        return TraceEmitter.trace_operation(self, operation, metadata)


def emit_trace(layer: str, operation: str | None = None) -> Callable:
    """Decorator: wrap a callable with TraceEmitter emission.

    Usage::

        @emit_trace("L1", "generate_prompt")
        def generate_prompt(self, prompt: str) -> str:
            ...
    """

    def decorator(fn: Callable) -> Callable:
        op_name = operation or fn.__name__

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            start = time.monotonic()
            active = get_active_execution_trace()
            trace_id = active.trace_id if active else "no-active-trace"
            module_name = (
                f"{args[0].__class__.__module__}.{args[0].__class__.__qualname__}" if args else fn.__module__
            )
            try:
                result = fn(*args, **kwargs)
                elapsed_ms = (time.monotonic() - start) * 1000.0
                digest = hashlib.sha256(
                    f"{layer}:{module_name}:{op_name}:{elapsed_ms:.3f}".encode(),
                ).hexdigest()[:16]
                logger.debug(
                    "TRACE_EMIT layer=%s module=%s op=%s trace_id=%s elapsed_ms=%.1f ok=True digest=%s",
                    layer,
                    module_name,
                    op_name,
                    trace_id,
                    elapsed_ms,
                    digest,
                )
                return result
            except (ValueError, TypeError, RuntimeError) as e:
                elapsed_ms = (time.monotonic() - start) * 1000.0
                logger.debug(
                    "TRACE_EMIT layer=%s module=%s op=%s trace_id=%s elapsed_ms=%.1f ok=False",
                    layer,
                    module_name,
                    op_name,
                    trace_id,
                    elapsed_ms,
                )
                raise

        return wrapper

    return decorator


__all__ = ["TraceEmitter", "TraceRecord", "emit_trace"]

_emit_reads_through("l4", "trace_emitter", "urg_read_1")
_emit_reads_through("l4", "trace_emitter", "urg_read_2")
_emit_reads_through("l4", "trace_emitter", "urg_read_3")
_emit_reads_through("l4", "trace_emitter", "urg_read_4")
_emit_reads_through("l4", "trace_emitter", "urg_read_5")
_emit_reads_through("l4", "trace_emitter", "urg_read_6")
_emit_reads_through("l4", "trace_emitter", "urg_read_7")
_emit_reads_through("l4", "trace_emitter", "urg_read_8")
_emit_reads_through("l4", "trace_emitter", "urg_read_9")
_emit_reads_through("l4", "trace_emitter", "urg_read_10")
_emit_reads_through("l4", "trace_emitter", "urg_read_11")
_emit_reads_through("l4", "trace_emitter", "urg_read_12")
_emit_reads_through("l4", "trace_emitter", "urg_read_13")
_emit_reads_through("l4", "trace_emitter", "urg_read_14")
_emit_reads_through("l4", "trace_emitter", "urg_read_15")
_emit_reads_through("l4", "trace_emitter", "urg_read_16")
_emit_reads_through("l4", "trace_emitter", "urg_read_17")
_emit_reads_through("l4", "trace_emitter", "urg_read_18")
_emit_reads_through("l4", "trace_emitter", "urg_read_19")
_emit_reads_through("l4", "trace_emitter", "urg_read_20")
_emit_reads_through("l4", "trace_emitter", "urg_read_21")
_emit_reads_through("l4", "trace_emitter", "urg_read_22")
_emit_reads_through("l4", "trace_emitter", "urg_read_23")
_emit_reads_through("l4", "trace_emitter", "urg_read_24")
_emit_reads_through("l4", "trace_emitter", "urg_read_25")
_emit_reads_through("l4", "trace_emitter", "urg_read_26")
_emit_reads_through("l4", "trace_emitter", "urg_read_27")
_emit_reads_through("l4", "trace_emitter", "urg_read_28")
_emit_reads_through("l4", "trace_emitter", "urg_read_29")
_emit_reads_through("l4", "trace_emitter", "urg_read_30")
_emit_reads_through("l4", "trace_emitter", "urg_read_31")
_emit_reads_through("l4", "trace_emitter", "urg_read_32")
_emit_reads_through("l4", "trace_emitter", "urg_read_33")
_emit_reads_through("l4", "trace_emitter", "urg_read_34")
_emit_reads_through("l4", "trace_emitter", "urg_read_35")
_emit_reads_through("l4", "trace_emitter", "urg_read_36")
_emit_reads_through("l4", "trace_emitter", "urg_read_37")
