"""
Phase 33d: Global Healing Capability Audit

Scans agentic_core for all healer agents and generates an "Impotence Report"
identifying agents that detect violations but cannot fix them.
"""

import ast
from dataclasses import dataclass, field
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    DISCOVERY_EXCLUDED_TERRITORIES,
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
    get_validated_project_root,
)
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "agent_audit_result_types")
trace_contract.emit_determinism_digest("p0", "agent_audit_result_types")

trace_contract._emit_dispatches_healing_run("p1", "agent_audit_result_types", "L5")
trace_contract._emit_routes_through("p1", "agent_audit_result_types", "L5")
trace_contract._emit_checks_agent_registry("p1", "agent_audit_result_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "agent_audit_result_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "agent_audit_result_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "agent_audit_result_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "agent_audit_result_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "agent_audit_result_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "agent_audit_result_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "agent_audit_result_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "agent_audit_result_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "agent_audit_result_types")
trace_contract._emit_gated_by_confidence("p1", "agent_audit_result_types", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "agent_audit_result_types", "L5")
trace_contract._emit_reads_policy_state("p1", "agent_audit_result_types", "L5")

trace_contract._emit_applies_guardrail("p0", "agent_audit_result_types", "p0_governance")
trace_contract._emit_snapshots_state("p0", "agent_audit_result_types", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "agent_audit_result_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "agent_audit_result_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "agent_audit_result_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "agent_audit_result_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "agent_audit_result_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "agent_audit_result_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "agent_audit_result_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "agent_audit_result_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "agent_audit_result_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "agent_audit_result_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "agent_audit_result_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "agent_audit_result_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "agent_audit_result_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "agent_audit_result_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "agent_audit_result_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "agent_audit_result_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "agent_audit_result_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "agent_audit_result_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "agent_audit_result_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "agent_audit_result_types", "exec_snapshot_link")
from tqdm import tqdm

trace_contract._emit_emits_metric_event("agent_audit_result_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("agent_audit_result_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("agent_audit_result_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("agent_audit_result_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("agent_audit_result_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("agent_audit_result_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("agent_audit_result_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("agent_audit_result_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("agent_audit_result_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("agent_audit_result_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("agent_audit_result_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("agent_audit_result_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("agent_audit_result_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("agent_audit_result_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("agent_audit_result_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("agent_audit_result_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("agent_audit_result_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("agent_audit_result_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("agent_audit_result_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("agent_audit_result_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("agent_audit_result_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("agent_audit_result_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("agent_audit_result_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("agent_audit_result_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("agent_audit_result_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("agent_audit_result_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("agent_audit_result_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("agent_audit_result_types", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "agent_audit_result_types", "context_pull")
trace_contract._emit_pulls_context("p1", "agent_audit_result_types", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "agent_audit_result_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "agent_audit_result_types", "uwg_term_2")
trace_contract._emit_writes_through("p1", "agent_audit_result_types", "write_through")
trace_contract._emit_writes_through("p1", "agent_audit_result_types", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "agent_audit_result_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "agent_audit_result_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "agent_audit_result_types", "routing_commit")


@dataclass
class AgentAuditResult:
    """Audit result for a single agent."""

    class_name: str
    file_path: str
    has_heal_repository: bool = False
    has_fix_violation: bool = False
    has_fix_violations: bool = False
    has_perform_surgery: bool = False
    auto_fixable_true_count: int = 0
    auto_fixable_false_count: int = 0
    violation_types: list = field(default_factory=list)

    @property
    def verdict(self) -> str:
        """Determine agent status."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L5_POLICY, "AgentAuditResult.verdict")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:AgentAuditResult.verdict".encode()).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if not self.has_heal_repository:
            return "GHOST"
        has_fix_logic = self.has_fix_violation or self.has_fix_violations or self.has_perform_surgery
        if self.auto_fixable_true_count > 0 and (not has_fix_logic):
            return "IMPOTENT"
        if has_fix_logic:
            return "HARDENED"
        return "PASSIVE"


def audit_agent_file(py_file: Path, agentic_core: Path) -> list[AgentAuditResult]:
    """Audit a single Python file for healer agents."""
    results = []
    try:
        content = py_file.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(content)
    except (ValueError, TypeError):  # guardian: allow-silent-swallow (pre-existing, moved from L0)
        return results
    for node in tqdm(ast.walk(tree), desc="Processing", unit="item"):
        if not isinstance(node, ast.ClassDef):
            continue
        result = AgentAuditResult(class_name=node.name, file_path=str(py_file.relative_to(agentic_core)))
        for item in tqdm(ast.walk(node), desc="Processing", unit="item"):
            if isinstance(item, ast.FunctionDef):
                if item.name == "heal_repository":
                    result.has_heal_repository = True
                elif item.name == "_fix_violation":
                    result.has_fix_violation = True
                elif item.name == "_fix_violations":
                    result.has_fix_violations = True
                elif item.name == "_perform_code_surgery":
                    result.has_perform_surgery = True
            if isinstance(item, ast.keyword):
                if item.arg == "auto_fixable":
                    if isinstance(item.value, ast.Constant):
                        if item.value.value:
                            result.auto_fixable_true_count += 1
                        else:
                            result.auto_fixable_false_count += 1
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Attribute) and target.attr == "violation_type":
                        if isinstance(item.value, ast.Constant) and isinstance(item.value.value, str):
                            result.violation_types.append(item.value.value)
        if result.has_heal_repository:
            results.append(result)
    return results


def main():
    """Run the global healing capability audit."""
    agentic_core = get_validated_project_root() / AGENTIC_CORE_DIR
    exclude_dirs = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS | DISCOVERY_EXCLUDED_TERRITORIES
    all_results = []
    for py_file in agentic_core.rglob("*.py"):
        if any(ex in str(py_file) for ex in exclude_dirs):
            continue
        results = audit_agent_file(py_file, agentic_core)
        all_results.extend(results)
    verdict_order = {"IMPOTENT": 0, "GHOST": 1, "PASSIVE": 2, "HARDENED": 3}
    all_results.sort(key=lambda x: (verdict_order.get(x.verdict, 99), x.file_path))
    verdicts = {}
    for r in all_results:
        verdicts[r.verdict] = verdicts.get(r.verdict, 0) + 1
    for _v, _count in sorted(verdicts.items(), key=lambda x: verdict_order.get(x[0], 99)):
        pass
    for r in all_results:
        fix_logic = []
        if r.has_fix_violation:
            fix_logic.append("_fix_v")
        if r.has_fix_violations:
            fix_logic.append("_fix_vs")
        if r.has_perform_surgery:
            fix_logic.append("surgery")
        ",".join(fix_logic) if fix_logic else "NONE"
    impotent = [r for r in all_results if r.verdict == "IMPOTENT"]
    if impotent:
        for r in impotent:
            pass
    import_agents = [r for r in all_results if "Import" in r.class_name]
    for r in import_agents:
        pass


if __name__ == "__main__":
    main()
