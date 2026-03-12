"""ADG-driven tests for L5_safety/config/detection_signal_config.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L5_safety.config.detection_signal_config import (
    ImpactAssessment,
    ImpactScope,
    Severity,
)


class TestSeverity:
    def test_critical_highest(self):
        assert Severity.CRITICAL.value > Severity.HIGH.value

    def test_info_lowest(self):
        assert Severity.INFO.value == 0

    def test_has_all_levels(self):
        for level in ("CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"):
            assert hasattr(Severity, level)


class TestImpactScope:
    def test_system_wide_value(self):
        assert ImpactScope.SYSTEM_WIDE.value == "system_wide"

    def test_file_value(self):
        assert ImpactScope.FILE.value == "file"

    def test_has_all_scopes(self):
        for scope in ("SYSTEM_WIDE", "DOMAIN", "COMPONENT", "FILE", "ISOLATED"):
            assert hasattr(ImpactScope, scope)


class TestImpactAssessment:
    def test_importable(self):
        assert callable(ImpactAssessment)

    def test_creates_with_defaults(self):
        ia = ImpactAssessment()
        assert ia.scope == ImpactScope.FILE

    def test_creates_with_scope(self):
        ia = ImpactAssessment(scope=ImpactScope.COMPONENT)
        assert ia.scope == ImpactScope.COMPONENT

    def test_blast_radius_default_zero(self):
        ia = ImpactAssessment()
        assert ia.estimated_blast_radius == 0

    def test_recovery_complexity_default(self):
        ia = ImpactAssessment()
        assert ia.recovery_complexity == "low"

    def test_to_dict_returns_dict(self):
        ia = ImpactAssessment(scope=ImpactScope.DOMAIN)
        d = ia.to_dict()
        assert isinstance(d, dict)
        assert d["scope"] == "domain"
