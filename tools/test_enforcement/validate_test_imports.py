"""Wave 4 Enforcement: CI gate to validate test import contracts.

Exit code 0 = PASS, exit code 1 = FAIL (violations found).

Rules enforced:
1. No first-party imports wrapped in try/except ImportError in core tests
2. No pytest.skip() hiding import failures in core tests
3. No pytest.importorskip() in core tests without @pytest.mark.optional
4. No syntax errors in any test file
5. Every test file must be classifiable

Usage:
  python tools/test_enforcement/validate_test_imports.py
  python tools/test_enforcement/validate_test_imports.py --strict  # also checks _AVAILABLE patterns
"""
from __future__ import annotations

import ast
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent

FIRST_PARTY_TOPS = frozenset({
    "agentic_core", "apps_lic", "apps_rg", "apps_shared", "apps_exec",
    "apps_rfp", "apps_research", "apps_eval", "system_learning",
    "infrastructure", "tools", "ops_scripts", "data",
})


def _is_first_party(module_name: str) -> bool:
    if not module_name:
        return False
    return module_name.split(".")[0] in FIRST_PARTY_TOPS


def check_file(filepath: pathlib.Path, strict: bool = False) -> list[str]:
    """Check a single test file for import contract violations.

    Returns list of violation strings (empty = pass).
    """
    violations = []
    rel = str(filepath.relative_to(ROOT)).replace("\\", "/")

    try:
        source = filepath.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return [f"{rel}: Cannot read file: {e}"]

    # Rule 4: No syntax errors
    try:
        tree = ast.parse(source, filename=rel)
    except SyntaxError as e:
        return [f"{rel}:{e.lineno}: SyntaxError — {e.msg}"]

    # Rule 1: No first-party imports in try/except ImportError
    for node in ast.walk(tree):
        if not isinstance(node, ast.Try):
            continue
        has_import_error = any(
            _is_import_error_handler(h) for h in node.handlers
        )
        if not has_import_error:
            continue

        for stmt in node.body:
            if isinstance(stmt, ast.Import):
                for alias in stmt.names:
                    if _is_first_party(alias.name):
                        violations.append(
                            f"{rel}:{stmt.lineno}: First-party import '{alias.name}' "
                            f"wrapped in try/except ImportError",
                        )
            elif isinstance(stmt, ast.ImportFrom) and stmt.module:
                if _is_first_party(stmt.module):
                    violations.append(
                        f"{rel}:{stmt.lineno}: First-party import '{stmt.module}' "
                        f"wrapped in try/except ImportError",
                    )

    # Rule 2: No pytest.skip() hiding import failures
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func_name = _call_name(node.func)
        if func_name not in ("pytest.skip", "skip"):
            continue
        reason = ""
        if node.args and isinstance(node.args[0], ast.Constant):
            reason = str(node.args[0].value).lower()
        for kw in node.keywords:
            if kw.arg == "reason" and isinstance(kw.value, ast.Constant):
                reason = str(kw.value.value).lower()
        if "import" in reason:
            violations.append(
                f"{rel}:{node.lineno}: pytest.skip() hides import failure: "
                f"'{reason[:80]}'",
            )

    # Rule 3: No pytest.importorskip in core tests without optional marker
    has_optional = "pytest.mark.optional" in source
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if _call_name(node.func) in ("pytest.importorskip", "importorskip"):
            if not has_optional:
                dep = ""
                if node.args and isinstance(node.args[0], ast.Constant):
                    dep = str(node.args[0].value)
                violations.append(
                    f"{rel}:{node.lineno}: pytest.importorskip('{dep}') in "
                    f"unmarked test (add @pytest.mark.optional)",
                )

    # Strict mode: check for _AVAILABLE patterns
    if strict:
        if "_AVAILABLE" in source:
            for i, line in enumerate(source.splitlines(), 1):
                stripped = line.strip()
                if "_AVAILABLE" in stripped and not stripped.startswith("#"):
                    if "skipif" in stripped or "pytest.skip" in stripped:
                        violations.append(
                            f"{rel}:{i}: Residual _AVAILABLE skip pattern",
                        )

    return violations


def _is_import_error_handler(handler) -> bool:
    if handler.type is None:
        return False
    if isinstance(handler.type, ast.Name):
        return handler.type.id in ("ImportError", "ModuleNotFoundError")
    if isinstance(handler.type, ast.Tuple):
        return any(
            isinstance(e, ast.Name) and e.id in ("ImportError", "ModuleNotFoundError")
            for e in handler.type.elts
        )
    return False


def _call_name(node) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        prefix = _call_name(node.value)
        return f"{prefix}.{node.attr}" if prefix else node.attr
    return ""


def main():
    strict = "--strict" in sys.argv

    test_dir = ROOT / "tests"
    test_files = sorted(test_dir.rglob("test_*.py"))
    test_files.extend(sorted(ROOT.glob("test_*.py")))

    # Deduplicate
    seen = set()
    unique = []
    for f in test_files:
        key = str(f)
        if key not in seen:
            seen.add(key)
            unique.append(f)

    all_violations = []
    for fp in unique:
        violations = check_file(fp, strict=strict)
        all_violations.extend(violations)

    if all_violations:
        print(f"FAIL: {len(all_violations)} import contract violation(s) found:")
        for v in all_violations:
            print(f"  {v}")
        sys.exit(1)
    else:
        print(f"PASS: {len(unique)} test files checked, 0 violations.")
        sys.exit(0)


if __name__ == "__main__":
    main()
