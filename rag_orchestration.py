"""Thin L3 orchestrator for RAG planning/execution."""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict

from agent_stacks_v10_8.state_adapter_stack import StateAdapterStack
from core_v10_7_services import RobustnessStack
from orchestration_policy import OrchestrationRoutingPolicy
from rag_execution import RAGExecutionStack
from rag_planning import RAGPlanningStack
from telemetry_v10_7 import log_event


class RAGOrchestratorStack:
    """Coordinates planning/execution without mutating state directly."""

    def __init__(self, context: Any, debug_mode: bool = False) -> None:
        self.context = context
        self.config = getattr(context, "config", None)
        self.debug_mode = debug_mode
        self._adapter = StateAdapterStack(context, debug_mode)
        self._planner = RAGPlanningStack(context, debug_mode)
        self._execution = RAGExecutionStack(context, debug_mode)
        self._robustness = RobustnessStack(config=self.config)
        self._routing_policy = OrchestrationRoutingPolicy(
            context,
            debug_mode=debug_mode,
            robustness=self._robustness,
        )

    async def run_async(self, state: Dict[str, Any]) -> Dict[str, Any]:
        workflow_id = state.get("metadata", {}).get("workflow_id", "")
        current_state = deepcopy(state)
        cumulative_patch: Dict[str, Any] = {}

        plan_payload = await self._planner.run_async(current_state)
        log_event(
            "RAGOrchestratorStack",
            "plan_created",
            {
                "workflow_id": workflow_id,
                "node": "RAG_PLAN",
                "category": "signal",
                "goal": plan_payload.get("rag", {}).get("plan", {}).get("goal"),
                "use_hyde": plan_payload.get("rag", {}).get("plan", {}).get("use_hyde", True),
            },
        )
        cumulative_patch = self._adapter.merge_patch(cumulative_patch, plan_payload)
        current_state = self._adapter.apply_patch(current_state, plan_payload)

        a2a_patch = self._adapter.build_a2a_message_patch(
            sender=self.__class__.__name__,
            message_type="PLAN_CREATED",
            payload={"workflow_id": workflow_id},
        )
        cumulative_patch = self._adapter.merge_patch(cumulative_patch, a2a_patch)
        current_state = self._adapter.apply_patch(current_state, a2a_patch)

        exec_patch = await self._execution.run_async(current_state, plan_payload)
        log_event(
            "RAGOrchestratorStack",
            "execution_started",
            {
                "workflow_id": workflow_id,
                "node": "RAG_EXECUTION",
                "category": "signal",
            },
        )
        cumulative_patch = self._adapter.merge_patch(cumulative_patch, exec_patch)
        current_state = self._adapter.apply_patch(current_state, exec_patch)

        retry_patch = await self._maybe_retry_rag(current_state, workflow_id)
        if retry_patch:
            cumulative_patch = self._adapter.merge_patch(cumulative_patch, retry_patch)
            current_state = self._adapter.apply_patch(current_state, retry_patch)

        completion_patch = self._adapter.build_a2a_message_patch(
            sender=self.__class__.__name__,
            message_type="EXECUTION_COMPLETED",
            payload={"workflow_id": workflow_id},
        )
        cumulative_patch = self._adapter.merge_patch(cumulative_patch, completion_patch)
        return cumulative_patch

    async def _maybe_retry_rag(self, state: Dict[str, Any], workflow_id: str) -> Dict[str, Any]:
        decision = self._routing_policy.after_rag_execution(state)
        if decision.should_retry and self._robustness.should_retry("rag_execution", decision.reason):
            log_event(
                "RAGOrchestratorStack",
                "rag_retry",
                {
                    "workflow_id": workflow_id,
                    "node": "RAG_EXECUTION",
                    "category": "signal",
                    "reason": decision.reason,
                },
            )
            return await self._execution.run_async(state, state.get("rag", {}))
        self._robustness.reset("rag_execution")
        return {}
