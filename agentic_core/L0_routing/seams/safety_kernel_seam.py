"""
Seam for L5 safety core kernel - approved L0→L5 interface.
"""

from __future__ import annotations

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

emit_replay_key("p0", "safety_kernel_seam")
emit_determinism_digest("p0", "safety_kernel_seam")

_emit_dispatches_healing_run("p1", "safety_kernel_seam", "L0")
_emit_routes_through("p1", "safety_kernel_seam", "L0")
_emit_escalates_to_human("p1", "safety_kernel_seam", "L0")
_emit_reads_policy_state("p1", "safety_kernel_seam", "L0")


def load_classification_kernel():
    """Load classification_kernel from L5."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "load_classification_kernel", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "load_classification_kernel", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "load_classification_kernel")
    import importlib

    return importlib.import_module("agentic_core.L5_safety.core_kernel.classification_kernel")


def get_classification_cache_context():
    """Get classification_cache_context from L5."""
    return load_classification_kernel().classification_cache_context
