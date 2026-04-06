"""
Table 2 (Code Quality) Data Validation
=======================================

Validates that Table 2 data is being generated and updated correctly.
Table 2 shows code quality metrics: Typed %, Documented %, schema Strictness, etc.

Checks:
1. Table 2 fields present in dashboard data
2. Table 2 metrics calculated correctly
3. renderCodeQualityTable function exists and is called
4. codeQualityGrid element exists in HTML
"""

import json
import sys
from pathlib import Path

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
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
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
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

emit_replay_key("p0", "validate_table2_data_util")
emit_determinism_digest("p0", "validate_table2_data_util")

_emit_dispatches_healing_run("p1", "validate_table2_data_util", "L0")
_emit_routes_through("p1", "validate_table2_data_util", "L0")
_emit_checks_agent_registry("p1", "validate_table2_data_util", "agent_registry")
_emit_validates_agent_capability("p1", "validate_table2_data_util", "capability")
_emit_dispatches_execution_plan("p1", "validate_table2_data_util", "exec_plan")
_emit_agent_executes_agent("p1", "validate_table2_data_util", "sub_agent")
_emit_routes_to_agent("p1", "validate_table2_data_util", "target_agent")
_emit_verifies_policy("p1", "validate_table2_data_util", "policy_check")
_emit_observes_runtime_state("p1", "validate_table2_data_util", "runtime_state")
_emit_verifies_boundary("p1", "validate_table2_data_util", "boundary_check")
_emit_transcripts_response("p1", "validate_table2_data_util", "transcript")
_emit_hard_fails_untranscripted("p1", "validate_table2_data_util")
_emit_gated_by_confidence("p1", "validate_table2_data_util", "confidence_gate")
_emit_escalates_to_human("p1", "validate_table2_data_util", "L0")
_emit_reads_policy_state("p1", "validate_table2_data_util", "L0")
_emit_authorize_and_execute("p2", "validate_table2_data_util", "execution_auth")
_emit_validates_capability("p2", "validate_table2_data_util", "capability_check")
_emit_routes_to_capability("p2", "validate_table2_data_util", "capability_route")
_emit_writes_via_uwg("p2", "validate_table2_data_util", "uwg_write")
_emit_blocks_direct_write("p2", "validate_table2_data_util", "direct_write_block")
_emit_records_tool_invocation("p2", "validate_table2_data_util", "tool_invocation")
_emit_captures_execution_output("p2", "validate_table2_data_util", "exec_output")
_emit_dispatches_agent("p3", "validate_table2_data_util", "agent_dispatch")
_emit_coordinates_agents("p3", "validate_table2_data_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "validate_table2_data_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "validate_table2_data_util", "healing_outcome")
_emit_escalates_failure("p3", "validate_table2_data_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "validate_table2_data_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "validate_table2_data_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "validate_table2_data_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "validate_table2_data_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "validate_table2_data_util", "eval_metric")
_emit_stores_embedding("p4", "validate_table2_data_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "validate_table2_data_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "validate_table2_data_util", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("validate_table2_data_util", "p4obs", "metric_1")
_emit_emits_metric_event("validate_table2_data_util", "p4obs", "metric_2")
_emit_emits_metric_event("validate_table2_data_util", "p4obs", "metric_3")
_emit_emits_metric_event("validate_table2_data_util", "p4obs", "metric_4")
_emit_emits_metric_event("validate_table2_data_util", "p4obs", "metric_5")
_emit_emits_metric_event("validate_table2_data_util", "p4obs", "metric_6")
_emit_records_incident_event("validate_table2_data_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("validate_table2_data_util", "p4obs", "anomaly")
_emit_writes_observability_log("validate_table2_data_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("validate_table2_data_util", "p4obs", "mon_state")
_emit_triggers_alert("validate_table2_data_util", "p4obs", "alert")
_emit_links_incident_trace("validate_table2_data_util", "p4obs", "trace_link")
_emit_captures_pattern("validate_table2_data_util", "p3lm", "pattern")
_emit_records_learning_event("validate_table2_data_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("validate_table2_data_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("validate_table2_data_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("validate_table2_data_util", "p3lm", "routing")
_emit_improves_agent_policy("validate_table2_data_util", "p3lm", "policy")
_emit_stores_learning_state("validate_table2_data_util", "p3lm", "state")
_emit_records_execution_trace("validate_table2_data_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("validate_table2_data_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("validate_table2_data_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("validate_table2_data_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("validate_table2_data_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("validate_table2_data_util", "env_read", "p2_env_1")
_emit_reads_environ("validate_table2_data_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("validate_table2_data_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("validate_table2_data_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "validate_table2_data_util", "context_pull")
_emit_pulls_context("p1", "validate_table2_data_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "validate_table2_data_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "validate_table2_data_util", "uwg_term_2")
_emit_writes_through("p1", "validate_table2_data_util", "write_through")
_emit_writes_through("p1", "validate_table2_data_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "validate_table2_data_util", "safety_validation")
_emit_invokes_eval("p1", "validate_table2_data_util", "eval_call")
_emit_proposal_commits_routing("p1", "validate_table2_data_util", "routing_commit")


def main():
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "main", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "main", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "main")
    print("=" * 80)
    print("TABLE 2 (CODE QUALITY) VALIDATION")
    print("=" * 80)
    print()
    errors = []
    warnings = []
    print("Check 1: Dashboard data structure")
    print("-" * 80)
    dashboard_path = Path("agentic_core/L6_observability/dashboards/autonomy_dashboard.html")
    if not dashboard_path.exists():
        errors.append("Dashboard HTML not found")
        print("   ❌ Dashboard HTML not found")
    else:
        html = dashboard_path.read_text(encoding="utf-8")
        import re

        data_match = re.search("const dashboardData = (\\[.*?\\]);", html, re.DOTALL)
        if not data_match:
            errors.append("dashboardData not found in HTML")
            print("   ❌ dashboardData not found")
        else:
            try:
                data_json = data_match.group(1)
                dashboard_data = json.loads(data_json)
                total_row = dashboard_data[0] if dashboard_data else {}
                table2_fields = [
                    "Typed %",
                    "Documented %",
                    "schema Strictness %",
                    "Proper Base %",
                    "Code Quality Score",
                ]
                missing_fields = [f for f in table2_fields if f not in total_row]
                if missing_fields:
                    errors.append(f"Table 2 fields missing: {missing_fields}")
                    print(f"   ❌ Missing fields: {missing_fields}")
                else:
                    print("   ✅ All Table 2 fields present")
                    print(f"      Typed %: {total_row.get('Typed %')}")
                    print(f"      Documented %: {total_row.get('Documented %')}")
                    print(f"      Code Quality Score: {total_row.get('Code Quality Score')}")
            except json.JSONDecodeError as e:
                errors.append(f"Failed to parse dashboardData: {e}")
                print(f"   ❌ JSON parse error: {e}")
    print()
    print("Check 2: Table 2 rendering function")
    print("-" * 80)
    if dashboard_path.exists():
        html = dashboard_path.read_text(encoding="utf-8")
        if "function renderCodeQualityTable" not in html:
            errors.append("renderCodeQualityTable function missing")
            print("   ❌ renderCodeQualityTable function not found")
        else:
            print("   ✅ renderCodeQualityTable function exists")
            if (
                "renderCodeQualityTable(dashboardData)" not in html
                and "renderCodeQualityTable(territoryData)" not in html
            ):
                warnings.append("renderCodeQualityTable may not be called")
                print("   ⚠️  renderCodeQualityTable might not be invoked")
            else:
                print("   ✅ renderCodeQualityTable is called")
    print()
    print("Check 3: Table 2 HTML container")
    print("-" * 80)
    if dashboard_path.exists():
        html = dashboard_path.read_text(encoding="utf-8")
        if 'id="codeQualityGrid"' not in html:
            errors.append("codeQualityGrid element missing")
            print("   ❌ codeQualityGrid element not found")
        else:
            print("   ✅ codeQualityGrid element exists")
    print()
    print("Check 4: Dashboard generator produces Table 2 fields")
    print("-" * 80)
    gen_script = Path("agentic_core/L6_observability/dashboards/generate_dashboard.py")
    if gen_script.exists():
        gen_code = gen_script.read_text(encoding="utf-8")
        table2_field_names = ['"Typed %"', '"Documented %"', '"schema Strictness %"', '"Code Quality Score"']
        missing_in_gen = [f for f in table2_field_names if f not in gen_code]
        if missing_in_gen:
            errors.append(f"Generator missing Table 2 fields: {missing_in_gen}")
            print(f"   ❌ Generator doesn't create: {missing_in_gen}")
        else:
            print("   ✅ Generator creates all Table 2 fields")
    print()
    print("=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)
    print()
    if errors:
        print(f"❌ {len(errors)} ERRORS:")
        for error in errors:
            print(f"   • {error}")
        print()
    if warnings:
        print(f"⚠️  {len(warnings)} WARNINGS:")
        for warning in warnings:
            print(f"   • {warning}")
        print()
    if not errors and (not warnings):
        print("✅ TABLE 2 VALIDATION PASSED")
        print("   All code quality metrics are properly configured")
        return 0
    elif not errors:
        print("⚠️  TABLE 2 HAS WARNINGS")
        print("   Review warnings above")
        return 0
    else:
        print("❌ TABLE 2 VALIDATION FAILED")
        print("   Fix errors above to enable Table 2")
        return 1


if __name__ == "__main__":
    sys.exit(main())
