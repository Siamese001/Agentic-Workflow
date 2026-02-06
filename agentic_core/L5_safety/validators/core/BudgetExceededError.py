from __future__ import annotations

"""Cost Governor for tracking and limiting mission costs.

Tracks token usage and halts execution if cost exceeds threshold.
"""
import logging
import os
import time
from typing import Any

Logger: Any = logging.getLogger(__name__)


class BudgetExceededError(Exception):
    """Raised when the cost budget is exceeded."""

    def __init__(self, message: str, current_spend: float = None, limit: float = None):
        super().__init__(message)
        self.current_spend = current_spend
        self.limit = limit


class MemoryPressureError(Exception):
    """Raised when system memory is too low."""

    def __init__(self, message: str, available_gb: float = None, threshold_gb: float = None):
        super().__init__(message)
        self.available_gb = available_gb
        self.threshold_gb = threshold_gb


class CostGovernor:
    """Governor that tracks costs and enforces budget limits."""

    def __init__(self, limit_usd: float = 5.0, min_memory_gb: float = 2.0):
        """Initialize the cost governor.

        Args:
            limit_usd: Maximum allowed cost in USD
            min_memory_gb: Minimum required available memory in GB
        """
        self.limit = limit_usd
        self.spend = 0.0
        self.start_time = time.time()
        self.action_count = 0
        self.min_memory_gb = min_memory_gb
        self.rates = {
            "gpt-4": 0.03,
            "gpt-4-turbo": 0.01,
            "gpt-3.5-turbo": 0.002,
            "claude-3-opus": 0.015,
            "claude-3-sonnet": 0.003,
            "claude-3-haiku": 0.00025,
            os.getenv("GEMINI_MODEL", "gemini-3-flash-preview"): 0.0005,
        }
        self.usage_by_model: dict[str, dict[str, int]] = {}
        LOGGER.info(f"CostGovernor initialized with budget limit: ${limit_usd:.2f}")
        LOGGER.info(f"Memory pressure check enabled - minimum: {min_memory_gb}GB")

    def check_memory_pressure(self) -> dict[str, float]:
        """Check system memory pressure.

        Returns:
            Dictionary with memory information

        Raises:
            MemoryPressureError: If available memory is below threshold
        """
        try:
            import psutil

            memory: Any = psutil.virtual_memory()
            available_gb: Any = memory.available / 1024**3
            total_gb: Any = memory.total / 1024**3
            used_percent: Any = memory.percent
            if available_gb < self.min_memory_gb:
                LOGGER.error(f"Low memory: {available_gb:.2f}GB available, {self.min_memory_gb}GB required")
                raise MemoryPressureError(
                    f"Insufficient memory: {available_gb:.2f}GB available, {self.min_memory_gb}GB required",
                    available_gb=available_gb,
                    threshold_gb=self.min_memory_gb,
                )
            if used_percent > 90:
                LOGGER.warning(f"High memory usage: {used_percent:.1f}%")
            return {
                "available_gb": available_gb,
                "total_gb": total_gb,
                "used_percent": used_percent,
                "pressure_ok": available_gb >= self.min_memory_gb,
            }
        except ImportError:
            try:
                with open("/proc/meminfo") as f:
                    meminfo: Any = f.read()
                for line in meminfo.split("\n"):
                    if "MemAvailable:" in line:
                        available_kb: Any = int(line.split()[1])
                        available_gb: Any = available_kb / 1024**2
                    elif "MemTotal:" in line:
                        total_kb: Any = int(line.split()[1])
                        total_gb: Any = total_kb / 1024**2
                if available_gb < self.min_memory_gb:
                    LOGGER.error(
                        f"Low memory: {available_gb:.2f}GB available, {self.min_memory_gb}GB required"
                    )
                    raise MemoryPressureError(
                        f"Insufficient memory: {available_gb:.2f}GB available, {self.min_memory_gb}GB required",
                        available_gb=available_gb,
                        threshold_gb=self.min_memory_gb,
                    )
                used_percent: Any = (total_gb - available_gb) / total_gb * 100
                return {
                    "available_gb": available_gb,
                    "total_gb": total_gb,
                    "used_percent": used_percent,
                    "pressure_ok": available_gb >= self.min_memory_gb,
                }
            except (FileNotFoundError, Exception):
                LOGGER.warning("Memory check not available on this platform")
                return {"available_gb": -1, "total_gb": -1, "used_percent": -1, "pressure_ok": True}

    def track(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Track token usage and check budget.

        Args:
            model: Model name used
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Cost of this interaction

        Raises:
            BudgetExceededError: If budget limit is exceeded
        """
        rate: Any = self.rates.get(model, 0.01)
        cost: Any = (input_tokens + output_tokens) / 1000 * rate
        self.spend += cost
        self.action_count += 1
        if model not in self.usage_by_model:
            self.usage_by_model[model] = {"input_tokens": 0, "output_tokens": 0, "cost": 0.0}
        self.usage_by_model[model]["input_tokens"] += input_tokens
        self.usage_by_model[model]["output_tokens"] += output_tokens
        self.usage_by_model[model]["cost"] += cost
        if self.spend > self.limit:
            LOGGER.warning(f"Budget exceeded! Current: ${self.spend:.2f}, Limit: ${self.limit:.2f}")
            raise BudgetExceededError(
                f"Budget limit ${self.limit:.2f} exceeded (Current: ${self.spend:.2f})",
                current_spend=self.spend,
                limit=self.limit,
            )
        if self.spend > self.limit * 0.8:
            LOGGER.warning(f"Approaching budget limit: ${self.spend:.2f} / ${self.limit:.2f}")
        LOGGER.debug(f"Tracked cost: ${cost:.4f} for {model} (Total: ${self.spend:.2f})")
        return cost

    def check_action_cost(self, estimated_tokens: int, model: str = "gpt-3.5-turbo") -> bool:
        """Check if an estimated action would exceed budget.

        Args:
            estimated_tokens: Estimated tokens for the action
            model: Model to be used

        Returns:
            True if action is within budget, False otherwise
        """
        rate: Any = self.rates.get(model, 0.01)
        estimated_cost: Any = estimated_tokens / 1000 * rate
        if self.spend + estimated_cost > self.limit:
            LOGGER.warning(f"Action would exceed budget: +${estimated_cost:.4f}")
            return False
        return True

    def get_stats(self) -> dict:
        """Get cost and usage statistics.

        Returns:
            Dictionary with cost statistics
        """
        runtime: Any = time.time() - self.start_time
        return {
            "total_spend": self.spend,
            "budget_limit": self.limit,
            "budget_remaining": self.limit - self.spend,
            "budget_used_percent": self.spend / self.limit * 100,
            "total_actions": self.action_count,
            "runtime_seconds": runtime,
            "usage_by_model": self.usage_by_model,
            "average_cost_per_action": self.spend / max(self.action_count, 1),
        }

    def reset(self) -> Any:
        """Reset the governor state."""
        self.spend = 0.0
        self.start_time = time.time()
        self.action_count = 0
        self.usage_by_model = {}
        LOGGER.info("CostGovernor reset")

    def set_limit(self, new_limit: float) -> Any:
        """Update the budget limit.

        Args:
            new_limit: New budget limit in USD
        """
        old_limit: Any = self.limit
        self.limit = new_limit
        LOGGER.info(f"Budget limit updated: ${old_limit:.2f} -> ${new_limit:.2f}")


def create_cost_governor(limit_usd: float = 5.0) -> CostGovernor:
    """Factory function to create cost governor instance.

    Args:
        limit_usd: Budget limit in USD

    Returns:
        CostGovernor instance
    """
    return CostGovernor(limit_usd)
