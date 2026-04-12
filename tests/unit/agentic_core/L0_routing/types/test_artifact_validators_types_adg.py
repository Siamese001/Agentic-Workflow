"""ADG contract tests for agentic_core/L0_routing/types/artifact_validators_types.py.

Uses AST-based source inspection — immune to broken transitive deps.
"""

from __future__ import annotations

import ast
import pathlib

import pytest

pytestmark = pytest.mark.unit

_SRC = (
    pathlib.Path(__file__).parents[5]
    / "agentic_core"
    / "L0_routing"
    / "types"
    / "artifact_validators_types.py"
)


def _tree():
    return ast.parse(_SRC.read_text(encoding="utf-8", errors="replace"))


def _func_names():
    return {n.name for n in ast.walk(_tree()) if isinstance(n, ast.FunctionDef)}


class TestArtifactValidatorsTypesSource:
    """Generated test class for agentic_core.L0_routing.types.artifact_validators_types."""

    def test_source_exists(self):
        assert _SRC.exists()

    def test_parses_without_error(self):
        _tree()

    def test_has_validate_result_artifact(self):
        assert "validate_result_artifact" in _func_names()

    def test_has_to_result_artifact_dict(self):
        assert "to_result_artifact_dict" in _func_names()
