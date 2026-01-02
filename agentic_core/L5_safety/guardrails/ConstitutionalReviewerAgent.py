from __future__ import annotations
"""Constitutional Reviewer Agent - Performs final constitutional review of the output."""

import json
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin

class BaseAgent(HealerMixin):
    """Stub for BaseAgent - TODO: Replace with sovereign equivalent"""
    def __init__(self, context, debug_mode=False):
        self.context = context
        self.debug_mode = debug_mode
    
    def log_info(self, msg):
        pass
    
    def log_warning(self, msg):
        pass
    
    def log_error(self, msg):
        pass

class ConstitutionalReviewResult:
    """Stub for ConstitutionalReviewResult - TODO: Replace with sovereign equivalent"""
    def __init__(self, review_passed=True, violations_found=None, feedback=""):
        self.review_passed = review_passed
        self.violations_found = violations_found or []
        self.feedback = feedback

def track_metrics(name):
    """Stub decorator for track_metrics - TODO: Replace with sovereign equivalent"""
    def decorator(func):
        return func
    return decorator

async def _format_prompt_with_defaults(template, data, budget_manager, goal_state, top_failures):
    """Stub for _format_prompt_with_defaults"""
    return template


class ConstitutionalReviewerAgent(HealerMixin, BaseAgent):
    """Performs final constitutional review of the output."""

    @track_metrics("run_constitutional_review")
    async def run_async(
        self,
        final_draft: str,
        workflow_id: str,
    ) -> ConstitutionalReviewResult:
        """Run async constitutional review of the final draft."""
        self.log_info("Running final constitutional review...")

        if not self.config.agent_stacks.enable_constitutional_review:
            self.log_warning("Constitutional review is disabled. Passing by default.")
            return ConstitutionalReviewResult(
                review_passed=True,
                violations_found=[],
                feedback="Review disabled",
            )

        client = self.get_model_client("constitutional_review_model")
        prompt_template = self.prompt_manager.get_template("constitutional_review")

        rules = self.context.rules_loader.get_constitution_rules()
        constitution_text = json.dumps(rules)

        prompt = await _format_prompt_with_defaults(
            prompt_template,
            {"final_draft": final_draft, "constitution": constitution_text},
            self.BudgetManager,
            client.goal_state,
            client.top_failures,
        )

        response = await client.chat_completion_async(
            messages=[{"role": "user", "content": prompt}],
            temperature=self.config.ModelConfig.constitutional_review_model.temperature,
            response_format="json_object",
        )

        validated_output, error = self.validator.validate(
            response["content"],
            ConstitutionalReviewResult,
        )
        if error:
            self.log_error(
                f"ConstitutionalReviewer failed validation: {error}. Failing open (passing draft)."
            )
            return ConstitutionalReviewResult(
                review_passed=True,
                violations_found=["VALIDATION_ERROR"],
                feedback=error,
            )

        if not validated_output.review_passed:
            self.log_warning(
                f"CONSTITUTIONAL REVIEW FAILED: {validated_output.violations_found}"
            )

        return validated_output
