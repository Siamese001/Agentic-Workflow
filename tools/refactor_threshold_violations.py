#!/usr/bin/env python3
"""
ADG-Guided Threshold Refactoring

Systematically replaces hardcoded threshold=0.95 with THRESHOLD import
from agentic_core.L0_routing.config.path_constants.

Uses AST transformation to ensure syntactically correct refactoring.
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

_emit_records_execution_trace("p0", "evidence", "refactor_threshold_violations")
_emit_applies_guardrail("p0", "refactor_threshold_violations", "p0_governance")
_emit_reads_policy_state("p0", "refactor_threshold_violations", "policy_binding")
_emit_snapshots_state("p0", "refactor_threshold_violations", "state_snapshot")
emit_replay_key("p0", "refactor_threshold_violations")
emit_determinism_digest("p0", "refactor_threshold_violations")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "refactor_threshold_violations", "execution_auth")
_emit_validates_capability("p2", "refactor_threshold_violations", "capability_check")
_emit_routes_to_capability("p2", "refactor_threshold_violations", "capability_route")
_emit_writes_via_uwg("p2", "refactor_threshold_violations", "uwg_write")
_emit_blocks_direct_write("p2", "refactor_threshold_violations", "direct_write_block")
_emit_records_tool_invocation("p2", "refactor_threshold_violations", "tool_invocation")
_emit_captures_execution_output("p2", "refactor_threshold_violations", "exec_output")
_emit_dispatches_agent("p3", "refactor_threshold_violations", "agent_dispatch")
_emit_coordinates_agents("p3", "refactor_threshold_violations", "agent_coordination")
_emit_records_workflow_lineage("p3", "refactor_threshold_violations", "workflow_lineage")
_emit_records_healing_outcome("p3", "refactor_threshold_violations", "healing_outcome")
_emit_escalates_failure("p3", "refactor_threshold_violations", "failure_escalation")
_emit_orchestrates_workflow("p3", "refactor_threshold_violations", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "refactor_threshold_violations", "healing_dispatch")
_emit_invokes_evaluation("p3", "refactor_threshold_violations", "evaluation_signal")
_emit_records_telemetry_event("p4", "refactor_threshold_violations", "telemetry_event")
_emit_captures_evaluation_metric("p4", "refactor_threshold_violations", "eval_metric")
_emit_stores_embedding("p4", "refactor_threshold_violations", "embedding_store")
_emit_updates_meta_learning_state("p4", "refactor_threshold_violations", "meta_learning")
_emit_links_execution_to_snapshot("p4", "refactor_threshold_violations", "exec_snapshot_link")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
# guardian: allow-global-mutation
sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L0_routing.config.path_constants import get_validated_project_root


class ThresholdReplacer(ast.NodeTransformer):
    """Replace threshold=0.95 with THRESHOLD constant."""

    def __init__(self):
        self.modified = False
        self.nodes_to_remove = []

    def visit_Assign(self, node: ast.Assign) -> ast.Assign | None:
        """Replace module-level threshold assignments."""
        if isinstance(node.value, ast.Constant) and node.value.value == 0.95:
            for target in node.targets:
                if isinstance(target, ast.Name):
                    var_name = target.id.upper()
                    # If variable IS named THRESHOLD, remove this assignment entirely
                    # since we'll import it instead
                    if var_name == 'THRESHOLD':
                        self.nodes_to_remove.append(node)
                        self.modified = True
                        return None  # Remove this node
        return self.generic_visit(node)

    def visit_keyword(self, node: ast.keyword) -> ast.keyword:
        """Replace threshold=0.95 in function calls."""
        if node.arg and 'threshold' in node.arg.lower():
            if isinstance(node.value, ast.Constant) and node.value.value == 0.95:
                node.value = ast.Name(id='THRESHOLD', ctx=ast.Load())
                self.modified = True
        return self.generic_visit(node)


def add_threshold_import(source: str, file_path: Path) -> str:
    """Add THRESHOLD import to file if not present."""
    lines = source.splitlines(keepends=True)

    # Check if import already exists
    if 'from agentic_core.L0_routing.config.path_constants import' in source:
        # Check if THRESHOLD is in the import
        if 'THRESHOLD' in source:
            return source

        # Add THRESHOLD to existing import
        for i, line in enumerate(lines):
            if 'from agentic_core.L0_routing.config.path_constants import' in line:
                # Check if it's a multi-line import
                if '(' in line:
                    # Find closing paren
                    for j in range(i, len(lines)):
                        if ')' in lines[j]:
                            # Add THRESHOLD before closing paren
                            lines[j] = lines[j].replace(')', ',\n    THRESHOLD,\n)')
                            break
                else:
                    # Single line import - add THRESHOLD
                    lines[i] = line.rstrip().rstrip(',') + ',\n'
                    lines.insert(i + 1, '    THRESHOLD,\n')
                break
    else:
        # Find where to insert import (after other imports)
        insert_pos = 0
        in_docstring = False

        for i, line in enumerate(lines):
            stripped = line.strip()

            # Skip docstrings
            if stripped.startswith('"""') or stripped.startswith("'''"):
                in_docstring = not in_docstring
                continue

            if in_docstring:
                continue

            # Find last import statement
            if stripped.startswith('import ') or stripped.startswith('from '):
                insert_pos = i + 1

        # Insert import after last import
        if insert_pos > 0:
            lines.insert(insert_pos, 'from agentic_core.L0_routing.config.path_constants import THRESHOLD\n')
        else:
            # No imports found, add after docstring or at top
            lines.insert(0, 'from agentic_core.L0_routing.config.path_constants import THRESHOLD\n\n')

    return ''.join(lines)


