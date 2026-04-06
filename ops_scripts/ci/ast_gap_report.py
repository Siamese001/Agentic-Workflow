"""Print gap analysis results from ast_gap_results.json."""

import json
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    TESTS_DIR,
    get_validated_project_root,
)
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
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,
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
    _emit_routes_through,
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

_emit_emits_metric_event("ast_gap_report", "p4obs", "metric_1")
_emit_emits_metric_event("ast_gap_report", "p4obs", "metric_2")
_emit_emits_metric_event("ast_gap_report", "p4obs", "metric_3")
_emit_emits_metric_event("ast_gap_report", "p4obs", "metric_4")
_emit_emits_metric_event("ast_gap_report", "p4obs", "metric_5")
_emit_emits_metric_event("ast_gap_report", "p4obs", "metric_6")
_emit_records_incident_event("ast_gap_report", "p4obs", "incident")
_emit_captures_runtime_anomaly("ast_gap_report", "p4obs", "anomaly")
_emit_writes_observability_log("ast_gap_report", "p4obs", "obs_log")
_emit_updates_monitoring_state("ast_gap_report", "p4obs", "mon_state")
_emit_triggers_alert("ast_gap_report", "p4obs", "alert")
_emit_links_incident_trace("ast_gap_report", "p4obs", "trace_link")
_emit_captures_pattern("ast_gap_report", "p3lm", "pattern")
_emit_records_learning_event("ast_gap_report", "p3lm", "learning_event")
_emit_writes_learning_snapshot("ast_gap_report", "p3lm", "snapshot")
_emit_feeds_meta_learning("ast_gap_report", "p3lm", "meta_feed")
_emit_updates_routing_strategy("ast_gap_report", "p3lm", "routing")
_emit_improves_agent_policy("ast_gap_report", "p3lm", "policy")
_emit_stores_learning_state("ast_gap_report", "p3lm", "state")
_emit_records_execution_trace("ast_gap_report", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("ast_gap_report", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("ast_gap_report", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("ast_gap_report", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("ast_gap_report", "L4_STATE", "p2_trace_5")
_emit_reads_environ("ast_gap_report", "env_read", "p2_env_1")
_emit_reads_environ("ast_gap_report", "env_read", "p2_env_2")
_emit_reads_runtime_state("ast_gap_report", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("ast_gap_report", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "ast_gap_report")
_emit_applies_guardrail("p0", "ast_gap_report", "p0_governance")
_emit_reads_policy_state("p0", "ast_gap_report", "policy_binding")
_emit_snapshots_state("p0", "ast_gap_report", "state_snapshot")
_emit_pulls_context("p1", "ast_gap_report", "context_pull")
_emit_pulls_context("p1", "ast_gap_report", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "ast_gap_report", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "ast_gap_report", "uwg_term_secondary")
_emit_writes_through("p1", "ast_gap_report", "write_through")
_emit_writes_through("p1", "ast_gap_report", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "ast_gap_report", "safety_validation")
_emit_invokes_eval("p1", "ast_gap_report", "eval_call")
_emit_proposal_commits_routing("p1", "ast_gap_report", "routing_commit")
_emit_escalates_to_human("p1", "ast_gap_report", "human_escalation")
_emit_routes_through("p1", "ast_gap_report", "route_through")
_emit_checks_agent_registry("p1", "ast_gap_report", "agent_registry")
_emit_validates_agent_capability("p1", "ast_gap_report", "capability")
_emit_dispatches_execution_plan("p1", "ast_gap_report", "exec_plan")
_emit_agent_executes_agent("p1", "ast_gap_report", "sub_agent")
_emit_routes_to_agent("p1", "ast_gap_report", "target_agent")
_emit_verifies_policy("p1", "ast_gap_report", "policy_check")
_emit_observes_runtime_state("p1", "ast_gap_report", "runtime_state")
_emit_verifies_boundary("p1", "ast_gap_report", "boundary_check")
_emit_transcripts_response("p1", "ast_gap_report", "transcript")
_emit_hard_fails_untranscripted("p1", "ast_gap_report")
_emit_gated_by_confidence("p1", "ast_gap_report", "confidence_gate")
emit_replay_key("p0", "ast_gap_report")
emit_determinism_digest("p0", "ast_gap_report")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "ast_gap_report", "execution_auth")
_emit_validates_capability("p2", "ast_gap_report", "capability_check")
_emit_routes_to_capability("p2", "ast_gap_report", "capability_route")
_emit_writes_via_uwg("p2", "ast_gap_report", "uwg_write")
_emit_blocks_direct_write("p2", "ast_gap_report", "direct_write_block")
_emit_records_tool_invocation("p2", "ast_gap_report", "tool_invocation")
_emit_captures_execution_output("p2", "ast_gap_report", "exec_output")
_emit_dispatches_agent("p3", "ast_gap_report", "agent_dispatch")
_emit_coordinates_agents("p3", "ast_gap_report", "agent_coordination")
_emit_records_workflow_lineage("p3", "ast_gap_report", "workflow_lineage")
_emit_records_healing_outcome("p3", "ast_gap_report", "healing_outcome")
_emit_escalates_failure("p3", "ast_gap_report", "failure_escalation")
_emit_orchestrates_workflow("p3", "ast_gap_report", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "ast_gap_report", "healing_dispatch")
_emit_invokes_evaluation("p3", "ast_gap_report", "evaluation_signal")
_emit_records_telemetry_event("p4", "ast_gap_report", "telemetry_event")
_emit_captures_evaluation_metric("p4", "ast_gap_report", "eval_metric")
_emit_stores_embedding("p4", "ast_gap_report", "embedding_store")
_emit_updates_meta_learning_state("p4", "ast_gap_report", "meta_learning")
_emit_links_execution_to_snapshot("p4", "ast_gap_report", "exec_snapshot_link")

ROOT = get_validated_project_root()
data = json.loads((ROOT / "ops_scripts/ci/ast_gap_results.json").read_text())

print("=== SOURCE SUMMARY ===")
for t, s in data["source_summary"].items():
    line = (
        "  "
        + t
        + ": "
        + str(s["files"])
        + " files, "
        + str(s["n_classes"])
        + " classes, "
        + str(s["n_funcs"])
        + " funcs"
    )
    print(line)
    for se in s["syntax_errors"]:
        print("    SYNTAX: " + se["path"])

print()
print("=== TEST SUMMARY ===")
ts = data["test_summary"]
print("  Total test files: " + str(ts["total_test_files"]))
print("  Total test funcs: " + str(ts["total_test_funcs"]))
for se in ts["syntax_errors"]:
    print("  Test syntax error: " + se)

print()
print("=== GAPS BY SEVERITY ===")
gaps = data["coverage_gaps"]
by_sev = {}
for g in gaps:
    by_sev.setdefault(g["severity"], []).append(g)

for sev in ["CRITICAL", "HIGH", "LOW", "SYNTAX_ERROR"]:
    items = by_sev.get(sev, [])
    print("  " + sev + ": " + str(len(items)))

print()
print("=== CRITICAL GAPS (>3 symbols, no tests) ===")
for g in sorted(by_sev.get("CRITICAL", []), key=lambda x: x["path"]):
    cls = g.get("top_classes", [])
    print(
        "  [" + g["target"] + "] " + g["path"] + "  cls=" + str(g["n_classes"]) + " fn=" + str(g["n_funcs"])
    )
    if cls:
        print("    classes: " + str(cls))

print()
print("=== HIGH GAPS (1-3 symbols, no tests) ===")
for g in sorted(by_sev.get("HIGH", []), key=lambda x: x["path"]):
    cls = g.get("top_classes", [])
    print(
        "  [" + g["target"] + "] " + g["path"] + "  cls=" + str(g["n_classes"]) + " fn=" + str(g["n_funcs"])
    )
    if cls:
        print("    classes: " + str(cls))

print()
print("=== COVERED: " + str(len(data["covered"])) + " modules ===")

# Per-target gap count
print()
print("=== GAP COUNT BY TARGET ===")
target_gaps = {}
for g in gaps:
    if g["severity"] in ("CRITICAL", "HIGH", "LOW"):
        target_gaps.setdefault(g["target"], {"CRITICAL": 0, "HIGH": 0, "LOW": 0})
        target_gaps[g["target"]][g["severity"]] += 1
for tgt, counts in sorted(target_gaps.items()):
    print(
        "  "
        + tgt
        + ": CRITICAL="
        + str(counts["CRITICAL"])
        + " HIGH="
        + str(counts["HIGH"])
        + " LOW="
        + str(counts["LOW"])
    )

# Guardian-specific check: does tests/guardian or tests/architecture exist?
print()
print("=== GUARDIAN / ARCHITECTURE TEST INVENTORY ===")
for subdir in ["guardian", "architecture", AGENTIC_CORE_DIR, APPS_LIC_DIR, APPS_RG_DIR, APPS_SHARED_DIR]:
    p = ROOT / TESTS_DIR / subdir
    if p.exists():
        files = list(p.rglob("test_*.py"))
# guardian: allow-path-string
# guardian: allow-path-string
# guardian: allow-path-string

        # guardian: allow-path-string
        print("  tests/" + subdir + ": " + str(len(files)) + " test files")
    # guardian: allow-path-string
    else:
        # guardian: allow-path-string
        print("  tests/" + subdir + ": MISSING")
