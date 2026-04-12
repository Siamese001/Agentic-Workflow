"""ADG contract tests for apps_rg/reasoning/RgTemplateOptimizerAgent.py.

Uses AST-based source inspection -- immune to broken transitive deps.
"""

from __future__ import annotations

import ast
import pathlib

import pytest

pytestmark = pytest.mark.unit

_SRC = pathlib.Path(__file__).parents[5] / "apps_rg" / "reasoning" / "RgTemplateOptimizerAgent.py"


def _tree():
    return ast.parse(_SRC.read_text(encoding="utf-8", errors="replace"))


def _src_text():
    return _SRC.read_text(encoding="utf-8", errors="replace")


class TestRgTemplateOptimizerAgentSource:
    def test_source_exists(self):
        assert _SRC.exists()

    def test_parses_without_error(self):
        _tree()

    def test_mentions_class_name(self):
        assert "RgTemplateOptimizerAgent" in _src_text()
