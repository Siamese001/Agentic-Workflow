"""Unit tests for HitlDecisionQualityEngine (W6 P6.1)."""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_core.L3_orchestration.exit_control.runtime_hitl_ledger import (
    LedgerEntry,
    LedgerState,
    RuntimeHitlLedger,
)
from agentic_core.L5_safety.exit_control.hitl_classes import HitlClass
from apps_eval.engines.hitl_decision_quality_engine import (
    HitlDecisionQualityEngine,
    HitlQualityReport,
    TARGET_P95_MS,
)


# ---------------------------------------------------------------------------
# LedgerEntry builders
# ---------------------------------------------------------------------------


def _entry(
    *,
    ledger_id: str = "l",
    hitl_class: HitlClass = HitlClass.FINANCIAL,
    approver_pool: str = "finance_oncall",
    state: LedgerState = LedgerState.APPROVED,
    created_at: float = 100.0,
    resolved_at: float | None = 101.0,
    approver_id: str | None = "alice",
    reason_code: str | None = None,
    timeout_s: int = 60,
) -> LedgerEntry:
    return LedgerEntry(
        ledger_id=ledger_id,
        run_id="run",
        trace_id="trace",
        hitl_class=hitl_class,
        approver_pool=approver_pool,
        timeout_s=timeout_s,
        policy_snapshot="snap",
        envelope={},
        state=state,
        created_at=created_at,
        resolved_at=resolved_at,
        approver_id=approver_id,
        reason_code=reason_code,
    )


# ---------------------------------------------------------------------------
# Empty / degenerate paths
# ---------------------------------------------------------------------------


class TestEmptyAndDegenerate:
    def test_empty_input_returns_unit_score(self) -> None:
        report = HitlDecisionQualityEngine().score_entries([])
        assert isinstance(report, HitlQualityReport)
        assert report.overall_score == 1.0
        assert report.total_entries == 0
        assert report.resolved_entries == 0
        assert report.buckets == ()

    def test_all_pending_entries_score_one(self) -> None:
        entries = [_entry(ledger_id=f"l{i}", state=LedgerState.PENDING, resolved_at=None) for i in range(3)]
        report = HitlDecisionQualityEngine().score_entries(entries)
        assert report.overall_score == 1.0
        assert report.resolved_entries == 0
        assert report.pending_entries == 3
        assert len(report.buckets) == 1
        bucket = report.buckets[0]
        assert bucket.pending_count == 3
        assert bucket.quality_score == 1.0


# ---------------------------------------------------------------------------
# Dimension math
# ---------------------------------------------------------------------------


class TestDimensions:
    def test_timeout_rate_lowers_score(self) -> None:
        # 3 of 5 timed out → timeout_rate = 0.6
        entries = [
            _entry(ledger_id="a", state=LedgerState.APPROVED),
            _entry(ledger_id="b", state=LedgerState.APPROVED),
            _entry(ledger_id="c", state=LedgerState.TIMEOUT, approver_id=None),
            _entry(ledger_id="d", state=LedgerState.TIMEOUT, approver_id=None),
            _entry(ledger_id="e", state=LedgerState.TIMEOUT, approver_id=None),
        ]
        report = HitlDecisionQualityEngine().score_entries(entries)
        bucket = report.buckets[0]
        assert bucket.dimensions.timeout_rate == pytest.approx(0.6)
        assert bucket.quality_score < 1.0
        # 0.35 × 0.6 = 0.21 timeout penalty; plus some consistency component
        assert bucket.quality_score <= 1.0 - 0.35 * 0.6 + 1e-9

    def test_reason_coverage_penalizes_missing_codes(self) -> None:
        entries = [
            _entry(ledger_id="a", state=LedgerState.DENIED, approver_id="a", reason_code=""),
            _entry(ledger_id="b", state=LedgerState.DENIED, approver_id="a", reason_code=""),
            _entry(ledger_id="c", state=LedgerState.DENIED, approver_id="a", reason_code="NC"),
        ]
        report = HitlDecisionQualityEngine().score_entries(entries)
        bucket = report.buckets[0]
        assert bucket.dimensions.reason_coverage == pytest.approx(1 / 3)
        # 0.25 * (1 - 1/3) = ~0.167 penalty
        assert bucket.quality_score < 1.0

    def test_approval_consistency_across_approvers(self) -> None:
        # alice always approves, bob always denies → stdev of rates = 0.5
        entries = [
            _entry(ledger_id="1", state=LedgerState.APPROVED, approver_id="alice"),
            _entry(ledger_id="2", state=LedgerState.APPROVED, approver_id="alice"),
            _entry(ledger_id="3", state=LedgerState.DENIED, approver_id="bob", reason_code="X"),
            _entry(ledger_id="4", state=LedgerState.DENIED, approver_id="bob", reason_code="X"),
        ]
        report = HitlDecisionQualityEngine().score_entries(entries)
        bucket = report.buckets[0]
        # pstdev([1.0, 0.0]) = 0.5; consistency = 1 - 0.5 = 0.5
        assert bucket.dimensions.approval_consistency == pytest.approx(0.5)

    def test_single_approver_consistency_is_one(self) -> None:
        entries = [
            _entry(ledger_id="1", state=LedgerState.APPROVED, approver_id="alice"),
            _entry(ledger_id="2", state=LedgerState.DENIED, approver_id="alice", reason_code="x"),
        ]
        report = HitlDecisionQualityEngine().score_entries(entries)
        assert report.buckets[0].dimensions.approval_consistency == 1.0

    def test_latency_quantiles(self) -> None:
        # Latencies: 1s, 2s, 3s, 4s, 10s (in ms)
        entries = [
            _entry(
                ledger_id=f"l{i}",
                state=LedgerState.APPROVED,
                created_at=0.0,
                resolved_at=latency_s,
            )
            for i, latency_s in enumerate([1.0, 2.0, 3.0, 4.0, 10.0])
        ]
        report = HitlDecisionQualityEngine().score_entries(entries)
        bucket = report.buckets[0]
        # nearest-rank: p50 at index ceil(0.5*5)-1 = 2 → 3000ms
        # p95 at index ceil(0.95*5)-1 = 4 → 10000ms
        assert bucket.dimensions.latency_p50_ms == 3000
        assert bucket.dimensions.latency_p95_ms == 10000

    def test_latency_penalty_caps_at_unity(self) -> None:
        # huge latency beyond TARGET_P95_MS → penalty capped
        entries = [
            _entry(
                ledger_id=f"l{i}",
                state=LedgerState.APPROVED,
                created_at=0.0,
                resolved_at=60 * 60 * 10.0,  # 10h each
            )
            for i in range(5)
        ]
        report = HitlDecisionQualityEngine().score_entries(entries)
        bucket = report.buckets[0]
        assert bucket.dimensions.latency_p95_ms >= TARGET_P95_MS
        # With all-approved, only latency penalty contributes (0.15)
        assert bucket.quality_score == pytest.approx(1.0 - 0.15)


