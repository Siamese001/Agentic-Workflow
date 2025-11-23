from __future__ import annotations

from typing import List, Dict, Any, Optional

from .schemas import PromptSchema, validate_prompt


def compile_prompt(prompt: PromptSchema | dict, context: Optional[Dict[str, Any]] = None) -> str:
    """Compile a governed prompt into a final string.

    This function is intentionally formatting-only and does not perform
    any I/O. It ensures that all prompts share a consistent structure
    with clear sections for objective, instructions, examples, and
    safety tags.
    """

    schema = validate_prompt(prompt)

    lines: List[str] = []

    lines.append(f"ROLE: {schema.role}")
    lines.append("")
    lines.append("OBJECTIVE:")
    lines.append(schema.objective.strip())
    lines.append("")
    lines.append("INSTRUCTIONS:")
    lines.append(schema.instructions.strip())

    if schema.examples:
        lines.append("")
        lines.append("EXAMPLES:")
        for idx, ex in enumerate(schema.examples, start=1):
            lines.append(f"- EXAMPLE {idx}: {ex}")

    if schema.safety_tags:
        lines.append("")
        lines.append("SAFETY TAGS:")
        lines.append(", ".join(sorted(set(schema.safety_tags))))

    return "\n".join(lines).strip() + "\n"
