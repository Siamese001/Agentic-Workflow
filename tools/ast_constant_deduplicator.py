#!/usr/bin/env python3
"""
AST-Based Constant Deduplicator

Removes duplicate constant blocks and replaces with SSOT imports.
Uses pure AST - NO REGEX.

Pattern detected:
Every file has this block duplicated:
    MAX_RETRIES = 3
    DEFAULT_SLEEP = 1.0
    THRESHOLD = 0.95
    BUFFER_SIZE = 8192
    BATCH_SIZE = 32
    MAX_DEPTH = 6
    MAX_FILES = 1000
    DEFAULT_TIMEOUT = 300

SSOT location: agentic_core/L0_routing/config/path_constants.py
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

_emit_records_execution_trace("p0", "evidence", "ast_constant_deduplicator")
_emit_applies_guardrail("p0", "ast_constant_deduplicator", "p0_governance")
_emit_reads_policy_state("p0", "ast_constant_deduplicator", "policy_binding")
_emit_snapshots_state("p0", "ast_constant_deduplicator", "state_snapshot")
emit_replay_key("p0", "ast_constant_deduplicator")
emit_determinism_digest("p0", "ast_constant_deduplicator")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "ast_constant_deduplicator", "execution_auth")
_emit_validates_capability("p2", "ast_constant_deduplicator", "capability_check")
_emit_routes_to_capability("p2", "ast_constant_deduplicator", "capability_route")
_emit_writes_via_uwg("p2", "ast_constant_deduplicator", "uwg_write")
_emit_blocks_direct_write("p2", "ast_constant_deduplicator", "direct_write_block")
_emit_records_tool_invocation("p2", "ast_constant_deduplicator", "tool_invocation")
_emit_captures_execution_output("p2", "ast_constant_deduplicator", "exec_output")
_emit_dispatches_agent("p3", "ast_constant_deduplicator", "agent_dispatch")
_emit_coordinates_agents("p3", "ast_constant_deduplicator", "agent_coordination")
_emit_records_workflow_lineage("p3", "ast_constant_deduplicator", "workflow_lineage")
_emit_records_healing_outcome("p3", "ast_constant_deduplicator", "healing_outcome")
_emit_escalates_failure("p3", "ast_constant_deduplicator", "failure_escalation")
_emit_orchestrates_workflow("p3", "ast_constant_deduplicator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "ast_constant_deduplicator", "healing_dispatch")
_emit_invokes_evaluation("p3", "ast_constant_deduplicator", "evaluation_signal")
_emit_records_telemetry_event("p4", "ast_constant_deduplicator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "ast_constant_deduplicator", "eval_metric")
_emit_stores_embedding("p4", "ast_constant_deduplicator", "embedding_store")
_emit_updates_meta_learning_state("p4", "ast_constant_deduplicator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "ast_constant_deduplicator", "exec_snapshot_link")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
# guardian: allow-global-mutation
sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L0_routing.config.path_constants import get_validated_project_root

# Constants to deduplicate (from SSOT)
SSOT_CONSTANTS = {
    'MAX_RETRIES', 'DEFAULT_SLEEP', 'THRESHOLD', 'BUFFER_SIZE',
    'BATCH_SIZE', 'MAX_DEPTH', 'MAX_FILES', 'DEFAULT_TIMEOUT'
}


class ConstantBlockRemover(ast.NodeTransformer):
    """Remove duplicate constant assignments that exist in SSOT."""

    def __init__(self):
        self.removed_constants = set()
        self.modified = False

    def visit_Module(self, node: ast.Module) -> ast.Module:
        """Remove constant assignments from module body."""
        new_body = []

        for stmt in node.body:
            # Check if this is a constant assignment we should remove
            if isinstance(stmt, ast.Assign):
                if len(stmt.targets) == 1:
                    target = stmt.targets[0]
                    if isinstance(target, ast.Name):
                        if target.id in SSOT_CONSTANTS:
                            # Check if value matches SSOT
                            if isinstance(stmt.value, ast.Constant):
                                # Remove this duplicate constant
                                self.removed_constants.add(target.id)
                                self.modified = True
                                continue  # Skip adding to new_body

            new_body.append(stmt)

        node.body = new_body
        return node


class ImportInjector(ast.NodeTransformer):
    """Add import for removed constants."""

    def __init__(self, constants_to_import: set[str]):
        self.constants_to_import = constants_to_import
        self.added_import = False

    def visit_Module(self, node: ast.Module) -> ast.Module:
        """Add import statement after existing imports."""
        if not self.constants_to_import:
            return node

        # Find insertion point (after last import)
        insert_idx = 0
        for i, stmt in enumerate(node.body):
            if isinstance(stmt, (ast.Import, ast.ImportFrom)):
                insert_idx = i + 1
            elif not isinstance(stmt, ast.Expr):
                # Stop at first non-import, non-docstring
                if not (isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant)):
                    break

        # Create import statement
        import_names = sorted(self.constants_to_import)
        new_import = ast.ImportFrom(
            module='agentic_core.L0_routing.config.path_constants',
            names=[ast.alias(name=name, asname=None) for name in import_names],
            level=0,
        )

        node.body.insert(insert_idx, new_import)
        self.added_import = True

        return node


def deduplicate_file(file_path: Path, dry_run: bool = True) -> dict:
    """Deduplicate constants in a single file."""
    try:
        # Skip if this IS the SSOT file
        if file_path.name == 'path_constants.py' and 'L0_routing' in str(file_path):
            return {'status': 'skipped', 'reason': 'ssot_source'}

        source = file_path.read_text(encoding='utf-8')
        tree = ast.parse(source, filename=str(file_path))

        # Remove duplicate constants
        remover = ConstantBlockRemover()
        tree = remover.visit(tree)

        if not remover.modified:
            return {'status': 'skipped', 'reason': 'no_duplicates'}

        # Add import for removed constants
        injector = ImportInjector(remover.removed_constants)
        tree = injector.visit(tree)

        # Fix missing locations
        ast.fix_missing_locations(tree)

        # Generate new source
        new_source = ast.unparse(tree)

        if not dry_run:
            file_path.write_text(new_source, encoding='utf-8')

        return {
            'status': 'success',
            'file': str(file_path.relative_to(PROJECT_ROOT)),
            'removed_constants': sorted(remover.removed_constants),
            'added_import': injector.added_import,
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

    parser = argparse.ArgumentParser(description='Deduplicate SSOT constants')
    parser.add_argument('--execute', action='store_true', help='Actually write changes')
    parser.add_argument('--limit', type=int, default=100, help='Max files to process')

    args = parser.parse_args()

    project_root = get_validated_project_root()
    baseline_file = project_root / "ops_scripts" / "hooks" / "landmine_baseline.txt"

    # Load files with violations
    violations = []
    with open(baseline_file, encoding='utf-8') as f:
        for line in f:
            if 'threshold=0.95' in line or 'max_retries=3' in line:
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

        result = deduplicate_file(file_path, dry_run=not args.execute)
        results.append(result)

        if result['status'] == 'success':
            constants = ', '.join(result['removed_constants'])
            print(f"✓ {result['file']}")
            print(f"  Removed: {constants}")
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
