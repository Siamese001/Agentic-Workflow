from __future__ import annotations

"""
Budget Auditor - Token usage tracking and cost enforcement.
Extracted from BudgetManagerAgent.py for single responsibility.
"""


class BudgetAuditor:
    """Tracks estimated token usage and enforces budget limits."""

    def __init__(self, limit_usd: float = 2.0):
        """Initialize budget auditor with spending limit.

        Args:
            limit_usd: Maximum allowed spending in USD
        """
        self.limit = limit_usd
        self.spent = 0.0
        self.input_tokens = 0
        self.output_tokens = 0

    def track(self, prompt: str, response: str) -> None:
        """Track token usage from a prompt/response pair.

        Args:
            prompt: Input prompt text
            response: LLM response text
        """
        # Rough estimation: 4 chars per token
        in_tokens = len(prompt) / 4
        out_tokens = len(response) / 4

        self.input_tokens += in_tokens
        self.output_tokens += out_tokens

        # Cost calculation: $0.50 per 1M input tokens, $1.50 per 1M output tokens
        cost = (in_tokens / 1_000_000 * 0.5) + (out_tokens / 1_000_000 * 1.5)
        self.spent += cost

    def check_budget(self) -> bool:
        """Check if budget is exceeded.

        Returns:
            True if within budget, False if exceeded
        """
        if self.spent > self.limit:
            print(f"💸 BUDGET EXCEEDED (${self.spent:.4f} / ${self.limit}). Halting Intelligence.")
            return False
        return True

    def get_status(self) -> str:
        """Get current budget status string.

        Returns:
            Formatted status string with spending and token counts
        """
        return f"${self.spent:.4f} / ${self.limit} ({self.input_tokens:.0f} in, {self.output_tokens:.0f} out)"

    def get_metrics(self) -> dict[str, float]:
        """Get detailed budget metrics.

        Returns:
            Dictionary with spending, tokens, and utilization metrics
        """
        utilization = (self.spent / self.limit * 100) if self.limit > 0 else 0
        return {
            "spent_usd": self.spent,
            "limit_usd": self.limit,
            "utilization_pct": utilization,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.input_tokens + self.output_tokens,
        }

    def reset(self) -> None:
        """Reset all counters to zero."""
        self.spent = 0.0
        self.input_tokens = 0
        self.output_tokens = 0
