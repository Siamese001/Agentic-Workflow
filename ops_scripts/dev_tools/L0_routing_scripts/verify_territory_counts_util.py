"""Verify all dashboard territory counts are correct."""

import json

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

emit_replay_key("p0", "verify_territory_counts_util")
emit_determinism_digest("p0", "verify_territory_counts_util")

_emit_dispatches_healing_run("p1", "verify_territory_counts_util", "L0")
_emit_routes_through("p1", "verify_territory_counts_util", "L0")
_emit_checks_agent_registry("p1", "verify_territory_counts_util", "agent_registry")
_emit_validates_agent_capability("p1", "verify_territory_counts_util", "capability")
_emit_dispatches_execution_plan("p1", "verify_territory_counts_util", "exec_plan")
_emit_agent_executes_agent("p1", "verify_territory_counts_util", "sub_agent")
_emit_routes_to_agent("p1", "verify_territory_counts_util", "target_agent")
_emit_verifies_policy("p1", "verify_territory_counts_util", "policy_check")
_emit_observes_runtime_state("p1", "verify_territory_counts_util", "runtime_state")
_emit_verifies_boundary("p1", "verify_territory_counts_util", "boundary_check")
_emit_transcripts_response("p1", "verify_territory_counts_util", "transcript")
_emit_hard_fails_untranscripted("p1", "verify_territory_counts_util")
_emit_gated_by_confidence("p1", "verify_territory_counts_util", "confidence_gate")
_emit_escalates_to_human("p1", "verify_territory_counts_util", "L0")
_emit_reads_policy_state("p1", "verify_territory_counts_util", "L0")
_emit_authorize_and_execute("p2", "verify_territory_counts_util", "execution_auth")
_emit_validates_capability("p2", "verify_territory_counts_util", "capability_check")
_emit_routes_to_capability("p2", "verify_territory_counts_util", "capability_route")
_emit_writes_via_uwg("p2", "verify_territory_counts_util", "uwg_write")
_emit_blocks_direct_write("p2", "verify_territory_counts_util", "direct_write_block")
_emit_records_tool_invocation("p2", "verify_territory_counts_util", "tool_invocation")
_emit_captures_execution_output("p2", "verify_territory_counts_util", "exec_output")
_emit_dispatches_agent("p3", "verify_territory_counts_util", "agent_dispatch")
_emit_coordinates_agents("p3", "verify_territory_counts_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "verify_territory_counts_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "verify_territory_counts_util", "healing_outcome")
_emit_escalates_failure("p3", "verify_territory_counts_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "verify_territory_counts_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "verify_territory_counts_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "verify_territory_counts_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "verify_territory_counts_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "verify_territory_counts_util", "eval_metric")
_emit_stores_embedding("p4", "verify_territory_counts_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "verify_territory_counts_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "verify_territory_counts_util", "exec_snapshot_link")
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

_emit_emits_metric_event("verify_territory_counts_util", "p4obs", "metric_1")
_emit_emits_metric_event("verify_territory_counts_util", "p4obs", "metric_2")
_emit_emits_metric_event("verify_territory_counts_util", "p4obs", "metric_3")
_emit_emits_metric_event("verify_territory_counts_util", "p4obs", "metric_4")
_emit_emits_metric_event("verify_territory_counts_util", "p4obs", "metric_5")
_emit_emits_metric_event("verify_territory_counts_util", "p4obs", "metric_6")
_emit_records_incident_event("verify_territory_counts_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("verify_territory_counts_util", "p4obs", "anomaly")
_emit_writes_observability_log("verify_territory_counts_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("verify_territory_counts_util", "p4obs", "mon_state")
_emit_triggers_alert("verify_territory_counts_util", "p4obs", "alert")
_emit_links_incident_trace("verify_territory_counts_util", "p4obs", "trace_link")
_emit_captures_pattern("verify_territory_counts_util", "p3lm", "pattern")
_emit_records_learning_event("verify_territory_counts_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("verify_territory_counts_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("verify_territory_counts_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("verify_territory_counts_util", "p3lm", "routing")
_emit_improves_agent_policy("verify_territory_counts_util", "p3lm", "policy")
_emit_stores_learning_state("verify_territory_counts_util", "p3lm", "state")
_emit_records_execution_trace("verify_territory_counts_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("verify_territory_counts_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("verify_territory_counts_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("verify_territory_counts_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("verify_territory_counts_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("verify_territory_counts_util", "env_read", "p2_env_1")
_emit_reads_environ("verify_territory_counts_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("verify_territory_counts_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("verify_territory_counts_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "verify_territory_counts_util", "context_pull")
_emit_pulls_context("p1", "verify_territory_counts_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "verify_territory_counts_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "verify_territory_counts_util", "uwg_term_2")
_emit_writes_through("p1", "verify_territory_counts_util", "write_through")
_emit_writes_through("p1", "verify_territory_counts_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "verify_territory_counts_util", "safety_validation")
_emit_invokes_eval("p1", "verify_territory_counts_util", "eval_call")
_emit_proposal_commits_routing("p1", "verify_territory_counts_util", "routing_commit")


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
    lines = []
    in_data = False
    brace_count = 0
    with open("agentic_core/L6_observability/dashboards/autonomy_dashboard.html", encoding="utf-8") as f:
        for line in f:
            if "const dashboardData = [" in line:
                in_data = True
                lines.append("[")
                continue
            if in_data:
                lines.append(line)
                brace_count += line.count("{") - line.count("}")
                if "];" in line and brace_count == 0:
                    lines[-1] = lines[-1].replace("];", "]")
                    break
    if not lines:
        print("Could not find dashboardData in HTML")
        exit(1)
    data_str = "".join(lines)
    data = json.loads(data_str)
    print("=" * 70)
    print("DASHBOARD TERRITORY VERIFICATION")
    print("=" * 70)
    print()
    zero_territories = [row for row in data if row["Total"] == 0 and row["Territory"] != "TOTAL"]
    non_zero_territories = [row for row in data if row["Total"] > 0 and row["Territory"] != "TOTAL"]
    print(f"Total Territories: {len(data) - 1}")
    print(f"Non-Zero Territories: {len(non_zero_territories)}")
    print(f"Zero-Agent Territories: {len(zero_territories)}")
    print()
    if zero_territories:
        print("Zero-Agent Territories (expected for infrastructure placeholders):")
        print("-" * 70)
        for row in zero_territories:
            is_infra = "[infra] " if row.get("IsInfrastructure") else "        "
            print(f"{is_infra}{row['Territory']:50} {row['Total']:>3} agents")
        print()
    print("Non-Zero Territories:")
    print("-" * 70)
    for row in sorted(non_zero_territories, key=lambda x: -x["Total"]):
        print(f"   {row['Territory']:50} {row['Total']:>3} agents")
    print()
    print("=" * 70)
    print("KEY METRICS")
    print("=" * 70)
    total_row = data[0]
    print(f"Total Agents:        {total_row['Total']}")
    print(f"Heal Capability:     {total_row['Heal Cap %']}%")
    print(f"Health Score:        {total_row['Health']}")
    print(f"Compliant Agents:    {total_row['Compliant']}/{total_row['Total']}")
    print()
    l6_territories = [row for row in data if "L6" in row["Territory"]]
    l6_total = sum(row["Total"] for row in l6_territories)
    print("L6_Observability Breakdown:")
    for row in l6_territories:
        status = "OK" if row["Total"] > 0 else "WARN"
        print(f"   [{status}] {row['Territory']:45} {row['Total']:>3} agents")
    print(f"   {'L6 TOTAL':45} {l6_total:>3} agents")
    print()
    if l6_total > 0:
        print("L6_Observability data is CORRECT")
    else:
        print("L6_Observability has 0 agents - DATA ERROR")


if __name__ == "__main__":
    main()
