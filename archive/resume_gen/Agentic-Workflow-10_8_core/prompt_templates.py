"""
Prompt Templates

Responsibilities:
    • House reusable prompt blueprints for various agentic roles and tasks.
    • Remain decoupled from rendering mechanics while supporting parameterization.
    • Provide structured metadata to inform safety and policy layers.

This file is scaffolded for Priority 0; implementation comes later.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict

from prompt_envelope import PromptEnvelope
from prompt_taxonomy import INSTRUCTIONAL_INJECTION_ALL, PromptSection


DEFAULT_TEMPLATE = {
    "Framing": "You are an orchestrator coordinating deterministic agents.",
    "Context": "Use the provided state to ground your response.",
    "Reasoning": "Keep reasoning minimal; downstream layers handle cognition.",
    "Instructions": "Follow the requested format and stay within scope.",
    "Safety Signals": "Respect safety directives from the gateway.",
    "Output Schema": "Return plain text content respecting the schema.",
}

DEFAULT_TEMPLATE_INJECTION = {
    "reason_then_answer": True
}

DEFAULT_TEMPLATE_OUTPUT_INJECTION = {
    "strict_json_output": False,
    "schema_enforcement": False,
    "stability_contracts": True,
    "error_normalization": True,
    "minimality_constraints": True,
}

DEFAULT_TEMPLATE_METADATA = {
    "taxonomy": {
        "sections": [s.value for s in PromptSection],
        "instructional_injection_types": INSTRUCTIONAL_INJECTION_ALL,
    },
    "injection_reasoning": DEFAULT_TEMPLATE_INJECTION,
    "stable_ordering": True,
    "taxonomy_version": "v5",
}

DEFAULT_TEMPLATE_METADATA["output_injection"] = DEFAULT_TEMPLATE_OUTPUT_INJECTION


def load_template(name: str | None = None) -> Dict[str, str]:
    """Return a copy of a known template by name."""

    if name in (None, "default"):
        return deepcopy(DEFAULT_TEMPLATE)
    raise ValueError(f"Unknown template: {name}")


def envelope_from_template(name: str | None = None, overrides: Dict[str, Any] | None = None) -> PromptEnvelope:
    """Create a PromptEnvelope from a named template with optional overrides."""

    template = load_template(name)
    overrides = overrides or {}
    metadata = overrides.get("metadata")
    if metadata is None:
        metadata = deepcopy(DEFAULT_TEMPLATE_METADATA)
    else:
        metadata = deepcopy(metadata)
        metadata.setdefault("taxonomy_version", "v5")

    envelope = PromptEnvelope(
        framing=overrides.get("framing", template.get("Framing", "")),
        context=overrides.get("context", template.get("Context", "")),
        reasoning=overrides.get("reasoning", template.get("Reasoning", "")),
        instructions=overrides.get("instructions", template.get("Instructions", "")),
        safety_signals=overrides.get("safety_signals", template.get("Safety Signals", "")),
        output_schema=overrides.get("output_schema", template.get("Output Schema", "")),
        metadata=metadata,
    )
    return envelope
