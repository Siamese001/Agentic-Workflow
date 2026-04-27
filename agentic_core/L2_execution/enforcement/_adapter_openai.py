"""OpenAI provider adapter — W2 RH2.4.

Renders CompiledPromptArtifact fields into OpenAI-idiomatic shape.

OpenAI best practice (per docs/reference/_primers/prompting/openai_best_practices_2026.md):
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

import os
from typing import Any

from agentic_core.L2_execution.enforcement.provider_adapter import (
    ProviderPayload,
)


# Long-context threshold (chars). C0 of this length or more triggers the
# "# Final instructions" tail-repetition per ADR-PROMPT-ASSEMBLY-001 Q3.
_LONG_CONTEXT_THRESHOLD_ENV = "OPENAI_LONG_CONTEXT_CHARS"
_LONG_CONTEXT_THRESHOLD_DEFAULT = 8_000


def _long_context_threshold() -> int:
    """Resolve the long-context tail-reminder threshold in characters."""
    raw = os.getenv(_LONG_CONTEXT_THRESHOLD_ENV)
    if raw and raw.strip().isdigit():
        return int(raw.strip())
    return _LONG_CONTEXT_THRESHOLD_DEFAULT


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
        response_schema: dict[str, Any] | None = None,
    ) -> ProviderPayload:
        system = final_system_string or ""
        long_context_tail_reminder = False
        if slots_map is not None:
            composed = self._compose_system_from_slots(slots_map)
            if composed:
                system = composed
            # EQ-2: append condensed I0 as `# Final instructions` when C0
            # is heavy — OpenAI long-context guidance.
            system, long_context_tail_reminder = self._apply_final_instructions_tail(system, slots_map)

        extra: dict[str, Any] = {
            "adapter": self.name,
            "slots_used": list(slots_used) if slots_used else [],
            # Hint for downstream clients that this system string uses
            # OpenAI-style markdown rather than Anthropic XML. Clients
            # that ship a messages[] array can place this as role=system.
            "system_format": "markdown",
            "long_context_tail_reminder": long_context_tail_reminder,
        }
        # EQ-5: translate response_schema into OpenAI's response_format API
        # contract. The ``strict: True`` flag enables OpenAI's structured
        # outputs guarantee (constrained decoding); the schema name is a
        # required field on that path.
        if response_schema:
            extra["response_format"] = {
                "type": "json_schema",
                "json_schema": {
                    "name": "Response",
                    "schema": response_schema,
                    "strict": True,
                },
            }

        return ProviderPayload(
            system_prompt=system,
            user_prompt=final_user_string or "",
            tools_schema=tools_schema,
            extra=extra,
        )

    def _apply_final_instructions_tail(self, system: str, slots_map: dict[str, str]) -> tuple[str, bool]:
        """Append a `# Final instructions` block when C0 is heavy.

        OpenAI long-context guidance: placing instructions both before and
        after the context (or at least echoing them at the tail) yields
        better recall. Triggered only when C0 slot length >= threshold.
        """
        c0 = slots_map.get("C0", "") or ""
        if len(c0) < _long_context_threshold():
            return system, False
        i0 = (slots_map.get("I0") or "").strip()
        if not i0:
            return system, False
        # Condense to first line for the tail reminder — keeps token
        # overhead low while preserving the task prompt.
        reminder = i0.splitlines()[0]
        tail = f"# Final instructions\n\n{reminder}"
        return f"{system}\n\n{tail}", True

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
