"""W8 wiring test: ApprovalGauntletEngine GAUNTLET_FALSE_PROMOTE_RATE KPI."""

from __future__ import annotations

import pytest

from system_learning.engines.approval_gauntlet_engine import ApprovalGauntletEngine
from system_learning.engines.v6_kpi_board import V6KPIBoard, V6KPIName


class TestPromotionCounters:
    def test_initial_counters_zero(self):
        engine = ApprovalGauntletEngine()
        assert engine.promotion_counters == (0, 0)

    def test_mark_promotion_increments_total(self):
        engine = ApprovalGauntletEngine()
        engine.mark_promotion()
        engine.mark_promotion()
        assert engine.promotion_counters == (0, 2)

    def test_mark_reversion_increments_reverted(self):
        engine = ApprovalGauntletEngine()
        engine.mark_promotion()
        engine.mark_reversion()
        assert engine.promotion_counters == (1, 1)

    def test_reset_clears_counters(self):
        engine = ApprovalGauntletEngine()
        engine.mark_promotion()
        engine.mark_reversion()
        engine.reset_promotion_counters()
        assert engine.promotion_counters == (0, 0)


class TestKpiPublication:
    def test_publishes_zero_with_no_promotions(self):
        engine = ApprovalGauntletEngine()
        board = V6KPIBoard()
        engine.publish_kpi_sample(board)
        sample = board.latest(V6KPIName.GAUNTLET_FALSE_PROMOTE_RATE)
        assert sample is not None
        # zero-total convention: ratio = 0.0
        assert sample.value == 0.0

    def test_publishes_correct_ratio(self):
        engine = ApprovalGauntletEngine()
        board = V6KPIBoard()
        for _ in range(99):
            engine.mark_promotion()
        engine.mark_promotion()  # 100th
        engine.mark_reversion()  # 1 reverted
        engine.publish_kpi_sample(board)
        sample = board.latest(V6KPIName.GAUNTLET_FALSE_PROMOTE_RATE)
        assert sample.value == pytest.approx(0.01)
        assert sample.source == "approval_gauntlet_engine"

    def test_publish_does_not_raise_with_invalid_board(self):
        engine = ApprovalGauntletEngine()
        engine.mark_promotion()
        # Pass an object with no record_value — must not raise.
        engine.publish_kpi_sample(object())
