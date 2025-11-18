# FILE: v10_9_clean/prompt/prompt_builder_stack.py
"""
Prompt Builder Stack (v10_9)

Responsible for constructing deterministic prompt envelopes used by
L2 executors (strategy, rag, bullets, drafting, qa, safety).

This file replaces the 10_8 prompt_builder and prompt_stack
with a clean, minimal 10_9-compliant interface.
"""

from __future__ import annotations
from typing import Any, Dict, List


def build_envelope(
    framing: str,
    context: str,
    reasoning: str,
    instructions: str,
) -> Dict[str, Any]:
    """
    Construct a deterministic prompt envelope with standardized sections.

    Output structure:
        {
            "framing": ...,
            "context": ...,
            "reasoning": ...,
            "instructions": ...
        }
    """
    return {
        "framing": framing.strip(),
        "context": context.strip(),
        "reasoning": reasoning.strip(),
        "instructions": instructions.strip(),
    }


def build_prompt_from_components(components: Dict[str, Any]) -> str:
    """
    Render a prompt string from envelope components in deterministic order.
    """

    framing = components.get("framing", "")
    context = components.get("context", "")
    reasoning = components.get("reasoning", "")
    instructions = components.get("instructions", "")

    parts: List[str] = []

    if framing:
        parts.append(f"[FRAMING]\n{framing}")
    if context:
        parts.append(f"[CONTEXT]\n{context}")
    if reasoning:
        parts.append(f"[REASONING]\n{reasoning}")
    if instructions:
        parts.append(f"[INSTRUCTIONS]\n{instructions}")

    return "\n\n".join(parts)
