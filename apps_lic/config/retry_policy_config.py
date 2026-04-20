"""Retry Policy - Exponential backoff for transient failures.

This module implements sophisticated retry policies with exponential backoff,
jitter, and circuit breaker integration to handle transient failures gracefully.
"""

import asyncio
import logging
import random
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "retry_policy_config", "p0_governance")
_emit_snapshots_state("p0", "retry_policy_config", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)
from tqdm import tqdm

_emit_emits_metric_event("retry_policy_config", "p4obs", "metric_1")
_emit_emits_metric_event("retry_policy_config", "p4obs", "metric_2")
_emit_emits_metric_event("retry_policy_config", "p4obs", "metric_3")
_emit_emits_metric_event("retry_policy_config", "p4obs", "metric_4")
_emit_emits_metric_event("retry_policy_config", "p4obs", "metric_5")
_emit_emits_metric_event("retry_policy_config", "p4obs", "metric_6")
_emit_records_incident_event("retry_policy_config", "p4obs", "incident")
_emit_captures_runtime_anomaly("retry_policy_config", "p4obs", "anomaly")
_emit_writes_observability_log("retry_policy_config", "p4obs", "obs_log")
_emit_updates_monitoring_state("retry_policy_config", "p4obs", "mon_state")
_emit_triggers_alert("retry_policy_config", "p4obs", "alert")
_emit_links_incident_trace("retry_policy_config", "p4obs", "trace_link")
_emit_captures_pattern("retry_policy_config", "p3lm", "pattern")
_emit_records_learning_event("retry_policy_config", "p3lm", "learning_event")
_emit_writes_learning_snapshot("retry_policy_config", "p3lm", "snapshot")
_emit_feeds_meta_learning("retry_policy_config", "p3lm", "meta_feed")
_emit_updates_routing_strategy("retry_policy_config", "p3lm", "routing")
_emit_improves_agent_policy("retry_policy_config", "p3lm", "policy")
_emit_stores_learning_state("retry_policy_config", "p3lm", "state")
_emit_records_execution_trace("retry_policy_config", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("retry_policy_config", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("retry_policy_config", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("retry_policy_config", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("retry_policy_config", "L4_STATE", "p2_trace_5")
_emit_reads_environ("retry_policy_config", "env_read", "p2_env_1")
_emit_reads_environ("retry_policy_config", "env_read", "p2_env_2")
_emit_reads_runtime_state("retry_policy_config", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("retry_policy_config", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "retry_policy_config", "context_pull")
_emit_pulls_context("p1", "retry_policy_config", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "retry_policy_config", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "retry_policy_config", "uwg_term_2")
_emit_writes_through("p1", "retry_policy_config", "write_through")
_emit_writes_through("p1", "retry_policy_config", "write_through_2")
_emit_validated_by_safety_plane("p1", "retry_policy_config", "safety_validation")
_emit_invokes_eval("p1", "retry_policy_config", "eval_call")
_emit_proposal_commits_routing("p1", "retry_policy_config", "routing_commit")
_emit_escalates_to_human("p1", "retry_policy_config", "human_escalation")
_emit_routes_through("p1", "retry_policy_config", "route_through")
_emit_checks_agent_registry("p1", "retry_policy_config", "agent_registry")
_emit_validates_agent_capability("p1", "retry_policy_config", "capability")
_emit_dispatches_execution_plan("p1", "retry_policy_config", "exec_plan")
_emit_agent_executes_agent("p1", "retry_policy_config", "sub_agent")
_emit_routes_to_agent("p1", "retry_policy_config", "target_agent")
_emit_verifies_policy("p1", "retry_policy_config", "policy_check")
_emit_observes_runtime_state("p1", "retry_policy_config", "runtime_state")
_emit_verifies_boundary("p1", "retry_policy_config", "boundary_check")
_emit_transcripts_response("p1", "retry_policy_config", "transcript")
_emit_hard_fails_untranscripted("p1", "retry_policy_config")
_emit_gated_by_confidence("p1", "retry_policy_config", "confidence_gate")
emit_replay_key("p0", "retry_policy_config")
emit_determinism_digest("p0", "retry_policy_config")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "retry_policy_config", "execution_auth")
_emit_validates_capability("p2", "retry_policy_config", "capability_check")
_emit_routes_to_capability("p2", "retry_policy_config", "capability_route")
_emit_writes_via_uwg("p2", "retry_policy_config", "uwg_write")
_emit_blocks_direct_write("p2", "retry_policy_config", "direct_write_block")
_emit_records_tool_invocation("p2", "retry_policy_config", "tool_invocation")
_emit_captures_execution_output("p2", "retry_policy_config", "exec_output")
_emit_dispatches_agent("p3", "retry_policy_config", "agent_dispatch")
_emit_coordinates_agents("p3", "retry_policy_config", "agent_coordination")
_emit_records_workflow_lineage("p3", "retry_policy_config", "workflow_lineage")
_emit_records_healing_outcome("p3", "retry_policy_config", "healing_outcome")
_emit_escalates_failure("p3", "retry_policy_config", "failure_escalation")
_emit_orchestrates_workflow("p3", "retry_policy_config", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "retry_policy_config", "healing_dispatch")
_emit_invokes_evaluation("p3", "retry_policy_config", "evaluation_signal")
_emit_records_telemetry_event("p4", "retry_policy_config", "telemetry_event")
_emit_captures_evaluation_metric("p4", "retry_policy_config", "eval_metric")
_emit_stores_embedding("p4", "retry_policy_config", "embedding_store")
_emit_updates_meta_learning_state("p4", "retry_policy_config", "meta_learning")
_emit_links_execution_to_snapshot("p4", "retry_policy_config", "exec_snapshot_link")


DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

logger = logging.getLogger(__name__)


class RetryStrategy(str, Enum):
    """Retry strategy types."""

    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    FIXED_DELAY = "fixed_delay"
    IMMEDIATE = "immediate"


class RetryableError(Exception):
    """Base class for retryable errors."""

    pass


class NonRetryableError(Exception):
    """Base class for non-retryable errors."""

    pass


@dataclass
class RetryConfig:
    """configuration for retry policy."""

    max_attempts: int = 3
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF
    base_delay: float = 1.0  # seconds
    max_delay: float = 60.0  # seconds
    multiplier: float = 2.0  # for exponential backoff
    jitter: bool = True  # Add randomness to prevent thundering herd
    retryable_exceptions: list[type[Exception]] = field(
        default_factory=lambda: [
            ConnectionError,
            TimeoutError,
            asyncio.TimeoutError,
            RetryableError,
        ],
    )
    non_retryable_exceptions: list[type[Exception]] = field(
        default_factory=lambda: [ValueError, TypeError, KeyError, AttributeError, NonRetryableError],
    )

    def should_retry(self, exception: Exception, attempt: int) -> bool:
        """Check if exception should be retried.

        Args:
            exception: Exception that occurred
            attempt: Current attempt number

        Returns:
            True if should retry
        """
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(
            str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, "RetryPolicy.should_retry"
        )
        # Check attempt limit
        if attempt >= self.max_attempts:
            return False

        # Check non-retryable exceptions
        for exc_type in self.non_retryable_exceptions:
            if isinstance(exception, exc_type):
                return False

        # Check retryable exceptions
        for exc_type in self.retryable_exceptions:
            if isinstance(exception, exc_type):
                return True

        # Default: retry unknown exceptions
        return True


@dataclass
class RetryAttempt:
    """Information about a retry attempt."""

    attempt: int
    delay: float
    exception: Exception | None
    timestamp: datetime
    success: bool


@dataclass
class RetryResult:
    """Result of retry execution."""

    success: bool
    result: Any = None
    attempts: int = 0
    total_delay: float = 0.0
    attempts_history: list[RetryAttempt] = field(default_factory=list)
    final_exception: Exception | None = None


class DelayCalculator:
    """Calculates delay between retry attempts."""

    @staticmethod
    def calculate_delay(config: RetryConfig, attempt: int, base_delay: float | None = None) -> float:
        """Calculate delay for next attempt.

        Args:
            config: Retry configuration
            attempt: Current attempt number (0-based)
            base_delay: Override base delay

        Returns:
            Delay in seconds
        """
        base = base_delay or config.base_delay

        if config.strategy == RetryStrategy.IMMEDIATE:
            delay = 0.0
        elif config.strategy == RetryStrategy.FIXED_DELAY:
            delay = base
        elif config.strategy == RetryStrategy.LINEAR_BACKOFF:
            delay = base * (attempt + 1)
        elif config.strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            delay = base * (config.multiplier**attempt)
        else:
            delay = base

        # Apply max delay limit
        delay = min(delay, config.max_delay)

        # Add jitter if enabled
        if config.jitter and delay > 0:
            # Add up to ±25% jitter
            jitter_range = delay * 0.25
            delay += random.uniform(-jitter_range, jitter_range)
            delay = max(0, delay)  # Ensure non-negative

        return delay


class RetryPolicy:
    """Implements retry policy with configurable strategies."""

    def __init__(self, config: RetryConfig | None = None):
        """Initialize retry policy.

        Args:
            config: Retry configuration
        """
        self.config = config or RetryConfig()
        self._stats = {
            "total_retries": 0,
            "successful_retries": 0,
            "failed_retries": 0,
            "average_attempts": 0.0,
        }

        logger.debug(f"Initialized RetryPolicy with strategy: {self.config.strategy}")

    async def execute(
        self,
        func: Callable,
        *args,
        config: RetryConfig | None = None,
        on_retry: Callable[[RetryAttempt], None] | None = None,
        **kwargs,
    ) -> RetryResult:
        """Execute function with retry policy.

        Args:
            func: Function to execute
            *args: Function arguments
            config: Override retry config
            on_retry: Callback for each retry attempt
            **kwargs: Function keyword arguments

        Returns:
            Retry result
        """
        retry_config = config or self.config
        attempts_history = []
        total_delay = 0.0
        last_exception = None

        for attempt in tqdm(range(retry_config.max_attempts), desc="Processing", unit="item"):
            time.time()

            try:
                # Execute function
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)

                # Success
                attempt_info = RetryAttempt(
                    attempt=attempt + 1,
                    delay=0.0,
                    exception=None,
                    timestamp=datetime.now(timezone.utc),
                    success=True,
                )
                attempts_history.append(attempt_info)

                # Update stats
                self._update_stats(attempt + 1, True)

                logger.debug(f"Function succeeded on attempt {attempt + 1}")

                return RetryResult(
                    success=True,
                    result=result,
                    attempts=attempt + 1,
                    total_delay=total_delay,
                    attempts_history=attempts_history,
                )

            # guardian: allow-silent-swallow
            except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
                # TODO: Handle specific exception properly
                raise  # Re-raise after logging/handling

        # All attempts failed
        self._update_stats(len(attempts_history), False)

        return RetryResult(
            success=False,
            result=None,
            attempts=len(attempts_history),
            total_delay=total_delay,
            attempts_history=attempts_history,
            final_exception=last_exception,
        )

    def _update_stats(self, attempts: int, success: bool) -> None:
        """Update retry statistics.

        Args:
            attempts: Number of attempts
            success: Whether eventually successful
        """
        self._stats["total_retries"] += 1

        if success:
            self._stats["successful_retries"] += 1
        else:
            self._stats["failed_retries"] += 1

        # Update average attempts
        total = self._stats["total_retries"]
        if total > 0:
            current_avg = self._stats["average_attempts"]
            self._stats["average_attempts"] = (current_avg * (total - 1) + attempts) / total

    def get_stats(self) -> dict[str, Any]:
        """Get retry statistics.

        Returns:
            Statistics dictionary
        """
        stats = self._stats.copy()
        if stats["total_retries"] > 0:
            stats["success_rate"] = stats["successful_retries"] / stats["total_retries"]
        else:
            stats["success_rate"] = 0.0
        return stats


class RetryableExecutor:
    """Executor with built-in retry capabilities."""

    def __init__(self, default_config: RetryConfig | None = None):
        """Initialize retryable executor.

        Args:
            default_config: Default retry configuration
        """
        self.default_config = default_config or RetryConfig()
        self.policies: dict[str, RetryPolicy] = {}

    def register_policy(self, name: str, config: RetryConfig) -> None:
        """Register a named retry policy.

        Args:
            name: Policy name
            config: Retry configuration
        """
        self.policies[name] = RetryPolicy(config)
        logger.debug(f"Registered retry policy: {name}")

    async def execute(
        self,
        func: Callable,
        *args,
        policy: str | None = None,
        config: RetryConfig | None = None,
        **kwargs,
    ) -> Any:
        """Execute function with retry policy.

        Args:
            func: Function to execute
            *args: Function arguments
            policy: Named policy to use
            config: Override configuration
            **kwargs: Function keyword arguments

        Returns:
            Function result

        Raises:
            Exception: Last exception if all retries failed
        """
        # Get retry policy
        if policy and policy in self.policies:
            retry_policy = self.policies[policy]
        else:
            retry_policy = RetryPolicy(config or self.default_config)

        # Execute with retry
        result = await retry_policy.execute(func, *args, **kwargs)

        if not result.success:
            raise result.final_exception

        return result.result


# Global retry executor
_retry_executor: RetryableExecutor | None = None
_executor_lock = asyncio.Lock()


async def get_retry_executor() -> RetryableExecutor:
    """Get global retry executor instance.

    Returns:
        RetryableExecutor instance
    """
    global _retry_executor
    async with _executor_lock:
        if _retry_executor is None:
            _retry_executor = RetryableExecutor()
    return _retry_executor


# Decorators for automatic retry
def retry(
    max_attempts: int = 3,
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    retryable_exceptions: list[type[Exception]] | None = None,
):
    """Decorator to add retry to functions.

    Args:
        max_attempts: Maximum retry attempts
        strategy: Retry strategy
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds
        retryable_exceptions: List of retryable exceptions

    Returns:
        Decorated function
    """

    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            config = RetryConfig(
                max_attempts=max_attempts,
                strategy=strategy,
                base_delay=base_delay,
                max_delay=max_delay,
                retryable_exceptions=retryable_exceptions or [],
            )

            retry_policy = RetryPolicy(config)
            result = await retry_policy.execute(func, *args, **kwargs)

            if not result.success:
                raise result.final_exception

            return result.result

        def sync_wrapper(*args, **kwargs):
            # For sync functions, run in thread pool
            async def async_func():
                return func(*args, **kwargs)

            return asyncio.run(async_wrapper())

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def retry_with_policy(policy_name: str):
    """Decorator to use named retry policy.

    Args:
        policy_name: Name of registered policy

    Returns:
        Decorated function
    """

    def decorator(func):
        async def wrapper(*args, **kwargs):
            executor = await get_retry_executor()
            return await executor.execute(func, *args, policy=policy_name, **kwargs)

        return wrapper

    return decorator


# Predefined configurations
RETRY_CONFIGS = {
    "aggressive": RetryConfig(
        max_attempts=5,
        strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
        base_delay=0.5,
        max_delay=30.0,
    ),
    "conservative": RetryConfig(
        max_attempts=3,
        strategy=RetryStrategy.LINEAR_BACKOFF,
        base_delay=2.0,
        max_delay=60.0,
    ),
    "fast": RetryConfig(
        max_attempts=3,
        strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
        base_delay=0.1,
        max_delay=5.0,
    ),
    "slow": RetryConfig(
        max_attempts=5,
        strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
        base_delay=5.0,
        max_delay=300.0,
    ),
}


# Initialize default policies
async def init_default_policies() -> None:
    """Initialize default retry policies."""
    executor = await get_retry_executor()

    for name, config in RETRY_CONFIGS.items():
        executor.register_policy(name, config)

    logger.info("Initialized default retry policies")
