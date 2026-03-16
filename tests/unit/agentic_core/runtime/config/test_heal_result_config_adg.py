"""ADG-driven tests for runtime/config/heal_result_config.py — fan_in=1."""
from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_heal_result_config_adg")
_emit_applies_guardrail("p0", "test_heal_result_config_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_heal_result_config_adg", "policy_binding")
_emit_snapshots_state("p0", "test_heal_result_config_adg", "state_snapshot")
emit_replay_key("p0", "test_heal_result_config_adg")
emit_determinism_digest("p0", "test_heal_result_config_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

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
