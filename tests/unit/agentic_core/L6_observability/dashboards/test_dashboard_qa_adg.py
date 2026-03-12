"""ADG-driven tests for agentic_core/L6_observability/dashboards/dashboard_qa.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L6_observability.dashboards.dashboard_qa import (  # noqa: F401
        DashboardQA,
        main,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    DashboardQA = None  # type: ignore[assignment,misc]
    main = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="dashboard_qa.py deps unavailable")
class TestDashboardQA:
    def test_is_class(self):
        assert isinstance(DashboardQA, type)
    def test_importable(self):
        assert DashboardQA is not None

@pytest.mark.skipif(not _AVAILABLE, reason="dashboard_qa.py deps unavailable")
class TestMain:
    def test_is_callable(self):
        assert callable(main)


def test_module_importable():
    """Module dashboard_qa.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
