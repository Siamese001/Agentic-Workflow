"""
Deterministic enforcement: No xfail/skip markers allowed in contract gate tests.

This test uses **pure AST analysis** to detect forbidden bypass constructs.
String/substring scanning is NOT used - only AST nodes are inspected,
which automatically ignores comments, docstrings, and string literals.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import NamedTuple

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

pytestmark = pytest.mark.guardian


class BypassViolation(NamedTuple):
    """Structured bypass violation report."""

    line: int
    construct: str
    kind: str  # 'decorator' | 'call'


# -----------------------------------------------------------------------------
# AST-True Detection Functions
# -----------------------------------------------------------------------------


def _get_attr_chain(node: ast.expr) -> list[str]:
    """Extract attribute chain from AST node, e.g., pytest.mark.xfail -> ['pytest','mark','xfail']."""
    if isinstance(node, ast.Name):
        return [node.id]
    elif isinstance(node, ast.Attribute):
        return _get_attr_chain(node.value) + [node.attr]
    elif isinstance(node, ast.Call):
        return _get_attr_chain(node.func)
    return []


def _matches_forbidden_decorator(chain: list[str]) -> str | None:
    """
    Check if attribute chain matches forbidden pytest/unittest decorator patterns.
    Returns the matched construct name or None.
    """
    # pytest.mark.{xfail, skip, skipif}
    if len(chain) >= 3 and chain[0] == "pytest" and chain[1] == "mark":
        if chain[2] in ("xfail", "skip", "skipif"):
            return f"pytest.mark.{chain[2]}"

    # unittest.{skip, skipIf, skipUnless}
    if len(chain) >= 2 and chain[0] == "unittest":
        if chain[1] in ("skip", "skipIf", "skipUnless"):
            return f"unittest.{chain[1]}"

    return None


def _matches_forbidden_call(chain: list[str]) -> str | None:
    """
    Check if attribute chain matches forbidden pytest call patterns.
    Returns the matched construct name or None.
    """
    # pytest.{xfail, skip, importorskip}
    if len(chain) >= 2 and chain[0] == "pytest":
        if chain[1] in ("xfail", "skip", "importorskip"):
            return f"pytest.{chain[1]}()"

    # pytest.mark.xfail() used as a call (rare but possible)
    if len(chain) >= 3 and chain[0] == "pytest" and chain[1] == "mark":
        if chain[2] in ("xfail", "skip", "skipif"):
            return f"pytest.mark.{chain[2]}()"

    return None


def find_bypass_constructs_ast(source: str) -> list[BypassViolation]:
    """
    Pure AST-based detection of forbidden bypass constructs.

    Detects:
      A) Decorators: pytest.mark.{xfail,skip,skipif}, unittest.{skip,skipIf,skipUnless}
      B) Calls: pytest.{xfail,skip,importorskip}() in function/method bodies

    Does NOT match strings, comments, or docstrings (AST-only).
    Does NOT double-count decorator calls (decorator already covers them).
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    violations: list[BypassViolation] = []

    # Track decorator call nodes to avoid double-counting
    decorator_call_ids: set[int] = set()

    for node in ast.walk(tree):
        # Check decorators on functions/classes
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            for decorator in node.decorator_list:
                chain = _get_attr_chain(decorator)
                matched = _matches_forbidden_decorator(chain)
                if matched:
                    violations.append(
                        BypassViolation(
                            line=decorator.lineno,
                            construct=matched,
                            kind="decorator",
                        ),
                    )
                    # Track if decorator is a Call to avoid double-counting
                    if isinstance(decorator, ast.Call):
                        decorator_call_ids.add(id(decorator))

    # Second pass: Check call expressions (excluding decorator calls)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            # Skip if this Call was already counted as a decorator
            if id(node) in decorator_call_ids:
                continue

            chain = _get_attr_chain(node.func)
            matched = _matches_forbidden_call(chain)
            if matched:
                violations.append(
                    BypassViolation(
                        line=node.lineno,
                        construct=matched,
                        kind="call",
                    ),
                )

    return violations


# -----------------------------------------------------------------------------
# Main Enforcement Test
# -----------------------------------------------------------------------------


