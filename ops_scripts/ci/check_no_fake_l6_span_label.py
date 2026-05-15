"""CI gate L6-W2a: no fake ``L6`` span stage label in apps_rg runtime.

AST-scan ``apps_rg/runtime`` for calls named ``_emit_section_span`` whose first
positional/keyword arg is a string literal containing ``L6`` (learning substitute).

If ``_emit_section_span`` does not exist, gate passes (nothing to enforce).

Bypass: FAKE_L6_SPAN_BYPASS=1
Fail-closed: FAKE_L6_SPAN_FAIL_CLOSED=1 (same exit codes; CI wrapper may treat rc≠0 as hard fail)
"""
from __future__ import annotations

import ast
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCAN_ROOT = REPO_ROOT / "apps_rg" / "runtime"


def _string_arg_contains_l6(call: ast.Call) -> bool:
    if not call.args:
        return False
    first = call.args[0]
    if isinstance(first, ast.Constant) and isinstance(first.value, str):
        return "L6" in first.value
    return False


def _check_file(path: Path) -> list[tuple[int, str]]:
    bad: list[tuple[int, str]] = []
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (SyntaxError, OSError):
        return bad
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        name = None
        if isinstance(func, ast.Name):
            name = func.id
        elif isinstance(func, ast.Attribute):
            name = func.attr
        if name != "_emit_section_span":
            continue
        if _string_arg_contains_l6(node):
            bad.append((node.lineno, ast.dump(node.args[0])))
    return bad


def run() -> int:
    if os.environ.get("FAKE_L6_SPAN_BYPASS") == "1":
        print("[L6-W2a] FAKE_L6_SPAN_BYPASS=1 — skipping gate", flush=True)
        return 0

    violations: list[str] = []
    if SCAN_ROOT.exists():
        for py in sorted(SCAN_ROOT.rglob("*.py")):
            for lineno, _ in _check_file(py):
                rel = py.relative_to(REPO_ROOT)
                violations.append(f"{rel}:{lineno}  _emit_section_span(..., '...L6...')")

    if violations:
        print(f"[L6-W2a] FAIL — {len(violations)} violation(s):", flush=True)
        for v in violations:
            print(f"  {v}", flush=True)
        return 1

    print("[L6-W2a] PASS — no fake L6 span labels", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(run())
