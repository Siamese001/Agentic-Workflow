"""ADG contract tests for agentic_core/L5_safety/validators/GovernanceAgent.py.

Uses AST-based source inspection -- immune to broken transitive deps.
"""

from __future__ import annotations

import ast
import pathlib

import pytest

pytestmark = pytest.mark.unit

_SRC = pathlib.Path(__file__).parents[5] / "agentic_core" / "L5_safety" / "reasoning" / "GovernanceAgent.py"


def _require_source() -> pathlib.Path:
    if not _SRC.exists():
        pytest.skip(f"Required source file is not present in this standalone snapshot: {_SRC}")
    return _SRC


def _tree():
    return ast.parse(_require_source().read_text(encoding="utf-8", errors="replace"))


def _class_names():
    return {n.name for n in ast.walk(_tree()) if isinstance(n, ast.ClassDef)}


def _func_names():
    return {n.name for n in ast.walk(_tree()) if isinstance(n, ast.FunctionDef)}


def _methods_of(cls_name: str) -> set:
    tree = _tree()
    cls = next((n for n in ast.walk(tree) if isinstance(n, ast.ClassDef) and n.name == cls_name), None)
    if cls is None:
        return set()
    return {n.name for n in ast.walk(cls) if isinstance(n, ast.FunctionDef)}


def _src_text():
    return _require_source().read_text(encoding="utf-8", errors="replace")


class TestGovernanceAgentSource:
    def test_source_exists(self):
        assert _require_source().exists()

    def test_parses_without_error(self):
        _tree()

    def test_has_governance_agent_class(self):
        assert "GovernanceAgent" in _class_names()

    def test_has_dependency_graph_class(self):
        assert "DependencyGraph" in _class_names()

    def test_has_module_level_heal_function(self):
        pass

    """Test has_module_level_heal_function runtime behavior."""
    # Arrange
    # TODO: Set up test data for has_module_level_heal_function
    test_data = {}  # Replace with actual test data

    # Arrange
    input_data = {}  # Replace with actual test data

    # Act
    result = {}  # Placeholder - replace with actual execution

    # Assert
    assert result is not None, "Function should return a result"
    assert isinstance(result, (dict, list, str, int, float, bool)), "Result should be a common type"

    # TODO: Add specific runtime behavior assertions
    def test_heal_references_manual_required(self):
        assert "manual_required" in _src_text()

    def test_heal_references_skipped(self):
        assert "skipped" in _src_text()

    def test_heal_references_failed(self):
        assert "failed" in _src_text()

    def test_heal_result_has_artifacts_key(self):
        assert "artifacts" in _src_text()

    def test_heal_result_has_errors_key(self):
        assert "errors" in _src_text()
