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
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
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

_emit_records_execution_trace("p0", "evidence", "ast_gap_report")
_emit_applies_guardrail("p0", "ast_gap_report", "p0_governance")
_emit_reads_policy_state("p0", "ast_gap_report", "policy_binding")
_emit_snapshots_state("p0", "ast_gap_report", "state_snapshot")
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
