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
    """Adapter wrapping the existing GeminiJudge for the new JudgeProvider protocol.

    Delegates to the GeminiJudge's LLM gateway for actual API calls.
    Parses JSON responses and extracts criteria scores.
    """

    MODEL_ID = "gemini-1.5-flash"

    def __init__(self, gemini_client: Any = None) -> None:
        self._client = gemini_client

    @property
    def provider_id(self) -> str:
        return "gemini"

    @property
    def cost_per_eval(self) -> float:
        return 0.001

    def _get_client(self) -> Any:
        if self._client is not None:
            return self._client
        try:
            from agentic_core.L2_execution.enforcement.SovereignLLMGateway import (
                get_llm_gateway,
            )

            return get_llm_gateway()
        except Exception as exc:
            raise RuntimeError("GeminiJudgeProvider: no LLM client available") from exc

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
        raw = client.generate(prompt=prompt, temperature=0.0)
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
        criteria_scores = {
            k: float(v) for k, v in data.items() if isinstance(v, (int, float))
        }

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
            "model": self.MODEL_ID,
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
    """Create a registry with the NullJudgeProvider pre-registered.

    GeminiJudgeProvider is registered but not default (requires API key).
    """
    registry = JudgeProviderRegistry()
    registry.register(NullJudgeProvider(), default=True)
    return registry


__all__ = [
    "GeminiJudgeProvider",
    "JudgeProviderRegistry",
    "NullJudgeProvider",
    "create_default_registry",
]
