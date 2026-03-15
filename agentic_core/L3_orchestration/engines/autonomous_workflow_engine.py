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

from agentic_core.L3_orchestration.contracts.orchestration_handoff_contract import emit_agent_executes_agent
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_records_execution_trace,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
)

_emit_snapshots_state("p0", "autonomous_workflow_engine", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "autonomous_workflow_engine", "p0_governance")

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
            except Exception as exc:  # guardian: allow-silent-swallower
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
            except Exception as exc:  # guardian: allow-silent-swallower
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
