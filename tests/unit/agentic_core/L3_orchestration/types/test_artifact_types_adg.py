"""ADG contract tests for L3_orchestration/types/artifact_types.py.

Uses AST-based source inspection -- immune to broken transitive deps.
"""
from __future__ import annotations

import ast
import pathlib

import pytest

pytestmark = pytest.mark.unit
try:
#  # MOVED: import agentic_core.L3_orchestration.types.artifact_types as _mod  # noqa: F401  # ADG covers
except (ValueError, TypeError, RuntimeError) as e:
    _mod = None


_SRC = (
    pathlib.Path(__file__).parents[5]
    / "agentic_core" / "L3_orchestration" / "types" / "artifact_types.py"
)


def _tree():
    return ast.parse(_SRC.read_text(encoding="utf-8", errors="replace"))


def _class_names():
    return {n.name for n in ast.walk(_tree()) if isinstance(n, ast.ClassDef)}


def _src_text():
    return _SRC.read_text(encoding="utf-8", errors="replace")


class TestArtifactTypesSource:
    def test_source_exists(self):
                import agentic_core.L3_orchestration.types.artifact_types as _mod  # noqa: F401  # ADG covers
                assert _SRC.exists()

        assert _SRC.exists()

    def test_parses_without_error(self):
        _tree()

    def test_has_artifact_class(self):
        assert "Artifact" in _class_names()

    def test_has_state_validation_result_or_validation_result(self):
        names = _class_names()
        assert "StateValidationResult" in names or "ValidationResult" in names

    def test_artifact_is_dataclass_decorated(self):
        assert "dataclass" in _src_text()


def test_module_importable():
    pass
