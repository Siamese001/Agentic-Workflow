"""RAG execution stack stub."""
from __future__ import annotations

from typing import Any, Dict

from stacks_v10_8.safety_policy_stack import SafetyPolicyStack
from stacks_v10_8.policy_stack import PolicyStack
from stacks_v10_8.constitutional_engine import ConstitutionalEngine


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
        self.policy_stack = getattr(
            context,
            "policy_stack",
            PolicyStack(context, debug_mode),
        )
        self.constitutional_engine = getattr(
            context,
            "constitutional_engine",
            ConstitutionalEngine(),
        )

    async def run_async(self, state: Dict[str, Any], plan_payload: Dict[str, Any]) -> Dict[str, Any]:
        plan = plan_payload.get("rag", {}).get("plan", {})
        results = state.get("rag", {}).get("results", [])
        results.append({"plan_goal": plan.get("goal", ""), "status": "executed"})
        state_patch = {"rag": {"results": results, "last_plan": plan}}
        safety_report = self.safety_policy.evaluate_node(state_patch)
        state_patch["safety_report"] = safety_report.to_dict()
        decision = self.policy_stack.guard_output(state_patch)
        state_patch["policy"] = decision.model_dump()
        review = self.constitutional_engine.review_node(state_patch)
        state_patch["constitutional_review"] = review.dict()
        return state_patch
