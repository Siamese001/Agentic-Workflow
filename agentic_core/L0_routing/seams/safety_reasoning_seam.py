"""
Seam for L5 safety reasoning agents - approved L0→L5 interface.
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
)

_emit_dispatches_healing_run("p1", "safety_reasoning_seam", "L0")
_emit_routes_through("p1", "safety_reasoning_seam", "L0")
_emit_escalates_to_human("p1", "safety_reasoning_seam", "L0")
_emit_reads_policy_state("p1", "safety_reasoning_seam", "L0")


def load_naming_agent():
    """Load NamingAgent from L5."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "load_naming_agent", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "load_naming_agent", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "load_naming_agent")
    import importlib

    mod = importlib.import_module("agentic_core.L5_safety.reasoning.NamingAgent")
    return mod.NamingAgent


def load_structure_enforcer_agent():
    """Load StructureEnforcerAgent from L5."""
    import importlib

    mod = importlib.import_module("agentic_core.L5_safety.reasoning.StructureEnforcerAgent")
    return mod.StructureEnforcerAgent


def load_cognitive_disposition_agent():
    """Load CognitiveDispositionAgent from L5 reasoning."""
    import importlib

    mod = importlib.import_module("agentic_core.L5_safety.reasoning.CognitiveDispositionAgent")
    return mod.CognitiveDispositionAgent


def load_file_classification_agent():
    """Load FileClassificationAgent from L5."""
    import importlib

    mod = importlib.import_module("agentic_core.L5_safety.reasoning.FileClassificationAgent")
    return mod.FileClassificationAgent


def load_location_validator_agent():
    """Load LocationValidatorAgent from L5."""
    import importlib

    mod = importlib.import_module("agentic_core.L5_safety.reasoning.location_validator")
    return mod.LocationValidatorAgent


def load_verification_gate_adapter():
    """Load verification_gate_adapter from L5."""
    import importlib

    return importlib.import_module("agentic_core.L5_safety.reasoning.verification_gate_adapter")


def load_human_review_adapter():
    """Load human_review_adapter from L5."""
    import importlib

    return importlib.import_module("agentic_core.L5_safety.reasoning.human_review_adapter")


def load_inspector_executor():
    """Load InspectorExecutor from L5."""
    import importlib

    mod = importlib.import_module("agentic_core.L5_safety.reasoning.InspectorExecutor")
    return mod.InspectorExecutor
