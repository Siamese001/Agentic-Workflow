"""Judge Provider Registry — manages LLM judge backends.

Provides:
- ``JudgeProviderRegistry``  — singleton registry for LLM judge providers
- ``GeminiJudgeProvider``    — adapter wrapping existing GeminiJudge
- ``NullJudgeProvider``      — deterministic stub for CI/testing

The registry maps provider IDs to JudgeProvider instances, allowing
the orchestrator to select backends by ID or capability.

Usage::

    registry = JudgeProviderRegistry()
    registry.register(NullJudgeProvider())
    provider = registry.get("null")
    result = await provider.judge("prompt text", "GOV-001")
"""

from __future__ import annotations

import importlib
import json
import logging
import os
import re
from typing import cast
from typing import Any

from agentic_core.evaluation.judges.types import JudgeProvider

_log = logging.getLogger(__name__)


class NullJudgeProvider:
    """Deterministic stub provider for CI — no LLM calls.

    Always returns a fixed score dict matching the expected
    judge response format. Useful for testing the full pipeline
    without API keys.
    """

    @property
    def provider_id(self) -> str:
        return "null"

    @property
    def cost_per_eval(self) -> float:
        return 0.0

    async def judge(self, prompt: str, rubric_id: str) -> dict[str, Any]:
        return {
            "score": 0.5,
            "reasoning": "NullJudgeProvider: deterministic stub — no LLM call made",
            "rubric_id": rubric_id,
            "provider": self.provider_id,
            "criteria_scores": {},
        }


class GeminiJudgeProvider:
    """Direct Gemini SDK provider for the JudgeProvider protocol.

    Uses ``google.generativeai`` directly with ``GEMINI_API_KEY`` or
    ``GOOGLE_API_KEY``. Bypasses SovereignLLMGateway (which requires
    agent_id and async routing not needed for judge evaluation).

    Supports model override via ``GEMINI_MODEL`` env var.
    Temperature is forced to 0.0 for maximum determinism.
    """

    DEFAULT_MODEL = "gemini-2.5-flash"

    def __init__(self, gemini_client: Any = None, model: str | None = None) -> None:
        self._client = gemini_client
        env_model = os.getenv("GEMINI_MODEL")
        self._model = model or env_model or self.DEFAULT_MODEL
        self._configured = False

    @property
    def provider_id(self) -> str:
        return "gemini"

    @property
    def cost_per_eval(self) -> float:
        return 0.001

    @property
    def model_id(self) -> str:
        return self._model

    def _get_client(self) -> Any:
        if self._client is not None:
            return self._client

        try:
            client = importlib.import_module("infrastructure.sdks_mcps").create_gemini_model(self._model)
        except (ImportError, ValueError) as exc:
            raise RuntimeError(
                "GeminiJudgeProvider: google-genai package not installed or GOOGLE_API_KEY missing.",
            ) from exc

        self._configured = True
        return client

    @staticmethod
    def _clean(raw: str) -> str:
        return re.sub(r"```(?:json)?|```", "", raw).strip()

    @staticmethod
    def _parse(raw: str) -> dict[str, Any]:
        try:
            return cast(dict[str, Any], json.loads(raw))
        except json.JSONDecodeError:
            return cast(dict[str, Any], json.loads(GeminiJudgeProvider._clean(raw)))

    async def judge(self, prompt: str, rubric_id: str) -> dict[str, Any]:
        client = self._get_client()
        try:
            response = client.generate_content(
                prompt,
                generation_config={"temperature": 0.0},
            )
            raw = response.text
        except (
            AttributeError,
            RuntimeError,
            TypeError,
            ValueError,
        ):  # guardian: allow-double-logging -- Gemini API error logged before re-raise for provider-judge diagnostics
            raise

        try:
            data = self._parse(raw)
        except (json.JSONDecodeError, ValueError) as exc:
            _log.warning(
                "[GeminiJudgeProvider] Failed to parse response for %s: %s",
                rubric_id,
                exc,
            )
            return {
                "score": 0.0,
                "reasoning": f"Parse error: {exc}",
                "rubric_id": rubric_id,
                "provider": self.provider_id,
                "error": str(exc),
                "raw_response": raw[:500],
            }

        # Extract reasoning
        reasoning = data.pop("reasoning", "")

        # Remaining keys are criteria scores
        criteria_scores = {k: float(v) for k, v in data.items() if isinstance(v, (int, float))}

        # Compute aggregate score as mean of criteria
        if criteria_scores:
            score = sum(criteria_scores.values()) / len(criteria_scores)
        else:
            score = 0.0

        return {
            "score": round(score, 4),
            "reasoning": reasoning,
            "rubric_id": rubric_id,
            "provider": self.provider_id,
            "criteria_scores": criteria_scores,
            "model": self._model,
        }


class JudgeProviderRegistry:
    """Registry managing available LLM judge providers.

    Providers are registered by their ``provider_id`` property.
    The registry supports lookup, listing, and default provider selection.
    """

    def __init__(self) -> None:
        self._providers: dict[str, JudgeProvider] = {}
        self._default_id: str = ""

    def register(self, provider: JudgeProvider, default: bool = False) -> None:
        """Register a judge provider.

        Args:
            provider: Instance satisfying the JudgeProvider protocol.
            default: If True, set as the default provider.
        """
        pid = provider.provider_id
        self._providers[pid] = provider
        if default or not self._default_id:
            self._default_id = pid
        _log.info("[JudgeProviderRegistry] Registered provider: %s", pid)

    def get(self, provider_id: str) -> JudgeProvider | None:
        """Get a provider by ID."""
        return self._providers.get(provider_id)

    @property
    def default(self) -> JudgeProvider | None:
        """Get the default provider."""
        return self._providers.get(self._default_id)

    @property
    def provider_ids(self) -> list[str]:
        """List all registered provider IDs."""
        return list(self._providers.keys())

    def set_default(self, provider_id: str) -> bool:
        """Set the default provider by ID. Returns False if not found."""
        if provider_id in self._providers:
            self._default_id = provider_id
            return True
        return False

    def summary(self) -> dict[str, Any]:
        """Summary of registered providers."""
        return {
            "providers": [
                {
                    "provider_id": pid,
                    "cost_per_eval": p.cost_per_eval,
                    "is_default": pid == self._default_id,
                }
                for pid, p in self._providers.items()
            ],
            "default": self._default_id,
            "count": len(self._providers),
        }


