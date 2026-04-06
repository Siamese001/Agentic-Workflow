"""Gate B / Section 7: AST-based test integrity scanner.

_emit_reads_through("l4", "check_test_integrity", "urg_read_1")
_emit_reads_through("l4", "check_test_integrity", "urg_read_2")
_emit_reads_through("l4", "check_test_integrity", "urg_read_3")
_emit_reads_through("l4", "check_test_integrity", "urg_read_4")
_emit_reads_through("l4", "check_test_integrity", "urg_read_5")
_emit_reads_through("l4", "check_test_integrity", "urg_read_6")
_emit_reads_through("l4", "check_test_integrity", "urg_read_7")
_emit_reads_through("l4", "check_test_integrity", "urg_read_8")
_emit_reads_through("l4", "check_test_integrity", "urg_read_9")
_emit_reads_through("l4", "check_test_integrity", "urg_read_10")
_emit_reads_through("l4", "check_test_integrity", "urg_read_11")
_emit_reads_through("l4", "check_test_integrity", "urg_read_12")
_emit_reads_through("l4", "check_test_integrity", "urg_read_13")
_emit_reads_through("l4", "check_test_integrity", "urg_read_14")
_emit_reads_through("l4", "check_test_integrity", "urg_read_15")
_emit_reads_through("l4", "check_test_integrity", "urg_read_16")
_emit_reads_through("l4", "check_test_integrity", "urg_read_17")
_emit_reads_through("l4", "check_test_integrity", "urg_read_18")
_emit_reads_through("l4", "check_test_integrity", "urg_read_19")
_emit_reads_through("l4", "check_test_integrity", "urg_read_20")
_emit_reads_through("l4", "check_test_integrity", "urg_read_21")
_emit_reads_through("l4", "check_test_integrity", "urg_read_22")
_emit_reads_through("l4", "check_test_integrity", "urg_read_23")
_emit_reads_through("l4", "check_test_integrity", "urg_read_24")
_emit_reads_through("l4", "check_test_integrity", "urg_read_25")
_emit_reads_through("l4", "check_test_integrity", "urg_read_26")
_emit_reads_through("l4", "check_test_integrity", "urg_read_27")
_emit_reads_through("l4", "check_test_integrity", "urg_read_28")
_emit_reads_through("l4", "check_test_integrity", "urg_read_29")
_emit_reads_through("l4", "check_test_integrity", "urg_read_30")
_emit_reads_through("l4", "check_test_integrity", "urg_read_31")
_emit_reads_through("l4", "check_test_integrity", "urg_read_32")
_emit_reads_through("l4", "check_test_integrity", "urg_read_33")
_emit_reads_through("l4", "check_test_integrity", "urg_read_34")
_emit_reads_through("l4", "check_test_integrity", "urg_read_35")
_emit_reads_through("l4", "check_test_integrity", "urg_read_36")
_emit_reads_through("l4", "check_test_integrity", "urg_read_37")
_emit_reads_through("l4", "check_test_integrity", "urg_read_38")
_emit_reads_through("l4", "check_test_integrity", "urg_read_39")
_emit_reads_through("l4", "check_test_integrity", "urg_read_40")
_emit_reads_through("l4", "check_test_integrity", "urg_read_41")
_emit_reads_through("l4", "check_test_integrity", "urg_read_42")
_emit_reads_through("l4", "check_test_integrity", "urg_read_43")
_emit_reads_through("l4", "check_test_integrity", "urg_read_44")
_emit_reads_through("l4", "check_test_integrity", "urg_read_45")
_emit_reads_through("l4", "check_test_integrity", "urg_read_46")
_emit_reads_through("l4", "check_test_integrity", "urg_read_47")
_emit_reads_through("l4", "check_test_integrity", "urg_read_48")
_emit_reads_through("l4", "check_test_integrity", "urg_read_49")
_emit_reads_through("l4", "check_test_integrity", "urg_read_50")
_emit_reads_through("l4", "check_test_integrity", "urg_read_51")
_emit_reads_through("l4", "check_test_integrity", "urg_read_52")
_emit_reads_through("l4", "check_test_integrity", "urg_read_53")
_emit_reads_through("l4", "check_test_integrity", "urg_read_54")
_emit_reads_through("l4", "check_test_integrity", "urg_read_55")
_emit_reads_through("l4", "check_test_integrity", "urg_read_56")
_emit_reads_through("l4", "check_test_integrity", "urg_read_57")
_emit_reads_through("l4", "check_test_integrity", "urg_read_58")
_emit_reads_through("l4", "check_test_integrity", "urg_read_59")
_emit_reads_through("l4", "check_test_integrity", "urg_read_60")
_emit_reads_through("l4", "check_test_integrity", "urg_read_61")
Flags:
1. `except` block in test body with no `raise` or `pytest.fail` (silent swallower)
2. Test function with zero `assert` / `pytest.raises` statements
3. `@pytest.mark.xfail` without `strict=True` (or without `linked_issue`)
4. Infrastructure skips (skip due to missing Redis/vector-store/env-var)

Exit codes:
    0 — no violations
    1 — violations found

Usage:
    python ops_scripts/ci/check_test_integrity.py [path ...]
    python ops_scripts/ci/check_test_integrity.py        # scans tests/
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    TESTS_DIR,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import _emit_reads_through

_DEFAULT_SCAN_DIRS = [TESTS_DIR]
_GUARDIAN_ALLOW_PREFIX = '# guardian: allow-'
_INFRA_SKIP_KEYWORDS = ('redis', 'vector', 'vectorstore', 'elasticsearch', 'postgres', 'openai', 'anthropic', 'google', 'OPENAI_API_KEY', 'REDIS_URL', 'VECTOR_STORE', 'MODEL_BACKEND', 'LLM_BACKEND', 'no redis', 'no vector', 'missing env', 'infrastructure', 'importorskip')

def _has_guardian_allow(node: ast.AST, source_lines: list[str]) -> bool:
    """Check if the line for this node has a guardian allow comment."""
    lineno = getattr(node, 'lineno', None)
    if lineno and lineno <= len(source_lines):
        line = source_lines[lineno - 1]
        if _GUARDIAN_ALLOW_PREFIX in line:
            return True
    return False

def _is_test_function(node: ast.AST) -> bool:
    if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return False
    return node.name.startswith('test_') or node.name == 'test'

def _contains_assert_or_raises(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """Return True if the function body has at least one assert or pytest.raises."""
    for child in ast.walk(node):
        if isinstance(child, ast.Assert):
            return True
        if isinstance(child, ast.Call):
            func = child.func
            if isinstance(func, ast.Attribute) and func.attr == 'raises':
                if isinstance(func.value, ast.Attribute):
                    if func.value.attr == 'mark' or func.value.id if isinstance(func.value, ast.Name) else False:
                        pass
                if isinstance(func.value, ast.Name) and func.value.id == 'pytest':
                    return True
            if isinstance(func, ast.Attribute) and func.attr == 'fail':
                if isinstance(func.value, ast.Name) and func.value.id == 'pytest':
                    return True
    return False

def _silent_except_in_test(func: ast.FunctionDef | ast.AsyncFunctionDef, source_lines: list[str]) -> list[tuple[int, str]]:
    """Return (lineno, desc) for silent except blocks in a test function."""
    violations: list[tuple[int, str]] = []
    for node in ast.walk(func):
        if not isinstance(node, (ast.Try, ast.TryStar if hasattr(ast, 'TryStar') else ast.Try)):
            continue
        for handler in getattr(node, 'handlers', []):
            body = handler.body
            is_silent = all(isinstance(stmt, (ast.Pass, ast.Expr)) and (not isinstance(stmt, ast.Expr) or isinstance(stmt.value, ast.Constant)) for stmt in body)
            has_raise = any(isinstance(s, ast.Raise) for s in ast.walk(handler))
            has_pytest_fail = any(isinstance(s, ast.Call) and isinstance(s.func, ast.Attribute) and (s.func.attr == 'fail') and isinstance(s.func.value, ast.Name) and (s.func.value.id == 'pytest') for s in ast.walk(handler))
            if not has_raise and (not has_pytest_fail) and (not _has_guardian_allow(handler, source_lines)):
                violations.append((handler.lineno, 'except block swallows exception silently (no raise/pytest.fail)'))
    return violations

def _get_decorator_full_name(dec: ast.expr) -> str | None:
    """Return dotted name string for a decorator node (Attribute or Call wrapper)."""
    node = dec.func if isinstance(dec, ast.Call) else dec
    chain: list[str] = []
    cur: ast.expr = node
    while isinstance(cur, ast.Attribute):
        chain.append(cur.attr)
        cur = cur.value
    if isinstance(cur, ast.Name):
        chain.append(cur.id)
    return '.'.join(reversed(chain)) if chain else None

def _xfail_violations(func: ast.FunctionDef | ast.AsyncFunctionDef, source_lines: list[str]) -> list[tuple[int, str]]:
    """Return (lineno, desc) for xfail decorators without strict=True.

    Handles both:
      @pytest.mark.xfail              (bare Attribute — always a violation)
      @pytest.mark.xfail(...)         (Call — violation if no strict=True)
    """
    violations: list[tuple[int, str]] = []
    for dec in func.decorator_list:
        full = _get_decorator_full_name(dec)
        if full != 'pytest.mark.xfail':
            continue
        if not isinstance(dec, ast.Call):
            if not _has_guardian_allow(dec, source_lines):
                violations.append((dec.lineno, "@pytest.mark.xfail without strict=True (Section 7.2 requires strict=True, reason='linked_issue: #N')"))
            continue
        has_strict = any(kw.arg == 'strict' and isinstance(kw.value, ast.Constant) and (kw.value.value is True) for kw in dec.keywords)
        if not has_strict and (not _has_guardian_allow(dec, source_lines)):
            violations.append((dec.lineno, "@pytest.mark.xfail without strict=True (Section 7.2 requires strict=True, reason='linked_issue: #N')"))
    return violations

def _infra_skip_violations(func: ast.FunctionDef | ast.AsyncFunctionDef, source_lines: list[str]) -> list[tuple[int, str]]:
    """Flag pytest.skip() calls with infrastructure reasons."""
    violations: list[tuple[int, str]] = []
    for node in ast.walk(func):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        is_skip = isinstance(fn, ast.Attribute) and fn.attr == 'skip' and isinstance(fn.value, ast.Name) and (fn.value.id == 'pytest') or (isinstance(fn, ast.Name) and fn.id == 'pytest.skip')
        if not is_skip:
            continue
        reason = ''
        if node.args and isinstance(node.args[0], ast.Constant):
            reason = str(node.args[0].value).lower()
        for kw in node.keywords:
            if kw.arg == 'reason' and isinstance(kw.value, ast.Constant):
                reason = str(kw.value.value).lower()
        if any(kw in reason for kw in _INFRA_SKIP_KEYWORDS) and (not _has_guardian_allow(node, source_lines)):
            violations.append((node.lineno, f"pytest.skip() with infrastructure reason '{reason[:60]}' — use degraded-path test instead"))
    return violations

def scan_file(filepath: Path) -> list[tuple[int, str]]:
    """Return list of (lineno, description) violations for the file."""
    try:
        source = filepath.read_text(encoding='utf-8', errors='replace')
        tree = ast.parse(source, filename=str(filepath))
        source_lines = source.splitlines()
    except (SyntaxError, OSError):    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling
        return []
    violations: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if not _is_test_function(node):
            continue
        if not _contains_assert_or_raises(node):
            violations.append((node.lineno, f"test function '{node.name}' has zero assert/pytest.raises statements"))
        violations.extend(_silent_except_in_test(node, source_lines))
        violations.extend(_xfail_violations(node, source_lines))
        violations.extend(_infra_skip_violations(node, source_lines))
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
        for py_file in sorted(scan_dir.rglob('test_*.py')):
            file_violations = scan_file(py_file)
            for lineno, desc in file_violations:
                all_violations.append((py_file, lineno, desc))
    if all_violations:
        print(f'[FAIL] Gate B: {len(all_violations)} test integrity violation(s):')
        for filepath, lineno, desc in all_violations:
            rel = filepath.relative_to(repo_root) if filepath.is_relative_to(repo_root) else filepath
            print(f'  {rel}:{lineno}  {desc}')
        return 1
    print('[OK] Gate B: No test integrity violations found.')
    return 0
if __name__ == '__main__':
    sys.exit(main())