# ---------------------------------------------------------------------------
# Bucketing + aggregation
# ---------------------------------------------------------------------------


class TestBucketing:
    def test_buckets_split_on_class_and_pool(self) -> None:
        entries = [
            _entry(ledger_id="f1", hitl_class=HitlClass.FINANCIAL, approver_pool="finance"),
            _entry(ledger_id="f2", hitl_class=HitlClass.FINANCIAL, approver_pool="finance"),
            _entry(ledger_id="r1", hitl_class=HitlClass.REGULATED, approver_pool="compliance"),
        ]
        report = HitlDecisionQualityEngine().score_entries(entries)
        assert len(report.buckets) == 2
        keys = {(b.hitl_class, b.approver_pool) for b in report.buckets}
        assert ("financial", "finance") in keys
        assert ("regulated", "compliance") in keys

    def test_overall_score_is_sample_weighted(self) -> None:
        # Bucket A: 10 approvals (score 1.0)
        # Bucket B: 2 timeouts (low score)
        entries_a = [
            _entry(
                ledger_id=f"a{i}",
                hitl_class=HitlClass.FINANCIAL,
                approver_pool="A",
                state=LedgerState.APPROVED,
            )
            for i in range(10)
        ]
        entries_b = [
            _entry(
                ledger_id=f"b{i}",
                hitl_class=HitlClass.FINANCIAL,
                approver_pool="B",
                state=LedgerState.TIMEOUT,
                approver_id=None,
            )
            for i in range(2)
        ]
        report = HitlDecisionQualityEngine().score_entries(entries_a + entries_b)
        # Weighted by resolved count (10 vs 2)
        a = next(b for b in report.buckets if b.approver_pool == "A")
        b = next(b for b in report.buckets if b.approver_pool == "B")
        expected = (a.quality_score * 10 + b.quality_score * 2) / 12
        assert report.overall_score == pytest.approx(expected)

    def test_policy_snapshot_captured_when_unambiguous(self) -> None:
        entries = [_entry(ledger_id=f"l{i}", state=LedgerState.APPROVED) for i in range(2)]
        report = HitlDecisionQualityEngine().score_entries(entries)
        assert report.policy_snapshot == "snap"

    def test_policy_snapshot_blank_when_mixed(self) -> None:
        mixed = [
            LedgerEntry(
                ledger_id=f"l{i}",
                run_id="r",
                trace_id="t",
                hitl_class=HitlClass.FINANCIAL,
                approver_pool="p",
                timeout_s=60,
                policy_snapshot=snap,
                envelope={},
                state=LedgerState.APPROVED,
                created_at=0.0,
                resolved_at=1.0,
                approver_id="a",
            )
            for i, snap in enumerate(("v1", "v2"))
        ]
        report = HitlDecisionQualityEngine().score_entries(mixed)
        assert report.policy_snapshot == ""


# ---------------------------------------------------------------------------
# Ledger-level API
# ---------------------------------------------------------------------------


class TestScoreLedger:
    def test_score_ledger_walks_pending(self, tmp_path: Path) -> None:
        ledger = RuntimeHitlLedger(tmp_path / "ledger.db")
        ledger.record_escalation(
            run_id="r1",
            trace_id="t1",
            hitl_class=HitlClass.FINANCIAL,
            approver_pool="finance",
            timeout_s=60,
            policy_snapshot="snap",
        )
        report = HitlDecisionQualityEngine().score_ledger(ledger)
        assert report.total_entries == 1
        assert report.pending_entries == 1
        assert report.overall_score == 1.0

    def test_score_ledger_filtered_by_run(self, tmp_path: Path) -> None:
        ledger = RuntimeHitlLedger(tmp_path / "ledger.db")
        for run_id in ("r1", "r2"):
            ledger.record_escalation(
                run_id=run_id,
                trace_id=run_id,
                hitl_class=HitlClass.FINANCIAL,
                approver_pool="finance",
                timeout_s=60,
                policy_snapshot="snap",
            )
        report = HitlDecisionQualityEngine().score_ledger(ledger, run_id_filter="r1")
        assert report.total_entries == 1


# ---------------------------------------------------------------------------
# Guard rails
# ---------------------------------------------------------------------------


class TestGuardRails:
    def test_rejects_nonpositive_target_p95(self) -> None:
        with pytest.raises(ValueError):
            HitlDecisionQualityEngine(target_p95_ms=0)
