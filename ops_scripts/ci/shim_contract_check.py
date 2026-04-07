"""CI Shim Contract Gate — AST-enforced invariants for all consolidation shims.

Fails CI if any shimmed file:
  1. Contains a ClassDef
  2. Exceeds 30 LOC (non-blank lines)
  3. Imports anything besides the canonical executor target
  4. Performs side effects at import time (calls, loops, conditionals)

Usage:
    python -m ops_scripts.ci.shim_contract_check
    python ops_scripts/ci/shim_contract_check.py

Exit codes:
    0 — all shims pass contract
    1 — one or more violations detected
"""
from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
_v3 = PROJECT_ROOT / 'artifacts' / 'consolidation' / 'target_manifest_v3.json'
_manifest = json.loads(_v3.read_text(encoding='utf-8'))
MERGE_FILES = [e['file_path'] for e in _manifest.get('entries', []) if e.get('action') == 'merge_to_executor']
VIOLATIONS: list[str] = []

def fail(msg: str) -> None:
    VIOLATIONS.append(msg)
    print(f'  FAIL: {msg}', file=sys.stderr)

def check_shim(rel_path: str) -> None:
    full = PROJECT_ROOT / rel_path
    if not full.exists():
        fail(f'{rel_path}: shim file missing from disk')
        return
    source = full.read_text(encoding='utf-8')
    loc = len([l for l in source.splitlines() if l.strip()])
    if loc > 30:
        fail(f'{rel_path}: {loc} LOC exceeds 30-line limit')
    try:
        tree = ast.parse(source)
    except SyntaxError as e:    # guardian: Syntax errors should be caught at parser level, not runtime
        fail(f'{rel_path}: SyntaxError — {e}')
        return
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef):
            fail(f"{rel_path}: contains ClassDef '{node.name}' (shim must not define classes)")
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            fail(f"{rel_path}: contains function '{node.name}' (shim must not define functions)")
        if isinstance(node, (ast.For, ast.While)):
            fail(f'{rel_path}: contains loop (shim must not have side effects)')
        if isinstance(node, ast.If):
            test = node.test
            is_name_guard = isinstance(test, ast.Compare) and isinstance(test.left, ast.Name) and (test.left.id == '__name__')
            if not is_name_guard:
                fail(f'{rel_path}: contains conditional logic (shim must not have side effects)')
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            fail(f'{rel_path}: contains import-time function call (shim must not have side effects)')
    imports_from = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            imports_from.append(node.module)
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports_from.append(alias.name)
    non_future = [m for m in imports_from if m not in ('__future__', 'typing')]
    if len(non_future) > 1:
        fail(f'{rel_path}: imports from {len(non_future)} non-future modules: {non_future} (expected exactly 1)')

def main() -> int:
    print(f'Shim Contract Gate: checking {len(MERGE_FILES)} merge shims')
    for rel_path in MERGE_FILES:
        check_shim(rel_path)
    if VIOLATIONS:
        print(f"\n{'=' * 60}", file=sys.stderr)
        print(f'SHIM CONTRACT GATE: FAILED — {len(VIOLATIONS)} violation(s)', file=sys.stderr)
        print(f"{'=' * 60}", file=sys.stderr)
        return 1
    print(f'\nShim Contract Gate: PASSED — {len(MERGE_FILES)} shims verified, 0 violations')
    return 0
if __name__ == '__main__':
    sys.exit(main())
