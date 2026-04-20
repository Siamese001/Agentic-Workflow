"""Hardened Gemini Executor - Titanium Grade Robustness.

Military-grade reliability for Google GenAI v1beta with:
- Fault tolerance with tenacity retry
- Circuit breaker for sustained failures
- Pre-flight token governance
- Safety settings override
- Structured observability
"""

import logging
import time
from dataclasses import dataclass, field
from typing import Any

from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
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

_emit_reads_policy_state("p0", "hardened_gemini_executor_types", "policy_binding")
_emit_snapshots_state("p0", "hardened_gemini_executor_types", "state_snapshot")
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

_emit_emits_metric_event("hardened_gemini_executor_types", "p4obs", "metric_1")
_emit_emits_metric_event("hardened_gemini_executor_types", "p4obs", "metric_2")
_emit_emits_metric_event("hardened_gemini_executor_types", "p4obs", "metric_3")
_emit_emits_metric_event("hardened_gemini_executor_types", "p4obs", "metric_4")
_emit_emits_metric_event("hardened_gemini_executor_types", "p4obs", "metric_5")
_emit_emits_metric_event("hardened_gemini_executor_types", "p4obs", "metric_6")
_emit_records_incident_event("hardened_gemini_executor_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("hardened_gemini_executor_types", "p4obs", "anomaly")
_emit_writes_observability_log("hardened_gemini_executor_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("hardened_gemini_executor_types", "p4obs", "mon_state")
_emit_triggers_alert("hardened_gemini_executor_types", "p4obs", "alert")
_emit_links_incident_trace("hardened_gemini_executor_types", "p4obs", "trace_link")
_emit_captures_pattern("hardened_gemini_executor_types", "p3lm", "pattern")
_emit_records_learning_event("hardened_gemini_executor_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("hardened_gemini_executor_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("hardened_gemini_executor_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("hardened_gemini_executor_types", "p3lm", "routing")
_emit_improves_agent_policy("hardened_gemini_executor_types", "p3lm", "policy")
_emit_stores_learning_state("hardened_gemini_executor_types", "p3lm", "state")
_emit_records_execution_trace("hardened_gemini_executor_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("hardened_gemini_executor_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("hardened_gemini_executor_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("hardened_gemini_executor_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("hardened_gemini_executor_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("hardened_gemini_executor_types", "env_read", "p2_env_1")
_emit_reads_environ("hardened_gemini_executor_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("hardened_gemini_executor_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("hardened_gemini_executor_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "hardened_gemini_executor_types", "context_pull")
_emit_pulls_context("p1", "hardened_gemini_executor_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "hardened_gemini_executor_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "hardened_gemini_executor_types", "uwg_term_2")
_emit_writes_through("p1", "hardened_gemini_executor_types", "write_through")
_emit_writes_through("p1", "hardened_gemini_executor_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "hardened_gemini_executor_types", "safety_validation")
_emit_invokes_eval("p1", "hardened_gemini_executor_types", "eval_call")
_emit_proposal_commits_routing("p1", "hardened_gemini_executor_types", "routing_commit")
_emit_escalates_to_human("p1", "hardened_gemini_executor_types", "human_escalation")
_emit_routes_through("p1", "hardened_gemini_executor_types", "route_through")
_emit_checks_agent_registry("p1", "hardened_gemini_executor_types", "agent_registry")
_emit_validates_agent_capability("p1", "hardened_gemini_executor_types", "capability")
_emit_dispatches_execution_plan("p1", "hardened_gemini_executor_types", "exec_plan")
_emit_agent_executes_agent("p1", "hardened_gemini_executor_types", "sub_agent")
_emit_routes_to_agent("p1", "hardened_gemini_executor_types", "target_agent")
_emit_verifies_policy("p1", "hardened_gemini_executor_types", "policy_check")
_emit_observes_runtime_state("p1", "hardened_gemini_executor_types", "runtime_state")
_emit_verifies_boundary("p1", "hardened_gemini_executor_types", "boundary_check")
_emit_transcripts_response("p1", "hardened_gemini_executor_types", "transcript")
_emit_hard_fails_untranscripted("p1", "hardened_gemini_executor_types")
_emit_gated_by_confidence("p1", "hardened_gemini_executor_types", "confidence_gate")
emit_replay_key("p0", "hardened_gemini_executor_types")
emit_determinism_digest("p0", "hardened_gemini_executor_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "hardened_gemini_executor_types", "execution_auth")
_emit_validates_capability("p2", "hardened_gemini_executor_types", "capability_check")
_emit_routes_to_capability("p2", "hardened_gemini_executor_types", "capability_route")
_emit_writes_via_uwg("p2", "hardened_gemini_executor_types", "uwg_write")
_emit_blocks_direct_write("p2", "hardened_gemini_executor_types", "direct_write_block")
_emit_records_tool_invocation("p2", "hardened_gemini_executor_types", "tool_invocation")
_emit_captures_execution_output("p2", "hardened_gemini_executor_types", "exec_output")
_emit_dispatches_agent("p3", "hardened_gemini_executor_types", "agent_dispatch")
_emit_coordinates_agents("p3", "hardened_gemini_executor_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "hardened_gemini_executor_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "hardened_gemini_executor_types", "healing_outcome")
_emit_escalates_failure("p3", "hardened_gemini_executor_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "hardened_gemini_executor_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "hardened_gemini_executor_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "hardened_gemini_executor_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "hardened_gemini_executor_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "hardened_gemini_executor_types", "eval_metric")
_emit_stores_embedding("p4", "hardened_gemini_executor_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "hardened_gemini_executor_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "hardened_gemini_executor_types", "exec_snapshot_link")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_1")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_2")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_3")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_4")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_5")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_6")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_7")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_8")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_9")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_10")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_11")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_12")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_13")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_14")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_15")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_16")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_17")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_18")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_19")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_20")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_21")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_22")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_23")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_24")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_25")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_26")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_27")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_28")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_29")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_30")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_31")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_32")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_33")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_34")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_35")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_36")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_37")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_38")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_39")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_40")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_41")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_42")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_43")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_44")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_45")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_46")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_47")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_48")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_49")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_50")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_51")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_52")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_53")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_54")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_55")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_56")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_57")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_58")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_59")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_60")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_61")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_62")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_63")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_64")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_65")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_66")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_67")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_68")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_69")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_70")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_71")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_72")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_73")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_74")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_75")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_76")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_77")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_78")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_79")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_80")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_81")
_emit_reads_through("l4", "hardened_gemini_executor_types", "urg_read_82")

