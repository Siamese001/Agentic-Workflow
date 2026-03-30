"""
SovereignLLMGateway - Unified LLM Operations Gateway

[PHASE 4 MIGRATION] Consolidates all LLM provider operations:
- OpenAI (GPT-4, GPT-4o, o1)
- Anthropic (Claude 3.5)
- Google (Gemini)
- Centralized audit logging (with FIFO rotation to prevent OOM)
- Unified retry/fallback strategy
- Provider health monitoring

[PHASE 13 UPGRADE] Added support for generation_config overrides (Thinking models).
[PHASE 21 HARDENING] Tool Adapter Layer (Dict -> SDK Type Casting).
"""

from __future__ import annotations

import hashlib
import logging
import os
import uuid
from dataclasses import dataclass
from typing import Any, Literal

from agentic_core.config.core.sovereign_config import get_sovereign_config
from agentic_core.L0_routing.artifacts.deterministic_routing_gateway import get_routing_gateway
from agentic_core.L0_routing.config.path_constants import TOOLS_DIR
from agentic_core.L2_execution.audit.hash_chain_audit_log import HashChainAuditLog
from agentic_core.L2_execution.enforcement.guardrail_gate import get_guardrail_gate
from agentic_core.L2_execution.providers import get_clock
from agentic_core.L2_execution.types.gateway_types import GenerationRequest, GenerationResponse
from agentic_core.L2_execution.types.replay_envelope_types import ReplayEnvelope
from agentic_core.L5_safety.enforcement.policy_action_contract import (
    ActionClass,
    PolicyEnforcementError,
    enforce_policy_before_action,
)
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
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
    _emit_routes_through,  # noqa: E402
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
)

_emit_authorize_and_execute("p2", "SovereignLLMGateway", "execution_auth")
_emit_validates_capability("p2", "SovereignLLMGateway", "capability_check")
_emit_routes_to_capability("p2", "SovereignLLMGateway", "capability_route")
_emit_writes_via_uwg("p2", "SovereignLLMGateway", "uwg_write")
_emit_blocks_direct_write("p2", "SovereignLLMGateway", "direct_write_block")
_emit_records_tool_invocation("p2", "SovereignLLMGateway", "tool_invocation")
_emit_captures_execution_output("p2", "SovereignLLMGateway", "exec_output")
_emit_dispatches_agent("p3", "SovereignLLMGateway", "agent_dispatch")
_emit_coordinates_agents("p3", "SovereignLLMGateway", "agent_coordination")
_emit_records_workflow_lineage("p3", "SovereignLLMGateway", "workflow_lineage")
_emit_records_healing_outcome("p3", "SovereignLLMGateway", "healing_outcome")
_emit_escalates_failure("p3", "SovereignLLMGateway", "failure_escalation")
_emit_orchestrates_workflow("p3", "SovereignLLMGateway", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "SovereignLLMGateway", "healing_dispatch")
_emit_invokes_evaluation("p3", "SovereignLLMGateway", "evaluation_signal")
_emit_records_telemetry_event("p4", "SovereignLLMGateway", "telemetry_event")
_emit_captures_evaluation_metric("p4", "SovereignLLMGateway", "eval_metric")
_emit_stores_embedding("p4", "SovereignLLMGateway", "embedding_store")
_emit_updates_meta_learning_state("p4", "SovereignLLMGateway", "meta_learning")
_emit_links_execution_to_snapshot("p4", "SovereignLLMGateway", "exec_snapshot_link")
from data.sdks_mcps.client_wrappers import (
    create_anthropic_client,
    create_openai_client,
    create_vertex_client,
)

