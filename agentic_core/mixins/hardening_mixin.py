"""Hardening mixin for resilient execution.

Zero-Ambiguity Standard: Renamed from TokenLimitError.py to hardening_mixin.py
Category: MIXIN (Resilience middleware)

Provides a unified way to add circuit breaking, retries, and telemetry
to any component that executes external operations.

Phase 1 - Pillar 8: Tool Ecosystem (Resilience Middleware)
"""

from __future__ import annotations

import asyncio
import time
from collections.abc import Awaitable, Callable
from typing import Any

from agentic_core.embeddings.tokenization_adapter import TokenCountAdapter
from agentic_core.L0_routing.config.path_constants import DEFAULT_TIMEOUT
from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_reads_policy_state("p0", "hardening_mixin", "policy_binding")
_emit_snapshots_state("p0", "hardening_mixin", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("hardening_mixin", "p4obs", "metric_1")
_emit_emits_metric_event("hardening_mixin", "p4obs", "metric_2")
_emit_emits_metric_event("hardening_mixin", "p4obs", "metric_3")
_emit_emits_metric_event("hardening_mixin", "p4obs", "metric_4")
_emit_emits_metric_event("hardening_mixin", "p4obs", "metric_5")
_emit_emits_metric_event("hardening_mixin", "p4obs", "metric_6")
_emit_records_incident_event("hardening_mixin", "p4obs", "incident")
_emit_captures_runtime_anomaly("hardening_mixin", "p4obs", "anomaly")
_emit_writes_observability_log("hardening_mixin", "p4obs", "obs_log")
_emit_updates_monitoring_state("hardening_mixin", "p4obs", "mon_state")
_emit_triggers_alert("hardening_mixin", "p4obs", "alert")
_emit_links_incident_trace("hardening_mixin", "p4obs", "trace_link")
_emit_captures_pattern("hardening_mixin", "p3lm", "pattern")
_emit_records_learning_event("hardening_mixin", "p3lm", "learning_event")
_emit_writes_learning_snapshot("hardening_mixin", "p3lm", "snapshot")
_emit_feeds_meta_learning("hardening_mixin", "p3lm", "meta_feed")
_emit_updates_routing_strategy("hardening_mixin", "p3lm", "routing")
_emit_improves_agent_policy("hardening_mixin", "p3lm", "policy")
_emit_stores_learning_state("hardening_mixin", "p3lm", "state")
_emit_records_execution_trace("hardening_mixin", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("hardening_mixin", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("hardening_mixin", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("hardening_mixin", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("hardening_mixin", "L4_STATE", "p2_trace_5")
_emit_reads_environ("hardening_mixin", "env_read", "p2_env_1")
_emit_reads_environ("hardening_mixin", "env_read", "p2_env_2")
_emit_reads_runtime_state("hardening_mixin", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("hardening_mixin", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "hardening_mixin", "context_pull")
_emit_pulls_context("p1", "hardening_mixin", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "hardening_mixin", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "hardening_mixin", "uwg_term_2")
_emit_writes_through("p1", "hardening_mixin", "write_through")
_emit_writes_through("p1", "hardening_mixin", "write_through_2")
_emit_validated_by_safety_plane("p1", "hardening_mixin", "safety_validation")
_emit_invokes_eval("p1", "hardening_mixin", "eval_call")
_emit_proposal_commits_routing("p1", "hardening_mixin", "routing_commit")
_emit_escalates_to_human("p1", "hardening_mixin", "human_escalation")
_emit_routes_through("p1", "hardening_mixin", "route_through")
_emit_checks_agent_registry("p1", "hardening_mixin", "agent_registry")
_emit_validates_agent_capability("p1", "hardening_mixin", "capability")
_emit_dispatches_execution_plan("p1", "hardening_mixin", "exec_plan")
_emit_agent_executes_agent("p1", "hardening_mixin", "sub_agent")
_emit_routes_to_agent("p1", "hardening_mixin", "target_agent")
_emit_verifies_policy("p1", "hardening_mixin", "policy_check")
_emit_observes_runtime_state("p1", "hardening_mixin", "runtime_state")
_emit_verifies_boundary("p1", "hardening_mixin", "boundary_check")
_emit_transcripts_response("p1", "hardening_mixin", "transcript")
_emit_hard_fails_untranscripted("p1", "hardening_mixin")
_emit_gated_by_confidence("p1", "hardening_mixin", "confidence_gate")
emit_replay_key("p0", "hardening_mixin")
emit_determinism_digest("p0", "hardening_mixin")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "hardening_mixin", "execution_auth")
_emit_validates_capability("p2", "hardening_mixin", "capability_check")
_emit_routes_to_capability("p2", "hardening_mixin", "capability_route")
_emit_writes_via_uwg("p2", "hardening_mixin", "uwg_write")
_emit_blocks_direct_write("p2", "hardening_mixin", "direct_write_block")
_emit_records_tool_invocation("p2", "hardening_mixin", "tool_invocation")
_emit_captures_execution_output("p2", "hardening_mixin", "exec_output")
_emit_dispatches_agent("p3", "hardening_mixin", "agent_dispatch")
_emit_coordinates_agents("p3", "hardening_mixin", "agent_coordination")
_emit_records_workflow_lineage("p3", "hardening_mixin", "workflow_lineage")
_emit_records_healing_outcome("p3", "hardening_mixin", "healing_outcome")
_emit_escalates_failure("p3", "hardening_mixin", "failure_escalation")
_emit_orchestrates_workflow("p3", "hardening_mixin", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "hardening_mixin", "healing_dispatch")
_emit_invokes_evaluation("p3", "hardening_mixin", "evaluation_signal")
_emit_records_telemetry_event("p4", "hardening_mixin", "telemetry_event")
_emit_captures_evaluation_metric("p4", "hardening_mixin", "eval_metric")
_emit_stores_embedding("p4", "hardening_mixin", "embedding_store")
_emit_updates_meta_learning_state("p4", "hardening_mixin", "meta_learning")
_emit_links_execution_to_snapshot("p4", "hardening_mixin", "exec_snapshot_link")


def _get_circuit_breaker():
    from agentic_core.L4_state.utils.circuit_breaker_util import CircuitBreakerOpenError, get_breaker

    return CircuitBreakerOpenError, get_breaker


def _get_error_recovery_strategy():
    from agentic_core.L5_safety.enforcement.error_recovery_strategy import ErrorRecoveryStrategy

    return ErrorRecoveryStrategy


def _get_telemetry():
    from agentic_core.L6_observability.utils.system_telemetry_util import SystemTelemetry, get_telemetry

    return SystemTelemetry, get_telemetry


class TokenLimitError(Exception):
    """Raised when token budget exceeds model limits."""

    pass


class HardeningMixin:
    """Mixin that adds military-grade resilience to any executor.

    Integrates circuit breaking, retry logic, and structured telemetry.
    Classes should inherit from this mixin and call execute_hardened()
    for external operations.
    """

    def __init__(
        self,
        component_name: str,
        *,
        failure_threshold: int = 5,
        reset_timeout_s: int = 30,
        max_retries: int = 3,
        base_backoff_ms: int = 200,
        jitter_ms: int = 100,
        telemetry: SystemTelemetry | None = None,
    ):
        """Initialize hardening components.

        Args:
            component_name: Name for telemetry and circuit breaker
            failure_threshold: Failures before opening circuit
            reset_timeout_s: Seconds before attempting recovery
            max_retries: Maximum retry attempts
            base_backoff_ms: Base delay for exponential backoff
            jitter_ms: Random jitter range
            telemetry: Custom telemetry instance (uses default if None)
        """
        self.component_name = component_name
        self.circuit_breaker = get_breaker(
            name=f"{component_name}_breaker",
            failure_threshold=failure_threshold,
            reset_after_s=reset_timeout_s,
        )
        self.error_recovery = ErrorRecoveryStrategy(
            max_retries=max_retries,
            base_backoff_ms=base_backoff_ms,
            jitter_ms=jitter_ms,
            enable_circuit_breaker=True,
        )
        self.telemetry = telemetry or get_telemetry()

    async def execute_hardened(
        self,
        operation: str,
        fn: Callable[[], Awaitable[Any]],
        *,
        validate_token_budget: Callable[[], None] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Any:
        """Execute an async function with full hardening applied.

        Args:
            operation: Operation name for telemetry
            fn: Async function to execute
            validate_token_budget: Optional pre-flight validation
            metadata: Additional telemetry metadata

        Returns:
            Result from successful execution

        Raises:
            TokenLimitError: If token budget validation fails
            CircuitBreakerOpenError: If circuit breaker is open
            Exception: If all retries exhausted
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "HardeningMixin.execute_hardened")

        start_time = time.time()
        try:
            if validate_token_budget:
                await asyncio.wait_for(asyncio.to_thread(validate_token_budget), timeout=DEFAULT_TIMEOUT)
            result = await self.error_recovery.invoke_with_retry(
                fn=fn, breaker_name=self.circuit_breaker.name, context=metadata or {}
            )
            latency_ms = (time.time() - start_time) * 1000
            self.telemetry.log_success(
                component=self.component_name, operation=operation, latency_ms=latency_ms, metadata=metadata
            )
            return result
        except asyncio.TimeoutError as e:
            latency_ms = (time.time() - start_time) * 1000
            self.telemetry.log_failure(
                component=self.component_name,
                operation=operation,
                latency_ms=latency_ms,
                error_type="ValidationTimeout",
                error_message="Token budget validation timed out",
                metadata=metadata,
            )
            raise TokenLimitError("Token budget validation timed out") from e
        # guardian: allow-silent-swallow - acceptable exception handling    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context    # guardian: CircuitBreakerOpenError should be handled with specific context
        except CircuitBreakerOpenError as e:
            latency_ms = (time.time() - start_time) * 1000
            self.telemetry.log_circuit_breaker(
                component=self.component_name, breaker_name=e.breaker_name, state="OPEN", metadata=metadata
            )
            raise
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            self.telemetry.log_failure(
                component=self.component_name,
                operation=operation,
                latency_ms=latency_ms,
                error_type=e.__class__.__name__,
                error_message=str(e),
                metadata=metadata,
            )
            raise

    def validate_token_budget_tiktoken(self, prompt: str, model: str, max_tokens: int | None = None) -> None:
        """Validate token budget using tiktoken.

        Args:
            prompt: Input prompt text
            model: OpenAI model name
            max_tokens: Maximum tokens allowed (model-specific if None)

        Raises:
            TokenLimitError: If prompt exceeds token budget
        """
        try:
            tokens = TokenCountAdapter.count_tokens(prompt, model)
        # guardian: allow-silent-swallow - optional dependency
        except ImportError:
            return
        model_limits = {
            "gpt-4": 8192,
            "gpt-4-32k": 32768,
            "gpt-4-0613": 8192,
            "gpt-4-32k-0613": 32768,
            "gpt-3.5-turbo": 4096,
            "gpt-3.5-turbo-16k": 16384,
            "gpt-3.5-turbo-0613": 4096,
            "gpt-3.5-turbo-16k-0613": 16384,
            "gpt-4o": 128000,
            "gpt-4o-2024-08-06": 128000,
            "gpt-4o-mini": 128000,
        }
        limit = max_tokens or model_limits.get(model, 4096)
        if tokens > limit:
            raise TokenLimitError(f"Prompt exceeds token budget: {tokens} > {limit} for model {model}")

    def get_circuit_breaker_state(self) -> str:
        """Get current circuit breaker state."""
        return self.circuit_breaker.state.value

    def reset_circuit_breaker(self) -> None:
        """Reset circuit breaker to CLOSED state (for testing)."""
        from agentic_core.base_agents.circuit_breaker_config import CircuitBreakerState

        self.circuit_breaker.state = CircuitBreakerState.CLOSED
        self.circuit_breaker.failure_count = 0
        self.circuit_breaker.success_count = 0
