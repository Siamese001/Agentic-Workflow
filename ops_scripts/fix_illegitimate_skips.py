"""Automated fixer: convert all illegitimate pytest.skip() / importorskip to
pytest.fail() or delete dead stubs, as classified by classify_skips.py.

Strategy:
  - pytest.skip(msg) → pytest.fail(msg)  for all illegitimate sites
  - pytest.importorskip(pkg) for mandatory deps → raise ImportError assertion
  - "not yet implemented" stubs → comment body with pytest.fail()
  - Legitimate sites (Redis, Playwright, tamper env flag, platform, faiss-gpu)
    are left untouched.

Run from repo root:
    python ops_scripts/fix_illegitimate_skips.py
"""
import ast
import re
from pathlib import Path
from agentic_core.L0_routing.config.path_constants import TESTS_DIR, get_validated_project_root
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
ROOT = get_validated_project_root()
TESTS = ROOT / TESTS_DIR
LEGITIMATE_REASONS_SUBSTRINGS = ['redis not running', 'redis not', 'playwright not installed', 'playwright visual tests should be run separately', 'ssot_orch_negctrl_tamper', 'activate tamper', 'read-only directory', 'faiss-gpu']
NOT_IMPLEMENTED_SUBSTRINGS = ['not yet implemented', 'method not implemented yet']

def is_legitimate(reason: str) -> bool:
    r = reason.lower()
    return any((k in r for k in LEGITIMATE_REASONS_SUBSTRINGS))

def is_not_implemented(reason: str) -> bool:
    r = reason.lower()
    return any((k in r for k in NOT_IMPLEMENTED_SUBSTRINGS))

def fix_file(path: Path) -> tuple[bool, int]:
    """Return (changed, num_fixes) for a single file."""
    original = path.read_text(encoding='utf-8', errors='replace')
    lines = original.splitlines(keepends=True)
    try:
        tree = ast.parse(original)
    except SyntaxError:
        return (False, 0)
    illegit_lines: dict[int, tuple[str, str]] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Attribute) and func.attr == 'importorskip':
            rawargs = [ast.unparse(a) for a in node.args]
            reason = rawargs[0].strip('"\'') if rawargs else 'missing import'
            illegit_lines[node.lineno] = ('importorskip', reason)
        elif isinstance(func, ast.Attribute) and func.attr == 'skip' and isinstance(func.value, ast.Name) and (func.value.id == 'pytest'):
            rawargs = [ast.unparse(a) for a in node.args]
            reason = rawargs[0].strip('"\'') if rawargs else ''
            if not is_legitimate(reason):
                kind = 'not_implemented' if is_not_implemented(reason) else 'skip'
                illegit_lines[node.lineno] = (kind, reason)
    if not illegit_lines:
        return (False, 0)
    changed = False
    fixes = 0
    new_lines = list(lines)
    for lineno, (kind, reason) in sorted(illegit_lines.items()):
        idx = lineno - 1
        line = new_lines[idx]
        if kind == 'importorskip':
            m = re.search('importorskip\\s*\\(\\s*["\\\']([^"\\\']+)["\\\']', line)
            if m:
                pkg = m.group(1)
                indent = len(line) - len(line.lstrip())
                ind = ' ' * indent
                new_lines[idx] = f'{ind}try:\n{ind}    import {pkg}  # noqa: F401\n{ind}except ImportError:\n{ind}    pytest.fail("{pkg} is a mandatory dependency — install it")\n'
                changed = True
                fixes += 1
            continue
        if kind == 'not_implemented':
            new_line = line.replace('pytest.skip(', 'pytest.fail(', 1)
            if new_line != line:
                new_lines[idx] = new_line
                changed = True
                fixes += 1
            continue
        new_line = line.replace('pytest.skip(', 'pytest.fail(', 1)
        if new_line != line:
            new_lines[idx] = new_line
            changed = True
            fixes += 1
    if changed:
        path.write_text(''.join(new_lines), encoding='utf-8')
    return (changed, fixes)

def main() -> None:
    total_files = 0
    total_fixes = 0
    for path in sorted(TESTS.rglob('test_*.py')):
        changed, fixes = fix_file(path)
        if changed:
            rel = path.relative_to(ROOT)
            print(f'  FIXED {fixes:3d} site(s)  {rel}')
            total_files += 1
            total_fixes += fixes
    print(f'\nDONE: {total_fixes} fixes across {total_files} files')
if __name__ == '__main__':
    main()
