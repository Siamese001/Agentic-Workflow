from typing import Any, Dict

from l4_memory import get_prompt_context_view
from prompt_envelope import PromptEnvelope
from prompt_renderer import PromptRenderer
from prompt_templates import envelope_from_template


def _format_context(context: Dict[str, Any]) -> str:
    summary = context.get("summary", "")
    messages = context.get("messages", []) or []
    message_lines = []
    for message in messages[-3:]:
        if isinstance(message, dict):
            role = message.get("role", "")
            content = message.get("content", "")
            message_lines.append(f"{role}: {content}")
        else:
            message_lines.append(str(message))
    formatted_messages = "\n".join(message_lines)
    return "\n".join(
        filter(
            None,
            [
                f"Summary: {summary}".strip(),
                "Recent Messages:",
                formatted_messages.strip(),
            ],
        )
    )


def _format_prompt_with_defaults(prompt_body: str, goal_state: str = "", top_failures: str = "") -> str:
    """Inject governance metadata into prompt text."""

    governance_header = "\n".join(
        filter(
            None,
            [
                f"Goal State: {goal_state}".strip(),
                f"Top Failures: {top_failures}".strip(),
            ],
        )
    ).strip()

    parts = [governance_header, prompt_body]
    return "\n\n".join([p for p in parts if p])


def build_prompt_from_plan_and_state(plan: Dict[str, Any], state: Dict[str, Any]) -> Dict[str, Any]:
    """Construct a rendered prompt using plan intent and orchestration state."""

    context = get_prompt_context_view(state)
    envelope: PromptEnvelope = envelope_from_template()

    envelope.framing = "\n".join(
        filter(
            None,
            [
                f"Objective: {plan.get('objective', '')}",
                f"Mode: {plan.get('mode', '')}",
            ],
        )
    ).strip()
    envelope.context = _format_context(context)
    envelope.reasoning = ""
    envelope.instructions = (
        "Respond deterministically using the provided context. "
        "Preserve section ordering and avoid adding extra formatting beyond what is requested."
    )

    renderer = PromptRenderer()
    rendered_prompt = renderer.render(envelope, runtime_context=context)
    rendered_prompt = _format_prompt_with_defaults(
        rendered_prompt,
        goal_state=plan.get("goal_state", ""),
        top_failures=plan.get("top_failures", ""),
    )
    metadata = renderer.get_last_render_metadata()

    return {"prompt": rendered_prompt, "envelope": envelope, "metadata": metadata}


