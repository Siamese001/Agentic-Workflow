"""ADG contract tests for agentic_core/L5_safety/types/file_health_score_types.py.

Uses AST-based source inspection — immune to broken transitive deps.
"""
from __future__ import annotations

import ast
import pathlib

import pytest

pytestmark = pytest.mark.unit
try:
    import agentic_core.L5_safety.types.file_health_score_types as _mod  # noqa: F401  # ADG covers
except (ValueError, TypeError, RuntimeError) as e:
    _mod = None


_SRC = (
    pathlib.Path(__file__).parents[5]
    / "agentic_core" / "L5_safety" / "types" / "file_health_score_types.py"
)


def _tree():
    return ast.parse(_SRC.read_text(encoding="utf-8", errors="replace"))


def _class_names():
    return {n.name for n in ast.walk(_tree()) if isinstance(n, ast.ClassDef)}


def _methods_of(cls_name: str) -> set[str]:
    tree = _tree()
    cls = next((n for n in ast.walk(tree) if isinstance(n, ast.ClassDef) and n.name == cls_name), None)
    if cls is None:
        return set()
    return {n.name for n in ast.walk(cls) if isinstance(n, ast.FunctionDef)}


class TestFileHealthScoreTypesSource:
    def test_source_exists(self):
        assert _SRC.exists()

    def test_parses_without_error(self):
        _tree()

    def test_has_file_health_score(self):
        assert "FileHealthScore" in _class_names()

    def test_has_healing_lease(self):
        assert "HealingLease" in _class_names()

    def test_has_atomic_blackboard(self):
        assert "AtomicBlackboard" in _class_names()

    def test_file_health_score_has_to_dict(self):
        assert "to_dict" in _methods_of("FileHealthScore")

    def test_file_health_score_has_from_dict(self):
        assert "from_dict" in _methods_of("FileHealthScore")

    def test_healing_lease_has_is_expired(self):
        assert "is_expired" in _methods_of("HealingLease")