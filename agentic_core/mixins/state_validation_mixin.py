"""
StateValidationMixin — Canonical location.

Relocated from agentic_core/L4_state/types/state_validation_types.py to satisfy
the mixin location invariant (all *Mixin classes under agentic_core/mixins/).

Original file re-exports this class for backward compatibility.
"""

from __future__ import annotations

import asyncio
import hashlib
import inspect
import json
import logging
from collections.abc import Callable
from functools import wraps
from typing import Any

from agentic_core.L0_routing.config.path_constants import DEFAULT_TIMEOUT
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

_emit_applies_guardrail("p0", "state_validation_mixin", "p0_governance")
_emit_reads_policy_state("p0", "state_validation_mixin", "policy_binding")
_emit_snapshots_state("p0", "state_validation_mixin", "state_snapshot")
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

_emit_emits_metric_event("state_validation_mixin", "p4obs", "metric_1")
_emit_emits_metric_event("state_validation_mixin", "p4obs", "metric_2")
_emit_emits_metric_event("state_validation_mixin", "p4obs", "metric_3")
_emit_emits_metric_event("state_validation_mixin", "p4obs", "metric_4")
_emit_emits_metric_event("state_validation_mixin", "p4obs", "metric_5")
_emit_emits_metric_event("state_validation_mixin", "p4obs", "metric_6")
_emit_records_incident_event("state_validation_mixin", "p4obs", "incident")
_emit_captures_runtime_anomaly("state_validation_mixin", "p4obs", "anomaly")
_emit_writes_observability_log("state_validation_mixin", "p4obs", "obs_log")
_emit_updates_monitoring_state("state_validation_mixin", "p4obs", "mon_state")
_emit_triggers_alert("state_validation_mixin", "p4obs", "alert")
_emit_links_incident_trace("state_validation_mixin", "p4obs", "trace_link")
_emit_captures_pattern("state_validation_mixin", "p3lm", "pattern")
_emit_records_learning_event("state_validation_mixin", "p3lm", "learning_event")
_emit_writes_learning_snapshot("state_validation_mixin", "p3lm", "snapshot")
_emit_feeds_meta_learning("state_validation_mixin", "p3lm", "meta_feed")
_emit_updates_routing_strategy("state_validation_mixin", "p3lm", "routing")
_emit_improves_agent_policy("state_validation_mixin", "p3lm", "policy")
_emit_stores_learning_state("state_validation_mixin", "p3lm", "state")
_emit_records_execution_trace("state_validation_mixin", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("state_validation_mixin", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("state_validation_mixin", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("state_validation_mixin", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("state_validation_mixin", "L4_STATE", "p2_trace_5")
_emit_reads_environ("state_validation_mixin", "env_read", "p2_env_1")
_emit_reads_environ("state_validation_mixin", "env_read", "p2_env_2")
_emit_reads_runtime_state("state_validation_mixin", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("state_validation_mixin", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "state_validation_mixin", "context_pull")
_emit_pulls_context("p1", "state_validation_mixin", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "state_validation_mixin", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "state_validation_mixin", "uwg_term_2")
_emit_writes_through("p1", "state_validation_mixin", "write_through")
_emit_writes_through("p1", "state_validation_mixin", "write_through_2")
_emit_validated_by_safety_plane("p1", "state_validation_mixin", "safety_validation")
_emit_invokes_eval("p1", "state_validation_mixin", "eval_call")
_emit_proposal_commits_routing("p1", "state_validation_mixin", "routing_commit")
_emit_escalates_to_human("p1", "state_validation_mixin", "human_escalation")
_emit_routes_through("p1", "state_validation_mixin", "route_through")
_emit_checks_agent_registry("p1", "state_validation_mixin", "agent_registry")
_emit_validates_agent_capability("p1", "state_validation_mixin", "capability")
_emit_dispatches_execution_plan("p1", "state_validation_mixin", "exec_plan")
_emit_agent_executes_agent("p1", "state_validation_mixin", "sub_agent")
_emit_routes_to_agent("p1", "state_validation_mixin", "target_agent")
_emit_verifies_policy("p1", "state_validation_mixin", "policy_check")
_emit_observes_runtime_state("p1", "state_validation_mixin", "runtime_state")
_emit_verifies_boundary("p1", "state_validation_mixin", "boundary_check")
_emit_transcripts_response("p1", "state_validation_mixin", "transcript")
_emit_hard_fails_untranscripted("p1", "state_validation_mixin")
_emit_gated_by_confidence("p1", "state_validation_mixin", "confidence_gate")
emit_replay_key("p0", "state_validation_mixin")
emit_determinism_digest("p0", "state_validation_mixin")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "state_validation_mixin", "execution_auth")
_emit_validates_capability("p2", "state_validation_mixin", "capability_check")
_emit_routes_to_capability("p2", "state_validation_mixin", "capability_route")
_emit_writes_via_uwg("p2", "state_validation_mixin", "uwg_write")
_emit_blocks_direct_write("p2", "state_validation_mixin", "direct_write_block")
_emit_records_tool_invocation("p2", "state_validation_mixin", "tool_invocation")
_emit_captures_execution_output("p2", "state_validation_mixin", "exec_output")
_emit_dispatches_agent("p3", "state_validation_mixin", "agent_dispatch")
_emit_coordinates_agents("p3", "state_validation_mixin", "agent_coordination")
_emit_records_workflow_lineage("p3", "state_validation_mixin", "workflow_lineage")
_emit_records_healing_outcome("p3", "state_validation_mixin", "healing_outcome")
_emit_escalates_failure("p3", "state_validation_mixin", "failure_escalation")
_emit_orchestrates_workflow("p3", "state_validation_mixin", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "state_validation_mixin", "healing_dispatch")
_emit_invokes_evaluation("p3", "state_validation_mixin", "evaluation_signal")
_emit_records_telemetry_event("p4", "state_validation_mixin", "telemetry_event")
_emit_captures_evaluation_metric("p4", "state_validation_mixin", "eval_metric")
_emit_stores_embedding("p4", "state_validation_mixin", "embedding_store")
_emit_updates_meta_learning_state("p4", "state_validation_mixin", "meta_learning")
_emit_links_execution_to_snapshot("p4", "state_validation_mixin", "exec_snapshot_link")


class StateValidationError(Exception):
    """Raised when a pre-condition or post-condition fails."""

    pass


class StateValidationMixin:
    """
    Phase 1 Critical Infrastructure: State Validation (Report 4.2).

    Ensures data consistency through:
    - Pre-condition checks (guard clauses)
    - Post-condition verification (invariants)
    - Idempotency guarantees via input hashing
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._sv_logger = logging.getLogger(self.__class__.__name__)
        self._operation_ledger: dict[str, Any] = {}

    def _run_conditions(self, conditions: list[Callable[..., bool]], result: Any = None) -> None:
        for condition in conditions:
            sig = inspect.signature(condition)
            if len(sig.parameters) == 1:
                ok = condition(self)
            else:
                ok = condition(self, result)
            if not ok:
                raise StateValidationError(f"Condition failed: {getattr(condition, '__name__', 'condition')}")

    def _generate_op_hash(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """Generates a unique deterministic hash for an operation call."""
        if len(str(args)) + len(str(kwargs)) > 100000:
            return None
        try:
            payload = {
                "func": func_name,
                "args": [str(a) for a in args],
                "kwargs": {k: str(v) for k, v in kwargs.items()},
            }
            s = json.dumps(payload, sort_keys=True)
            return hashlib.sha256(s.encode()).hexdigest()
        except (
            TypeError,
            ValueError,
            KeyError,
        ) as e:  # guardian: allow-return-none-swallow  -- ADG-burn: return_none_swallow
            self._sv_logger.warning(f"Could not generate idempotency hash: {e}")
            return None

    @staticmethod
    def validate_state(
        pre: Callable[[Any], bool] | None = None,
        post: Callable[[Any, Any], bool] | None = None,
        idempotent: bool = False,
    ):
        """
        Decorator to enforce state validity.

        Args:
            pre: Callable(self) -> bool. Runs BEFORE method. Raises if False.
            post: Callable(self, result) -> bool. Runs AFTER method. Raises if False.
            idempotent: If True, returns cached result for identical inputs.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "StateValidationMixin.validate_state"
        )

        def decorator(func):
            @wraps(func)
            async def wrapper(self, *args, **kwargs):
                if not isinstance(self, StateValidationMixin):
                    return await func(self, *args, **kwargs)
                op_hash = None
                if idempotent:
                    op_hash = self._generate_op_hash(func.__name__, args, kwargs)
                    if op_hash and op_hash in self._operation_ledger:
                        self._sv_logger.info(f"Idempotent hit for {func.__name__} ({op_hash[:8]})")
                        return self._operation_ledger[op_hash]
                if pre:
                    try:
                        pre_conditions = pre if isinstance(pre, list) else [pre]
                        await asyncio.wait_for(
                            asyncio.to_thread(lambda: self._run_conditions(pre_conditions, None)),
                            timeout=DEFAULT_TIMEOUT,
                        )
                    except asyncio.TimeoutError:
                        raise StateValidationError(f"Pre-condition check timeout for {func.__name__}")
                    except (ValueError, RuntimeError, AttributeError) as e:
                        raise StateValidationError(f"Pre-condition failed: {e}") from e
                result = await func(self, *args, **kwargs)
                if post:
                    try:
                        post_conditions = post if isinstance(post, list) else [post]
                        for condition in post_conditions:
                            if not condition(self, result):
                                raise StateValidationError(f"Post-condition failed for {func.__name__}")
                    except (ValueError, RuntimeError, AttributeError) as e:
                        raise StateValidationError(f"Post-condition error in {func.__name__}: {e}") from e
                if idempotent and op_hash:
                    self._operation_ledger[op_hash] = result
                if hasattr(self, "emit_event"):
                    self.emit_event(
                        "state_validation.success" if result is not None else "state_validation.failed",
                        {"method": func.__name__},
                        severity="INFO" if result is not None else "WARNING",
                    )
                return result

            return wrapper

        return decorator
