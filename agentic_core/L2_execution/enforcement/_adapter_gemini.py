"""Gemini provider adapter \u2014 W8 RH8.1.

Renders ``CompiledPromptArtifact`` fields into Google-Gemini-idiomatic shape.

Gemini best practice (summarized):
- SystemInstruction + contents(role=user|model) is the canonical envelope.
  Cascade's gateway passes ``system_prompt`` and ``user_prompt`` separately
  which maps cleanly: ``system_prompt`` \u2192 SystemInstruction, ``user_prompt``
  \u2192 contents[0].parts[0].text with role=user.
- Markdown headings parse well; XML-style fences are less idiomatic than
  Anthropic but Gemini tolerates them. We prefer markdown when composing
  from ``slots_map`` but preserve whatever the caller already rendered in
  the passthrough path.
- Function calling uses ``function_declarations`` and ``function_response``
  field names (different from Anthropic's ``tool_use`` / ``tool_result``
  and OpenAI's ``tools``). Tools schema conversion is the caller's
  responsibility \u2014 this adapter only selects rendering style.

Today's behavior is passthrough (same contract as the W2 Anthropic/OpenAI
adapters). Structured composition from ``slots_map`` is wired for W9+ when
the assembler produces slot maps.
"""

from __future__ import annotations

import os
from typing import Any

from agentic_core.L2_execution.enforcement.provider_adapter import (
    ProviderPayload,
)


# EQ-13: long-context threshold for Gemini. Reuses the Anthropic env so
# operators can tune both simultaneously; Gemini falls back to its own
# default if the Anthropic one is unset.
_GEMINI_LONG_CTX_ENV = "GEMINI_LONG_CONTEXT_CHARS"
_ANTHROPIC_LONG_CTX_ENV = "ANTHROPIC_LONG_CONTEXT_CHARS"
_LONG_CTX_DEFAULT = 8_000


def _long_context_threshold() -> int:
    for env in (_GEMINI_LONG_CTX_ENV, _ANTHROPIC_LONG_CTX_ENV):
        raw = os.getenv(env)
        if raw and raw.strip().isdigit():
            return int(raw.strip())
    return _LONG_CTX_DEFAULT


class GeminiMessageAdapter:
    """Gemini-idiomatic message rendering.

    Passthrough today; markdown-section composition via ``slots_map`` when
    the caller provides one.
    """

    name = "gemini"

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
        if slots_map is not None:
            composed = self._compose_system_from_slots(slots_map)
            if composed:
                system = composed

        # EQ-13: mark long-context composition when C0 is heavy so
        # downstream clients can switch to the long-context request
        # shape (Gemini has no separate API surface today; this is
        # observability + future-proofing).
        long_context = False
        if slots_map is not None:
            c0 = slots_map.get("C0") or ""
            if len(c0) >= _long_context_threshold():
                long_context = True

        extra: dict[str, Any] = {
            "adapter": self.name,
            "slots_used": list(slots_used) if slots_used else [],
            # Gemini-specific routing hint for clients that build the
            # generate_content envelope. SystemInstruction accepts a
            # single content part; the markdown hint tells the caller
            # to place this string there.
            "system_format": "markdown",
            "envelope": "system_instruction+contents",
            "long_context": long_context,
        }
        # EQ-5 (ADR-PROMPT-ASSEMBLY-001 Q4): Gemini has native structured
        # output via ``response_mime_type="application/json"`` plus
        # ``response_schema=<schema>`` on GenerationConfig. Both fields
        # are required together — emit them as a pair.
        if response_schema:
            extra["response_mime_type"] = "application/json"
            extra["response_schema"] = response_schema

        return ProviderPayload(
            system_prompt=system,
            user_prompt=final_user_string or "",
            tools_schema=tools_schema,
            extra=extra,
        )

    def _compose_system_from_slots(self, slots_map: dict[str, str]) -> str:
        """Compose Gemini-idiomatic system prompt from structured slots.

        Uses markdown headings rather than XML fences \u2014 matches Google's
        documented examples more closely than Anthropic-style XML.
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


__all__ = ["GeminiMessageAdapter"]
