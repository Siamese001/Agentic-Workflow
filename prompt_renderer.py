"""
Prompt Renderer

Responsibilities:
    • Render composite prompts by combining envelopes, templates, and runtime context.
    • Support parameter injection while preserving safety and policy metadata.
    • Expose rendering hooks for orchestrators without embedding execution logic.

This file is scaffolded for Priority 0; implementation comes later.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from prompt_envelope import PromptEnvelope
from prompt_templates import envelope_from_template, load_template


class PromptRenderer:
    """Render composite prompts from envelopes and templates."""

    SECTION_ORDER = [
        "Framing",
        "Context",
        "Reasoning",
        "Instructions",
        "Safety Signals",
        "Output Schema",
    ]

    def __init__(self, default_template: str | None = "default") -> None:
        self.default_template = default_template

    def render(
        self,
        envelope: PromptEnvelope | None = None,
        template: str | Dict[str, str] | None = None,
        runtime_context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Assemble a full prompt string in deterministic section order."""

        runtime_context = runtime_context or {}
        resolved_template = self._resolve_template(template)
        envelope = envelope or envelope_from_template(self.default_template)

        sections = envelope.to_sections()
        rendered_sections = []
        for name in self.SECTION_ORDER:
            content = sections.get(name) or resolved_template.get(name, "")
            try:
                content = content.format(**runtime_context)
            except KeyError:
                # Leave unresolved placeholders intact
                pass
            rendered_sections.append(f"[{name}]\n{content}".strip())

        return "\n\n".join(rendered_sections)

    def _resolve_template(self, template: str | Dict[str, str] | None) -> Dict[str, str]:
        if template is None:
            return load_template(self.default_template)
        if isinstance(template, str):
            return load_template(template)
        return dict(template)
