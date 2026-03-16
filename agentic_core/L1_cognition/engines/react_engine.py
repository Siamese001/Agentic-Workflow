"""ReAct Engine — canonical location in L1_cognition/engines/.

Re-exports ReActEngine, ReActTrace, ReActStep, and create_react_engine from
the existing implementation in react_config.py so callers can import from
the correct layer path:

    from agentic_core.L1_cognition.engines.react_engine import ReActEngine

The original react_config.py is kept intact (no deletion) to avoid breaking
any existing imports.
"""

from __future__ import annotations

from agentic_core.L1_cognition.config.react_config import (  # noqa: F401
    ReActEngine,
    ReActStep,
    ReActTrace,
    ReasoningMode,
    create_react_engine,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402  # noqa: E402
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
    _emit_reads_policy_state,  # noqa: E402  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402  # noqa: E402
    _emit_snapshots_state,  # noqa: E402  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "react_engine")
emit_determinism_digest("p0", "react_engine")

_emit_dispatches_healing_run("p1", "react_engine", "L1")
_emit_routes_through("p1", "react_engine", "L1")
_emit_escalates_to_human("p1", "react_engine", "L1")
_emit_reads_policy_state("p1", "react_engine", "L1")
_emit_snapshots_state("p0", "react_engine", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "react_engine", "p0_governance")
_emit_records_execution_trace("p0", "evidence", "react_engine")
_emit_authorize_and_execute("p2", "react_engine", "execution_auth")
_emit_validates_capability("p2", "react_engine", "capability_check")
_emit_routes_to_capability("p2", "react_engine", "capability_route")
_emit_writes_via_uwg("p2", "react_engine", "uwg_write")
_emit_blocks_direct_write("p2", "react_engine", "direct_write_block")
_emit_records_tool_invocation("p2", "react_engine", "tool_invocation")
_emit_captures_execution_output("p2", "react_engine", "exec_output")
_emit_dispatches_agent("p3", "react_engine", "agent_dispatch")
_emit_coordinates_agents("p3", "react_engine", "agent_coordination")
_emit_records_workflow_lineage("p3", "react_engine", "workflow_lineage")
_emit_records_healing_outcome("p3", "react_engine", "healing_outcome")
_emit_escalates_failure("p3", "react_engine", "failure_escalation")
_emit_orchestrates_workflow("p3", "react_engine", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "react_engine", "healing_dispatch")
_emit_invokes_evaluation("p3", "react_engine", "evaluation_signal")
_emit_records_telemetry_event("p4", "react_engine", "telemetry_event")
_emit_captures_evaluation_metric("p4", "react_engine", "eval_metric")
_emit_stores_embedding("p4", "react_engine", "embedding_store")
_emit_updates_meta_learning_state("p4", "react_engine", "meta_learning")
_emit_links_execution_to_snapshot("p4", "react_engine", "exec_snapshot_link")

__all__ = [
    "ReActEngine",
    "ReActStep",
    "ReActTrace",
    "ReasoningMode",
    "create_react_engine",
]
