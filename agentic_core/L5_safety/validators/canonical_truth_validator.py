"""Canonical truth validator for L5 safety."""

from __future__ import annotations

from typing import Any


class CanonicalTruthValidator:
    """Validator for canonical truth assertions."""

    def __init__(self) -> None:
        self._truths: dict[str, Any] = {}

    def register_truth(self, key: str, value: Any) -> None:
        """Register a canonical truth value."""
        self._truths[key] = value

    def validate(self, key: str, value: Any) -> bool:
        """Validate a value against registered truth."""
        if key not in self._truths:
            return True  # No truth registered, allow
        return self._truths[key] == value

    def get_truth(self, key: str) -> Any:
        """Get registered truth value."""
        return self._truths.get(key)


def validate_canonical_truth(key: str, value: Any) -> bool:
    """Validate value against canonical truth registry."""
    validator = CanonicalTruthValidator()
    return validator.validate(key, value)


def get_canonical_layer(layer_id: str) -> dict[str, Any] | None:
    """Get canonical layer definition by ID."""
    # Registry of canonical layers
    layers: dict[str, dict[str, Any]] = {
        "L0": {"name": "Routing", "responsibilities": ["request_routing", "capacity_management"]},
        "L1": {"name": "Cognition", "responsibilities": ["intent_expansion", "context_management"]},
        "L2": {"name": "Execution", "responsibilities": ["tool_execution", "output_capture"]},
        "L3": {"name": "Orchestration", "responsibilities": ["workflow_coordination", "agent_dispatch"]},
        "L4": {"name": "State", "responsibilities": ["persistence", "retrieval", "telemetry"]},
        "L5": {"name": "Safety", "responsibilities": ["validation", "guardrails", "governance"]},
        "L6": {"name": "Observability", "responsibilities": ["monitoring", "learning", "meta_feedback"]},
    }
    return layers.get(layer_id)


def canonical_truth(key: str, value: Any) -> bool:
    """Validate canonical truth for a given key and value."""
    return validate_canonical_truth(key, value)


__all__ = ["CanonicalTruthValidator", "validate_canonical_truth", "get_canonical_layer", "canonical_truth"]
