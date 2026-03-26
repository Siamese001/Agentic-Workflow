"""ADG-driven tests for apps_rg/engines/job_pattern_matcher.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit



def test_module_importable():
    """Module job_pattern_matcher must be importable."""
    import apps_rg.engines.job_pattern_matcher  # noqa: F401

    assert apps_rg.engines.job_pattern_matcher is not None
