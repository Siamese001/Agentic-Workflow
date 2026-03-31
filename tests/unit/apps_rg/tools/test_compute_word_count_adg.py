"""ADG-driven tests for apps_rg/tools/compute_word_count.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module compute_word_count must be importable."""
    import apps_rg.tools.compute_word_count  # noqa: F401

    assert apps_rg.tools.compute_word_count is not None