def create_default_registry(*, prefer_local: bool = True) -> JudgeProviderRegistry:
    """Create a registry with NullJudgeProvider and optional cloud/local judges.

    Registration order (each is only default when the prior slot is empty):
      1. ``NullJudgeProvider`` — always present as safe fallback.
      2. ``QwenJudgeProvider`` — registered when ``JUDGE_PROVIDER=qwen`` or
         when ``VLLM_BASE_URL`` is explicitly set AND ``JUDGE_PROVIDER`` is
         not explicitly set to another backend. Zero marginal cost — preferred
         default when available. Wave A (qwen-adoption-waves-a7f3c2).
      3. ``GeminiJudgeProvider`` — registered when ``GEMINI_API_KEY`` /
         ``GOOGLE_API_KEY`` is present. Becomes default if Qwen did not.

    An explicit ``JUDGE_PROVIDER`` env var (``null`` / ``qwen`` / ``gemini``)
    forces that provider as default if registered.

    Args:
        prefer_local: When ``True`` (the default, set by the 2026-05-02
            eval/control gap-closure audit), the locally-hosted Qwen vLLM
            provider claims the default slot whenever it is registered AND
            ``JUDGE_PROVIDER`` is not an explicit external override. This
            makes the cheapest-safe local backend the production default,
            with external providers reserved for escalation. Set to
            ``False`` to restore the prior Gemini-wins-on-API-key behavior
            for callers that need the legacy registration ordering.
    """
    registry = JudgeProviderRegistry()
    registry.register(NullJudgeProvider(), default=True)

    judge_provider_override = (os.getenv("JUDGE_PROVIDER") or "").strip().lower()

    # Wave A: Qwen registration. Opt-in via JUDGE_PROVIDER=qwen OR by setting
    # VLLM_BASE_URL explicitly (local vLLM is intended to be used).
    qwen_should_register = judge_provider_override == "qwen" or (
        os.getenv("VLLM_BASE_URL")
        and judge_provider_override != "gemini"
        and judge_provider_override != "null"
    )
    qwen_registered = False
    if qwen_should_register:
        try:
            from agentic_core.evaluation.judges.qwen_judge_provider import (  # noqa: PLC0415  guardian: allow-log-and-swallow -- optional Qwen backend: registration failure is non-fatal, registry still returns with other providers (Gemini/null)
                QwenJudgeProvider,
            )

            qwen = QwenJudgeProvider()
            # Qwen claims default when explicitly chosen OR when prefer_local
            # is True and JUDGE_PROVIDER is not an explicit external override.
            # The prior behavior (default only when JUDGE_PROVIDER==qwen) is
            # preserved when prefer_local=False.
            qwen_default = judge_provider_override == "qwen" or (
                prefer_local and judge_provider_override not in ("gemini", "null")
            )
            registry.register(qwen, default=qwen_default)
            qwen_registered = True
            _log.info(
                "[create_default_registry] Qwen judge provider auto-registered (default=%s)",
                qwen_default,
            )
        except (
            RuntimeError,
            ValueError,
            OSError,
            ImportError,
        ) as exc:  # guardian: allow-log-and-swallow -- optional backend; registry must still return
            _log.warning("[create_default_registry] Qwen registration failed: %s", exc)

    if os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"):
        try:
            default_model = os.getenv("GEMINI_MODEL", GeminiJudgeProvider.DEFAULT_MODEL)
            gemini_model = importlib.import_module("infrastructure.sdks_mcps").create_gemini_model(
                default_model
            )
            gemini = GeminiJudgeProvider(gemini_client=gemini_model)
            # Gemini claims default only when (a) explicitly chosen, OR
            # (b) JUDGE_PROVIDER is empty AND Qwen did not already claim
            # the default slot. The prefer_local=True path keeps Qwen
            # in the default slot when both backends are registered.
            if judge_provider_override == "gemini":
                gemini_default = True
            elif prefer_local and qwen_registered:
                gemini_default = False
            else:
                gemini_default = judge_provider_override in ("", "gemini")
            registry.register(gemini, default=gemini_default)
            _log.info(
                "[create_default_registry] Gemini provider auto-registered (default=%s)",
                gemini_default,
            )
        except (
            RuntimeError,
            ValueError,
            OSError,
            ImportError,
        ) as exc:  # guardian: allow-log-and-swallow  -- ADG-burn: log_and_swallow
            _log.warning("[create_default_registry] Gemini registration failed: %s", exc)

    # Final explicit override: if JUDGE_PROVIDER was set and the provider is
    # registered, force it as default regardless of registration order.
    if judge_provider_override and judge_provider_override in registry.provider_ids:
        registry.set_default(judge_provider_override)

    return registry


__all__ = [
    "GeminiJudgeProvider",
    "JudgeProviderRegistry",
    "NullJudgeProvider",
    "create_default_registry",
]
