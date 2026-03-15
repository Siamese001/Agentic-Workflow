"""
Seam for L6 vigilance event types - approved L0→L6 interface.
"""

from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)


def load_vigilance_types():
    """Load vigilance event types from L6."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "load_vigilance_types", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "load_vigilance_types", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "load_vigilance_types")
    import importlib

    return importlib.import_module("agentic_core.L6_observability.types.vigilance_event_types")


def get_vigilance_event_artifact():
    """Get VigilanceEventArtifact class."""
    return load_vigilance_types().VigilanceEventArtifact


def get_vigilance_severity():
    """Get VigilanceSeverity enum."""
    return load_vigilance_types().VigilanceSeverity
