"""
L2 — Execution Engine (v10_9)

Coordinates execution of L1 plans via L2 ExecutionAgents.

Responsibilities:
    • Consume a PlanObject from L1.
    • For each step, select the appropriate ExecutionAgent via ToolRouter.
    • Execute steps (sequentially) using resilience-safe wrappers.
    • Aggregate ExecutionResult objects into a ToolCallResult.
    • Track basic cost/latency via CostTracker.
    • Never mutate global state directly (L3+L4 own state).

This layer performs *execution only* — no planning, no state mutation,
no safety decisions.
"""

from __future__ import annotations

from typing import Any, Dict, List

from ..models import PlanObject, ExecutionResult, ToolCallResult
from ..exceptions import ToolExecutionError, OrchestrationError
from ..cost_tracker import CostTracker
from ..resilience import safe_execute
from ..telemetry import record_event
from .l2_tool_base import ExecutionAgent
from .tool_router import ToolRouter


class ExecutionEngine:
    """
    Core L2 execution coordinator.

    Typical usage:
        engine = ExecutionEngine(router=ToolRouter(...))
        result = await engine.run(plan, state)
    """

    def __init__(
        self,
        router: ToolRouter,
        cost_tracker: CostTracker | None = None,
    ) -> None:
        self.router = router
        self.cost_tracker = cost_tracker or CostTracker()

    async def run(self, plan: PlanObject, state: Dict[str, Any]) -> ToolCallResult:
        """
        Execute the given plan against the provided state.

        Returns:
            ToolCallResult containing per-step ExecutionResult objects and
            an optional final_payload (e.g., last step payload).

        Raises:
            OrchestrationError if routing or execution fails irrecoverably.
        """

        self.cost_tracker.start_span("execution")

        results: List[ExecutionResult] = []
        last_payload: Dict[str, Any] = {}

        steps = plan.steps or []

        try:
            for step in steps:
                step_id = str(step.get("id", f"step-{len(results) + 1}"))
                action = step.get("action", "unknown")

                # Route to appropriate ExecutionAgent
                agent: ExecutionAgent = self.router.route(step, plan=plan, state=state)
                if not agent:
                    raise OrchestrationError(f"No execution agent available for action '{action}'")

                # Execute using resilience-safe wrapper
                async def _invoke() -> ExecutionResult:
                    return await agent.execute(plan, state)

                exec_result: ExecutionResult = await safe_execute(_invoke)

                # Ensure type correctness
                if not isinstance(exec_result, ExecutionResult):
                    raise ToolExecutionError(
                        f"Execution agent returned invalid type for step '{step_id}'"
                    )

                # Attach step id into payload metadata (non-destructive)
                exec_result.payload.setdefault("_step_id", step_id)
                exec_result.payload.setdefault("_action", action)

                results.append(exec_result)
                last_payload = exec_result.payload

                # Emit telemetry event per step
                record_event(
                    "l2.step_executed",
                    {
                        "step_id": step_id,
                        "action": action,
                        "status": exec_result.status.value,
                        "model": exec_result.model,
                    },
                )

        except Exception as exc:  # noqa: BLE001
            # End span before propagating error
            self.cost_tracker.end_span("execution")
            record_event(
                "l2.execution_failed",
                {
                    "plan_id": plan.plan_id,
                    "error_type": type(exc).__name__,
                    "message": str(exc),
                },
            )
            raise OrchestrationError(str(exc)) from exc

        # End execution span on success
        self.cost_tracker.end_span("execution")

        # Emit final telemetry summary
        snapshot = self.cost_tracker.snapshot()
        record_event(
            "l2.execution_completed",
            {
                "plan_id": plan.plan_id,
                "steps": len(steps),
                "spans": snapshot.get("spans", []),
            },
        )

        return ToolCallResult(
            results=results,
            final_payload=last_payload or {},
        )
