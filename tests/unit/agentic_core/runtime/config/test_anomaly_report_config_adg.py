"""ADG-driven tests for runtime/config/anomaly_report_config.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.runtime.config.anomaly_report_config import (
    AnomalyReport,
    AnomalySeverity,
)


class TestAnomalySeverity:
    def test_low_value(self):
        assert AnomalySeverity.LOW.value == "low"

    def test_critical_value(self):
        assert AnomalySeverity.CRITICAL.value == "critical"

    def test_all_levels(self):
        for level in ("LOW", "MEDIUM", "HIGH", "CRITICAL"):
            assert hasattr(AnomalySeverity, level)


class TestAnomalyReport:
    def test_creates(self):
        report = AnomalyReport(
            type="test_anomaly",
            severity=AnomalySeverity.LOW,
            description="Test description",
            source="TestAgent",
        )
        assert report.type == "test_anomaly"
        assert report.severity == AnomalySeverity.LOW

    def test_frozen_immutable(self):
        report = AnomalyReport(
            type="test",
            severity=AnomalySeverity.HIGH,
            description="desc",
            source="Agent",
        )
        with pytest.raises(Exception):
            report.type = "modified"

    def test_details_default_empty(self):
        report = AnomalyReport(
            type="test",
            severity=AnomalySeverity.MEDIUM,
            description="desc",
            source="Agent",
        )
        assert report.details == {}