__all__ = ["build_prompt_from_plan_and_state", "_format_prompt_with_defaults"]
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
"""
Prompt Templates

Responsibilities:
    • House reusable prompt blueprints for various agentic roles and tasks.
    • Remain decoupled from rendering mechanics while supporting parameterization.
    • Provide structured metadata to inform safety and policy layers.

This file is scaffolded for Priority 0; implementation comes later.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict

from prompt_envelope import PromptEnvelope
from prompt_taxonomy import INSTRUCTIONAL_INJECTION_ALL, PromptSection


DEFAULT_TEMPLATE = {
    "Framing": "You are an orchestrator coordinating deterministic agents.",
    "Context": "Use the provided state to ground your response.",
    "Reasoning": "Keep reasoning minimal; downstream layers handle cognition.",
    "Instructions": "Follow the requested format and stay within scope.",
    "Safety Signals": "Respect safety directives from the gateway.",
    "Output Schema": "Return plain text content respecting the schema.",
}

DEFAULT_TEMPLATE_INJECTION = {
    "reason_then_answer": True
}

DEFAULT_TEMPLATE_OUTPUT_INJECTION = {
    "strict_json_output": False,
    "schema_enforcement": False,
    "stability_contracts": True,
    "error_normalization": True,
    "minimality_constraints": True,
}

DEFAULT_TEMPLATE_METADATA = {
    "taxonomy": {
        "sections": [s.value for s in PromptSection],
        "instructional_injection_types": INSTRUCTIONAL_INJECTION_ALL,
    },
    "injection_reasoning": DEFAULT_TEMPLATE_INJECTION,
    "stable_ordering": True,
    "taxonomy_version": "v5",
}

DEFAULT_TEMPLATE_METADATA["output_injection"] = DEFAULT_TEMPLATE_OUTPUT_INJECTION


def load_template(name: str | None = None) -> Dict[str, str]:
    """Return a copy of a known template by name."""

    if name in (None, "default"):
        return deepcopy(DEFAULT_TEMPLATE)
    raise ValueError(f"Unknown template: {name}")


def envelope_from_template(name: str | None = None, overrides: Dict[str, Any] | None = None) -> PromptEnvelope:
    """Create a PromptEnvelope from a named template with optional overrides."""

    template = load_template(name)
    overrides = overrides or {}
    metadata = overrides.get("metadata")
    if metadata is None:
        metadata = deepcopy(DEFAULT_TEMPLATE_METADATA)
    else:
        metadata = deepcopy(metadata)
        metadata.setdefault("taxonomy_version", "v5")

    envelope = PromptEnvelope(
        framing=overrides.get("framing", template.get("Framing", "")),
        context=overrides.get("context", template.get("Context", "")),
        reasoning=overrides.get("reasoning", template.get("Reasoning", "")),
        instructions=overrides.get("instructions", template.get("Instructions", "")),
        safety_signals=overrides.get("safety_signals", template.get("Safety Signals", "")),
        output_schema=overrides.get("output_schema", template.get("Output Schema", "")),
        metadata=metadata,
    )
    return envelope
"""Prompt utilities module consolidating builders and validators."""

from __future__ import annotations
"""Read-only helper functions for inspecting prompt render metadata."""



def get_section_names(renderer):
    """Return the ordered list of section names from the last render."""

    meta = renderer.get_last_render_metadata()
    return list(meta.keys())


def get_section_types(renderer):
    """Return a mapping of section name to section type."""

    meta = renderer.get_last_render_metadata()
    return {k: v.get("section_type", "") for k, v in meta.items()}


def get_instructional_injection_types(renderer):
    """Return the instructional injection types for the first section."""

    meta = renderer.get_last_render_metadata()
    if not meta:
        return []
    first_key = next(iter(meta))
    return meta[first_key].get("instructional_injection_types", [])


def get_prompt_taxonomy(renderer):
    """Return the full render metadata map."""

    return renderer.get_last_render_metadata()

from typing import Dict

from prompt_taxonomy import PromptSection


def validate_sections(sections: Dict[str, str]) -> dict:
    """Validate prompt sections against taxonomy ordering and completeness."""

    expected_order = [section.value for section in PromptSection]
    present_sections = [key for key in sections.keys() if key in expected_order]

    missing_sections = [section for section in expected_order if section not in sections]
    empty_sections = [
        section
        for section in expected_order
        if section in sections and not sections.get(section, "").strip()
    ]

    out_of_order = []
    for idx, section in enumerate(present_sections):
        if idx >= len(expected_order) or section != expected_order[idx]:
            out_of_order.append(section)

    valid = not (missing_sections or empty_sections or out_of_order)

    return {
        "valid": valid,
        "missing_sections": missing_sections,
        "out_of_order": out_of_order,
        "empty_sections": empty_sections,
    }
from typing import Any, Dict

from l4_memory import get_prompt_context_view
from prompt_envelope import PromptEnvelope
from prompt_renderer import PromptRenderer
from prompt_templates import envelope_from_template


def _format_context(context: Dict[str, Any]) -> str:
    summary = context.get("summary", "")
    messages = context.get("messages", []) or []
    message_lines = []
    for message in messages[-3:]:
        if isinstance(message, dict):
            role = message.get("role", "")
            content = message.get("content", "")
            message_lines.append(f"{role}: {content}")
        else:
            message_lines.append(str(message))
    formatted_messages = "\n".join(message_lines)
    return "\n".join(
        filter(
            None,
            [
                f"Summary: {summary}".strip(),
                "Recent Messages:",
                formatted_messages.strip(),
            ],
        )
    )


def build_prompt_from_plan_and_state(
    plan: Dict[str, Any], state: Dict[str, Any]
) -> Dict[str, Any]:
    """Construct a rendered prompt using plan intent and orchestration state."""

    context = get_prompt_context_view(state)
    envelope: PromptEnvelope = envelope_from_template()

    envelope.framing = "\n".join(
        filter(
            None,
            [
                f"Objective: {plan.get('objective', '')}",
                f"Mode: {plan.get('mode', '')}",
            ],
        )
    ).strip()
    envelope.context = _format_context(context)
    envelope.reasoning = ""
    envelope.instructions = (
        "Respond deterministically using the provided context. "
        "Preserve section ordering and avoid adding extra formatting beyond what is requested."
    )

    renderer = PromptRenderer()
    rendered_prompt = renderer.render(envelope, runtime_context=context)
    metadata = renderer.get_last_render_metadata()

    return {"prompt": rendered_prompt, "envelope": envelope, "metadata": metadata}
"""Read-only helper functions for inspecting prompt render metadata."""

from __future__ import annotations


def get_section_names(renderer):
    """Return the ordered list of section names from the last render."""

    meta = renderer.get_last_render_metadata()
    return list(meta.keys())


def get_section_types(renderer):
    """Return a mapping of section name to section type."""

    meta = renderer.get_last_render_metadata()
    return {k: v.get("section_type", "") for k, v in meta.items()}


def get_instructional_injection_types(renderer):
    """Return the instructional injection types for the first section."""

    meta = renderer.get_last_render_metadata()
    if not meta:
        return []
    first_key = next(iter(meta))
    return meta[first_key].get("instructional_injection_types", [])


def get_prompt_taxonomy(renderer):
    """Return the full render metadata map."""

    return renderer.get_last_render_metadata()
