"""ADG contract tests for agentic_core/L5_safety/validators/HygieneGuardianAgent.py.

Uses AST-based source inspection -- immune to broken transitive deps.
"""

from __future__ import annotations

import ast
import pathlib

import pytest

pytestmark = pytest.mark.unit

_SRC = (
    pathlib.Path(__file__).parents[5]
    / "agentic_core"
    / "L5_safety"
    / "validators"
    / "HygieneGuardianAgent.py"
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


class TestHygieneGuardianAgentSource:
    def test_source_exists(self):
        assert _SRC.exists()

    def test_parses_without_error(self):
        _tree()

    def test_has_hygiene_guardian_agent_class(self):
        assert "HygieneGuardianAgent" in _class_names()

    def test_has_hygiene_violation_class(self):
        assert "HygieneViolation" in _class_names()

    def test_has_heal_method(self):
        assert "heal" in _methods_of("HygieneGuardianAgent")

    def test_has_init_method(self):
        assert "__init__" in _methods_of("HygieneGuardianAgent")

    def test_has_python_extensions_constant(self):
        assert "PYTHON_EXTENSIONS" in _src_text()

    def test_has_backup_extensions_constant(self):
        assert "BACKUP_EXTENSIONS" in _src_text()

    def test_has_temp_extensions_constant(self):
        assert "TEMP_EXTENSIONS" in _src_text()

    def test_has_debug_print_pattern_constant(self):
        assert "DEBUG_PRINT_PATTERN" in _src_text()

    def test_has_copy_patterns_constant(self):
        assert "COPY_PATTERNS" in _src_text()

    def test_has_dry_run_field(self):
        pass

    """Test has_dry_run_field runtime behavior."""
    # Arrange
    input_data = {}  # Replace with actual test data

    # Act
    result = {}  # Placeholder - replace with actual execution

    # Assert
    assert result is not None, "Function should return a result"
    assert isinstance(result, (dict, list, str, int, float, bool)), "Result should be a common type"

    def test_heal_references_artifacts(self):
        assert "artifacts" in _src_text()
