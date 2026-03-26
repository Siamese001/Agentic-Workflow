"""ADG contract tests for L1_cognition/engines/cognitive_engine.py.

Uses AST-based source inspection -- immune to broken transitive deps.
"""
from __future__ import annotations

import ast
import pathlib

import pytest

pytestmark = pytest.mark.unit
try:
#  # MOVED: import agentic_core.L1_cognition.engines.cognitive_engine as _mod  # noqa: F401  # ADG covers
except (ValueError, TypeError, RuntimeError) as e:
    _mod = None


_SRC = (
    pathlib.Path(__file__).parents[5]
    / "agentic_core" / "L1_cognition" / "engines" / "cognitive_engine.py"
)


def _tree():
    return ast.parse(_SRC.read_text(encoding="utf-8", errors="replace"))


def _class_names():
    return {n.name for n in ast.walk(_tree()) if isinstance(n, ast.ClassDef)}


def _methods_of(cls_name: str) -> set:
    tree = _tree()
    cls = next((n for n in ast.walk(tree) if isinstance(n, ast.ClassDef) and n.name == cls_name), None)
    if cls is None:
        return set()
    return {n.name for n in ast.walk(cls) if isinstance(n, ast.FunctionDef)}


class TestCognitiveEngineSource:
    def test_source_exists(self):
        import agentic_core.L1_cognition.engines.cognitive_engine as _mod  # noqa: F401  # ADG covers
        assert _SRC.exists()

    def test_parses_without_error(self):
        _tree()

    def test_has_cognitive_node_refactored_class(self):
        assert "CognitiveNodeRefactored" in _class_names()

    def test_has_process_or_execute(self):
    """Test has_process_or_execute runtime behavior."""
    # Arrange
    # TODO: Set up execution parameters
    input_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute has_process_or_execute
    result = None  # Replace with actual execution

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, (dict, list, str, int, float, bool)), "Result should be a common type"
    # TODO: Add specific execution assertions
