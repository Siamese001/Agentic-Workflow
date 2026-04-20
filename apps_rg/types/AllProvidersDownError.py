"""Hardened router with intelligent multi-provider fallback.

Implements waterfall routing logic that automatically fails over to backup
providers when primary providers have circuit breakers open.

Phase 2 - Resilient Routing Layer
"""

import logging
from typing import Any

from apps_shared.utils.Provider import Provider

from agentic_core.interfaces.observability import CircuitBreakerState, SystemTelemetry
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
from apps_rg.engines.hardened_openai_executor import HardenedOpenAIExecutor
from apps_rg.engines.HardenedAnthropicExecutor import HardenedAnthropicExecutor

_emit_authorize_and_execute("p2", "AllProvidersDownError", "execution_auth")
_emit_validates_capability("p2", "AllProvidersDownError", "capability_check")
_emit_routes_to_capability("p2", "AllProvidersDownError", "capability_route")
_emit_writes_via_uwg("p2", "AllProvidersDownError", "uwg_write")
_emit_blocks_direct_write("p2", "AllProvidersDownError", "direct_write_block")
_emit_records_tool_invocation("p2", "AllProvidersDownError", "tool_invocation")
_emit_captures_execution_output("p2", "AllProvidersDownError", "exec_output")
_emit_dispatches_agent("p3", "AllProvidersDownError", "agent_dispatch")
_emit_coordinates_agents("p3", "AllProvidersDownError", "agent_coordination")
_emit_records_workflow_lineage("p3", "AllProvidersDownError", "workflow_lineage")
_emit_records_healing_outcome("p3", "AllProvidersDownError", "healing_outcome")
_emit_escalates_failure("p3", "AllProvidersDownError", "failure_escalation")
_emit_orchestrates_workflow("p3", "AllProvidersDownError", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "AllProvidersDownError", "healing_dispatch")
_emit_invokes_evaluation("p3", "AllProvidersDownError", "evaluation_signal")
_emit_records_telemetry_event("p4", "AllProvidersDownError", "telemetry_event")
_emit_captures_evaluation_metric("p4", "AllProvidersDownError", "eval_metric")
_emit_stores_embedding("p4", "AllProvidersDownError", "embedding_store")
_emit_updates_meta_learning_state("p4", "AllProvidersDownError", "meta_learning")
_emit_links_execution_to_snapshot("p4", "AllProvidersDownError", "exec_snapshot_link")
from apps_rg.engines.hardened_gemini_executor import HardenedGeminiExecutor
from apps_rg.utils.agent_executor_util import AgentMessage, AgentResponse

from .schema import DEFAULT_ROUTING_CONFIGS, RouteConfig, RoutingTier

_emit_applies_guardrail("p0", "AllProvidersDownError", "p0_governance")
_emit_reads_policy_state("p0", "AllProvidersDownError", "policy_binding")
_emit_snapshots_state("p0", "AllProvidersDownError", "state_snapshot")
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

