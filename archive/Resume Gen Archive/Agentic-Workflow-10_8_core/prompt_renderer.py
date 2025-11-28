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
from prompt_schema_validator import validate_sections
from prompt_taxonomy import INSTRUCTIONAL_INJECTION_ALL, PromptSection
from prompt_templates import (
    DEFAULT_TEMPLATE_OUTPUT_INJECTION,
    envelope_from_template,
    load_template,
)


class PromptRenderer:
    """Render composite prompts from envelopes and templates."""

    SECTION_ORDER = [
        PromptSection.FRAMING.value,
        PromptSection.CONTEXT.value,
        PromptSection.REASONING.value,
        PromptSection.INSTRUCTIONS.value,
        PromptSection.SAFETY.value,
        PromptSection.OUTPUT_SCHEMA.value,
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

        render_metadata = {}
        for sec in self.SECTION_ORDER:
            render_metadata[sec] = {
                "section_type": sec,
                "instructional_injection_types": INSTRUCTIONAL_INJECTION_ALL,
            }

        render_metadata["injection_reasoning"] = {
            "reason_then_answer": True
        }

        render_metadata["injection_tooling"] = {"model_switch_awareness": True}

        render_metadata["injection_output"] = DEFAULT_TEMPLATE_OUTPUT_INJECTION

        validation = validate_sections(sections)
        render_metadata["taxonomy_validation"] = validation

        self._last_render_metadata = render_metadata

        return "\n\n".join(rendered_sections)

    def _resolve_template(self, template: str | Dict[str, str] | None) -> Dict[str, str]:
        if template is None:
            return load_template(self.default_template)
        if isinstance(template, str):
            return load_template(template)
        return dict(template)

    def get_render_metadata(self) -> Dict[str, Any]:
        return self.get_last_render_metadata()

    def get_last_render_metadata(self):
        return getattr(self, "_last_render_metadata", {})
