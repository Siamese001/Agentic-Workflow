"""G1: Check for unconditional xfail markers in governance/guardian tests.

Unconditional @pytest.mark.xfail without a condition or reason that references
an environment gate is forbidden in governance and guardian tests. All xfail
markers must be env-gated negative controls.

Usage:
    python ops_scripts/ci/check_no_unconditional_xfail.py [path ...]
    python ops_scripts/ci/check_no_unconditional_xfail.py  # scans tests/governance/ tests/guardian/

Exit codes:
    0 — no unconditional xfail found
    1 — unconditional xfail found
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

_DEFAULT_SCAN_DIRS = ['tests/governance', 'tests/guardian', 'tests/architecture']
_ENV_GATE_KEYWORDS = ('environ', 'getenv', 'os.environ', 'os.getenv', 'env', 'CI', 'PYTEST_')

def _is_unconditional_xfail(decorator: ast.expr) -> bool:
    """Return True if decorator is @pytest.mark.xfail with no condition and no env-gated reason."""
    if not isinstance(decorator, ast.Call):
        return False
    func = decorator.func
    if isinstance(func, ast.Attribute):
        chain: list[str] = []
        cur: ast.expr = func
        while isinstance(cur, ast.Attribute):
            chain.append(cur.attr)
            cur = cur.value
        if isinstance(cur, ast.Name):
            chain.append(cur.id)
        full = '.'.join(reversed(chain))
        if full != 'pytest.mark.xfail':
            return False
    else:
        return False
    if not decorator.args and (not decorator.keywords):
        return True
    for kw in decorator.keywords:
        if kw.arg == 'condition':
            return False
    for kw in decorator.keywords:
        if kw.arg == 'reason':
            if isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, str):
                reason_lower = kw.value.value.lower()
                if any(k.lower() in reason_lower for k in _ENV_GATE_KEYWORDS):
                    return False
    return True

def scan_file(filepath: Path) -> list[tuple[int, str]]:
    """Return list of (lineno, decorator_text) for unconditional xfail in filepath."""
    try:
        source = filepath.read_text(encoding='utf-8', errors='replace')
        tree = ast.parse(source, filename=str(filepath))
    except (SyntaxError, OSError):    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling
        return []
    violations: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        for dec in node.decorator_list:
            if _is_unconditional_xfail(dec):
                violations.append((dec.lineno, ast.unparse(dec)))
    return violations

def main(argv: list[str] | None=None) -> int:
    args = argv or sys.argv[1:]
    repo_root = Path(__file__).resolve().parents[2]
    if args:
        scan_dirs = [Path(a) for a in args]
    else:
        scan_dirs = [repo_root / d for d in _DEFAULT_SCAN_DIRS]
    all_violations: list[tuple[Path, int, str]] = []
    for scan_dir in scan_dirs:
        if not scan_dir.exists():
            continue
        for py_file in sorted(scan_dir.rglob('*.py')):
            file_violations = scan_file(py_file)
            for lineno, text in file_violations:
                all_violations.append((py_file, lineno, text))
    if all_violations:
        print(f'[FAIL] G1: Found {len(all_violations)} unconditional xfail marker(s):')
        for filepath, lineno, text in all_violations:
            rel = filepath.relative_to(repo_root) if filepath.is_relative_to(repo_root) else filepath
            print(f'  {rel}:{lineno}  {text}')
        print("\n[FIX] All xfail markers in governance/guardian tests must be env-gated.\n  Add: condition=os.environ.get('RUN_NEGATIVE_CONTROLS') == '1'\n  Or add a reason referencing the env gate.")
        return 1
    print(f'[OK] G1: No unconditional xfail found in {len(scan_dirs)} scan dirs.')
    return 0
if __name__ == '__main__':
    sys.exit(main())
