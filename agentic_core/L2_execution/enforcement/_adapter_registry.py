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
from agentic_core.L2_execution.enforcement._adapter_openai import (
    OpenAIMessageAdapter,
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
    # VERTEX_AI, LOCAL_VLLM → fall back to OpenAI-style until dedicated adapters ship in W8.
    "VERTEX_AI": OpenAIMessageAdapter(),
    "LOCAL_VLLM": OpenAIMessageAdapter(),
}


def get_adapter(provider_type: "ProviderType") -> "ProviderMessageAdapter":
    """Return the adapter for ``provider_type``.

    Falls back to the OpenAI adapter for unknown providers so the gateway
    never crashes on a missing adapter — the reception-audit logger will
    record the fallback.
    """
    return _REGISTRY.get(provider_type.name, OpenAIMessageAdapter())


__all__ = ["get_adapter"]
