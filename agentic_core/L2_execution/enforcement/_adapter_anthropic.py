"""Anthropic provider adapter — W2 RH2.3.

Renders CompiledPromptArtifact fields into Anthropic-idiomatic shape.

Anthropic best practice (per docs/reference/prompting/anthropic_best_practices_2026.md):
- System prompt uses explicit XML tags: <instructions>, <context>, <examples>,
  <role> — parser-stable, Claude-native.
- Clean user turn for the actual request (U0 content).
- Tools schema passes through unchanged (gateway already conforms to
  Anthropic's tool_use format).

Today's implementation is conservative: it passes through the flat strings
unchanged. The gateway instrumentation from W1 already detects XML-tag
presence at the seam. A future slot-map-aware rev (W3+) will compose the
system prompt FROM structured slots rather than accepting a pre-joined blob.
"""

from __future__ import annotations

from typing import Any

from agentic_core.L2_execution.enforcement.provider_adapter import (
    ProviderPayload,
)


class AnthropicMessageAdapter:
    """Anthropic-idiomatic message rendering.

    Preserves XML tags already present in ``final_system_string``; adds a
    top-level ``<system>`` wrapper only if the input has no structural tags
    at all (raw blob). This keeps existing Anthropic-formatted prompts
    byte-for-byte identical.
    """

    name = "anthropic"

    # Structural tags we treat as "already shaped for Anthropic"; presence of
    # any of these means we do not re-wrap the system string.
    _STRUCTURAL_MARKERS: tuple[str, ...] = (
        "<instructions>",
        "<context>",
        "<examples>",
        "<example",
        "<role>",
        "<D0>",
        "<document",
        "<documents>",
        "<thinking>",
    )

    def render(
        self,
        *,
        final_system_string: str,
        final_user_string: str,
        tools_schema: Any,
        slots_used: list[str] | tuple[str, ...] | None = None,
        slots_map: dict[str, str] | None = None,
    ) -> ProviderPayload:
        # Today: pure passthrough. The structural-wrapping path is reserved
        # for W3 when slots_map is populated by the assembler.
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
                "structural_tags_detected": any(
                    m in system for m in self._STRUCTURAL_MARKERS
                ),
            },
        )

    def _compose_system_from_slots(self, slots_map: dict[str, str]) -> str:
        """Compose Anthropic-idiomatic system prompt from structured slots.

        Anthropic convention: XML tags wrap each semantic section.
        Slot → tag mapping:
          S0 (system/role)      → <role> ... </role>
          I0 (instructions)     → <instructions> ... </instructions>
          D0 (constraints)      → <D0> ... </D0>
          C0 (context/RAG)      → <context> ... </context>
          E0 (examples)         → <examples><example>...</example>...</examples>
          M0 (meta-cognitive)   → <thinking_guidance> ... </thinking_guidance>
          H0 (healing re-entry) → <healing_context> ... </healing_context>
        U0 is user-turn content and does NOT go in system prompt.
        """
        parts: list[str] = []
        tag_by_slot = {
            "S0": "role",
            "I0": "instructions",
            "D0": "D0",
            "C0": "context",
            "E0": "examples",
            "M0": "thinking_guidance",
            "H0": "healing_context",
        }
        # Order matches S0 → I0 → D0 → C0 → E0 → M0 → H0 authority gradient.
        for slot in ("S0", "I0", "D0", "C0", "E0", "M0", "H0"):
            content = slots_map.get(slot, "")
            if not content:
                continue
            tag = tag_by_slot[slot]
            parts.append(f"<{tag}>\n{content}\n</{tag}>")
        return "\n\n".join(parts)


__all__ = ["AnthropicMessageAdapter"]
