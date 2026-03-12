"""
Seam for layer emission validation - approved L0→L5 interface.

This seam provides a controlled interface for L0 types to validate
layer emission permissions without direct L5 imports.
"""
from __future__ import annotations
from typing import Protocol
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

class LayerEmissionValidator(Protocol):
    """Protocol for layer emission validation."""

    def validate_emission(self, artifact_type: str, emitting_layer: str, trace_id: str) -> None:
        """Validate that a layer may emit a specific artifact type."""
        ...

def get_layer_emission_validator() -> LayerEmissionValidator:
    """Get the layer emission validator implementation.

    This function uses dynamic import to avoid static L0→L5 dependency
    while providing runtime access to L5 validation logic.
    """
    import importlib
    try:
        module = importlib.import_module('agentic_core.L5_safety.enforcement.artifact_emission_prohibition_enforcer')
        return module
    except ImportError as e:
        raise RuntimeError(f'Failed to load layer emission validator: {e}')

def assert_layer_may_emit(artifact_type: str, emitting_layer: str, trace_id: str) -> None:
    """Assert that a layer may emit a specific artifact type.

    This is the approved interface for L0 types to validate emissions.
    """
    validator = get_layer_emission_validator()
    validator.validate_emission(artifact_type, emitting_layer, trace_id)
