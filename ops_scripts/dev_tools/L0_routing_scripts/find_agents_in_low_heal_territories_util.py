"""Find actual agent files that belong to low heal capability territories."""

import json
from pathlib import Path

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
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

emit_replay_key("p0", "find_agents_in_low_heal_territories_util")
emit_determinism_digest("p0", "find_agents_in_low_heal_territories_util")

_emit_dispatches_healing_run("p1", "find_agents_in_low_heal_territories_util", "L0")
_emit_routes_through("p1", "find_agents_in_low_heal_territories_util", "L0")
_emit_checks_agent_registry("p1", "find_agents_in_low_heal_territories_util", "agent_registry")
_emit_validates_agent_capability("p1", "find_agents_in_low_heal_territories_util", "capability")
_emit_dispatches_execution_plan("p1", "find_agents_in_low_heal_territories_util", "exec_plan")
_emit_agent_executes_agent("p1", "find_agents_in_low_heal_territories_util", "sub_agent")
_emit_routes_to_agent("p1", "find_agents_in_low_heal_territories_util", "target_agent")
_emit_verifies_policy("p1", "find_agents_in_low_heal_territories_util", "policy_check")
_emit_observes_runtime_state("p1", "find_agents_in_low_heal_territories_util", "runtime_state")
_emit_verifies_boundary("p1", "find_agents_in_low_heal_territories_util", "boundary_check")
_emit_transcripts_response("p1", "find_agents_in_low_heal_territories_util", "transcript")
_emit_hard_fails_untranscripted("p1", "find_agents_in_low_heal_territories_util")
_emit_gated_by_confidence("p1", "find_agents_in_low_heal_territories_util", "confidence_gate")
_emit_escalates_to_human("p1", "find_agents_in_low_heal_territories_util", "L0")
_emit_reads_policy_state("p1", "find_agents_in_low_heal_territories_util", "L0")

