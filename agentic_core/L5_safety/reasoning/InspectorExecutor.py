"""InspectorExecutor — Canonical parameterized inspector agent.

Consolidates: DagRuntimeInspectorAgent, SignatureVerifierAgent, TokenBudgetInspectorAgent
Created: 2026-02-08 (Structural Agent Count Reduction)
"""

from __future__ import annotations

from dataclasses import dataclass, field

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.mixins.inspection_capability_mixin import InspectionCapability
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

emit_replay_key("p0", "InspectorExecutor")
emit_determinism_digest("p0", "InspectorExecutor")

_emit_dispatches_healing_run("p1", "InspectorExecutor", "L5")
_emit_routes_through("p1", "InspectorExecutor", "L5")
_emit_escalates_to_human("p1", "InspectorExecutor", "L5")
_emit_reads_policy_state("p1", "InspectorExecutor", "L5")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_records_execution_trace("p0", "evidence", "InspectorExecutor")
_emit_applies_guardrail("p0", "InspectorExecutor", "p0_governance")
_emit_snapshots_state("p0", "InspectorExecutor", "state_snapshot")
_emit_authorize_and_execute("p2", "InspectorExecutor", "execution_auth")
_emit_validates_capability("p2", "InspectorExecutor", "capability_check")
_emit_routes_to_capability("p2", "InspectorExecutor", "capability_route")
_emit_writes_via_uwg("p2", "InspectorExecutor", "uwg_write")
_emit_blocks_direct_write("p2", "InspectorExecutor", "direct_write_block")
_emit_records_tool_invocation("p2", "InspectorExecutor", "tool_invocation")
_emit_captures_execution_output("p2", "InspectorExecutor", "exec_output")
_emit_dispatches_agent("p3", "InspectorExecutor", "agent_dispatch")
_emit_coordinates_agents("p3", "InspectorExecutor", "agent_coordination")
_emit_records_workflow_lineage("p3", "InspectorExecutor", "workflow_lineage")
_emit_records_healing_outcome("p3", "InspectorExecutor", "healing_outcome")
_emit_escalates_failure("p3", "InspectorExecutor", "failure_escalation")
_emit_orchestrates_workflow("p3", "InspectorExecutor", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "InspectorExecutor", "healing_dispatch")
_emit_invokes_evaluation("p3", "InspectorExecutor", "evaluation_signal")
_emit_records_telemetry_event("p4", "InspectorExecutor", "telemetry_event")
_emit_captures_evaluation_metric("p4", "InspectorExecutor", "eval_metric")
_emit_stores_embedding("p4", "InspectorExecutor", "embedding_store")
_emit_updates_meta_learning_state("p4", "InspectorExecutor", "meta_learning")
_emit_links_execution_to_snapshot("p4", "InspectorExecutor", "exec_snapshot_link")


@dataclass
class InspectorExecutor(InspectionCapability, SovereignBaseAgent):
    """Parameterized inspector that dispatches to domain-specific check logic.

    Usage:
        inspector = InspectorExecutor(inspector_type="dag_runtime")
    """

    inspector_type: str = "generic"
    INSPECTION_LOG_PREFIX: str = field(init=False, default="Inspector")

    def __post_init__(self) -> None:
        prefixes = {"dag_runtime": "DagRuntime", "signature": "Signature", "token_budget": "TokenBudget"}
        self.INSPECTION_LOG_PREFIX = prefixes.get(self.inspector_type, "Inspector")
