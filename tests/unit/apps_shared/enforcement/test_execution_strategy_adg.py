"""ADG-driven tests for apps_shared/enforcement/execution_strategy.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_shared.enforcement.execution_strategy  # noqa: F401


def test_module_importable():
    """Module execution_strategy must be importable."""
    assert apps_shared.enforcement.execution_strategy is not None
