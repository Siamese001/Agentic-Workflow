"""Provider-aware message adapter protocol — W2 RH2.1.

Defines the seam between the governed ``CompiledPromptArtifact`` and the
concrete LLM provider wire format. Each provider gets a dedicated adapter
that renders the artifact's slots into provider-idiomatic shape:

- Anthropic: XML-tagged system sections, clean user turn.
- OpenAI: markdown-sectioned system, optional developer role.

This is the seam referenced by ADR-PROMPT-ASSEMBLY-001. Today adapters accept
a flat ``CompiledPromptArtifact`` and render from the already-assembled
``final_system_string`` / ``final_user_string``. When W3 lands the structured
slot map, adapters will receive it directly via ``slots_map`` kwarg and
produce provider-idiomatic output from structured input.

Enable via env: ``PROMPT_ADAPTER_V2=1`` (default off; legacy pass-through).
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Protocol


_ENV_ADAPTER_V2 = "PROMPT_ADAPTER_V2"


def adapter_v2_enabled() -> bool:
    """Whether the provider-adapter v2 dispatch path is enabled."""
    return os.getenv(_ENV_ADAPTER_V2, "").lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class ProviderPayload:
    """Canonical provider-ready payload returned by an adapter.

    Fields correspond to the arguments the provider adapter's ``generate``
    method expects today: ``(system_prompt, user_prompt, tools_schema,
    **kwargs)``. Carrying them as a dataclass preserves the seam contract
    while letting adapters opt into richer shapes (e.g., OpenAI messages
    arrays) via ``extra``.
    """

    system_prompt: str
    user_prompt: str
    tools_schema: Any
    extra: dict[str, Any] = field(default_factory=dict)


class ProviderMessageAdapter(Protocol):
    """Renders a CompiledPromptArtifact into a provider-idiomatic payload."""

    name: str

    def render(
        self,
        *,
        final_system_string: str,
        final_user_string: str,
        tools_schema: Any,
        slots_used: list[str] | tuple[str, ...] | None = None,
        slots_map: dict[str, str] | None = None,
    ) -> ProviderPayload:
        """Render artifact fields into a provider payload.

        Args
        ----
        final_system_string: Flat system string from CompiledPromptArtifact.
        final_user_string: Flat user string from CompiledPromptArtifact.
        tools_schema: Tools schema passed through unchanged today.
        slots_used: Ordered list of slot codes that were assembled.
        slots_map: Optional per-slot content (S0, I0, D0, C0, U0, E0, M0, H0).
            When present, adapter MAY use it to produce structured output
            instead of parsing the flat strings. W2 adapters ignore this for
            now and passthrough from the flat strings; W3 wires it in.
        """
        ...


__all__ = [
    "ProviderPayload",
    "ProviderMessageAdapter",
    "adapter_v2_enabled",
]
