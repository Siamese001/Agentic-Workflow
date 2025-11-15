"""Bullet execution stack."""
from __future__ import annotations

from typing import Any, Dict, List

from stacks_v10_8.safety_policy_stack import SafetyPolicyStack
from stacks_v10_8.policy_stack import PolicyStack


class BulletExecutionStack:
    """Generates bullet drafts for targeted sections."""

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

    async def run_async(self, state: Dict[str, Any], plan_payload: Dict[str, Any]) -> Dict[str, Any]:
        sections: List[int] = plan_payload.get("bullets", {}).get("plan", {}).get("target_sections", [])
        bullets = [
            {"section": section, "text": f"Bullet for section {section}"}
            for section in sections
        ]
        state_patch = {"bullets": {"generated": bullets}}
        safety_report = self.safety_policy.evaluate_node(state_patch)
        state_patch["safety_report"] = safety_report.to_dict()
        decision = self.policy_stack.guard_output(state_patch)
        state_patch["policy"] = decision.model_dump()
        return state_patch
