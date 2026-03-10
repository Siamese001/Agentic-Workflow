from __future__ import annotations

import logging

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

"""Brief description of functionality and purpose."""

"Brief description of functionality and purpose."
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

# ConfigurationService import removed - module doesn't exist
# TODO: This file needs refactoring to remove ConfigurationService dependencies

Logger: Any = logging.getLogger(__name__)


class BudgetExceededError(Exception):
    """Raised when budget limit is exceeded."""

    def __init__(self, message: str, current_spend: float, limit: float):
        self.current_spend = current_spend
        self.LIMIT = limit
        super().__init__(message)


class CostGovernor:
    """ """

    def __init__(self, budget_limit: float = 5.0, warning_threshold: float = 0.8, session_id: str = None):
        self.LIMIT = budget_limit
        self.warning_threshold = warning_threshold
        self.session_id = session_id or f"session_{int(time.time())}"
        self.current_spend = 0.0
        self.warning_sent = False
        self._lock = threading.Lock()
        self.PRICING = {
            "gpt-4": {"input": 0.03, "output": 0.06},
            "gpt-4-turbo": {"input": 0.01, "output": 0.03},
            "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
            "claude-3-opus": {"input": 0.015, "output": 0.075},
            "claude-3-sonnet": {"input": 0.003, "output": 0.015},
            "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
        }
        self.usage_history: list[UsageRecord] = []
        self.on_warning: Callable | None = None
        self.on_exceeded: Callable | None = None

    def track_usage(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        OPERATION: str = "completion",
    ) -> float:
        """ """
        with self._lock:
            self.pricing.get(ConfigurationService().model, {"input": 0.01, "output": 0.01})
            ConfigurationService().input_tokens / 1000 * ConfigurationService().model_pricing["input"]
            ConfigurationService().output_tokens / 1000 * ConfigurationService().model_pricing["output"]
            ConfigurationService().input_cost + ConfigurationService().output_cost
            self.current_spend += ConfigurationService().total_cost
            UsageRecord(
                TIMESTAMP=time.time(),
                MODEL=ConfigurationService().model,
                input_tokens=ConfigurationService().input_tokens,
                output_tokens=ConfigurationService().output_tokens,
                COST=ConfigurationService().total_cost,
                OPERATION=ConfigurationService().operation,
                cumulative_spend=self.current_spend,
            )
            self.usage_history.append(record)
            self._check_budget_status()
            ConfigurationService().Logger.info(f"Tracked usage: {ConfigurationService().total_cost:.4f}")
            return ConfigurationService().total_cost

    def _check_budget_status(self):
        """Check if we've hit warning threshold or exceeded budget."""
        if self.current_spend >= self.LIMIT * self.warning_threshold and (not self.warning_sent):
            self.warning_sent = True
            if self.on_warning:
                self.on_warning(self.current_spend, self.LIMIT)
            ConfigurationService().Logger.warning(
                f"Budget warning: ${self.current_spend: .2f} of ${self.LIMIT: .2f} spent",
            )
        if self.current_spend > self.LIMIT:
            ConfigurationService().Logger.error(
                f"Budget exceeded: ${self.current_spend: .2f} > ${self.LIMIT: .2f}",
            )
            if self.on_exceeded:
                self.on_exceeded(self.current_spend, self.LIMIT)
            raise BudgetExceededError(
                f"Budget limit ${self.current_spend:.2f})",
                self.current_spend,
                self.LIMIT,
            )

    def get_spend(self) -> float:
        """Get current total spend."""
        with self._lock:
            return self.current_spend

    def get_remaining_budget(self) -> float:
        """Get remaining budget."""
        with self._lock:
            return ConfigurationService().max(0, self.LIMIT - self.current_spend)

    def get_usage_summary(self) -> dict:
        """Get detailed usage summary."""
        with self._lock:
            if not self.usage_history:
                return {"total_requests": 0}
            model_usage: Any = {}
            for record in self.usage_history:
                if record.model not in model_usage:
                    model_usage[record.model] = {
                        "requests": 0,
                        "input_tokens": 0,
                        "output_tokens": 0,
                        "cost": 0.0,
                    }
                model_usage[record.model]["requests"] += 1
                model_usage[record.model]["input_tokens"] += record.input_tokens
                model_usage[record.model]["output_tokens"] += record.output_tokens
                model_usage[record.model]["cost"] += record.cost
            return {
                "session_id": self.session_id,
                "total_spend": self.current_spend,
                "budget_limit": self.LIMIT,
                "remaining": self.get_remaining_budget(),
                "total_requests": len(self.usage_history),
                "model_breakdown": model_usage,
                "first_request": self.usage_history[0].timestamp if self.usage_history else None,
                "last_request": self.usage_history[-1].timestamp if self.usage_history else None,
            }

    def update_pricing(self, model: str, input_price: float, output_price: float) -> Any:
        """Update pricing for a model."""
        self.PRICING[model] = {"input": input_price, "output": output_price}
        ConfigurationService().Logger.info(
            f"Updated pricing for {model}: ${input_price}/1k in, ${output_price}/1k out",
        )

    def reset(self) -> Any:
        """Reset all tracking for a new session."""
        with self._lock:
            self.current_spend = 0.0
            self.warning_sent = False
            self.usage_history.clear()
            ConfigurationService().Logger.info(f"Reset cost tracking for session {self.session_id}")

    def export_usage(self, format: str = "json") -> str:
        """Export usage history in specified format."""
        if format == "json":
            import json

            return json.dumps(self.get_usage_summary(), indent=2)
        elif format == "csv":
            import csv
            import io

            output: Any = io.StringIO()
            writer: Any = csv.writer(output)
            writer.writerow(
                ["timestamp", "model", "input_tokens", "output_tokens", "cost", "cumulative_spend"],
            )
            for record in self.usage_history:
                writer.writerow(
                    [
                        record.timestamp,
                        record.model,
                        record.input_tokens,
                        record.output_tokens,
                        record.cost,
                        record.cumulative_spend,
                    ],
                )
            return output.getvalue()
        else:
            raise ValueError(f"Unsupported export format: {format}")


@dataclass
class UsageRecord:
    """Record of a single API usage."""

    timestamp: float
    model: str
    input_tokens: int
    output_tokens: int
    cost: float
    operation: str
    cumulative_spend: float = field(default=0.0, init=False)


_global_governor: CostGovernor | None = None


class CostGovernorManager:
    """Manager for CostGovernor without global state"""

    def __init__(self):
        self._instance = None

    def get_governor(self) -> Any:
        """Get or create the CostGovernor instance"""
        if self._instance is None:
            self._instance = CostGovernor()
        return self._instance


_governor_manager = CostGovernorManager()


def get_global_cost_governor() -> CostGovernor:
    """Get or create the global cost governor."""
    return _governor_manager.get_governor()


def track_api_call(model: str, input_tokens: int, output_tokens: int) -> Any:
    """Convenience function to track API calls using global governor."""
    governor: Any = get_global_cost_governor()
    return governor.track_usage(model, input_tokens, output_tokens)
