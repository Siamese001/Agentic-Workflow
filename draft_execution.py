"""Draft execution stack."""
from __future__ import annotations

from typing import Any, Dict

from stacks_v10_8.safety_policy_stack import SafetyPolicyStack
from stacks_v10_8.policy_stack import PolicyStack


class DraftingExecutionStack:
    """Assembles final drafts from plans and bullets."""

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

    async def run_async(
        self,
        state: Dict[str, Any],
        bullet_payload: Dict[str, Any],
        draft_plan_payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        sections = draft_plan_payload.get("draft", {}).get("plan", {}).get("sections", [])
        bullets = bullet_payload.get("bullets", {}).get("generated", [])
        draft_sections = {
            section: f"Section {section} with {len(bullets)} bullets"
            for section in sections
        }
        state_patch = {"draft": {"sections": draft_sections}}
        safety_report = self.safety_policy.evaluate_node(state_patch)
        state_patch["safety_report"] = safety_report.to_dict()
        decision = self.policy_stack.guard_output(state_patch)
        state_patch["policy"] = decision.model_dump()
        return state_patch