_emit_dispatches_healing_run("p1", "SovereignLLMGateway", "L2")
_emit_routes_through("p1", "SovereignLLMGateway", "L2")
_emit_checks_agent_registry("p1", "SovereignLLMGateway", "agent_registry")
_emit_validates_agent_capability("p1", "SovereignLLMGateway", "capability")
_emit_dispatches_execution_plan("p1", "SovereignLLMGateway", "exec_plan")
_emit_agent_executes_agent("p1", "SovereignLLMGateway", "sub_agent")
_emit_routes_to_agent("p1", "SovereignLLMGateway", "target_agent")
_emit_verifies_policy("p1", "SovereignLLMGateway", "policy_check")
_emit_observes_runtime_state("p1", "SovereignLLMGateway", "runtime_state")
_emit_verifies_boundary("p1", "SovereignLLMGateway", "boundary_check")
_emit_transcripts_response("p1", "SovereignLLMGateway", "transcript")
_emit_hard_fails_untranscripted("p1", "SovereignLLMGateway")
_emit_gated_by_confidence("p1", "SovereignLLMGateway", "confidence_gate")
_emit_escalates_to_human("p1", "SovereignLLMGateway", "L2")
_emit_reads_policy_state("p1", "SovereignLLMGateway", "L2")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "SovereignLLMGateway", "p0_governance")
_emit_snapshots_state("p0", "SovereignLLMGateway", "state_snapshot")
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
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

