"""Pure action implementation of the v10.8 drafting execution stack."""

from __future__ import annotations

import json
from typing import Any, Dict, Optional

from core_v10_7 import BaseAgent, DraftPlan, StrategyPlan
from agent_stacks_v10_8.components.drafting import (
    ComplianceEditorAgent,
    NarrativeStylistAgent,
    StructureLeadAgent,
)


class DraftingExecutionStack(BaseAgent):
    """Applies a DraftPlan by invoking deterministic drafting specialists."""

    def __init__(self, context: Any, debug_mode: bool = False) -> None:
        super().__init__(context, debug_mode)
        self.structure_lead = StructureLeadAgent(context, debug_mode)
        self.narrative_stylist = NarrativeStylistAgent(context, debug_mode)
        self.compliance_editor = ComplianceEditorAgent(context, debug_mode)
        self.safety_policy = getattr(context, "safety_policy", None)
        self.policy_stack = getattr(context, "policy_stack", None)
        self.constitutional_engine = getattr(context, "constitutional_engine", None)

    async def run_async(
        self, state: Dict[str, Any], workflow_id: Optional[str] = None
    ) -> Dict[str, Any]:
        workflow_id = workflow_id or state.get("metadata", {}).get("workflow_id", "")
        plan = self._plan_from_state(state)
        bullets = state.get("bullets", {}).get("generated_bullets", [])
        strategy = self._strategy_from_state(state, plan)

        structure_packet = await self.structure_lead.run_async(
            bullets, strategy, workflow_id
        )
        narrative_packet = await self.narrative_stylist.run_async(
            structure_packet.sections, strategy, workflow_id
        )
        compliance_packet = await self.compliance_editor.run_async(
            narrative_packet.sections, workflow_id
        )

        final_sections = self._apply_plan_structure(plan, compliance_packet.sections)
        artifacts = {
            "draft": {
                "structure": structure_packet.model_dump(),
                "narrative": narrative_packet.model_dump(),
                "compliance": compliance_packet.model_dump(),
            }
        }

        patch = {
            "draft": {
                "plan": plan.model_dump(),
                "sections": final_sections,
                "tone": plan.tone,
                "structure": plan.structure,
            },
            "artifacts": {"artifacts": artifacts},
        }
        safety_report = state.get("safety_report") or {}
        policy_decision = state.get("policy_decision") or {}
        constitutional_review = state.get("constitutional_review") or {}
        if not hasattr(safety_report, "dict"):
            safety_report = type("_Wrapper", (), {"dict": lambda self: dict(safety_report or {})})()
        if not hasattr(policy_decision, "dict"):
            policy_decision = type("_Wrapper", (), {"dict": lambda self: dict(policy_decision or {})})()
        if not hasattr(constitutional_review, "dict"):
            constitutional_review = type(
                "_Wrapper", (), {"dict": lambda self: dict(constitutional_review or {})}
            )()
        patch["safety_report"] = safety_report.dict()
        patch["policy_decision"] = policy_decision.dict()
        patch["constitutional_review"] = constitutional_review.dict()
        return patch

    def _plan_from_state(self, state: Dict[str, Any]) -> DraftPlan:
        plan_payload = state.get("draft", {}).get("plan")
        if plan_payload is None:
            raise ValueError("Draft plan missing from state['draft']['plan']")
        if isinstance(plan_payload, DraftPlan):
            return plan_payload
        return DraftPlan.model_validate(plan_payload)

    def _strategy_from_state(self, state: Dict[str, Any], plan: DraftPlan) -> StrategyPlan:
        strategy_payload = state.get("strategy", {}).get("strategy_plan")
        if isinstance(strategy_payload, StrategyPlan):
            base = strategy_payload
        elif strategy_payload:
            base = StrategyPlan.model_validate(strategy_payload)
        else:
            base = StrategyPlan(
                strategy_name="draft-plan",
                focus_areas=plan.key_messages or ["core narrative"],
                key_achievements_to_highlight=plan.key_messages[:3],
                tone=plan.tone,
            )
        if base.tone != plan.tone:
            base.tone = plan.tone
        return base

    def _apply_plan_structure(
        self, plan: DraftPlan, sections: Dict[str, Any]
    ) -> Dict[str, Any]:
        ordered_sections: Dict[str, Any] = {}
        for section_name in plan.structure:
            key = section_name.lower().replace(" ", "_")
            payload = json.loads(json.dumps(sections.get(key) or sections.get(section_name) or {}))
            if key == "executive_summary" and plan.key_messages:
                summary = payload.get("draft", "")
                highlights = "; ".join(plan.key_messages)
                payload["draft"] = f"{summary} | Key Messages: {highlights}".strip()
                payload["tone"] = plan.tone
            ordered_sections[key] = payload
        return ordered_sections

    async def run_from_state_async(
        self, state: Dict[str, Any], workflow_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Route drafting orchestration through the L2 stack."""

        from .draft_orchestration import DraftOrchestratorStack

        orchestrator = DraftOrchestratorStack(self.context, self.debug_mode)
        return await orchestrator.run_async(
            state,
            workflow_id or state.get("metadata", {}).get("workflow_id", ""),
            state_snapshot=state,
        )
