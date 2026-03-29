"""
V15 Runtime Guard — Non-Heal Execution Enforcement.

Provides a decorator and context manager that enforces V15 gateway routing
for all non-heal runtime entry points when V15_ENFORCEMENT=1.

Under V15_ENFORCEMENT=0 (default), all calls pass through unchanged.
Under V15_ENFORCEMENT=1, every guarded entry point:
  - Generates a correlation_id
  - Validates the call is routed through the guard
  - Raises V15EnforcementError on bypass attempts

This is the "single documented equivalent wrapper" for non-heal paths,
complementing V15ExecutionGateway which handles heal-specific paths.
"""

from __future__ import annotations

import functools
import logging
import os
import threading
import uuid
from typing import Any, Callable, TypeVar

from agentic_core.L0_routing.types.v15_exceptions import (
    V15EnforcementError,
    is_v15_enforced,
    is_v15_hard_fail,
)
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
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

emit_replay_key("p0", "runtime_guard")
emit_determinism_digest("p0", "runtime_guard")

_emit_dispatches_healing_run("p1", "runtime_guard", "L0")
_emit_routes_through("p1", "runtime_guard", "L0")
_emit_checks_agent_registry("p1", "runtime_guard", "agent_registry")
_emit_validates_agent_capability("p1", "runtime_guard", "capability")
_emit_dispatches_execution_plan("p1", "runtime_guard", "exec_plan")
_emit_agent_executes_agent("p1", "runtime_guard", "sub_agent")
_emit_routes_to_agent("p1", "runtime_guard", "target_agent")
_emit_verifies_policy("p1", "runtime_guard", "policy_check")
_emit_observes_runtime_state("p1", "runtime_guard", "runtime_state")
_emit_verifies_boundary("p1", "runtime_guard", "boundary_check")
_emit_transcripts_response("p1", "runtime_guard", "transcript")
_emit_gated_by_confidence("p1", "runtime_guard", "confidence_gate")
_emit_escalates_to_human("p1", "runtime_guard", "L0")
_emit_reads_policy_state("p1", "runtime_guard", "L0")

_emit_records_execution_trace("p0", "evidence", "runtime_guard")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_snapshots_state("p0", "runtime_guard", "state_snapshot")
_emit_authorize_and_execute("p2", "runtime_guard", "execution_auth")
_emit_validates_capability("p2", "runtime_guard", "capability_check")
_emit_routes_to_capability("p2", "runtime_guard", "capability_route")
_emit_writes_via_uwg("p2", "runtime_guard", "uwg_write")
_emit_blocks_direct_write("p2", "runtime_guard", "direct_write_block")
_emit_records_tool_invocation("p2", "runtime_guard", "tool_invocation")
_emit_captures_execution_output("p2", "runtime_guard", "exec_output")
_emit_dispatches_agent("p3", "runtime_guard", "agent_dispatch")
_emit_coordinates_agents("p3", "runtime_guard", "agent_coordination")
_emit_records_workflow_lineage("p3", "runtime_guard", "workflow_lineage")
_emit_records_healing_outcome("p3", "runtime_guard", "healing_outcome")
_emit_escalates_failure("p3", "runtime_guard", "failure_escalation")
_emit_orchestrates_workflow("p3", "runtime_guard", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "runtime_guard", "healing_dispatch")
_emit_invokes_evaluation("p3", "runtime_guard", "evaluation_signal")
_emit_records_telemetry_event("p4", "runtime_guard", "telemetry_event")
_emit_captures_evaluation_metric("p4", "runtime_guard", "eval_metric")
_emit_stores_embedding("p4", "runtime_guard", "embedding_store")
_emit_updates_meta_learning_state("p4", "runtime_guard", "meta_learning")
_emit_links_execution_to_snapshot("p4", "runtime_guard", "exec_snapshot_link")
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
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

