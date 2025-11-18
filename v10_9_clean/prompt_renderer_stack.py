# FILE: v10_9_clean/prompt/prompt_renderer_stack.py
"""
Prompt Renderer Stack (v10_9)

Renders a fully structured LLM prompt from:
    • a prompt envelope (built by prompt_builder_stack)
    • state/context blocks passed in by L2 executors

This modular renderer replaces the 10_8 renderer with a clean, deterministic,
L1–L5-compliant formatting pipeline.
"""

from __future__ import annotations
from typing import Any, Dict, List


class PromptRenderer:
    """
    Deterministic prompt renderer that:
        • Accepts an envelope dict
        • Accepts a runtime_context dict
        • Produces a final prompt string for L2 executors

    Output is:
        [FRAMING]
        ...
        [CONTEXT]
        ...
        [REASONING]
        ...
        [INSTRUCTIONS]
        ...
        [RUNTIME_CONTEXT]
        <flattened user/runtime hints>
    """

    def __init__(self) -> None:
        self._last_metadata: Dict[str, Any] = {}

    # ------------------------------------------------------------------
    def render(
        self,
        envelope: Dict[str, Any],
        runtime_context: Dict[str, Any] | None = None,
    ) -> str:
        """
        Render a final prompt string in deterministic order.
        """

        framing = envelope.get("framing", "").strip()
        context = envelope.get("context", "").strip()
        reasoning = envelope.get("reasoning", "").strip()
        instructions = envelope.get("instructions", "").strip()

        runtime_context = runtime_context or {}

        # Build sections
        parts: List[str] = []

        if framing:
            parts.append(f"[FRAMING]\n{framing}")

        if context:
            parts.append(f"[CONTEXT]\n{context}")

        if reasoning:
            parts.append(f"[REASONING]\n{reasoning}")

        if instructions:
            parts.append(f"[INSTRUCTIONS]\n{instructions}")

        if runtime_context:
            rc = self._render_runtime_context(runtime_context)
            parts.append(f"[RUNTIME_CONTEXT]\n{rc}")

        final = "\n\n".join(parts)

        # store metadata for retrieval
        self._last_metadata = {
            "sections": list(envelope.keys()),
            "runtime_keys": list(runtime_context.keys()),
        }

        return final

    # ------------------------------------------------------------------
    def _render_runtime_context(self, ctx: Dict[str, Any]) -> str:
        lines: List[str] = []
        for k, v in ctx.items():
            if isinstance(v, (list, dict)):
                lines.append(f"{k}: {str(v)}")
            else:
                lines.append(f"{k}: {v}")
        return "\n".join(lines).strip()

    # ------------------------------------------------------------------
    def get_last_render_metadata(self) -> Dict[str, Any]:
        """Return metadata from the most recent render call."""
        return dict(self._last_metadata)
