"""
Planning Preflight Hook for Token Budget Estimation

Integrates the ContextWindowEstimator into the planning pipeline.
Every plan step must pass through this hook before calling Kimi 2.5.
"""

import json
import logging
from pathlib import Path
from typing import Any

from ..token_estimator import ContextWindowEstimator, TokenEstimate

logger = logging.getLogger(__name__)


class PlanningPreflightHook:
    """
    Preflight hook for planning steps that enforces token budget compliance.

    This hook must be called before every plan step executes to ensure
    the context window stays within safe limits.
    """

    def __init__(self, estimator: ContextWindowEstimator | None = None, budget_file: Path | None = None):
        self.estimator = estimator or ContextWindowEstimator()
        self.budget_file = budget_file or Path("docs/reports/plans/token_budget_log.json")
        self.budget_history = []
        self._load_budget_history()

    def _load_budget_history(self) -> None:
        """Load previous budget estimates from file"""
        if self.budget_file.exists():
            try:
                with open(self.budget_file) as f:
                    self.budget_history = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load budget history: {e}")
                self.budget_history = []

    def _save_budget_history(self) -> None:
        """Save budget estimates to file"""
        try:
            self.budget_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.budget_file, "w") as f:
                json.dump(self.budget_history, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save budget history: {e}")

    def preflight_check(
        self,
        plan_step: str,
        system_prompt: str,
        user_prompt: str,
        files: list[dict[str, Any]],
        diffs: list[dict[str, Any]],
        logs: list[dict[str, Any]],
        retrieved_context: list[dict[str, Any]],
        prior_steps: list[str],
        **kwargs,
    ) -> TokenEstimate:
        """
        Perform preflight token budget check for a plan step.

        Args:
            plan_step: Name/description of the plan step
            system_prompt: System and scaffold prompt content
            user_prompt: User/task prompt content
            files: List of file contents with metadata
            diffs: List of diff contents with metadata
            logs: List of log outputs with metadata
            retrieved_context: List of retrieved context chunks
            prior_steps: List of prior step contents to carry forward
            **kwargs: Additional parameters (reserved_output, safety_buffer)

        Returns:
            TokenEstimate with detailed breakdown

        Raises:
            TokenBudgetExceededError: If tokens exceed hard limit
        """
        logger.info(f"Preflight check for plan step: {plan_step}")

        # Estimate tokens
        estimate = self.estimator.estimate_step_tokens(
            plan_step=plan_step,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            files=files,
            diffs=diffs,
            logs=logs,
            retrieved_context=retrieved_context,
            prior_steps=prior_steps,
            **kwargs,
        )

        # Print report
        self.estimator.print_report(estimate)

        # Check hard limit
        if estimate.total_projected_tokens > self.estimator.budget.HARD_MAX_CONTEXT:
            raise TokenBudgetExceededError(
                f"Token budget exceeded for step '{plan_step}': "
                f"{estimate.total_projected_tokens:,} > {self.estimator.budget.HARD_MAX_CONTEXT:,}",
            )

        # Save to history
        self.budget_history.append(self.estimator.to_dict(estimate))
        self._save_budget_history()

        # Return estimate for caller to use
        return estimate

    def get_budget_summary(self) -> dict[str, Any]:
        """Get summary of budget usage across all steps"""
        if not self.budget_history:
            return {"total_steps": 0, "message": "No budget history available"}

        total_steps = len(self.budget_history)
        total_tokens = sum(step["total_projected_tokens"] for step in self.budget_history)
        avg_tokens = total_tokens / total_steps

        status_counts = {}
        for step in self.budget_history:
            status = step["status"]
            status_counts[status] = status_counts.get(status, 0) + 1

        return {
            "total_steps": total_steps,
            "total_tokens": total_tokens,
            "average_tokens_per_step": avg_tokens,
            "status_distribution": status_counts,
            "max_tokens": max(step["total_projected_tokens"] for step in self.budget_history),
            "min_tokens": min(step["total_projected_tokens"] for step in self.budget_history),
        }

    def clear_history(self) -> None:
        """Clear budget history"""
        self.budget_history = []
        self._save_budget_history()


class TokenBudgetExceededError(Exception):
    """Raised when token budget exceeds hard limit"""

    pass


# Decorator for automatic preflight checking
def require_token_budget(preflight_hook: PlanningPreflightHook):
    """
    Decorator that automatically applies token budget preflight check

    Usage:
        @require_token_budget(preflight_hook)
        def execute_plan_step(step_name, system_prompt, user_prompt, files, ...):
            # Step implementation
            pass
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            # Extract relevant parameters for token estimation
            plan_step = kwargs.get("plan_step", func.__name__)
            system_prompt = kwargs.get("system_prompt", "")
            user_prompt = kwargs.get("user_prompt", "")
            files = kwargs.get("files", [])
            diffs = kwargs.get("diffs", [])
            logs = kwargs.get("logs", [])
            retrieved_context = kwargs.get("retrieved_context", [])
            prior_steps = kwargs.get("prior_steps", [])

            # Perform preflight check
            estimate = preflight_hook.preflight_check(
                plan_step=plan_step,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                files=files,
                diffs=diffs,
                logs=logs,
                retrieved_context=retrieved_context,
                prior_steps=prior_steps,
            )

            # If action is 'block', raise error
            if estimate.action == "block":
                raise TokenBudgetExceededError(
                    f"Plan step '{plan_step}' blocked due to token budget: "
                    f"{estimate.total_projected_tokens:,} tokens",
                )

            # If compression was applied, update kwargs with compressed content
            if estimate.compression_applied:
                logger.info(f"Compression applied: {estimate.compression_applied}")
                # Note: In a real implementation, you'd need to update the actual
                # content in kwargs based on the compression applied

            # Execute the function
            return func(*args, **kwargs)

        return wrapper

    return decorator
