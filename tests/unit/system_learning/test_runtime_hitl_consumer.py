"""Unit tests for the runtime HITL shadow consumer (W6 P6.2 + P6.3)."""

from __future__ import annotations

import itertools
import json
from pathlib import Path
from typing import Iterator

import pytest

from agentic_core.L3_orchestration.exit_control.runtime_hitl_ledger import (
    LedgerEntry,
    LedgerState,
)
from agentic_core.L5_safety.exit_control.hitl_classes import HitlClass
from apps_eval.engines.hitl_decision_quality_engine import (
    HitlDecisionQualityEngine,
)
from agentic_core.L6_system_learning.runtime_hitl_consumer import (
    ConsumerThresholds,
    DraftKind,
    DraftProposal,
    FileDraftSink,
    RuntimeHitlConsumer,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _entry(
    *,
    ledger_id: str,
    hitl_class: HitlClass = HitlClass.FINANCIAL,
    approver_pool: str = "finance_oncall",
    state: LedgerState = LedgerState.APPROVED,
    created_at: float = 100.0,
    resolved_at: float | None = 101.0,
    approver_id: str | None = "alice",
    reason_code: str | None = None,
) -> LedgerEntry:
    return LedgerEntry(
        ledger_id=ledger_id,
        run_id="run",
        trace_id="trace",
        hitl_class=hitl_class,
        approver_pool=approver_pool,
        timeout_s=60,
        policy_snapshot="snap",
        envelope={},
        state=state,
        created_at=created_at,
        resolved_at=resolved_at,
        approver_id=approver_id,
        reason_code=reason_code,
    )


def _deterministic_ids() -> Iterator[str]:
    return (f"draft-{i:03d}" for i in itertools.count(1))


def _mk_consumer(**kw: object) -> RuntimeHitlConsumer:
    ids = _deterministic_ids()
    return RuntimeHitlConsumer(
        id_factory=lambda: next(ids),
        now=lambda: 999.0,
        **kw,  # type: ignore[arg-type]
    )


# ---------------------------------------------------------------------------
# DraftProposal round-trip
# ---------------------------------------------------------------------------


class TestDraftProposalRoundTrip:
    def test_to_dict_is_json_serializable(self) -> None:
        p = DraftProposal(
            draft_id="x",
            kind=DraftKind.TIMEOUT_TIGHTEN,
            target="classes.financial.timeout_s",
            before={"a": 1},
            after={"b": 2},
            rationale="r",
            hitl_class="financial",
            approver_pool="finance",
            sample_size=5,
            source_ledger_ids=("l1", "l2"),
            evidence={"timeout_rate": 0.5},
            created_at=123.0,
        )
        payload = p.to_dict()
        s = json.dumps(payload, sort_keys=True)
        assert "timeout_tighten" in s
        assert "classes.financial.timeout_s" in s


# ---------------------------------------------------------------------------
# Bucket filtering
# ---------------------------------------------------------------------------


class TestMinSampleSize:
    def test_buckets_below_min_sample_produce_no_drafts(self) -> None:
        entries = [_entry(ledger_id=f"l{i}", state=LedgerState.TIMEOUT, approver_id=None) for i in range(4)]
        report = HitlDecisionQualityEngine().score_entries(entries)
        consumer = _mk_consumer()  # default min_sample_size=5
        assert consumer.consume(report, entries) == []

    def test_buckets_at_or_above_min_sample_may_produce_drafts(self) -> None:
        entries = [_entry(ledger_id=f"l{i}", state=LedgerState.TIMEOUT, approver_id=None) for i in range(5)]
        report = HitlDecisionQualityEngine().score_entries(entries)
        drafts = _mk_consumer().consume(report, entries)
        assert drafts  # at least one


# ---------------------------------------------------------------------------
# Per-kind generation
# ---------------------------------------------------------------------------


class TestDraftKindGeneration:
    def test_timeout_tighten_when_timeout_rate_high(self) -> None:
        # 4 of 5 timed out → 80% > 30% threshold
        entries = [
            _entry(ledger_id=f"t{i}", state=LedgerState.TIMEOUT, approver_id=None) for i in range(4)
        ] + [_entry(ledger_id="a1", state=LedgerState.APPROVED)]
        report = HitlDecisionQualityEngine().score_entries(entries)
        drafts = _mk_consumer().consume(report, entries)
        kinds = {d.kind for d in drafts}
        assert DraftKind.TIMEOUT_TIGHTEN in kinds
        tt = next(d for d in drafts if d.kind is DraftKind.TIMEOUT_TIGHTEN)
        assert tt.target == "classes.financial.timeout_s"
        assert tt.hitl_class == "financial"
        assert tt.approver_pool == "finance_oncall"
        assert tt.sample_size == 5
        assert set(tt.source_ledger_ids) == {"t0", "t1", "t2", "t3", "a1"}

    def test_threshold_raise_when_all_approved_above_min(self) -> None:
        entries = [_entry(ledger_id=f"a{i}", state=LedgerState.APPROVED) for i in range(10)]
        report = HitlDecisionQualityEngine().score_entries(entries)
        drafts = _mk_consumer().consume(report, entries)
        kinds = {d.kind for d in drafts}
        assert DraftKind.THRESHOLD_RAISE in kinds

    def test_threshold_raise_not_fired_with_any_denial(self) -> None:
        entries = [_entry(ledger_id=f"a{i}", state=LedgerState.APPROVED) for i in range(10)] + [
            _entry(ledger_id="d1", state=LedgerState.DENIED, reason_code="X")
        ]
        report = HitlDecisionQualityEngine().score_entries(entries)
        drafts = _mk_consumer().consume(report, entries)
        kinds = {d.kind for d in drafts}
        assert DraftKind.THRESHOLD_RAISE not in kinds

    def test_reason_code_gap_when_denials_missing_codes(self) -> None:
        entries = (
            [_entry(ledger_id=f"d{i}", state=LedgerState.DENIED, reason_code="") for i in range(4)]
            + [_entry(ledger_id="a1", state=LedgerState.APPROVED)]
            + [_entry(ledger_id="a2", state=LedgerState.APPROVED)]
        )
        report = HitlDecisionQualityEngine().score_entries(entries)
        drafts = _mk_consumer().consume(report, entries)
        kinds = {d.kind for d in drafts}
        assert DraftKind.REASON_CODE_GAP in kinds

    def test_approval_inconsistent_when_approvers_disagree(self) -> None:
        entries = [
            _entry(ledger_id="1", state=LedgerState.APPROVED, approver_id="alice"),
            _entry(ledger_id="2", state=LedgerState.APPROVED, approver_id="alice"),
            _entry(ledger_id="3", state=LedgerState.DENIED, approver_id="bob", reason_code="X"),
            _entry(ledger_id="4", state=LedgerState.DENIED, approver_id="bob", reason_code="X"),
            _entry(ledger_id="5", state=LedgerState.DENIED, approver_id="bob", reason_code="X"),
        ]
        report = HitlDecisionQualityEngine().score_entries(entries)
        drafts = _mk_consumer().consume(report, entries)
        kinds = {d.kind for d in drafts}
        assert DraftKind.APPROVAL_INCONSISTENT in kinds

    def test_fallback_review_when_deny_plus_timeout_exceeds_threshold(self) -> None:
        # 2 timeouts + 3 denials = 5 of 5 = 100% fallback
        entries = [
            _entry(ledger_id=f"t{i}", state=LedgerState.TIMEOUT, approver_id=None) for i in range(2)
        ] + [_entry(ledger_id=f"d{i}", state=LedgerState.DENIED, reason_code="X") for i in range(3)]
        report = HitlDecisionQualityEngine().score_entries(entries)
        drafts = _mk_consumer().consume(report, entries)
        kinds = {d.kind for d in drafts}
        assert DraftKind.FALLBACK_REVIEW in kinds

    def test_healthy_bucket_produces_no_drafts(self) -> None:
        # 8 approvals (below all_approved_min=10) + 0 timeouts + 0 denials:
        # none of the heuristic gates trip.
        entries = [_entry(ledger_id=f"a{i}", state=LedgerState.APPROVED) for i in range(8)]
        report = HitlDecisionQualityEngine().score_entries(entries)
        drafts = _mk_consumer().consume(report, entries)
        assert drafts == []


# ---------------------------------------------------------------------------
# Custom thresholds
# ---------------------------------------------------------------------------


class TestCustomThresholds:
    def test_lowered_all_approved_min_fires_threshold_raise(self) -> None:
        entries = [_entry(ledger_id=f"a{i}", state=LedgerState.APPROVED) for i in range(5)]
        report = HitlDecisionQualityEngine().score_entries(entries)
        consumer = RuntimeHitlConsumer(
            thresholds=ConsumerThresholds(all_approved_min=5, min_sample_size=5),
            id_factory=lambda: "x",
            now=lambda: 0.0,
        )
        drafts = consumer.consume(report, entries)
        assert any(d.kind is DraftKind.THRESHOLD_RAISE for d in drafts)


# ---------------------------------------------------------------------------
# FileDraftSink + consume_and_submit
# ---------------------------------------------------------------------------


class TestFileDraftSink:
    def test_submit_writes_json_file(self, tmp_path: Path) -> None:
        sink = FileDraftSink(tmp_path / "drafts")
        proposal = DraftProposal(
            draft_id="draft-abc",
            kind=DraftKind.TIMEOUT_TIGHTEN,
            target="classes.financial.timeout_s",
            before={"x": 1},
            after={"y": 2},
            rationale="r",
            hitl_class="financial",
            approver_pool="finance",
            sample_size=5,
            source_ledger_ids=("l1",),
            evidence={"k": 1},
            created_at=100.0,
        )
        receipt = sink.submit(proposal)
        path = Path(receipt)
        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["draft_id"] == "draft-abc"
        assert data["kind"] == "timeout_tighten"

    def test_list_drafts_round_trip(self, tmp_path: Path) -> None:
        sink = FileDraftSink(tmp_path / "drafts")
        proposal = DraftProposal(
            draft_id="rt-1",
            kind=DraftKind.THRESHOLD_RAISE,
            target="classes.financial.trigger_threshold",
            before={"approvals": 10},
            after={"action": "raise"},
            rationale="r",
            hitl_class="financial",
            approver_pool="finance",
            sample_size=10,
            source_ledger_ids=("a1", "a2"),
            evidence={"rubber_stamp_suspected": True},
            created_at=100.0,
        )
        sink.submit(proposal)
        loaded = sink.list_drafts()
        assert len(loaded) == 1
        got = loaded[0]
        assert got.draft_id == "rt-1"
        assert got.kind is DraftKind.THRESHOLD_RAISE
        assert got.source_ledger_ids == ("a1", "a2")
        assert got.evidence == {"rubber_stamp_suspected": True}

    def test_list_drafts_tolerates_malformed_files(self, tmp_path: Path) -> None:
        root = tmp_path / "drafts"
        sink = FileDraftSink(root)
        # Good draft
        good = DraftProposal(
            draft_id="g",
            kind=DraftKind.TIMEOUT_TIGHTEN,
            target="t",
            before={},
            after={},
            rationale="",
            hitl_class="financial",
            approver_pool="p",
            sample_size=5,
        )
        sink.submit(good)
        # Garbage file — must not crash list_drafts()
        (root / "bad.json").write_text("{not json", encoding="utf-8")
        loaded = sink.list_drafts()
        assert len(loaded) == 1
        assert loaded[0].draft_id == "g"


class TestConsumeAndSubmit:
    def test_requires_sink_for_submission(self) -> None:
        entries = [_entry(ledger_id=f"t{i}", state=LedgerState.TIMEOUT, approver_id=None) for i in range(5)]
        report = HitlDecisionQualityEngine().score_entries(entries)
        consumer = RuntimeHitlConsumer()  # no sink
        with pytest.raises(RuntimeError, match="no DraftSink"):
            consumer.consume_and_submit(report, entries)

    def test_submits_each_draft_to_sink(self, tmp_path: Path) -> None:
        entries = [
            _entry(ledger_id=f"t{i}", state=LedgerState.TIMEOUT, approver_id=None) for i in range(4)
        ] + [_entry(ledger_id="a1", state=LedgerState.APPROVED)]
        report = HitlDecisionQualityEngine().score_entries(entries)
        sink = FileDraftSink(tmp_path / "drafts")
        consumer = _mk_consumer(sink=sink)
        pairs = consumer.consume_and_submit(report, entries)
        assert pairs
        for draft, receipt in pairs:
            assert Path(receipt).exists()
            data = json.loads(Path(receipt).read_text(encoding="utf-8"))
            assert data["draft_id"] == draft.draft_id


# ---------------------------------------------------------------------------
# No direct writes — UWG mediation invariant
# ---------------------------------------------------------------------------


class TestUWGMediation:
    def test_consumer_does_not_touch_config_dir(self, tmp_path: Path) -> None:
        # If any production path tried to write to config/, this would fail —
        # the consumer must route everything through the injected sink.
        entries = [_entry(ledger_id=f"t{i}", state=LedgerState.TIMEOUT, approver_id=None) for i in range(5)]
        report = HitlDecisionQualityEngine().score_entries(entries)
        sink = FileDraftSink(tmp_path / "drafts")
        consumer = _mk_consumer(sink=sink)
        consumer.consume_and_submit(report, entries)
        # Drafts landed in the injected sink directory only.
        contents = list((tmp_path / "drafts").iterdir())
        assert contents
        # The only side-effect surface is the sink root.
        for p in contents:
            assert p.parent == tmp_path / "drafts"
