"""ADG-driven tests for apps_rg/tools/PrepareResumeContext.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_rg.tools.PrepareResumeContext  # noqa: F401


def test_module_importable():
    """Module PrepareResumeContext must be importable."""
    assert apps_rg.tools.PrepareResumeContext is not None
