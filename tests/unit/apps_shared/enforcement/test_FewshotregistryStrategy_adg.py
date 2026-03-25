"""ADG-driven tests for apps_shared/enforcement/FewshotregistryStrategy.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_shared.enforcement.FewshotregistryStrategy  # noqa: F401


def test_module_importable():
    """Module FewshotregistryStrategy must be importable."""
    assert apps_shared.enforcement.FewshotregistryStrategy is not None
