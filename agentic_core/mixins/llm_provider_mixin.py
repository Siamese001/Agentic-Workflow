"""
LLMProviderMixin - Unified LLM Access for Agents

[PHASE 4 MIGRATION] Provides single interface to all LLM providers.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    from agentic_core.L2_execution.enforcement.SovereignLLMGateway import SovereignLLMGateway
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

Provider = Literal["openai", "anthropic", "google"]


def _get_llm_gateway():
    from agentic_core.L2_execution.enforcement.SovereignLLMGateway import get_llm_gateway

    return get_llm_gateway()


class LLMProviderMixin:
    """
    Mixin providing unified LLM gateway access.

    [PHASE 4 MIGRATION] Replaces direct SDK imports.

    Usage:
        class MyAgent(LLMProviderMixin, SovereignBaseAgent):
            async def process(self, query: str) -> str:
                response = await self.llm_generate(query)
                return response["content"]
    """

    _llm_gateway: SovereignLLMGateway | None = None

    @property
    def llm_gateway(self) -> SovereignLLMGateway:
        """Lazy-load LLM gateway singleton."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "LLMProviderMixin.llm_gateway")

        if self._llm_gateway is None:
            self._llm_gateway = _get_llm_gateway()
        return self._llm_gateway

    async def llm_generate(
        self,
        prompt: str,
        model: str | None = None,
        provider: Provider = "openai",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate LLM response through gateway."""
        return await self.llm_gateway.generate(prompt, model=model, provider=provider, **kwargs)

    async def llm_generate_with_fallback(
        self,
        prompt: str,
        model: str | None = None,
        fallback_providers: list[Provider] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate with automatic provider fallback."""
        return await self.llm_gateway.generate(
            prompt,
            model=model,
            fallback_providers=fallback_providers,
            **kwargs,
        )
