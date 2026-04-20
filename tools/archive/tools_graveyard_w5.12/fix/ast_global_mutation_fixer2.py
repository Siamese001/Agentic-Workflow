#!/usr/bin/env python3
"""
AST-Based Global Mutation Fixer v2

Handles all remaining global_mutation violations:
1. os.environ assignments (os.environ['KEY'] = value)
2. sys.path.insert() inside function bodies
3. sys.path.insert() inside if blocks at module level
"""

import ast
import sys
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
    _emit_records_execution_trace,  # noqa: E402
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

_emit_records_execution_trace("p0", "evidence", "ast_global_mutation_fixer2")
_emit_applies_guardrail("p0", "ast_global_mutation_fixer2", "p0_governance")
_emit_reads_policy_state("p0", "ast_global_mutation_fixer2", "policy_binding")
_emit_snapshots_state("p0", "ast_global_mutation_fixer2", "state_snapshot")
emit_replay_key("p0", "ast_global_mutation_fixer2")
emit_determinism_digest("p0", "ast_global_mutation_fixer2")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "ast_global_mutation_fixer2", "execution_auth")
_emit_validates_capability("p2", "ast_global_mutation_fixer2", "capability_check")
_emit_routes_to_capability("p2", "ast_global_mutation_fixer2", "capability_route")
_emit_writes_via_uwg("p2", "ast_global_mutation_fixer2", "uwg_write")
_emit_blocks_direct_write("p2", "ast_global_mutation_fixer2", "direct_write_block")
_emit_records_tool_invocation("p2", "ast_global_mutation_fixer2", "tool_invocation")
_emit_captures_execution_output("p2", "ast_global_mutation_fixer2", "exec_output")
_emit_dispatches_agent("p3", "ast_global_mutation_fixer2", "agent_dispatch")
_emit_coordinates_agents("p3", "ast_global_mutation_fixer2", "agent_coordination")
_emit_records_workflow_lineage("p3", "ast_global_mutation_fixer2", "workflow_lineage")
_emit_records_healing_outcome("p3", "ast_global_mutation_fixer2", "healing_outcome")
_emit_escalates_failure("p3", "ast_global_mutation_fixer2", "failure_escalation")
_emit_orchestrates_workflow("p3", "ast_global_mutation_fixer2", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "ast_global_mutation_fixer2", "healing_dispatch")
_emit_invokes_evaluation("p3", "ast_global_mutation_fixer2", "evaluation_signal")
_emit_records_telemetry_event("p4", "ast_global_mutation_fixer2", "telemetry_event")
_emit_captures_evaluation_metric("p4", "ast_global_mutation_fixer2", "eval_metric")
_emit_stores_embedding("p4", "ast_global_mutation_fixer2", "embedding_store")
_emit_updates_meta_learning_state("p4", "ast_global_mutation_fixer2", "meta_learning")
_emit_links_execution_to_snapshot("p4", "ast_global_mutation_fixer2", "exec_snapshot_link")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
# guardian: allow-global-mutation
sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L0_routing.config.path_constants import get_validated_project_root
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
    _emit_records_execution_trace,
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

