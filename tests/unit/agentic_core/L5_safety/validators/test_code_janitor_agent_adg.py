"""ADG contract tests for L5_safety/validators/CodeJanitorAgent.py.

Uses AST-based source inspection -- immune to broken transitive deps.
"""
from __future__ import annotations

import ast
import pathlib

import pytest

pytestmark = pytest.mark.unit

_SRC = (
    pathlib.Path(__file__).parents[5]
    / "agentic_core" / "L5_safety" / "reasoning" / "CodeJanitorAgent.py"
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


def _src_text():
    return _SRC.read_text(encoding="utf-8", errors="replace")


class TestJanitorViolationSource:
    def test_source_exists(self):
        assert _SRC.exists()

    def test_parses_without_error(self):
        _tree()

    def test_has_janitor_violation_class(self):
        assert "JanitorViolation" in _class_names()

    def test_has_is_valid_field(self):
        assert "is_valid" in _src_text()

    def test_has_message_field(self):
        assert "message" in _src_text()

    def test_has_severity_field(self):
        assert "severity" in _src_text()

    def test_has_file_path_field(self):
        assert "file_path" in _src_text()

    def test_has_line_number_field(self):
        assert "line_number" in _src_text()


class TestCodeJanitorAgentSource:
    def test_has_code_janitor_agent_class(self):
        assert "CodeJanitorAgent" in _class_names()

    def test_has_check_syntax(self):
    """Test has_check_syntax contract compliance."""
    # Arrange
    # TODO: Set up test data
    test_data = {}  # Replace with actual test data

    # Act
    """Test has_check_indentation contract compliance."""
    # Arrange
    # TODO: Set up test data
    """Test has_check_trailing_whitespace contract compliance."""
    # Arrange
    # TODO: Set up test data
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Validate schema
    validation_result = None  # Replace with actual validation

    # Assert - Schema Contract
    assert validation_result is not None, "Schema validation should produce a result"
    assert isinstance(validation_result, (bool, dict)), "Validation result should be structured"
    # TODO: Add specific schema validation assertions
    # assert validation_result.get("valid", False), "Data should conform to schema"