"""ADG-driven tests for apps_shared/enforcement/RankingStrategy.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module RankingStrategy must be importable."""
    import apps_shared.enforcement.RankingStrategy  # noqa: F401

    assert apps_shared.enforcement.RankingStrategy is not None