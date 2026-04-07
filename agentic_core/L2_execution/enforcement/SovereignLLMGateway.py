"""
Sovereign LLM Gateway

Unified outbound seam for all LLM calls with:
- Signature verification for CompiledPromptArtifact
- Provider abstraction (OpenAI, Anthropic, Vertex, etc.)
- Telemetry ledger for audit trails
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Protocol

from agentic_core.L2_execution.reasoning import CompiledPromptArtifact

_LOGGER = logging.getLogger(__name__)


class ProviderType(Enum):
    """Supported LLM provider types."""

    OPENAI = auto()
    ANTHROPIC = auto()
    VERTEX_AI = auto()
    AZURE_OPENAI = auto()
    LOCAL_VLLM = auto()


class GatewayError(Exception):
    """Base exception for gateway errors."""

    pass


class SignatureVerificationError(GatewayError):
    """Raised when CompiledPromptArtifact signature verification fails."""

    pass


class ProviderError(GatewayError):
    """Raised when provider call fails."""

    pass


class CircuitBreakerOpenError(GatewayError):
    """Raised when circuit breaker is open."""

    pass


@dataclass
class ProviderConfig:
    """Configuration for an LLM provider."""

    provider_type: ProviderType
    api_key: str = ""
    base_url: str = ""
    model: str = ""
    timeout: float = 60.0
    max_retries: int = 3
    extra_headers: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class ReasoningPath:
    """Dynamic reasoning path configuration based on ADG complexity tier."""

    path_id: str
    use_cot: bool
    cot_paths: int
    use_tot: bool
    tot_branches: int
    tot_depth: int
    use_reflexion: bool
    max_reflexion_loops: int
    self_consistency_samples: int
    temperature: float
    adg_complexity_tier: str  # simple, moderate, complex, deep
    estimated_latency_ms: int  # Estimated latency for telemetry


@dataclass
class PathSelectionResult:
    """Result of dynamic reasoning path selection."""

    path: ReasoningPath
    selection_reason: str
    profile_hash: str | None = None
    complexity_tier: str | None = None


# Dynamic reasoning path configurations by ADG complexity tier
REASONING_PATH_TABLE: dict[str, ReasoningPath] = {
    "simple": ReasoningPath(
        path_id="simple_cot",
        use_cot=True,
        cot_paths=1,
        use_tot=False,
        tot_branches=0,
        tot_depth=0,
        use_reflexion=False,
        max_reflexion_loops=0,
        self_consistency_samples=1,
        temperature=0.3,
        adg_complexity_tier="simple",
        estimated_latency_ms=500,
    ),
    "moderate": ReasoningPath(
        path_id="moderate_cot_hybrid",
        use_cot=True,
        cot_paths=2,
        use_tot=True,
        tot_branches=2,
        tot_depth=1,
        use_reflexion=False,
        max_reflexion_loops=0,
        self_consistency_samples=2,
        temperature=0.5,
        adg_complexity_tier="moderate",
        estimated_latency_ms=1500,
    ),
    "complex": ReasoningPath(
        path_id="complex_tot_reflexion",
        use_cot=True,
        cot_paths=3,
        use_tot=True,
        tot_branches=3,
        tot_depth=2,
        use_reflexion=True,
        max_reflexion_loops=1,
        self_consistency_samples=3,
        temperature=0.6,
        adg_complexity_tier="complex",
        estimated_latency_ms=3000,
    ),
    "deep": ReasoningPath(
        path_id="deep_full_reasoning",
        use_cot=True,
        cot_paths=4,
        use_tot=True,
        tot_branches=5,
        tot_depth=3,
        use_reflexion=True,
        max_reflexion_loops=2,
        self_consistency_samples=6,
        temperature=0.7,
        adg_complexity_tier="deep",
        estimated_latency_ms=6000,
    ),
}


@dataclass
class TelemetryRecord:
    """Single telemetry record for an LLM call."""

    trace_id: str
    timestamp: float
    provider: ProviderType
    model: str
    tokens_in: int
    tokens_out: int
    latency_ms: float
    success: bool
    error_type: str | None = None
    error_message: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        trace_id: str,
        provider: ProviderType,
        model: str,
        tokens_in: int,
        tokens_out: int,
        latency_ms: float,
        success: bool,
        **kwargs,
    ) -> TelemetryRecord:
        """Create a telemetry record."""
        return cls(
            trace_id=trace_id,
            timestamp=time.time(),
            provider=provider,
            model=model,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            latency_ms=latency_ms,
            success=success,
            **kwargs,
        )


class LLMProvider(Protocol):
    """Protocol for LLM provider implementations."""

    def generate(
        self, system_prompt: str, user_prompt: str, tools_schema: list[dict] | None = None, **kwargs,
    ) -> dict[str, Any]:
        """Generate response from LLM."""
        ...

    def get_token_count(self, text: str) -> int:
        """Estimate token count for text."""
        ...


class TelemetryLedger:
    """
    Ledger for LLM call telemetry.

    Records all outbound LLM calls for audit and cost tracking.
    """

    def __init__(self) -> None:
        self._records: list[TelemetryRecord] = []
        self._total_calls = 0
        self._successful_calls = 0
        self._failed_calls = 0
        self._total_tokens_in = 0
        self._total_tokens_out = 0
        self._total_latency_ms = 0.0

    def record(self, record: TelemetryRecord) -> None:
        """Add a telemetry record."""
        self._records.append(record)
        self._total_calls += 1

        if record.success:
            self._successful_calls += 1
        else:
            self._failed_calls += 1

        self._total_tokens_in += record.tokens_in
        self._total_tokens_out += record.tokens_out
        self._total_latency_ms += record.latency_ms

        _LOGGER.debug(
            "Telemetry recorded: trace_id=%s provider=%s model=%s success=%s",
            record.trace_id,
            record.provider.name,
            record.model,
            record.success,
        )

    def get_stats(self) -> dict[str, Any]:
        """Get aggregated telemetry statistics."""
        avg_latency = self._total_latency_ms / max(self._total_calls, 1)
        success_rate = self._successful_calls / max(self._total_calls, 1)

        return {
            "total_calls": self._total_calls,
            "successful_calls": self._successful_calls,
            "failed_calls": self._failed_calls,
            "success_rate": success_rate,
            "total_tokens_in": self._total_tokens_in,
            "total_tokens_out": self._total_tokens_out,
            "avg_latency_ms": avg_latency,
        }

    def get_records(
        self, trace_id: str | None = None, provider: ProviderType | None = None, success_only: bool = False,
    ) -> list[TelemetryRecord]:
        """Query telemetry records with optional filters."""
        results = self._records

        if trace_id:
            results = [r for r in results if r.trace_id == trace_id]

        if provider:
            results = [r for r in results if r.provider == provider]

        if success_only:
            results = [r for r in results if r.success]

        return results

    def export_to_dict(self) -> list[dict[str, Any]]:
        """Export all records as dictionaries."""
        return [
            {
                "trace_id": r.trace_id,
                "timestamp": r.timestamp,
                "provider": r.provider.name,
                "model": r.model,
                "tokens_in": r.tokens_in,
                "tokens_out": r.tokens_out,
                "latency_ms": r.latency_ms,
                "success": r.success,
                "error_type": r.error_type,
                "error_message": r.error_message,
                "metadata": r.metadata,
            }
            for r in self._records
        ]


class CircuitBreaker:
    """
    Circuit breaker for LLM provider calls.

    Opens after threshold failures, preventing cascade failures.
    """

    def __init__(
        self, failure_threshold: int = 5, recovery_timeout: float = 30.0, half_open_max_calls: int = 3,
    ) -> None:
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls

        self._failures = 0
        self._last_failure_time: float | None = None
        self._state = "closed"  # closed, open, half_open
        self._half_open_calls = 0

    def call(self, fn, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        if self._state == "open":
            if time.time() - (self._last_failure_time or 0) > self.recovery_timeout:
                self._state = "half_open"
                self._half_open_calls = 0
                _LOGGER.info("Circuit breaker entering half-open state")
            else:
                raise CircuitBreakerOpenError("Circuit breaker is open")

        if self._state == "half_open" and self._half_open_calls >= self.half_open_max_calls:
            raise CircuitBreakerOpenError("Circuit breaker half-open limit reached")

        if self._state == "half_open":
            self._half_open_calls += 1

        try:
            result = fn(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
            self._on_failure()
            raise

    def _on_success(self) -> None:
        """Handle successful call."""
        if self._state == "half_open":
            self._state = "closed"
            self._failures = 0
            _LOGGER.info("Circuit breaker closed after successful half-open call")
        else:
            self._failures = max(0, self._failures - 1)

    def _on_failure(self) -> None:
        """Handle failed call."""
        self._failures += 1
        self._last_failure_time = time.time()

        if self._failures >= self.failure_threshold:
            self._state = "open"
            _LOGGER.warning("Circuit breaker opened after %d failures", self._failures)


class SovereignLLMGateway:
    """
    Sovereign LLM Gateway - single outbound seam for all LLM calls.

    Features:
    - CompiledPromptArtifact signature verification
    - Provider abstraction with pluggable backends
    - Telemetry ledger for audit trails
    - Circuit breaker for resilience

    Usage:
        gateway = SovereignLLMGateway(secret_key=b"hmac-secret")
        gateway.register_provider(ProviderType.OPENAI, openai_config)

        artifact = engine.assemble()  # CompiledPromptArtifact
        response = gateway.generate(artifact)
    """

    def __init__(
        self, secret_key: bytes, verify_signatures: bool = True, default_provider: ProviderType | None = None,
    ) -> None:
        self._secret_key = secret_key
        self._verify_signatures = verify_signatures
        self._default_provider = default_provider
        self._providers: dict[ProviderType, tuple[LLMProvider, ProviderConfig]] = {}
        self._ledger = TelemetryLedger()
        self._circuit_breaker = CircuitBreaker()

    def register_provider(
        self, provider_type: ProviderType, config: ProviderConfig, provider_impl: LLMProvider | None = None,
    ) -> None:
        """Register an LLM provider."""
        if provider_impl is None:
            provider_impl = self._create_default_provider(provider_type, config)

        self._providers[provider_type] = (provider_impl, config)
        _LOGGER.info("Registered provider: %s", provider_type.name)

    def set_default_provider(self, provider_type: ProviderType) -> None:
        """Set the default provider for generate calls."""
        if provider_type not in self._providers:
            raise GatewayError(f"Cannot set default: provider {provider_type.name} not registered")
        self._default_provider = provider_type
        _LOGGER.info("Default provider set to: %s", provider_type.name)

    def _create_default_provider(self, provider_type: ProviderType, config: ProviderConfig) -> LLMProvider:
        """Create default provider implementation."""
        # Placeholder - actual implementations would be in separate modules
        return _PlaceholderProvider(config)

    def select_reasoning_path(
        self,
        complexity_tier: str = "moderate",
        profile_hash: str | None = None,
        latency_budget_ms: int | None = None,
    ) -> PathSelectionResult:
        """
        Dynamically select reasoning path based on ADG complexity tier.

        Args:
            complexity_tier: ADG complexity tier (simple, moderate, complex, deep)
            profile_hash: Optional L0-stamped profile hash for traceability
            latency_budget_ms: Optional latency constraint for path selection

        Returns:
            PathSelectionResult with selected path and selection metadata
        """
        # Normalize complexity tier
        tier = complexity_tier.lower() if complexity_tier else "moderate"

        # Validate tier against available paths
        if tier not in REASONING_PATH_TABLE:
            _LOGGER.warning("Unknown complexity tier '%s', falling back to 'moderate'", tier)
            tier = "moderate"

        path = REASONING_PATH_TABLE[tier]

        # If latency budget specified, check if path fits
        if latency_budget_ms is not None and path.estimated_latency_ms > latency_budget_ms:
            # Fall back to simpler path if available
            fallback_order = ["simple", "moderate", "complex", "deep"]
            current_idx = fallback_order.index(tier) if tier in fallback_order else 1

            for fallback_tier in fallback_order[:current_idx]:
                fallback_path = REASONING_PATH_TABLE[fallback_tier]
                if fallback_path.estimated_latency_ms <= latency_budget_ms:
                    _LOGGER.info(
                        "Latency budget %dms exceeded by '%s' (%dms), falling back to '%s' (%dms)",
                        latency_budget_ms,
                        path.path_id,
                        path.estimated_latency_ms,
                        fallback_path.path_id,
                        fallback_path.estimated_latency_ms,
                    )
                    path = fallback_path
                    tier = fallback_tier
                    break

        selection_reason = f"ADG complexity tier '{tier}' selected"
        if latency_budget_ms:
            selection_reason += f" within {latency_budget_ms}ms latency budget"

        return PathSelectionResult(
            path=path,
            selection_reason=selection_reason,
            profile_hash=profile_hash,
            complexity_tier=tier,
        )

    def generate_with_reasoning(
        self,
        artifact: CompiledPromptArtifact,
        complexity_tier: str = "moderate",
        profile_hash: str | None = None,
        latency_budget_ms: int | None = None,
        provider: ProviderType | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Generate LLM response with dynamic reasoning path selection.

        1. Selects reasoning path based on ADG complexity tier
        2. Verifies artifact signature
        3. Selects provider
        4. Makes LLM call with circuit breaker
        5. Records telemetry with path selection metadata
        """
        # Step 1: Select reasoning path
        path_result = self.select_reasoning_path(
            complexity_tier=complexity_tier,
            profile_hash=profile_hash,
            latency_budget_ms=latency_budget_ms,
        )
        path = path_result.path

        # Step 2: Verify signature
        if self._verify_signatures:
            if not artifact.verify_signature(self._secret_key):
                raise SignatureVerificationError(
                    f"Artifact signature verification failed: {artifact.trace_id}",
                )

        # Step 3: Select provider
        provider_type = provider or self._default_provider
        if provider_type is None:
            raise GatewayError("No provider specified and no default set")

        if provider_type not in self._providers:
            raise GatewayError(f"Provider not registered: {provider_type.name}")

        provider_impl, config = self._providers[provider_type]

        # Step 4: Execute with circuit breaker and reasoning configuration
        start_time = time.time()
        success = False
        error_type = None
        error_message = None
        tokens_out = 0

        try:
            # Apply reasoning configuration to generation
            reasoning_kwargs = {
                "temperature": path.temperature,
                "cot_paths": path.cot_paths if path.use_cot else 0,
                "tot_branches": path.tot_branches if path.use_tot else 0,
                "tot_depth": path.tot_depth if path.use_tot else 0,
                "reflexion_loops": path.max_reflexion_loops if path.use_reflexion else 0,
                "self_consistency_samples": path.self_consistency_samples,
            }
            # Merge with user-provided kwargs (user values take precedence)
            reasoning_kwargs.update(kwargs)

            response = self._circuit_breaker.call(
                provider_impl.generate,
                artifact.final_system_string,
                artifact.final_user_string,
                artifact.allowed_tools_schema,
                **reasoning_kwargs,
            )
            success = True
            tokens_out = response.get("tokens_used", 0)

            # Add reasoning path metadata to response
            response["_reasoning_path"] = {
                "path_id": path.path_id,
                "complexity_tier": path.adg_complexity_tier,
                "cot_used": path.use_cot,
                "tot_used": path.use_tot,
                "reflexion_used": path.use_reflexion,
                "self_consistency": path.self_consistency_samples,
            }
            return response

        except CircuitBreakerOpenError:
            error_type = "circuit_breaker_open"
            error_message = "Circuit breaker is open"
            raise

        except Exception as e:
            error_type = type(e).__name__
            error_message = str(e)
            raise ProviderError(f"Provider call failed: {e}") from e

        finally:
            # Step 5: Record telemetry with reasoning path metadata
            latency_ms = (time.time() - start_time) * 1000
            record = TelemetryRecord.create(
                trace_id=artifact.trace_id,
                provider=provider_type,
                model=config.model,
                tokens_in=artifact.tokens,
                tokens_out=tokens_out,
                latency_ms=latency_ms,
                success=success,
                error_type=error_type,
                error_message=error_message,
                metadata={
                    "slots_used": artifact.slots_used,
                    "signature_present": bool(artifact.signature),
                    "reasoning_path_id": path.path_id,
                    "complexity_tier": path.adg_complexity_tier,
                    "profile_hash": profile_hash,
                    "latency_budget_ms": latency_budget_ms,
                    "selection_reason": path_result.selection_reason,
                },
            )
            self._ledger.record(record)

    def generate(
        self, artifact: CompiledPromptArtifact, provider: ProviderType | None = None, **kwargs,
    ) -> dict[str, Any]:
        """
        Generate LLM response from CompiledPromptArtifact.

        1. Verifies artifact signature
        2. Selects provider
        3. Makes LLM call with circuit breaker
        4. Records telemetry
        """
        # Step 1: Verify signature
        if self._verify_signatures:
            if not artifact.verify_signature(self._secret_key):
                raise SignatureVerificationError(
                    f"Artifact signature verification failed: {artifact.trace_id}",
                )

        # Step 2: Select provider
        provider_type = provider or self._default_provider
        if provider_type is None:
            raise GatewayError("No provider specified and no default set")

        if provider_type not in self._providers:
            raise GatewayError(f"Provider not registered: {provider_type.name}")

        provider_impl, config = self._providers[provider_type]

        # Step 3: Execute with circuit breaker
        start_time = time.time()
        success = False
        error_type = None
        error_message = None
        tokens_out = 0

        try:
            response = self._circuit_breaker.call(
                provider_impl.generate,
                artifact.final_system_string,
                artifact.final_user_string,
                artifact.allowed_tools_schema,
                **kwargs,
            )
            success = True
            tokens_out = response.get("tokens_used", 0)
            return response

        except CircuitBreakerOpenError:
            error_type = "circuit_breaker_open"
            error_message = "Circuit breaker is open"
            raise

        except Exception as e:
            error_type = type(e).__name__
            error_message = str(e)
            raise ProviderError(f"Provider call failed: {e}") from e

        finally:
            # Step 4: Record telemetry
            latency_ms = (time.time() - start_time) * 1000
            record = TelemetryRecord.create(
                trace_id=artifact.trace_id,
                provider=provider_type,
                model=config.model,
                tokens_in=artifact.tokens,
                tokens_out=tokens_out,
                latency_ms=latency_ms,
                success=success,
                error_type=error_type,
                error_message=error_message,
                metadata={
                    "slots_used": artifact.slots_used,
                    "signature_present": bool(artifact.signature),
                },
            )
            self._ledger.record(record)

    def get_telemetry_stats(self) -> dict[str, Any]:
        """Get aggregated telemetry statistics."""
        return self._ledger.get_stats()

    def get_telemetry_records(self, **filters) -> list[TelemetryRecord]:
        """Query telemetry records."""
        return self._ledger.get_records(**filters)

    def verify_artifact(self, artifact: CompiledPromptArtifact) -> bool:
        """Verify CompiledPromptArtifact signature without generating."""
        if not self._verify_signatures:
            return True
        return artifact.verify_signature(self._secret_key)


