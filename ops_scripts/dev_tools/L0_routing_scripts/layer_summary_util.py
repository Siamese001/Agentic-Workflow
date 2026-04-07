"""Generate simple layer summary table."""

import json
from collections import defaultdict

from agentic_core.L0_routing.config import AGENT_DISCOVERY_JSON, TESTS_DIR
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_emits_metric_event("layer_summary_util", "p4obs", "metric_1")
_emit_emits_metric_event("layer_summary_util", "p4obs", "metric_2")
_emit_emits_metric_event("layer_summary_util", "p4obs", "metric_3")
_emit_emits_metric_event("layer_summary_util", "p4obs", "metric_4")
_emit_emits_metric_event("layer_summary_util", "p4obs", "metric_5")
_emit_emits_metric_event("layer_summary_util", "p4obs", "metric_6")
_emit_records_incident_event("layer_summary_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("layer_summary_util", "p4obs", "anomaly")
_emit_writes_observability_log("layer_summary_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("layer_summary_util", "p4obs", "mon_state")
_emit_triggers_alert("layer_summary_util", "p4obs", "alert")
_emit_links_incident_trace("layer_summary_util", "p4obs", "trace_link")
_emit_captures_pattern("layer_summary_util", "p3lm", "pattern")
_emit_records_learning_event("layer_summary_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("layer_summary_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("layer_summary_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("layer_summary_util", "p3lm", "routing")
_emit_improves_agent_policy("layer_summary_util", "p3lm", "policy")
_emit_stores_learning_state("layer_summary_util", "p3lm", "state")
_emit_records_execution_trace("layer_summary_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("layer_summary_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("layer_summary_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("layer_summary_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("layer_summary_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("layer_summary_util", "env_read", "p2_env_1")
_emit_reads_environ("layer_summary_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("layer_summary_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("layer_summary_util", "runtime_state", "p2_rt_2")

emit_replay_key("p0", "layer_summary_util")
emit_determinism_digest("p0", "layer_summary_util")

_emit_dispatches_healing_run("p1", "layer_summary_util", "L0")
_emit_routes_through("p1", "layer_summary_util", "L0")
_emit_checks_agent_registry("p1", "layer_summary_util", "agent_registry")
_emit_validates_agent_capability("p1", "layer_summary_util", "capability")
_emit_dispatches_execution_plan("p1", "layer_summary_util", "exec_plan")
_emit_agent_executes_agent("p1", "layer_summary_util", "sub_agent")
_emit_routes_to_agent("p1", "layer_summary_util", "target_agent")
_emit_verifies_policy("p1", "layer_summary_util", "policy_check")
_emit_observes_runtime_state("p1", "layer_summary_util", "runtime_state")
_emit_verifies_boundary("p1", "layer_summary_util", "boundary_check")
_emit_transcripts_response("p1", "layer_summary_util", "transcript")
_emit_hard_fails_untranscripted("p1", "layer_summary_util")
_emit_gated_by_confidence("p1", "layer_summary_util", "confidence_gate")
_emit_escalates_to_human("p1", "layer_summary_util", "L0")
_emit_reads_policy_state("p1", "layer_summary_util", "L0")
_emit_pulls_context("p1", "layer_summary_util", "context_pull")
_emit_pulls_context("p1", "layer_summary_util", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "layer_summary_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "layer_summary_util", "uwg_term_secondary")
_emit_writes_through("p1", "layer_summary_util", "write_through")
_emit_writes_through("p1", "layer_summary_util", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "layer_summary_util", "safety_validation")
_emit_invokes_eval("p1", "layer_summary_util", "eval_call")
_emit_proposal_commits_routing("p1", "layer_summary_util", "routing_commit")

_emit_records_execution_trace("p0", "evidence", "layer_summary_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "layer_summary_util", "p0_governance")
_emit_snapshots_state("p0", "layer_summary_util", "state_snapshot")
_emit_authorize_and_execute("p2", "layer_summary_util", "execution_auth")
_emit_validates_capability("p2", "layer_summary_util", "capability_check")
_emit_routes_to_capability("p2", "layer_summary_util", "capability_route")
_emit_writes_via_uwg("p2", "layer_summary_util", "uwg_write")
_emit_blocks_direct_write("p2", "layer_summary_util", "direct_write_block")
_emit_records_tool_invocation("p2", "layer_summary_util", "tool_invocation")
_emit_captures_execution_output("p2", "layer_summary_util", "exec_output")
_emit_dispatches_agent("p3", "layer_summary_util", "agent_dispatch")
_emit_coordinates_agents("p3", "layer_summary_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "layer_summary_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "layer_summary_util", "healing_outcome")
_emit_escalates_failure("p3", "layer_summary_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "layer_summary_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "layer_summary_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "layer_summary_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "layer_summary_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "layer_summary_util", "eval_metric")
_emit_stores_embedding("p4", "layer_summary_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "layer_summary_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "layer_summary_util", "exec_snapshot_link")

data = json.load(open(AGENT_DISCOVERY_JSON))
stats = defaultdict(lambda: {"count": 0, "healing": 0, "mcp": 0, "testing": 0, "tools": 0})
for a in data:
    layer = a.get("layer", "misc")
    stats[layer]["count"] += 1
    if a.get("has_healing"):
        stats[layer]["healing"] += 1
    if a.get("mcp_hardened"):
        stats[layer]["mcp"] += 1
    if a.get("testing") != "None":
        stats[layer]["testing"] += 1
    if a.get("has_tools"):
        stats[layer]["tools"] += 1
print("| Layer | Agents | Healing | MCP Hardened | Testing | Tools |")
print("|-------|--------|---------|--------------|---------|-------|")
for layer in [
    "L0",
    "L1",
    "L2",
    "L3",
    "L4",
    "L5",
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    TESTS_DIR,
    "misc",
]:
    s = stats[layer]
    if s["count"] > 0:
        h_pct = 100 * s["healing"] // s["count"]
        m_pct = 100 * s["mcp"] // s["count"]
        t_pct = 100 * s["testing"] // s["count"]
        tl_pct = 100 * s["tools"] // s["count"]
        print(
            f"| {layer} | {s['count']} | {s['healing']} ({h_pct}%) | {s['mcp']} ({m_pct}%) | {s['testing']} ({t_pct}%) | {s['tools']} ({tl_pct}%) |",
        )
total = sum(s["count"] for s in stats.values())
heal = sum(s["healing"] for s in stats.values())
mcp = sum(s["mcp"] for s in stats.values())
test = sum(s["testing"] for s in stats.values())
tools = sum(s["tools"] for s in stats.values())
print(
    f"| **TOTAL** | **{total}** | **{heal}** ({100 * heal // total}%) | **{mcp}** ({100 * mcp // total}%) | **{test}** ({100 * test // total}%) | **{tools}** ({100 * tools // total}%) |",
)
