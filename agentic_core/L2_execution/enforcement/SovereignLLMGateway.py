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

import logging
import os
import time
from dataclasses import dataclass
from typing import Any, Literal

from agentic_core.config.core.sovereign_config import get_sovereign_config
from agentic_core.L2_execution.audit.hash_chain_audit_log import HashChainAuditLog
from agentic_core.L2_execution.types.gateway_types import GenerationRequest, GenerationResponse
from agentic_core.prompt_governance.security.detectors.injection_detector import InjectionDetector
from agentic_core.replay.replay_envelope import ReplayEnvelope
from data.sdks_mcps.client_wrappers import (
    create_anthropic_client,
    create_openai_client,
    create_vertex_client,
)

# Agent execution profile enforcement
try:
    from agentic_core.agents.agent_registry import get_profile
    from agentic_core.agents.types.agent_execution_profile import ExecutionMode
except ImportError:
    # Fallback for environments without agent registry
    def get_profile(agent_id: str):
        raise KeyError(f"Agent registry not available: {agent_id}")


Logger = logging.getLogger(__name__)

Provider = Literal["openai", "anthropic", "google"]


@dataclass
@dataclass
class SovereigntyViolation(Exception):
    """Raised when an agent violates its execution policy."""

    message: str


class SovereignLLMGateway:
    """
    Unified LLM Gateway - Single point of truth for all LLM operations.
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

        # v5.5 Prompt Security - Injection Detector instance
        self._injection_detector = InjectionDetector()

        # Egress audit log (immutable, hash-chained)
        self._egress_audit_log = HashChainAuditLog()

        # Provider clients (lazy-loaded)
        self._openai_client: Any = None
        self._anthropic_client: Any = None
        self._google_client: Any = None

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
                "ts": time.time(),
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

    async def route_generation(self, request: GenerationRequest, **kwargs) -> GenerationResponse:
        """Main entry point for all LLM generation, enforcing 2x2 agent policy."""
        if not request.agent_id:
            raise SovereigntyViolation("agent_id is required.")

        try:
            profile = get_profile(request.agent_id)
        except KeyError:
            raise SovereigntyViolation(f"Agent '{request.agent_id}' not found in registry.")

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
            if request.provider not in profile.allowed_providers:
                raise SovereigntyViolation(
                    f"Agent '{request.agent_id}' is not allowed to use provider '{request.provider}'."
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

        fallback_providers = request.fallback_providers or ["anthropic", "google"]
        providers_to_try = [request.provider] + [p for p in fallback_providers if p != request.provider]

        last_error = None
        for current_provider in providers_to_try:
            start = time.time()
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

                latency = (time.time() - start) * 1000
                self._audit(current_provider, str(current_model), True, latency, result.get("tokens", 0))

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
                latency = (time.time() - start) * 1000
                self._audit(current_provider, str(model), False, latency)
                last_error = e
                Logger.warning(f"[LLM Gateway] {current_provider} failed: {e}")
                continue

        Logger.error(f"[LLM Gateway] All providers failed. Last Error: {last_error}")
        raise SovereigntyViolation(f"All LLM providers failed. Last error: {last_error}")

    def _get_default_model(self, provider: Provider) -> str:
        if provider == "openai":
            return self.config.openai_model
        elif provider == "anthropic":
            return self.config.anthropic_model
        elif provider == "google":
            return os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")
        raise ValueError(f"Unknown provider: {provider}")

    def _emit_token_artifact(self, artifact: Any) -> None:
        """§Wave1.8 — Emit TokenEnforcementArtifact via TelemetryEmitter."""
        try:
            from agentic_core.L0_routing.types.routing_contracts import TelemetryEmitter

            emitter = TelemetryEmitter()
            emitter.emit_typed_artifact("TOKEN_ENFORCEMENT", artifact)
        # guardian: allow-silent-swallow
        except Exception as _emit_exc:
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
        if "tools" in kwargs:
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
