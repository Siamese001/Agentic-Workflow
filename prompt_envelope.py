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

    def to_dict(self) -> Dict[str, Any]:
        """Materialize the envelope as a serializable dictionary."""

        metadata = dict(self.metadata)
        metadata["instructional_injection_types"] = INSTRUCTIONAL_INJECTION_ALL

        data = {"sections": self.to_sections(), "metadata": metadata}
        return data