class _PlaceholderProvider:
    """Placeholder provider for testing."""

    def __init__(self, config: ProviderConfig) -> None:
        self._config = config

    def generate(
        self, system_prompt: str, user_prompt: str, tools_schema: list[dict] | None = None, **kwargs,
    ) -> dict[str, Any]:
        """Placeholder generate - returns mock response."""
        _LOGGER.debug("PlaceholderProvider.generate called")
        return {
            "content": "[Placeholder response]",
            "tokens_used": 10,
            "model": self._config.model,
        }

    def get_token_count(self, text: str) -> int:
        """Rough token estimate."""
        return len(text.split())


# Convenience factory functions
def create_gateway(secret_key: bytes, **kwargs) -> SovereignLLMGateway:
    """Create a new SovereignLLMGateway with defaults."""
    return SovereignLLMGateway(secret_key=secret_key, **kwargs)


def create_openai_gateway(api_key: str, model: str = "gpt-4", **kwargs) -> SovereignLLMGateway:
    """Create gateway with OpenAI provider pre-configured."""
    gateway = create_gateway(**kwargs)
    config = ProviderConfig(
        provider_type=ProviderType.OPENAI,
        api_key=api_key,
        model=model,
    )
    gateway.register_provider(ProviderType.OPENAI, config)
    gateway.set_default_provider(ProviderType.OPENAI)
    return gateway