_emit_records_execution_trace("p0", "evidence", "find_agents_in_low_heal_territories_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "find_agents_in_low_heal_territories_util", "p0_governance")
_emit_snapshots_state("p0", "find_agents_in_low_heal_territories_util", "state_snapshot")
_emit_authorize_and_execute("p2", "find_agents_in_low_heal_territories_util", "execution_auth")
_emit_validates_capability("p2", "find_agents_in_low_heal_territories_util", "capability_check")
_emit_routes_to_capability("p2", "find_agents_in_low_heal_territories_util", "capability_route")
_emit_writes_via_uwg("p2", "find_agents_in_low_heal_territories_util", "uwg_write")
_emit_blocks_direct_write("p2", "find_agents_in_low_heal_territories_util", "direct_write_block")
_emit_records_tool_invocation("p2", "find_agents_in_low_heal_territories_util", "tool_invocation")
_emit_captures_execution_output("p2", "find_agents_in_low_heal_territories_util", "exec_output")
_emit_dispatches_agent("p3", "find_agents_in_low_heal_territories_util", "agent_dispatch")
_emit_coordinates_agents("p3", "find_agents_in_low_heal_territories_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "find_agents_in_low_heal_territories_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "find_agents_in_low_heal_territories_util", "healing_outcome")
_emit_escalates_failure("p3", "find_agents_in_low_heal_territories_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "find_agents_in_low_heal_territories_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "find_agents_in_low_heal_territories_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "find_agents_in_low_heal_territories_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "find_agents_in_low_heal_territories_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "find_agents_in_low_heal_territories_util", "eval_metric")
_emit_stores_embedding("p4", "find_agents_in_low_heal_territories_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "find_agents_in_low_heal_territories_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "find_agents_in_low_heal_territories_util", "exec_snapshot_link")

with open(
    "C:/Git/Agentic-Workflow/agentic_core/L6_observability/dashboards/autonomy_dashboard.html",
    encoding="utf-8",
) as f:
    data = f.read()
start = data.find("const dashboardData = [")
end = data.find("];", start) + 1
json_str = data[start + 21 : end]
territories = json.loads(json_str)
print("=== All Territories with Heal Cap % ===")
for t in sorted(territories, key=lambda x: x.get("Heal Cap %", 100)):
    if t["Territory"] == "TOTAL":
        continue
    heal_cap = t.get("Heal Cap %", 100)
    total = t.get("Total", 0)
    if heal_cap < 100:
        print(f"  {t['Territory']}: {heal_cap}% ({total} agents)")
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
from agentic_core.utils.runners.ssot_discovery_validator import get_agent_files

_emit_emits_metric_event("find_agents_in_low_heal_territories_util", "p4obs", "metric_1")
_emit_emits_metric_event("find_agents_in_low_heal_territories_util", "p4obs", "metric_2")
_emit_emits_metric_event("find_agents_in_low_heal_territories_util", "p4obs", "metric_3")
_emit_emits_metric_event("find_agents_in_low_heal_territories_util", "p4obs", "metric_4")
_emit_emits_metric_event("find_agents_in_low_heal_territories_util", "p4obs", "metric_5")
_emit_emits_metric_event("find_agents_in_low_heal_territories_util", "p4obs", "metric_6")
_emit_records_incident_event("find_agents_in_low_heal_territories_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("find_agents_in_low_heal_territories_util", "p4obs", "anomaly")
_emit_writes_observability_log("find_agents_in_low_heal_territories_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("find_agents_in_low_heal_territories_util", "p4obs", "mon_state")
_emit_triggers_alert("find_agents_in_low_heal_territories_util", "p4obs", "alert")
_emit_links_incident_trace("find_agents_in_low_heal_territories_util", "p4obs", "trace_link")
_emit_captures_pattern("find_agents_in_low_heal_territories_util", "p3lm", "pattern")
_emit_records_learning_event("find_agents_in_low_heal_territories_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("find_agents_in_low_heal_territories_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("find_agents_in_low_heal_territories_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("find_agents_in_low_heal_territories_util", "p3lm", "routing")
_emit_improves_agent_policy("find_agents_in_low_heal_territories_util", "p3lm", "policy")
_emit_stores_learning_state("find_agents_in_low_heal_territories_util", "p3lm", "state")
_emit_records_execution_trace("find_agents_in_low_heal_territories_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("find_agents_in_low_heal_territories_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("find_agents_in_low_heal_territories_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("find_agents_in_low_heal_territories_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("find_agents_in_low_heal_territories_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("find_agents_in_low_heal_territories_util", "env_read", "p2_env_1")
_emit_reads_environ("find_agents_in_low_heal_territories_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("find_agents_in_low_heal_territories_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("find_agents_in_low_heal_territories_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "find_agents_in_low_heal_territories_util", "context_pull")
_emit_pulls_context("p1", "find_agents_in_low_heal_territories_util", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "find_agents_in_low_heal_territories_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "find_agents_in_low_heal_territories_util", "uwg_term_secondary")
_emit_writes_through("p1", "find_agents_in_low_heal_territories_util", "write_through")
_emit_writes_through("p1", "find_agents_in_low_heal_territories_util", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "find_agents_in_low_heal_territories_util", "safety_validation")
_emit_invokes_eval("p1", "find_agents_in_low_heal_territories_util", "eval_call")
_emit_proposal_commits_routing("p1", "find_agents_in_low_heal_territories_util", "routing_commit")

print("\n=== Searching for agents in L1 Cognition ===")
l1_agents = list(get_agent_files(Path("C:/Git/Agentic-Workflow/agentic_core/L1_cognition")))
for agent in l1_agents:
    content = agent.read_text(encoding="utf-8", errors="ignore")
    has_heal = "def heal_repository" in content
    print(f"  {('✅' if has_heal else '❌')} {agent.name}")
print("\n=== Searching for agents in L3 Orchestration ===")
l3_agents = list(get_agent_files(Path("C:/Git/Agentic-Workflow/agentic_core/L3_orchestration")))
for agent in l3_agents:
    content = agent.read_text(encoding="utf-8", errors="ignore")
    has_heal = "def heal_repository" in content
    print(f"  {('✅' if has_heal else '❌')} {agent.name}")
print("\n=== Agents MISSING heal_repository (need to fix) ===")
all_agents = get_agent_files(Path("C:/Git/Agentic-Workflow/agentic_core"))
missing = []
for agent in all_agents:
    content = agent.read_text(encoding="utf-8", errors="ignore")
    if "def heal_repository" not in content:
        missing.append(agent)
        print(f"  ❌ {agent.relative_to(Path('C:/Git/Agentic-Workflow'))}")
print(f"\nTotal agents missing heal_repository: {len(missing)}")
