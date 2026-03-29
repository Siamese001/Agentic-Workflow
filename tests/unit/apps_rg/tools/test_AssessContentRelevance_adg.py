"""ADG-driven tests for apps_rg/tools/AssessContentRelevance.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module AssessContentRelevance must be importable."""
    import apps_rg.tools.AssessContentRelevance  # noqa: F401

    assert apps_rg.tools.AssessContentRelevance is not None