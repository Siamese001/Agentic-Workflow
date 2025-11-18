# FILE: prompt.py
"""
Unified Prompt Module (v10_9) — FULL AGENTIC IMPLEMENTATION

This module consolidates ALL prompt-related behavior across the v10_9
architecture, providing:

SECTIONS:
    1. PromptEnvelope      – canonical structured prompt container
    2. Builder             – deterministic envelope construction
    3. Renderer            – full prompt rendering (framing/context/reasoning/instructions)
    4. Injectors           – Instructional Injections 1–30 (v10_7 parity)
    5. System              – high-level orchestration for L1 → L2 prompt preparation
    6. Utils               – normalization, trimming, formatting

Pure prompt transformation:
    • NO L1 cognition
    • NO L2 execution
    • NO L3 orchestration
    • NO L4 mutation
    • NO safety decisions (L5) — only safety *metadata injection*
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# ============================================================================
# 1. PROMPT ENVELOPE (CANONICAL)
# ============================================================================

@dataclass
class PromptEnvelope:
    """
    Canonical structured container for prompts.

    Sections:
        • framing        – high-level context & scenario
        • context        – job/resume/messages/RAG data
        • reasoning      – explicit chain-of-thought scaffolding
        • instructions   – strict directives for L2
        • safety_context – injection of safety metadata (from plan)
        • tool_context   – optional tool metadata
        • output_schema  – strict format requirements

    Equivalent to the combined v10_7/v10_8 envelope structure.
    """

    framing: str = ""
    context: str = ""
    reasoning: str = ""
    instructions: str = ""
    safety_context: Dict[str, Any] = field(default_factory=dict)
    tool_context: Dict[str, Any] = field(default_factory=dict)
    output_schema: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "framing": self.framing.strip(),
            "context": self.context.strip(),
            "reasoning": self.reasoning.strip(),
            "instructions": self.instructions.strip(),
            "safety_context": self.safety_context.copy(),
            "tool_context": self.tool_context.copy(),
            "output_schema": self.output_schema.strip(),
        }


# ============================================================================
# 2. BUILDER — DETERMINISTIC ENVELOPE CONSTRUCTION
# ============================================================================

class Builder:

    @staticmethod
    def build(
        *,
        framing: str,
        context: str,
        reasoning: str,
        instructions: str,
        safety_context: Optional[Dict[str, Any]] = None,
        tool_context: Optional[Dict[str, Any]] = None,
        output_schema: str = "",
    ) -> Dict[str, Any]:

        env = PromptEnvelope(
            framing=framing,
            context=context,
            reasoning=reasoning,
            instructions=instructions,
            safety_context=safety_context or {},
            tool_context=tool_context or {},
            output_schema=output_schema,
        )
        return env.to_dict()

    @staticmethod
    def from_parts(parts: Dict[str, Any]) -> PromptEnvelope:
        return PromptEnvelope(
            framing=parts.get("framing", ""),
            context=parts.get("context", ""),
            reasoning=parts.get("reasoning", ""),
            instructions=parts.get("instructions", ""),
            safety_context=parts.get("safety_context", {}) or {},
            tool_context=parts.get("tool_context", {}) or {},
            output_schema=parts.get("output_schema", ""),
        )


# ============================================================================
# 3. RENDERER — FULL PROMPT RENDERING ENGINE
# ============================================================================

class Renderer:
    """
    Converts a PromptEnvelope + optional runtime context into a final prompt string.

    Output Structure:
        [FRAMING]
        ...
        [CONTEXT]
        ...
        [REASONING]
        ...
        [INSTRUCTIONS]
        ...
        [SAFETY_CONTEXT]
        key: value
        ...
        [TOOL_CONTEXT]
        ...
        [OUTPUT_SCHEMA]
        ...
        [RUNTIME_CONTEXT]
        ...
    """

    def __init__(self):
        self._last_metadata = {}

    def render(
        self,
        env: Dict[str, Any] | PromptEnvelope,
        runtime_context: Optional[Dict[str, Any]] = None,
    ) -> str:

        if isinstance(env, PromptEnvelope):
            e = env.to_dict()
        else:
            e = dict(env)

        framing       = e.get("framing", "") or ""
        context       = e.get("context", "") or ""
        reasoning     = e.get("reasoning", "") or ""
        instructions  = e.get("instructions", "") or ""
        safety        = e.get("safety_context", {}) or {}
        tool_ctx      = e.get("tool_context", {}) or {}
        output_schema = e.get("output_schema", "") or ""
        runtime_ctx   = runtime_context or {}

        parts: List[str] = []

        if framing:
            parts.append(f"[FRAMING]\n{framing.strip()}")

        if context:
            parts.append(f"[CONTEXT]\n{context.strip()}")

        if reasoning:
            parts.append(f"[REASONING]\n{reasoning.strip()}")

        if instructions:
            parts.append(f"[INSTRUCTIONS]\n{instructions.strip()}")

        # L5 metadata injection (but no L5 logic)
        if safety:
            parts.append("[SAFETY_CONTEXT]\n" + self._format_kv(safety))

        if tool_ctx:
            parts.append("[TOOL_CONTEXT]\n" + self._format_kv(tool_ctx))

        if output_schema:
            parts.append(f"[OUTPUT_SCHEMA]\n{output_schema.strip()}")

        if runtime_ctx:
            parts.append("[RUNTIME_CONTEXT]\n" + self._format_kv(runtime_ctx))

        final = "\n\n".join(parts).strip()

        self._last_metadata = {
            "sections": list(e.keys()),
            "runtime_keys": list(runtime_ctx.keys()),
        }

        return final

    def _format_kv(self, d: Dict[str, Any]) -> str:
        return "\n".join(f"{k}: {v}" for k, v in d.items()).strip()

    def get_last_render_metadata(self) -> Dict[str, Any]:
        return dict(self._last_metadata)


# ============================================================================
# 4. INJECTORS — (Instructional Injections 1–30)
# ============================================================================

class Injectors:
    """
    High-level transformation utilities used by L1 → L2 prompt generation.

    These correspond to the "Instructional Injection" set (1–30)
    you defined in prior versions. These do NOT perform safety decisions;
    they simply alter/augment prompt structure for clarity, robustness,
    and deterministic adherence to agentic behavior.

    Only the core subset are implemented here, because the others are
    automatically handled by L1/L2/L5 metadata.
    """

    @staticmethod
    def inject_global_goal(framing: str, goal: str) -> str:
        return framing + f"\n\nObjective: {goal.strip()}"

    @staticmethod
    def inject_success_criteria(framing: str, criteria: str) -> str:
        return framing + f"\n\nSuccess Criteria: {criteria.strip()}"

    @staticmethod
    def inject_scope_boundaries(instructions: str, boundaries: str) -> str:
        return instructions + f"\n\nScope Boundaries:\n{boundaries.strip()}"

    @staticmethod
    def inject_reason_then_answer(reasoning: str) -> str:
        return reasoning + "\n\nRespond using: (1) Reasoning, then (2) Final Answer."

    @staticmethod
    def inject_failure_anticipation(reasoning: str, modes: List[str]) -> str:
        if not modes:
            return reasoning
        block = "Potential Failure Modes:\n" + "\n".join(f"- {m}" for m in modes)
        return reasoning + "\n\n" + block

    @staticmethod
    def inject_self_consistency(reasoning: str, n: int) -> str:
        return reasoning + f"\n\nUse {n} self-consistency checks before finalizing."

    @staticmethod
    def inject_safety_metadata(context: str, safety: Dict[str, Any]) -> str:
        return context + "\n\nSafety Metadata:\n" + "\n".join(f"{k}: {v}" for k, v in safety.items())


# ============================================================================
# 5. SYSTEM — HIGH-LEVEL PROMPT ORCHESTRATION
# ============================================================================

class System:

    @staticmethod
    def make_prompt(
        *,
        framing: str,
        context: str,
        reasoning: str,
        instructions: str,
        safety_ctx: Optional[Dict[str, Any]] = None,
        tool_ctx: Optional[Dict[str, Any]] = None,
        output_schema: str = "",
        runtime_context: Optional[Dict[str, Any]] = None,
    ) -> str:

        env = Builder.build(
            framing=framing,
            context=context,
            reasoning=reasoning,
            instructions=instructions,
            safety_context=safety_ctx or {},
            tool_context=tool_ctx or {},
            output_schema=output_schema,
        )

        renderer = Renderer()
        return renderer.render(env, runtime_context)


# ============================================================================
# 6. UTILS — string normalization, trimming, formatting
# ============================================================================

class Utils:

    @staticmethod
    def normalize(text: Optional[str]) -> str:
        return (text or "").strip()

    @staticmethod
    def truncate(text: str, max_chars: int = 4096) -> str:
        return text[:max_chars].rstrip()

    @staticmethod
    def pretty_dict(d: Dict[str, Any]) -> str:
        return "\n".join(f"{k}: {v}" for k, v in d.items())

    @staticmethod
    def join_sections(sections: List[str]) -> str:
        return "\n\n".join(sec.strip() for sec in sections if sec.strip())

    @staticmethod
    def ensure_block(label: str, content: str) -> str:
        content = (content or "").strip()
        return f"[{label.upper()}]\n{content}" if content else f"[{label.upper()}]\n"
