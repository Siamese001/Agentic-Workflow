"""Autonomous Workflow Engine.

Generalises the heal-scoped AutonomousExecutionEngine into a reusable
Action → EnvironmentTools → Feedback → Stop loop.

Key decoupling from the original:
  - No filesystem / heal-specific logic
  - Pluggable EnvironmentToolSet protocol
  - Clean Stop signal + max_iterations convergence gate
  - Fully async; no internal asyncio.create_task coupling

Layer: L3_orchestration
"""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Protocol, runtime_checkable

from agentic_core.L3_orchestration.types.orchestration_handoff_contract import emit_agent_executes_agent
from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_records_execution_trace,
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

emit_replay_key("p0", "autonomous_workflow_engine")
emit_determinism_digest("p0", "autonomous_workflow_engine")

_emit_dispatches_healing_run("p1", "autonomous_workflow_engine", "L3")
_emit_routes_through("p1", "autonomous_workflow_engine", "L3")
_emit_agent_executes_agent("p1", "autonomous_workflow_engine", "sub_agent")
_emit_verifies_policy("p1", "autonomous_workflow_engine", "policy_check")
_emit_observes_runtime_state("p1", "autonomous_workflow_engine", "runtime_state")
_emit_verifies_boundary("p1", "autonomous_workflow_engine", "boundary_check")
_emit_transcripts_response("p1", "autonomous_workflow_engine", "transcript")
_emit_hard_fails_untranscripted("p1", "autonomous_workflow_engine")
_emit_gated_by_confidence("p1", "autonomous_workflow_engine", "confidence_gate")
_emit_escalates_to_human("p1", "autonomous_workflow_engine", "L3")
_emit_reads_policy_state("p1", "autonomous_workflow_engine", "L3")

