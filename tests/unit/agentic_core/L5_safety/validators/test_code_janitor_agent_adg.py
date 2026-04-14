"""ADG contract tests for L5_safety/validators/CodeJanitorAgent.py.

Uses AST-based source inspection -- immune to broken transitive deps.
"""

from __future__ import annotations

import ast
import pathlib

import pytest

pytestmark = pytest.mark.unit

_SRC = pathlib.Path(__file__).parents[5] / "agentic_core" / "L5_safety" / "reasoning" / "CodeJanitorAgent.py"


def _require_source() -> pathlib.Path:
    if not _SRC.exists():
        pytest.skip(f"Required source file is not present in this standalone snapshot: {_SRC}")
    return _SRC


def _tree():
    return ast.parse(_require_source().read_text(encoding="utf-8", errors="replace"))


def _class_names():
    return {n.name for n in ast.walk(_tree()) if isinstance(n, ast.ClassDef)}


def _methods_of(cls_name: str) -> set:
    tree = _tree()
    cls = next((n for n in ast.walk(tree) if isinstance(n, ast.ClassDef) and n.name == cls_name), None)
    if cls is None:
        return set()
    return {n.name for n in ast.walk(cls) if isinstance(n, ast.FunctionDef)}


def _src_text():
    return _require_source().read_text(encoding="utf-8", errors="replace")


class TestJanitorViolationSource:
    def test_source_exists(self):
        assert _require_source().exists()

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
        assert "check_syntax" in _methods_of("CodeJanitorAgent")

    def test_has_check_indentation(self):
        """Test has_check_indentation contract compliance."""
        assert "check_indentation" in _methods_of("CodeJanitorAgent")

    def test_has_check_trailing_whitespace(self):
        """Test has_check_trailing_whitespace contract compliance."""
        assert "check_trailing_whitespace" in _methods_of("CodeJanitorAgent")
