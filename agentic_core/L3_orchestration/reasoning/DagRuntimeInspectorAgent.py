"""CONSOLIDATED: DagRuntimeInspectorAgent → InspectorExecutor (2026-02-08).

This file is a backward-compatibility shim.
Import the canonical executor directly for new code.
"""

import importlib as _importlib

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
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
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "DagRuntimeInspectorAgent")
emit_determinism_digest("p0", "DagRuntimeInspectorAgent")

_emit_dispatches_healing_run("p1", "DagRuntimeInspectorAgent", "L3")
_emit_routes_through("p1", "DagRuntimeInspectorAgent", "L3")
_emit_escalates_to_human("p1", "DagRuntimeInspectorAgent", "L3")
_emit_reads_policy_state("p1", "DagRuntimeInspectorAgent", "L3")

_emit_snapshots_state("p0", "DagRuntimeInspectorAgent", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "DagRuntimeInspectorAgent", "p0_governance")
_emit_records_execution_trace("p0", "evidence", "DagRuntimeInspectorAgent")
_emit_authorize_and_execute("p2", "DagRuntimeInspectorAgent", "execution_auth")
_emit_validates_capability("p2", "DagRuntimeInspectorAgent", "capability_check")
_emit_routes_to_capability("p2", "DagRuntimeInspectorAgent", "capability_route")
_emit_writes_via_uwg("p2", "DagRuntimeInspectorAgent", "uwg_write")
_emit_blocks_direct_write("p2", "DagRuntimeInspectorAgent", "direct_write_block")
_emit_records_tool_invocation("p2", "DagRuntimeInspectorAgent", "tool_invocation")
_emit_captures_execution_output("p2", "DagRuntimeInspectorAgent", "exec_output")
_emit_dispatches_agent("p3", "DagRuntimeInspectorAgent", "agent_dispatch")
_emit_coordinates_agents("p3", "DagRuntimeInspectorAgent", "agent_coordination")
_emit_records_workflow_lineage("p3", "DagRuntimeInspectorAgent", "workflow_lineage")
_emit_records_healing_outcome("p3", "DagRuntimeInspectorAgent", "healing_outcome")
_emit_escalates_failure("p3", "DagRuntimeInspectorAgent", "failure_escalation")
_emit_orchestrates_workflow("p3", "DagRuntimeInspectorAgent", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "DagRuntimeInspectorAgent", "healing_dispatch")
_emit_invokes_evaluation("p3", "DagRuntimeInspectorAgent", "evaluation_signal")
_emit_records_telemetry_event("p4", "DagRuntimeInspectorAgent", "telemetry_event")
_emit_captures_evaluation_metric("p4", "DagRuntimeInspectorAgent", "eval_metric")
_emit_stores_embedding("p4", "DagRuntimeInspectorAgent", "embedding_store")
_emit_updates_meta_learning_state("p4", "DagRuntimeInspectorAgent", "meta_learning")
_emit_links_execution_to_snapshot("p4", "DagRuntimeInspectorAgent", "exec_snapshot_link")

_mod = _importlib.import_module("agentic_core.L5_safety.reasoning.InspectorExecutor")
DagRuntimeInspectorAgent = _mod.InspectorExecutor
__all__ = ["DagRuntimeInspectorAgent"]
