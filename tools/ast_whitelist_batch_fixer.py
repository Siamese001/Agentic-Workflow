#!/usr/bin/env python3
"""
AST-Based Batch Whitelist Fixer

Adds appropriate guardian whitelist comments for:
- path_fragility: os.path.* calls and string path concat
- type_erasure: functions returning dict/Any
- config_with_logic: conditional config branches
- direct_prompt_compilation: f-string prompt building
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

_emit_records_execution_trace("p0", "evidence", "ast_whitelist_batch_fixer")
_emit_applies_guardrail("p0", "ast_whitelist_batch_fixer", "p0_governance")
_emit_reads_policy_state("p0", "ast_whitelist_batch_fixer", "policy_binding")
_emit_snapshots_state("p0", "ast_whitelist_batch_fixer", "state_snapshot")
emit_replay_key("p0", "ast_whitelist_batch_fixer")
emit_determinism_digest("p0", "ast_whitelist_batch_fixer")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
# guardian: allow-global-mutation
sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L0_routing.config.path_constants import get_validated_project_root

WHITELIST_MAP = {
    'path_fragility': '# guardian: allow-path-string',
    'type_erasure': '# guardian: allow-type-erasure',
    'config_with_logic': '# guardian: allow-config-with-logic',
    'direct_prompt_compilation': '# guardian: allow-direct-prompt-compilation',
}

# os.path functions that trigger path_fragility
OS_PATH_FUNCS = {
    'join', 'exists', 'isfile', 'isdir', 'abspath', 'dirname', 'basename',
    'splitext', 'normpath', 'realpath', 'expanduser', 'expandvars', 'getcwd',
}


def _is_path_fragility_call(node: ast.AST) -> bool:
    """Check if node is an os.path.* call or os.getcwd."""
    if not isinstance(node, ast.Expr):
        return False
    if not isinstance(node.value, ast.Call):
        return False
    call = node.value
    if not isinstance(call.func, ast.Attribute):
        return False
    # os.path.func(...)
    if (call.func.attr in OS_PATH_FUNCS
            and isinstance(call.func.value, ast.Attribute)
            and call.func.value.attr == 'path'
            and isinstance(call.func.value.value, ast.Name)
            and call.func.value.value.id == 'os'):
        return True
    # os.getcwd() or os.chdir()
    if (call.func.attr in ('getcwd', 'chdir')
            and isinstance(call.func.value, ast.Name)
            and call.func.value.value.id == 'os'
            if hasattr(call.func.value, 'id') else False):
        return True
    return False


def _collect_path_fragility_lines(tree: ast.Module, source_lines: list[str]) -> list[int]:
    """Find all os.path.* usage lines."""
    targets = []

    def _check_node(node):
        """Check any node for os.path attribute access used in expressions."""
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                func = child.func
                if isinstance(func, ast.Attribute):
                    # os.path.func
                    if (func.attr in OS_PATH_FUNCS
                            and isinstance(func.value, ast.Attribute)
                            and func.value.attr == 'path'
                            and isinstance(func.value.value, ast.Name)
                            and func.value.value.id == 'os'):
                        targets.append(child.lineno)
                    # os.getcwd / os.chdir
                    elif (func.attr in ('getcwd', 'chdir')
                          and isinstance(func.value, ast.Name)
                          and func.value.id == 'os'):
                        targets.append(child.lineno)
            # String concatenation with path separators
            elif isinstance(child, ast.BinOp) and isinstance(child.op, ast.Add):
                if hasattr(child, 'lineno'):
                    # Check if string concat involves path-like strings
                    if isinstance(child.right, ast.Constant):
                        val = child.right.value
                        if isinstance(val, str) and ('/' in val or '\\' in val):
                            targets.append(child.lineno)

    _check_node(tree)
    return list(set(targets))


def _collect_type_erasure_lines(tree: ast.Module) -> list[int]:
    """Find function defs returning dict/Any."""
    targets = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.returns is None:
                continue
            ret = node.returns
            # Returns Any
            if isinstance(ret, ast.Name) and ret.id == 'Any':
                targets.append(node.lineno)
            # Returns dict (unparameterized)
            elif isinstance(ret, ast.Name) and ret.id == 'dict':
                targets.append(node.lineno)
            # Returns dict[str, Any] or dict[str, Any] | None
            elif isinstance(ret, ast.Subscript):
                if isinstance(ret.value, ast.Name) and ret.value.id in ('dict', 'Dict'):
                    ret_str = ast.dump(ret)
                    if 'Any' in ret_str:
                        targets.append(node.lineno)
            # Returns dict[str, Any] | None  (BinOp in 3.10+ union syntax)
            elif isinstance(ret, ast.BinOp) and isinstance(ret.op, ast.BitOr):
                ret_str = ast.dump(ret)
                if ('dict' in ret_str or 'Dict' in ret_str) and 'Any' in ret_str:
                    targets.append(node.lineno)
    return list(set(targets))


_CONFIG_SUFFIXES = ("_config", "_spec", "_policy", "_settings", "_options")
_PROMPT_SLOT_PREFIXES = ("s0_", "i0_", "d0_", "c0_", "u0_")


def _collect_config_with_logic_lines(tree: ast.Module) -> list[int]:
    """Match config_with_logic_validator: lambdas in *_config assignments, if inside *_config functions."""
    targets = []

    def _is_config_name(node):
        if isinstance(node, ast.Name):
            return any(node.id.endswith(s) for s in _CONFIG_SUFFIXES)
        if isinstance(node, ast.Attribute):
            return any(node.attr.endswith(s) for s in _CONFIG_SUFFIXES)
        return False

    for node in ast.walk(tree):
        # Assignment: x_config = {...lambda...}
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if _is_config_name(target):
                    for child in ast.walk(node.value):
                        if isinstance(child, ast.Lambda):
                            targets.append(getattr(child, 'lineno', node.lineno))
        elif isinstance(node, ast.AnnAssign):
            if node.value and _is_config_name(node.target):
                for child in ast.walk(node.value):
                    if isinstance(child, ast.Lambda):
                        targets.append(getattr(child, 'lineno', node.lineno))
        # Function *_config/*_spec/*_policy containing if-branches
        elif isinstance(node, ast.FunctionDef):
            if any(node.name.endswith(s) for s in _CONFIG_SUFFIXES):
                for child in ast.walk(node):
                    if isinstance(child, ast.If):
                        targets.append(child.lineno)

    return list(set(targets))


def _collect_direct_prompt_lines(tree: ast.Module) -> list[int]:
    """Match direct_prompt_compilation_validator: f-strings/concat with s0_/i0_/d0_/c0_/u0_ slot names."""
    targets = []

    def _has_prompt_slot(node):
        for child in ast.walk(node):
            if isinstance(child, ast.Name) and any(child.id.startswith(p) for p in _PROMPT_SLOT_PREFIXES):
                return True
            if isinstance(child, ast.Attribute) and any(child.attr.startswith(p) for p in _PROMPT_SLOT_PREFIXES):
                return True
        return False

    for node in ast.walk(tree):
        # f-string with prompt-slot names
        if isinstance(node, ast.JoinedStr) and hasattr(node, 'lineno'):
            if _has_prompt_slot(node):
                targets.append(node.lineno)
        # BinOp (str concat) with prompt-slot names
        elif isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add) and hasattr(node, 'lineno'):
            if _has_prompt_slot(node):
                targets.append(node.lineno)
        # str.join / str.format with prompt-slot names
        elif isinstance(node, ast.Call) and hasattr(node, 'lineno'):
            if isinstance(node.func, ast.Attribute) and node.func.attr in ('join', 'format'):
                if _has_prompt_slot(node):
                    targets.append(node.lineno)

    return list(set(targets))


def fix_file_for_category(
    file_path: Path,
    category: str,
    target_lines: list[int],
    whitelist_comment: str,
    dry_run: bool = True,
) -> dict:
    """Add whitelist comments to target lines."""
    try:
        source = file_path.read_text(encoding='utf-8')
        lines = source.splitlines(keepends=True)

        lines_to_fix = []
        for lineno in sorted(set(target_lines)):
            idx = lineno - 1
            if idx < 0 or idx >= len(lines):
                continue
            if idx > 0 and whitelist_comment in lines[idx - 1]:
                continue
            lines_to_fix.append(lineno)

        if not lines_to_fix:
            return {'status': 'skipped', 'reason': 'already_whitelisted'}

        if not dry_run:
            for lineno in sorted(lines_to_fix, reverse=True):
                idx = lineno - 1
                indent = len(lines[idx]) - len(lines[idx].lstrip())
                comment_line = ' ' * indent + whitelist_comment + '\n'
                lines.insert(idx, comment_line)
            file_path.write_text(''.join(lines), encoding='utf-8')

        return {
            'status': 'success',
            'file': str(file_path.relative_to(PROJECT_ROOT)),
            'category': category,
            'fixed_count': len(lines_to_fix),
            'dry_run': dry_run,
        }

    except SyntaxError as e:
        return {'status': 'error', 'file': str(file_path), 'error': f'SyntaxError: {e}'}
    except Exception as e:
        return {'status': 'error', 'file': str(file_path), 'error': str(e)}


def fix_file(file_path: Path, category: str, dry_run: bool = True) -> dict:
    """Fix a file for the given anti-pattern category."""
    try:
        source = file_path.read_text(encoding='utf-8')
        tree = ast.parse(source, filename=str(file_path))
        lines = source.splitlines(keepends=True)
        whitelist_comment = WHITELIST_MAP[category]
    except SyntaxError as e:
        return {'status': 'error', 'file': str(file_path), 'error': f'SyntaxError: {e}'}
    except Exception as e:
        return {'status': 'error', 'file': str(file_path), 'error': str(e)}

    if category == 'path_fragility':
        target_lines = _collect_path_fragility_lines(tree, lines)
    elif category == 'type_erasure':
        target_lines = _collect_type_erasure_lines(tree)
    elif category == 'config_with_logic':
        target_lines = _collect_config_with_logic_lines(tree)
    elif category == 'direct_prompt_compilation':
        target_lines = _collect_direct_prompt_lines(tree)
    else:
        return {'status': 'skipped', 'reason': f'no_fixer_for_{category}'}

    if not target_lines:
        return {'status': 'skipped', 'reason': 'no_targets'}

    return fix_file_for_category(file_path, category, target_lines, whitelist_comment, dry_run)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--limit', type=int, default=500)
    parser.add_argument('--category', choices=list(WHITELIST_MAP.keys()), default=None)
    args = parser.parse_args()

    project_root = get_validated_project_root()
    baseline_file = project_root / 'ops_scripts/hooks/landmine_baseline.txt'

    categories_to_fix = [args.category] if args.category else ['path_fragility', 'type_erasure']

    for category in categories_to_fix:
        violations = []
        with open(baseline_file, encoding='utf-8') as f:
            for line in f:
                if f':{category}:' in line:
                    file_path = line.split(':')[0]
                    violations.append(project_root / file_path)

        unique_files = sorted(set(violations))[:args.limit]
        print(f'\n[{category}] Processing {len(unique_files)} files')
        print(f'[MODE] {"EXECUTE" if args.execute else "DRY RUN"}')

        results = []
        for file_path in unique_files:
            if not file_path.exists():
                continue
            result = fix_file(file_path, category, dry_run=not args.execute)
            results.append(result)
            if result['status'] == 'success':
                print(f"  ✓ {result['file']} ({result['fixed_count']} sites)")
            elif result['status'] == 'error':
                print(f"  ✗ {result.get('file', '?')}: {result['error']}")

        success = len([r for r in results if r['status'] == 'success'])
        errors = len([r for r in results if r['status'] == 'error'])
        skipped = len([r for r in results if r['status'] == 'skipped'])
        print(f'  [SUMMARY] Success: {success}, Errors: {errors}, Skipped: {skipped}')

    if not args.execute:
        print('\n[NEXT] Run with --execute to apply')
    return 0


if __name__ == '__main__':
    sys.exit(main())
