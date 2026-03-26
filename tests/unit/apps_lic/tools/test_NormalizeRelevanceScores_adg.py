"""ADG-driven tests for apps_lic/tools/NormalizeRelevanceScores.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit



def test_module_importable():
    """Module NormalizeRelevanceScores must be importable."""
    import apps_lic.tools.NormalizeRelevanceScores  # noqa: F401

    assert apps_lic.tools.NormalizeRelevanceScores is not None