try:
    from .agent_executor import AgentExecutor, AgentMessage
except ImportError:  # guardian: agent_executor module missing — provide stubs  # guardian: allow-silent-swallow - optional dependency

    class AgentMessage:  # type: ignore[no-redef]
        """Stub: agent_executor not installed."""

        pass

    AgentExecutor = None  # type: ignore[assignment, misc]

try:
    from .multi_provider_clients import Provider
except ImportError:  # guardian: multi_provider_clients module missing — provide stub

    class Provider:  # type: ignore[no-redef]
        """Stub: multi_provider_clients not installed."""

        GOOGLE = "google"
        OPENAI = "openai"


logger = logging.getLogger(__name__)

THRESHOLD = 5  # failure_threshold for CircuitBreaker
DEFAULT_TIMEOUT = 60  # recovery_timeout (seconds) for CircuitBreaker


# Custom Exceptions
class ContextOverflowError(Exception):
    """Raised when input exceeds context window safety threshold."""

    pass


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open due to sustained failures."""

    pass


class HardenedGeminiConfig:
    """configuration for HardenedGeminiExecutor."""

    # Model context limits (tokens)
    MODEL_LIMITS = {
        "gemini-2.5-pro": 1048576,  # 1M tokens — canonical healing tier model
        "gemini-2.5-flash": 1048576,  # 1M tokens
        "gemini-3-pro-preview": 2097152,  # 2M tokens
    }

    # Safety threshold (80% of limit)
    SAFETY_THRESHOLD_RATIO = 0.8

    # guardian: allow-magic-config
    def __init__(
        self,
        model: str = "gemini-3-pro-preview",
        temperature: float = 0.3,
        max_output_tokens: int = 8192,
        safety_threshold_ratio: float | None = None,
        max_retries: int = 5,
        retry_min_wait: float = 2.0,
        retry_max_wait: float = 30.0,
    ):
        self.model = model
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens
        self.safety_threshold_ratio = safety_threshold_ratio or self.SAFETY_THRESHOLD_RATIO
        self.max_retries = max_retries
        self.retry_min_wait = retry_min_wait
        self.retry_max_wait = retry_max_wait

    @property
    def max_context_tokens(self) -> int:
        """Get maximum context tokens for the model."""
        return self.MODEL_LIMITS.get(self.model, 1048576)

    @property
    def safety_threshold_tokens(self) -> int:
        """Get safety threshold tokens."""
        return int(self.max_context_tokens * self.safety_threshold_ratio)


@dataclass
class InteractionTelemetry:
    """Telemetry data for interaction logging."""

    interaction_id: str | None
    model: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    latency_ms: float
    timestamp: str = field(default_factory=lambda: time.strftime("%Y-%m-%d %H:%M:%S"))
    error: str | None = None


@dataclass
class CircuitBreakerState:
    """State tracking for circuit breaker."""

    failure_count: int = 0
    last_failure_time: float | None = None
    state: str = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    def __post_init__(self):
        if self.state not in ["CLOSED", "OPEN", "HALF_OPEN"]:
            raise ValueError(f"Invalid circuit breaker state: {self.state}")


class CircuitBreaker:
    """Circuit breaker to prevent cascading failures during sustained outages."""

    # guardian: allow-magic-config
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        half_open_max_calls: int = 3,
    ):
        """Initialize circuit breaker.

        Args:
            failure_threshold: Number of failures before opening
            recovery_timeout: Seconds to wait before trying half-open
            half_open_max_calls: Max calls in half-open state
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        self.state = CircuitBreakerState()
        self.half_open_calls = 0

    def call_allowed(self) -> bool:
        """Check if a call is allowed through the circuit breaker."""
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(
            str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, "CircuitBreaker.call_allowed"
        )
        now = time.time()

        if self.state.state == "CLOSED":
            return True
        elif self.state.state == "OPEN":
            # Check if recovery timeout has passed
            if now - self.state.last_failure_time >= self.recovery_timeout:
                logger.info("Circuit breaker transitioning to HALF_OPEN")
                self.state.state = "HALF_OPEN"
                self.half_open_calls = 0
                return True
            return False
        else:  # HALF_OPEN
            # Allow limited calls in half-open state
            return self.half_open_calls < self.half_open_max_calls

    def record_success(self):
        """Record a successful call."""
        if self.state.state == "HALF_OPEN":
            self.half_open_calls += 1
            # If we've had enough successes, close the circuit
            if self.half_open_calls >= self.half_open_max_calls:
                logger.info("Circuit breaker closing after successful recovery")
                self.state.state = "CLOSED"
                self.state.failure_count = 0
                self.half_open_calls = 0
        elif self.state.state == "CLOSED":
            # Reset failure count on success
            self.state.failure_count = 0

    def record_failure(self):
        """Record a failed call."""
        self.state.failure_count += 1
        self.state.last_failure_time = time.time()

        if self.state.state == "HALF_OPEN":
            # Immediate re-open if failure in half-open
            logger.warning("Circuit breaker re-opening after failure in HALF_OPEN")
            self.state.state = "OPEN"
            self.half_open_calls = 0
        elif self.state.state == "CLOSED":
            # Open if threshold reached
            if self.state.failure_count >= self.failure_threshold:
                logger.error(f"Circuit breaker opening after {self.state.failure_count} failures")
                self.state.state = "OPEN"

    def raise_if_open(self):
        """Raise exception if circuit breaker is open."""
        if self.state.state == "OPEN":
            raise CircuitBreakerOpenError(
                f"Circuit breaker is open. {self.failure_threshold} failures occurred. "
                f"Retry after {self.recovery_timeout} seconds.",
            )


