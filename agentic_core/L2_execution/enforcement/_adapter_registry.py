"""Provider adapter registry — W2 RH2.5.

Single point of lookup from ``ProviderType`` to ``ProviderMessageAdapter``.
Gateway calls ``get_adapter(provider_type)`` when ``PROMPT_ADAPTER_V2=1`` is
set; otherwise legacy pass-through is used.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from agentic_core.L2_execution.enforcement._adapter_anthropic import (
    AnthropicMessageAdapter,
)
from agentic_core.L2_execution.enforcement._adapter_gemini import (
    GeminiMessageAdapter,
)
from agentic_core.L2_execution.enforcement._adapter_openai import (
    OpenAIMessageAdapter,
)
from agentic_core.L2_execution.enforcement._adapter_openai_oseries import (
    OSeriesMessageAdapter,
)

if TYPE_CHECKING:
    from agentic_core.L2_execution.enforcement.provider_adapter import (
        ProviderMessageAdapter,
    )
    from agentic_core.L2_execution.enforcement.SovereignLLMGateway import (
        ProviderType,
    )


_REGISTRY: dict[str, "ProviderMessageAdapter"] = {
    "OPENAI": OpenAIMessageAdapter(),
    "ANTHROPIC": AnthropicMessageAdapter(),
    "AZURE_OPENAI": OpenAIMessageAdapter(),  # Azure uses OpenAI-compatible wire format
    # W8: dedicated Gemini adapter for Vertex AI (was OpenAI fallback pre-W8).
    "VERTEX_AI": GeminiMessageAdapter(),
    # LOCAL_VLLM defaults to OpenAI-style until a dedicated adapter is warranted.
    "LOCAL_VLLM": OpenAIMessageAdapter(),
}


def get_adapter(provider_type: "ProviderType") -> "ProviderMessageAdapter":
    """Return the adapter for ``provider_type``.

    Falls back to the OpenAI adapter for unknown providers so the gateway
    never crashes on a missing adapter — the reception-audit logger will
    record the fallback.
    """
    return _REGISTRY.get(provider_type.name, OpenAIMessageAdapter())


# EQ-2: model-aware selector. Some providers (OpenAI) ship multiple model
# families with distinct prompting conventions. We keep the ``ProviderType``
# enum stable and branch on ``model_id`` here instead of introducing a new
# enum variant. Recognized o-series prefixes per OpenAI model docs.
_OSERIES_MODEL_PREFIXES: tuple[str, ...] = (
    "o1",
    "o3",
    "o4",
)


def _is_oseries_model(model_id: str | None) -> bool:
    if not model_id:
        return False
    normalized = model_id.strip().lower()
    for prefix in _OSERIES_MODEL_PREFIXES:
        # Match e.g. "o1", "o1-mini", "o3-pro", "o4" but not "openai-*".
        if normalized == prefix or normalized.startswith(prefix + "-"):
            return True
    return False


def get_adapter_for_model(provider_type: "ProviderType", model_id: str | None) -> "ProviderMessageAdapter":
    """Return the adapter for ``(provider_type, model_id)``.

    EQ-2 extension (ADR-PROMPT-ASSEMBLY-001 Q2): OpenAI o-series models
    (``o1``, ``o3``, ``o4`` and their variants) route to
    :class:`OSeriesMessageAdapter`, which lifts D0 to the ``developer``
    role and drops M0 (CoT prompts). All other providers fall back to the
    same table used by :func:`get_adapter`.
    """
    if provider_type.name in {"OPENAI", "AZURE_OPENAI"} and _is_oseries_model(model_id):
        return OSeriesMessageAdapter()
    return get_adapter(provider_type)


__all__ = ["get_adapter", "get_adapter_for_model"]
