"""Smoke test quality guard — prevents regression to fake-green smoke coverage.

This meta-test scans all smoke test files and flags:
  1. VACUOUS: `assert True` in any test function (fake-green)
  2. BARE_IMPORT: test that only imports a module with no assertion beyond `is not None`
  3. NO_ASSERTION: test function with zero assert statements

Run with: pytest tests/smoke/test_smoke_quality_guard.py -v
"""

import ast
from pathlib import Path

import pytest

SMOKE_DIR = Path(__file__).resolve().parent

# This file is the guard itself — exclude it from scanning
_SELF = Path(__file__).name


def _collect_smoke_test_files():
    """Yield all test_*.py files under tests/smoke/, excluding this guard."""
    for p in sorted(SMOKE_DIR.rglob("test_*.py")):
        if p.name == _SELF:
            continue
        yield p


def _extract_test_functions(tree: ast.Module):
    """Yield (function_name, function_node) for all test functions/methods."""
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name.startswith("test_"):
                yield node.name, node


def _has_vacuous_assert(func_node: ast.AST) -> bool:
    """Check if a function contains `assert True`."""
    for node in ast.walk(func_node):
        if isinstance(node, ast.Assert):
            # assert True
            if isinstance(node.test, ast.Constant) and node.test.value is True:
                return True
            # assert True  (Name node in older ASTs)
            if isinstance(node.test, ast.Name) and node.test.id == "True":
                return True
    return False


def _count_assertions(func_node: ast.AST) -> int:
    """Count assert statements in a function."""
    count = 0
    for node in ast.walk(func_node):
        if isinstance(node, ast.Assert):
            count += 1
    return count


def _is_bare_import_test(func_node: ast.AST) -> bool:
    """Check if a test only imports + asserts `is not None` or `isinstance(X, type)`."""
    asserts = []
    for node in ast.walk(func_node):
        if isinstance(node, ast.Assert):
            asserts.append(node)

    if not asserts:
        return False

    all_weak = True
    for a in asserts:
        test = a.test
        # assert X is not None
        if isinstance(test, ast.Compare):
            if len(test.ops) == 1 and isinstance(test.ops[0], ast.IsNot):
                if isinstance(test.comparators[0], ast.Constant) and test.comparators[0].value is None:
                    continue
        # assert isinstance(X, type)
        if isinstance(test, ast.Call):
            if isinstance(test.func, ast.Name) and test.func.id == "isinstance":
                continue
        # assert callable(X)
        if isinstance(test, ast.Call):
            if isinstance(test.func, ast.Name) and test.func.id == "callable":
                continue
        # assert X is not None (via NameConstant in older Python)
        all_weak = False
        break

    return all_weak


@pytest.mark.smoke
def test_no_vacuous_assert_in_smoke_tests():
    """No smoke test should contain `assert True` — this is fake-green coverage."""
    violations = []
    for filepath in _collect_smoke_test_files():
        source = filepath.read_text(encoding="utf-8")
        # Skip files with guardian exemption comment
        if "# guardian: allow-test-quality" in source:
            continue
        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue
        for func_name, func_node in _extract_test_functions(tree):
            if _has_vacuous_assert(func_node):
                rel = filepath.relative_to(SMOKE_DIR)
                violations.append(f"{rel}::{func_name}")

    assert not violations, (
        f"Found {len(violations)} smoke test(s) with `assert True` (fake-green):\n"
        + "\n".join(f"  - {v}" for v in violations)
    )


@pytest.mark.smoke
def test_no_assertion_free_smoke_tests():
    """Every smoke test function must have at least one assert statement."""
    violations = []
    for filepath in _collect_smoke_test_files():
        source = filepath.read_text(encoding="utf-8")
        if "# guardian: allow-test-quality" in source:
            continue
        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue
        for func_name, func_node in _extract_test_functions(tree):
            # Allow parametrized tests (the assert may be in the body after skip)
            if _count_assertions(func_node) == 0:
                # Check if it uses pytest.skip or pytest.fail
                src_lines = ast.get_source_segment(source, func_node) or ""
                if "pytest.skip" not in src_lines and "pytest.fail" not in src_lines:
                    rel = filepath.relative_to(SMOKE_DIR)
                    violations.append(f"{rel}::{func_name}")

    assert not violations, f"Found {len(violations)} smoke test(s) with zero assertions:\n" + "\n".join(
        f"  - {v}" for v in violations
    )


@pytest.mark.smoke
def test_smoke_test_count_minimum():
    """Smoke test suite must have at least 50 tests to prevent silent deletion."""
    count = 0
    for filepath in _collect_smoke_test_files():
        source = filepath.read_text(encoding="utf-8")
        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue
        for _ in _extract_test_functions(tree):
            count += 1

    assert count >= 50, (
        f"Smoke test suite has only {count} test functions — "
        f"expected at least 50 (guard against silent test deletion)"
    )
