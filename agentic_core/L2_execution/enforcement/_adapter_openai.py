"""OpenAI provider adapter — W2 RH2.4.

Renders CompiledPromptArtifact fields into OpenAI-idiomatic shape.

OpenAI best practice (per docs/reference/prompting/openai_best_practices_2026.md):
- System prompt uses clear markdown-sectioned hierarchy: "# Role", "# Goal",
  "# Instructions", "# Output Format", "# Examples". Hashtag headings parse
  cleanly for GPT-4 series and o1 family.
- `messages` array with role separation: system / user / assistant. Function
  calls use the ``tools`` field of the Chat Completions API, not inline XML.
- o1-class models respond best to concise delimited sections; GPT-4o family
  tolerates richer markdown.

Today's implementation passes through flat strings; a future slot-map-aware
rev (W3+) will compose markdown-sectioned system prompts from structured
slots.
"""

from __future__ import annotations

from typing import Any

from agentic_core.L2_execution.enforcement.provider_adapter import (
    ProviderPayload,
)


class OpenAIMessageAdapter:
    """OpenAI-idiomatic message rendering.

    Passthrough today; structured composition from slots_map deferred to W3.
    """

    name = "openai"

    def render(
        self,
        *,
        final_system_string: str,
        final_user_string: str,
        tools_schema: Any,
        slots_used: list[str] | tuple[str, ...] | None = None,
        slots_map: dict[str, str] | None = None,
    ) -> ProviderPayload:
        system = final_system_string or ""
        if slots_map is not None:
            system = self._compose_system_from_slots(slots_map) or system

        return ProviderPayload(
            system_prompt=system,
            user_prompt=final_user_string or "",
            tools_schema=tools_schema,
            extra={
                "adapter": self.name,
                "slots_used": list(slots_used) if slots_used else [],
                # Hint for downstream clients that this system string uses
                # OpenAI-style markdown rather than Anthropic XML. Clients
                # that ship a messages[] array can place this as role=system.
                "system_format": "markdown",
            },
        )

    def _compose_system_from_slots(self, slots_map: dict[str, str]) -> str:
        """Compose OpenAI-idiomatic system prompt from structured slots.

        OpenAI convention: markdown headings.
          S0 (system/role)      → ``# Role``
          I0 (instructions)     → ``# Instructions``
          D0 (constraints)      → ``# Constraints``
          C0 (context/RAG)      → ``# Context``
          E0 (examples)         → ``# Examples``
          M0 (meta-cognitive)   → ``# Thinking Approach``
          H0 (healing re-entry) → ``# Recovery Context``
        """
        parts: list[str] = []
        heading_by_slot = {
            "S0": "# Role",
            "I0": "# Instructions",
            "D0": "# Constraints",
            "C0": "# Context",
            "E0": "# Examples",
            "M0": "# Thinking Approach",
            "H0": "# Recovery Context",
        }
        for slot in ("S0", "I0", "D0", "C0", "E0", "M0", "H0"):
            content = slots_map.get(slot, "")
            if not content:
                continue
            heading = heading_by_slot[slot]
            parts.append(f"{heading}\n\n{content}")
        return "\n\n".join(parts)


__all__ = ["OpenAIMessageAdapter"]
