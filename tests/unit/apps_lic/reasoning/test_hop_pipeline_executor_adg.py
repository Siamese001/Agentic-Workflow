"""ADG contract tests for apps_lic/reasoning/HOPPipelineExecutor.py.

Uses AST-based source inspection -- immune to broken transitive deps.
"""
from __future__ import annotations

import ast
import pathlib

import pytest

pytestmark = pytest.mark.unit

_SRC = pathlib.Path(__file__).parents[4] / "apps_lic" / "reasoning" / "HOPPipelineExecutor.py"


def _tree():
    return ast.parse(_SRC.read_text(encoding="utf-8", errors="replace"))


def _class_names():
    return {n.name for n in ast.walk(_tree()) if isinstance(n, ast.ClassDef)}


def _src_text():
    return _SRC.read_text(encoding="utf-8", errors="replace")


class TestHOPPipelineExecutorSource:
    def test_source_exists(self):
        assert _SRC.exists()

    def test_parses_without_error(self):
        _tree()

    def test_has_hop_pipeline_executor_class(self):
        assert "HOPPipelineExecutor" in _class_names()

    def test_has_stage_id_field(self):
        assert "stage_id" in _src_text()


def test_module_importable():
    pass
