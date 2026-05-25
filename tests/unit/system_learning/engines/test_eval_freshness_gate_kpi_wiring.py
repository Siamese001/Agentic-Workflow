"""W6 wiring test: ``EvalFreshnessGate`` counters and KPI publication.

Asserts gate semantics are preserved and counters accurately track
fresh/total writes across a mix of blocked and allowed checks.
"""

from __future__ import annotations

import pytest

from agentic_core.L6_system_learning.eval_freshness_gate import (
    EvalFreshnessGate,
    FreshnessPolicy,
)
from agentic_core.L6_system_learning.v6_kpi_board import V6KPIBoard, V6KPIName


def _gate() -> EvalFreshnessGate:
    return EvalFreshnessGate(
        FreshnessPolicy.from_mapping(
            {
                "ttl_seconds": {"prompt": 3600.0},
                "default_on_unknown_class": "block",
                "fail_open": False,
                "schema": "test.v1",
                "version": 1,
                "fail_open_adr_ref": None,
            }
        )
    )


class TestCounters:
    def test_initial_counters_zero(self):
        fresh, total = _gate().write_counters
        assert fresh == 0
        assert total == 0

    def test_one_fresh_check_increments_both(self):
        gate = _gate()
        gate.check(change_class="prompt", eval_record_timestamp=0.0, now=10.0)
        assert gate.write_counters == (1, 1)

    def test_one_stale_check_increments_only_total(self):
        gate = _gate()
        # Age 7200s > TTL 3600s — blocked.
        gate.check(change_class="prompt", eval_record_timestamp=0.0, now=7200.0)
        assert gate.write_counters == (0, 1)

    def test_mixed_checks(self):
        gate = _gate()
        gate.check(change_class="prompt", eval_record_timestamp=0.0, now=10.0)
        gate.check(change_class="prompt", eval_record_timestamp=0.0, now=7200.0)
        gate.check(change_class="prompt", eval_record_timestamp=0.0, now=100.0)
        assert gate.write_counters == (2, 3)

    def test_reset_counters(self):
        gate = _gate()
        gate.check(change_class="prompt", eval_record_timestamp=0.0, now=10.0)
        gate.reset_counters()
        assert gate.write_counters == (0, 0)


class TestKpiPublication:
    def test_publish_records_ratio_to_board(self):
        gate = _gate()
        board = V6KPIBoard()
        gate.check(change_class="prompt", eval_record_timestamp=0.0, now=10.0)
        gate.check(change_class="prompt", eval_record_timestamp=0.0, now=7200.0)
        gate.publish_kpi_sample(board)
        sample = board.latest(V6KPIName.EVAL_FRESHNESS_ON_WRITE)
        assert sample is not None
        assert sample.value == pytest.approx(0.5)
        assert sample.source == "eval_freshness_gate"

    def test_publish_with_zero_checks_reports_vacuous_fresh(self):
        gate = _gate()
        board = V6KPIBoard()
        gate.publish_kpi_sample(board)
        sample = board.latest(V6KPIName.EVAL_FRESHNESS_ON_WRITE)
        assert sample is not None
        # zero-total convention from producers: vacuously 100% fresh
        assert sample.value == 1.0

    def test_gate_decisions_unchanged_by_kpi_wiring(self):
        """Regression: adding counters must NOT alter policy decisions."""
        gate = _gate()
        decision_fresh = gate.check(
            change_class="prompt", eval_record_timestamp=0.0, now=10.0
        )
        decision_stale = gate.check(
            change_class="prompt", eval_record_timestamp=0.0, now=7200.0
        )
        decision_missing = gate.check(
            change_class="prompt", eval_record_timestamp=None, now=10.0
        )
        assert decision_fresh.blocked is False
        assert decision_stale.blocked is True
        assert decision_missing.blocked is True
