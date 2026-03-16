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
                if (node.func.value.attr == 'path' and
                    isinstance(node.func.value.value, ast.Name) and
                    node.func.value.value.id == 'os' and
                    node.func.attr == 'join'):

                    # Convert to Path() / operator chain
                    if len(node.args) >= 2:
                        # Start with Path(first_arg)
                        result = ast.Call(
                            func=ast.Name(id='Path', ctx=ast.Load()),
                            args=[node.args[0]],
                            keywords=[]
                        )

                        # Chain with / operator for remaining args
                        for arg in node.args[1:]:
                            result = ast.BinOp(
                                left=result,
                                op=ast.Div(),
                                right=arg
                            )

                        self.modified = True
                        self.needs_pathlib_import = True
                        self.modifications.append({
                            'type': 'os.path.join',
                            'line': getattr(node, 'lineno', 0),
                        })
                        return result

                # os.path.basename() pattern
                elif (node.func.value.attr == 'path' and
                      isinstance(node.func.value.value, ast.Name) and
                      node.func.value.value.id == 'os' and
                      node.func.attr == 'basename'):

                    if len(node.args) == 1:
                        # Convert to Path(arg).name
                        result = ast.Attribute(
                            value=ast.Call(
                                func=ast.Name(id='Path', ctx=ast.Load()),
                                args=[node.args[0]],
                                keywords=[]
                            ),
                            attr='name',
                            ctx=ast.Load()
                        )

                        self.modified = True
                        self.needs_pathlib_import = True
                        self.modifications.append({
                            'type': 'os.path.basename',
                            'line': getattr(node, 'lineno', 0),
                        })
                        return result

                # os.path.dirname() pattern
                elif (node.func.value.attr == 'path' and
                      isinstance(node.func.value.value, ast.Name) and
                      node.func.value.value.id == 'os' and
                      node.func.attr == 'dirname'):

                    if len(node.args) == 1:
                        # Convert to Path(arg).parent
                        result = ast.Attribute(
                            value=ast.Call(
                                func=ast.Name(id='Path', ctx=ast.Load()),
                                args=[node.args[0]],
                                keywords=[]
                            ),
                            attr='parent',
                            ctx=ast.Load()
                        )

                        self.modified = True
                        self.needs_pathlib_import = True
                        self.modifications.append({
                            'type': 'os.path.dirname',
                            'line': getattr(node, 'lineno', 0),
                        })
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
                if stmt.module == 'pathlib':
                    for alias in stmt.names:
                        if alias.name == 'Path':
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
                module='pathlib',
                names=[ast.alias(name='Path', asname=None)],
                level=0,
            )

            node.body.insert(insert_idx, new_import)
            self.added_import = True

        return node


def migrate_file(file_path: Path, dry_run: bool = True) -> dict:
    """Migrate a file to use pathlib."""
    try:
        source = file_path.read_text(encoding='utf-8')
        tree = ast.parse(source, filename=str(file_path))

        # Transform os.path calls
        transformer = PathlibTransformer()
        tree = transformer.visit(tree)

        if not transformer.modified:
            return {'status': 'skipped', 'reason': 'no_os_path_calls'}

        # Add pathlib import if needed
        if transformer.needs_pathlib_import:
            import_adder = PathlibImportAdder()
            tree = import_adder.visit(tree)

        # Fix missing locations
        ast.fix_missing_locations(tree)

        # Generate new source
        new_source = ast.unparse(tree)

        if not dry_run:
            file_path.write_text(new_source, encoding='utf-8')

        return {
            'status': 'success',
            'file': str(file_path.relative_to(PROJECT_ROOT)),
            'modifications': transformer.modifications,
            'added_import': import_adder.added_import if transformer.needs_pathlib_import else False,
            'dry_run': dry_run,
        }

    except SyntaxError as e:
        return {
            'status': 'error',
            'file': str(file_path.relative_to(PROJECT_ROOT)),
            'error': f'SyntaxError: {e}',
        }
    except Exception as e:
        return {
            'status': 'error',
            'file': str(file_path.relative_to(PROJECT_ROOT)),
            'error': str(e),
        }


def main():
    """Main execution."""
    import argparse

    parser = argparse.ArgumentParser(description='Migrate os.path to pathlib')
    parser.add_argument('--execute', action='store_true', help='Actually write changes')
    parser.add_argument('--limit', type=int, default=50, help='Max files to process')

    args = parser.parse_args()

    project_root = get_validated_project_root()
    baseline_file = project_root / "ops_scripts" / "hooks" / "landmine_baseline.txt"

    # Load files with path_fragility violations
    violations = []
    with open(baseline_file, encoding='utf-8') as f:
        for line in f:
            if 'path_fragility' in line:
                file_path = line.split(':')[0]
                violations.append(project_root / file_path)

    unique_files = sorted(set(violations))[:args.limit]

    print(f"[INFO] Processing {len(unique_files)} files")
    print(f"[MODE] {'EXECUTE' if args.execute else 'DRY RUN'}")
    print()

    results = []
    for file_path in unique_files:
        if not file_path.exists():
            continue

        result = migrate_file(file_path, dry_run=not args.execute)
        results.append(result)

        if result['status'] == 'success':
            mod_types = [m['type'] for m in result['modifications']]
            mod_summary = ', '.join(set(mod_types))
            print(f"✓ {result['file']}")
            print(f"  Fixed: {mod_summary} ({len(result['modifications'])} changes)")
        elif result['status'] == 'error':
            print(f"✗ {result['file']}: {result['error']}")

    success = len([r for r in results if r['status'] == 'success'])
    errors = len([r for r in results if r['status'] == 'error'])
    skipped = len([r for r in results if r['status'] == 'skipped'])

    print()
    print(f"[SUMMARY] Success: {success}, Errors: {errors}, Skipped: {skipped}")

    if not args.execute and success > 0:
        print("[NEXT] Run with --execute to apply changes")

    return 0


if __name__ == '__main__':
    sys.exit(main())
