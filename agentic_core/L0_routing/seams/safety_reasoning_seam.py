"""
Seam for L5 safety reasoning agents - approved L0→L5 interface.
"""

from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "safety_reasoning_seam")
emit_determinism_digest("p0", "safety_reasoning_seam")

_emit_dispatches_healing_run("p1", "safety_reasoning_seam", "L0")
_emit_routes_through("p1", "safety_reasoning_seam", "L0")
_emit_escalates_to_human("p1", "safety_reasoning_seam", "L0")
_emit_reads_policy_state("p1", "safety_reasoning_seam", "L0")
_emit_authorize_and_execute("p2", "safety_reasoning_seam", "execution_auth")
_emit_validates_capability("p2", "safety_reasoning_seam", "capability_check")
_emit_routes_to_capability("p2", "safety_reasoning_seam", "capability_route")
_emit_writes_via_uwg("p2", "safety_reasoning_seam", "uwg_write")
_emit_blocks_direct_write("p2", "safety_reasoning_seam", "direct_write_block")
_emit_records_tool_invocation("p2", "safety_reasoning_seam", "tool_invocation")
_emit_captures_execution_output("p2", "safety_reasoning_seam", "exec_output")
_emit_dispatches_agent("p3", "safety_reasoning_seam", "agent_dispatch")
_emit_coordinates_agents("p3", "safety_reasoning_seam", "agent_coordination")
_emit_records_workflow_lineage("p3", "safety_reasoning_seam", "workflow_lineage")
_emit_records_healing_outcome("p3", "safety_reasoning_seam", "healing_outcome")
_emit_escalates_failure("p3", "safety_reasoning_seam", "failure_escalation")
_emit_orchestrates_workflow("p3", "safety_reasoning_seam", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "safety_reasoning_seam", "healing_dispatch")
_emit_invokes_evaluation("p3", "safety_reasoning_seam", "evaluation_signal")
_emit_records_telemetry_event("p4", "safety_reasoning_seam", "telemetry_event")
_emit_captures_evaluation_metric("p4", "safety_reasoning_seam", "eval_metric")
_emit_stores_embedding("p4", "safety_reasoning_seam", "embedding_store")
_emit_updates_meta_learning_state("p4", "safety_reasoning_seam", "meta_learning")
_emit_links_execution_to_snapshot("p4", "safety_reasoning_seam", "exec_snapshot_link")


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
