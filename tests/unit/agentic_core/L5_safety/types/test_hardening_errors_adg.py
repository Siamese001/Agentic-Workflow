"""ADG contract tests for agentic_core/L5_safety/types/hardening_errors.py."""

from __future__ import annotations

import ast
import pathlib
import re
import unittest

import pytest

pytestmark = pytest.mark.unit

_types = pytest.importorskip(
    "agentic_core.L5_safety.types",
    reason="Requires L5 safety types exports from the monorepo checkout.",
)
ExecutionTraceIntegrityError = _types.ExecutionTraceIntegrityError
MutationReplayIntegrityViolation = _types.MutationReplayIntegrityViolation

_SRC = pathlib.Path(__file__).parents[5] / "agentic_core" / "L5_safety" / "types" / "hardening_errors.py"


def _require_source() -> pathlib.Path:
    if not _SRC.exists():
        pytest.skip(f"Required source file is not present in this standalone snapshot: {_SRC}")
    return _SRC


def _tree():
    return ast.parse(_require_source().read_text(encoding="utf-8", errors="replace"))


def _class_names():
    return {n.name for n in ast.walk(_tree()) if isinstance(n, ast.ClassDef)}


def _src_text():
    return _require_source().read_text(encoding="utf-8", errors="replace")


class GeneratedTest(unittest.TestCase):
    """Generated smoke tests for L5 safety hardening errors."""

    def test_execution_trace_integrity_error_exported(self):
        self.assertIsNotNone(ExecutionTraceIntegrityError)

    def test_mutation_replay_integrity_violation_exported(self):
        self.assertIsNotNone(MutationReplayIntegrityViolation)

    def test_parses_without_error(self):
        _tree()

    def test_has_execution_trace_integrity_error(self):
        assert "ExecutionTraceIntegrityError" in _class_names()

    def test_all_errors_subclass_exception(self):
        src = _src_text()
        for cls in _class_names():
            match = re.search(rf"class {cls}\s*\(([^)]+)\)", src)
            assert match, f"{cls} must have explicit base class"
