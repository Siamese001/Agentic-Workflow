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

import json
import logging
import os
import re
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
        self._model = model or os.getenv("GEMINI_MODEL", self.DEFAULT_MODEL)
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
        # guardian: allow-layer-violation -- infrastructure SDK access required for LLM provider, no agentic_core alternative exists
        from infrastructure.sdks_mcps import create_vertex_client

        try:
            genai = create_vertex_client()
        except (ImportError, ValueError) as exc:
            raise RuntimeError(
                "GeminiJudgeProvider: google-genai package not installed or GOOGLE_API_KEY missing.",
            ) from exc

        self._configured = True
        return genai.GenerativeModel(self._model)

    @staticmethod
    def _clean(raw: str) -> str:
        return re.sub(r"```(?:json)?|```", "", raw).strip()

    @staticmethod
    def _parse(raw: str) -> dict[str, Any]:
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return json.loads(GeminiJudgeProvider._clean(raw))

    async def judge(self, prompt: str, rubric_id: str) -> dict[str, Any]:
        client = self._get_client()
        try:
            response = client.generate_content(
                prompt,
                generation_config={"temperature": 0.0},
            )
            raw = response.text
        except Exception as exc:
            _log.warning(
                "[GeminiJudgeProvider] Gemini API error for %s: %s",
                rubric_id,
                exc,
            )
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


def create_default_registry() -> JudgeProviderRegistry:
    """Create a registry with NullJudgeProvider and optional GeminiJudgeProvider.

    NullJudgeProvider is always registered as the default fallback.
    GeminiJudgeProvider is registered and set as default when
    ``GEMINI_API_KEY`` or ``GOOGLE_API_KEY`` is present.
    """
    registry = JudgeProviderRegistry()
    registry.register(NullJudgeProvider(), default=True)

    if os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"):
        try:
            from infrastructure.sdks_mcps import create_vertex_client

            genai = create_vertex_client()
            default_model = os.getenv("GEMINI_MODEL", GeminiJudgeProvider.DEFAULT_MODEL)
            gemini_model = genai.GenerativeModel(default_model)
            gemini = GeminiJudgeProvider(gemini_client=gemini_model)
            registry.register(gemini, default=True)
            _log.info("[create_default_registry] Gemini provider auto-registered (API key found)")
        except (RuntimeError, ValueError, OSError, ImportError) as exc:
            _log.warning("[create_default_registry] Gemini registration failed: %s", exc)

    return registry


__all__ = [
    "GeminiJudgeProvider",
    "JudgeProviderRegistry",
    "NullJudgeProvider",
    "create_default_registry",
]
