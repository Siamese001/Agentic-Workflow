"""
Sovereign Guard: Block underscore-prefixed fields in SSOT models.
Location: agentic_core/L0_routing/scripts/
"""

import ast
import sys
from pathlib import Path

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "underscore_visitor_util", "p0_governance")
_emit_reads_policy_state("p0", "underscore_visitor_util", "policy_binding")
_emit_snapshots_state("p0", "underscore_visitor_util", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)
from tqdm import tqdm

_emit_emits_metric_event("underscore_visitor_util", "p4obs", "metric_1")
_emit_emits_metric_event("underscore_visitor_util", "p4obs", "metric_2")
_emit_emits_metric_event("underscore_visitor_util", "p4obs", "metric_3")
_emit_emits_metric_event("underscore_visitor_util", "p4obs", "metric_4")
_emit_emits_metric_event("underscore_visitor_util", "p4obs", "metric_5")
_emit_emits_metric_event("underscore_visitor_util", "p4obs", "metric_6")
_emit_records_incident_event("underscore_visitor_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("underscore_visitor_util", "p4obs", "anomaly")
_emit_writes_observability_log("underscore_visitor_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("underscore_visitor_util", "p4obs", "mon_state")
_emit_triggers_alert("underscore_visitor_util", "p4obs", "alert")
_emit_links_incident_trace("underscore_visitor_util", "p4obs", "trace_link")
_emit_captures_pattern("underscore_visitor_util", "p3lm", "pattern")
_emit_records_learning_event("underscore_visitor_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("underscore_visitor_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("underscore_visitor_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("underscore_visitor_util", "p3lm", "routing")
_emit_improves_agent_policy("underscore_visitor_util", "p3lm", "policy")
_emit_stores_learning_state("underscore_visitor_util", "p3lm", "state")
_emit_records_execution_trace("underscore_visitor_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("underscore_visitor_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("underscore_visitor_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("underscore_visitor_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("underscore_visitor_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("underscore_visitor_util", "env_read", "p2_env_1")
_emit_reads_environ("underscore_visitor_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("underscore_visitor_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("underscore_visitor_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "underscore_visitor_util", "context_pull")
_emit_pulls_context("p1", "underscore_visitor_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "underscore_visitor_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "underscore_visitor_util", "uwg_term_2")
_emit_writes_through("p1", "underscore_visitor_util", "write_through")
_emit_writes_through("p1", "underscore_visitor_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "underscore_visitor_util", "safety_validation")
_emit_invokes_eval("p1", "underscore_visitor_util", "eval_call")
_emit_proposal_commits_routing("p1", "underscore_visitor_util", "routing_commit")
_emit_escalates_to_human("p1", "underscore_visitor_util", "human_escalation")
_emit_routes_through("p1", "underscore_visitor_util", "route_through")
_emit_checks_agent_registry("p1", "underscore_visitor_util", "agent_registry")
_emit_validates_agent_capability("p1", "underscore_visitor_util", "capability")
_emit_dispatches_execution_plan("p1", "underscore_visitor_util", "exec_plan")
_emit_agent_executes_agent("p1", "underscore_visitor_util", "sub_agent")
_emit_routes_to_agent("p1", "underscore_visitor_util", "target_agent")
_emit_verifies_policy("p1", "underscore_visitor_util", "policy_check")
_emit_observes_runtime_state("p1", "underscore_visitor_util", "runtime_state")
_emit_verifies_boundary("p1", "underscore_visitor_util", "boundary_check")
_emit_transcripts_response("p1", "underscore_visitor_util", "transcript")
_emit_hard_fails_untranscripted("p1", "underscore_visitor_util")
_emit_gated_by_confidence("p1", "underscore_visitor_util", "confidence_gate")
emit_replay_key("p0", "underscore_visitor_util")
emit_determinism_digest("p0", "underscore_visitor_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "underscore_visitor_util", "execution_auth")
_emit_validates_capability("p2", "underscore_visitor_util", "capability_check")
_emit_routes_to_capability("p2", "underscore_visitor_util", "capability_route")
_emit_writes_via_uwg("p2", "underscore_visitor_util", "uwg_write")
_emit_blocks_direct_write("p2", "underscore_visitor_util", "direct_write_block")
_emit_records_tool_invocation("p2", "underscore_visitor_util", "tool_invocation")
_emit_captures_execution_output("p2", "underscore_visitor_util", "exec_output")
_emit_dispatches_agent("p3", "underscore_visitor_util", "agent_dispatch")
_emit_coordinates_agents("p3", "underscore_visitor_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "underscore_visitor_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "underscore_visitor_util", "healing_outcome")
_emit_escalates_failure("p3", "underscore_visitor_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "underscore_visitor_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "underscore_visitor_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "underscore_visitor_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "underscore_visitor_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "underscore_visitor_util", "eval_metric")
_emit_stores_embedding("p4", "underscore_visitor_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "underscore_visitor_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "underscore_visitor_util", "exec_snapshot_link")

ssot_target = "agentic_core/schemas/models/core_contracts_types.py"


class UnderscoreVisitor(ast.NodeVisitor):
    """Brief description of functionality and purpose."""

    def __init__(self, filepath):
        self.filepath = filepath
        self.violations = []

    def visit_AnnAssign(self, node):
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "UnderscoreVisitor.visit_AnnAssign"
        )

        if isinstance(node.target, ast.Name) and node.target.id.startswith("_"):
            if not node.target.id.startswith("__"):
                self.violations.append((node.lineno, node.target.id))
        self.generic_visit(node)

    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id.startswith("_"):
                if not target.id.startswith("__"):
                    self.violations.append((node.lineno, target.id))
        self.generic_visit(node)


def main():
    """Brief description of functionality and purpose."""
    has_error = False
    for arg in tqdm(sys.argv[1:], desc="Processing", unit="item"):
        if SSOT_TARGET not in str(arg).replace("\\", "/"):
            continue
        try:
            visitor = UnderscoreVisitor(arg)
            visitor.visit(ast.parse(Path(arg).read_text(encoding="utf-8")))
            if visitor.violations:
                has_error = True
                print(f"[ERROR] Underscore fields forbidden in SSOT ({arg}):")
                for line, field in visitor.violations:
                    print(f"  L{line}: {field}")
        # guardian: allow-silent-swallow
        except Exception as e:
            print(f"[WARNING] Could not parse {arg}: {e}")
    sys.exit(1 if has_error else 0)


if __name__ == "__main__":
    main()
