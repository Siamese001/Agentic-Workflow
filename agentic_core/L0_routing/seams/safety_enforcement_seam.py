"""
Seam for L5 safety enforcement - approved L0→L5 interface.
"""

from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)


def load_code_deduplication_agent():
    """Load CodeDeduplicationAgent from L5."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "load_code_deduplication_agent", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "load_code_deduplication_agent", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "load_code_deduplication_agent")
    import importlib

    mod = importlib.import_module("agentic_core.L5_safety.enforcement.CodeDeduplicationAgent")
    return mod.CodeDeduplicationAgent


def load_archival_gatekeeper():
    """Load archival_gatekeeper from L5."""
    import importlib

    return importlib.import_module("agentic_core.L5_safety.enforcement.archival_gatekeeper_gate")


def load_ssot_scanner():
    """Load ssot_scanner from L5."""
    import importlib

    return importlib.import_module("agentic_core.L5_safety.enforcement.ssot_scanner_enforcer")


def load_activation_gate():
    """Load activation_gate from L5 — approved seam for healing approval mediation."""
    import importlib

    return importlib.import_module("agentic_core.L5_safety.enforcement.activation_gate")
