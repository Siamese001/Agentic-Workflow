"""
Prompt Envelope

Responsibilities:
    • Define the outer prompt structure used across agentic interactions.
    • Provide hooks for layering safety, policy, and orchestration metadata.
    • Remain agnostic to specific templates while enabling consistent rendering.

This file is scaffolded for Priority 0; implementation comes later.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict

from injection_profiles import DEFAULT_CONTEXT_PROFILE, DEFAULT_FRAMING_PROFILE
from injection_tooling_profiles import DEFAULT_TOOLING_PROFILE
from prompt_taxonomy import INSTRUCTIONAL_INJECTION_ALL, PromptSection


@dataclass
class PromptEnvelope:
    """Structured container for assembling deterministic prompts."""

    framing: str = ""
    context: str = ""
    reasoning: str = ""
    instructions: str = ""
    safety_signals: str = ""
    output_schema: str = ""
    metadata: Dict[str, Any] = field(
        default_factory=lambda: {
            "taxonomy": {
                "sections": [s.value for s in PromptSection],
                "instructional_injection_types": INSTRUCTIONAL_INJECTION_ALL,
            }
        }
    )

    def to_sections(self) -> Dict[str, str]:
        """Return an ordered mapping of envelope sections."""

        return {
            "Framing": self.framing.strip(),
            "Context": self.context.strip(),
            "Reasoning": self.reasoning.strip(),
            "Instructions": self.instructions.strip(),
            "Safety Signals": self.safety_signals.strip(),
            "Output Schema": self.output_schema.strip(),
        }

    def to_dict(self, plan: Dict[str, Any] | None = None) -> Dict[str, Any]:
        """Materialize the envelope as a serializable dictionary."""

        metadata = dict(self.metadata)
        metadata["instructional_injection_types"] = INSTRUCTIONAL_INJECTION_ALL
        metadata["routing"] = (plan or {}).get("routing", {})
        from prompt_templates import DEFAULT_TEMPLATE_OUTPUT_INJECTION

        metadata["injection"] = {
            "framing": {
                "global_goal": DEFAULT_FRAMING_PROFILE.global_goal,
                "success_criteria": DEFAULT_FRAMING_PROFILE.success_criteria,
                "task_mode": DEFAULT_FRAMING_PROFILE.task_mode,
            },
            "context": {
                "untrusted_block_wrapping": DEFAULT_CONTEXT_PROFILE.untrusted_block_wrapping,
                "canonicalize_inputs": DEFAULT_CONTEXT_PROFILE.canonicalize_inputs,
                "apply_pruning_rules": DEFAULT_CONTEXT_PROFILE.apply_pruning_rules,
                "enforce_structured_ordering": DEFAULT_CONTEXT_PROFILE.enforce_structured_ordering,
            },
            "tooling": {
                "model_switch_awareness": DEFAULT_TOOLING_PROFILE.model_switch_awareness
            },
            "output": DEFAULT_TEMPLATE_OUTPUT_INJECTION,
        }

        data = {"sections": self.to_sections(), "metadata": metadata}
        return data
