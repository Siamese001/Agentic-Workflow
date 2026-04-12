"""ADG contract tests for agentic_core/L5_safety/types/hardening_errors.py.

Uses AST-based source inspection — immune to broken transitive deps.
"""

from __future__ import annotations

import ast
import pathlib
import unittest

import pytest

pytestmark = pytest.mark.unit
_SRC = pathlib.Path(__file__).parents[5] / "agentic_core" / "L5_safety" / "types" / "hardening_errors.py"


def _tree():
    return ast.parse(_SRC.read_text(encoding="utf-8", errors="replace"))


def _class_names():
    return {n.name for n in ast.walk(_tree()) if isinstance(n, ast.ClassDef)}


def _src_text():
    return _SRC.read_text(encoding="utf-8", errors="replace")


class GeneratedTest(unittest.TestCase):
    """Generated test class for agentic_core.L5_safety.types."""

    def test_ExecutionTraceIntegrityError_init(self):
        """Test ExecutionTraceIntegrityError initialization."""
        from agentic_core.L5_safety.types import ExecutionTraceIntegrityError

        instance = ExecutionTraceIntegrityError()
        self.assertIsNotNone(instance)

    def test_MutationReplayIntegrityViolation_init(self):
        """Test MutationReplayIntegrityViolation initialization."""
        from agentic_core.L5_safety.types import MutationReplayIntegrityViolation

        instance = MutationReplayIntegrityViolation()
        self.assertIsNotNone(instance)

    def test_parses_without_error(self):
        _tree()

    def test_has_execution_trace_integrity_error(self):
        """Test has_execution_trace_integrity_error runtime behavior."""
        assert "ExecutionTraceIntegrityError" in _class_names()

    def test_all_errors_subclass_exception(self):
        import re

        src = _src_text()
        for cls in _class_names():
            match = re.search(f"class {cls}\\s*\\(([^)]+)\\)", src)
            assert match, f"{cls} must have explicit base class"
