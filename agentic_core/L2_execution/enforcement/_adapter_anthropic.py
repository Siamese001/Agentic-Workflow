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

import os
from typing import Any

from agentic_core.L2_execution.enforcement.provider_adapter import (
    ProviderPayload,
)


# Long-context threshold (chars). C0 slot content of this length or more
# triggers the hoist-to-top + tail-task-reminder transformation per
# ADR-PROMPT-ASSEMBLY-001 Q3. Overridable via env for tuning (W5 of that ADR).
_LONG_CONTEXT_THRESHOLD_ENV = "ANTHROPIC_LONG_CONTEXT_CHARS"
_LONG_CONTEXT_THRESHOLD_DEFAULT = 8_000

# Marker that flags C0 content as a sequence of discrete documents ready
# for <document> wrapping. Callers delimit with this exact boundary line
# so the adapter can split without parsing prose.
_DOCUMENT_BOUNDARY = "\n---DOC---\n"


def _long_context_threshold() -> int:
    """Resolve the long-context hoist threshold in characters."""
    raw = os.getenv(_LONG_CONTEXT_THRESHOLD_ENV)
    if raw and raw.strip().isdigit():
        return int(raw.strip())
    return _LONG_CONTEXT_THRESHOLD_DEFAULT


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
        response_schema: dict[str, Any] | None = None,
    ) -> ProviderPayload:
        system = final_system_string or ""
        long_context_hoisted = False
        if slots_map is not None:
            composed = self._compose_system_from_slots(slots_map)
            if composed:
                system = composed
            # EQ-2: long-context hoist when C0 is heavy. Mutates `system`
            # but only when a real slots_map is present.
            hoisted, long_context_hoisted = self._apply_long_context_hoist(system, slots_map)
            system = hoisted

        extra: dict[str, Any] = {
            "adapter": self.name,
            "slots_used": list(slots_used) if slots_used else [],
            "structural_tags_detected": any(m in system for m in self._STRUCTURAL_MARKERS),
            "long_context_hoisted": long_context_hoisted,
        }
        # EQ-5 (ADR-PROMPT-ASSEMBLY-001 Q4): Anthropic has no native JSON
        # mode. The recommended structured-output pattern is forced tool use:
        # surface a synthetic ``emit_response`` tool whose input_schema is
        # the requested response shape, and instruct the gateway to set
        # ``tool_choice={"type": "tool", "name": "emit_response"}``. The
        # gateway is responsible for unwrapping the resulting tool_use
        # block back into a plain JSON response on the client side.
        if response_schema:
            extra["forced_tool_use"] = {
                "tool": {
                    "name": "emit_response",
                    "description": "Emit the response in the required JSON shape.",
                    "input_schema": response_schema,
                },
                "tool_choice": {"type": "tool", "name": "emit_response"},
            }

        return ProviderPayload(
            system_prompt=system,
            user_prompt=final_user_string or "",
            tools_schema=tools_schema,
            extra=extra,
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

    # ------------------------------------------------------------------
    # EQ-2 — ADR-PROMPT-ASSEMBLY-001 Q3: long-context hoist + <document>
    # wrapping. Both helpers are additive and only run when a slots_map
    # is present.
    # ------------------------------------------------------------------

    def _apply_long_context_hoist(self, system: str, slots_map: dict[str, str]) -> tuple[str, bool]:
        """Hoist C0 to the top and append a tail task reminder when heavy.

        Anthropic long-context guidance: placing longform data near the
        top of the prompt and echoing the task at the tail improves recall
        across 100k+ token contexts by up to 30%. Only runs when C0 slot
        content is >= the configured threshold.

        Returns ``(new_system, hoisted_flag)``. When the hoist is not
        triggered, returns the input system string unchanged and
        ``hoisted_flag=False``.
        """
        c0 = slots_map.get("C0", "") or ""
        if len(c0) < _long_context_threshold():
            return system, False

        c0_block = self._wrap_documents_if_delimited(c0)
        hoist_prefix = f"<context>\n{c0_block}\n</context>"

        # Invariant: after hoist, <context> is the first block. If the
        # composed system already embeds a <context> (from _compose_from_slots)
        # we strip it out and prepend the hoisted copy so the block moves
        # to the top rather than staying interleaved with instructions.
        stripped = self._strip_first_context(system)
        new_system = f"{hoist_prefix}\n\n{stripped}".strip()

        # Tail task reminder — one line distilled from I0 (instructions).
        i0 = (slots_map.get("I0") or "").strip().splitlines()
        reminder = i0[0] if i0 else ""
        if reminder:
            new_system = f"{new_system}\n\n<task_reminder>\n{reminder}\n</task_reminder>"

        return new_system, True

    def _wrap_documents_if_delimited(self, c0: str) -> str:
        """Split C0 into ``<document index=n>`` blocks on the sentinel boundary.

        Callers that have multi-doc C0 content join chunks with the
        sentinel ``\\n---DOC---\\n`` and let this helper produce the
        Anthropic-idiomatic container. Single-doc C0 (no sentinel) is
        returned unchanged.
        """
        if _DOCUMENT_BOUNDARY not in c0:
            return c0
        docs = [d.strip() for d in c0.split(_DOCUMENT_BOUNDARY) if d.strip()]
        if not docs:
            return c0
        parts: list[str] = ["<documents>"]
        for idx, doc in enumerate(docs, start=1):
            parts.append(f'  <document index="{idx}">')
            parts.append("    <document_content>")
            parts.append(doc)
            parts.append("    </document_content>")
            parts.append("  </document>")
        parts.append("</documents>")
        return "\n".join(parts)

    @staticmethod
    def _strip_first_context(system: str) -> str:
        """Remove the first ``<context>...</context>`` block and return the rest.

        EQ-2 helper for long-context hoist. When the composed system already
        embeds a ``<context>`` block (because ``_compose_system_from_slots``
        always wraps C0), the hoist path needs to lift C0 to position 0.
        Stripping the existing block first prevents duplicate ``<context>``
        tags in the final output.
        """
        open_idx = system.find("<context>")
        close_idx = system.find("</context>", open_idx)
        if open_idx == -1 or close_idx == -1:
            return system
        before = system[:open_idx].rstrip()
        after = system[close_idx + len("</context>") :].lstrip()
        if before and after:
            return f"{before}\n\n{after}"
        return before or after


__all__ = ["AnthropicMessageAdapter"]
