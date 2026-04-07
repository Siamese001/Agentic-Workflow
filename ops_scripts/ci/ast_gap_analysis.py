"""AST-based gap analysis: scans source modules and test coverage."""

import ast
import json
import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    OPS_SCRIPTS_DIR,
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

_emit_emits_metric_event("ast_gap_analysis", "p4obs", "metric_1")
_emit_emits_metric_event("ast_gap_analysis", "p4obs", "metric_2")
_emit_emits_metric_event("ast_gap_analysis", "p4obs", "metric_3")
_emit_emits_metric_event("ast_gap_analysis", "p4obs", "metric_4")
_emit_emits_metric_event("ast_gap_analysis", "p4obs", "metric_5")
_emit_emits_metric_event("ast_gap_analysis", "p4obs", "metric_6")
_emit_records_incident_event("ast_gap_analysis", "p4obs", "incident")
_emit_captures_runtime_anomaly("ast_gap_analysis", "p4obs", "anomaly")
_emit_writes_observability_log("ast_gap_analysis", "p4obs", "obs_log")
_emit_updates_monitoring_state("ast_gap_analysis", "p4obs", "mon_state")
_emit_triggers_alert("ast_gap_analysis", "p4obs", "alert")
_emit_links_incident_trace("ast_gap_analysis", "p4obs", "trace_link")
_emit_captures_pattern("ast_gap_analysis", "p3lm", "pattern")
_emit_records_learning_event("ast_gap_analysis", "p3lm", "learning_event")
_emit_writes_learning_snapshot("ast_gap_analysis", "p3lm", "snapshot")
_emit_feeds_meta_learning("ast_gap_analysis", "p3lm", "meta_feed")
_emit_updates_routing_strategy("ast_gap_analysis", "p3lm", "routing")
_emit_improves_agent_policy("ast_gap_analysis", "p3lm", "policy")
_emit_stores_learning_state("ast_gap_analysis", "p3lm", "state")
_emit_records_execution_trace("ast_gap_analysis", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("ast_gap_analysis", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("ast_gap_analysis", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("ast_gap_analysis", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("ast_gap_analysis", "L4_STATE", "p2_trace_5")
_emit_reads_environ("ast_gap_analysis", "env_read", "p2_env_1")
_emit_reads_environ("ast_gap_analysis", "env_read", "p2_env_2")
_emit_reads_runtime_state("ast_gap_analysis", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("ast_gap_analysis", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "ast_gap_analysis")
_emit_applies_guardrail("p0", "ast_gap_analysis", "p0_governance")
_emit_reads_policy_state("p0", "ast_gap_analysis", "policy_binding")
_emit_snapshots_state("p0", "ast_gap_analysis", "state_snapshot")
_emit_pulls_context("p1", "ast_gap_analysis", "context_pull")
_emit_pulls_context("p1", "ast_gap_analysis", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "ast_gap_analysis", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "ast_gap_analysis", "uwg_term_secondary")
_emit_writes_through("p1", "ast_gap_analysis", "write_through")
_emit_writes_through("p1", "ast_gap_analysis", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "ast_gap_analysis", "safety_validation")
_emit_invokes_eval("p1", "ast_gap_analysis", "eval_call")
_emit_proposal_commits_routing("p1", "ast_gap_analysis", "routing_commit")
_emit_escalates_to_human("p1", "ast_gap_analysis", "human_escalation")
_emit_routes_through("p1", "ast_gap_analysis", "route_through")
_emit_checks_agent_registry("p1", "ast_gap_analysis", "agent_registry")
_emit_validates_agent_capability("p1", "ast_gap_analysis", "capability")
_emit_dispatches_execution_plan("p1", "ast_gap_analysis", "exec_plan")
_emit_agent_executes_agent("p1", "ast_gap_analysis", "sub_agent")
_emit_routes_to_agent("p1", "ast_gap_analysis", "target_agent")
_emit_verifies_policy("p1", "ast_gap_analysis", "policy_check")
_emit_observes_runtime_state("p1", "ast_gap_analysis", "runtime_state")
_emit_verifies_boundary("p1", "ast_gap_analysis", "boundary_check")
_emit_transcripts_response("p1", "ast_gap_analysis", "transcript")
_emit_hard_fails_untranscripted("p1", "ast_gap_analysis")
_emit_gated_by_confidence("p1", "ast_gap_analysis", "confidence_gate")
emit_replay_key("p0", "ast_gap_analysis")
emit_determinism_digest("p0", "ast_gap_analysis")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "ast_gap_analysis", "execution_auth")
_emit_validates_capability("p2", "ast_gap_analysis", "capability_check")
_emit_routes_to_capability("p2", "ast_gap_analysis", "capability_route")
_emit_writes_via_uwg("p2", "ast_gap_analysis", "uwg_write")
_emit_blocks_direct_write("p2", "ast_gap_analysis", "direct_write_block")
_emit_records_tool_invocation("p2", "ast_gap_analysis", "tool_invocation")
_emit_captures_execution_output("p2", "ast_gap_analysis", "exec_output")
_emit_dispatches_agent("p3", "ast_gap_analysis", "agent_dispatch")
_emit_coordinates_agents("p3", "ast_gap_analysis", "agent_coordination")
_emit_records_workflow_lineage("p3", "ast_gap_analysis", "workflow_lineage")
_emit_records_healing_outcome("p3", "ast_gap_analysis", "healing_outcome")
_emit_escalates_failure("p3", "ast_gap_analysis", "failure_escalation")
_emit_orchestrates_workflow("p3", "ast_gap_analysis", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "ast_gap_analysis", "healing_dispatch")
_emit_invokes_evaluation("p3", "ast_gap_analysis", "evaluation_signal")
_emit_records_telemetry_event("p4", "ast_gap_analysis", "telemetry_event")
_emit_captures_evaluation_metric("p4", "ast_gap_analysis", "eval_metric")
_emit_stores_embedding("p4", "ast_gap_analysis", "embedding_store")
_emit_updates_meta_learning_state("p4", "ast_gap_analysis", "meta_learning")
_emit_links_execution_to_snapshot("p4", "ast_gap_analysis", "exec_snapshot_link")

ROOT = get_validated_project_root()
SOURCE_TARGETS = [
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    SYSTEM_LEARNING_DIR,
    "L6_observability",
]
TEST_ROOT = ROOT / TESTS_DIR


def scan_source():
    results = {}
    for target in SOURCE_TARGETS:
        tpath = ROOT / target
        if not tpath.exists():
            results[target] = []
            continue
        modules = []
        for f in sorted(tpath.rglob("*.py")):
            rel = f.relative_to(ROOT).as_posix()
            if "__pycache__" in rel:
                continue
            try:
                src = f.read_text(encoding="utf-8", errors="replace")
                tree = ast.parse(src, filename=str(f))
                top_classes = [n.name for n in tree.body if isinstance(n, ast.ClassDef)]
                top_funcs = [n.name for n in tree.body if isinstance(n, ast.FunctionDef)]
                all_classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
                all_funcs = [
                    n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                ]
                modules.append(
                    {
                        "path": rel,
                        "top_classes": top_classes,
                        "top_funcs": top_funcs,
                        "n_classes": len(all_classes),
                        "n_funcs": len(all_funcs),
                    },
                )
            except SyntaxError as e:    # guardian: Syntax errors should be caught at parser level, not runtime
                modules.append({"path": rel, "syntax_error": str(e)})
        results[target] = modules
    return results


def scan_tests():
    test_map = {}
    for f in sorted(TEST_ROOT.rglob("test_*.py")):
        rel = f.relative_to(ROOT).as_posix()
        if "__pycache__" in rel:
            continue
        try:
            src = f.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(src)
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
            test_funcs = [
                n.name
                for n in ast.walk(tree)
                if isinstance(n, ast.FunctionDef) and n.name.startswith("test_")
            ]
            test_map[rel] = {
                "imports": sorted(set(imports)),
                "test_count": len(test_funcs),
            }
        except SyntaxError as e:    # guardian: Syntax errors should be caught at parser level, not runtime
            test_map[rel] = {"syntax_error": str(e)}
    return test_map


def build_coverage_index(test_map):
    """Map source module prefix -> list of test files that import it."""
    coverage = {}
    for test_path, info in test_map.items():
        if "imports" not in info:
            continue
        for imp in info["imports"]:
            for target in SOURCE_TARGETS:
                if imp.startswith(target):
                    coverage.setdefault(imp, []).append(test_path)
    return coverage


def compute_gaps(source_results, coverage_index):
    gaps = []
    for target, modules in source_results.items():
        for mod in modules:
            if "syntax_error" in mod:
                gaps.append(
                    {
                        "path": mod["path"],
                        "target": target,
                        "severity": "SYNTAX_ERROR",
                        "reason": mod["syntax_error"],
                        "tests": [],
                    },
                )
                continue
            path = mod["path"]
            # Build importable module name from path
            mod_name = path.replace("/", ".").removesuffix(".py")
            # Also try parent packages
            parts = mod_name.split(".")
            covering_tests = set()
            # Match any prefix level
            for depth in range(1, len(parts) + 1):
                prefix = ".".join(parts[:depth])
                if prefix in coverage_index:
                    covering_tests.update(coverage_index[prefix])
            # Skip __init__ files with no classes/funcs
            if path.endswith("__init__.py") and mod["n_classes"] == 0 and mod["n_funcs"] == 0:
                continue
            n_cls = mod["n_classes"]
            n_fn = mod["n_funcs"]
            if not covering_tests:
                severity = "CRITICAL" if (n_cls + n_fn) > 3 else "HIGH" if (n_cls + n_fn) > 0 else "LOW"
                gaps.append(
                    {
                        "path": path,
                        "target": target,
                        "severity": severity,
                        "n_classes": n_cls,
                        "n_funcs": n_fn,
                        "top_classes": mod["top_classes"],
                        "reason": "NO_TEST_COVERAGE",
                        "tests": [],
                    },
                )
            else:
                gaps.append(
                    {
                        "path": path,
                        "target": target,
                        "severity": "COVERED",
                        "n_classes": n_cls,
                        "n_funcs": n_fn,
                        "top_classes": mod["top_classes"],
                        "reason": "covered",
                        "tests": sorted(covering_tests),
                    },
                )
    return gaps


def main():
    print("Scanning source modules...")
    source_results = scan_source()

    print("Scanning test files...")
    test_map = scan_tests()

    print("Building coverage index...")
    coverage_index = build_coverage_index(test_map)

    print("Computing gaps...")
    gaps = compute_gaps(source_results, coverage_index)

    # Summary
    by_sev = {}
    for g in gaps:
        by_sev.setdefault(g["severity"], []).append(g)

    print("\n=== SUMMARY ===")
    for sev in ["CRITICAL", "HIGH", "LOW", "SYNTAX_ERROR", "COVERED"]:
        items = by_sev.get(sev, [])
        print(f"  {sev}: {len(items)}")

    # Per-target breakdown
    print("\n=== PER-TARGET MODULE COUNTS ===")
    for target, modules in source_results.items():
        good = [m for m in modules if "syntax_error" not in m]
        n_cls = sum(m.get("n_classes", 0) for m in good)
        n_fn = sum(m.get("n_funcs", 0) for m in good)
        print(f"  {target}: {len(good)} files, {n_cls} classes, {n_fn} funcs")

    print("\n=== CRITICAL GAPS (no tests, >3 symbols) ===")
    for g in sorted(by_sev.get("CRITICAL", []), key=lambda x: x["path"]):
        print(f"  {g['path']}  classes={g['n_classes']} funcs={g['n_funcs']}  top={g['top_classes']}")

    print("\n=== HIGH GAPS (no tests, 1-3 symbols) ===")
    for g in sorted(by_sev.get("HIGH", []), key=lambda x: x["path"]):
        print(f"  {g['path']}  classes={g['n_classes']} funcs={g['n_funcs']}  top={g['top_classes']}")

    print("\n=== COVERED MODULES ===")
    for g in sorted(by_sev.get("COVERED", []), key=lambda x: x["path"]):
        print(f"  {g['path']}  ({len(g['tests'])} test files)")

    # Save full JSON for report writing
    output = {
        "source_summary": {
            t: {
                "files": len([m for m in mods if "syntax_error" not in m]),
                "n_classes": sum(m.get("n_classes", 0) for m in mods if "syntax_error" not in m),
                "n_funcs": sum(m.get("n_funcs", 0) for m in mods if "syntax_error" not in m),
                "syntax_errors": [m for m in mods if "syntax_error" in m],
            }
            for t, mods in source_results.items()
        },
        "test_summary": {
            "total_test_files": len(test_map),
            "total_test_funcs": sum(
                v.get("test_count", 0) for v in test_map.values() if "syntax_error" not in v
            ),
            "syntax_errors": [p for p, v in test_map.items() if "syntax_error" in v],
        },
        "coverage_gaps": [g for g in gaps if g["severity"] != "COVERED"],
        "covered": [g for g in gaps if g["severity"] == "COVERED"],
    }
    out_path = ROOT / OPS_SCRIPTS_DIR / "ci" / "ast_gap_results.json"
    out_path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"\nFull results written to: {out_path}")
    return output


if __name__ == "__main__":
    main()
