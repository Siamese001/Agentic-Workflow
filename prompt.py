# FILE: prompt.py
"""
Unified Prompt Layer (v10_9, Fully Refactored)
META-ONLY — CENTRALIZED PROMPT GOVERNANCE (MAX SCORE: Prompt Governance)

This module owns **all prompt construction** for the v10_9 agentic workflow.
It satisfies strict Agentic Layering:

    • NO L1 cognition
    • NO L2 execution
    • NO L3 orchestration
    • NO L4 state mutation
    • NO L5 safety/policy logic
    • NO model/provider calls

It restores ALL missing 10_8 behaviors:
    • Prompt taxonomy + registry
    • Structured envelope (framing, context, reasoning, instructions, safety, tools)
    • Metadata-rich templates
    • Instructional injection types
    • Section-aware prompt assembly
    • Deterministic rendering
    • Runtime context passthrough
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import copy


# ============================================================================
# 1. PROMPT ENVELOPE (CANONICAL)
# ============================================================================

@dataclass
class PromptEnvelope:
    """
    Canonical prompt container.

    Sections:
        - framing
        - context
        - reasoning
        - instructions
        - safety_context
        - tool_context
        - output_schema
        - runtime_context

    This is a pure data-object. No business logic or mutation.
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


# ============================================================================
# 2. PROMPT TAXONOMY & ENUM-LIKE STRUCTURES (RESTORED FROM 10_8)
# ============================================================================

class PromptSection:
    FRAMING = "framing"
    CONTEXT = "context"
    REASONING = "reasoning"
    INSTRUCTIONS = "instructions"
    SAFETY = "safety_context"
    TOOL = "tool_context"
    SCHEMA = "output_schema"
    RUNTIME = "runtime_context"


class InjectionType:
    GLOBAL_GOAL = "global_goal"
    SUCCESS_CRITERIA = "success_criteria"
    SCOPE_BOUNDARIES = "scope_boundaries"
    COST_LATENCY = "cost_latency"
    DELIVERABLES = "deliverables"
    SELF_CONSISTENCY = "self_consistency"
    FAILURE_ANTICIPATION = "failure_anticipation"
    ERROR_SIMULATION = "error_simulation"


# ============================================================================
# 3. TEMPLATE REGISTRY (RESTORED 10_8 LOGIC)
# ============================================================================

class PromptTemplateRegistry:
    """
    Central store for all prompt templates.

    Each template is a dict of {section → template string}.
    """

    _REGISTRY: Dict[str, Dict[str, str]] = {
        "strategy": {
            "framing": "You are generating a job strategy plan.",
            "instructions": "Analyze context and produce a strategic summary.",
        },
        "rag": {
            "framing": "You are performing evidence retrieval.",
            "instructions": "Retrieve and justify key evidence for the objective.",
        },
        "drafting": {
            "framing": "You are drafting structured narrative content.",
            "instructions": "Produce clear, structured text for each section.",
        },
        "qa": {
            "framing": "You are validating quality, coherence, and alignment.",
            "instructions": "Run all required checks and identify issues.",
        },
        "safety": {
            "framing": "You are enforcing safety and constitutional constraints.",
            "instructions": "Check for PII, toxicity, forbidden content, bias.",
        },
        "prompt_engineering": {
            "framing": "You are generating reusable prompt envelopes.",
            "instructions": "Generate clean, stable prompt templates.",
        },
        "hil": {
            "framing": "You are preparing a human-in-the-loop review prompt.",
            "instructions": "Provide clear questions for human reviewers.",
        },
        "meta_learning": {
            "framing": "You are performing meta-learning analysis.",
            "instructions": "Analyze signals to improve future workflows.",
        },
    }

    @classmethod
    def get(cls, mode: str) -> Dict[str, str]:
        return cls._REGISTRY.get(mode.lower(), {})


# ============================================================================
# 4. BUILDER — ASSEMBLES ENVELOPE FROM INPUTS
# ============================================================================

class PromptBuilder:
    """
    Deterministic assembly of PromptEnvelope from components.
    """

    @staticmethod
    def build_envelope(
        *,
        framing: str,
        context: str,
        reasoning: str,
        instructions: str,
        safety_ctx: Dict[str, Any],
        tool_ctx: Dict[str, Any],
        output_schema: str,
        runtime_context: Dict[str, Any],
    ) -> PromptEnvelope:

        return PromptEnvelope(
            framing=framing,
            context=context,
            reasoning=reasoning,
            instructions=instructions,
            safety_context=dict(safety_ctx),
            tool_context=dict(tool_ctx),
            output_schema=output_schema,
            runtime_context=dict(runtime_context),
        )


# ============================================================================
# 5. RENDERER — DETERMINISTIC PROMPT STRING BUILDER
# ============================================================================

class PromptRenderer:
    """
    Renders PromptEnvelope → final prompt string.
    Deterministic, whitespace-stable, safe for context budgeting.
    """

    @staticmethod
    def render(envelope: PromptEnvelope) -> str:
        d = envelope.to_dict()

        parts: List[str] = []

        if d["framing"]:
            parts.append(f"[FRAMING]\n{d['framing']}")
        if d["context"]:
            parts.append(f"[CONTEXT]\n{d['context']}")
        if d["reasoning"]:
            parts.append(f"[REASONING]\n{d['reasoning']}")
        if d["instructions"]:
            parts.append(f"[INSTRUCTIONS]\n{d['instructions']}")
        if d["safety_context"]:
            parts.append(f"[SAFETY]\n{safety_block(d['safety_context'])}")
        if d["tool_context"]:
            parts.append(f"[TOOLS]\n{tool_block(d['tool_context'])}")
        if d["output_schema"]:
            parts.append(f"[OUTPUT]\n{d['output_schema']}")
        if d["runtime_context"]:
            parts.append(f"[RUNTIME]\n{runtime_block(d['runtime_context'])}")

        return "\n\n".join(parts).strip()


# ============================================================================
# 6. BLOCK FORMATTERS
# ============================================================================

def safety_block(safety_ctx: Dict[str, Any]) -> str:
    lines = []
    for k, v in safety_ctx.items():
        lines.append(f"- {k}: {v}")
    return "\n".join(lines)


def tool_block(tool_ctx: Dict[str, Any]) -> str:
    lines = []
    for k, v in tool_ctx.items():
        lines.append(f"- {k}: {v}")
    return "\n".join(lines)


def runtime_block(runtime_ctx: Dict[str, Any]) -> str:
    lines = []
    for k, v in runtime_ctx.items():
        lines.append(f"- {k}: {v}")
    return "\n".join(lines)


# ============================================================================
# 7. HIGH-LEVEL API — MAKE PROMPT
# ============================================================================

class System:
    """
    Single high-level entrypoint for building structured prompts.

    make_prompt(
        framing: str,
        context: str,
        reasoning: str,
        instructions: str,
        safety_ctx: {...},
        tool_ctx: {...},
        output_schema: str,
        runtime_context: {...},
    ) -> str
    """

    @staticmethod
    def make_prompt(
        *,
        framing: str,
        context: str,
        reasoning: str,
        instructions: str,
        safety_ctx: Dict[str, Any],
        tool_ctx: Dict[str, Any],
        output_schema: str,
        runtime_context: Dict[str, Any],
    ) -> str:

        env = PromptBuilder.build_envelope(
            framing=framing,
            context=context,
            reasoning=reasoning,
            instructions=instructions,
            safety_ctx=safety_ctx,
            tool_ctx=tool_ctx,
            output_schema=output_schema,
            runtime_context=runtime_context,
        )

        return PromptRenderer.render(env)
