# FILE: prompt.py
"""
Unified Prompt Layer (v10_9) — META LAYER ONLY

This module defines the complete prompt lifecycle for the v10_9 agentic
architecture. It is strictly a *meta-layer* — outside L1–L5 — and owns:

    • PromptEnvelope        – canonical prompt container
    • Template Registry     – base templates per mode (optional usage)
    • Injection Utilities   – instructional / safety / context injections
    • Builder               – envelope construction
    • Renderer              – envelope → string
    • System API            – high-level make_prompt()

Guardrails (Agentic L1–L5):

    • NO planning (L1 cognition).
    • NO tool/LLM execution (L2).
    • NO orchestration (L3).
    • NO state mutation (L4).
    • NO safety/policy decisions (L5).

The purpose of this layer is to build deterministic, structured,
schema-enforced prompts for downstream model/tool execution.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable

import copy


# =============================================================================
# 1. PROMPT ENVELOPE (CANONICAL)
# =============================================================================


@dataclass
class PromptEnvelope:
    """
    Canonical structured container for prompts.

    Sections:
        • framing        – high-level context & scenario
        • context        – job/resume/messages/RAG data
        • reasoning      – structured reasoning scaffolding (CoT/ToT)
        • instructions   – strict directives for execution
        • safety_context – safety / policy metadata
        • tool_context   – optional tool metadata from L2/tool layer
        • output_schema  – format constraints for downstream parser
        • runtime_context– dynamic run metadata (workflow_id, mode, etc.)

    Constraints:
        • No business logic here — pure data structure only.
    """

    framing: str = ""
    context: str = ""
    reasoning: str = ""
    instructions: str = ""
    safety_context: Dict[str, Any] = field(default_factory=dict)
    tool_context: Dict[str, Any] = field(default_factory=dict)
    output_schema: str = ""
    runtime_context: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "framing": self.framing.strip(),
            "context": self.context.strip(),
            "reasoning": self.reasoning.strip(),
            "instructions": self.instructions.strip(),
            "safety_context": copy.deepcopy(self.safety_context),
            "tool_context": copy.deepcopy(self.tool_context),
            "output_schema": self.output_schema.strip(),
            "runtime_context": copy.deepcopy(self.runtime_context),
        }


# =============================================================================
# 2. TEMPLATE REGISTRY
# =============================================================================


class PromptTemplateRegistry:
    """
    Central registry for template strings used for each mode:
        • strategy
        • rag
        • drafting
        • bullets
        • qa
        • safety
        • prompt_engineering
        • hil
        • meta_learning

    Templates are intentionally short and deterministic. They serve as
    base defaults for framing and instructions when higher layers do
    not provide explicit strings.
    """

    _REGISTRY: Dict[str, Dict[str, str]] = {
        "strategy": {
            "framing": "You are generating a job strategy plan.",
            "instructions": "Analyze the provided context and produce a strategic summary.",
        },
        "rag": {
            "framing": "You are performing evidence retrieval and reasoning.",
            "instructions": "Surface key evidence, maintaining accuracy and trustworthiness.",
        },
        "drafting": {
            "framing": "You are generating structured narrative content.",
            "instructions": "Draft clean, coherent sections following the tone and audience.",
        },
        "bullets": {
            "framing": "You are generating resume bullets.",
            "instructions": "Produce concise, metric-focused bullets.",
        },
        "qa": {
            "framing": "You are analyzing content for quality and correctness.",
            "instructions": "Run QA checks and prepare a QA report.",
        },
        "safety": {
            "framing": "You are verifying safety and policy compliance.",
            "instructions": "Apply safety rules and produce a safety evaluation.",
        },
        "prompt_engineering": {
            "framing": "You are shaping prompt structures for downstream tasks.",
            "instructions": "Build clean, reusable prompt envelopes for multiple modes.",
        },
        "hil": {
            "framing": "A human reviewer must make a decision.",
            "instructions": "Structure the human question with clarity and neutrality.",
        },
        "meta_learning": {
            "framing": "You are synthesizing patterns from feedback data.",
            "instructions": "Produce a structured meta-learning insight summary.",
        },
    }

    @classmethod
    def get(cls, mode: str, section: str) -> str:
        mode_n = mode.lower().strip()
        section_n = section.lower().strip()
        return cls._REGISTRY.get(mode_n, {}).get(section_n, "")


# =============================================================================
# 3. INSTRUCTIONAL INJECTIONS (1–30, ABSTRACTED)
# =============================================================================


class Injectors:
    """
    Instructional Injections (1–30) at the envelope/text level.

    These methods are deliberately narrow: they mutate text or envelope
    fields in simple, deterministic ways. Higher abstractions (like your
    30-prompt taxonomy) can be implemented by composing these primitives.
    """

    # ----- High-level text injectors ---------------------------------------

    @staticmethod
    def inject_global_goal(text: str, goal: str) -> str:
        return text + f"\n\nGoal: {goal.strip()}"

    @staticmethod
    def inject_success_criteria(text: str, criteria: str) -> str:
        return text + f"\n\nSuccess Criteria:\n- {criteria.strip()}"

    @staticmethod
    def inject_task_mode(text: str, mode: str) -> str:
        return text + f"\n\nTask Mode: {mode}"

    @staticmethod
    def inject_scope_boundaries(text: str, boundaries: str) -> str:
        return text + f"\n\nScope:\n{boundaries.strip()}"

    @staticmethod
    def inject_cost_latency(text: str, cost_hint: str) -> str:
        return text + f"\n\nCost/Latency Target: {cost_hint.strip()}"

    @staticmethod
    def wrap_untrusted(text: str) -> str:
        return text + "\n\n[UNTRUSTED_BLOCK_BEGIN]\n{{content}}\n[UNTRUSTED_BLOCK_END]"

    @staticmethod
    def inject_canonicalization(text: str) -> str:
        return text + "\n\nEnsure that all fields are normalized and deduplicated."

    @staticmethod
    def inject_pruning_rules(text: str) -> str:
        return text + "\n\nEnforce context budgets where necessary."

    @staticmethod
    def inject_cross_field_rules(text: str) -> str:
        return text + "\n\nCross-check consistency between resume, JD, and RAG results."

    @staticmethod
    def inject_reasoning_visibility(text: str) -> str:
        return text + "\n\nExplain your reasoning before the final answer."

    @staticmethod
    def inject_failure_modes(text: str, modes: List[str]) -> str:
        if not modes:
            return text
        return text + "\n\nPotential Failure Modes:\n" + "\n".join(f"- {m}" for m in modes)

    @staticmethod
    def inject_self_consistency(text: str, n: int) -> str:
        return text + f"\n\nUse {n} self-consistency checks."

    @staticmethod
    def inject_safety_metadata(text: str, safety: Dict[str, Any]) -> str:
        if not safety:
            return text
        block = "\n".join(f"{k}: {v}" for k, v in safety.items())
        return text + "\n\nSafety Metadata:\n" + block

    @staticmethod
    def inject_tool_metadata(text: str, tool: Dict[str, Any]) -> str:
        if not tool:
            return text
        block = "\n".join(f"{k}: {v}" for k, v in tool.items())
        return text + "\n\nTool Context:\n" + block

    @staticmethod
    def inject_output_schema(text: str, schema: str) -> str:
        return text + f"\n\nOutput Schema:\n{schema}"

    @staticmethod
    def inject_extension(text: str, label: str, value: str) -> str:
        return text + f"\n\n[{label.upper()}]\n{value}"

    # ----- Envelope-level helpers ------------------------------------------

    @staticmethod
    def apply_reasoning_injections(env: PromptEnvelope) -> PromptEnvelope:
        """
        Apply generic reasoning-related injections based on existing
        envelope content (idempotent).
        """
        reasoning = env.reasoning or ""
        if reasoning and "Explain your reasoning" not in reasoning:
            reasoning = Injectors.inject_reasoning_visibility(reasoning)
        env.reasoning = reasoning
        return env

    @staticmethod
    def apply_safety_injections(env: PromptEnvelope) -> PromptEnvelope:
        """
        Apply generic safety context injection into the instructions
        or reasoning sections for clarity.
        """
        if env.safety_context:
            env.instructions = Injectors.inject_safety_metadata(
                env.instructions, env.safety_context
            )
        return env


# =============================================================================
# 4. BUILDER — Input → PromptEnvelope (structure only)
# =============================================================================


class Builder:
    """
    Constructs PromptEnvelope instances from structured metadata.

    This builder is intentionally generic and does not depend on PlanObject
    or any runtime state type; it just takes plain arguments.

    Typical usage (from routing layer):

        env = Builder.build(
            framing=framing_text,
            context=context_text,
            reasoning=reasoning_text,
            instructions=instructions_text,
            safety_context=safety_ctx,
            tool_context=tool_ctx,
            output_schema=output_schema,
            runtime_context=runtime_ctx,
        )
    """

    @staticmethod
    def build(
        *,
        framing: str = "",
        context: str = "",
        reasoning: str = "",
        instructions: str = "",
        safety_context: Optional[Dict[str, Any]] = None,
        tool_context: Optional[Dict[str, Any]] = None,
        output_schema: str = "",
        runtime_context: Optional[Dict[str, Any]] = None,
    ) -> PromptEnvelope:
        env = PromptEnvelope(
            framing=framing,
            context=context,
            reasoning=reasoning,
            instructions=instructions,
            safety_context=safety_context or {},
            tool_context=tool_context or {},
            output_schema=output_schema,
            runtime_context=runtime_context or {},
        )
        return env


# =============================================================================
# 5. RENDERER — PromptEnvelope → String
# =============================================================================


class Renderer:
    """
    Renders a PromptEnvelope into a final prompt string.

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
        ...
        [TOOL_CONTEXT]
        ...
        [OUTPUT_SCHEMA]
        ...
        [RUNTIME_CONTEXT]
        ...

    Rendered prompt metadata (length, sections) is accessible via
    get_last_metadata().
    """

    def __init__(self):
        self._last_metadata: Dict[str, Any] = {}

    def render(self, env: PromptEnvelope) -> str:
        e = env.to_dict()

        parts: List[str] = []

        if e.get("framing"):
            parts.append(f"[FRAMING]\n{e['framing']}")

        if e.get("context"):
            parts.append(f"[CONTEXT]\n{e['context']}")

        if e.get("reasoning"):
            parts.append(f"[REASONING]\n{e['reasoning']}")

        if e.get("instructions"):
            parts.append(f"[INSTRUCTIONS]\n{e['instructions']}")

        safety = e.get("safety_context") or {}
        if safety:
            parts.append(
                "[SAFETY_CONTEXT]\n" + "\n".join(f"{k}: {v}" for k, v in safety.items())
            )

        tool_ctx = e.get("tool_context") or {}
        if tool_ctx:
            parts.append(
                "[TOOL_CONTEXT]\n" + "\n".join(f"{k}: {v}" for k, v in tool_ctx.items())
            )

        if e.get("output_schema"):
            parts.append(f"[OUTPUT_SCHEMA]\n{e['output_schema']}")

        runtime = e.get("runtime_context") or {}
        if runtime:
            parts.append(
                "[RUNTIME_CONTEXT]\n" + "\n".join(f"{k}: {v}" for k, v in runtime.items())
            )

        final = "\n\n".join(parts).strip()

        self._last_metadata = {
            "sections": list(e.keys()),
            "length_chars": len(final),
        }

        return final

    def get_last_metadata(self) -> Dict[str, Any]:
        return copy.deepcopy(self._last_metadata)


# =============================================================================
# 6. SYSTEM — High-level API
# =============================================================================


class System:
    """
    High-level prompt generation API used by routing/meta layers:

        text = System.make_prompt(
            framing=...,
            context=...,
            reasoning=...,
            instructions=...,
            safety_ctx={...},
            tool_ctx={...},
            output_schema="json",
            runtime_context={...},
            injections=[optional_envelope_transformers...],
        )

    This class is pure META; it never touches L1–L5 or providers.
    """

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
        injections: Optional[List[Callable[[PromptEnvelope], PromptEnvelope]]] = None,
    ) -> str:
        # Build envelope
        env = Builder.build(
            framing=framing,
            context=context,
            reasoning=reasoning,
            instructions=instructions,
            safety_context=safety_ctx,
            tool_context=tool_ctx,
            output_schema=output_schema,
            runtime_context=runtime_context,
        )

        # Default reasoning/safety injections
        env = Injectors.apply_reasoning_injections(env)
        env = Injectors.apply_safety_injections(env)

        # Optional functional envelope transformations
        if injections:
            for injector_fn in injections:
                env = injector_fn(env)

        renderer = Renderer()
        return renderer.render(env)
