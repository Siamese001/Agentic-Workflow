"""OpenAI o-series (reasoning) provider adapter — EQ-2 (ADR-PROMPT-ASSEMBLY-001 Q2).

Renders ``CompiledPromptArtifact`` fields for OpenAI reasoning models
(o1, o3, o4 families). Differs from the standard GPT-4.1 adapter in three
ways that follow OpenAI's o-series prompting guidance:

1. **D0 (constraints) migrates to the ``developer`` role**, not the system
   string. o-series respects the developer > system > user instruction
   hierarchy, and developer-role content gets stronger adherence. The
   adapter surfaces D0 on ``extra["developer_prompt"]`` so the client
   constructs the three-role messages array.
2. **No M0 (meta-cognitive / CoT) composition.** Reasoning is internal on
   o-series; injecting CoT prompts degrades performance per OpenAI
   guidance. M0 content is dropped with a note on ``extra["m0_dropped"]``.
3. **Optional ``Formatting re-enabled``** prefix when the caller marks
   ``AgentSpec.markdown_output=True``. Opt-in via
   ``slots_map["_markdown_output"] == "1"`` marker (string, since slots_map
   values are strings by contract).

Tools continue to ride the API ``tools=`` field; schemas pass through.
"""

from __future__ import annotations

from typing import Any

from agentic_core.L2_execution.enforcement.provider_adapter import (
    ProviderPayload,
)


class OSeriesMessageAdapter:
    """OpenAI o-series (reasoning) message rendering.

    Composes system string from S0 + I0 + C0 + E0 + H0 in markdown; lifts
    D0 to developer role via ``extra``; drops M0 entirely.
    """

    name = "openai_oseries"

    # Slot codes that compose into the system string (markdown-sectioned).
    _SYSTEM_SLOTS: tuple[str, ...] = ("S0", "I0", "C0", "E0", "H0")

    # Slot codes that are intentionally not rendered by this adapter.
    _DROPPED_SLOTS: tuple[str, ...] = ("M0",)

    # Marker key a caller sets on slots_map to opt into the
    # "Formatting re-enabled" prefix (per OpenAI o-series docs).
    _MARKDOWN_OUTPUT_KEY = "_markdown_output"

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
        developer_prompt = ""
        m0_dropped = False

        if slots_map is not None:
            system, developer_prompt, m0_dropped = self._compose_from_slots(slots_map)
            if not system:
                system = final_system_string or ""

        extra: dict[str, Any] = {
            "adapter": self.name,
            "slots_used": list(slots_used) if slots_used else [],
            "system_format": "markdown",
            # o-series clients read this to build the developer-role
            # entry in their messages array. Empty string means no
            # D0 was provided (skip developer role entirely).
            "developer_prompt": developer_prompt,
            # Observability: confirms the adapter honored the
            # "no CoT on reasoning models" discipline.
            "m0_dropped": m0_dropped,
        }
        # EQ-5: o-series uses the identical OpenAI ``response_format``
        # wire contract as the GPT-4 family.
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

    def _compose_from_slots(self, slots_map: dict[str, str]) -> tuple[str, str, bool]:
        """Build (system_markdown, developer_prompt, m0_dropped)."""
        heading_by_slot = {
            "S0": "# Role",
            "I0": "# Instructions",
            "C0": "# Context",
            "E0": "# Examples",
            "H0": "# Recovery Context",
        }

        parts: list[str] = []
        if slots_map.get(self._MARKDOWN_OUTPUT_KEY) == "1":
            # o-series uses this exact string to re-enable markdown in
            # responses that would otherwise be plain text (per OpenAI docs).
            parts.append("Formatting re-enabled")

        for slot in self._SYSTEM_SLOTS:
            content = slots_map.get(slot, "")
            if not content:
                continue
            heading = heading_by_slot[slot]
            parts.append(f"{heading}\n\n{content}")

        system_markdown = "\n\n".join(parts)
        developer_prompt = (slots_map.get("D0") or "").strip()
        m0_dropped = bool((slots_map.get("M0") or "").strip())

        return system_markdown, developer_prompt, m0_dropped


__all__ = ["OSeriesMessageAdapter"]