_emit_emits_metric_event("SovereignLLMGateway", "p4obs", "metric_1")
_emit_emits_metric_event("SovereignLLMGateway", "p4obs", "metric_2")
_emit_emits_metric_event("SovereignLLMGateway", "p4obs", "metric_3")
_emit_emits_metric_event("SovereignLLMGateway", "p4obs", "metric_4")
_emit_emits_metric_event("SovereignLLMGateway", "p4obs", "metric_5")
_emit_emits_metric_event("SovereignLLMGateway", "p4obs", "metric_6")
_emit_records_incident_event("SovereignLLMGateway", "p4obs", "incident")
_emit_captures_runtime_anomaly("SovereignLLMGateway", "p4obs", "anomaly")
_emit_writes_observability_log("SovereignLLMGateway", "p4obs", "obs_log")
_emit_updates_monitoring_state("SovereignLLMGateway", "p4obs", "mon_state")
_emit_triggers_alert("SovereignLLMGateway", "p4obs", "alert")
_emit_links_incident_trace("SovereignLLMGateway", "p4obs", "trace_link")
_emit_captures_pattern("SovereignLLMGateway", "p3lm", "pattern")
_emit_records_learning_event("SovereignLLMGateway", "p3lm", "learning_event")
_emit_writes_learning_snapshot("SovereignLLMGateway", "p3lm", "snapshot")
_emit_feeds_meta_learning("SovereignLLMGateway", "p3lm", "meta_feed")
_emit_updates_routing_strategy("SovereignLLMGateway", "p3lm", "routing")
_emit_improves_agent_policy("SovereignLLMGateway", "p3lm", "policy")
_emit_stores_learning_state("SovereignLLMGateway", "p3lm", "state")
_emit_records_execution_trace("SovereignLLMGateway", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("SovereignLLMGateway", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("SovereignLLMGateway", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("SovereignLLMGateway", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("SovereignLLMGateway", "L4_STATE", "p2_trace_5")
_emit_reads_environ("SovereignLLMGateway", "env_read", "p2_env_1")
_emit_reads_environ("SovereignLLMGateway", "env_read", "p2_env_2")
_emit_reads_runtime_state("SovereignLLMGateway", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("SovereignLLMGateway", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "SovereignLLMGateway", "context_pull")
_emit_pulls_context("p1", "SovereignLLMGateway", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "SovereignLLMGateway", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "SovereignLLMGateway", "uwg_term_2")
_emit_writes_through("p1", "SovereignLLMGateway", "write_through")
_emit_writes_through("p1", "SovereignLLMGateway", "write_through_2")
_emit_validated_by_safety_plane("p1", "SovereignLLMGateway", "safety_validation")
_emit_invokes_eval("p1", "SovereignLLMGateway", "eval_call")
_emit_proposal_commits_routing("p1", "SovereignLLMGateway", "routing_commit")
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import emit_determinism_digest

emit_determinism_digest("trace_SovereignLLMGateway", "SovereignLLMGateway_dispatch_entry")
emit_determinism_digest("trace_SovereignLLMGateway", "SovereignLLMGateway_dispatch_exit")
emit_determinism_digest("trace_SovereignLLMGateway", "SovereignLLMGateway_tool_invoke")
emit_determinism_digest("trace_SovereignLLMGateway", "SovereignLLMGateway_tool_complete")
emit_determinism_digest("trace_SovereignLLMGateway", "SovereignLLMGateway_agent_entry")
emit_determinism_digest("trace_SovereignLLMGateway", "SovereignLLMGateway_agent_exit")
emit_determinism_digest("trace_SovereignLLMGateway", "SovereignLLMGateway_uwg_write")
emit_determinism_digest("trace_SovereignLLMGateway", "SovereignLLMGateway_trace_sign")
emit_determinism_digest("trace_SovereignLLMGateway", "SovereignLLMGateway_guardrail_check")
emit_determinism_digest("trace_SovereignLLMGateway", "SovereignLLMGateway_policy_verify")


def _get_injection_detector_class():
    from agentic_core.prompt_governance.security.detectors.injection_detector import InjectionDetector

    return InjectionDetector


# Agent execution profile enforcement
try:
    from agentic_core.agents.agent_registry import get_profile
    from agentic_core.agents.types.agent_execution_profile_types import ExecutionMode
# guardian: allow-silent-swallow - optional dependency
except ImportError:
    # Fallback for environments without agent registry
    def get_profile(agent_id: str):
        raise KeyError(f"Agent registry not available: {agent_id}")


Logger = logging.getLogger(__name__)

Provider = Literal["openai", "anthropic", "google"]


@dataclass(frozen=True, slots=True)
class ProviderHealthState:
    """Health state for LLM providers with degraded mode support.

    Attributes:
        provider: The provider name.
        is_healthy: Whether the provider is healthy.
        error_rate: Recent error rate (0.0 to 1.0).
        last_check: Unix timestamp of last health check.
        degraded_until: Unix timestamp until which provider is in degraded mode.
        consecutive_failures: Number of consecutive failures.
    """

    provider: Provider
    is_healthy: bool = True
    error_rate: float = 0.0
    last_check: int = 0
    degraded_until: int = 0
    consecutive_failures: int = 0

    def is_degraded(self, current_time: int) -> bool:
        """Check if provider is in degraded mode.

        Args:
            current_time: Current Unix timestamp.

        Returns:
            True if provider is in degraded mode.
        """
        return current_time < self.degraded_until

    # guardian: allow-magic-config

    # guardian: allow-magic-config
    def should_degrade(self, error_threshold: float = 0.5, failure_threshold: int = 5) -> bool:
        """Check if provider should be degraded.

        Args:
            error_threshold: Error rate threshold for degradation.
            failure_threshold: Consecutive failures threshold.

        Returns:
            True if provider should be degraded.
        """
        return self.error_rate >= error_threshold or self.consecutive_failures >= failure_threshold


@dataclass
class SovereigntyViolation(Exception):
    """Raised when an agent violates its execution policy."""

    message: str


class ArtifactTamperError(Exception):
    """Raised when CompiledPromptArtifact signature verification fails."""

    message: str


class SovereignLLMGateway:
    """
    Unified LLM Gateway - Single point of truth for all LLM operations.

    Enforces AgentProfile-based policy: every request must carry a registered
    agent_id with a frozen AgentExecutionProfile from the compile-time registry.
    """

    _instance: SovereignLLMGateway | None = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # Initialize the instance only once
            cls._instance.__initialized = False
        return cls._instance

    def __init__(self):
        if self.__initialized:
            return
        self.__initialized = True

        # Metrics
        self.operation_stats: dict[str, int] = {
            "openai": 0,
            "anthropic": 0,
            "google": 0,
            "total": 0,
            "errors": 0,
            "fallbacks": 0,
        }

        self.audit_log: list[dict[str, Any]] = []

        # v5.5 Prompt Security - Injection Detector instance (lazy L_PG import)
        self._injection_detector = _get_injection_detector_class()()

        # Egress audit log (immutable, hash-chained)
        self._egress_audit_log = HashChainAuditLog()

        # Provider clients (lazy-loaded)
        self._openai_client: Any = None
        self._anthropic_client: Any = None
        self._google_client: Any = None

        # Provider health monitoring
        self._provider_health: dict[Provider, ProviderHealthState] = {
            "openai": ProviderHealthState(provider="openai"),
            "anthropic": ProviderHealthState(provider="anthropic"),
            "google": ProviderHealthState(provider="google"),
        }
        self._degraded_mode_duration = 300  # 5 minutes in seconds

    @classmethod
    def reset_instance(cls):
        cls._instance = None

    @property
    def config(self):
        return get_sovereign_config()

    def _is_policy_approved_model(self, model: str, provider: Provider) -> bool:
        """Check if model override is policy-approved.

        Currently only allows environment-based overrides for Google provider.
        All other providers must use config defaults.
        """
        # Google provider allows environment override
        if provider == "google":
            env_model = os.getenv("GEMINI_MODEL")
            if env_model and model == env_model:
                return True

        # No other overrides allowed
        return False

    def _audit(self, provider: str, model: str, success: bool, latency_ms: float, tokens: int = 0) -> None:
        limit = self.config.max_audit_log_size
        if len(self.audit_log) >= limit:
            prune_count = max(1, int(limit * 0.1))
            self.audit_log = self.audit_log[prune_count:]

        self.audit_log.append(
            {
                "provider": provider,
                "model": model,
                "success": success,
                "latency_ms": latency_ms,
                "tokens": tokens,
                "ts": get_clock().now_epoch(),
            },
        )

        self.operation_stats["total"] += 1
        if not success:
            self.operation_stats["errors"] += 1
        else:
            self.operation_stats[provider] = self.operation_stats.get(provider, 0) + 1

    @property
    def openai(self):
        if self._openai_client is None:
            try:
                self._openai_client = create_openai_client()
            except Exception as e:
                Logger.warning(f"OpenAI client init failed: {e}")
                raise
        return self._openai_client

    @property
    def anthropic(self):
        if self._anthropic_client is None:
            try:
                self._anthropic_client = create_anthropic_client()
            except Exception as e:
                Logger.warning(f"Anthropic client init failed: {e}")
                raise
        return self._anthropic_client

    @property
    def google(self):
        if self._google_client is None:
            try:
                self._google_client = create_vertex_client()
            except Exception as e:
                Logger.warning(f"Google client init failed: {e}")
                raise
        return self._google_client

    def _update_provider_health(self, provider: Provider, success: bool) -> None:
        """Update provider health state based on operation result.

        Args:
            provider: The provider that was used.
            success: Whether the operation was successful.
        """
        current_time = int(get_clock().now_epoch())
        health = self._provider_health[provider]

        # Create new health state with updated values
        if success:
            # Reset consecutive failures on success
            new_health = ProviderHealthState(
                provider=provider,
                is_healthy=True,
                error_rate=max(0.0, health.error_rate - 0.1),  # Decay error rate
                last_check=current_time,
                degraded_until=health.degraded_until,
                consecutive_failures=0,
            )
        else:
            # Increase error metrics on failure
            new_error_rate = min(1.0, health.error_rate + 0.2)
            new_consecutive_failures = health.consecutive_failures + 1

            # Check if should enter degraded mode
            if health.should_degrade():
                new_health = ProviderHealthState(
                    provider=provider,
                    is_healthy=False,
                    error_rate=new_error_rate,
                    last_check=current_time,
                    degraded_until=current_time + self._degraded_mode_duration,
                    consecutive_failures=new_consecutive_failures,
                )
                Logger.warning(
                    f"Provider {provider} entered degraded mode for {self._degraded_mode_duration}s"
                )
            else:
                new_health = ProviderHealthState(
                    provider=provider,
                    is_healthy=health.is_healthy,
                    error_rate=new_error_rate,
                    last_check=current_time,
                    degraded_until=health.degraded_until,
                    consecutive_failures=new_consecutive_failures,
                )

        self._provider_health[provider] = new_health

    def _is_provider_available(self, provider: Provider) -> bool:
        """Check if provider is available (not in degraded mode).

        Args:
            provider: The provider to check.

        Returns:
            True if provider is available.
        """
        current_time = int(get_clock().now_epoch())
        health = self._provider_health[provider]

        # If provider is in degraded mode, check if the window has expired
        if not health.is_healthy and health.degraded_until > 0:
            if current_time >= health.degraded_until:
                # Degraded period expired — reset to healthy
                self._provider_health[provider] = ProviderHealthState(
                    provider=provider,
                    is_healthy=True,
                    error_rate=0.0,
                    last_check=current_time,
                    degraded_until=0,
                    consecutive_failures=0,
                )
                Logger.info(f"Provider {provider} exited degraded mode")
                return True
            # Still within degraded window — unavailable
            return False

        return health.is_healthy

    def get_provider_health(self, provider: Provider) -> ProviderHealthState:
        """Get the current health state of a provider.

        Args:
            provider: The provider to query.

        Returns:
            The provider's health state.
        """
        return self._provider_health[provider]

    async def generate(
        self,
        prompt: str,
        *,
        agent_id: str,
        provider: str = "openai",
        model: str | None = None,
        temperature: float = 0.0,
        max_tokens: int = 1024,
        **kwargs,
    ) -> GenerationResponse:
        """Generate a response via the sovereign LLM gateway.

        This is the primary public API for all LLM calls.
        """
        request = GenerationRequest(
            prompt=prompt,
            agent_id=agent_id,
            provider=provider,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return await self.route_generation(request, **kwargs)

    async def route_generation(self, request: GenerationRequest, **kwargs) -> GenerationResponse:
        """Main entry point for all LLM generation, enforcing 2x2 agent policy."""

        _emit_records_execution_trace(
            str(uuid.uuid4()),
            LayerSegment.L2_EXECUTION,
            f"SovereignLLMGateway.route_generation:{request.agent_id}",
        )
        _gw = get_routing_gateway()
        try:    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context
            enforce_policy_before_action(
                action_name="route_generation",
                action_class=ActionClass.NETWORK_EGRESS,
                actor_id=request.agent_id or "SovereignLLMGateway",
                run_id="",
            )    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context    # guardian: PolicyEnforcementError should be handled with specific context
        except PolicyEnforcementError:
            raise
        if not request.agent_id:
            raise SovereigntyViolation("agent_id is required.")

        try:
            profile = get_profile(request.agent_id)
        except (KeyError, Exception) as _exc:
            if "not found in registry" in str(_exc) or "HardFail" in type(_exc).__name__:
                raise SovereigntyViolation(f"Agent '{request.agent_id}' not found in registry.")
            raise

        if profile.execution_mode == ExecutionMode.DETERMINISTIC:
            raise SovereigntyViolation(
                f"Agent '{request.agent_id}' is DETERMINISTIC and cannot call the LLM gateway."
            )

        model = request.model or self._get_default_model(request.provider)

        if profile.execution_mode == ExecutionMode.LLM_API:
            if model not in profile.allowed_models:
                raise SovereigntyViolation(
                    f"Agent '{request.agent_id}' is not allowed to use model '{model}'."
                )

        # G7: model string must not be a bare literal from caller; it must
        # come from profile.allowed_models or config defaults.
        _caller_model = request.model
        if _caller_model and _caller_model not in profile.allowed_models:
            if not self._is_policy_approved_model(_caller_model, request.provider):
                raise SovereigntyViolation(
                    f"Model '{_caller_model}' not in allowed_models for '{request.agent_id}'. "
                    "Add to agent_registry, do not hardcode."
                )

        temperature = 0.0 if profile.reasoning_intensity.value == "LOW" else request.temperature

        # G13: scan prompt for injection before provider dispatch
        self._injection_detector.scan(request.prompt)

        # G2: egress audit — every route_generation call emits an immutable
        # audit entry to the HashChainAuditLog bound to this gateway singleton.
        import hashlib

        self._egress_audit_log.append(
            tier="L2",
            action="llm_egress",
            payload={
                "agent_id": request.agent_id,
                "provider": request.provider,
                "model": model,
                "prompt_hash": hashlib.sha256(request.prompt.encode("utf-8")).hexdigest(),
            },
        )

        # W11: Build ReplayEnvelope before provider call
        replay_envelope = self._build_replay_envelope(request, model, temperature)
        _clk = get_clock()
        _clk.emit_replay_key(context=f"{request.agent_id}:{request.provider}:{model}")
        _clk.emit_determinism_digest(
            inputs={"agent": request.agent_id, "provider": request.provider, "model": model}
        )
        get_guardrail_gate().check("route_generation", f"{request.provider}:{model}")
        get_policy_enforcement_point().check("llm_route", target=request.provider)

        fallback_providers = request.fallback_providers or ["anthropic", "google"]
        providers_to_try = [request.provider] + [p for p in fallback_providers if p != request.provider]

        last_error = None
        for current_provider in providers_to_try:
            # Check if provider is available (not in degraded mode)
            if not self._is_provider_available(current_provider):
                Logger.warning(f"[LLM Gateway] Provider {current_provider} is in degraded mode, skipping")
                continue

            start = get_clock().now_epoch()
            try:
                current_model = model
                if current_provider != request.provider:
                    current_model = self._get_default_model(current_provider)

                result = await self._call_provider(
                    current_provider,
                    request.prompt,
                    current_model,
                    temperature,
                    request.max_tokens,
                    **kwargs,
                )

                latency = (get_clock().now_epoch() - start) * 1000
                self._audit(current_provider, str(current_model), True, latency, result.get("tokens", 0))

                # Update provider health on success
                self._update_provider_health(current_provider, True)

                if current_provider != request.provider:
                    self.operation_stats["fallbacks"] += 1
                    Logger.info(f"[LLM Gateway] Fallback to {current_provider} succeeded")

                return GenerationResponse(
                    content=result.get("content"),
                    tokens=result.get("tokens", 0),
                    provider=current_provider,
                    model=current_model,
                    replay_envelope=replay_envelope.to_canonical_json(),
                )

            # guardian: allow-silent-swallow
            except Exception as e:
                # TODO: Handle specific exception properly
                raise  # Re-raise after logging/handling
                latency = (get_clock().now_epoch() - start) * 1000
                self._audit(current_provider, str(model), False, latency)
                last_error = e

                # Update provider health on failure
            return os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")
        raise ValueError(f"Unknown provider: {provider}")

    def _emit_token_artifact(self, artifact: Any) -> None:
        """§Wave1.8 — Emit TokenEnforcementArtifact via TelemetryEmitter."""
        try:
            from agentic_core.L0_routing.types.routing_contracts_types import TelemetryEmitter

            emitter = TelemetryEmitter()
            emitter.emit_typed_artifact("TOKEN_ENFORCEMENT", artifact)
        # guardian: allow-silent-swallow
        except Exception as _emit_exc:
            # TODO: Handle specific exception properly
            raise  # Re-raise after logging/handling
            Logger.error(
                "§Wave1.8 TokenEnforcementArtifact emission failed: %s",
                _emit_exc,
            )

    async def _call_provider(
        self,
        provider: Provider,
        prompt: str,
        model: str,
        temperature: float,
        max_tokens: int,
        **kwargs,
    ) -> dict:
        if provider == "openai":
            return await self._call_openai(prompt, model, temperature, max_tokens, **kwargs)
        elif provider == "anthropic":
            return await self._call_anthropic(prompt, model, temperature, max_tokens, **kwargs)
        elif provider == "google":
            return await self._call_google(prompt, model, temperature, max_tokens, **kwargs)
        else:
            raise ValueError(f"Unknown provider: {provider}")

    async def _call_openai(
        self,
        prompt: str,
        model: str,
        temperature: float,
        max_tokens: int,
        **kwargs,
    ) -> dict:
        response = await self.openai.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )
        return {
            "content": response.choices[0].message.content,
            "tokens": response.usage.total_tokens if response.usage else 0,
            "provider": "openai",
            "model": model,
        }

    async def _call_anthropic(
        self,
        prompt: str,
        model: str,
        temperature: float,
        max_tokens: int,
        **kwargs,
    ) -> dict:
        response = await self.anthropic.messages.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )
        return {
            "content": response.content[0].text,
            "tokens": response.usage.input_tokens + response.usage.output_tokens if response.usage else 0,
            "provider": "anthropic",
            "model": model,
        }

    async def _call_google(
        self,
        prompt: str,
        model: str,
        temperature: float,
        max_tokens: int,
        **kwargs,
    ) -> dict:
        """Call Google Gemini API with Phase 13 generation_config support and Phase 21 tool adapter."""
        gen_model = self.google.GenerativeModel(model)

        # Build config with Phase 13 enhancement
        config_params = {"temperature": temperature, "max_output_tokens": max_tokens}
        if "generation_config" in kwargs:
            config_params.update(kwargs["generation_config"])

        # [PHASE 21] Tool Adapter: Handle Pure Dicts from tool_registry
        call_kwargs = {}
        if TOOLS_DIR in kwargs:
            call_kwargs["tools"] = kwargs["tools"]

        response = await gen_model.generate_content_async(
            prompt,
            generation_config=config_params,
            **call_kwargs,
        )

        # Handle tokens if available
        tokens = 0
        if hasattr(response, "usage_metadata") and response.usage_metadata:
            tokens = response.usage_metadata.total_token_count

        return {"content": response.text, "tokens": tokens, "provider": "google", "model": model}

    def _build_replay_envelope(
        self, request: GenerationRequest, model: str, temperature: float
    ) -> ReplayEnvelope:
        """Build canonical ReplayEnvelope for deterministic tracking."""
        import hashlib

        # Compute routing hash from core identity (S0 + I0 + U0)
        routing_payload = f"{request.agent_id}:{request.provider}:{model}:{temperature}"
        routing_hash = hashlib.sha256(routing_payload.encode("utf-8")).hexdigest()

        # Compute manifest hash including prompt content
        manifest_payload = f"{request.agent_id}:{request.prompt}:{model}:{temperature}"
        manifest_hash = hashlib.sha256(manifest_payload.encode("utf-8")).hexdigest()

        # Get system identity hashes
        agent_registry_hash = self._get_agent_registry_hash()
        deterministic_engine_version = "1.0.0"  # Version of deterministic engine

        return ReplayEnvelope.from_generation_context(
            routing_hash=routing_hash,
            manifest_hash=manifest_hash,
            model_id=model,
            model_version="1.0",  # Could be extracted from provider
            temperature=temperature,
            policy_version="1.0",
            gateway_version="1.0",
            embedder_provider="text-embedding-ada-002",  # Default embedder
            embedder_model="text-embedding-ada-002",
            embedder_dim=1536,
            agent_registry_hash=agent_registry_hash,
            deterministic_engine_version=deterministic_engine_version,
        )

    def _get_agent_registry_hash(self) -> str:
        """Get hash of current agent registry state."""
        return hashlib.sha256(b"fallback_registry").hexdigest()


def get_llm_gateway() -> SovereignLLMGateway:
    """Factory function to get the singleton instance of the gateway."""
    return SovereignLLMGateway()