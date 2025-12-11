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