def refactor_file(file_path: Path, dry_run: bool = True) -> dict:
    """Refactor a single file to use THRESHOLD constant."""
    try:
        source = file_path.read_text(encoding='utf-8')

        # Parse AST
        tree = ast.parse(source, filename=str(file_path))

        # Transform AST
        replacer = ThresholdReplacer()
        new_tree = replacer.visit(tree)

        if not replacer.modified:
            return {'status': 'skipped', 'reason': 'no_modifications_needed'}

        # Generate new source
        new_source = ast.unparse(new_tree)

        # Add import if needed
        if 'THRESHOLD' not in source or 'from agentic_core.L0_routing.config.path_constants import' not in source:
            new_source = add_threshold_import(new_source, file_path)

        if not dry_run:
            file_path.write_text(new_source, encoding='utf-8')

        return {
            'status': 'success',
            'file': str(file_path.relative_to(PROJECT_ROOT)),
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
    """Main refactoring execution."""
    import argparse

    parser = argparse.ArgumentParser(description='Refactor threshold=0.95 violations')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without writing')
    parser.add_argument('--limit', type=int, default=10, help='Max files to process')
    parser.add_argument('--execute', action='store_true', help='Actually write changes')

    args = parser.parse_args()

    project_root = get_validated_project_root()
    baseline_file = project_root / "ops_scripts" / "hooks" / "landmine_baseline.txt"

    # Load violations
    violations = []
    with open(baseline_file, encoding='utf-8') as f:
        for line in f:
            if 'threshold=0.95' in line:
                file_path = line.split(':')[0]
                violations.append(project_root / file_path)

    unique_files = sorted(set(violations))[:args.limit]

    print(f"[INFO] Processing {len(unique_files)} files (limit={args.limit})")
    print(f"[MODE] {'DRY RUN' if not args.execute else 'EXECUTE'}")
    print()

    results = []
    for file_path in unique_files:
        if not file_path.exists():
            continue

        result = refactor_file(file_path, dry_run=not args.execute)
        results.append(result)

        if result['status'] == 'success':
            print(f"✓ {result['file']}")
        elif result['status'] == 'error':
            print(f"✗ {result['file']}: {result['error']}")
        elif result['status'] == 'skipped':
            print(f"- {result.get('file', file_path.name)}: {result['reason']}")

    # Summary
    success = len([r for r in results if r['status'] == 'success'])
    errors = len([r for r in results if r['status'] == 'error'])
    skipped = len([r for r in results if r['status'] == 'skipped'])

    print()
    print("[SUMMARY]")
    print(f"  Success: {success}")
    print(f"  Errors: {errors}")
    print(f"  Skipped: {skipped}")

    if not args.execute and success > 0:
        print()
        print("[NEXT] Run with --execute to apply changes")

    return 0


if __name__ == '__main__':
    sys.exit(main())
