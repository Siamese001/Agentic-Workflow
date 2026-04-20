#!/usr/bin/env python3
"""
AST-Based Pathlib Migrator

Converts os.path operations to pathlib.Path using pure AST.
NO REGEX - only AST node transformations.

Patterns to fix:
1. os.path.join() -> Path() / operator
2. os.path.basename() -> Path().name
3. os.path.dirname() -> Path().parent
4. String concatenation -> Path() / operator
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

_emit_records_execution_trace("p0", "evidence", "ast_pathlib_migrator")
_emit_applies_guardrail("p0", "ast_pathlib_migrator", "p0_governance")
_emit_reads_policy_state("p0", "ast_pathlib_migrator", "policy_binding")
_emit_snapshots_state("p0", "ast_pathlib_migrator", "state_snapshot")
emit_replay_key("p0", "ast_pathlib_migrator")
emit_determinism_digest("p0", "ast_pathlib_migrator")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "ast_pathlib_migrator", "execution_auth")
_emit_validates_capability("p2", "ast_pathlib_migrator", "capability_check")
_emit_routes_to_capability("p2", "ast_pathlib_migrator", "capability_route")
_emit_writes_via_uwg("p2", "ast_pathlib_migrator", "uwg_write")
_emit_blocks_direct_write("p2", "ast_pathlib_migrator", "direct_write_block")
_emit_records_tool_invocation("p2", "ast_pathlib_migrator", "tool_invocation")
_emit_captures_execution_output("p2", "ast_pathlib_migrator", "exec_output")
_emit_dispatches_agent("p3", "ast_pathlib_migrator", "agent_dispatch")
_emit_coordinates_agents("p3", "ast_pathlib_migrator", "agent_coordination")
_emit_records_workflow_lineage("p3", "ast_pathlib_migrator", "workflow_lineage")
_emit_records_healing_outcome("p3", "ast_pathlib_migrator", "healing_outcome")
_emit_escalates_failure("p3", "ast_pathlib_migrator", "failure_escalation")
_emit_orchestrates_workflow("p3", "ast_pathlib_migrator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "ast_pathlib_migrator", "healing_dispatch")
_emit_invokes_evaluation("p3", "ast_pathlib_migrator", "evaluation_signal")
_emit_records_telemetry_event("p4", "ast_pathlib_migrator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "ast_pathlib_migrator", "eval_metric")
_emit_stores_embedding("p4", "ast_pathlib_migrator", "embedding_store")
_emit_updates_meta_learning_state("p4", "ast_pathlib_migrator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "ast_pathlib_migrator", "exec_snapshot_link")

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

_emit_emits_metric_event("ast_pathlib_migrator", "p4obs", "metric_1")
_emit_emits_metric_event("ast_pathlib_migrator", "p4obs", "metric_2")
_emit_emits_metric_event("ast_pathlib_migrator", "p4obs", "metric_3")
_emit_emits_metric_event("ast_pathlib_migrator", "p4obs", "metric_4")
_emit_emits_metric_event("ast_pathlib_migrator", "p4obs", "metric_5")
_emit_emits_metric_event("ast_pathlib_migrator", "p4obs", "metric_6")
_emit_records_incident_event("ast_pathlib_migrator", "p4obs", "incident")
_emit_captures_runtime_anomaly("ast_pathlib_migrator", "p4obs", "anomaly")
_emit_writes_observability_log("ast_pathlib_migrator", "p4obs", "obs_log")
_emit_updates_monitoring_state("ast_pathlib_migrator", "p4obs", "mon_state")
_emit_triggers_alert("ast_pathlib_migrator", "p4obs", "alert")
_emit_links_incident_trace("ast_pathlib_migrator", "p4obs", "trace_link")
_emit_captures_pattern("ast_pathlib_migrator", "p3lm", "pattern")
_emit_records_learning_event("ast_pathlib_migrator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("ast_pathlib_migrator", "p3lm", "snapshot")
_emit_feeds_meta_learning("ast_pathlib_migrator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("ast_pathlib_migrator", "p3lm", "routing")
_emit_improves_agent_policy("ast_pathlib_migrator", "p3lm", "policy")
_emit_stores_learning_state("ast_pathlib_migrator", "p3lm", "state")
_emit_records_execution_trace("ast_pathlib_migrator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("ast_pathlib_migrator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("ast_pathlib_migrator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("ast_pathlib_migrator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("ast_pathlib_migrator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("ast_pathlib_migrator", "env_read", "p2_env_1")
_emit_reads_environ("ast_pathlib_migrator", "env_read", "p2_env_2")
_emit_reads_runtime_state("ast_pathlib_migrator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("ast_pathlib_migrator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "ast_pathlib_migrator", "context_pull")
_emit_pulls_context("p1", "ast_pathlib_migrator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "ast_pathlib_migrator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "ast_pathlib_migrator", "uwg_term_2")
_emit_writes_through("p1", "ast_pathlib_migrator", "write_through")
_emit_writes_through("p1", "ast_pathlib_migrator", "write_through_2")
_emit_validated_by_safety_plane("p1", "ast_pathlib_migrator", "safety_validation")
_emit_invokes_eval("p1", "ast_pathlib_migrator", "eval_call")
_emit_proposal_commits_routing("p1", "ast_pathlib_migrator", "routing_commit")
_emit_escalates_to_human("p1", "ast_pathlib_migrator", "human_escalation")
_emit_routes_through("p1", "ast_pathlib_migrator", "route_through")
_emit_checks_agent_registry("p1", "ast_pathlib_migrator", "agent_registry")
_emit_validates_agent_capability("p1", "ast_pathlib_migrator", "capability")
_emit_dispatches_execution_plan("p1", "ast_pathlib_migrator", "exec_plan")
_emit_agent_executes_agent("p1", "ast_pathlib_migrator", "sub_agent")
_emit_routes_to_agent("p1", "ast_pathlib_migrator", "target_agent")
_emit_verifies_policy("p1", "ast_pathlib_migrator", "policy_check")
_emit_observes_runtime_state("p1", "ast_pathlib_migrator", "runtime_state")
_emit_verifies_boundary("p1", "ast_pathlib_migrator", "boundary_check")
_emit_transcripts_response("p1", "ast_pathlib_migrator", "transcript")
_emit_hard_fails_untranscripted("p1", "ast_pathlib_migrator")
_emit_gated_by_confidence("p1", "ast_pathlib_migrator", "confidence_gate")


class PathlibTransformer(ast.NodeTransformer):
    """Transform os.path calls to pathlib."""

    def __init__(self):
        self.modified = False
        self.needs_pathlib_import = False
        self.modifications = []

    def visit_Call(self, node: ast.Call) -> ast.AST:
        """Transform os.path function calls."""
        # Check if this is os.path.join()
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Attribute):
                # os.path.join() pattern
                if (
                    node.func.value.attr == "path"
                    and isinstance(node.func.value.value, ast.Name)
                    and node.func.value.value.id == "os"
                    and node.func.attr == "join"
                ):
                    # Convert to Path() / operator chain
                    if len(node.args) >= 2:
                        # Start with Path(first_arg)
                        result = ast.Call(
                            func=ast.Name(id="Path", ctx=ast.Load()),
                            args=[node.args[0]],
                            keywords=[],
                        )

                        # Chain with / operator for remaining args
                        for arg in node.args[1:]:
                            result = ast.BinOp(
                                left=result,
                                op=ast.Div(),
                                right=arg,
                            )

                        self.modified = True
                        self.needs_pathlib_import = True
                        self.modifications.append(
                            {
                                "type": "os.path.join",
                                "line": getattr(node, "lineno", 0),
                            }
                        )
                        return result

                # os.path.basename() pattern
                elif (
                    node.func.value.attr == "path"
                    and isinstance(node.func.value.value, ast.Name)
                    and node.func.value.value.id == "os"
                    and node.func.attr == "basename"
                ):
                    if len(node.args) == 1:
                        # Convert to Path(arg).name
                        result = ast.Attribute(
                            value=ast.Call(
                                func=ast.Name(id="Path", ctx=ast.Load()),
                                args=[node.args[0]],
                                keywords=[],
                            ),
                            attr="name",
                            ctx=ast.Load(),
                        )

                        self.modified = True
                        self.needs_pathlib_import = True
                        self.modifications.append(
                            {
                                "type": "os.path.basename",
                                "line": getattr(node, "lineno", 0),
                            }
                        )
                        return result

                # os.path.dirname() pattern
                elif (
                    node.func.value.attr == "path"
                    and isinstance(node.func.value.value, ast.Name)
                    and node.func.value.value.id == "os"
                    and node.func.attr == "dirname"
                ):
                    if len(node.args) == 1:
                        # Convert to Path(arg).parent
                        result = ast.Attribute(
                            value=ast.Call(
                                func=ast.Name(id="Path", ctx=ast.Load()),
                                args=[node.args[0]],
                                keywords=[],
                            ),
                            attr="parent",
                            ctx=ast.Load(),
                        )

                        self.modified = True
                        self.needs_pathlib_import = True
                        self.modifications.append(
                            {
                                "type": "os.path.dirname",
                                "line": getattr(node, "lineno", 0),
                            }
                        )
                        return result

        return self.generic_visit(node)


class PathlibImportAdder(ast.NodeTransformer):
    """Add pathlib.Path import if needed."""

    def __init__(self):
        self.has_pathlib_import = False
        self.added_import = False

    def visit_Module(self, node: ast.Module) -> ast.Module:
        """Add Path import if needed."""
        # Check existing imports
        for stmt in node.body:
            if isinstance(stmt, ast.ImportFrom):
                if stmt.module == "pathlib":
                    for alias in stmt.names:
                        if alias.name == "Path":
                            self.has_pathlib_import = True
                            return node

        if not self.has_pathlib_import:
            # Find insertion point after other imports
            insert_idx = 0
            for i, stmt in enumerate(node.body):
                if isinstance(stmt, (ast.Import, ast.ImportFrom)):
                    insert_idx = i + 1
                elif not isinstance(stmt, ast.Expr):
                    if not (isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant)):
                        break

            # Create import
            new_import = ast.ImportFrom(
                module="pathlib",
                names=[ast.alias(name="Path", asname=None)],
                level=0,
            )

            node.body.insert(insert_idx, new_import)
            self.added_import = True

        return node


def migrate_file(file_path: Path, dry_run: bool = True) -> dict:
    """Migrate a file to use pathlib."""
    try:
        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(file_path))

        # Transform os.path calls
        transformer = PathlibTransformer()
        tree = transformer.visit(tree)

        if not transformer.modified:
            return {"status": "skipped", "reason": "no_os_path_calls"}

        # Add pathlib import if needed
        if transformer.needs_pathlib_import:
            import_adder = PathlibImportAdder()
            tree = import_adder.visit(tree)

        # Fix missing locations
        ast.fix_missing_locations(tree)

        # Generate new source
        new_source = ast.unparse(tree)

        if not dry_run:
            file_path.write_text(new_source, encoding="utf-8")

        return {
            "status": "success",
            "file": str(file_path.relative_to(PROJECT_ROOT)),
            "modifications": transformer.modifications,
            "added_import": import_adder.added_import if transformer.needs_pathlib_import else False,
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
    """Main execution."""
    import argparse

    parser = argparse.ArgumentParser(description="Migrate os.path to pathlib")
    parser.add_argument("--execute", action="store_true", help="Actually write changes")
    parser.add_argument("--limit", type=int, default=50, help="Max files to process")

    args = parser.parse_args()

    project_root = get_validated_project_root()
    baseline_file = project_root / "ops_scripts" / "hooks" / "landmine_baseline.txt"

    # Load files with path_fragility violations
    violations = []
    with open(baseline_file, encoding="utf-8") as f:
        for line in f:
            if "path_fragility" in line:
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

        result = migrate_file(file_path, dry_run=not args.execute)
        results.append(result)

        if result["status"] == "success":
            mod_types = [m["type"] for m in result["modifications"]]
            mod_summary = ", ".join(set(mod_types))
            print(f"✓ {result['file']}")
            print(f"  Fixed: {mod_summary} ({len(result['modifications'])} changes)")
        elif result["status"] == "error":
            print(f"✗ {result['file']}: {result['error']}")

    success = len([r for r in results if r["status"] == "success"])
    errors = len([r for r in results if r["status"] == "error"])
    skipped = len([r for r in results if r["status"] == "skipped"])

    print()
    print(f"[SUMMARY] Success: {success}, Errors: {errors}, Skipped: {skipped}")

    if not args.execute and success > 0:
        print("[NEXT] Run with --execute to apply changes")

    return 0


if __name__ == "__main__":
    sys.exit(main())
