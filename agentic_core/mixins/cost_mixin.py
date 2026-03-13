"""
CostGuardrailMixin - Phase 1 Critical Infrastructure: Cost Control

Provides token usage monitoring and hard limits on recursive loops to prevent
runaway costs in production environments.

Features:
- Token usage tracking per operation
- Budget enforcement with configurable limits
- Recursive loop detection and prevention
- Cost estimation for LLM operations
- Real-time budget alerts

SSOT PRINCIPLE:
    All agents requiring cost control should inherit from this mixin.
    This ensures consistent cost tracking across the agent ecosystem.
"""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass, field
from typing import Any

Logger = logging.getLogger(__name__)


@dataclass
class TokenUsage:
    """Tracks token usage for a single operation."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: float = 0.0
    model: str = "unknown"
    timestamp: float = field(default_factory=time.time)


@dataclass
class BudgetConfig:
    """Configuration for budget limits."""

    max_tokens_per_request: int = 8000
    max_tokens_per_session: int = 100000
    max_cost_per_session_usd: float = 10.0
    max_recursive_depth: int = 10
    max_loop_iterations: int = 50
    alert_threshold_pct: float = 0.8


class BudgetExceededError(Exception):
    """Raised when budget limits are exceeded."""

    def __init__(self, limit_type: str, current: float, limit: float):
        self.limit_type = limit_type
        self.current = current
        self.limit = limit
        super().__init__(f"Budget exceeded: {limit_type} - Current: {current}, Limit: {limit}")


class RecursionLimitError(Exception):
    """Raised when recursive depth or loop iterations exceed limits."""

    def __init__(self, limit_type: str, current: int, limit: int):
        self.limit_type = limit_type
        self.current = current
        self.limit = limit
        super().__init__(f"Recursion limit exceeded: {limit_type} - Current: {current}, Limit: {limit}")


MODEL_PRICING: dict[str, dict[str, float]] = {
    "gpt-4o": {"input": 0.0025, "output": 0.01},
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
    "gpt-4-turbo": {"input": 0.01, "output": 0.03},
    "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
    "claude-3-opus": {"input": 0.015, "output": 0.075},
    "claude-3-sonnet": {"input": 0.003, "output": 0.015},
    "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
    "default": {"input": 0.001, "output": 0.002},
}


class CostGuardrailMixin:
    """
    Mixin providing cost control and budget enforcement for agents.

    Phase 1 Critical Infrastructure:
    - Token usage tracking
    - Budget limits enforcement
    - Recursive loop prevention
    - Cost estimation and alerts

    Usage:
        class MyAgent(CostGuardrailMixin, SovereignBaseAgent):
            def __init__(self):
                super().__init__()
                self.configure_budget(max_tokens_per_session=50000)

            async def process(self, query: str) -> str:
                with self.track_operation("llm_call"):
                    response = await self.llm_generate(query)
                    self.record_token_usage(
                        prompt_tokens=response["usage"]["prompt_tokens"],
                        completion_tokens=response["usage"]["completion_tokens"],
                        model=response["model"]
                    )
                return response["content"]
    """

    def __init__(self, **kwargs: Any) -> None:
        """Initialize cost guardrail state."""
        super().__init__(**kwargs)
        self._budget_config: BudgetConfig = BudgetConfig()
        self._session_token_usage: list[TokenUsage] = []
        self._session_start_time: float = time.time()
        self._total_session_tokens: int = 0
        self._total_session_cost: float = 0.0
        self._call_stack: list[str] = []
        self._loop_counters: dict[str, int] = {}
        self._cost_lock = threading.RLock()
        self._budget_alerts_sent: set[str] = set()
        self._cost_guardrail_initialized = True
        Logger.debug(f"[COST] {self.__class__.__name__} cost guardrails initialized")

    def configure_budget(
        self,
        max_tokens_per_request: int | None = None,
        max_tokens_per_session: int | None = None,
        max_cost_per_session_usd: float | None = None,
        max_recursive_depth: int | None = None,
        max_loop_iterations: int | None = None,
        alert_threshold_pct: float | None = None,
    ) -> None:
        """
        Configure budget limits for this agent.

        Args:
            max_tokens_per_request: Maximum tokens allowed per single request
            max_tokens_per_session: Maximum tokens allowed per session
            max_cost_per_session_usd: Maximum cost in USD per session
            max_recursive_depth: Maximum recursive call depth
            max_loop_iterations: Maximum iterations in a loop
            alert_threshold_pct: Percentage of budget at which to alert (0.0-1.0)

        Raises:
            ValueError: If any parameter is invalid (negative or out of range)
        """
        if max_tokens_per_request is not None and max_tokens_per_request <= 0:
            raise ValueError("max_tokens_per_request must be positive")
        if max_tokens_per_session is not None and max_tokens_per_session <= 0:
            raise ValueError("max_tokens_per_session must be positive")
        if max_cost_per_session_usd is not None and max_cost_per_session_usd <= 0:
            raise ValueError("max_cost_per_session_usd must be positive")
        if max_recursive_depth is not None and max_recursive_depth <= 0:
            raise ValueError("max_recursive_depth must be positive")
        if max_loop_iterations is not None and max_loop_iterations <= 0:
            raise ValueError("max_loop_iterations must be positive")
        if alert_threshold_pct is not None and (not 0.0 < alert_threshold_pct <= 1.0):
            raise ValueError("alert_threshold_pct must be between 0.0 and 1.0")
        with self._cost_lock:
            if max_tokens_per_request is not None:
                self._budget_config.max_tokens_per_request = max_tokens_per_request
            if max_tokens_per_session is not None:
                self._budget_config.max_tokens_per_session = max_tokens_per_session
            if max_cost_per_session_usd is not None:
                self._budget_config.max_cost_per_session_usd = max_cost_per_session_usd
            if max_recursive_depth is not None:
                self._budget_config.max_recursive_depth = max_recursive_depth
            if max_loop_iterations is not None:
                self._budget_config.max_loop_iterations = max_loop_iterations
            if alert_threshold_pct is not None:
                self._budget_config.alert_threshold_pct = alert_threshold_pct
        Logger.info(f"[COST] Budget configured: {self._budget_config}")

    def estimate_cost(self, prompt_tokens: int, completion_tokens: int, model: str = "default") -> float:
        """
        Estimate cost for a given token usage.

        Args:
            prompt_tokens: Number of input tokens
            completion_tokens: Number of output tokens
            model: Model name for pricing lookup

        Returns:
            Estimated cost in USD
        """
        pricing = MODEL_PRICING.get(model, MODEL_PRICING["default"])
        input_cost = prompt_tokens / 1000 * pricing["input"]
        output_cost = completion_tokens / 1000 * pricing["output"]
        return input_cost + output_cost

    def record_token_usage(
        self, prompt_tokens: int, completion_tokens: int, model: str = "unknown"
    ) -> TokenUsage:
        """
        Record token usage for an operation.

        Args:
            prompt_tokens: Number of input tokens
            completion_tokens: Number of output tokens
            model: Model used for the operation

        Returns:
            TokenUsage record

        Raises:
            BudgetExceededError: If budget limits are exceeded
        """
        total_tokens = prompt_tokens + completion_tokens
        estimated_cost = self.estimate_cost(prompt_tokens, completion_tokens, model)
        with self._cost_lock:
            if total_tokens > self._budget_config.max_tokens_per_request:
                raise BudgetExceededError(
                    "tokens_per_request", total_tokens, self._budget_config.max_tokens_per_request
                )
            new_session_total = self._total_session_tokens + total_tokens
            if new_session_total > self._budget_config.max_tokens_per_session:
                raise BudgetExceededError(
                    "tokens_per_session", new_session_total, self._budget_config.max_tokens_per_session
                )
            new_session_cost = self._total_session_cost + estimated_cost
            if new_session_cost > self._budget_config.max_cost_per_session_usd:
                raise BudgetExceededError(
                    "cost_per_session", new_session_cost, self._budget_config.max_cost_per_session_usd
                )
            usage = TokenUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                estimated_cost_usd=estimated_cost,
                model=model,
            )
            self._session_token_usage.append(usage)
            self._total_session_tokens = new_session_total
            self._total_session_cost = new_session_cost
            self._check_budget_alerts()
        Logger.debug(
            f"[COST] Recorded: {total_tokens} tokens, ${estimated_cost:.4f} (Session: {self._total_session_tokens} tokens, ${self._total_session_cost:.4f})"
        )
        return usage

    def _check_budget_alerts(self) -> None:
        """Check and emit budget alerts if thresholds are exceeded."""
        threshold = self._budget_config.alert_threshold_pct
        token_pct = self._total_session_tokens / self._budget_config.max_tokens_per_session
        if token_pct >= threshold and "token_threshold" not in self._budget_alerts_sent:
            self._budget_alerts_sent.add("token_threshold")
            Logger.warning(
                f"[COST ALERT] Token usage at {token_pct:.0%} of session limit ({self._total_session_tokens}/{self._budget_config.max_tokens_per_session})"
            )
        cost_pct = self._total_session_cost / self._budget_config.max_cost_per_session_usd
        if cost_pct >= threshold and "cost_threshold" not in self._budget_alerts_sent:
            self._budget_alerts_sent.add("cost_threshold")
            Logger.warning(
                f"[COST ALERT] Cost at {cost_pct:.0%} of session limit (${self._total_session_cost:.4f}/${self._budget_config.max_cost_per_session_usd})"
            )

    def check_recursion_limit(self, operation_id: str) -> None:
        """
        Check and enforce recursion depth limits.

        Args:
            operation_id: Unique identifier for the operation

        Raises:
            RecursionLimitError: If recursion depth exceeds limit
        """
        with self._cost_lock:
            current_depth = self._call_stack.count(operation_id)
            if current_depth >= self._budget_config.max_recursive_depth:
                raise RecursionLimitError(
                    "recursive_depth", current_depth, self._budget_config.max_recursive_depth
                )
            self._call_stack.append(operation_id)

    def exit_recursion(self, operation_id: str) -> None:
        """
        Exit a recursive operation, removing it from the call stack.

        Args:
            operation_id: Unique identifier for the operation
        """
        with self._cost_lock:
            if operation_id in self._call_stack:
                self._call_stack.remove(operation_id)

    def check_loop_limit(self, loop_id: str) -> int:
        """
        Check and enforce loop iteration limits.

        Args:
            loop_id: Unique identifier for the loop

        Returns:
            Current iteration count

        Raises:
            RecursionLimitError: If loop iterations exceed limit
        """
        with self._cost_lock:
            current_count = self._loop_counters.get(loop_id, 0) + 1
            if current_count > self._budget_config.max_loop_iterations:
                raise RecursionLimitError(
                    "loop_iterations", current_count, self._budget_config.max_loop_iterations
                )
            self._loop_counters[loop_id] = current_count
            return current_count

    def reset_loop_counter(self, loop_id: str) -> None:
        """
        Reset a loop counter.

        Args:
            loop_id: Unique identifier for the loop
        """
        with self._cost_lock:
            self._loop_counters.pop(loop_id, None)

    def get_budget_status(self) -> dict[str, Any]:
        """
        Get current budget status.

        Returns:
            Dictionary with budget status information
        """
        with self._cost_lock:
            return {
                "session_tokens": self._total_session_tokens,
                "session_cost_usd": self._total_session_cost,
                "max_tokens_per_session": self._budget_config.max_tokens_per_session,
                "max_cost_per_session_usd": self._budget_config.max_cost_per_session_usd,
                "token_usage_pct": self._total_session_tokens / self._budget_config.max_tokens_per_session,
                "cost_usage_pct": self._total_session_cost / self._budget_config.max_cost_per_session_usd,
                "operations_count": len(self._session_token_usage),
                "current_recursion_depth": len(self._call_stack),
                "active_loops": len(self._loop_counters),
                "alerts_sent": list(self._budget_alerts_sent),
            }

    def reset_session(self) -> dict[str, Any]:
        """
        Reset session tracking.

        Returns:
            Summary of the reset session
        """
        with self._cost_lock:
            summary = {
                "total_tokens": self._total_session_tokens,
                "total_cost_usd": self._total_session_cost,
                "operations_count": len(self._session_token_usage),
                "duration_seconds": time.time() - self._session_start_time,
            }
            self._session_token_usage = []
            self._total_session_tokens = 0
            self._total_session_cost = 0.0
            self._session_start_time = time.time()
            self._call_stack = []
            self._loop_counters = {}
            self._budget_alerts_sent = set()
        Logger.info(f"[COST] Session reset. Previous session: {summary}")
        return summary


__all__ = [
    "CostGuardrailMixin",
    "BudgetConfig",
    "TokenUsage",
    "BudgetExceededError",
    "RecursionLimitError",
    "MODEL_PRICING",
]
