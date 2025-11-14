"""Prompt engineering stack."""

import json
from typing import Any, Dict, Optional, Tuple

from core_v10_7 import (
    BaseAgent,
    GeneratedPrompts,
    StrategyPlan,
    ValidationError,
    track_metrics,
    _format_prompt_with_defaults,
)


class PromptEngineerAgent(BaseAgent):
    """LLM-driven prompt engineering that adapts to task complexity."""

    @track_metrics("run_prompt_engineer")
    async def run_async(
        self,
        strategy: StrategyPlan,
        complexity: str,
        workflow_id: str,
    ) -> Dict[str, Any]:
        pcm = self.context.predictive_cache_manager
        if pcm and pcm.enabled():
            pcm.schedule({
                "coroutine": (
                    lambda s_json=strategy.model_dump_json(), c=complexity: self.context.precompute_engine.precompute_prompt_plan(
                        s_json,
                        c,
                    )
                )
            })
            await pcm.run_scheduled()
        base_result, validated_output = await self._generate_prompts(
            strategy,
            complexity,
            workflow_id,
        )
        return await self._maybe_self_correct(
            strategy,
            complexity,
            workflow_id,
            base_result,
            validated_output,
        )

    async def _generate_prompts(
        self,
        strategy: StrategyPlan,
        complexity: str,
        workflow_id: str,
        temperature_offset: float = 0.0,
        force_structured: bool = False,
    ) -> Tuple[Dict[str, Any], GeneratedPrompts]:
        self.log_info(f"Engineering prompts (Complexity: {complexity})...")

        client = self.get_model_client("prompt_engineer_model")
        meta_prompt_template = self.prompt_manager.get_template("prompt_engineer")

        style_guide = "Style: Generate clear, role-appropriate prompts."
        if force_structured:
            style_guide = (
                "Style: Enforce numbered prompts with explicit QA coverage and guardrails."
            )

        meta_prompt = await _format_prompt_with_defaults(
            meta_prompt_template,
            {
                "strategy": strategy.model_dump_json(),
                "complexity": complexity,
                "style_guide": style_guide,
                "job_description": "N/A",
            },
            self.budget_manager,
            client.goal_state,
            client.top_failures,
        )

        base_temp = self.config.model_config.prompt_engineer_model.temperature
        if self.context.policy_auto_tuner and self.context.policy_auto_tuner.enabled():
            base_temp = self.context.tuning_profile.temperature
        temperature = max(0.0, min(1.0, base_temp + temperature_offset))

        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": meta_prompt}],
            temperature=temperature,
            response_format="json_object",
        )

        validated_output, error = self.validator.validate(
            response["content"],
            GeneratedPrompts,
        )
        if error:
            self.log_error(
                f"PromptEngineerAgent failed validation: {error}. Returning baseline prompts."
            )
            raise ValidationError(error)

        self.log_feedback(
            workflow_id,
            "prompt_engineering",
            "success",
            {"prompt_count": len(validated_output.prompts)},
        )

        result = {
            "prompts": validated_output,
            "complexity": complexity,
        }
        return result, validated_output

    async def _maybe_self_correct(
        self,
        strategy: StrategyPlan,
        complexity: str,
        workflow_id: str,
        base_result: Dict[str, Any],
        validated_output: GeneratedPrompts,
    ) -> Dict[str, Any]:
        if not self.self_correction_manager:
            return base_result
        if not self.self_correction_manager.can_retry(workflow_id, "prompt"):
            return base_result

        issue = self._needs_retry(validated_output)
        if not issue:
            return base_result

        report = self.self_correction_manager.start_retry(
            workflow_id,
            "prompt",
            issue=issue,
            action="stabilize_prompt_structure",
        )

        corrected_result, corrected_output = await self._generate_prompts(
            strategy,
            complexity,
            workflow_id,
            temperature_offset=-0.2,
            force_structured=True,
        )
        resolved = not self._needs_retry(corrected_output)
        self.self_correction_manager.finalize_retry(report, resolved)
        if resolved:
            corrected_result.setdefault("self_correction", {})["prompt"] = report.model_dump()
            return corrected_result
        return base_result

    def _needs_retry(self, prompts: GeneratedPrompts) -> Optional[str]:
        if not prompts.qa_prompts or len(prompts.qa_prompts) < 1:
            return "missing_qa_prompts"
        if len(prompts.bullet_generation_prompt.strip()) < 40:
            return "short_bullet_prompt"
        return None
