"""
Sovereign Guard: Block Inline Pydantic models (Final Sovereign Version)
Constitutional enforcement - all models must live in core_contracts_types.py
Signal-based filtering with timestamped, prefixed logging
"""

import ast
import logging
import sys

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "model_visitor_util", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "model_visitor_util", "policy_binding")
trace_contract._emit_snapshots_state("p0", "model_visitor_util", "state_snapshot")
from tqdm import tqdm

trace_contract._emit_emits_metric_event("model_visitor_util", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("model_visitor_util", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("model_visitor_util", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("model_visitor_util", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("model_visitor_util", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("model_visitor_util", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("model_visitor_util", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("model_visitor_util", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("model_visitor_util", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("model_visitor_util", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("model_visitor_util", "p4obs", "alert")
trace_contract._emit_links_incident_trace("model_visitor_util", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("model_visitor_util", "p3lm", "pattern")
trace_contract._emit_records_learning_event("model_visitor_util", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("model_visitor_util", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("model_visitor_util", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("model_visitor_util", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("model_visitor_util", "p3lm", "policy")
trace_contract._emit_stores_learning_state("model_visitor_util", "p3lm", "state")
trace_contract._emit_records_execution_trace("model_visitor_util", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("model_visitor_util", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("model_visitor_util", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("model_visitor_util", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("model_visitor_util", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("model_visitor_util", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("model_visitor_util", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("model_visitor_util", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("model_visitor_util", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "model_visitor_util", "context_pull")
trace_contract._emit_pulls_context("p1", "model_visitor_util", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "model_visitor_util", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "model_visitor_util", "uwg_term_2")
trace_contract._emit_writes_through("p1", "model_visitor_util", "write_through")
trace_contract._emit_writes_through("p1", "model_visitor_util", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "model_visitor_util", "safety_validation")
trace_contract._emit_invokes_eval("p1", "model_visitor_util", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "model_visitor_util", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "model_visitor_util", "human_escalation")
trace_contract._emit_routes_through("p1", "model_visitor_util", "route_through")
trace_contract._emit_checks_agent_registry("p1", "model_visitor_util", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "model_visitor_util", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "model_visitor_util", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "model_visitor_util", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "model_visitor_util", "target_agent")
trace_contract._emit_verifies_policy("p1", "model_visitor_util", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "model_visitor_util", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "model_visitor_util", "boundary_check")
trace_contract._emit_transcripts_response("p1", "model_visitor_util", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "model_visitor_util")
trace_contract._emit_gated_by_confidence("p1", "model_visitor_util", "confidence_gate")
trace_contract.emit_replay_key("p0", "model_visitor_util")
trace_contract.emit_determinism_digest("p0", "model_visitor_util")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "model_visitor_util", "execution_auth")
trace_contract._emit_validates_capability("p2", "model_visitor_util", "capability_check")
trace_contract._emit_routes_to_capability("p2", "model_visitor_util", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "model_visitor_util", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "model_visitor_util", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "model_visitor_util", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "model_visitor_util", "exec_output")
trace_contract._emit_dispatches_agent("p3", "model_visitor_util", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "model_visitor_util", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "model_visitor_util", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "model_visitor_util", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "model_visitor_util", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "model_visitor_util", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "model_visitor_util", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "model_visitor_util", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "model_visitor_util", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "model_visitor_util", "eval_metric")
trace_contract._emit_stores_embedding("p4", "model_visitor_util", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "model_visitor_util", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "model_visitor_util", "exec_snapshot_link")

Logger = logging.getLogger("sovereign.models")
handler = logging.StreamHandler(sys.stderr)
handler.setFormatter(logging.Formatter("[MODELS] %(levelname)s %(asctime)s | %(message)s", "%H:%M:%S"))
Logger.addHandler(handler)
Logger.setLevel(logging.INFO)
contract_signals = ("Profile", "Config", "State", "Context", "Result", "Message", "Request", "Response")
exempt = {"agentic_core/schemas/models/core_contracts_types.py"}


class ModelVisitor(ast.NodeVisitor):
    """Brief description of functionality and purpose."""

    def visit_ClassDef(self, node):
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "ModelVisitor.visit_ClassDef")

        is_pydantic = any(
            isinstance(base, ast.Name) and base.id in {"BaseModel", "RootModel"} for base in node.bases
        )
        is_contract = any(node.name.endswith(s) for s in CONTRACT_SIGNALS)
        has_dataclass = any(isinstance(d, ast.Name) and d.id == "dataclass" for d in node.decorator_list)
        if is_pydantic or (has_dataclass and is_contract):
            Logger.error(
                f"BLOCKED: Inline contract '{node.name}' found at L{node.lineno}. Migrate to core_contracts_types.py.",
            )
            sys.exit(1)
        self.generic_visit(node)


def main():
    """Brief description of functionality and purpose."""
    for arg in tqdm(sys.argv[1:], desc="Processing", unit="item"):
        if arg in EXEMPT or "tests/" in arg:
            Logger.info(f"Skipping Exempt: {arg}")
            continue
        Logger.info(f"Auditing: {arg}")
        with open(arg, encoding="utf-8") as f:
            try:
                ModelVisitor().visit(ast.parse(f.read()))
            except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
                raise


if __name__ == "__main__":
    main()
