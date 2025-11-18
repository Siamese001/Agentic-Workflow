# FILE: v10_9_clean/prompt.py
"""
Unified Prompt Module (v10_9)

Namespace-organized consolidation of ALL prompt-related logic:

    • Builder  – constructs prompt envelopes
    • Renderer – converts envelopes + runtime context into final prompt text
    • System   – high-level prompt system orchestration used by L2 executors
    • Utils    – normalization, formatting, string utilities

This replaces:
    prompt_builder_stack.py
    prompt_renderer_stack.py
    prompt_system.py
    prompt_utils.py

Pure utilities:
    • No execution (L2)
    • No planning (L1)
    • No state mutation (L4)
"""

from __future__ import annotations
from typing import Any, Dict, List


# ============================================================================
# BUILDER NAMESPACE
# ============================================================================

class Builder:
    """
    Responsible for building prompt envelopes made of four deterministic
    sections:
        [FRAMING]
        [CONTEXT]
        [REASONING]
        [INSTRUCTIONS]
    """

    @staticmethod
    def build_envelope(
        framing: str,
        context: str,
        reasoning: str,
        instructions: str,
    ) -> Dict[str, Any]:
        return {
            "framing": framing.strip(),
            "context": context.strip(),
            "reasoning": reasoning.strip(),
            "instructions": instructions.strip(),
        }

    @staticmethod
    def from_components(components: Dict[str, Any]) -> str:
        framing = components.get("framing", "").strip()
        context = components.get("context", "").strip()
        reasoning = components.get("reasoning", "").strip()
        instructions = components.get("instructions", "").strip()

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


# ============================================================================
# RENDERER NAMESPACE
# ============================================================================

class Renderer:
    """
    Renders a final LLM prompt from:
        • A Builder envelope
        • Optional runtime context

    Output format:
        [FRAMING]
        ...
        [CONTEXT]
        ...
        [REASONING]
        ...
        [INSTRUCTIONS]
        ...
        [RUNTIME_CONTEXT]
        key: value
        key2: value2
    """

    def __init__(self) -> None:
        self._last_metadata: Dict[str, Any] = {}

    def render(self, envelope: Dict[str, Any], runtime_context: Dict[str, Any] | None = None) -> str:
        framing = envelope.get("framing", "") or ""
        context = envelope.get("context", "") or ""
        reasoning = envelope.get("reasoning", "") or ""
        instructions = envelope.get("instructions", "") or ""
        runtime_context = runtime_context or {}

        parts: List[str] = []

        if framing:
            parts.append(f"[FRAMING]\n{framing}")
        if context:
            parts.append(f"[CONTEXT]\n{context}")
        if reasoning:
            parts.append(f"[REASONING]\n{reasoning}")
        if instructions:
            parts.append(f"[INSTRUCTIONS]\n{instructions}")

        # Runtime context (flattened key/value pairs)
        if runtime_context:
            rc_text = self._format_runtime_context(runtime_context)
            parts.append(f"[RUNTIME_CONTEXT]\n{rc_text}")

        final = "\n\n".join(parts)

        self._last_metadata = {
            "sections": list(envelope.keys()),
            "runtime_keys": list(runtime_context.keys()),
        }

        return final

    def _format_runtime_context(self, ctx: Dict[str, Any]) -> str:
        lines = []
        for k, v in ctx.items():
            lines.append(f"{k}: {v}")
        return "\n".join(lines).strip()

    def get_last_render_metadata(self) -> Dict[str, Any]:
        return dict(self._last_metadata)


# ============================================================================
# PROMPT SYSTEM (HIGH-LEVEL)
# ============================================================================

class System:
    """
    High-level orchestration for prompt assembly.

    Provides:
        • make_prompt_for_executor()
        • standardized construction for L2 executors
        • combined framing + reasoning + context + instructions
        • optional runtime context injection
    """

    @staticmethod
    def make_prompt_for_executor(
        framing: str,
        context: str,
        reasoning: str,
        instructions: str,
        runtime_context: Dict[str, Any] | None = None,
    ) -> str:
        envelope = Builder.build_envelope(framing, context, reasoning, instructions)
        renderer = Renderer()
        return renderer.render(envelope, runtime_context)


# ============================================================================
# UTILS NAMESPACE
# ============================================================================

class Utils:
    """
    Prompt-related small utilities:
        • safe string formatting
        • normalization helpers
        • content trimming
        • key-value pretty-printing
    """

    @staticmethod
    def normalize(text: str | None) -> str:
        return (text or "").strip()

    @staticmethod
    def truncate(text: str, max_chars: int = 2000) -> str:
        return text[:max_chars].rstrip()

    @staticmethod
    def pretty_dict(d: Dict[str, Any]) -> str:
        return "\n".join([f"{k}: {v}" for k, v in d.items()])

    @staticmethod
    def join_sections(sections: List[str]) -> str:
        return "\n\n".join(sec.strip() for sec in sections if sec.strip())

    @staticmethod
    def ensure_block(label: str, content: str) -> str:
        return f"[{label.upper()}]\n{content.strip()}" if content else ""
