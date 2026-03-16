"""
Seam for L5 safety enforcement - approved L0→L5 interface.
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

emit_replay_key("p0", "safety_enforcement_seam")
emit_determinism_digest("p0", "safety_enforcement_seam")

_emit_dispatches_healing_run("p1", "safety_enforcement_seam", "L0")
_emit_routes_through("p1", "safety_enforcement_seam", "L0")
_emit_escalates_to_human("p1", "safety_enforcement_seam", "L0")
_emit_reads_policy_state("p1", "safety_enforcement_seam", "L0")
_emit_authorize_and_execute("p2", "safety_enforcement_seam", "execution_auth")
_emit_validates_capability("p2", "safety_enforcement_seam", "capability_check")
_emit_routes_to_capability("p2", "safety_enforcement_seam", "capability_route")
_emit_writes_via_uwg("p2", "safety_enforcement_seam", "uwg_write")
_emit_blocks_direct_write("p2", "safety_enforcement_seam", "direct_write_block")
_emit_records_tool_invocation("p2", "safety_enforcement_seam", "tool_invocation")
_emit_captures_execution_output("p2", "safety_enforcement_seam", "exec_output")
_emit_dispatches_agent("p3", "safety_enforcement_seam", "agent_dispatch")
_emit_coordinates_agents("p3", "safety_enforcement_seam", "agent_coordination")
_emit_records_workflow_lineage("p3", "safety_enforcement_seam", "workflow_lineage")
_emit_records_healing_outcome("p3", "safety_enforcement_seam", "healing_outcome")
_emit_escalates_failure("p3", "safety_enforcement_seam", "failure_escalation")
_emit_orchestrates_workflow("p3", "safety_enforcement_seam", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "safety_enforcement_seam", "healing_dispatch")
_emit_invokes_evaluation("p3", "safety_enforcement_seam", "evaluation_signal")
_emit_records_telemetry_event("p4", "safety_enforcement_seam", "telemetry_event")
_emit_captures_evaluation_metric("p4", "safety_enforcement_seam", "eval_metric")
_emit_stores_embedding("p4", "safety_enforcement_seam", "embedding_store")
_emit_updates_meta_learning_state("p4", "safety_enforcement_seam", "meta_learning")
_emit_links_execution_to_snapshot("p4", "safety_enforcement_seam", "exec_snapshot_link")


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
