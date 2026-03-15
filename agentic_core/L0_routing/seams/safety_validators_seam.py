"""
Seam for L5 safety validators - approved L0→L5 interface.
"""

from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)


def load_hygiene_guardian():
    """Load HygieneGuardianAgent from L5."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "load_hygiene_guardian", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "load_hygiene_guardian", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "load_hygiene_guardian")
    import importlib

    mod = importlib.import_module("agentic_core.L5_safety.validators.HygieneGuardianAgent")
    return mod.HygieneGuardianAgent


def load_autonomy_guardian():
    """Load AutonomyGuardianAgent from L5."""
    import importlib

    mod = importlib.import_module("agentic_core.L5_safety.validators.AutonomyGuardianAgent")
    return mod.AutonomyGuardianAgent


def load_healing_strategy():
    """Load healing_strategy module from L5."""
    import importlib

    return importlib.import_module("agentic_core.L5_safety.validators.healing_strategy")


def load_canonical_truth_validator():
    """Load canonical_truth_validator from L5."""
    import importlib

    return importlib.import_module("agentic_core.L5_safety.validators.canonical_truth_validator")


def load_cognitive_disposition_agent():
    """Load CognitiveDispositionAgent from L5."""
    import importlib

    mod = importlib.import_module("agentic_core.L5_safety.validators.CognitiveDispositionAgent")
    return mod.CognitiveDispositionAgent


def load_dashboard_ssot_definitions():
    """Load dashboard_ssot_definitions_config from L5."""
    import importlib

    return importlib.import_module("agentic_core.L5_safety.validators.dashboard_ssot_definitions_config")