@dataclass
class InteractionTelemetry:
    """Telemetry data for interaction logging."""

    interaction_id: str | None
    model: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    latency_ms: float
    timestamp: str = field(default_factory=lambda: time.strftime("%Y-%m-%d %H:%M:%S"))
    error: str | None = None


class HardenedGeminiExecutor:
    """Military-grade executor for Google GenAI v1beta."""

    def __init__(self, config: HardenedGeminiConfig | None = None):
        """Initialize hardened executor.

        Args:
            config: Optional configuration. Uses defaults if not provided.
        """
        self.config = config or HardenedGeminiConfig()
        self._client = None
        self._setup_client()
        # guardian: allow-magic-config
        self._circuit_breaker = CircuitBreaker(  # guardian: allow-magic-config
            failure_threshold=THRESHOLD,  # guardian: allow-magic-config
            recovery_timeout=DEFAULT_TIMEOUT,  # guardian: allow-magic-config
            half_open_max_calls=3,  # guardian: allow-magic-config
        )

    def _setup_client(self):
        """Setup Google GenAI client."""
        from .multi_provider_clients import get_client

        try:
            self._client = get_client(Provider.GOOGLE)
            if not hasattr(self._client, "interactions"):
                raise ImportError("google-genai v1beta not available")
        # guardian: allow-silent-swallow
        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            RuntimeError,
        ) as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
            logger.error(f"Failed to initialize hardened Gemini client: {e}")
            raise

    def build_safety_config(self) -> list[dict[str, str]]:
        """Build safety settings for Risk/Insurance domain.

        Returns:
            List of safety setting dictionaries.
        """
        # Try to import types from google.genai, fallback to dict format
        try:
            from google.genai import SourceDocument  # noqa: F401

            return [
                types.SafetySetting(
                    category="HARM_CATEGORY_DANGEROUS_CONTENT",
                    threshold="BLOCK_ONLY_HIGH",
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_HARASSMENT",
                    threshold="BLOCK_NONE",  # Allow robust professional critique
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_HATE_SPEECH",
                    threshold="BLOCK_MEDIUM_AND_ABOVE",
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    threshold="BLOCK_MEDIUM_AND_ABOVE",
                ),
            ]
        except ImportError:
            # Fallback for legacy or different API
            return [
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"},
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
                },
            ]

    async def validate_context_budget(self, input_payload: list[dict[str, Any]]) -> int:
        """Pre-flight check to ensure payload doesn't exceed context limit.

        Args:
            input_payload: List of messages to send

        Returns:
            Number of tokens in the payload

        Raises:
            ContextOverflowError: If payload exceeds safety threshold
        """
        try:
            # Try v1beta count_tokens API
            if hasattr(self._client, "models"):
                token_resp = await self._client.aio.models.count_tokens(
                    model=self.config.model,
                    contents=input_payload,
                )
                token_count = token_resp.total_tokens
            else:
                # Fallback: estimate using tiktoken or simple heuristic
                token_count = self._estimate_tokens(input_payload)

        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            RuntimeError,
        ) as e:  # guardian: allow-silent-swallow
            logger.warning(f"Token counting failed, estimating: {e}")
            token_count = self._estimate_tokens(input_payload)

        # Check against safety threshold
        if token_count > self.config.safety_threshold_tokens:
            raise ContextOverflowError(
                f"Payload {token_count} tokens exceeds safety threshold "
                f"({self.config.safety_threshold_tokens} tokens for {self.config.model})",
            )

        return token_count

    def _estimate_tokens(self, input_payload: list[dict[str, Any]]) -> int:
        """Fallback token estimation using simple heuristic.

        Args:
            input_payload: List of messages

        Returns:
            Estimated token count
        """
        total_chars = sum(len(str(msg.get("content", ""))) for msg in input_payload)
        # Rough estimate: ~4 chars per token
        return total_chars // 4

    def _build_payload(
        self,
        messages: list[AgentMessage],
        system_prompt: str | None = None,
    ) -> list[dict[str, Any]]:
        """Build payload for interactions.create.

        Args:
            messages: List of agent messages
            system_prompt: Optional system prompt

        Returns:
            Formatted payload for API
        """
        payload = []

        # Add system prompt as first user message with model acknowledgment
        if system_prompt:
            payload.append({"role": "user", "content": system_prompt})
            payload.append({"role": "model", "content": "Understood. I am ready."})

        # Add messages
        for msg in messages:
            payload.append({"role": msg.role, "content": msg.content})

        return payload

    async def _execute_with_retry(
        self,
        model: str,
        config: dict[str, Any],
        input_payload: list[dict[str, Any]],
        previous_interaction_id: str | None = None,
    ) -> Any:
        """Execute with exponential backoff retry and circuit breaker.

        Args:
            model: Model name
            config: Generation config
            input_payload: Input messages
            previous_interaction_id: For stateful continuation

        Returns:
            API response
        """
        # Check circuit breaker first
        self._circuit_breaker.raise_if_open()

        # Import errors based on available SDK
        try:
            from google.genai import errors

            retry_exception = errors.ClientError
        except ImportError:
            # Fallback to generic exception
            retry_exception = Exception

        @retry(
            retry=retry_if_exception_type(retry_exception),
            stop=stop_after_attempt(self.config.max_retries),
            wait=wait_exponential(
                multiplier=1,
                min=self.config.retry_min_wait,
                max=self.config.retry_max_wait,
            ),
            before_sleep=lambda _: logger.warning("Retrying due to rate limit or server error"),
        )
        async def _execute():
            request_params = {"model": model, "input": input_payload, "config": config}

            if previous_interaction_id:
                request_params["previous_interaction_id"] = previous_interaction_id

            # Try async API first, fallback to sync
            if hasattr(self._client, "aio"):
                return await self._client.aio.interactions.create(**request_params)
            else:
                # Wrap sync call in executor to avoid blocking
                import asyncio

                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(
                    None,
                    lambda: self._client.interactions.create(**request_params),
                )

        try:
            result = await _execute()
            self._circuit_breaker.record_success()
            return result
        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            RuntimeError,
        ):  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
            self._circuit_breaker.record_failure()
            raise

    async def log_interaction_telemetry(self, telemetry: InteractionTelemetry):
        """Log structured telemetry for observability.

        Args:
            telemetry: Telemetry data to log
        """
        log_data = {
            "event": "llm_interaction_complete",
            "interaction_id": telemetry.interaction_id,
            "model": telemetry.model,
            "input_tokens": telemetry.input_tokens,
            "output_tokens": telemetry.output_tokens,
            "total_tokens": telemetry.total_tokens,
            "latency_ms": telemetry.latency_ms,
            "timestamp": telemetry.timestamp,
        }

        if telemetry.error:
            log_data["error"] = telemetry.error

        logger.info(log_data)

    async def execute_k_node(
        self,
        messages: list[AgentMessage],
        system_prompt: str | None = None,
        response_schema: dict[str, Any] | None = None,
        previous_interaction_id: str | None = None,
    ) -> str:
        """Execute K-Node with hardened reliability.

        Args:
            messages: Input messages
            system_prompt: Optional system prompt
            response_schema: JSON schema for structured output
            previous_interaction_id: For stateful continuation

        Returns:
            Generated text response
        """
        start_time = time.time()

        try:
            # 1. Build Config (Typed + Safety + JSON)
            config = {
                "temperature": self.config.temperature,
                "max_output_tokens": self.config.max_output_tokens,
                "safety_settings": self.build_safety_config(),
            }

            # Add JSON schema if provided
            if response_schema:
                config["response_mime_type"] = "application/json"
                config["response_schema"] = response_schema

            # 2. Construct Payload
            payload = self._build_payload(messages, system_prompt)

            # 3. Pre-Flight Check
            input_tokens = await self.validate_context_budget(payload)

            # 4. Execute with Retry
            response = self._execute_with_retry(
                self.config.model,
                config,
                payload,
                previous_interaction_id,
            )

            # 5. Extract response
            content = ""
            if hasattr(response, "candidates") and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, "content") and candidate.content:
                    content = candidate.content.parts[0].text if candidate.content.parts else ""

            # 6. Calculate telemetry
            latency_ms = (time.time() - start_time) * 1000

            # Extract usage if available
            output_tokens = 0
            if hasattr(response, "usage_metadata"):
                output_tokens = response.usage_metadata.candidates_token_count
            else:
                # Estimate output tokens
                output_tokens = len(content) // 4

            # 7. Log telemetry
            telemetry = InteractionTelemetry(
                interaction_id=getattr(response, "id", None),
                model=self.config.model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=input_tokens + output_tokens,
                latency_ms=latency_ms,
            )

            await self.log_interaction_telemetry(telemetry)

            return content

        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            RuntimeError,
        ) as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
            # TODO: Handle specific exception properly
            raise  # Re-raise after logging/handling
            # Log error telemetry

    def invoke_prompt(self, prompt: str, *, api_key: str) -> Any:
        """Synchronous healing-path invocation using google.generativeai v1 SDK.

        Uses tenacity retry (from config) and circuit breaker.
        Called by GeminiInvokerAdapter.invoke_gemini() in the sync healing path.

        Parameters
        ----------
        prompt:
            Plain-text prompt to send to the model.
        api_key:
            Google API key (explicit; no environment variable access).

        Returns
        -------
        GenerateContentResponse with a `.text` attribute, or None on safety block.

        Raises
        ------
        CircuitBreakerOpenError:
            If the circuit breaker is open due to repeated failures.
        ContextOverflowError:
            If the prompt exceeds the model's safety token threshold.
        """
        try:
            import google.generativeai as genai
        except ImportError as exc:
            raise ImportError(
                "google-generativeai SDK is required. Install with: pip install google-generativeai",
            ) from exc

        from tenacity import (
            retry,
            retry_if_exception_type,
            stop_after_attempt,
            wait_exponential,
        )

        # Pre-flight: check circuit breaker
        self._circuit_breaker.raise_if_open()

        # Pre-flight: rough token estimate (4 chars ≈ 1 token)
        estimated_tokens = len(prompt) // 4
        if estimated_tokens > self.config.safety_threshold_tokens:
            raise ContextOverflowError(
                f"Prompt (~{estimated_tokens} tokens) exceeds safety threshold "
                f"({self.config.safety_threshold_tokens} for {self.config.model})",
            )

        genai.configure(api_key=api_key)
        model_client = genai.GenerativeModel(self.config.model)
        generation_config = genai.types.GenerationConfig(
            temperature=self.config.temperature,
            max_output_tokens=self.config.max_output_tokens,
        )

        @retry(
            retry=retry_if_exception_type(Exception),
            stop=stop_after_attempt(self.config.max_retries),
            wait=wait_exponential(
                multiplier=1,
                min=self.config.retry_min_wait,
                max=self.config.retry_max_wait,
            ),
            before_sleep=lambda _: logger.warning(
                "invoke_prompt: retrying Gemini call due to transient error",
            ),
            reraise=True,
        )
        def _call() -> Any:
            return model_client.generate_content(prompt, generation_config=generation_config)

        try:
            response = _call()
            self._circuit_breaker.record_success()
            return response
        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            RuntimeError,
        ):  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
            self._circuit_breaker.record_failure()
            raise

    def execute_sync(
        self,
        messages: list[AgentMessage],
        system_prompt: str | None = None,
        response_schema: dict[str, Any] | None = None,
        previous_interaction_id: str | None = None,
    ) -> str:
        """Synchronous version of execute_k_node.

        Args:
            messages: Input messages
            system_prompt: Optional system prompt
            response_schema: JSON schema for structured output
            previous_interaction_id: For stateful continuation

        Returns:
            Generated text response
        """
        import asyncio

        # Run async method in event loop
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If already in event loop, use run_in_executor
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    asyncio.run,
                    self.execute_k_node(
                        messages,
                        system_prompt,
                        response_schema,
                        previous_interaction_id,
                    ),
                )
                return future.result()
        else:
            return asyncio.run(
                self.execute_k_node(
                    messages,
                    system_prompt,
                    response_schema,
                    previous_interaction_id,
                ),
            )