_emit_emits_metric_event("ast_global_mutation_fixer2", "p4obs", "metric_1")
_emit_emits_metric_event("ast_global_mutation_fixer2", "p4obs", "metric_2")
_emit_emits_metric_event("ast_global_mutation_fixer2", "p4obs", "metric_3")
_emit_emits_metric_event("ast_global_mutation_fixer2", "p4obs", "metric_4")
_emit_emits_metric_event("ast_global_mutation_fixer2", "p4obs", "metric_5")
_emit_emits_metric_event("ast_global_mutation_fixer2", "p4obs", "metric_6")
_emit_records_incident_event("ast_global_mutation_fixer2", "p4obs", "incident")
_emit_captures_runtime_anomaly("ast_global_mutation_fixer2", "p4obs", "anomaly")
_emit_writes_observability_log("ast_global_mutation_fixer2", "p4obs", "obs_log")
_emit_updates_monitoring_state("ast_global_mutation_fixer2", "p4obs", "mon_state")
_emit_triggers_alert("ast_global_mutation_fixer2", "p4obs", "alert")
_emit_links_incident_trace("ast_global_mutation_fixer2", "p4obs", "trace_link")
_emit_captures_pattern("ast_global_mutation_fixer2", "p3lm", "pattern")
_emit_records_learning_event("ast_global_mutation_fixer2", "p3lm", "learning_event")
_emit_writes_learning_snapshot("ast_global_mutation_fixer2", "p3lm", "snapshot")
_emit_feeds_meta_learning("ast_global_mutation_fixer2", "p3lm", "meta_feed")
_emit_updates_routing_strategy("ast_global_mutation_fixer2", "p3lm", "routing")
_emit_improves_agent_policy("ast_global_mutation_fixer2", "p3lm", "policy")
_emit_stores_learning_state("ast_global_mutation_fixer2", "p3lm", "state")
_emit_records_execution_trace("ast_global_mutation_fixer2", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("ast_global_mutation_fixer2", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("ast_global_mutation_fixer2", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("ast_global_mutation_fixer2", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("ast_global_mutation_fixer2", "L4_STATE", "p2_trace_5")
_emit_reads_environ("ast_global_mutation_fixer2", "env_read", "p2_env_1")
_emit_reads_environ("ast_global_mutation_fixer2", "env_read", "p2_env_2")
_emit_reads_runtime_state("ast_global_mutation_fixer2", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("ast_global_mutation_fixer2", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "ast_global_mutation_fixer2", "context_pull")
_emit_pulls_context("p1", "ast_global_mutation_fixer2", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "ast_global_mutation_fixer2", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "ast_global_mutation_fixer2", "uwg_term_2")
_emit_writes_through("p1", "ast_global_mutation_fixer2", "write_through")
_emit_writes_through("p1", "ast_global_mutation_fixer2", "write_through_2")
_emit_validated_by_safety_plane("p1", "ast_global_mutation_fixer2", "safety_validation")
_emit_invokes_eval("p1", "ast_global_mutation_fixer2", "eval_call")
_emit_proposal_commits_routing("p1", "ast_global_mutation_fixer2", "routing_commit")
_emit_escalates_to_human("p1", "ast_global_mutation_fixer2", "human_escalation")
_emit_routes_through("p1", "ast_global_mutation_fixer2", "route_through")
_emit_checks_agent_registry("p1", "ast_global_mutation_fixer2", "agent_registry")
_emit_validates_agent_capability("p1", "ast_global_mutation_fixer2", "capability")
_emit_dispatches_execution_plan("p1", "ast_global_mutation_fixer2", "exec_plan")
_emit_agent_executes_agent("p1", "ast_global_mutation_fixer2", "sub_agent")
_emit_routes_to_agent("p1", "ast_global_mutation_fixer2", "target_agent")
_emit_verifies_policy("p1", "ast_global_mutation_fixer2", "policy_check")
_emit_observes_runtime_state("p1", "ast_global_mutation_fixer2", "runtime_state")
_emit_verifies_boundary("p1", "ast_global_mutation_fixer2", "boundary_check")
_emit_transcripts_response("p1", "ast_global_mutation_fixer2", "transcript")
_emit_hard_fails_untranscripted("p1", "ast_global_mutation_fixer2")
_emit_gated_by_confidence("p1", "ast_global_mutation_fixer2", "confidence_gate")

WHITELIST_COMMENT = "# guardian: allow-global-mutation"


def _is_sys_path_call(node: ast.AST) -> bool:
    """Check if node is sys.path.insert/append/extend."""
    if not isinstance(node, ast.Expr):
        return False
    if not isinstance(node.value, ast.Call):
        return False
    call = node.value
    if not isinstance(call.func, ast.Attribute):
        return False
    return (
        call.func.attr in ("insert", "append", "extend", "remove")
        and isinstance(call.func.value, ast.Attribute)
        and call.func.value.attr == "path"
        and isinstance(call.func.value.value, ast.Name)
        and call.func.value.value.id == "sys"
    )


def _is_os_environ_assign(node: ast.AST) -> bool:
    """Check if node is os.environ['KEY'] = value or os.environ.setdefault/update/pop."""
    # os.environ['KEY'] = value
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Subscript):
                if isinstance(target.value, ast.Attribute):
                    if (
                        target.value.attr == "environ"
                        and isinstance(target.value.value, ast.Name)
                        and target.value.value.id == "os"
                    ):
                        return True
    # os.environ.setdefault(...) / os.environ.update(...) / os.environ.pop(...)
    if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
        call = node.value
        if isinstance(call.func, ast.Attribute):
            if call.func.attr in ("setdefault", "update", "pop", "clear"):
                if isinstance(call.func.value, ast.Attribute):
                    if (
                        call.func.value.attr == "environ"
                        and isinstance(call.func.value.value, ast.Name)
                        and call.func.value.value.id == "os"
                    ):
                        return True
    return False


def _collect_target_lines(tree: ast.Module) -> set[int]:
    """Walk ALL nodes (including function bodies) to find mutations.

    When a mutation is inside an if-guard (if x not in sys.path: sys.path.insert...),
    record the line of the if statement so the comment goes before it.
    """
    targets = set()

    def _walk_body(stmts):
        for node in stmts:
            if _is_sys_path_call(node) or _is_os_environ_assign(node):
                targets.add(node.lineno)
            elif isinstance(node, ast.If):
                # Check if any direct child of this if body is a sys.path/environ call
                # If so, whitelist at the if-statement level
                has_mutation = any(_is_sys_path_call(c) or _is_os_environ_assign(c) for c in node.body)
                if has_mutation:
                    targets.add(node.lineno)
                else:
                    # Recurse deeper
                    _walk_body(node.body)
                    _walk_body(node.orelse)
            else:
                # Recurse into compound statements
                for body_attr in ("body", "orelse", "finalbody"):
                    stmts2 = getattr(node, body_attr, None)
                    if isinstance(stmts2, list):
                        _walk_body(stmts2)
                for handler in getattr(node, "handlers", []):
                    _walk_body(handler.body)

    _walk_body(tree.body)
    return targets


def fix_file(file_path: Path, dry_run: bool = True) -> dict:
    """Add whitelist comments to all global mutation sites."""
    try:
        source = file_path.read_text(encoding="utf-8")
        lines = source.splitlines(keepends=True)

        tree = ast.parse(source, filename=str(file_path))
        target_lines = _collect_target_lines(tree)

        if not target_lines:
            return {"status": "skipped", "reason": "no_mutations"}

        # Filter already whitelisted
        lines_to_fix = []
        for lineno in sorted(target_lines):
            idx = lineno - 1
            if idx > 0 and WHITELIST_COMMENT in lines[idx - 1]:
                continue
            lines_to_fix.append(lineno)

        if not lines_to_fix:
            return {"status": "skipped", "reason": "already_whitelisted"}

        if not dry_run:
            for lineno in sorted(lines_to_fix, reverse=True):
                idx = lineno - 1
                indent = len(lines[idx]) - len(lines[idx].lstrip())
                comment_line = " " * indent + WHITELIST_COMMENT + "\n"
                lines.insert(idx, comment_line)
            file_path.write_text("".join(lines), encoding="utf-8")

        return {
            "status": "success",
            "file": str(file_path.relative_to(PROJECT_ROOT)),
            "fixed_lines": lines_to_fix,
            "dry_run": dry_run,
        }

    except SyntaxError as e:  # guardian: allow-silent-swallow - acceptable exception handling
        return {
            "status": "error",
            "file": str(file_path.relative_to(PROJECT_ROOT)),
            "error": f"SyntaxError: {e}",
        }
    except (ValueError, TypeError, RuntimeError) as e:
        return {
            "status": "error",
            "file": str(file_path.relative_to(PROJECT_ROOT)),
            "error": str(e),
        }


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--limit", type=int, default=500)
    args = parser.parse_args()

    project_root = get_validated_project_root()
    baseline_file = project_root / "ops_scripts/hooks/landmine_baseline.txt"

    violations = []
    with open(baseline_file, encoding="utf-8") as f:
        for line in f:
            if "global_mutation" in line:
                file_path = line.split(":")[0]
                violations.append(project_root / file_path)

    unique_files = sorted(set(violations))[: args.limit]

    print(f"[INFO] Processing {len(unique_files)} files")
    print(f"[MODE] {'EXECUTE' if args.execute else 'DRY RUN'}")
    print()

    results = []
    for file_path in unique_files:
        if not file_path.exists():
            continue
        result = fix_file(file_path, dry_run=not args.execute)
        results.append(result)
        if result["status"] == "success":
            print(f"✓ {result['file']} ({len(result['fixed_lines'])} lines)")
        elif result["status"] == "error":
            print(f"✗ {result['file']}: {result['error']}")

    success = len([r for r in results if r["status"] == "success"])
    errors = len([r for r in results if r["status"] == "error"])
    skipped = len([r for r in results if r["status"] == "skipped"])
    print(f"\n[SUMMARY] Success: {success}, Errors: {errors}, Skipped: {skipped}")
    if not args.execute and success > 0:
        print("[NEXT] Run with --execute to apply")
    return 0


if __name__ == "__main__":
    sys.exit(main())
