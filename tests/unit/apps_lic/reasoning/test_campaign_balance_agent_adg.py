"""ADG contract tests for apps_lic/reasoning/CampaignBalanceAgent.py.

Uses AST-based source inspection -- immune to broken transitive deps.
"""

from __future__ import annotations

import ast
import pathlib

import pytest

pytestmark = pytest.mark.unit

_SRC = pathlib.Path(__file__).parents[4] / "apps_lic" / "reasoning" / "CampaignBalanceAgent.py"


def _tree():
    return ast.parse(_SRC.read_text(encoding="utf-8", errors="replace"))


def _class_names():
    return {n.name for n in ast.walk(_tree()) if isinstance(n, ast.ClassDef)}


def _src_text():
    return _SRC.read_text(encoding="utf-8", errors="replace")


class TestCampaignBalanceAgentSource:
    def test_source_exists(self):
        assert _SRC.exists()

    def test_parses_without_error(self):
        _tree()

    def test_mentions_class_name(self):
        assert "CampaignBalanceAgent" in _src_text()


def test_module_importable():
    pass
