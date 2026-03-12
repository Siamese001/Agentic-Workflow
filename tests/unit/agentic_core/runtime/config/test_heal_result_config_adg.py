"""ADG-driven tests for runtime/config/heal_result_config.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.runtime.config.heal_result_config import HealResult, HealStatus


class TestHealStatus:
    def test_success_value(self):
        assert HealStatus.SUCCESS.value == "SUCCESS"

    def test_error_value(self):
        assert HealStatus.ERROR.value == "ERROR"

    def test_all_statuses(self):
        for name in ("SUCCESS", "PARTIAL", "SKIPPED", "ERROR", "DRY_RUN", "UNKNOWN"):
            assert hasattr(HealStatus, name)


class TestHealResult:
    def test_creates_with_defaults(self):
        result = HealResult()
        assert result.violations_found == 0
        assert result.violations_fixed == 0
        assert result.status == HealStatus.UNKNOWN

    def test_creates_with_values(self):
        result = HealResult(
            violations_found=5,
            violations_fixed=3,
            status=HealStatus.PARTIAL,
        )
        assert result.violations_found == 5
        assert result.violations_fixed == 3
        assert result.status == HealStatus.PARTIAL

    def test_errors_default_zero(self):
        result = HealResult()
        assert result.errors == 0

    def test_details_default_empty(self):
        result = HealResult()
        assert result.details == []
