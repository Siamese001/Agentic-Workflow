"""
Seam for layer emission validation - approved L0→L5 interface.

This seam provides a controlled interface for L0 types to validate
layer emission permissions without direct L5 imports.
"""

from __future__ import annotations

from typing import Protocol

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "layer_emission_seam")
emit_determinism_digest("p0", "layer_emission_seam")

_emit_dispatches_healing_run("p1", "layer_emission_seam", "L0")
_emit_routes_through("p1", "layer_emission_seam", "L0")
_emit_escalates_to_human("p1", "layer_emission_seam", "L0")
_emit_reads_policy_state("p1", "layer_emission_seam", "L0")


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
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "get_layer_emission_validator", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "get_layer_emission_validator", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "get_layer_emission_validator")
    import importlib

    try:
        module = importlib.import_module(
            "agentic_core.L5_safety.enforcement.artifact_emission_prohibition_enforcer"
        )
        return module
    except ImportError as e:
        raise RuntimeError(f"Failed to load layer emission validator: {e}")


def assert_layer_may_emit(artifact_type: str, emitting_layer: str, trace_id: str) -> None:
    """Assert that a layer may emit a specific artifact type.

    This is the approved interface for L0 types to validate emissions.
    """
    validator = get_layer_emission_validator()
    validator.validate_emission(artifact_type, emitting_layer, trace_id)
