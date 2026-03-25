"""ADG-driven tests for apps_shared/scripts/benchmark_consolidation_performance.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_shared.scripts.benchmark_consolidation_performance  # noqa: F401


def test_module_importable():
    """Module benchmark_consolidation_performance must be importable."""
    assert apps_shared.scripts.benchmark_consolidation_performance is not None
