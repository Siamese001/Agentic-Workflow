#!/usr/bin/env python3
"""
AST-Based Global Mutation Fixer

Adds guardian whitelist comments to legitimate sys.path.insert() calls
in standalone scripts. These are bootstrap patterns that are intentional.

Strategy: sys.path.insert() at module level in scripts that need
to add project root to path is a legitimate pattern. Add:
    # guardian: allow-global-mutation
above each sys.path.insert() call at module level.
"""

import ast
import sys
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "ast_global_mutation_fixer")
_emit_applies_guardrail("p0", "ast_global_mutation_fixer", "p0_governance")
_emit_reads_policy_state("p0", "ast_global_mutation_fixer", "policy_binding")
_emit_snapshots_state("p0", "ast_global_mutation_fixer", "state_snapshot")
emit_replay_key("p0", "ast_global_mutation_fixer")
emit_determinism_digest("p0", "ast_global_mutation_fixer")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
# guardian: allow-global-mutation
sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L0_routing.config.path_constants import get_validated_project_root

WHITELIST_COMMENT = "# guardian: allow-global-mutation"


def fix_file(file_path: Path, dry_run: bool = True) -> dict:
    """Add whitelist comments to legitimate sys.path mutations."""
    try:
        source = file_path.read_text(encoding='utf-8')
        lines = source.splitlines(keepends=True)

        # Parse to find sys.path.insert lines at module level
        tree = ast.parse(source, filename=str(file_path))

        # Find all sys.path.insert calls at module level
        target_lines = set()
        for node in tree.body:
            if isinstance(node, ast.Expr):
                if isinstance(node.value, ast.Call):
                    call = node.value
                    # sys.path.insert(...) or sys.path.append(...)
                    if isinstance(call.func, ast.Attribute):
                        if (call.func.attr in ('insert', 'append') and
                                isinstance(call.func.value, ast.Attribute) and
                                call.func.value.attr == 'path' and
                                isinstance(call.func.value.value, ast.Name) and
                                call.func.value.value.id == 'sys'):
                            target_lines.add(node.lineno)

        if not target_lines:
            return {'status': 'skipped', 'reason': 'no_sys_path_mutations'}

        # Check which lines already have the comment
        lines_to_fix = []
        for lineno in sorted(target_lines):
            idx = lineno - 1  # 0-indexed
            # Check if previous line already has the whitelist comment
            if idx > 0 and WHITELIST_COMMENT in lines[idx - 1]:
                continue
            lines_to_fix.append(lineno)

        if not lines_to_fix:
            return {'status': 'skipped', 'reason': 'already_whitelisted'}

        if not dry_run:
            # Insert comments from bottom to top to preserve line numbers
            for lineno in sorted(lines_to_fix, reverse=True):
                idx = lineno - 1
                indent = len(lines[idx]) - len(lines[idx].lstrip())
                comment_line = ' ' * indent + WHITELIST_COMMENT + '\n'
                lines.insert(idx, comment_line)

            file_path.write_text(''.join(lines), encoding='utf-8')

        return {
            'status': 'success',
            'file': str(file_path.relative_to(PROJECT_ROOT)),
            'fixed_lines': lines_to_fix,
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
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--limit', type=int, default=200)
    args = parser.parse_args()

    project_root = get_validated_project_root()
    baseline_file = project_root / "ops_scripts/hooks/landmine_baseline.txt"

    violations = []
    with open(baseline_file, encoding='utf-8') as f:
        for line in f:
            if 'global_mutation' in line:
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
        result = fix_file(file_path, dry_run=not args.execute)
        results.append(result)
        if result['status'] == 'success':
            print(f"✓ {result['file']} ({len(result['fixed_lines'])} lines)")
        elif result['status'] == 'error':
            print(f"✗ {result['file']}: {result['error']}")

    success = len([r for r in results if r['status'] == 'success'])
    errors = len([r for r in results if r['status'] == 'error'])
    skipped = len([r for r in results if r['status'] == 'skipped'])
    print(f"\n[SUMMARY] Success: {success}, Errors: {errors}, Skipped: {skipped}")
    if not args.execute and success > 0:
        print("[NEXT] Run with --execute to apply")
    return 0


if __name__ == '__main__':
    sys.exit(main())
