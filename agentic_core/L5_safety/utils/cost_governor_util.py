"""Cost Governor Utility - Deterministic LLM cost tracking.

This module provides deterministic cost tracking functionality previously
implemented in CostGovernorAgent. Converted from agent to utility script
as part of Phase 2 optimization (Wave 7 Micro-Wave 3).

Usage:
    from agentic_core.L5_safety.utils.cost_governor_util import (
        CostGovernor, BudgetExceededError, track_cost
    )

    # Track costs
    governor = CostGovernor(budget_limit=10.0)
    cost = governor.track("gpt-4", input_tokens=1000, output_tokens=500)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

Logger = logging.getLogger(__name__)

# Default cost rate: $0.00002 per token (approximate blended rate)
DEFAULT_COST_PER_TOKEN = 2e-05


class BudgetExceededError(Exception):
    """Raised when LLM spending exceeds the configured budget limit."""

    pass


@dataclass
class ModelPricing:
    """Pricing information for a specific model."""

    model_name: str
    input_cost_per_token: float
    output_cost_per_token: float


# Model pricing registry (can be extended)
MODEL_PRICING: dict[str, ModelPricing] = {
    "gpt-4": ModelPricing("gpt-4", 3e-05, 6e-05),
    "gpt-4-turbo": ModelPricing("gpt-4-turbo", 1e-05, 3e-05),
    "gpt-3.5-turbo": ModelPricing("gpt-3.5-turbo", 5e-06, 1.5e-05),
    "claude-3-opus": ModelPricing("claude-3-opus", 1.5e-05, 7.5e-05),
    "claude-3-sonnet": ModelPricing("claude-3-sonnet", 3e-06, 1.5e-05),
    "default": ModelPricing("default", DEFAULT_COST_PER_TOKEN, DEFAULT_COST_PER_TOKEN),
}


@dataclass
class CostGovernor:
    """Deterministic cost tracking without agent overhead."""

    budget_limit: float = 10.0
    current_spend: float = 0.0
    _history: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self):
        """Initialize after dataclass creation."""
        if self.budget_limit <= 0:
            raise ValueError("budget_limit must be positive")

    def track(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        metadata: dict[str, Any] | None = None,
    ) -> float:
        """Calculate and record the cost of an LLM call.

        Args:
            model: Name of the LLM model used
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            metadata: Optional metadata about the call

        Returns:
            Cost of this call in dollars

        Raises:
            BudgetExceededError: If total spend exceeds budget
        """
        # Get pricing for model
        pricing = MODEL_PRICING.get(model, MODEL_PRICING["default"])

        # Calculate cost
        input_cost = input_tokens * pricing.input_cost_per_token
        output_cost = output_tokens * pricing.output_cost_per_token
        total_cost = input_cost + output_cost

        # Update spend
        self.current_spend += total_cost

        # Record in history
        self._history.append(
            {
                "model": model,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost": total_cost,
                "metadata": metadata or {},
            }
        )

        # Trim history if needed
        if len(self._history) > 1000:
            self._history = self._history[-1000:]

        Logger.info(
            f"CostGovernor: ${self.current_spend:.4f} / ${self.budget_limit:.2f} "
            f"({model}: ${total_cost:.4f})",
        )

        # Check budget
        if self.current_spend > self.budget_limit:
            raise BudgetExceededError(
                f"BUDGET EXCEEDED: ${self.current_spend:.2f} exceeds limit of ${self.budget_limit:.2f}",
            )

        return total_cost

    def get_spend_summary(self) -> dict[str, Any]:
        """Get current spending summary.

        Returns:
            Dictionary with spending information
        """
        if not self._history:
            return {
                "current_spend": self.current_spend,
                "budget_limit": self.budget_limit,
                "remaining": self.budget_limit - self.current_spend,
                "percent_used": (self.current_spend / self.budget_limit * 100) if self.budget_limit else 0,
                "call_count": 0,
                "by_model": {},
            }

        # Group by model
        by_model: dict[str, dict[str, Any]] = {}
        for entry in self._history:
            model = entry["model"]
            if model not in by_model:
                by_model[model] = {"calls": 0, "cost": 0.0, "tokens": 0}
            by_model[model]["calls"] += 1
            by_model[model]["cost"] += entry["cost"]
            by_model[model]["tokens"] += entry["input_tokens"] + entry["output_tokens"]

        return {
            "current_spend": self.current_spend,
            "budget_limit": self.budget_limit,
            "remaining": self.budget_limit - self.current_spend,
            "percent_used": (self.current_spend / self.budget_limit * 100) if self.budget_limit else 0,
            "call_count": len(self._history),
            "by_model": by_model,
        }

    def reset(self) -> None:
        """Reset spend tracking (use with caution)."""
        self.current_spend = 0.0
        self._history = []
        Logger.warning("Cost tracking reset")


def track_cost(
    model: str,
    input_tokens: int,
    output_tokens: int,
    budget_limit: float = 10.0,
    current_spend: float = 0.0,
) -> tuple[float, float]:
    """Standalone function to track a single cost.

    Args:
        model: Model name
        input_tokens: Input token count
        output_tokens: Output token count
        budget_limit: Budget limit
        current_spend: Current accumulated spend

    Returns:
        Tuple of (new_total_spend, this_call_cost)

    Raises:
        BudgetExceededError: If budget exceeded
    """
    governor = CostGovernor(budget_limit=budget_limit)
    governor.current_spend = current_spend

    cost = governor.track(model, input_tokens, output_tokens)
    return governor.current_spend, cost


def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Calculate cost without tracking.

    Args:
        model: Model name
        input_tokens: Input token count
        output_tokens: Output token count

    Returns:
        Estimated cost in dollars
    """
    pricing = MODEL_PRICING.get(model, MODEL_PRICING["default"])
    return input_tokens * pricing.input_cost_per_token + output_tokens * pricing.output_cost_per_token