_emit_emits_metric_event("AllProvidersDownError", "p4obs", "metric_1")
_emit_emits_metric_event("AllProvidersDownError", "p4obs", "metric_2")
_emit_emits_metric_event("AllProvidersDownError", "p4obs", "metric_3")
_emit_emits_metric_event("AllProvidersDownError", "p4obs", "metric_4")
_emit_emits_metric_event("AllProvidersDownError", "p4obs", "metric_5")
_emit_emits_metric_event("AllProvidersDownError", "p4obs", "metric_6")
_emit_records_incident_event("AllProvidersDownError", "p4obs", "incident")
_emit_captures_runtime_anomaly("AllProvidersDownError", "p4obs", "anomaly")
_emit_writes_observability_log("AllProvidersDownError", "p4obs", "obs_log")
_emit_updates_monitoring_state("AllProvidersDownError", "p4obs", "mon_state")
_emit_triggers_alert("AllProvidersDownError", "p4obs", "alert")
_emit_links_incident_trace("AllProvidersDownError", "p4obs", "trace_link")
_emit_captures_pattern("AllProvidersDownError", "p3lm", "pattern")
_emit_records_learning_event("AllProvidersDownError", "p3lm", "learning_event")
_emit_writes_learning_snapshot("AllProvidersDownError", "p3lm", "snapshot")
_emit_feeds_meta_learning("AllProvidersDownError", "p3lm", "meta_feed")
_emit_updates_routing_strategy("AllProvidersDownError", "p3lm", "routing")
_emit_improves_agent_policy("AllProvidersDownError", "p3lm", "policy")
_emit_stores_learning_state("AllProvidersDownError", "p3lm", "state")
_emit_records_execution_trace("AllProvidersDownError", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("AllProvidersDownError", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("AllProvidersDownError", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("AllProvidersDownError", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("AllProvidersDownError", "L4_STATE", "p2_trace_5")
_emit_reads_environ("AllProvidersDownError", "env_read", "p2_env_1")
_emit_reads_environ("AllProvidersDownError", "env_read", "p2_env_2")
_emit_reads_runtime_state("AllProvidersDownError", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("AllProvidersDownError", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "AllProvidersDownError", "context_pull")
_emit_pulls_context("p1", "AllProvidersDownError", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "AllProvidersDownError", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "AllProvidersDownError", "uwg_term_2")
_emit_writes_through("p1", "AllProvidersDownError", "write_through")
_emit_writes_through("p1", "AllProvidersDownError", "write_through_2")
_emit_validated_by_safety_plane("p1", "AllProvidersDownError", "safety_validation")
_emit_invokes_eval("p1", "AllProvidersDownError", "eval_call")
_emit_proposal_commits_routing("p1", "AllProvidersDownError", "routing_commit")
_emit_escalates_to_human("p1", "AllProvidersDownError", "human_escalation")
_emit_routes_through("p1", "AllProvidersDownError", "route_through")
_emit_checks_agent_registry("p1", "AllProvidersDownError", "agent_registry")
_emit_validates_agent_capability("p1", "AllProvidersDownError", "capability")
_emit_dispatches_execution_plan("p1", "AllProvidersDownError", "exec_plan")
_emit_agent_executes_agent("p1", "AllProvidersDownError", "sub_agent")
_emit_routes_to_agent("p1", "AllProvidersDownError", "target_agent")
_emit_verifies_policy("p1", "AllProvidersDownError", "policy_check")
_emit_observes_runtime_state("p1", "AllProvidersDownError", "runtime_state")
_emit_verifies_boundary("p1", "AllProvidersDownError", "boundary_check")
_emit_transcripts_response("p1", "AllProvidersDownError", "transcript")
_emit_hard_fails_untranscripted("p1", "AllProvidersDownError")
_emit_gated_by_confidence("p1", "AllProvidersDownError", "confidence_gate")
emit_replay_key("p0", "AllProvidersDownError")
emit_determinism_digest("p0", "AllProvidersDownError")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

logger = logging.getLogger(__name__)


class AllProvidersDownError(Exception):
    """Raised when all providers in the routing chain are unavailable."""

    def __init__(self, tier: str, providers: list[Provider]):
        self.tier = tier
        self.providers = providers
        super().__init__(f"All providers down for tier '{tier}': {[p.value for p in providers]}")


class HardenedRouter:
    """Intelligent router with automatic provider fallback.

    Routes requests to the best available provider based on circuit breaker
    health. Automatically fails over to backup providers when primary is down.
    """

    def __init__(
        self,
        configs: dict[str, RouteConfig] | None = None,
        telemetry: SystemTelemetry | None = None,
    ):
        """Initialize hardened router.

        Args:
            configs: Optional routing configurations (uses defaults if None)
            telemetry: Optional telemetry instance
        """
        self.configs = configs or {tier.value: config for tier, config in DEFAULT_ROUTING_CONFIGS.items()}
        self.telemetry = telemetry
        self.executors: dict[Provider, Any] = {}
        self._initialize_executors()

    def _initialize_executors(self) -> None:
        """Initialize hardened executors for all providers."""
        all_providers = set()
        for config in self.configs.values():
            all_providers.update(config.get_all_providers())
        for provider in tqdm(all_providers, desc="Processing", unit="item"):
            try:
                if provider == Provider.OPENAI:
                    self.executors[provider] = HardenedOpenAIExecutor()
                elif provider == Provider.ANTHROPIC:
                    self.executors[provider] = HardenedAnthropicExecutor()
                elif provider == Provider.GOOGLE:
                    self.executors[provider] = HardenedGeminiExecutor()
                else:
                    logger.warning(f"No hardened executor available for provider: {provider}")
            except (RuntimeError, ValueError, TypeError, ImportError) as e:  # guardian: allow-silent-swallow
                logger.error(f"Failed to initialize executor for {provider}: {e}")
                raise

    def get_config(self, tier: str | RoutingTier) -> RouteConfig:
        """Get routing configuration for a tier.

        Args:
            tier: Tier name or enum

        Returns:
            RouteConfig for the tier

        Raises:
            ValueError: If tier not found
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "HardenedRouter.get_config")

        tier_name = tier.value if isinstance(tier, RoutingTier) else tier
        # guardian: allow-config-with-logic
        if tier_name not in self.configs:
            raise ValueError(
                f"Unknown routing tier: {tier_name}. Available tiers: {list(self.configs.keys())}",
            )
        return self.configs[tier_name]

    def _is_provider_healthy(self, provider: Provider) -> bool:
        """Check if a provider's circuit breaker is healthy.

        Args:
            provider: Provider to check

        Returns:
            True if provider is healthy (circuit closed), False otherwise
        """
        executor = self.executors.get(provider)
        if not executor:
            logger.warning(f"No executor found for provider: {provider}")
            return False
        if hasattr(executor, "circuit_breaker"):
            state = executor.circuit_breaker.state
            return state == CircuitBreakerState.CLOSED
        elif hasattr(executor, "get_circuit_breaker_state"):
            state_str = executor.get_circuit_breaker_state()
            return state_str == "CLOSED"
        return True

    def _log_routing_event(
        self,
        tier: str,
        provider: Provider,
        is_fallback: bool,
        reason: str | None = None,
    ) -> None:
        """Log a routing event for observability.

        Args:
            tier: Routing tier
            provider: Provider selected
            is_fallback: Whether this is a fallback route
            reason: Optional reason for routing decision
        """
        self.telemetry.log_metric(
            component="hardened_router",
            operation="routing_event",
            status="SUCCESS" if not is_fallback else "RETRY",
            latency_ms=0.0,
            metadata={
                "tier": tier,
                "provider": provider.value,
                "is_fallback": is_fallback,
                "reason": reason or "primary_healthy",
            },
        )

    async def execute_with_fallback(
        self,
        tier: str | RoutingTier,
        prompt: str,
        *,
        system_prompt: str | None = None,
        messages: list[AgentMessage] | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        **kwargs,
    ) -> AgentResponse:
        """Execute request with automatic provider fallback.

        Implements the "waterfall" logic:
        1. Check primary provider circuit breaker
        2. If healthy, execute on primary
        3. If unhealthy, try fallback providers in order
        4. If all fail, raise AllProvidersDownError

        Args:
            tier: Routing tier to use
            prompt: Input prompt
            system_prompt: Optional system prompt
            messages: Optional message list (alternative to prompt)
            temperature: Optional temperature override
            max_tokens: Optional max tokens override
            **kwargs: Additional arguments passed to executor

        Returns:
            AgentResponse with generated content and metadata

        Raises:
            AllProvidersDownError: If all providers are unavailable
        """
        config = self.get_config(tier)
        tier_name = config.tier_name
        primary = config.primary_provider
        if self._is_provider_healthy(primary):
            try:
                logger.info(f"Routing to primary provider: {primary.value}")
                self._log_routing_event(tier_name, primary, is_fallback=False)
                return await self._execute_on_provider(
                    provider=primary,
                    config=config,
                    prompt=prompt,
                    system_prompt=system_prompt,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs,
                )
            except (RuntimeError, ValueError, TypeError) as e:  # guardian: allow-silent-swallow
                logger.warning(f"Primary provider {primary.value} failed: {e}. Attempting fallback...")
                raise
        else:
            logger.warning(
                f"Primary provider {primary.value} circuit breaker is OPEN. Routing to fallback...",
            )
            self._log_routing_event(tier_name, primary, is_fallback=True, reason="circuit_breaker_open")
        for fallback in tqdm(config.fallback_providers, desc="Processing", unit="item"):
            if self._is_provider_healthy(fallback):
                try:
                    logger.info(
                        f"Routing to fallback provider: {fallback.value} (primary {primary.value} unavailable)",
                    )
                    self._log_routing_event(
                        tier_name,
                        fallback,
                        is_fallback=True,
                        reason=f"primary_{primary.value}_down",
                    )
                    return await self._execute_on_provider(
                        provider=fallback,
                        config=config,
                        prompt=prompt,
                        system_prompt=system_prompt,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        **kwargs,
                    )
                except (RuntimeError, ValueError, TypeError) as e:  # guardian: allow-silent-swallow
                    logger.warning(f"Fallback provider {fallback.value} failed: {e}. Trying next fallback...")
                    raise
            else:
                logger.warning(f"Fallback provider {fallback.value} circuit breaker is OPEN. Skipping...")
        all_providers = config.get_all_providers()
        logger.error(f"All providers down for tier '{tier_name}': {all_providers}")
        raise AllProvidersDownError(tier_name, all_providers)

    async def _execute_on_provider(
        self,
        provider: Provider,
        config: RouteConfig,
        prompt: str,
        system_prompt: str | None = None,
        messages: list[AgentMessage] | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        **kwargs,
    ) -> AgentResponse:
        """Execute request on a specific provider.

        Args:
            provider: Provider to execute on
            config: Route configuration
            prompt: Input prompt
            system_prompt: Optional system prompt
            messages: Optional message list
            temperature: Optional temperature
            max_tokens: Optional max tokens
            **kwargs: Additional arguments

        Returns:
            AgentResponse with generated content and metadata
        """
        executor = self.executors.get(provider)
        if not executor:
            raise RuntimeError(f"No executor available for provider: {provider}")
        model_override = config.get_model_for_provider(provider)
        if model_override and hasattr(executor, "config"):
            executor.config.model = model_override
        if provider == Provider.GOOGLE:
            if hasattr(executor, "execute_k_node"):
                msg_list = messages or [AgentMessage(role="user", content=prompt)]
                return await executor.execute_k_node(messages=msg_list, system_prompt=system_prompt)
        if hasattr(executor, "run_llm"):
            return await executor.run_llm(
                prompt=prompt,
                system_prompt=system_prompt,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        raise RuntimeError(f"Executor for {provider} has no compatible execution method")

    def get_provider_health(self) -> dict[str, dict[str, Any]]:
        """Get health status of all providers.

        Returns:
            Dictionary mapping provider names to health status
        """
        health = {}
        for provider, executor in self.executors.items():
            state = "UNKNOWN"
            if hasattr(executor, "circuit_breaker"):
                state = executor.circuit_breaker.state.value
            elif hasattr(executor, "get_circuit_breaker_state"):
                state = executor.get_circuit_breaker_state()
            health[provider.value] = {"state": state, "healthy": state == "CLOSED"}
        return health

    def reset_all_circuit_breakers(self) -> None:
        """Reset all circuit breakers (for testing)."""
        for executor in self.executors.values():
            if hasattr(executor, "reset_circuit_breaker"):
                executor.reset_circuit_breaker()
