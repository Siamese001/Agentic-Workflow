"""ADG-driven tests for apps_lic/reasoning/LeadQualityAgent.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module LeadQualityAgent must be importable."""
    import apps_lic.reasoning.LeadQualityAgent as _mod  # noqa: F401

    assert _mod is not None
