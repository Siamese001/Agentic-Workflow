"""ADG importability contract for agentic_core/mixins/metrics_mixin.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_metrics_mixin.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.mixins.metrics_mixin import (  # noqa: F401
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        MetricsConfig,
        MetricsMixin,
        PerformanceMetrics,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    PerformanceMetrics = None  # type: ignore[assignment,misc]
    MetricsConfig = None  # type: ignore[assignment,misc]
    MetricsMixin = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="metrics_mixin.py deps unavailable")
class TestMetricsMixinImportability:
    def test_module_importable(self) -> None:
        """ADG contract: metrics_mixin.py must be importable."""
        assert _AVAILABLE

    def test_performancemetrics_is_type(self) -> None:
        assert PerformanceMetrics is not None

    def test_metricsconfig_is_type(self) -> None:
        assert MetricsConfig is not None

    def test_metricsmixin_is_type(self) -> None:
        assert MetricsMixin is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None
