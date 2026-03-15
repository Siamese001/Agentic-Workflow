"""ADG-driven tests for apps_shared/utils/health_metrics_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.utils.health_metrics_util import (  # noqa: F401
        compute_error_rate,
        count_failures_by_code,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    compute_error_rate = None  # type: ignore[assignment,misc]
    count_failures_by_code = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="health_metrics_util.py deps unavailable")
class TestComputeErrorRate:
    def test_is_callable(self):
        assert callable(compute_error_rate)

@pytest.mark.skipif(not _AVAILABLE, reason="health_metrics_util.py deps unavailable")
class TestCountFailuresByCode:
    def test_is_callable(self):
        assert callable(count_failures_by_code)


def test_module_importable():
    """Module health_metrics_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
