"""Hardened router with intelligent multi-provider fallback.

Implements waterfall routing logic that automatically fails over to backup
providers when primary providers have circuit breakers open.

Phase 2 - Resilient Routing Layer
"""

import logging
from typing import Any

from agentic_core.base_agents.CircuitBreakerState import CircuitBreakerState
from agentic_core.L6_observability.telemetry.system_telemetry_util import SystemTelemetry
from apps_rg.engines.AgentExecutor import AgentMessage, AgentResponse
from apps_rg.engines.hardened_openai_executor import HardenedOpenAIExecutor

# [Diff Start: Updated Imports for Relocation]
# Previous: from runtime.shared.HardenedAnthropicExecutor import HardenedAnthropicExecutor
from apps_rg.engines.HardenedAnthropicExecutor import HardenedAnthropicExecutor
from apps_shared.common_utils.multi_provider_clients import Provider

# [Diff End]
from .schema import DEFAULT_ROUTING_CONFIGS, RouteConfig, RoutingTier

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
        # Telemetry is optional - use provided or None
        self.telemetry = telemetry

        # Initialize hardened executors for each provider
        self.executors: dict[Provider, Any] = {}
        self._initialize_executors()

    def _initialize_executors(self) -> None:
        """Initialize hardened executors for all providers."""
        # Collect all unique providers from all configs
        all_providers = set()
        for config in self.configs.values():
            all_providers.update(config.get_all_providers())

        # Initialize executors
        for provider in all_providers:
            try:
                if provider == Provider.OPENAI:
                    self.executors[provider] = HardenedOpenAIExecutor()
                elif provider == Provider.ANTHROPIC:
                    self.executors[provider] = HardenedAnthropicExecutor()
                elif provider == Provider.GOOGLE:
                    # HardenedGeminiExecutor not yet implemented
                    logger.warning(f"HardenedGeminiExecutor not available for {provider}")
                else:
                    logger.warning(f"No hardened executor available for provider: {provider}")
            except Exception as e:
                logger.error(f"Failed to initialize executor for {provider}: {e}")

    def get_config(self, tier: str | RoutingTier) -> RouteConfig:
        """Get routing configuration for a tier.

        Args:
            tier: Tier name or enum

        Returns:
            RouteConfig for the tier

        Raises:
            ValueError: If tier not found
        """
        tier_name = tier.value if isinstance(tier, RoutingTier) else tier

        if tier_name not in self.configs:
            raise ValueError(
                f"Unknown routing tier: {tier_name}. Available tiers: {list(self.configs.keys())}"
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

        # Check circuit breaker state
        if hasattr(executor, "circuit_breaker"):
            state = executor.circuit_breaker.state
            return state == CircuitBreakerState.CLOSED
        elif hasattr(executor, "get_circuit_breaker_state"):
            state_str = executor.get_circuit_breaker_state()
            return state_str == "CLOSED"

        # If no circuit breaker, assume healthy
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

        # Try primary provider first
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
            except Exception as e:
                logger.warning(f"Primary provider {primary.value} failed: {e}. Attempting fallback...")
        else:
            logger.warning(
                f"Primary provider {primary.value} circuit breaker is OPEN. Routing to fallback..."
            )
            self._log_routing_event(
                tier_name,
                primary,
                is_fallback=True,
                reason="circuit_breaker_open",
            )

        # Try fallback providers
        for fallback in config.fallback_providers:
            if self._is_provider_healthy(fallback):
                try:
                    logger.info(
                        f"Routing to fallback provider: {fallback.value} "
                        f"(primary {primary.value} unavailable)"
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
                except Exception as e:
                    logger.warning(f"Fallback provider {fallback.value} failed: {e}. Trying next fallback...")
            else:
                logger.warning(f"Fallback provider {fallback.value} circuit breaker is OPEN. Skipping...")

        # All providers failed
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

        # Get model override if specified
        model_override = config.get_model_for_provider(provider)

        # Update executor config if model override specified
        if model_override and hasattr(executor, "config"):
            executor.config.model = model_override

        # Execute based on provider type
        if provider == Provider.GOOGLE:
            # Gemini executor uses different method signature
            if hasattr(executor, "execute_k_node"):
                # Build messages
                msg_list = messages or [AgentMessage(role="user", content=prompt)]
                return await executor.execute_k_node(
                    messages=msg_list,
                    system_prompt=system_prompt,
                )

        # OpenAI and Anthropic use run_llm
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

            health[provider.value] = {
                "state": state,
                "healthy": state == "CLOSED",
            }

        return health

    def reset_all_circuit_breakers(self) -> None:
        """Reset all circuit breakers (for testing)."""
        for executor in self.executors.values():
            if hasattr(executor, "reset_circuit_breaker"):
                executor.reset_circuit_breaker()
