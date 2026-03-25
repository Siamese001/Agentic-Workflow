"""ADG-driven tests for apps_rg/tools/skill_similarity_tool.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_rg.tools.skill_similarity_tool  # noqa: F401


def test_module_importable():
    """Module skill_similarity_tool must be importable."""
    assert apps_rg.tools.skill_similarity_tool is not None
