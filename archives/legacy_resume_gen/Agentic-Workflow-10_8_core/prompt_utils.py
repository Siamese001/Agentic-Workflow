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

# from archives.legacy_resume_gen.Agentic-Workflow-10_8_core.prompt_taxonomy import PromptSection  # INVALID: Cannot import from path with hyphens


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

# from archives.legacy_resume_gen.Agentic-Workflow-10_8_core.l4_memory import get_prompt_context_view  # INVALID: Cannot import from path with hyphens
# from archives.legacy_resume_gen.Agentic-Workflow-10_8_core.prompt_envelope import PromptEnvelope  # INVALID: Cannot import from path with hyphens
# from archives.legacy_resume_gen.Agentic-Workflow-10_8_core.prompt_renderer import PromptRenderer  # INVALID: Cannot import from path with hyphens
# from archives.legacy_resume_gen.Agentic-Workflow-10_8_core.prompt_templates import envelope_from_template  # INVALID: Cannot import from path with hyphens


def _format_context(context: Dict[str, object]) -> str:
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
    plan: Dict[str, object], state: Dict[str, object]
) -> Dict[str, object]:
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
