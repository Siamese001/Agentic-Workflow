"""Pure action implementation of the v10.8 bullet execution stack."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from core_v10_7 import BaseAgent, BulletPlan, StrategyPlan
from agent_stacks_v10_8.components.bullet import (
    AsyncBulletCritiqueAgent,
    AsyncBulletGeneratorAgent,
    BulletCoordinatorAgent,
)


class BulletExecutionStack(BaseAgent):
    """Generates deterministic bullets by applying a BulletPlan to resume data."""

    def __init__(self, context: Any, debug_mode: bool = False) -> None:
        super().__init__(context, debug_mode)
        self.coordinator = BulletCoordinatorAgent(context, debug_mode)
        self.generator = AsyncBulletGeneratorAgent(context, debug_mode)
        self.critique_agent = AsyncBulletCritiqueAgent(context, debug_mode)
        self.bullets_per_experience = max(
            1, getattr(self.config.agent_stacks, "bullets_per_experience", 2)
        )
        self.safety_policy = getattr(context, "safety_policy", None)
        self.policy_stack = getattr(context, "policy_stack", None)
        self.constitutional_engine = getattr(context, "constitutional_engine", None)

    async def generate_from_state_async(
        self, state: Dict[str, Any], workflow_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Extract inputs from state and delegate to ``generate_async``."""

        prompts_bucket = state.get("prompts", {})
        final_prompt = prompts_bucket.get("final_prompt")
        legacy_prompts = prompts_bucket.get("prompts", {}) if isinstance(prompts_bucket, dict) else {}
        prompt = final_prompt or legacy_prompts.get("bullet_generation_prompt")
        if not prompt:
            prompt = (
                self.prompt_manager.get_template("bullet_generation_prompt")
                if self.prompt_manager
                else "Generate bullets"
            )
        strategy_payload = state.get("strategy", {}).get("strategy_plan")
        if isinstance(strategy_payload, StrategyPlan):
            strategy = strategy_payload
        elif strategy_payload:
            strategy = StrategyPlan.model_validate(strategy_payload)
        else:
            strategy = StrategyPlan(
                strategy_name="bullet_generation",
                focus_areas=["impact"],
                key_achievements_to_highlight=[],
                tone="Confident",
            )

        experiences = list(state.get("resume", {}).get("experience_bullets", []))
        experience_slice = experiences[:3]

        return await self.generate_async(
            prompt,
            experience_slice,
            strategy,
            workflow_id or state.get("metadata", {}).get("workflow_id", ""),
        )

    async def critique_from_state_async(
        self, state: Dict[str, Any], workflow_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Extract bullets and critique prompt directly from shared state."""

        prompts_bucket = state.get("prompts", {})
        final_prompt = prompts_bucket.get("final_prompt")
        legacy_prompts = prompts_bucket.get("prompts", {}) if isinstance(prompts_bucket, dict) else {}
        critique_prompt = final_prompt or legacy_prompts.get("critique_prompt")
        if not critique_prompt:
            critique_prompt = (
                self.prompt_manager.get_template("critique_prompt")
                if self.prompt_manager
                else "Critique bullets"
            )
        bullets = state.get("bullets", {}).get("generated_bullets", [])
        return await self.critique_async(
            bullets,
            critique_prompt,
            workflow_id or state.get("metadata", {}).get("workflow_id", ""),
        )

    async def generate_async(
        self,
        prompt: str,
        experiences: List[Dict[str, Any]],
        strategy: StrategyPlan,
        workflow_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate bullets by delegating to the async generator helper."""

        task_context = {"prompts": [prompt], "experience": experiences}
        result = await self.generator.run_async(
            task_context,
            strategy if isinstance(strategy, StrategyPlan) else StrategyPlan.model_validate(strategy),
            workflow_id or "",
        )
        bullets = result.get("bullets", [])
        patch = {"bullets": {"generated_bullets": bullets}}
        safety_report = result.get("safety_report") or {}
        policy_decision = result.get("policy_decision") or {}
        constitutional_review = result.get("constitutional_review") or {}
        if not hasattr(safety_report, "dict"):
            safety_report = type("_Wrapper", (), {"dict": lambda self: dict(result.get("safety_report") or {})})()
        if not hasattr(policy_decision, "dict"):
            policy_decision = type("_Wrapper", (), {"dict": lambda self: dict(result.get("policy_decision") or {})})()
        if not hasattr(constitutional_review, "dict"):
            constitutional_review = type(
                "_Wrapper", (), {"dict": lambda self: dict(result.get("constitutional_review") or {})}
            )()
        patch["safety_report"] = safety_report.dict()
        patch["policy_decision"] = policy_decision.dict()
        patch["constitutional_review"] = constitutional_review.dict()
        return patch

    async def critique_async(
        self,
        bullets: List[Dict[str, Any]],
        critique_prompt: str,
        workflow_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Critique generated bullets using the critique helper."""

        critiqued = await self.critique_agent.run_async(
            bullets,
            critique_prompt,
            workflow_id or "",
        )
        patch = {"bullets": {"critiqued_bullets": critiqued}}
        safety_report = critiqued.get("safety_report") if isinstance(critiqued, dict) else {}
        policy_decision = critiqued.get("policy_decision") if isinstance(critiqued, dict) else {}
        constitutional_review = critiqued.get("constitutional_review") if isinstance(critiqued, dict) else {}
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

    async def run_async(
        self, state: Dict[str, Any], workflow_id: Optional[str] = None
    ) -> Dict[str, Any]:
        workflow_id = workflow_id or state.get("metadata", {}).get("workflow_id", "")
        plan = self._plan_from_state(state)
        experiences = self._extract_experiences(state)
        raw_bullets = self._generate_bullets(plan, experiences, workflow_id)
        resume_section = state.get("resume", {}).get("master_resume", {})
        enriched = await self.coordinator.run_async(raw_bullets, resume_section, workflow_id)

        patch = {
            "bullets": {
                "plan": plan.model_dump(),
                "generated_bullets": enriched,
                "instructions": self._plan_instructions(plan),
            }
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
