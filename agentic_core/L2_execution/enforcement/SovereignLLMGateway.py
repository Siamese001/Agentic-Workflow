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
from dataclasses import dataclass, field
from typing import Any, Literal

from agentic_core.config.core.sovereign_config import get_sovereign_config
from agentic_core.embeddings.embedding_factory import create_embedding_client
from agentic_core.L0_routing.types.guardian_contract import (
    V15HardFailAbort,
    is_v15_enforced,
)
from agentic_core.L0_routing.types.routing_artifact_types import (
    TokenCapArtifact,
    TokenGateResult,
)
from agentic_core.prompt_governance.security.detectors.injection_detector import InjectionDetector
from agentic_core.replay.replay_envelope import ReplayEnvelope
from data.sdks_mcps.client_wrappers import (
    create_anthropic_client,
    create_openai_client,
    create_vertex_client,
)
from system_learning.engines.retrieval_profile import RetrievalProfile

# Agent execution profile enforcement
try:
    from agentic_core.agents.agent_registry import get_profile
except ImportError:
    # Fallback for environments without agent registry
    def get_profile(agent_id: str):
        raise KeyError(f"Agent registry not available: {agent_id}")


Logger = logging.getLogger(__name__)

Provider = Literal["openai", "anthropic", "google"]


@dataclass
class SovereignLLMGateway:
    """
    Unified LLM Gateway - Single point of truth for all LLM operations.
    """

    _instance: SovereignLLMGateway | None = None

    # Metrics
    operation_stats: dict[str, int] = field(
        default_factory=lambda: {
            "openai": 0,
            "anthropic": 0,
            "google": 0,
            "total": 0,
            "errors": 0,
            "fallbacks": 0,
        },
    )

    audit_log: list[dict[str, Any]] = field(default_factory=list)

    # v5.5 Prompt Security - Injection Detector instance
    _injection_detector: InjectionDetector = field(default_factory=InjectionDetector, init=False)

    # Provider clients (lazy-loaded)
    _openai_client: Any = None
    _anthropic_client: Any = None
    _google_client: Any = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

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

    async def route_generation(
        self,
        prompt: str,
        agent_id: str,
        model: str | None = None,
        provider: Provider = "openai",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        fallback_providers: list[Provider] | None = None,
        token_cap: TokenCapArtifact | None = None,
        trace_id: str = "",
        token_budget_limit: int = 0,
        response_schema: Any | None = None,
        **kwargs,
    ) -> dict:
        """
        Route generation for apps_* - the ONLY supported public generation method.

        This method enforces:
        - agent_id is required (from agent_registry.py SSOT)
        - temperature=0.0 for deterministic classes OR normalized to 0.0 in deterministic contexts
        - allowed model selection (Qwen + gemini-2.5-pro) via policy surface
        """
        # Get agent profile to enforce deterministic temperature
        try:
            profile = get_profile(agent_id)
        except KeyError as e:
            raise V15HardFailAbort(f"§AgentProfile: Agent '{agent_id}' not found in registry: {e}")

        # Enforce temperature=0.0 for deterministic classes
        if profile.is_deterministic():
            temperature = 0.0

        # Call the existing generate method with agent_id
        return await self.generate(
            prompt=prompt,
            model=model,
            provider=provider,
            temperature=temperature,
            max_tokens=max_tokens,
            fallback_providers=fallback_providers,
            token_cap=token_cap,
            trace_id=trace_id,
            token_budget_limit=token_budget_limit,
            response_schema=response_schema,
            agent_id=agent_id,
            **kwargs,
        )

    # guardian: allow-magic-config
    async def generate(
        self,
        prompt: str,
        model: str | None = None,
        provider: Provider = "openai",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        fallback_providers: list[Provider] | None = None,
        token_cap: TokenCapArtifact | None = None,
        trace_id: str = "",
        token_budget_limit: int = 0,
        response_schema: Any | None = None,
        agent_id: str | None = None,
        **kwargs,
    ) -> dict:
        # §11.1 — TokenCapArtifact gate (existing V15 enforcement)
        if is_v15_enforced():
            if token_cap is None:
                raise V15HardFailAbort(
                    "§11.1 TokenCapArtifact missing: callers must supply a "
                    "TokenCapArtifact when V15 enforcement is active",
                )
            if token_cap.gate_result != TokenGateResult.ALLOW:
                raise V15HardFailAbort(
                    f"§11.1 TokenCapArtifact denied: gate_result={token_cap.gate_result.value}",
                )

        # Phase 5: Agent execution profile enforcement
        if agent_id is None:
            raise V15HardFailAbort("§AgentProfile: agent_id is required for all gateway calls")

        try:
            profile = get_profile(agent_id)
        except KeyError as e:
            raise V15HardFailAbort(f"§AgentProfile: Agent '{agent_id}' not found in registry: {e}")

        # Enforce execution mode - only LLM_API agents can use gateway
        if not profile.is_llm_allowed():
            raise V15HardFailAbort(
                f"§AgentProfile: Agent '{agent_id}' has execution_mode=DETERMINISTIC, cannot use LLM gateway"
            )

        # Enforce allowed models
        if model and not profile.can_use_model(model):
            raise V15HardFailAbort(
                f"§AgentProfile: Agent '{agent_id}' not allowed to use model '{model}'. Allowed models: {profile.allowed_models}"
            )

        # Model resolution (if not explicitly provided)
        if model is None:
            if provider == "openai":
                model = self.config.openai_model
            elif provider == "anthropic":
                model = self.config.anthropic_model
            elif provider == "google":
                model = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")

        # Enforce allowed models after resolution
        if model and not profile.can_use_model(model):
            raise V15HardFailAbort(
                f"§AgentProfile: Agent '{agent_id}' not allowed to use model '{model}'. Allowed models: {profile.allowed_models}"
            )

        effective_model = model or "unknown"

        # Model injection lock - ensure model resolution from immutable config
        if model and provider == "openai":
            # Verify model is from approved config
            approved_models = [self.config.openai_model]
            if model not in approved_models and not self._is_policy_approved_model(model, provider):
                raise V15HardFailAbort(
                    f"§ModelInjection: Runtime model override detected - '{model}' not in approved config for {provider}"
                )
            # Defensive assertion: model_id resolved from immutable config surface
            if model != self.config.openai_model and not self._is_policy_approved_model(model, provider):
                raise V15HardFailAbort(
                    f"§ModelInjection: Model ID '{model}' not resolved from immutable config surface for {provider}"
                )
        elif model and provider == "anthropic":
            approved_models = [self.config.anthropic_model]
            if model not in approved_models and not self._is_policy_approved_model(model, provider):
                raise V15HardFailAbort(
                    f"§ModelInjection: Runtime model override detected - '{model}' not in approved config for {provider}"
                )
            # Defensive assertion: model_id resolved from immutable config surface
            if model != self.config.anthropic_model and not self._is_policy_approved_model(model, provider):
                raise V15HardFailAbort(
                    f"§ModelInjection: Model ID '{model}' not resolved from immutable config surface for {provider}"
                )

        # §Wave1.8 — Hard token budget enforcement (pre-call gate)
        if trace_id and token_budget_limit > 0:
            from agentic_core.L2_execution.types.token_enforcement_types import (
                TokenBudgetExceeded,
                TokenEnforcementOutcome,
                build_token_enforcement_artifact,
                estimate_prompt_tokens,
                get_token_budget_store,
            )

            store = get_token_budget_store()
            budget_ctx = store.get_or_init(trace_id, token_budget_limit)
            estimated_prompt = estimate_prompt_tokens(prompt)

            if estimated_prompt > budget_ctx.remaining_budget:
                fail_artifact = build_token_enforcement_artifact(
                    trace_id=trace_id,
                    model=effective_model,
                    prompt_tokens=estimated_prompt,
                    completion_tokens=0,
                    remaining_budget=budget_ctx.remaining_budget,
                    hard_limit=budget_ctx.initial_budget,
                    outcome=TokenEnforcementOutcome.FAIL_PRE_CALL,
                )
                self._emit_token_artifact(fail_artifact)
                raise TokenBudgetExceeded(
                    trace_id=trace_id,
                    required=estimated_prompt,
                    remaining=budget_ctx.remaining_budget,
                    phase="pre_call",
                    artifact=fail_artifact,
                )

        # §P1 — Pre-call injection scan (uses instance detector)
        self._injection_detector.scan(prompt)

        # W11: Build Universal Replay Envelope
        retrieval_profile = RetrievalProfile.create_default()
        embedding_client = create_embedding_client(
            provider="openai",
            model=retrieval_profile.primary_embedder_id,
            dimensions=retrieval_profile.embedding_dim,
        )
        embedder_metadata = embedding_client.get_replay_metadata()

        # This is a placeholder for the real hashes that would be computed.
        # In a real scenario, these would be calculated based on the current state.
        replay_envelope = ReplayEnvelope(
            routing_hash="placeholder_routing_hash",
            manifest_hash="placeholder_manifest_hash",
            model_id=effective_model,
            model_version="1.0",  # Placeholder
            temperature=temperature,
            allowed_model_policy_version="1.0",  # Placeholder
            embedder_provider=embedder_metadata.get("provider"),
            embedder_model=embedder_metadata.get("model"),
            embedder_dim=embedder_metadata.get("embedding_dimension"),
            normalization_policy=embedder_metadata.get("normalization_policy"),
            chunking_policy=embedder_metadata.get("chunking_policy"),
            distance_metric=embedder_metadata.get("distance_metric"),
            retrieval_top_k=retrieval_profile.top_k,
            retrieval_similarity_cutoff=retrieval_profile.similarity_cutoff,
            policy_version="1.0",  # Placeholder
            gateway_version="1.0",  # Placeholder
            agent_registry_hash="placeholder_agent_registry_hash",
            code_commit_hash=None,  # Optional
            deterministic_engine_version="1.0",  # Placeholder
        )

        # §Phase3 — vLLM gateway controller seam (local import: no heavy deps at module level)
        _p3_route_to_gemini = False
        _p3_telemetry_dict: dict | None = None
        try:
            from agentic_core.L2_execution.types.vllm_gateway_adapter import (
                VLLMGatewayAdapter,
            )
            from agentic_core.L2_execution.types.vllm_token_budget_types import (
                TaskClass,
            )

            _p3_severity = kwargs.pop("vllm_severity", "low")
            _p3_task_class = kwargs.pop("vllm_task_class", TaskClass.PATCH_SUGGESTION.value)
            _p3_adapter = VLLMGatewayAdapter()
            _p3_decision = _p3_adapter.evaluate(
                prompt=prompt,
                task_class=_p3_task_class,
                severity=_p3_severity,
            )
            _p3_telemetry_dict = _p3_decision.telemetry.as_dict()
            _p3_route_to_gemini = _p3_decision.route_to_gemini
            if _p3_decision.local_request is not None:
                max_tokens = _p3_decision.local_request.max_tokens
                temperature = _p3_decision.local_request.temperature
            Logger.debug("[Phase3] vllm_gateway_adapter decision: %s", _p3_telemetry_dict)
        except Exception as _p3_exc:  # guardian: allow-silent-swallow
            Logger.warning("[Phase3] vllm_gateway_adapter seam failed (non-fatal): %s", _p3_exc)

        if _p3_route_to_gemini:
            provider = "google"
            fallback_providers = []

        fallback_providers = fallback_providers or ["anthropic", "google"]
        providers_to_try = [provider] + [p for p in fallback_providers if p != provider]

        last_error = None
        for current_provider in providers_to_try:
            start = time.time()
            try:
                current_model = model
                if current_provider != provider:
                    if current_provider == "anthropic":
                        current_model = self.config.anthropic_model
                    elif current_provider == "google":
                        current_model = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")
                    elif current_provider == "openai":
                        current_model = self.config.openai_model

                result = await self._call_provider(
                    current_provider,
                    prompt,
                    current_model,
                    temperature,
                    max_tokens,
                    **kwargs,
                )

                latency = (time.time() - start) * 1000
                self._audit(current_provider, str(current_model), True, latency, result.get("tokens", 0))

                if current_provider != provider:
                    self.operation_stats["fallbacks"] += 1
                    Logger.info(f"[LLM Gateway] Fallback to {current_provider} succeeded")

                # §Wave1.8 — Hard token budget enforcement (post-call gate)
                if trace_id and token_budget_limit > 0:
                    from agentic_core.L2_execution.types.token_enforcement_types import (
                        TokenBudgetExceeded,
                        TokenEnforcementOutcome,
                        build_token_enforcement_artifact,
                        estimate_prompt_tokens,
                        get_token_budget_store,
                    )

                    store = get_token_budget_store()
                    budget_ctx = store.get_or_init(trace_id, token_budget_limit)
                    total_tokens = result.get("tokens", 0)
                    prompt_tokens = result.get("prompt_tokens", total_tokens // 2)
                    completion_tokens = result.get("completion_tokens", total_tokens - prompt_tokens)
                    tokens_used = prompt_tokens + completion_tokens
                    new_remaining = store.consume(trace_id, tokens_used)

                    if new_remaining < 0:
                        fail_artifact = build_token_enforcement_artifact(
                            trace_id=trace_id,
                            model=effective_model,
                            prompt_tokens=prompt_tokens,
                            completion_tokens=completion_tokens,
                            remaining_budget=new_remaining,
                            hard_limit=budget_ctx.initial_budget,
                            outcome=TokenEnforcementOutcome.FAIL_POST_CALL,
                        )
                        self._emit_token_artifact(fail_artifact)
                        raise TokenBudgetExceeded(
                            trace_id=trace_id,
                            required=tokens_used,
                            remaining=new_remaining,
                            phase="post_call",
                            artifact=fail_artifact,
                        )

                    pass_artifact = build_token_enforcement_artifact(
                        trace_id=trace_id,
                        model=effective_model,
                        prompt_tokens=prompt_tokens,
                        completion_tokens=completion_tokens,
                        remaining_budget=new_remaining,
                        hard_limit=budget_ctx.initial_budget,
                        outcome=TokenEnforcementOutcome.PASS,
                    )
                    self._emit_token_artifact(pass_artifact)

                # §P2 — Bounded schema validation retry (max 1)
                if response_schema is not None:
                    from agentic_core.prompt_governance.security.validators.output_schema_validator import (
                        validate_against_schema,
                    )

                    content = result.get("content", "")
                    ok, code, details = validate_against_schema(content, response_schema)
                    if not ok:
                        # First attempt failed — retry once with schema hint
                        retry_prompt = (
                            prompt
                            + "\n\nReturn ONLY valid JSON matching this schema:\n"
                            + str(response_schema)
                            + "\nDo not add extra keys. Do not include explanations."
                        )
                        retry_result = await self._call_provider(
                            current_provider,
                            retry_prompt,
                            current_model,
                            temperature,
                            max_tokens,
                            **kwargs,
                        )
                        retry_content = retry_result.get("content", "")
                        ok2, code2, details2 = validate_against_schema(retry_content, response_schema)
                        if not ok2:
                            from agentic_core.runtime.exceptions.SovereignError import (
                                SecurityViolationError,
                            )

                            raise SecurityViolationError(
                                message=(f"§P2 Output schema validation failed after retry: code={code2}"),
                                violation_type="SCHEMA_VALIDATION_FAILED",
                            )
                        result = retry_result

                # §P3 — Post-call output injection scan (warn-mode)
                _response_content = result.get("content")
                result["replay_envelope"] = replay_envelope.to_canonical_json()

                if _response_content:
                    from agentic_core.prompt_governance.security.utils import (
                        injection_scan_util as _isu,
                    )
                    from agentic_core.runtime.exceptions.SovereignError import (
                        SecurityViolationError as _SVE_P3,
                    )

                    try:
                        _isu.scan_untrusted_text(_response_content, source="llm_response_output")
                    # guardian: allow-silent-swallow
                    except _SVE_P3 as _p3_sve:
                        Logger.warning(
                            "[LLM Gateway] Output injection detected: %s",
                            _p3_sve,
                        )
                    except Exception as _p3_exc:
                        Logger.exception(
                            "[LLM Gateway] Output scan failed (swallowed): %s",
                            _p3_exc,
                        )
                        raise

                return result

            # guardian: allow-silent-swallow
            except Exception as e:
                from agentic_core.L2_execution.types.token_enforcement_types import (
                    TokenBudgetExceeded,
                )
                from agentic_core.runtime.exceptions.SovereignError import (
                    SecurityViolationError as _SVE,
                )

                if isinstance(e, (TokenBudgetExceeded, _SVE)):
                    raise
                latency = (time.time() - start) * 1000
                self._audit(current_provider, str(model), False, latency)
                last_error = e
                Logger.warning(f"[LLM Gateway] {current_provider} failed: {e}")
                continue

        Logger.error(f"[LLM Gateway] All providers failed. Last Error: {last_error}")
        raise RuntimeError(f"All LLM providers failed. Last error: {last_error}")

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


_llm_gateway_instance = None


def get_llm_gateway() -> SovereignLLMGateway:
    global _llm_gateway_instance
    if _llm_gateway_instance is None:
        _llm_gateway_instance = SovereignLLMGateway()
    return _llm_gateway_instance
