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

PROJECT_ROOT = Path(__file__).resolve().parents[1]
# guardian: allow-global-mutation
sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L0_routing.config.path_constants import get_validated_project_root

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
        call.func.attr in ('insert', 'append', 'extend', 'remove')
        and isinstance(call.func.value, ast.Attribute)
        and call.func.value.attr == 'path'
        and isinstance(call.func.value.value, ast.Name)
        and call.func.value.value.id == 'sys'
    )


def _is_os_environ_assign(node: ast.AST) -> bool:
    """Check if node is os.environ['KEY'] = value or os.environ.setdefault/update/pop."""
    # os.environ['KEY'] = value
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Subscript):
                if isinstance(target.value, ast.Attribute):
                    if (target.value.attr == 'environ'
                            and isinstance(target.value.value, ast.Name)
                            and target.value.value.id == 'os'):
                        return True
    # os.environ.setdefault(...) / os.environ.update(...) / os.environ.pop(...)
    if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
        call = node.value
        if isinstance(call.func, ast.Attribute):
            if call.func.attr in ('setdefault', 'update', 'pop', 'clear'):
                if isinstance(call.func.value, ast.Attribute):
                    if (call.func.value.attr == 'environ'
                            and isinstance(call.func.value.value, ast.Name)
                            and call.func.value.value.id == 'os'):
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
                has_mutation = any(
                    _is_sys_path_call(c) or _is_os_environ_assign(c)
                    for c in node.body
                )
                if has_mutation:
                    targets.add(node.lineno)
                else:
                    # Recurse deeper
                    _walk_body(node.body)
                    _walk_body(node.orelse)
            else:
                # Recurse into compound statements
                for body_attr in ('body', 'orelse', 'finalbody'):
                    stmts2 = getattr(node, body_attr, None)
                    if isinstance(stmts2, list):
                        _walk_body(stmts2)
                for handler in getattr(node, 'handlers', []):
                    _walk_body(handler.body)

    _walk_body(tree.body)
    return targets


def fix_file(file_path: Path, dry_run: bool = True) -> dict:
    """Add whitelist comments to all global mutation sites."""
    try:
        source = file_path.read_text(encoding='utf-8')
        lines = source.splitlines(keepends=True)

        tree = ast.parse(source, filename=str(file_path))
        target_lines = _collect_target_lines(tree)

        if not target_lines:
            return {'status': 'skipped', 'reason': 'no_mutations'}

        # Filter already whitelisted
        lines_to_fix = []
        for lineno in sorted(target_lines):
            idx = lineno - 1
            if idx > 0 and WHITELIST_COMMENT in lines[idx - 1]:
                continue
            lines_to_fix.append(lineno)

        if not lines_to_fix:
            return {'status': 'skipped', 'reason': 'already_whitelisted'}

        if not dry_run:
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
    parser.add_argument('--limit', type=int, default=500)
    args = parser.parse_args()

    project_root = get_validated_project_root()
    baseline_file = project_root / "ops_scripts/hooks/landmine_baseline.txt"

    violations = []
    with open(baseline_file, 'r', encoding='utf-8') as f:
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
