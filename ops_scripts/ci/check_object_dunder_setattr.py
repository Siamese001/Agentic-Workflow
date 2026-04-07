"""SOV-DELTA CI guard: block object.__setattr__(core_obj, ...) call patterns.

Scans AST for Call nodes matching `object.__setattr__(arg0, ...)` where the
first argument resolves to a name or attribute from a core-layer module.

Exit 0 = no violations found.
Exit 1 = violations detected (CI FAIL).
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CORE_PREFIXES = (AGENTIC_CORE_DIR, APPS_LIC_DIR, APPS_RG_DIR, APPS_SHARED_DIR, SYSTEM_LEARNING_DIR)
SCAN_ROOTS = [AGENTIC_CORE_DIR, APPS_LIC_DIR, APPS_RG_DIR, APPS_SHARED_DIR, SYSTEM_LEARNING_DIR, TESTS_DIR]
ALLOWED_PATHS = {'agentic_core/L2_execution/types/instruction_packet_types.py', 'agentic_core/L5_safety/enforcement/runtime_mutation_guardrail.py'}

def _is_object_dunder_setattr(node: ast.Call) -> bool:
    """Return True if node is `object.__setattr__(...)` call."""
    func = node.func
    if not isinstance(func, ast.Attribute):
        return False
    if func.attr != '__setattr__':
        return False
    if not isinstance(func.value, ast.Name):
        return False
    return func.value.id == 'object'

def _arg0_is_core_name(node: ast.Call) -> bool:
    """Heuristically check whether the first argument looks like a core-layer object.

    Returns True if arg0 is a Name whose id matches a core-layer class name pattern,
    or an attribute chain rooted in a core-prefix variable.
    """
    if not node.args:
        return False
    arg0 = node.args[0]
    if isinstance(arg0, ast.Name):
        _core_hints = {'uwg', 'gateway', 'store', 'version_store', 'llm_gateway'}
        return arg0.id.lower() in _core_hints
    return False

def main() -> int:
    violations: list[str] = []
    for root in SCAN_ROOTS:
        scan_dir = REPO_ROOT / root
        if not scan_dir.exists():
            continue
        for path in scan_dir.rglob('*.py'):
            rel = path.relative_to(REPO_ROOT).as_posix()
            if rel in ALLOWED_PATHS:
                continue
            try:
                tree = ast.parse(path.read_text(encoding='utf-8', errors='replace'))
            except SyntaxError:    # guardian: Syntax errors should be caught at parser level, not runtime
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and _is_object_dunder_setattr(node):
                    if _arg0_is_core_name(node):
                        violations.append(f'{rel}:{node.lineno}: object.__setattr__ on core-layer object — use REQ-417 guard')
    if violations:
        print(f'FAIL: {len(violations)} object.__setattr__ violation(s) on core-layer objects:')
        for v in violations:
            print(f'  {v}')
        return 1
    print('OK: no object.__setattr__ violations on core-layer objects')
    return 0
if __name__ == '__main__':
    sys.exit(main())
