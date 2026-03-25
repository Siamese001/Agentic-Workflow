"""ADG-driven tests for apps_rg/tools/EvaluateWritingQuality.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_rg.tools.EvaluateWritingQuality  # noqa: F401


def test_module_importable():
    """Module EvaluateWritingQuality must be importable."""
    assert apps_rg.tools.EvaluateWritingQuality is not None
