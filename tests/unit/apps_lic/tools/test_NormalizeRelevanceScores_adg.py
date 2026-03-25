"""ADG-driven tests for apps_lic/tools/NormalizeRelevanceScores.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_lic.tools.NormalizeRelevanceScores  # noqa: F401


def test_module_importable():
    """Module NormalizeRelevanceScores must be importable."""
    assert apps_lic.tools.NormalizeRelevanceScores is not None
