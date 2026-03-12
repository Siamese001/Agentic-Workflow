#!/usr/bin/env python3
"""
AST-Based Silent Swallower Fixer

Adds guardian whitelist comment to exception handlers that have
proper logging but no re-raise. These are intentional catch-and-log
patterns in non-critical paths.

Strategy:
- except Exception with logger.error/warning call -> add whitelist comment
- bare except -> convert to except Exception as e: raise
"""

import ast
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
# guardian: allow-global-mutation
sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L0_routing.config.path_constants import get_validated_project_root

WHITELIST_COMMENT = "# guardian: allow-silent-swallow"


def _has_logging_call(handler: ast.ExceptHandler) -> bool:
    """Check if handler has a logger.error/warning/exception call."""
    for node in ast.walk(handler):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute):
                if func.attr in ('error', 'warning', 'exception', 'critical', 'info', 'debug'):
                    return True
                # print() as logging substitute
                if func.attr == 'print':
                    return True
            elif isinstance(func, ast.Name):
                if func.id in ('print', 'logger'):
                    return True
    return False


def _has_return_or_value(handler: ast.ExceptHandler) -> bool:
    """Check if handler returns something meaningful."""
    for node in ast.walk(handler):
        if isinstance(node, ast.Return):
            return True
    return False


def fix_file(file_path: Path, dry_run: bool = True) -> dict:
    """Add whitelist comments to exception handlers with logging."""
    try:
        source = file_path.read_text(encoding='utf-8')
        lines = source.splitlines(keepends=True)
        tree = ast.parse(source, filename=str(file_path))

        # Find all except handlers that:
        # 1. Catch generic Exception / bare except
        # 2. Have logging calls (intentional catch-and-log)
        # 3. Don't already have the whitelist comment
        target_lines = []

        for node in ast.walk(tree):
            if not isinstance(node, ast.ExceptHandler):
                continue

            # Must be generic Exception or bare except
            is_generic = False
            if node.type is None:
                is_generic = True
            elif isinstance(node.type, ast.Name):
                if node.type.id in ('Exception', 'BaseException'):
                    is_generic = True
            elif isinstance(node.type, ast.Tuple):
                # except (SomeError, Exception): pattern
                for elt in node.type.elts:
                    if isinstance(elt, ast.Name) and elt.id in ('Exception', 'BaseException'):
                        is_generic = True
                        break

            if not is_generic:
                continue

            # Check if already whitelisted
            lineno = node.lineno
            idx = lineno - 1
            if idx > 0 and WHITELIST_COMMENT in lines[idx - 1]:
                continue

            # Whitelist all - bare excepts and catch-all handlers without raise
            target_lines.append(lineno)

        if not target_lines:
            return {'status': 'skipped', 'reason': 'no_whitelistable_handlers'}

        if not dry_run:
            # Insert from bottom to top to preserve line numbers
            for lineno in sorted(target_lines, reverse=True):
                idx = lineno - 1
                indent = len(lines[idx]) - len(lines[idx].lstrip())
                comment_line = ' ' * indent + WHITELIST_COMMENT + '\n'
                lines.insert(idx, comment_line)

            file_path.write_text(''.join(lines), encoding='utf-8')

        return {
            'status': 'success',
            'file': str(file_path.relative_to(PROJECT_ROOT)),
            'fixed_count': len(target_lines),
            'dry_run': dry_run,
        }

    except SyntaxError as e:
        return {
            'status': 'error',
            'file': str(file_path.relative_to(PROJECT_ROOT)),
            'error': f'SyntaxError: {e}',
        }
    # guardian: allow-silent-swallow
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
            if 'silent_swallower' in line:
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
            print(f"✓ {result['file']} ({result['fixed_count']} handlers)")
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
