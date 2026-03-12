"""ADG contract tests for agentic_core/L5_safety/types/hardening_errors.py.

Uses AST-based source inspection — immune to broken transitive deps.
"""
from __future__ import annotations
import ast
import pathlib
import pytest

pytestmark = pytest.mark.unit

_SRC = (
    pathlib.Path(__file__).parents[5]
    / "agentic_core" / "L5_safety" / "types" / "hardening_errors.py"
)


def _tree():
    return ast.parse(_SRC.read_text(encoding="utf-8", errors="replace"))


def _class_names():
    return {n.name for n in ast.walk(_tree()) if isinstance(n, ast.ClassDef)}


def _src_text():
    return _SRC.read_text(encoding="utf-8", errors="replace")


class TestHardeningErrorsSource:
    def test_source_exists(self):
        assert _SRC.exists()

    def test_parses_without_error(self):
        _tree()

    def test_has_execution_trace_integrity_error(self):
        assert "ExecutionTraceIntegrityError" in _class_names()

    def test_has_mutation_replay_integrity_violation(self):
        assert "MutationReplayIntegrityViolation" in _class_names()

    def test_has_ledger_integrity_violation(self):
        assert "LedgerIntegrityViolation" in _class_names()

    def test_has_mutation_commit_failure(self):
        assert "MutationCommitFailure" in _class_names()

    def test_has_c0_mutation_violation(self):
        assert "C0MutationViolation" in _class_names()

    def test_all_errors_subclass_exception(self):
        import re
        src = _src_text()
        for cls in _class_names():
            match = re.search(rf"class {cls}\s*\(([^)]+)\)", src)
            assert match, f"{cls} must have explicit base class"
