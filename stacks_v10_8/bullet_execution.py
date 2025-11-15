"""Pure action implementation of the v10.8 bullet execution stack."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from core_v10_7 import BaseAgent, BulletPlan
from stacks_v10_7.bullet import BulletCoordinatorAgent


class BulletExecutionStack(BaseAgent):
    """Generates deterministic bullets by applying a BulletPlan to resume data."""

    def __init__(self, context: Any, debug_mode: bool = False) -> None:
        super().__init__(context, debug_mode)
        self.coordinator = BulletCoordinatorAgent(context, debug_mode)
        self.bullets_per_experience = max(
            1, getattr(self.config.agent_stacks, "bullets_per_experience", 2)
        )

    async def run_async(
        self, state: Dict[str, Any], workflow_id: Optional[str] = None
    ) -> Dict[str, Any]:
        workflow_id = workflow_id or state.get("metadata", {}).get("workflow_id", "")
        plan = self._plan_from_state(state)
        experiences = self._extract_experiences(state)
        raw_bullets = self._generate_bullets(plan, experiences, workflow_id)
        resume_section = state.get("resume", {}).get("master_resume", {})
        enriched = await self.coordinator.run_async(raw_bullets, resume_section, workflow_id)

        return {
            "bullets": {
                "plan": plan.model_dump(),
                "generated_bullets": enriched,
                "instructions": self._plan_instructions(plan),
            }
        }

    def _plan_from_state(self, state: Dict[str, Any]) -> BulletPlan:
        plan_payload = state.get("bullets", {}).get("plan")
        if plan_payload is None:
            raise ValueError("Bullet plan missing from state['bullets']['plan']")
        if isinstance(plan_payload, BulletPlan):
            return plan_payload
        return BulletPlan.model_validate(plan_payload)

    def _extract_experiences(self, state: Dict[str, Any]) -> List[Dict[str, Any]]:
        resume = state.get("resume", {})
        master_resume = resume.get("master_resume") or {}
        experiences = master_resume.get("professional_experience") or []
        return list(experiences)

    def _plan_instructions(self, plan: BulletPlan) -> Dict[str, Any]:
        return {
            "target_sections": plan.target_sections,
            "highlight_order": plan.highlight_order,
            "metrics_focus": plan.metrics_focus,
            "style_guidelines": plan.style_guidelines,
            "validation_checks": plan.validation_checks,
        }

    def _generate_bullets(
        self,
        plan: BulletPlan,
        experiences: List[Dict[str, Any]],
        workflow_id: str,
    ) -> List[Dict[str, Any]]:
        generated: List[Dict[str, Any]] = []
        guidelines = "; ".join(plan.style_guidelines)
        metrics_hint = ", ".join(plan.metrics_focus) or "impact metrics"
        highlights = plan.highlight_order or []

        for exp_index, experience in enumerate(experiences):
            company = experience.get("company", "")
            title = experience.get("title", "")
            exp_label = highlights[exp_index % len(highlights)] if highlights else "Key win"
            summary = experience.get("impact_summary") or experience.get("bullet_pool", [""])[0]
            for slot in range(self.bullets_per_experience):
                bullet_id = f"{workflow_id or 'wf'}-exp{exp_index}-b{slot}"
                focus_metric = plan.metrics_focus[slot % len(plan.metrics_focus)] if plan.metrics_focus else metrics_hint
                bullet_text = self._compose_text(
                    title=title,
                    company=company,
                    exp_label=exp_label,
                    focus_metric=focus_metric,
                    summary=summary,
                    guidelines=guidelines,
                )
                generated.append(
                    {
                        "id": bullet_id,
                        "text": bullet_text,
                        "experience": experience,
                    }
                )
        return generated

    def _compose_text(
        self,
        *,
        title: str,
        company: str,
        exp_label: str,
        focus_metric: str,
        summary: str,
        guidelines: str,
    ) -> str:
        parts = [p for p in [title, company] if p]
        header = " at ".join(parts) if parts else exp_label
        summary_fragment = summary or exp_label
        guideline_fragment = guidelines.split(";")[0] if guidelines else "Impact-first phrasing"
        return (
            f"{header}: Delivered {summary_fragment} while emphasizing {focus_metric}. "
            f"[{guideline_fragment.strip()}]"
        )
