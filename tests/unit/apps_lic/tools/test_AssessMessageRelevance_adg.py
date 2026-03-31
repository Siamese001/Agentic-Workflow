"""ADG-driven tests for apps_lic/tools/AssessMessageRelevance.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module AssessMessageRelevance must be importable."""
    import apps_lic.tools.AssessMessageRelevance  # noqa: F401

    assert apps_lic.tools.AssessMessageRelevance is not None
