"""Prompt engineering stack."""

from typing import Any

from core_v10_7 import (
    BaseAgent,
    GeneratedPrompts,
    StrategyPlan,
    ValidationError,
    _format_prompt_with_defaults,
    track_metrics,
)


class PromptEngineerAgent(BaseAgent):
    """LLM-driven prompt engineering that adapts to task complexity."""

    @track_metrics("run_prompt_engineer")
    async def run_async(
        self,
        strategy: StrategyPlan,
        complexity: str,
        workflow_id: str,
    ) -> dict[str, Any]:
        self.log_info(f"Engineering prompts (Complexity: {complexity})...")

        client = self.get_model_client("prompt_engineer_model")
        meta_prompt_template = self.prompt_manager.get_template("prompt_engineer")

        meta_prompt = await _format_prompt_with_defaults(
            meta_prompt_template,
            {
                "strategy": strategy.model_dump_json(),
                "complexity": complexity,
                "style_guide": "Style: Generate clear, role-appropriate prompts.",
                "job_description": "N/A",
            },
            self.budget_manager,
            client.goal_state,
            client.top_failures,
        )

        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": meta_prompt}],
            temperature=self.config.model_config.prompt_engineer_model.temperature,
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

        return {
            "prompts": validated_output,
            "complexity": complexity,
        }
