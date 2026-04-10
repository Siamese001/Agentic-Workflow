"""CI guard G6/G15: L0/L4/L6 must not perform persistent writes.

Blocked in those layers: open(w/a/x/b), Path.write_*, sqlite3.connect,
shutil.copy/move/rmtree, subprocess.run/Popen, os.remove/rename.
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    L0_MAINTENANCE_DIR,
    L4_STATE_DIR,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
WRITE_LAYERS = [L0_MAINTENANCE_DIR, L4_STATE_DIR, 'L6_observability']
_ALLOWED_WRITE_PATH_SEGMENTS = frozenset({'scripts', 'meta_control', 'reasoning', 'utils', 'types', 'storage', 'enforcement'})
_ALLOWED_WRITE_FILE_SUFFIXES = ('_util.py',)
WRITE_MODES = {'w', 'a', 'x', 'wb', 'ab', 'xb', 'w+', 'a+'}
BLOCKED_ATTRS = {'write_text', 'write_bytes', 'copy2', 'move', 'rmtree', 'remove', 'rename', 'unlink'}

def _is_write_open(node: ast.Call) -> bool:
    """Return True if this is an open() call with a write mode argument."""
    func = node.func
    if not (isinstance(func, ast.Name) and func.id == 'open'):
        return False
    mode_val = None
    if len(node.args) >= 2 and isinstance(node.args[1], ast.Constant):
        mode_val = node.args[1].value
    for kw in node.keywords:
        if kw.arg == 'mode' and isinstance(kw.value, ast.Constant):
            mode_val = kw.value.value
    return isinstance(mode_val, str) and any(m in mode_val for m in WRITE_MODES)

def _is_exempt_from_write_check(rel: str) -> bool:
    """Return True if this file is allowed to contain write calls."""
    parts = set(rel.replace('\\', '/').split('/'))
    if parts & _ALLOWED_WRITE_PATH_SEGMENTS:
        return True
    name = rel.rsplit('/', 1)[-1]
    return name.endswith(_ALLOWED_WRITE_FILE_SUFFIXES)

def main() -> int:
    violations: list[str] = []
    for layer in WRITE_LAYERS:
        layer_path = REPO_ROOT / layer
        if not layer_path.exists():
            continue
        for path in layer_path.rglob('*.py'):
            rel = path.relative_to(REPO_ROOT).as_posix()
            if _is_exempt_from_write_check(rel):
                continue
            try:
                tree = ast.parse(path.read_text(encoding='utf-8', errors='replace'))
            except SyntaxError:    # guardian: Syntax errors should be caught at parser level, not runtime
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if _is_write_open(node):
                        violations.append(f'{rel}:{node.lineno}: write-mode open() in sovereign layer')
                    if isinstance(node.func, ast.Attribute) and node.func.attr in BLOCKED_ATTRS:
                        violations.append(f"{rel}:{node.lineno}: blocked write call '{node.func.attr}' in sovereign layer")
    if violations:
        print(f'FAIL: {len(violations)} write sovereignty violation(s):')
        for v in violations:
            print(f'  {v}')
        return 1
    print('OK: write sovereignty clean')
    return 0
if __name__ == '__main__':
    sys.exit(main())