# Pre-existing files that legitimately use pytest.skip() for conditional guards
# (e.g., "no agents found", "optional feature missing"). NOT bypass constructs.
_SKIP_ALLOWLISTED_FILES = frozenset(
    {
        "test_all_active_agents_have_heal.py",
        "test_core_components.py",
        "test_discovery_sovereign_classification.py",
        "test_folder_purity_hardening.py",
        "test_import_safety.py",
        "test_mro_mixin_order.py",
        "test_obsolete_functionality_detection.py",
        "test_ssot_alignment.py",
    },
)


def test_no_bypass_constructs_in_guardian_tests():
    """
    HARD ENFORCEMENT: No xfail/skip/skipif constructs allowed in tests/guardian/.

    Uses pure AST analysis - automatically ignores comments, docstrings, strings.
    Files in _SKIP_ALLOWLISTED_FILES are excluded (pre-existing conditional guards).
    """
    guardian_test_dir = Path(__file__).parent
    all_violations: list[str] = []

    for py_file in guardian_test_dir.glob("test_*.py"):
        # Skip this enforcement file itself
        if py_file.name == "test_no_xfail_skip_in_contract_gate.py":
            continue
        # Skip allowlisted files with pre-existing conditional guards
        if py_file.name in _SKIP_ALLOWLISTED_FILES:
            continue

        source = py_file.read_text(encoding="utf-8")
        violations = find_bypass_constructs_ast(source)

        for v in violations:
            all_violations.append(f"  {py_file.name}:{v.line} [{v.kind}] {v.construct}")

    assert not all_violations, (
        "CONSTITUTIONAL VIOLATION: Bypass constructs found in guardian tests.\n"
        "These weaken deterministic governance and are FORBIDDEN:\n"
        + "\n".join(all_violations)
        + "\n\nFix the underlying issue or remove the test. No exceptions."
    )


# -----------------------------------------------------------------------------
# Synthetic Fixture Tests: Prove Each Forbidden Construct Is Detected
# -----------------------------------------------------------------------------


