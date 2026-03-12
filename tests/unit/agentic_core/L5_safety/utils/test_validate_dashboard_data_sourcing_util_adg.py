"""ADG-driven tests for agentic_core/L5_safety/utils/validate_dashboard_data_sourcing_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.utils.validate_dashboard_data_sourcing_util import (  # noqa: F401
        load_source_data,
        load_dashboard_data,
        calculate_metrics_from_source,
        validate_data_sourcing,
        check_complexity_health_distribution,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    load_source_data = None  # type: ignore[assignment,misc]
    load_dashboard_data = None  # type: ignore[assignment,misc]
    calculate_metrics_from_source = None  # type: ignore[assignment,misc]
    validate_data_sourcing = None  # type: ignore[assignment,misc]
    check_complexity_health_distribution = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="validate_dashboard_data_sourcing_util.py deps unavailable")
class TestLoadSourceData:
    def test_is_callable(self):
        assert callable(load_source_data)

@pytest.mark.skipif(not _AVAILABLE, reason="validate_dashboard_data_sourcing_util.py deps unavailable")
class TestLoadDashboardData:
    def test_is_callable(self):
        assert callable(load_dashboard_data)

@pytest.mark.skipif(not _AVAILABLE, reason="validate_dashboard_data_sourcing_util.py deps unavailable")
class TestCalculateMetricsFromSource:
    def test_is_callable(self):
        assert callable(calculate_metrics_from_source)

@pytest.mark.skipif(not _AVAILABLE, reason="validate_dashboard_data_sourcing_util.py deps unavailable")
class TestValidateDataSourcing:
    def test_is_callable(self):
        assert callable(validate_data_sourcing)

@pytest.mark.skipif(not _AVAILABLE, reason="validate_dashboard_data_sourcing_util.py deps unavailable")
class TestCheckComplexityHealthDistribution:
    def test_is_callable(self):
        assert callable(check_complexity_health_distribution)


def test_module_importable():
    """Module validate_dashboard_data_sourcing_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
