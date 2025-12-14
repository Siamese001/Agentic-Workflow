import logging
import threading
import time
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

logger = logging.getLogger(__name__)

class BudgetExceededError(Exception):
    """Raised when budget limit is exceeded."""
    def __init__(self, message: str, current_spend: float, limit: float):
        self.current_spend = current_spend
        self.limit = limit
        super().__init__(message)

class CostGovernor:
    """
    Financial Circuit Breaker with real-time cost tracking.

    Tracks costs per session, per model, and implements automatic cutoff
    when budget limits are exceeded.
    """

    def __init__(self,
                 budget_limit: float = 5.00,
                 warning_threshold: float = 0.8,
                 session_id: str = None):
        self.limit = budget_limit
        self.warning_threshold = warning_threshold
        self.session_id = session_id or f"session_{int(time.time())}"

        # Cost tracking
        self.current_spend = 0.0
        self.warning_sent = False
        self._lock = threading.Lock()

        # Model pricing (per 1k tokens) - can be updated
        self.pricing = {
            "gpt-4": {"input": 0.03, "output": 0.06},
            "gpt-4-turbo": {"input": 0.01, "output": 0.03},
            "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
            "claude-3-opus": {"input": 0.015, "output": 0.075},
            "claude-3-sonnet": {"input": 0.003, "output": 0.015},
            "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
        }

        # Usage history
        self.usage_history: List[UsageRecord] = []

        # Callbacks for budget events
        self.on_warning: Optional[Callable] = None
        self.on_exceeded: Optional[Callable] = None

    def track_usage(self,
                   model: str,
                   input_tokens: int,
                   output_tokens: int,
                   operation: str = "completion") -> float:
        """
        Track API usage and update costs.

        Args:
            model: Model name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            operation: Type of operation (completion, embedding, etc.)

        Returns:
            Cost of this operation

        Raises:
            BudgetExceededError: If budget limit is exceeded
        """
        with self._lock:
            # Get pricing for model
            model_pricing = self.pricing.get(model, {"input": 0.01, "output": 0.01})

            # Calculate cost
            input_cost = (input_tokens / 1000) * model_pricing["input"]
            output_cost = (output_tokens / 1000) * model_pricing["output"]
            total_cost = input_cost + output_cost

            # Update spend
            self.current_spend += total_cost

            # Record usage
            record = UsageRecord(
                timestamp=time.time(),
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost=total_cost,
                operation=operation,
                cumulative_spend=self.current_spend
            )
            self.usage_history.append(record)

            # Check warnings and limits
            self._check_budget_status()

            logger.info(f"Tracked usage: {model},
                {input_tokens} in,
                {output_tokens} out,
                ${total_cost:.4f}")

            return total_cost

    def _check_budget_status(self):
        """Check if we've hit warning threshold or exceeded budget."""
        # Check warning threshold
        if not self.warning_sent and self.current_spend >= (self.limit * self.warning_threshold):
            self.warning_sent = True
            logger.warning(f"Budget warning: ${self.current_spend:.2f} of ${self.limit:.2f} spent")
            if self.on_warning:
                self.on_warning(self.current_spend, self.limit)

        # Check budget exceeded
        if self.current_spend >= self.limit:
            logger.error(f"Budget exceeded: ${self.current_spend:.2f} > ${self.limit:.2f}")
            if self.on_exceeded:
                self.on_exceeded(self.current_spend, self.limit)
            raise BudgetExceededError(
                f"Budget limit ${self.limit:.2f} exceeded (Current: ${self.current_spend:.2f})",
                self.current_spend,
                self.limit
            )

    def get_spend(self) -> float:
        """Get current total spend."""
        with self._lock:
            return self.current_spend

    def get_remaining_budget(self) -> float:
        """Get remaining budget."""
        with self._lock:
            return max(0, self.limit - self.current_spend)

    def get_usage_summary(self) -> Dict:
        """Get detailed usage summary."""
        with self._lock:
            if not self.usage_history:
                return {"total_requests": 0}

            # Aggregate by model
            model_usage = {}
            for record in self.usage_history:
                if record.model not in model_usage:
                    model_usage[record.model] = {
                        "requests": 0,
                        "input_tokens": 0,
                        "output_tokens": 0,
                        "cost": 0.0
                    }

                model_usage[record.model]["requests"] += 1
                model_usage[record.model]["input_tokens"] += record.input_tokens
                model_usage[record.model]["output_tokens"] += record.output_tokens
                model_usage[record.model]["cost"] += record.cost

            return {
                "session_id": self.session_id,
                "total_spend": self.current_spend,
                "budget_limit": self.limit,
                "remaining": self.get_remaining_budget(),
                "total_requests": len(self.usage_history),
                "model_breakdown": model_usage,
                "first_request": self.usage_history[0].timestamp if self.usage_history else None,
                "last_request": self.usage_history[-1].timestamp if self.usage_history else None
            }

    def update_pricing(self, model: str, input_price: float, output_price: float):
        """Update pricing for a model."""
        self.pricing[model] = {"input": input_price, "output": output_price}
        logger.info(f"Updated pricing for {model}: ${input_price}/1k in, ${output_price}/1k out")

    def reset(self):
        """Reset all tracking for a new session."""
        with self._lock:
            self.current_spend = 0.0
            self.warning_sent = False
            self.usage_history.clear()
            logger.info(f"Reset cost tracking for session {self.session_id}")

    def export_usage(self, format: str = "json") -> str:
        """Export usage history in specified format."""
        if format == "json":
            import json
            return json.dumps(self.get_usage_summary(), indent=2)
        elif format == "csv":
            import csv
            import io

            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["timestamp",
                "model",
                "input_tokens",
                "output_tokens",
                "cost",
                "cumulative_spend"])

            for record in self.usage_history:
                writer.writerow([
                    record.timestamp,
                    record.model,
                    record.input_tokens,
                    record.output_tokens,
                    record.cost,
                    record.cumulative_spend
                ])

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

# Global cost governor instance
_global_governor: Optional[CostGovernor] = None

def get_global_cost_governor() -> CostGovernor:
    """Get or create the global cost governor."""
    global _global_governor
    if _global_governor is None:
        _global_governor = CostGovernor()
    return _global_governor

def track_api_call(model: str, input_tokens: int, output_tokens: int):
    """Convenience function to track API calls using global governor."""
    governor = get_global_cost_governor()
    return governor.track_usage(model, input_tokens, output_tokens)