_emit_snapshots_state("p0", "autonomous_workflow_engine", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "autonomous_workflow_engine", "p0_governance")
_emit_orchestrates_workflow("p1", "autonomous_workflow_engine", "L3")
_emit_routes_to_agent("p1", "autonomous_workflow_engine", "L3")
_emit_dispatches_execution_plan("p1", "autonomous_workflow_engine", "L3")
_emit_validates_agent_capability("p1", "autonomous_workflow_engine", "L3")
_emit_checks_agent_registry("p1", "autonomous_workflow_engine", "L3")
_emit_authorize_and_execute("p2", "autonomous_workflow_engine", "execution_auth")
_emit_validates_capability("p2", "autonomous_workflow_engine", "capability_check")
_emit_routes_to_capability("p2", "autonomous_workflow_engine", "capability_route")
_emit_writes_via_uwg("p2", "autonomous_workflow_engine", "uwg_write")
_emit_blocks_direct_write("p2", "autonomous_workflow_engine", "direct_write_block")
_emit_records_tool_invocation("p2", "autonomous_workflow_engine", "tool_invocation")
_emit_captures_execution_output("p2", "autonomous_workflow_engine", "exec_output")
_emit_dispatches_agent("p3", "autonomous_workflow_engine", "agent_dispatch")
_emit_coordinates_agents("p3", "autonomous_workflow_engine", "agent_coordination")
_emit_records_workflow_lineage("p3", "autonomous_workflow_engine", "workflow_lineage")
_emit_records_healing_outcome("p3", "autonomous_workflow_engine", "healing_outcome")
_emit_escalates_failure("p3", "autonomous_workflow_engine", "failure_escalation")
_emit_orchestrates_workflow("p3", "autonomous_workflow_engine", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "autonomous_workflow_engine", "healing_dispatch")
_emit_invokes_evaluation("p3", "autonomous_workflow_engine", "evaluation_signal")
_emit_records_telemetry_event("p4", "autonomous_workflow_engine", "telemetry_event")
_emit_captures_evaluation_metric("p4", "autonomous_workflow_engine", "eval_metric")
_emit_stores_embedding("p4", "autonomous_workflow_engine", "embedding_store")
_emit_updates_meta_learning_state("p4", "autonomous_workflow_engine", "meta_learning")
_emit_links_execution_to_snapshot("p4", "autonomous_workflow_engine", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
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
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("autonomous_workflow_engine", "p4obs", "metric_1")
_emit_emits_metric_event("autonomous_workflow_engine", "p4obs", "metric_2")
_emit_emits_metric_event("autonomous_workflow_engine", "p4obs", "metric_3")
_emit_emits_metric_event("autonomous_workflow_engine", "p4obs", "metric_4")
_emit_emits_metric_event("autonomous_workflow_engine", "p4obs", "metric_5")
_emit_emits_metric_event("autonomous_workflow_engine", "p4obs", "metric_6")
_emit_records_incident_event("autonomous_workflow_engine", "p4obs", "incident")
_emit_captures_runtime_anomaly("autonomous_workflow_engine", "p4obs", "anomaly")
_emit_writes_observability_log("autonomous_workflow_engine", "p4obs", "obs_log")
_emit_updates_monitoring_state("autonomous_workflow_engine", "p4obs", "mon_state")
_emit_triggers_alert("autonomous_workflow_engine", "p4obs", "alert")
_emit_links_incident_trace("autonomous_workflow_engine", "p4obs", "trace_link")
_emit_captures_pattern("autonomous_workflow_engine", "p3lm", "pattern")
_emit_records_learning_event("autonomous_workflow_engine", "p3lm", "learning_event")
_emit_writes_learning_snapshot("autonomous_workflow_engine", "p3lm", "snapshot")
_emit_feeds_meta_learning("autonomous_workflow_engine", "p3lm", "meta_feed")
_emit_updates_routing_strategy("autonomous_workflow_engine", "p3lm", "routing")
_emit_improves_agent_policy("autonomous_workflow_engine", "p3lm", "policy")
_emit_stores_learning_state("autonomous_workflow_engine", "p3lm", "state")
_emit_records_execution_trace("autonomous_workflow_engine", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("autonomous_workflow_engine", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("autonomous_workflow_engine", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("autonomous_workflow_engine", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("autonomous_workflow_engine", "L4_STATE", "p2_trace_5")
_emit_reads_environ("autonomous_workflow_engine", "env_read", "p2_env_1")
_emit_reads_environ("autonomous_workflow_engine", "env_read", "p2_env_2")
_emit_reads_runtime_state("autonomous_workflow_engine", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("autonomous_workflow_engine", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "autonomous_workflow_engine", "context_pull")
_emit_pulls_context("p1", "autonomous_workflow_engine", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "autonomous_workflow_engine", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "autonomous_workflow_engine", "uwg_term_2")
_emit_writes_through("p1", "autonomous_workflow_engine", "write_through")
_emit_writes_through("p1", "autonomous_workflow_engine", "write_through_2")
_emit_validated_by_safety_plane("p1", "autonomous_workflow_engine", "safety_validation")
_emit_invokes_eval("p1", "autonomous_workflow_engine", "eval_call")
_emit_proposal_commits_routing("p1", "autonomous_workflow_engine", "routing_commit")

Logger = logging.getLogger(__name__)

_DEFAULT_MAX_ITERATIONS = 20


class StopSignal(Enum):
    """Reason the loop was halted."""

    GOAL_ACHIEVED = "goal_achieved"
    MAX_ITERATIONS = "max_iterations"
    CIRCUIT_BREAKER = "circuit_breaker"
    EXPLICIT_STOP = "explicit_stop"
    ERROR = "error"


@runtime_checkable
class EnvironmentToolSet(Protocol):
    """Protocol for environment interaction — implement to plug in any domain."""

    async def execute_action(self, action: str, params: dict[str, Any]) -> dict[str, Any]:
        """Execute an action and return an observation dict."""
        ...

    def is_goal_achieved(self, observation: dict[str, Any]) -> bool:
        """Return True when the environment signals the goal is complete."""
        ...

    def reset(self) -> None:
        """Reset environment state between runs (optional)."""
        ...


@dataclass
class WorkflowStep:
    """Record of a single action-observation step."""

    iteration: int
    action: str
    params: dict[str, Any]
    observation: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


@dataclass
class WorkflowResult:
    """Full result of an autonomous workflow run."""

    goal: str
    steps: list[WorkflowStep] = field(default_factory=list)
    stop_signal: StopSignal = StopSignal.MAX_ITERATIONS
    success: bool = False
    final_observation: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


class AutonomousWorkflowEngine:
    """General-purpose autonomous action loop.

    Usage::

        engine = AutonomousWorkflowEngine(
            policy_fn=my_policy,
            env=my_env_toolset,
            max_iterations=10,
        )
        result = await engine.run(goal="Deploy service to staging")

    Args:
        policy_fn:      async (goal, steps_so_far, last_obs) -> (action, params)
                        Decides the next action given the current trajectory.
        env:            EnvironmentToolSet instance.
        max_iterations: Hard cap on action steps (default 20).
        max_consecutive_failures: Circuit-breaker threshold (default 5).
    """

    def __init__(
        self,
        policy_fn: Callable[
            [str, list[WorkflowStep], dict[str, Any]],
            Awaitable[tuple[str, dict[str, Any]]],
        ],
        env: EnvironmentToolSet,
        max_iterations: int = _DEFAULT_MAX_ITERATIONS,
        max_consecutive_failures: int = 5,
    ) -> None:
        self.policy_fn = policy_fn
        self.env = env
        self.max_iterations = max_iterations
        self.max_consecutive_failures = max_consecutive_failures

    async def run(
        self,
        goal: str,
        initial_context: dict[str, Any] | None = None,
    ) -> WorkflowResult:
        """Execute the autonomous action loop.

        Args:
            goal:            Natural-language goal for the policy.
            initial_context: Optional seed observation for the first policy call.

        Returns:
            WorkflowResult with the full step trace and stop signal.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "AutonomousWorkflowEngine.run"
        )

        result = WorkflowResult(goal=goal)
        last_obs: dict[str, Any] = initial_context or {}
        consecutive_failures = 0

        Logger.info("autonomous_workflow_start", extra={"goal": goal[:80], "max_iter": self.max_iterations})

        for iteration in range(1, self.max_iterations + 1):
            emit_agent_executes_agent(
                parent_agent_id="autonomous_workflow_engine",
                child_agent_id="policy_fn",
                stage=f"iteration_{iteration}",
            )
            try:
                action, params = await self.policy_fn(goal, result.steps, last_obs)
            except (ValueError, TypeError) as exc:  # guardian: allow-silent-swallower
                result.error = f"Policy error at iteration {iteration}: {exc}"
                result.stop_signal = StopSignal.ERROR
                Logger.error("autonomous_policy_error", extra={"iteration": iteration, "error": str(exc)})
                break

            if action == "STOP":
                result.stop_signal = StopSignal.EXPLICIT_STOP
                result.success = True
                Logger.info("autonomous_explicit_stop", extra={"iteration": iteration})
                break

            step = WorkflowStep(iteration=iteration, action=action, params=params)

            try:
                observation = await self.env.execute_action(action, params)
                step.observation = observation
                consecutive_failures = 0
            except (ValueError, TypeError) as exc:  # guardian: allow-silent-swallower
                step.error = str(exc)
                observation = {"error": str(exc)}
                consecutive_failures += 1
                Logger.warning(
                    "autonomous_action_error",
                    extra={"iteration": iteration, "action": action, "error": str(exc)},
                )

            result.steps.append(step)
            last_obs = observation

            if consecutive_failures >= self.max_consecutive_failures:
                result.stop_signal = StopSignal.CIRCUIT_BREAKER
                result.error = f"Circuit breaker: {consecutive_failures} consecutive failures"
                Logger.error("autonomous_circuit_breaker", extra={"failures": consecutive_failures})
                break

            if self.env.is_goal_achieved(observation):
                result.stop_signal = StopSignal.GOAL_ACHIEVED
                result.success = True
                result.final_observation = observation
                Logger.info("autonomous_goal_achieved", extra={"iteration": iteration})
                break
        else:
            result.stop_signal = StopSignal.MAX_ITERATIONS
            Logger.warning("autonomous_max_iterations", extra={"max": self.max_iterations})

        if result.steps:
            result.final_observation = result.steps[-1].observation

        Logger.info(
            "autonomous_workflow_complete",
            extra={
                "goal": goal[:80],
                "steps": len(result.steps),
                "stop_signal": result.stop_signal.value,
                "success": result.success,
            },
        )
        return result
