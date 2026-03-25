"""ADG-driven tests for apps_rg/tools/compute_word_count.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_rg.tools.compute_word_count  # noqa: F401


def test_module_importable():
    """Module compute_word_count must be importable."""
    assert apps_rg.tools.compute_word_count is not None
