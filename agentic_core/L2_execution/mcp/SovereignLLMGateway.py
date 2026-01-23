"""
SovereignLLMGateway - Unified LLM Operations Gateway

[PHASE 4 MIGRATION] Consolidates all LLM provider operations:
- OpenAI (GPT-4, GPT-4o, o1)
- Anthropic (Claude 3.5)
- Google (Gemini)
- Centralized audit logging (with FIFO rotation to prevent OOM)
- Unified retry/fallback strategy
- Provider health monitoring
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Literal
import time
import logging
import os

from agentic_core.config.SovereignConfigManager import get_sovereign_config

Logger = logging.getLogger(__name__)

Provider = Literal["openai", "anthropic", "google"]


@dataclass
class SovereignLLMGateway:
    """
    Unified LLM Gateway - Single point of truth for all LLM operations.

    [PHASE 4 MIGRATION] Absorbed from:
    - inference_engine.py (12 classes)
    - llm_engine.py
    - UnifiedModelRouterAgent.py
    - runtime_shared_multi_provider_clients.py

    [PHASE 8] NOT an agent - utility singleton to avoid circular imports.
    """

    _instance: SovereignLLMGateway | None = None

    # [PHASE 6] Configuration now managed by SovereignConfigManager

    # Metrics
    operation_stats: dict[str, int] = field(
        default_factory=lambda: {
            "openai": 0,
            "anthropic": 0,
            "google": 0,
            "total": 0,
            "errors": 0,
            "fallbacks": 0,
        }
    )

    audit_log: list[dict[str, Any]] = field(default_factory=list)

    # Provider clients (lazy-loaded)
    _openai_client: Any = None
    _anthropic_client: Any = None
    _google_client: Any = None

    def __new__(cls):
        """Singleton constructor."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def reset_instance(cls):
        """[TESTING ONLY] Reset the singleton instance to allow fresh state."""
        cls._instance = None

    @property
    def config(self):
        """[PHASE 6] Access centralized config."""
        return get_sovereign_config()

    def _audit(
        self, provider: str, model: str, success: bool, latency_ms: float, tokens: int = 0
    ) -> None:
        """
        [PHASE 4] Record LLM operation to audit plane.

        CRITICAL FIX: Implements FIFO rotation. If log exceeds MAX_AUDIT_LOG_SIZE,
        oldest entries are removed to prevent Memory Leaks in long-running agents.
        """
        # [PHASE 6] Dynamic limit from config
        limit = self.config.max_audit_log_size

        if len(self.audit_log) >= limit:
            # Remove oldest 10% to reduce frequent popping overhead
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
            }
        )

        self.operation_stats["total"] += 1
        if not success:
            self.operation_stats["errors"] += 1
        else:
            self.operation_stats[provider] = self.operation_stats.get(provider, 0) + 1

    @property
    def openai(self):
        """Lazy-load OpenAI client."""
        if self._openai_client is None:
            try:
                import openai

                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    raise ValueError("OPENAI_API_KEY not found in environment")
                self._openai_client = openai.OpenAI(api_key=api_key)
            except Exception as e:
                Logger.warning(f"OpenAI client init failed: {e}")
                raise
        return self._openai_client

    @property
    def anthropic(self):
        """Lazy-load Anthropic client."""
        if self._anthropic_client is None:
            try:
                import anthropic

                api_key = os.getenv("ANTHROPIC_API_KEY")
                if not api_key:
                    raise ValueError("ANTHROPIC_API_KEY not found in environment")
                self._anthropic_client = anthropic.Anthropic(api_key=api_key)
            except Exception as e:
                Logger.warning(f"Anthropic client init failed: {e}")
                raise
        return self._anthropic_client

    @property
    def google(self):
        """Lazy-load Google client."""
        if self._google_client is None:
            try:
                import google.generativeai as genai

                api_key = os.getenv("GOOGLE_API_KEY")
                if not api_key:
                    raise ValueError("GOOGLE_API_KEY not found in environment")
                genai.configure(api_key=api_key)
                self._google_client = genai
            except Exception as e:
                Logger.warning(f"Google client init failed: {e}")
                raise
        return self._google_client

    async def generate(
        self,
        prompt: str,
        model: str | None = None,
        provider: Provider = "openai",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        fallback_providers: list[Provider] | None = None,
        **kwargs,
    ) -> dict:
        """
        Generate LLM response with automatic fallback.
        [PHASE 4] Unified interface for all providers.
        """
        # [PHASE 6] Resolve default model from ConfigManager
        if model is None:
            if provider == "openai":
                model = self.config.openai_model
            elif provider == "anthropic":
                model = self.config.anthropic_model
            elif provider == "google":
                model = self.config.google_model

        fallback_providers = fallback_providers or ["anthropic", "google"]
        providers_to_try = [provider] + [p for p in fallback_providers if p != provider]

        last_error = None

        for current_provider in providers_to_try:
            start = time.time()
            try:
                # Basic model mapping for fallback scenarios
                current_model = model
                if current_provider != provider:
                    # [PHASE 6] Dynamic defaults for fallback
                    if current_provider == "anthropic":
                        current_model = self.config.anthropic_model
                    elif current_provider == "google":
                        current_model = self.config.google_model
                    elif current_provider == "openai":
                        current_model = self.config.openai_model

                result = await self._call_provider(
                    current_provider, prompt, current_model, temperature, max_tokens, **kwargs
                )

                latency = (time.time() - start) * 1000
                self._audit(
                    current_provider, str(current_model), True, latency, result.get("tokens", 0)
                )

                if current_provider != provider:
                    self.operation_stats["fallbacks"] += 1
                    Logger.info(f"[LLM Gateway] Fallback to {current_provider} succeeded")

                return result

            except Exception as e:
                latency = (time.time() - start) * 1000
                self._audit(current_provider, str(model), False, latency)
                last_error = e
                Logger.warning(f"[LLM Gateway] {current_provider} failed: {e}")
                continue

        Logger.error(f"[LLM Gateway] All providers failed. Last Error: {last_error}")
        raise RuntimeError(f"All LLM providers failed. Last error: {last_error}")

    async def _call_provider(
        self,
        provider: Provider,
        prompt: str,
        model: str,
        temperature: float,
        max_tokens: int,
        **kwargs,
    ) -> dict:
        """Route to specific provider implementation."""
        if provider == "openai":
            return await self._call_openai(prompt, model, temperature, max_tokens, **kwargs)
        elif provider == "anthropic":
            return await self._call_anthropic(prompt, model, temperature, max_tokens, **kwargs)
        elif provider == "google":
            return await self._call_google(prompt, model, temperature, max_tokens, **kwargs)
        else:
            raise ValueError(f"Unknown provider: {provider}")

    async def _call_openai(
        self, prompt: str, model: str, temperature: float, max_tokens: int, **kwargs
    ) -> dict:
        """Call OpenAI API."""
        # Note: Using synchronous client wrapped in async context in real usage or upgrade to AsyncOpenAI
        response = self.openai.chat.completions.create(
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
        self, prompt: str, model: str, temperature: float, max_tokens: int, **kwargs
    ) -> dict:
        """Call Anthropic API."""
        response = self.anthropic.messages.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )
        return {
            "content": response.content[0].text,
            "tokens": response.usage.input_tokens + response.usage.output_tokens
            if response.usage
            else 0,
            "provider": "anthropic",
            "model": model,
        }

    async def _call_google(
        self, prompt: str, model: str, temperature: float, max_tokens: int, **kwargs
    ) -> dict:
        """Call Google Gemini API."""
        gen_model = self.google.GenerativeModel(model)
        response = gen_model.generate_content(
            prompt,
            generation_config=self.google.types.GenerationConfig(
                temperature=temperature, max_output_tokens=max_tokens
            ),
        )
        return {
            "content": response.text,
            "tokens": 0,  # Gemini doesn't always return token count
            "provider": "google",
            "model": model,
        }


# Singleton accessor
_llm_gateway_instance = None


def get_llm_gateway() -> SovereignLLMGateway:
    """Get or create the global LLM gateway."""
    return SovereignLLMGateway()
