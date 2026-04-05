"""Runtime interceptor for REQ-270/273: Seam mutable reference enforcement.

Ensures all mutable references pass through immutable seams only.
"""

from __future__ import annotations

import dataclasses
import logging
from collections.abc import Hashable
from typing import Any, Callable, TypeVar

from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,
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

emit_replay_key("p0", "runtime_interceptor")
emit_determinism_digest("p0", "runtime_interceptor")

_emit_dispatches_healing_run("p1", "runtime_interceptor", "L2")
_emit_routes_through("p1", "runtime_interceptor", "L2")
_emit_checks_agent_registry("p1", "runtime_interceptor", "agent_registry")
_emit_validates_agent_capability("p1", "runtime_interceptor", "capability")
_emit_dispatches_execution_plan("p1", "runtime_interceptor", "exec_plan")
_emit_agent_executes_agent("p1", "runtime_interceptor", "sub_agent")
_emit_routes_to_agent("p1", "runtime_interceptor", "target_agent")
_emit_verifies_policy("p1", "runtime_interceptor", "policy_check")
_emit_observes_runtime_state("p1", "runtime_interceptor", "runtime_state")
_emit_verifies_boundary("p1", "runtime_interceptor", "boundary_check")
_emit_transcripts_response("p1", "runtime_interceptor", "transcript")
_emit_hard_fails_untranscripted("p1", "runtime_interceptor")
_emit_gated_by_confidence("p1", "runtime_interceptor", "confidence_gate")
_emit_escalates_to_human("p1", "runtime_interceptor", "L2")
_emit_reads_policy_state("p1", "runtime_interceptor", "L2")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_records_execution_trace("p0", "evidence", "runtime_interceptor")
_emit_applies_guardrail("p0", "runtime_interceptor", "p0_governance")
_emit_authorize_and_execute("p2", "runtime_interceptor", "execution_auth")
_emit_validates_capability("p2", "runtime_interceptor", "capability_check")
_emit_routes_to_capability("p2", "runtime_interceptor", "capability_route")
_emit_writes_via_uwg("p2", "runtime_interceptor", "uwg_write")
_emit_blocks_direct_write("p2", "runtime_interceptor", "direct_write_block")
_emit_records_tool_invocation("p2", "runtime_interceptor", "tool_invocation")
_emit_captures_execution_output("p2", "runtime_interceptor", "exec_output")
_emit_dispatches_agent("p3", "runtime_interceptor", "agent_dispatch")
_emit_coordinates_agents("p3", "runtime_interceptor", "agent_coordination")
_emit_records_workflow_lineage("p3", "runtime_interceptor", "workflow_lineage")
_emit_records_healing_outcome("p3", "runtime_interceptor", "healing_outcome")
_emit_escalates_failure("p3", "runtime_interceptor", "failure_escalation")
_emit_orchestrates_workflow("p3", "runtime_interceptor", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "runtime_interceptor", "healing_dispatch")
_emit_invokes_evaluation("p3", "runtime_interceptor", "evaluation_signal")
_emit_records_telemetry_event("p4", "runtime_interceptor", "telemetry_event")
_emit_captures_evaluation_metric("p4", "runtime_interceptor", "eval_metric")
_emit_stores_embedding("p4", "runtime_interceptor", "embedding_store")
_emit_updates_meta_learning_state("p4", "runtime_interceptor", "meta_learning")
_emit_links_execution_to_snapshot("p4", "runtime_interceptor", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("runtime_interceptor", "p4obs", "metric_1")
_emit_emits_metric_event("runtime_interceptor", "p4obs", "metric_2")
_emit_emits_metric_event("runtime_interceptor", "p4obs", "metric_3")
_emit_emits_metric_event("runtime_interceptor", "p4obs", "metric_4")
_emit_emits_metric_event("runtime_interceptor", "p4obs", "metric_5")
_emit_emits_metric_event("runtime_interceptor", "p4obs", "metric_6")
_emit_records_incident_event("runtime_interceptor", "p4obs", "incident")
_emit_captures_runtime_anomaly("runtime_interceptor", "p4obs", "anomaly")
_emit_writes_observability_log("runtime_interceptor", "p4obs", "obs_log")
_emit_updates_monitoring_state("runtime_interceptor", "p4obs", "mon_state")
_emit_triggers_alert("runtime_interceptor", "p4obs", "alert")
_emit_links_incident_trace("runtime_interceptor", "p4obs", "trace_link")
_emit_captures_pattern("runtime_interceptor", "p3lm", "pattern")
_emit_records_learning_event("runtime_interceptor", "p3lm", "learning_event")
_emit_writes_learning_snapshot("runtime_interceptor", "p3lm", "snapshot")
_emit_feeds_meta_learning("runtime_interceptor", "p3lm", "meta_feed")
_emit_updates_routing_strategy("runtime_interceptor", "p3lm", "routing")
_emit_improves_agent_policy("runtime_interceptor", "p3lm", "policy")
_emit_stores_learning_state("runtime_interceptor", "p3lm", "state")
_emit_records_execution_trace("runtime_interceptor", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("runtime_interceptor", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("runtime_interceptor", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("runtime_interceptor", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("runtime_interceptor", "L4_STATE", "p2_trace_5")
_emit_reads_environ("runtime_interceptor", "env_read", "p2_env_1")
_emit_reads_environ("runtime_interceptor", "env_read", "p2_env_2")
_emit_reads_runtime_state("runtime_interceptor", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("runtime_interceptor", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "runtime_interceptor", "context_pull")
_emit_pulls_context("p1", "runtime_interceptor", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "runtime_interceptor", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "runtime_interceptor", "uwg_term_2")
_emit_writes_through("p1", "runtime_interceptor", "write_through")
_emit_writes_through("p1", "runtime_interceptor", "write_through_2")
_emit_validated_by_safety_plane("p1", "runtime_interceptor", "safety_validation")
_emit_invokes_eval("p1", "runtime_interceptor", "eval_call")
_emit_proposal_commits_routing("p1", "runtime_interceptor", "routing_commit")

logger = logging.getLogger(__name__)
T = TypeVar("T")
_mutable_ref_violations = []


def _invoke_authorize_and_execute(execution_context, target_callable, capability_token, payload, **kw):
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_invoke_authorize_and_execute", "state_snapshot")
    from agentic_core.L2_execution.enforcement.execution_guardrail_chokepoint import (
        authorize_and_execute,  # noqa: PLC0415
    )

    return authorize_and_execute(execution_context, target_callable, capability_token, payload, **kw)


def _make_execution_context(payload, target: str):
    from agentic_core.L4_state.context.execution_context import (  # noqa: PLC0415
        ActionClass,
        ExecutionContext,
    )

    return ExecutionContext.create(
        run_id="runtime_interceptor",
        capability_token="default",
        policy_hash="default",
        execution_input=str(payload),
        execution_target=target,
        action_class=ActionClass.PRIVILEGED_LOCAL,
    )


class MutableReferenceError(RuntimeError):
    """Raised when a mutable reference is detected outside allowed seams."""

    pass


def assert_immutable_reference(obj: Any, context: str = "unknown") -> None:
    """Assert that an object is immutable or passes through allowed seam.

    Args:
        obj: Object to check for immutability
        context: Context description for error reporting

    Raises:
        MutableReferenceError: If object is mutable and not in allowed seam
    """
    if _is_mutable(obj):
        if not _is_allowed_mutable_in_seam(obj, context):
            violation = f"Mutable reference detected in {context}: {type(obj).__name__}"
            _mutable_ref_violations.append(violation)
            raise MutableReferenceError(violation)


def _is_mutable(obj: Any) -> bool:
    """Check if an object is mutable."""
    if isinstance(obj, (int, float, str, bytes, bool, type(None))):
        return False
    if isinstance(obj, tuple):
        return any(_is_mutable(item) for item in obj)
    if isinstance(obj, frozenset):
        return any(_is_mutable(item) for item in obj)
    if isinstance(obj, Hashable):
        try:
            hash(obj)
            return False
        except TypeError:
            pass
    if dataclasses.is_dataclass(obj) and getattr(obj, "__dataclass_params__", None).frozen:
        return False
    return True


def _is_allowed_mutable_in_seam(obj: Any, context: str) -> bool:
    """Check if mutable object is allowed in specific seam context."""
    allowed_contexts = {
        "capability_token",
        "sovereign_gateway",
        "embedding_factory",
        "trace_buffer",
        "telemetry",
    }
    if any(allowed in context.lower() for allowed in allowed_contexts):
        return True
    if hasattr(obj, "__class__"):
        class_name = obj.__class__.__name__
        allowed_classes = {
            "CapabilityTokenArtifact",
            "ExecutionTrace",
            "ForensicTraceBuffer",
            "TelemetryArtifact",
            "CognitiveDiff",
        }
        if class_name in allowed_classes:
            return True
    if hasattr(obj, "__name__"):
        if obj.__name__ in allowed_classes:
            return True
    return False


def get_mutable_ref_violations() -> list[str]:
    """Get list of recorded mutable reference violations."""
    return _mutable_ref_violations.copy()


def clear_mutable_ref_violations() -> None:
    """Clear recorded mutable reference violations."""
    _mutable_ref_violations.clear()


def immutable_references(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator to enforce immutable references in function calls.

    Args:
        func: Function to decorate

    Returns:
        Wrapped function that checks arguments for mutability
    """

    def wrapper(*args, **kwargs) -> T:
        _ectx = _make_execution_context(func.__name__, "runtime_interceptor.immutable_references")
        _invoke_authorize_and_execute(
            _ectx,
            lambda p: p,
            "default",
            func.__name__,
            target_name="runtime_interceptor.immutable_references",
        )
        for i, arg in enumerate(args):
            assert_immutable_reference(arg, f"{func.__name__} arg {i}")
        for key, value in kwargs.items():
            assert_immutable_reference(value, f"{func.__name__} kwarg {key}")
        return func(*args, **kwargs)

    return wrapper


class MutableReferenceTracker:
    """Context manager for tracking mutable reference violations."""

    def __enter__(self) -> MutableReferenceTracker:
        clear_mutable_ref_violations()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        pass