def register_model_pricing(
    model_name: str,
    input_cost_per_token: float,
    output_cost_per_token: float,
) -> None:
    """Register pricing for a new model.

    Args:
        model_name: Model identifier
        input_cost_per_token: Cost per input token
        output_cost_per_token: Cost per output token
    """
    MODEL_PRICING[model_name] = ModelPricing(
        model_name=model_name,
        input_cost_per_token=input_cost_per_token,
        output_cost_per_token=output_cost_per_token,
    )


def heal_repository(**kwargs: Any) -> dict[str, Any]:
    """Autonomous healing interface (Canon Key 51 compliance)."""
    Logger.info("[CostGovernor] Budget violations are runtime-managed, not code-healable")
    return {
        "violations_found": 0,
        "violations_fixed": 0,
        "errors": 0,
        "skipped": 1,
        "reason": "Budget violations are runtime-managed, not code-healable",
    }


def heal(violation: dict[str, Any]) -> dict[str, Any]:
    """Heal cost governance violations.

    Args:
        violation: Violation dict with keys:
            - type: budget_exceeded, invalid_pricing, etc.
            - details: Additional details

    Returns:
        Healing result dict
    """
    violation_type = violation.get("type", "unknown")

    if violation_type == "budget_exceeded":
        Logger.warning("[CostGovernor] Cannot heal budget exceeded - runtime issue")
        return {
            "status": "skipped",
            "details": "Budget exceeded is runtime-managed",
            "artifacts": [],
            "errors": [],
        }

    elif violation_type == "invalid_pricing":
        model = violation.get("model", "unknown")
        # Reset to default pricing
        if model in MODEL_PRICING:
            del MODEL_PRICING[model]
        return {
            "status": "success",
            "details": f"Reset pricing for {model} to default",
            "artifacts": [f"pricing:{model}"],
            "errors": [],
        }

    return {
        "status": "skipped",
        "details": f"Unknown violation: {violation_type}",
        "artifacts": [],
        "errors": [],
    }


def main():
    """Main entry point for Cost Governor Utility."""
    import argparse

    parser = argparse.ArgumentParser(description="Cost Governor Utility")
    parser.add_argument("--model", type=str, required=True)
    parser.add_argument("--input-tokens", type=int, default=1000)
    parser.add_argument("--output-tokens", type=int, default=500)
    parser.add_argument("--budget", type=float, default=10.0)
    parser.add_argument("--verbose", "-v", action="store_true")

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    governor = CostGovernor(budget_limit=args.budget)

    try:
        cost = governor.track(args.model, args.input_tokens, args.output_tokens)
        print(f"Model: {args.model}")
        print(f"Input tokens: {args.input_tokens}")
        print(f"Output tokens: {args.output_tokens}")
        print(f"Cost: ${cost:.4f}")
        print(f"Total spend: ${governor.current_spend:.4f} / ${governor.budget_limit:.2f}")
    except BudgetExceededError as e:
        print(f"ERROR: {e}")


if __name__ == "__main__":
    main()