class TestSyntheticBypassDetection:
    """Prove AST detection works for each forbidden construct."""

    def test_detects_pytest_mark_xfail_decorator(self):
        """Detect @pytest.mark.xfail decorator."""
        source = """
import pytest

@pytest.mark.xfail(reason="test")
def test_foo():
    pass
"""
        violations = find_bypass_constructs_ast(source)
        assert len(violations) == 1
        assert violations[0].construct == "pytest.mark.xfail"
        assert violations[0].kind == "decorator"

    def test_detects_pytest_mark_skip_decorator(self):
        """Detect @pytest.mark.skip decorator."""
        source = """
import pytest

@pytest.mark.skip(reason="test")
def test_foo():
    pass
"""
        violations = find_bypass_constructs_ast(source)
        assert len(violations) == 1
        assert violations[0].construct == "pytest.mark.skip"
        assert violations[0].kind == "decorator"

    def test_detects_pytest_mark_skipif_decorator(self):
        """Detect @pytest.mark.skipif decorator."""
        source = """
import pytest

@pytest.mark.skipif(True, reason="test")
def test_foo():
    pass
"""
        violations = find_bypass_constructs_ast(source)
        assert len(violations) == 1
        assert violations[0].construct == "pytest.mark.skipif"
        assert violations[0].kind == "decorator"

    def test_detects_pytest_xfail_call(self):
        """Detect pytest.xfail() call in test body."""
        source = """
import pytest

def test_foo():
    pytest.xfail("reason")
"""
        violations = find_bypass_constructs_ast(source)
        assert len(violations) == 1
        assert violations[0].construct == "pytest.xfail()"
        assert violations[0].kind == "call"

    def test_detects_pytest_skip_call(self):
        """Detect pytest.skip() call in test body."""
        source = """
import pytest

def test_foo():
    pytest.skip("reason")
"""
        violations = find_bypass_constructs_ast(source)
        assert len(violations) == 1
        assert violations[0].construct == "pytest.skip()"
        assert violations[0].kind == "call"

    def test_detects_pytest_importorskip_call(self):
        """Detect pytest.importorskip() call."""
        source = """
import pytest

def test_foo():
    pytest.importorskip("some_module")
"""
        violations = find_bypass_constructs_ast(source)
        assert len(violations) == 1
        assert violations[0].construct == "pytest.importorskip()"
        assert violations[0].kind == "call"

    def test_detects_unittest_skip_decorator(self):
        """Detect @unittest.skip decorator."""
        source = """
import unittest

@unittest.skip("reason")
def test_foo():
    pass
"""
        violations = find_bypass_constructs_ast(source)
        assert len(violations) == 1
        assert violations[0].construct == "unittest.skip"
        assert violations[0].kind == "decorator"

    def test_detects_unittest_skipIf_decorator(self):
        """Detect @unittest.skipIf decorator."""
        source = """
import unittest

@unittest.skipIf(True, "reason")
def test_foo():
    pass
"""
        violations = find_bypass_constructs_ast(source)
        assert len(violations) == 1
        assert violations[0].construct == "unittest.skipIf"
        assert violations[0].kind == "decorator"

    def test_detects_unittest_skipUnless_decorator(self):
        """Detect @unittest.skipUnless decorator."""
        source = """
import unittest

@unittest.skipUnless(False, "reason")
def test_foo():
    pass
"""
        violations = find_bypass_constructs_ast(source)
        assert len(violations) == 1
        assert violations[0].construct == "unittest.skipUnless"
        assert violations[0].kind == "decorator"

    def test_ignores_string_containing_xfail(self):
        """String literals containing 'xfail' are NOT detected (AST-only)."""
        source = """
def test_foo():
    msg = "pytest.mark.xfail is forbidden"
    assert True
"""
        violations = find_bypass_constructs_ast(source)
        assert len(violations) == 0

    def test_ignores_docstring_containing_skip(self):
        """Docstrings containing 'skip' are NOT detected (AST-only)."""
        source = '''
def test_foo():
    """This docstring mentions pytest.skip() but is not a violation."""
    assert True
'''
        violations = find_bypass_constructs_ast(source)
        assert len(violations) == 0

    def test_clean_file_passes(self):
        """A clean test file with no bypasses has zero violations."""
        source = """
import pytest

def test_clean():
    assert True

class TestClean:
    def test_also_clean(self):
        assert 1 + 1 == 2
"""
        violations = find_bypass_constructs_ast(source)
        assert len(violations) == 0

    def test_distinct_violations_both_reported(self):
        """
        Decorator + call in same file => 2 distinct violations (no suppression).

        This tests that dedupe logic doesn't accidentally suppress distinct violations.
        """
        source = """
import pytest

@pytest.mark.xfail(reason="test")
def test_with_decorator():
    pass

def test_with_call():
    pytest.skip("skipping this one")
"""
        violations = find_bypass_constructs_ast(source)

        # Should detect exactly 2 distinct violations
        assert len(violations) == 2, (
            f"Expected 2 distinct violations (decorator + call), got {len(violations)}: {violations}"
        )

        # Verify both kinds are reported
        kinds = {v.kind for v in violations}
        assert "decorator" in kinds, "Decorator violation should be reported"
        assert "call" in kinds, "Call violation should be reported"

        # Verify distinct constructs
        constructs = {v.construct for v in violations}
        assert "pytest.mark.xfail" in constructs, "xfail decorator should be detected"
        assert "pytest.skip()" in constructs, "skip() call should be detected"

    def test_multiple_decorators_all_reported(self):
        """Multiple decorators on different functions => all reported."""
        source = """
import pytest

@pytest.mark.xfail
def test_one():
    pass

@pytest.mark.skip
def test_two():
    pass

@pytest.mark.skipif(True, reason="test")
def test_three():
    pass
"""
        violations = find_bypass_constructs_ast(source)

        # Should detect all 3 decorators
        assert len(violations) == 3, f"Expected 3 decorator violations, got {len(violations)}: {violations}"

        constructs = {v.construct for v in violations}
        assert "pytest.mark.xfail" in constructs
        assert "pytest.mark.skip" in constructs
        assert "pytest.mark.skipif" in constructs
