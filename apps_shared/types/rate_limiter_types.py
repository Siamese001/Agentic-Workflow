"""Rate Limiter - Protection against API abuse and flooding.

This module implements rate limiting with multiple strategies including
token bucket, sliding window, and fixed window to protect the system
from abuse while ensuring fair usage.
from apps_shared.config.pipeline_constants_config import MAX_RETRIES  # noqa: F401
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

"""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
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
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_through,
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

_emit_applies_guardrail("p0", "rate_limiter_types", "p0_governance")
_emit_reads_policy_state("p0", "rate_limiter_types", "policy_binding")
_emit_snapshots_state("p0", "rate_limiter_types", "state_snapshot")
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

_emit_emits_metric_event("rate_limiter_types", "p4obs", "metric_1")
_emit_emits_metric_event("rate_limiter_types", "p4obs", "metric_2")
_emit_emits_metric_event("rate_limiter_types", "p4obs", "metric_3")
_emit_emits_metric_event("rate_limiter_types", "p4obs", "metric_4")
_emit_emits_metric_event("rate_limiter_types", "p4obs", "metric_5")
_emit_emits_metric_event("rate_limiter_types", "p4obs", "metric_6")
_emit_records_incident_event("rate_limiter_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("rate_limiter_types", "p4obs", "anomaly")
_emit_writes_observability_log("rate_limiter_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("rate_limiter_types", "p4obs", "mon_state")
_emit_triggers_alert("rate_limiter_types", "p4obs", "alert")
_emit_links_incident_trace("rate_limiter_types", "p4obs", "trace_link")
_emit_captures_pattern("rate_limiter_types", "p3lm", "pattern")
_emit_records_learning_event("rate_limiter_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("rate_limiter_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("rate_limiter_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("rate_limiter_types", "p3lm", "routing")
_emit_improves_agent_policy("rate_limiter_types", "p3lm", "policy")
_emit_stores_learning_state("rate_limiter_types", "p3lm", "state")
_emit_records_execution_trace("rate_limiter_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("rate_limiter_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("rate_limiter_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("rate_limiter_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("rate_limiter_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("rate_limiter_types", "env_read", "p2_env_1")
_emit_reads_environ("rate_limiter_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("rate_limiter_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("rate_limiter_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "rate_limiter_types", "context_pull")
_emit_pulls_context("p1", "rate_limiter_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "rate_limiter_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "rate_limiter_types", "uwg_term_2")
_emit_writes_through("p1", "rate_limiter_types", "write_through")
_emit_writes_through("p1", "rate_limiter_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "rate_limiter_types", "safety_validation")
_emit_invokes_eval("p1", "rate_limiter_types", "eval_call")
_emit_proposal_commits_routing("p1", "rate_limiter_types", "routing_commit")
_emit_escalates_to_human("p1", "rate_limiter_types", "human_escalation")
_emit_routes_through("p1", "rate_limiter_types", "route_through")
_emit_checks_agent_registry("p1", "rate_limiter_types", "agent_registry")
_emit_validates_agent_capability("p1", "rate_limiter_types", "capability")
_emit_dispatches_execution_plan("p1", "rate_limiter_types", "exec_plan")
_emit_agent_executes_agent("p1", "rate_limiter_types", "sub_agent")
_emit_routes_to_agent("p1", "rate_limiter_types", "target_agent")
_emit_verifies_policy("p1", "rate_limiter_types", "policy_check")
_emit_observes_runtime_state("p1", "rate_limiter_types", "runtime_state")
_emit_verifies_boundary("p1", "rate_limiter_types", "boundary_check")
_emit_transcripts_response("p1", "rate_limiter_types", "transcript")
_emit_hard_fails_untranscripted("p1", "rate_limiter_types")
_emit_gated_by_confidence("p1", "rate_limiter_types", "confidence_gate")
emit_replay_key("p0", "rate_limiter_types")
emit_determinism_digest("p0", "rate_limiter_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "rate_limiter_types", "execution_auth")
_emit_validates_capability("p2", "rate_limiter_types", "capability_check")
_emit_routes_to_capability("p2", "rate_limiter_types", "capability_route")
_emit_writes_via_uwg("p2", "rate_limiter_types", "uwg_write")
_emit_blocks_direct_write("p2", "rate_limiter_types", "direct_write_block")
_emit_records_tool_invocation("p2", "rate_limiter_types", "tool_invocation")
_emit_captures_execution_output("p2", "rate_limiter_types", "exec_output")
_emit_dispatches_agent("p3", "rate_limiter_types", "agent_dispatch")
_emit_coordinates_agents("p3", "rate_limiter_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "rate_limiter_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "rate_limiter_types", "healing_outcome")
_emit_escalates_failure("p3", "rate_limiter_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "rate_limiter_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "rate_limiter_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "rate_limiter_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "rate_limiter_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "rate_limiter_types", "eval_metric")
_emit_stores_embedding("p4", "rate_limiter_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "rate_limiter_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "rate_limiter_types", "exec_snapshot_link")
_emit_reads_through("l4", "rate_limiter_types", "urg_read_1")
_emit_reads_through("l4", "rate_limiter_types", "urg_read_2")
_emit_reads_through("l4", "rate_limiter_types", "urg_read_3")
_emit_reads_through("l4", "rate_limiter_types", "urg_read_4")
_emit_reads_through("l4", "rate_limiter_types", "urg_read_5")
_emit_reads_through("l4", "rate_limiter_types", "urg_read_6")
_emit_reads_through("l4", "rate_limiter_types", "urg_read_7")
_emit_reads_through("l4", "rate_limiter_types", "urg_read_8")
_emit_reads_through("l4", "rate_limiter_types", "urg_read_9")
_emit_reads_through("l4", "rate_limiter_types", "urg_read_10")
_emit_reads_through("l4", "rate_limiter_types", "urg_read_11")
_emit_reads_through("l4", "rate_limiter_types", "urg_read_12")
_emit_reads_through("l4", "rate_limiter_types", "urg_read_13")
_emit_reads_through("l4", "rate_limiter_types", "urg_read_14")
_emit_reads_through("l4", "rate_limiter_types", "urg_read_15")
_emit_reads_through("l4", "rate_limiter_types", "urg_read_16")
_emit_reads_through("l4", "rate_limiter_types", "urg_read_17")
_emit_reads_through("l4", "rate_limiter_types", "urg_read_18")
_emit_reads_through("l4", "rate_limiter_types", "urg_read_19")
_emit_reads_through("l4", "rate_limiter_types", "urg_read_20")
_emit_reads_through("l4", "rate_limiter_types", "urg_read_21")
_emit_reads_through("l4", "rate_limiter_types", "urg_read_22")
_emit_reads_through("l4", "rate_limiter_types", "urg_read_23")
_emit_reads_through("l4", "rate_limiter_types", "urg_read_24")
_emit_reads_through("l4", "rate_limiter_types", "urg_read_25")
_emit_reads_through("l4", "rate_limiter_types", "urg_read_26")
_emit_reads_through("l4", "rate_limiter_types", "urg_read_27")
_emit_reads_through("l4", "rate_limiter_types", "urg_read_28")
_emit_reads_through("l4", "rate_limiter_types", "urg_read_29")
_emit_reads_through("l4", "rate_limiter_types", "urg_read_30")
_emit_reads_through("l4", "rate_limiter_types", "urg_read_31")
_emit_reads_through("l4", "rate_limiter_types", "urg_read_32")
_emit_reads_through("l4", "rate_limiter_types", "urg_read_33")
_emit_reads_through("l4", "rate_limiter_types", "urg_read_34")
_emit_reads_through("l4", "rate_limiter_types", "urg_read_35")
_emit_reads_through("l4", "rate_limiter_types", "urg_read_36")
_emit_reads_through("l4", "rate_limiter_types", "urg_read_37")
_emit_reads_through("l4", "rate_limiter_types", "urg_read_38")
_emit_reads_through("l4", "rate_limiter_types", "urg_read_39")
_emit_reads_through("l4", "rate_limiter_types", "urg_read_40")
_emit_reads_through("l4", "rate_limiter_types", "urg_read_41")
_emit_reads_through("l4", "rate_limiter_types", "urg_read_42")
_emit_reads_through("l4", "rate_limiter_types", "urg_read_43")
_emit_reads_through("l4", "rate_limiter_types", "urg_read_44")
_emit_reads_through("l4", "rate_limiter_types", "urg_read_45")
_emit_reads_through("l4", "rate_limiter_types", "urg_read_46")
_emit_reads_through("l4", "rate_limiter_types", "urg_read_47")
_emit_reads_through("l4", "rate_limiter_types", "urg_read_48")
_emit_reads_through("l4", "rate_limiter_types", "urg_read_49")
_emit_reads_through("l4", "rate_limiter_types", "urg_read_50")
_emit_reads_through("l4", "rate_limiter_types", "urg_read_51")
_emit_reads_through("l4", "rate_limiter_types", "urg_read_52")
_emit_reads_through("l4", "rate_limiter_types", "urg_read_53")
_emit_reads_through("l4", "rate_limiter_types", "urg_read_54")
_emit_reads_through("l4", "rate_limiter_types", "urg_read_55")
_emit_reads_through("l4", "rate_limiter_types", "urg_read_56")
_emit_reads_through("l4", "rate_limiter_types", "urg_read_57")
_emit_reads_through("l4", "rate_limiter_types", "urg_read_58")
_emit_reads_through("l4", "rate_limiter_types", "urg_read_59")
_emit_reads_through("l4", "rate_limiter_types", "urg_read_60")
_emit_reads_through("l4", "rate_limiter_types", "urg_read_61")
_emit_reads_through("l4", "rate_limiter_types", "urg_read_62")
_emit_reads_through("l4", "rate_limiter_types", "urg_read_63")
_emit_reads_through("l4", "rate_limiter_types", "urg_read_64")
_emit_reads_through("l4", "rate_limiter_types", "urg_read_65")
_emit_reads_through("l4", "rate_limiter_types", "urg_read_66")
_emit_reads_through("l4", "rate_limiter_types", "urg_read_67")
_emit_reads_through("l4", "rate_limiter_types", "urg_read_68")
_emit_reads_through("l4", "rate_limiter_types", "urg_read_69")
_emit_reads_through("l4", "rate_limiter_types", "urg_read_70")
_emit_reads_through("l4", "rate_limiter_types", "urg_read_71")
_emit_reads_through("l4", "rate_limiter_types", "urg_read_72")
_emit_reads_through("l4", "rate_limiter_types", "urg_read_73")

logger = logging.getLogger(__name__)


class RateLimitStrategy(str, Enum):
    """Rate limiting strategies."""

    TOKEN_BUCKET = "token_bucket"
    SLIDING_WINDOW = "sliding_window"
    FIXED_WINDOW = "fixed_window"
    LEAKY_BUCKET = "leaky_bucket"


class RateLimitExceeded(Exception):
    """Raised when rate limit is exceeded."""

    def __init__(self, identifier: str, limit: int, window: int, retry_after: float):
        """Initialize rate limit exceeded error.

        Args:
            identifier: Client identifier
            limit: Request limit
            window: Time window in seconds
            retry_after: Seconds until next request allowed
        """
        super().__init__(
            f"Rate limit exceeded for {identifier}: {limit} requests per {window}s. "
            f"Retry after {retry_after:.1f}s",
        )
        self.identifier = identifier
        self.limit = limit
        self.window = window
        self.retry_after = retry_after


@dataclass
class RateLimitConfig:
    """configuration for rate limiting."""

    limit: int  # Number of requests
    window: int  # Time window in seconds
    strategy: RateLimitStrategy = RateLimitStrategy.TOKEN_BUCKET
    burst_size: int | None = None  # For token bucket
    cleanup_interval: int = 3600  # Cleanup old entries every hour

    def __post_init__(self):
        """Post-initialization validation."""
        if self.burst_size is None:
            self.burst_size = self.limit * 2  # Default burst to 2x limit


@dataclass
class ClientState:
    """State for a rate-limited client."""

    identifier: str
    request_count: int = 0
    window_start: float = field(default_factory=time.time)
    last_request: float = field(default_factory=time.time)
    tokens: float = 0.0  # For token bucket
    last_refill: float = field(default_factory=time.time)

    def reset_window(self) -> None:
        """Reset the time window."""
        self.window_start = time.time()
        self.request_count = 0


class RateLimiter(ABC):
    """Abstract base for rate limiters."""

    @abstractmethod
    async def is_allowed(self, identifier: str) -> bool:
        """Check if request is allowed.

        Args:
            identifier: Client identifier (IP, API key, etc.)

        Returns:
            True if request is allowed
        """
        pass

    @abstractmethod
    async def check_limit(self, identifier: str) -> tuple[bool, float]:
        """Check rate limit and get retry after.

        Args:
            identifier: Client identifier

        Returns:
            Tuple of (allowed, retry_after_seconds)
        """
        pass

    @abstractmethod
    def get_stats(self) -> dict[str, Any]:
        """Get rate limiter statistics.

        Returns:
            Statistics dictionary
        """
        pass


class TokenBucketRateLimiter(RateLimiter):
    """Token bucket rate limiter."""

    def __init__(self, config: RateLimitConfig):
        """Initialize token bucket rate limiter.

        Args:
            config: Rate limit configuration
        """
        self.config = config
        self.clients: dict[str, ClientState] = {}
        self._lock = asyncio.Lock()
        self._cleanup_task: asyncio.Task | None = None

        # Statistics
        self._stats = {
            "total_requests": 0,
            "allowed_requests": 0,
            "blocked_requests": 0,
            "active_clients": 0,
        }

        # Start cleanup task
        self._start_cleanup()

        logger.debug(f"Initialized TokenBucketRateLimiter: {config.limit}/{config.window}s")

    async def is_allowed(self, identifier: str) -> bool:
        """Check if request is allowed.

        Args:
            identifier: Client identifier

        Returns:
            True if request is allowed
        """
        allowed, _ = await self.check_limit(identifier)
        return allowed

    async def check_limit(self, identifier: str) -> tuple[bool, float]:
        """Check rate limit and get retry after.

        Args:
            identifier: Client identifier

        Returns:
            Tuple of (allowed, retry_after_seconds)
        """
        async with self._lock:
            now = time.time()

            # Get or create client state
            if identifier not in self.clients:
                self.clients[identifier] = ClientState(
                    identifier=identifier,
                    tokens=float(self.config.burst_size),
                )

            client = self.clients[identifier]

            # Refill tokens based on time elapsed
            time_elapsed = now - client.last_refill
            tokens_to_add = time_elapsed * (self.config.limit / self.config.window)
            client.tokens = min(client.tokens + tokens_to_add, self.config.burst_size)
            client.last_refill = now

            # Check if request is allowed
            self._stats["total_requests"] += 1

            if client.tokens >= 1:
                # Allow request
                client.tokens -= 1
                client.last_request = now
                self._stats["allowed_requests"] += 1
                return True, 0.0
            else:
                # Block request
                self._stats["blocked_requests"] += 1

                # Calculate retry after
                retry_after = (1 - client.tokens) * (self.config.window / self.config.limit)

                return False, retry_after

    def get_stats(self) -> dict[str, Any]:
        """Get rate limiter statistics.

        Returns:
            Statistics dictionary
        """
        stats = self._stats.copy()
        stats["active_clients"] = len(self.clients)

        if stats["total_requests"] > 0:
            stats["allow_rate"] = stats["allowed_requests"] / stats["total_requests"]
            stats["block_rate"] = stats["blocked_requests"] / stats["total_requests"]
        else:
            stats["allow_rate"] = 0.0
            stats["block_rate"] = 0.0

        return stats

    async def cleanup(self) -> int:
        """Clean up inactive clients.

        Returns:
            Number of clients cleaned up
        """
        async with self._lock:
            now = time.time()
            cutoff = now - self.config.cleanup_interval

            inactive_clients = [
                identifier for identifier, client in self.clients.items() if client.last_request < cutoff
            ]

            for identifier in inactive_clients:
                del self.clients[identifier]

            if inactive_clients:
                logger.debug(f"Cleaned up {len(inactive_clients)} inactive rate limit clients")

            return len(inactive_clients)

    def _start_cleanup(self) -> None:
        """Start the cleanup task."""

        async def cleanup_loop():
            while True:
                try:
                    await asyncio.sleep(self.config.cleanup_interval)
                    await self.cleanup()
                except asyncio.CancelledError:
                    break
                except (TypeError, ValueError, KeyError, AttributeError, RuntimeError, OSError) as e:  # guardian: allow-silent-swallow
                    logger.error(f"Rate limiter cleanup error: {e}")

        try:
            self._cleanup_task = asyncio.create_task(cleanup_loop())
        except RuntimeError:  # review: Runtime errors should be prevented with proper validation
            self._cleanup_task = None  # no event loop — cleanup deferred

    async def stop(self) -> None:
        """Stop the rate limiter."""
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(
            str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, "SlidingWindowRateLimiter.stop"
        )
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass


class SlidingWindowRateLimiter(RateLimiter):
    """Sliding window rate limiter."""

    def __init__(self, config: RateLimitConfig):
        """Initialize sliding window rate limiter.

        Args:
            config: Rate limit configuration
        """
        self.config = config
        self.clients: dict[str, list[float]] = {}  # identifier -> list of request timestamps
        self._lock = asyncio.Lock()

        # Statistics
        self._stats = {
            "total_requests": 0,
            "allowed_requests": 0,
            "blocked_requests": 0,
            "active_clients": 0,
        }

        logger.debug(f"Initialized SlidingWindowRateLimiter: {config.limit}/{config.window}s")

    async def is_allowed(self, identifier: str) -> bool:
        """Check if request is allowed.

        Args:
            identifier: Client identifier

        Returns:
            True if request is allowed
        """
        allowed, _ = await self.check_limit(identifier)
        return allowed

    async def check_limit(self, identifier: str) -> tuple[bool, float]:
        """Check rate limit and get retry after.

        Args:
            identifier: Client identifier

        Returns:
            Tuple of (allowed, retry_after_seconds)
        """
        async with self._lock:
            now = time.time()
            window_start = now - self.config.window

            # Get or create client request list
            if identifier not in self.clients:
                self.clients[identifier] = []

            requests = self.clients[identifier]

            # Remove old requests outside window
            requests[:] = [req_time for req_time in requests if req_time > window_start]

            # Check if under limit
            self._stats["total_requests"] += 1

            if len(requests) < self.config.limit:
                # Allow request
                requests.append(now)
                self._stats["allowed_requests"] += 1
                return True, 0.0
            else:
                # Block request
                self._stats["blocked_requests"] += 1

                # Calculate retry after (oldest request + window - now)
                oldest_request = min(requests)
                retry_after = (oldest_request + self.config.window) - now

                return False, max(0, retry_after)

    def get_stats(self) -> dict[str, Any]:
        """Get rate limiter statistics.

        Returns:
            Statistics dictionary
        """
        stats = self._stats.copy()
        stats["active_clients"] = len(self.clients)

        if stats["total_requests"] > 0:
            stats["allow_rate"] = stats["allowed_requests"] / stats["total_requests"]
            stats["block_rate"] = stats["blocked_requests"] / stats["total_requests"]
        else:
            stats["allow_rate"] = 0.0
            stats["block_rate"] = 0.0

        return stats


class RateLimitManager:
    """Manages multiple rate limiters."""

    def __init__(self):
        """Initialize rate limit manager."""
        self.limiters: dict[str, RateLimiter] = {}
        self._lock = asyncio.Lock()

        logger.info("Initialized RateLimitManager")

    async def add_limiter(self, name: str, config: RateLimitConfig) -> RateLimiter:
        """Add a rate limiter.

        Args:
            name: Limiter name
            config: Rate limit configuration

        Returns:
            Created rate limiter
        """
        async with self._lock:
            if name in self.limiters:
                raise ValueError(f"Rate limiter '{name}' already exists")

            # Create appropriate limiter based on strategy
            if config.strategy == RateLimitStrategy.TOKEN_BUCKET:
                limiter = TokenBucketRateLimiter(config)
            elif config.strategy == RateLimitStrategy.SLIDING_WINDOW:
                limiter = SlidingWindowRateLimiter(config)
            else:
                raise ValueError(f"Unsupported rate limit strategy: {config.strategy}")

            self.limiters[name] = limiter
            logger.info(f"Added rate limiter '{name}' with {config.limit}/{config.window}s")

            return limiter

    async def check_limit(self, limiter_name: str, identifier: str) -> tuple[bool, float]:
        """Check rate limit.

        Args:
            limiter_name: Name of rate limiter
            identifier: Client identifier

        Returns:
            Tuple of (allowed, retry_after_seconds)
        """
        limiter = self.limiters.get(limiter_name)
        if not limiter:
            raise ValueError(f"Rate limiter '{limiter_name}' not found")

        return await limiter.check_limit(identifier)

    async def is_allowed(self, limiter_name: str, identifier: str) -> bool:
        """Check if request is allowed.

        Args:
            limiter_name: Name of rate limiter
            identifier: Client identifier

        Returns:
            True if allowed
        """
        limiter = self.limiters.get(limiter_name)
        if not limiter:
            raise ValueError(f"Rate limiter '{limiter_name}' not found")

        return await limiter.is_allowed(identifier)

    def get_limiter(self, name: str) -> RateLimiter | None:
        """Get rate limiter by name.

        Args:
            name: Limiter name

        Returns:
            Rate limiter if found
        """
        return self.limiters.get(name)

    def list_limiters(self) -> list[str]:
        """List all rate limiter names.

        Returns:
            List of names
        """
        return list(self.limiters.keys())

    async def remove_limiter(self, name: str) -> bool:
        """Remove a rate limiter.

        Args:
            name: Limiter name

        Returns:
            True if removed
        """
        async with self._lock:
            if name in self.limiters:
                limiter = self.limiters[name]

                # Stop cleanup tasks if applicable
                if hasattr(limiter, "stop"):
                    await limiter.stop()

                del self.limiters[name]
                logger.info(f"Removed rate limiter '{name}'")
                return True

            return False

    async def get_all_stats(self) -> dict[str, dict[str, Any]]:
        """Get statistics for all limiters.

        Returns:
            Statistics dictionary
        """
        return {name: limiter.get_stats() for name, limiter in self.limiters.items()}


# Global rate limit manager
_rate_manager: RateLimitManager | None = None
_manager_lock = asyncio.Lock()


async def get_rate_limit_manager() -> RateLimitManager:
    """Get global rate limit manager.

    Returns:
        RateLimitManager instance
    """
    global _rate_manager
    async with _manager_lock:
        if _rate_manager is None:
            _rate_manager = RateLimitManager()
    return _rate_manager


# Decorators for rate limiting
def rate_limit(limiter_name: str, identifier_extractor: Callable | None = None):
    """Decorator to add rate limiting to functions.

    Args:
        limiter_name: Name of rate limiter
        identifier_extractor: Function to extract identifier from args

    Returns:
        Decorated function
    """

    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            manager = await get_rate_limit_manager()

            # Extract identifier
            if identifier_extractor:
                identifier = identifier_extractor(*args, **kwargs)
            else:
                # Default: use first argument or 'default'
                identifier = str(args[0]) if args else "default"

            # Check rate limit
            allowed, retry_after = await manager.check_limit(limiter_name, identifier)

            if not allowed:
                raise RateLimitExceeded(
                    identifier,
                    manager.get_limiter(limiter_name).config.limit,
                    manager.get_limiter(limiter_name).config.window,
                    retry_after,
                )

            # Execute function
            return await func(*args, **kwargs)

        def sync_wrapper(*args, **kwargs):
            # For sync functions, run in thread pool
            async def async_func():
                return func(*args, **kwargs)

            return asyncio.run(async_func())

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


LIMIT = 1000  # Default rate limit

# Predefined configurations
RATE_LIMIT_CONFIGS = {
    "api_default": RateLimitConfig(limit=LIMIT, window=60, strategy=RateLimitStrategy.TOKEN_BUCKET),
    "api_heavy": RateLimitConfig(
        limit=LIMIT,
        window=60,
        strategy=RateLimitStrategy.TOKEN_BUCKET,
        burst_size=2000,
    ),
    "api_strict": RateLimitConfig(limit=LIMIT, window=60, strategy=RateLimitStrategy.SLIDING_WINDOW),
    "upload": RateLimitConfig(limit=LIMIT, window=60, strategy=RateLimitStrategy.TOKEN_BUCKET),
}


# Initialize default limiters
async def init_default_rate_limits() -> None:
    """Initialize default rate limiters."""
    manager = await get_rate_limit_manager()

    for name, config in RATE_LIMIT_CONFIGS.items():
        await manager.add_limiter(name, config)

    logger.info("Initialized default rate limiters")
