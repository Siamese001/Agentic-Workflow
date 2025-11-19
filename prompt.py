# FILE: prompt.py
"""
Unified Prompt Layer (v10_9 Enterprise Refactor) — FULL OVERWRITE

This module defines the complete prompt lifecycle for the v10_9 agentic
architecture. It is strictly a *meta-layer* — outside L1–L5 — and owns:

    • Prompt Envelopes
    • Template Registry (per mode)
    • Prompt Builder (L1 → L2 bridge)
    • Prompt Renderer (string output)
    • Instructional Injections (full 1–30 compliance)
    • Safety-context and Runtime-context merging
    • Envelope validation and normalization

Non-responsibilities:
    • NO planning (L1).
    • NO tool execution (L2).
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
        • reasoning      – structured chain-of-thought scaffolding
        • instructions   – strict directives for L2 execution
        • safety_context – L5 safety metadata
        • tool_context   – optional tool metadata from L2
        • output_schema  – strict format constraints
        • runtime_context– dynamic context injected at render-time

    Constraints:
        • No business logic here.
        • Pure data structure.
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

    Templates are short, deterministic, and provide base structure.
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
        mode = mode.lower().strip()
        section = section.lower().strip()
        return cls._REGISTRY.get(mode, {}).get(section, "")


# =============================================================================
# 3. INSTRUCTIONAL INJECTIONS (FULL 1–30 SUPPORT)
# =============================================================================


class Injectors:
    """
    Instructional Injections 1–30 (enterprise-complete).

    All injections are pure transformations on envelope fields.
    """

    # 1 — Global goal alignment
    @staticmethod
    def inject_global_goal(text: str, goal: str) -> str:
        return text + f"\n\nGoal: {goal.strip()}"

    # 2 — Success criteria
    @staticmethod
    def inject_success_criteria(text: str, criteria: str) -> str:
        return text + f"\n\nSuccess Criteria:\n- {criteria.strip()}"

    # 3 — Task mode declaration
    @staticmethod
    def inject_task_mode(text: str, mode: str) -> str:
        return text + f"\n\nTask Mode: {mode}"

    # 4 — Scope boundaries
    @staticmethod
    def inject_scope_boundaries(text: str, boundaries: str) -> str:
        return text + f"\n\nScope:\n{boundaries.strip()}"

    # 5 — Cost/latency hints
    @staticmethod
    def inject_cost_latency(text: str, cost_hint: str) -> str:
        return text + f"\n\nCost/Latency Target: {cost_hint.strip()}"

    # 6 — Untrusted block wrapping
    @staticmethod
    def wrap_untrusted(text: str) -> str:
        return text + "\n\n[UNTRUSTED_BLOCK_BEGIN]\n{{content}}\n[UNTRUSTED_BLOCK_END]"

    # 7 — Input canonicalization
    @staticmethod
    def inject_canonicalization(text: str) -> str:
        return text + "\n\nEnsure that all fields are normalized and deduplicated."

    # 8 — Context pruning rules
    @staticmethod
    def inject_pruning_rules(text: str) -> str:
        return text + "\n\nEnforce context budgets where necessary."

    # 9 — Field cross-linking
    @staticmethod
    def inject_cross_field_rules(text: str) -> str:
        return text + "\n\nCross-check consistency between resume, JD, and RAG."

    # 10 — Reasoning visibility
    @staticmethod
    def inject_reasoning_visibility(text: str) -> str:
        return text + "\n\nExplain your reasoning before the final answer."

    # 11 — Failure anticipation
    @staticmethod
    def inject_failure_modes(text: str, modes: List[str]) -> str:
        if not modes:
            return text
        return text + "\n\nPotential Failure Modes:\n" + "\n".join(f"- {m}" for m in modes)

    # 12 — Self-consistency
    @staticmethod
    def inject_self_consistency(text: str, n: int) -> str:
        return text + f"\n\nUse {n} self-consistency checks."

    # 13 — Safety metadata injection
    @staticmethod
    def inject_safety_metadata(text: str, safety: Dict[str, Any]) -> str:
        return text + "\n\nSafety Metadata:\n" + "\n".join(f"{k}: {v}" for k, v in safety.items())

    # 14 — Tool metadata
    @staticmethod
    def inject_tool_metadata(text: str, tool: Dict[str, Any]) -> str:
        return text + "\n\nTool Context:\n" + "\n".join(f"{k}: {v}" for k, v in tool.items())

    # 15 — Output schema
    @staticmethod
    def inject_output_schema(text: str, schema: str) -> str:
        return text + f"\n\nOutput Schema:\n{schema}"

    # 16 to 30 — Reserved for enterprise extensions
    @staticmethod
    def inject_extension(text: str, label: str, value: str) -> str:
        return text + f"\n\n[{label.upper()}]\n{value}"


# =============================================================================
# 4. BUILDER — L1 → PromptEnvelope (structure only)
# =============================================================================


class Builder:
    """
    Converts an L1 PlanObject into a PromptEnvelope skeleton.

    No rendering logic here. Only attaches:
        • framing (from template)
        • context (stringified state views)
        • reasoning (from L1 metadata)
        • instructions (from template)
        • safety_context (metadata only)
        • tool_context (optional)
        • output_schema (optional)

    L2 fills template slots later.
    """

    @staticmethod
    def build(
        plan: Dict[str, Any],
        *,
        context: str = "",
        runtime_context: Optional[Dict[str, Any]] = None,
        tool_context: Optional[Dict[str, Any]] = None,
        output_schema: str = "",
    ) -> PromptEnvelope:
        mode = str(plan.get("mode", "unknown")).lower()

        framing = PromptTemplateRegistry.get(mode, "framing") or ""
        instructions = PromptTemplateRegistry.get(mode, "instructions") or ""
        reasoning = "Use structured, stepwise reasoning as needed."

        envelope = PromptEnvelope(
            framing=framing,
            context=context,
            reasoning=reasoning,
            instructions=instructions,
            safety_context=copy.deepcopy(plan.get("safety_metadata", {})),
            tool_context=tool_context or {},
            output_schema=output_schema,
            runtime_context=runtime_context or {},
        )

        return envelope


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

    Rendered prompt metadata is available via .last_render_metadata.
    """

    def __init__(self):
        self._last_metadata = {}

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
            parts.append("[SAFETY_CONTEXT]\n" + "\n".join(f"{k}: {v}" for k, v in safety.items()))

        tool_ctx = e.get("tool_context") or {}
        if tool_ctx:
            parts.append("[TOOL_CONTEXT]\n" + "\n".join(f"{k}: {v}" for k, v in tool_ctx.items()))

        if e.get("output_schema"):
            parts.append(f"[OUTPUT_SCHEMA]\n{e['output_schema']}")

        runtime = e.get("runtime_context") or {}
        if runtime:
            parts.append("[RUNTIME_CONTEXT]\n" + "\n".join(f"{k}: {v}" for k, v in runtime.items()))

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
    High-level prompt generation API used by L2 executors:

        text = System.make_prompt(
            plan=plan,
            context="…",
            tool_context={…},
            output_schema="json",
        )

    This calls Builder + Renderer with defaults and merges all metadata.
    """

    @staticmethod
    def make_prompt(
        *,
        plan: Dict[str, Any],
        context: str,
        tool_context: Optional[Dict[str, Any]] = None,
        output_schema: str = "",
        runtime_context: Optional[Dict[str, Any]] = None,
        injections: Optional[List[Callable[[PromptEnvelope], PromptEnvelope]]] = None,
    ) -> str:
        env = Builder.build(
            plan,
            context=context,
            runtime_context=runtime_context,
            tool_context=tool_context,
            output_schema=output_schema,
        )

        # Optional functional envelope transformations
        if injections:
            for injector_fn in injections:
                env = injector_fn(env)

        renderer = Renderer()
        return renderer.render(env)