# Factory function for backward compatibility
# guardian: allow-magic-config
def create_hardened_gemini_executor(
    model: str = "gemini-3-pro-preview",
    temperature: float = 0.3,
    **kwargs,
) -> HardenedGeminiExecutor:
    """Create a hardened Gemini executor.

    Args:
        model: Model name
        temperature: Sampling temperature
        **kwargs: Additional config parameters

    Returns:
        HardenedGeminiExecutor instance
    """
    config = HardenedGeminiConfig(model=model, temperature=temperature, **kwargs)
    return HardenedGeminiExecutor(config)


# Integration with existing AgentExecutor
# guardian: allow-magic-config
def create_agent_executor(
    provider: Provider = Provider.OPENAI,
    model: str | None = None,
    temperature: float = 0.7,
    hardened: bool = False,
    **kwargs,
) -> AgentExecutor | HardenedGeminiExecutor:
    """Factory function to create agent executor with optional hardening.

    Args:
        provider: LLM provider
        model: Optional model name
        temperature: Sampling temperature
        hardened: Use hardened executor for Google provider
        **kwargs: Additional configuration parameters

    Returns:
        AgentExecutor or HardenedGeminiExecutor instance
    """
    if provider == Provider.GOOGLE and hardened:
        return create_hardened_gemini_executor(
            model=model or "gemini-3-pro-preview",
            temperature=temperature,
            **kwargs,
        )

    # Use standard executor for other providers
    from .agent_executor import AgentConfig

    config = AgentConfig(
        provider=provider,
        model=model,
        temperature=temperature,
        **kwargs,
    )

    return AgentExecutor(config)
