"""ADG-driven tests for apps_rg/tools/create_experience_bullets.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_rg.tools.create_experience_bullets  # noqa: F401


def test_module_importable():
    """Module create_experience_bullets must be importable."""
    assert apps_rg.tools.create_experience_bullets is not None
