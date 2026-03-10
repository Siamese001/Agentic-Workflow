"""Token Budget Enforcement for cost control.

Phase 1 - Pillar 11: Cost & Optimization (Semantic Caching)
Converts token budget inspector into active enforcement mechanism.
"""

import logging
from dataclasses import dataclass
from typing import Any

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

logger = logging.getLogger(__name__)


class BudgetExceededError(Exception):
    """Raised when token budget is exceeded."""

    def __init__(
        self,
        message: str,
        current_tokens: int,
        max_tokens: int,
        budget_type: str = "total",
    ):
        super().__init__(message)
        self.current_tokens = current_tokens
        self.max_tokens = max_tokens
        self.budget_type = budget_type


@dataclass
class TokenBudgetConfig:
    """Token budget configuration."""

    max_prompt_tokens: int = 100000
    max_completion_tokens: int = 50000
    max_total_tokens: int = 150000
    max_tokens_per_request: int = 8000
    enforce_limits: bool = True
    warn_threshold: float = 0.8


class TokenBudget:
    """Token budget tracker and enforcer.

    Tracks token usage across requests and enforces limits
    to prevent cost overruns.
    """

    def __init__(
        self,
        config: TokenBudgetConfig | None = None,
        enable_logging: bool = True,
    ):
        """Initialize token budget.

        Args:
            config: Budget configuration
            enable_logging: Enable logging of budget events
        """
        self.config = config or TokenBudgetConfig()
        self.enable_logging = enable_logging

        self._prompt_tokens = 0
        self._completion_tokens = 0
        self._total_tokens = 0
        self._request_count = 0

    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text.

        Uses simple heuristic: ~4 characters per token.
        For production, use tiktoken or similar.

        Args:
            text: Text to estimate

        Returns:
            Estimated token count
        """
        return len(text) // 4

    def check_request_budget(
        self,
        prompt: str,
        max_completion_tokens: int,
    ) -> None:
        """Check if a request fits within budget.

        Args:
            prompt: The prompt text
            max_completion_tokens: Max tokens for completion

        Raises:
            BudgetExceededError: If budget would be exceeded
        """
        prompt_tokens = self.estimate_tokens(prompt)

        if prompt_tokens > self.config.max_tokens_per_request:
            raise BudgetExceededError(
                f"Prompt exceeds per-request limit: {prompt_tokens} > {self.config.max_tokens_per_request}",
                current_tokens=prompt_tokens,
                max_tokens=self.config.max_tokens_per_request,
                budget_type="per_request",
            )

        projected_total = self._total_tokens + prompt_tokens + max_completion_tokens

        if self.config.enforce_limits and projected_total > self.config.max_total_tokens:
            raise BudgetExceededError(
                f"Request would exceed total budget: {projected_total} > {self.config.max_total_tokens}",
                current_tokens=projected_total,
                max_tokens=self.config.max_total_tokens,
                budget_type="total",
            )

        warn_threshold = self.config.max_total_tokens * self.config.warn_threshold
        if self.enable_logging and projected_total > warn_threshold:
            logger.warning(
                "token_budget_warning",
                extra={
                    "projected_total": projected_total,
                    "max_total": self.config.max_total_tokens,
                    "utilization": projected_total / self.config.max_total_tokens,
                },
            )

    def record_usage(
        self,
        prompt_tokens: int,
        completion_tokens: int,
    ) -> None:
        """Record token usage for a request.

        Args:
            prompt_tokens: Tokens used in prompt
            completion_tokens: Tokens used in completion
        """
        self._prompt_tokens += prompt_tokens
        self._completion_tokens += completion_tokens
        self._total_tokens += prompt_tokens + completion_tokens
        self._request_count += 1

        if self.enable_logging:
            logger.info(
                "token_usage_recorded",
                extra={
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": self._total_tokens,
                    "request_count": self._request_count,
                },
            )

        if self.config.enforce_limits:
            if self._prompt_tokens > self.config.max_prompt_tokens:
                raise BudgetExceededError(
                    f"Prompt token budget exceeded: {self._prompt_tokens} > {self.config.max_prompt_tokens}",
                    current_tokens=self._prompt_tokens,
                    max_tokens=self.config.max_prompt_tokens,
                    budget_type="prompt",
                )

            if self._completion_tokens > self.config.max_completion_tokens:
                raise BudgetExceededError(
                    f"Completion token budget exceeded: "
                    f"{self._completion_tokens} > {self.config.max_completion_tokens}",
                    current_tokens=self._completion_tokens,
                    max_tokens=self.config.max_completion_tokens,
                    budget_type="completion",
                )

            if self._total_tokens > self.config.max_total_tokens:
                raise BudgetExceededError(
                    f"Total token budget exceeded: {self._total_tokens} > {self.config.max_total_tokens}",
                    current_tokens=self._total_tokens,
                    max_tokens=self.config.max_total_tokens,
                    budget_type="total",
                )

    def get_stats(self) -> dict[str, Any]:
        """Get budget statistics.

        Returns:
            Dict with budget stats
        """
        return {
            "prompt_tokens": self._prompt_tokens,
            "completion_tokens": self._completion_tokens,
            "total_tokens": self._total_tokens,
            "request_count": self._request_count,
            "max_prompt_tokens": self.config.max_prompt_tokens,
            "max_completion_tokens": self.config.max_completion_tokens,
            "max_total_tokens": self.config.max_total_tokens,
            "prompt_utilization": self._prompt_tokens / max(1, self.config.max_prompt_tokens),
            "completion_utilization": self._completion_tokens / max(1, self.config.max_completion_tokens),
            "total_utilization": self._total_tokens / max(1, self.config.max_total_tokens),
        }

    def reset(self) -> None:
        """Reset budget counters."""
        self._prompt_tokens = 0
        self._completion_tokens = 0
        self._total_tokens = 0
        self._request_count = 0

        if self.enable_logging:
            logger.info("token_budget_reset")

    def get_remaining(self) -> dict[str, int]:
        """Get remaining token budget.

        Returns:
            Dict with remaining tokens for each category
        """
        return {
            "prompt": max(0, self.config.max_prompt_tokens - self._prompt_tokens),
            "completion": max(0, self.config.max_completion_tokens - self._completion_tokens),
            "total": max(0, self.config.max_total_tokens - self._total_tokens),
        }


def enforce_token_budget(
    prompt: str,
    max_completion_tokens: int,
    budget: TokenBudget,
) -> None:
    """Convenience function to enforce token budget.

    Args:
        prompt: The prompt text
        max_completion_tokens: Max completion tokens
        budget: TokenBudget instance

    Raises:
        BudgetExceededError: If budget exceeded
    """
    budget.check_request_budget(prompt, max_completion_tokens)
