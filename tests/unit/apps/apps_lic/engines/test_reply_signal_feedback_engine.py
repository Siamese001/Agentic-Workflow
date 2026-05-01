"""Unit tests for reply_signal_feedback_engine (W4-P10)."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from apps_lic.config.outreach_experiment_cells import (
    LATTICE_FINGERPRINT,
    cell_id,
)
from apps_lic.engines.reply_signal_feedback_engine import (
    DIM_PRIOR_DELTA,
    MIN_SAMPLES_FOR_PROMOTION,
    PROMOTE_PRIOR_DELTA,
    CellPosterior,
    CellVerdict,
    ReplyFeedbackLedger,
    ReplySignalFeedbackEngine,
    _wilson_ci,
)


@pytest.fixture
def engine() -> ReplySignalFeedbackEngine:
    return ReplySignalFeedbackEngine()


@pytest.fixture
def ledger() -> ReplyFeedbackLedger:
    return ReplyFeedbackLedger()


def _feed(
    engine: ReplySignalFeedbackEngine,
    ledger: ReplyFeedbackLedger,
    *,
    archetype: str,
    template: str,
    subject_variant: str,
    sends: int,
    replies: int,
) -> None:
    assert replies <= sends
    for i in range(sends):
        engine.record_event(
            ledger,
            archetype=archetype,
            template=template,
            subject_variant=subject_variant,
            replied=(i < replies),
        )


class TestLedgerBasics:
    def test_new_ledger_is_empty(self, ledger: ReplyFeedbackLedger) -> None:
        assert ledger.posteriors == {}
        assert ledger.lattice_fingerprint == LATTICE_FINGERPRINT

    def test_record_event_creates_posterior(
        self, engine: ReplySignalFeedbackEngine, ledger: ReplyFeedbackLedger
    ) -> None:
        engine.record_event(
            ledger,
            archetype="EXECUTIVE",
            template="initial",
            subject_variant="question",
            replied=True,
        )
        cid = cell_id("EXECUTIVE", "initial", "question")
        assert cid in ledger.posteriors
        p = ledger.posteriors[cid]
        assert p.sends == 1
        assert p.replies == 1

    def test_record_event_accumulates(
        self, engine: ReplySignalFeedbackEngine, ledger: ReplyFeedbackLedger
    ) -> None:
        _feed(
            engine,
            ledger,
            archetype="EXECUTIVE",
            template="initial",
            subject_variant="question",
            sends=10,
            replies=3,
        )
        cid = cell_id("EXECUTIVE", "initial", "question")
        p = ledger.posteriors[cid]
        assert p.sends == 10
        assert p.replies == 3
        assert p.unreplied == 7
        assert p.alpha == 4.0  # replies + 1
        assert p.beta == 8.0  # unreplied + 1

    def test_invalid_cell_raises(
        self, engine: ReplySignalFeedbackEngine, ledger: ReplyFeedbackLedger
    ) -> None:
        with pytest.raises(ValueError) as excinfo:
            engine.record_event(
                ledger,
                archetype="MARTIAN",
                template="initial",
                subject_variant="question",
                replied=False,
            )
        assert "Invalid cell" in str(excinfo.value)

    def test_invalid_template_raises(
        self, engine: ReplySignalFeedbackEngine, ledger: ReplyFeedbackLedger
    ) -> None:
        with pytest.raises(ValueError):
            engine.record_event(
                ledger,
                archetype="EXECUTIVE",
                template="does_not_exist",
                subject_variant="question",
                replied=False,
            )


class TestPosteriorMath:
    def test_posterior_mean_with_laplace(self) -> None:
        p = CellPosterior(cell_id="x", sends=0, replies=0)
        # Beta(1, 1) mean = 0.5
        assert p.posterior_mean == 0.5

    def test_posterior_mean_with_observations(self) -> None:
        p = CellPosterior(cell_id="x", sends=10, replies=3)
        # alpha = 4, beta = 8 -> mean = 4 / 12 = 0.333...
        assert p.posterior_mean == pytest.approx(4 / 12)


class TestWilsonCI:
    def test_zero_sends_returns_full_range(self) -> None:
        lo, hi = _wilson_ci(0, 0, 1.96)
        assert (lo, hi) == (0.0, 1.0)

    def test_all_success(self) -> None:
        lo, hi = _wilson_ci(100, 100, 1.96)
        assert lo > 0.95
        assert hi == pytest.approx(1.0)

    def test_all_failure(self) -> None:
        lo, hi = _wilson_ci(0, 100, 1.96)
        assert lo == 0.0
        assert hi < 0.05

    def test_interval_contains_empirical(self) -> None:
        lo, hi = _wilson_ci(30, 100, 1.96)
        assert lo <= 0.30 <= hi


class TestFleetBaseline:
    def test_empty_ledger_baseline(
        self, engine: ReplySignalFeedbackEngine, ledger: ReplyFeedbackLedger
    ) -> None:
        # Laplace: (0+1)/(0+2) = 0.5
        assert engine.fleet_baseline(ledger) == 0.5

    def test_baseline_reflects_pooled_rate(
        self, engine: ReplySignalFeedbackEngine, ledger: ReplyFeedbackLedger
    ) -> None:
        _feed(engine, ledger, archetype="EXECUTIVE", template="initial",
              subject_variant="question", sends=50, replies=5)
        _feed(engine, ledger, archetype="SENIOR_TA", template="initial",
              subject_variant="question", sends=50, replies=25)
        # Pooled: 30 replies / 100 sends, Laplace-smoothed: 31/102.
        assert engine.fleet_baseline(ledger) == pytest.approx(31 / 102)


class TestVerdicts:
    def test_insufficient_data(
        self, engine: ReplySignalFeedbackEngine, ledger: ReplyFeedbackLedger
    ) -> None:
        _feed(engine, ledger, archetype="EXECUTIVE", template="initial",
              subject_variant="question", sends=5, replies=3)
        cid = cell_id("EXECUTIVE", "initial", "question")
        v = engine.evaluate_cell(ledger, cid)
        assert v.verdict == "insufficient_data"
        assert v.prior_delta == 0.0

    def test_promote_on_strong_uplift(
        self, engine: ReplySignalFeedbackEngine, ledger: ReplyFeedbackLedger
    ) -> None:
        # Promoted cell: 40% reply.
        _feed(engine, ledger, archetype="EXECUTIVE", template="initial",
              subject_variant="question", sends=200, replies=80)
        # Baseline dragger: 5% reply across many other cells.
        _feed(engine, ledger, archetype="SENIOR_TA", template="initial",
              subject_variant="question", sends=200, replies=10)
        _feed(engine, ledger, archetype="RECRUITER", template="initial",
              subject_variant="question", sends=200, replies=10)
        cid = cell_id("EXECUTIVE", "initial", "question")
        v = engine.evaluate_cell(ledger, cid)
        assert v.verdict == "promote"
        assert v.prior_delta == PROMOTE_PRIOR_DELTA
        assert v.wilson_lower > v.fleet_baseline

    def test_dim_on_strong_downlift(
        self, engine: ReplySignalFeedbackEngine, ledger: ReplyFeedbackLedger
    ) -> None:
        # Dim cell: 1% reply.
        _feed(engine, ledger, archetype="EXECUTIVE", template="initial",
              subject_variant="question", sends=300, replies=3)
        # Baseline risers: 30% reply.
        _feed(engine, ledger, archetype="SENIOR_TA", template="initial",
              subject_variant="question", sends=200, replies=60)
        _feed(engine, ledger, archetype="RECRUITER", template="initial",
              subject_variant="question", sends=200, replies=60)
        cid = cell_id("EXECUTIVE", "initial", "question")
        v = engine.evaluate_cell(ledger, cid)
        assert v.verdict == "dim"
        assert v.prior_delta == DIM_PRIOR_DELTA
        assert v.wilson_upper < v.fleet_baseline

    def test_neutral_when_ci_overlaps(
        self, engine: ReplySignalFeedbackEngine, ledger: ReplyFeedbackLedger
    ) -> None:
        # All cells at same rate -> nobody outruns the pool.
        for archetype in ("EXECUTIVE", "SENIOR_TA", "RECRUITER"):
            _feed(engine, ledger, archetype=archetype, template="initial",
                  subject_variant="question", sends=100, replies=15)
        cid = cell_id("EXECUTIVE", "initial", "question")
        v = engine.evaluate_cell(ledger, cid)
        assert v.verdict == "neutral"
        assert v.prior_delta == 0.0


class TestEvaluateAll:
    def test_evaluate_all_only_returns_seen_cells(
        self, engine: ReplySignalFeedbackEngine, ledger: ReplyFeedbackLedger
    ) -> None:
        _feed(engine, ledger, archetype="EXECUTIVE", template="initial",
              subject_variant="question", sends=5, replies=1)
        verdicts = engine.evaluate_all(ledger)
        assert len(verdicts) == 1
        assert verdicts[0].cell_id == "EXECUTIVE.initial.question"

    def test_evaluate_all_sorted(
        self, engine: ReplySignalFeedbackEngine, ledger: ReplyFeedbackLedger
    ) -> None:
        _feed(engine, ledger, archetype="SENIOR_TA", template="initial",
              subject_variant="question", sends=5, replies=1)
        _feed(engine, ledger, archetype="EXECUTIVE", template="initial",
              subject_variant="question", sends=5, replies=1)
        verdicts = engine.evaluate_all(ledger)
        ids = [v.cell_id for v in verdicts]
        assert ids == sorted(ids)


class TestPriorDeltas:
    def test_empty_ledger_returns_empty_deltas(
        self, engine: ReplySignalFeedbackEngine, ledger: ReplyFeedbackLedger
    ) -> None:
        assert engine.emit_prior_deltas(ledger) == {}

    def test_insufficient_data_contributes_nothing(
        self, engine: ReplySignalFeedbackEngine, ledger: ReplyFeedbackLedger
    ) -> None:
        _feed(engine, ledger, archetype="EXECUTIVE", template="initial",
              subject_variant="question", sends=5, replies=1)
        deltas = engine.emit_prior_deltas(ledger)
        assert deltas == {}

    def test_promoted_cell_emits_axis_deltas(
        self, engine: ReplySignalFeedbackEngine, ledger: ReplyFeedbackLedger
    ) -> None:
        _feed(engine, ledger, archetype="EXECUTIVE", template="initial",
              subject_variant="question", sends=200, replies=80)
        _feed(engine, ledger, archetype="SENIOR_TA", template="initial",
              subject_variant="question", sends=200, replies=10)
        _feed(engine, ledger, archetype="RECRUITER", template="initial",
              subject_variant="question", sends=200, replies=10)
        deltas = engine.emit_prior_deltas(ledger)
        # EXECUTIVE archetype should get promote delta.
        assert "archetype:EXECUTIVE" in deltas
        assert deltas["archetype:EXECUTIVE"] == pytest.approx(PROMOTE_PRIOR_DELTA)
        # SENIOR_TA / RECRUITER should be dim.
        assert deltas["archetype:SENIOR_TA"] == pytest.approx(DIM_PRIOR_DELTA)
        # Template + subject_variant axes average across contributing cells.
        # 1 promote (+0.10), 2 dim (-0.10 each) -> mean = -0.0333...
        assert "template:initial" in deltas
        assert deltas["template:initial"] == pytest.approx((PROMOTE_PRIOR_DELTA + 2 * DIM_PRIOR_DELTA) / 3)

    def test_event_time_recorded(
        self, engine: ReplySignalFeedbackEngine, ledger: ReplyFeedbackLedger
    ) -> None:
        ts = datetime(2026, 5, 1, 12, 0, 0, tzinfo=timezone.utc)
        engine.record_event(
            ledger,
            archetype="EXECUTIVE",
            template="initial",
            subject_variant="question",
            replied=True,
            event_time_utc=ts,
        )
        cid = cell_id("EXECUTIVE", "initial", "question")
        assert ledger.posteriors[cid].last_updated_utc == ts


class TestMinSamplesThreshold:
    def test_just_below_threshold_insufficient(
        self, engine: ReplySignalFeedbackEngine, ledger: ReplyFeedbackLedger
    ) -> None:
        _feed(engine, ledger, archetype="EXECUTIVE", template="initial",
              subject_variant="question", sends=MIN_SAMPLES_FOR_PROMOTION - 1, replies=25)
        cid = cell_id("EXECUTIVE", "initial", "question")
        v = engine.evaluate_cell(ledger, cid)
        assert v.verdict == "insufficient_data"

    def test_at_threshold_evaluates(
        self, engine: ReplySignalFeedbackEngine, ledger: ReplyFeedbackLedger
    ) -> None:
        _feed(engine, ledger, archetype="EXECUTIVE", template="initial",
              subject_variant="question", sends=MIN_SAMPLES_FOR_PROMOTION, replies=15)
        cid = cell_id("EXECUTIVE", "initial", "question")
        v = engine.evaluate_cell(ledger, cid)
        assert v.verdict != "insufficient_data"
