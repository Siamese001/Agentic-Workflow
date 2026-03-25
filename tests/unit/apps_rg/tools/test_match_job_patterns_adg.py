"""ADG-driven tests for apps_rg/tools/match_job_patterns.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_rg.tools.match_job_patterns  # noqa: F401


def test_module_importable():
    """Module match_job_patterns must be importable."""
    assert apps_rg.tools.match_job_patterns is not None
