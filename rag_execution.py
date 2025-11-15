"""RAG execution stack stub."""
from __future__ import annotations

from typing import Any, Dict

from stacks_v10_8.safety_policy_stack import SafetyPolicyStack


class RAGExecutionStack:
    """Executes a prepared RAG plan and emits state patches."""

    def __init__(self, context: Any, debug_mode: bool = False) -> None:
        self.context = context
        self.debug_mode = debug_mode
        self.safety_policy = getattr(
            context,
            "safety_policy",
            SafetyPolicyStack(context, debug_mode),
        )

    async def run_async(self, state: Dict[str, Any], plan_payload: Dict[str, Any]) -> Dict[str, Any]:
        plan = plan_payload.get("rag", {}).get("plan", {})
        results = state.get("rag", {}).get("results", [])
        results.append({"plan_goal": plan.get("goal", ""), "status": "executed"})
        state_patch = {"rag": {"results": results, "last_plan": plan}}
        safety_report = self.safety_policy.evaluate_node(state_patch)
        state_patch["safety_report"] = safety_report.to_dict()
        return state_patch