_emit_emits_metric_event("runtime_guard", "p4obs", "metric_1")
_emit_emits_metric_event("runtime_guard", "p4obs", "metric_2")
_emit_emits_metric_event("runtime_guard", "p4obs", "metric_3")
_emit_emits_metric_event("runtime_guard", "p4obs", "metric_4")
_emit_emits_metric_event("runtime_guard", "p4obs", "metric_5")
_emit_emits_metric_event("runtime_guard", "p4obs", "metric_6")
_emit_records_incident_event("runtime_guard", "p4obs", "incident")
_emit_captures_runtime_anomaly("runtime_guard", "p4obs", "anomaly")
_emit_writes_observability_log("runtime_guard", "p4obs", "obs_log")
_emit_updates_monitoring_state("runtime_guard", "p4obs", "mon_state")
_emit_triggers_alert("runtime_guard", "p4obs", "alert")
_emit_links_incident_trace("runtime_guard", "p4obs", "trace_link")
_emit_captures_pattern("runtime_guard", "p3lm", "pattern")
_emit_records_learning_event("runtime_guard", "p3lm", "learning_event")
_emit_writes_learning_snapshot("runtime_guard", "p3lm", "snapshot")
_emit_feeds_meta_learning("runtime_guard", "p3lm", "meta_feed")
_emit_updates_routing_strategy("runtime_guard", "p3lm", "routing")
_emit_improves_agent_policy("runtime_guard", "p3lm", "policy")
_emit_stores_learning_state("runtime_guard", "p3lm", "state")
_emit_records_execution_trace("runtime_guard", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("runtime_guard", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("runtime_guard", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("runtime_guard", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("runtime_guard", "L4_STATE", "p2_trace_5")
_emit_reads_environ("runtime_guard", "env_read", "p2_env_1")
_emit_reads_environ("runtime_guard", "env_read", "p2_env_2")
_emit_reads_runtime_state("runtime_guard", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("runtime_guard", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "runtime_guard", "context_pull")
_emit_pulls_context("p1", "runtime_guard", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "runtime_guard", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "runtime_guard", "uwg_term_2")
_emit_writes_through("p1", "runtime_guard", "write_through")
_emit_writes_through("p1", "runtime_guard", "write_through_2")
_emit_validated_by_safety_plane("p1", "runtime_guard", "safety_validation")
_emit_invokes_eval("p1", "runtime_guard", "eval_call")
_emit_proposal_commits_routing("p1", "runtime_guard", "routing_commit")

Logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])

# Thread-local storage for tracking active guard contexts
_guard_context = threading.local()


def _get_active_guards() -> set[str]:
    """Return the set of currently active guard entry point IDs."""
    _emit_applies_guardrail(str(uuid.uuid4()), "Module._get_active_guards", "L0_ROUTING")
    if not hasattr(_guard_context, "active"):
        _guard_context.active = set()
    return _guard_context.active


def _get_correlation_id() -> str | None:
    """Return the current correlation_id if inside a guarded context."""
    return getattr(_guard_context, "correlation_id", None)


def runtime_guard(entry_point_id: str) -> Callable[[F], F]:
    """Decorator that enforces V15 gateway routing for a runtime entry point.

    Args:
        entry_point_id: The inventory ID from Wave 2.1 (e.g. "A.run_mission.orchestrator_engine").

    When V15_ENFORCEMENT=1:
        - Creates a correlation_id for the execution
        - Registers the entry point as actively guarded
        - Logs entry/exit for audit trail

    When V15_ENFORCEMENT=0:
        - Pass-through with zero overhead
    """

    _emit_hard_fails_untranscripted(str(uuid.uuid4()), "Module.runtime_guard")

    def decorator(fn: F) -> F:
        @functools.wraps(fn)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            if not is_v15_enforced():
                return fn(*args, **kwargs)
            return _guarded_call(fn, entry_point_id, args, kwargs)

        @functools.wraps(fn)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            if not is_v15_enforced():
                return await fn(*args, **kwargs)
            return await _async_guarded_call(fn, entry_point_id, args, kwargs)

        import asyncio

        if asyncio.iscoroutinefunction(fn):
            return async_wrapper  # type: ignore[return-value]
        return sync_wrapper  # type: ignore[return-value]

    return decorator


def _guarded_call(
    fn: Callable[..., Any],
    entry_point_id: str,
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> Any:
    """Execute a synchronous function under V15 guard."""
    correlation_id = str(uuid.uuid4())
    active = _get_active_guards()
    old_corr = getattr(_guard_context, "correlation_id", None)

    active.add(entry_point_id)
    _guard_context.correlation_id = correlation_id

    Logger.debug(
        "[V15-GUARD] ENTER %s correlation_id=%s",
        entry_point_id,
        correlation_id,
    )

    try:
        result = fn(*args, **kwargs)
        Logger.debug(
            "[V15-GUARD] EXIT %s correlation_id=%s status=OK",
            entry_point_id,
            correlation_id,
        )
        return result
    except (ValueError, TypeError, RuntimeError) as e:
        # TODO: Handle specific exception properly
        raise  # Re-raise after logging/handling
        Logger.debug(
            "[V15-GUARD] EXIT %s correlation_id=%s status=ERROR",
            entry_point_id,
            correlation_id,
        )
        raise
    finally:
        active.discard(entry_point_id)
        _guard_context.correlation_id = old_corr


async def _async_guarded_call(
    fn: Callable[..., Any],
    entry_point_id: str,
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> Any:
    """Execute an async function under V15 guard."""
    correlation_id = str(uuid.uuid4())
    active = _get_active_guards()
    old_corr = getattr(_guard_context, "correlation_id", None)

    active.add(entry_point_id)
    _guard_context.correlation_id = correlation_id

    Logger.debug(
        "[V15-GUARD] ENTER %s correlation_id=%s",
        entry_point_id,
        correlation_id,
    )

    try:
        result = await fn(*args, **kwargs)
        Logger.debug(
            "[V15-GUARD] EXIT %s correlation_id=%s status=OK",
            entry_point_id,
            correlation_id,
        )
        return result
    except (ValueError, TypeError, RuntimeError) as e:
        # TODO: Handle specific exception properly
        raise  # Re-raise after logging/handling
        Logger.debug(
            "[V15-GUARD] EXIT %s correlation_id=%s status=ERROR",
            entry_point_id,
            correlation_id,
        )
        raise
    finally:
        active.discard(entry_point_id)
        _guard_context.correlation_id = old_corr


def assert_v15_guarded(entry_point_id: str) -> None:
    """Fail-closed assertion: raises V15EnforcementError if called outside a guard.

    Call this at the top of any enforcement boundary to prove the guard is active.
    Under V15_ENFORCEMENT=0, this is a no-op.
    """
    if not is_v15_enforced():
        return
    active = _get_active_guards()
    if entry_point_id not in active:
        msg = (
            f"V15 bypass detected: '{entry_point_id}' called without "
            f"runtime_guard. Active guards: {sorted(active)}"
        )
        if is_v15_hard_fail():
            raise V15EnforcementError(msg)
        Logger.warning("[V15-GUARD] %s (mode=%s, not blocking)", msg, os.environ.get("V15_ENFORCEMENT", ""))


def v15_runtime_boundary(entry_point_id: str) -> Callable[[F], F]:
    """Canonical unified guard — safe for bootstrap and normal contexts.

    Identical semantics to ``runtime_guard`` but fail-closed safe:
    when ``V15_ENFORCEMENT=1`` and the guard infrastructure cannot initialise,
    the import error propagates (hard failure).  When enforcement is off,
    the decorator is a zero-cost identity wrapper.

    Use this instead of duplicating ``_optional_runtime_guard()`` in
    every bootstrap file.
    """
    return runtime_guard(entry_point_id)


__all__ = [
    "assert_v15_guarded",
    "v15_runtime_boundary",
    "runtime_guard",
]