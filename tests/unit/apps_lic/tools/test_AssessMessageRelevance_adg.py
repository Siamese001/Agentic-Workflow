"""ADG-driven tests for apps_lic/tools/AssessMessageRelevance.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_lic.tools.AssessMessageRelevance  # noqa: F401


def test_module_importable():
    """Module AssessMessageRelevance must be importable."""
    assert apps_lic.tools.AssessMessageRelevance is not None
