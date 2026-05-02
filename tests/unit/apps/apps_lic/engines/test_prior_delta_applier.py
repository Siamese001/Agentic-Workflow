"""Unit tests for prior_delta_applier (deferred follow-up #1)."""

from __future__ import annotations

import pytest

from apps_lic.config.outreach_experiment_cells import cell_id
from apps_lic.engines.prior_delta_applier import (
    PRIOR_SCORE_MAX,
    PRIOR_SCORE_MIN,
    PriorApplicationReport,
    PriorDeltaApplier,
)
from apps_lic.engines.reply_signal_feedback_engine import (
    ReplyFeedbackLedger,
    ReplySignalFeedbackEngine,
)


class _StubMessagePlanner:
    def __init__(self) -> None:
        self.section_templates: dict = {
            "subject": {"max_length": 60},
            "hook": {"max_length": 150},
        }


class _StubProfilePlanner:
    pass


def _populate_promote_dim_neutral(
    engine: ReplySignalFeedbackEngine, ledger: ReplyFeedbackLedger
) -> None:
    """Construct a ledger that produces a clear promote/dim/neutral mix."""
    # Promote: EXECUTIVE.initial.question 40% reply over 200.
    for i in range(200):
        engine.record_event(
            ledger,
            archetype="EXECUTIVE",
            template="initial",
            subject_variant="question",
            replied=(i < 80),
        )
    # Dim: SENIOR_TA.initial.question 5% reply over 200.
    for i in range(200):
        engine.record_event(
            ledger,
            archetype="SENIOR_TA",
            template="initial",
            subject_variant="question",
            replied=(i < 10),
        )
    # Dim: RECRUITER.initial.question 5% reply over 200.
    for i in range(200):
        engine.record_event(
            ledger,
            archetype="RECRUITER",
            template="initial",
            subject_variant="question",
            replied=(i < 10),
        )


class TestApplyArchetypeDeltas:
    def test_applies_to_profile_planner(self) -> None:
        engine = ReplySignalFeedbackEngine()
        ledger = ReplyFeedbackLedger()
        _populate_promote_dim_neutral(engine, ledger)
        applier = PriorDeltaApplier(engine=engine)
        profile = _StubProfilePlanner()
        report = applier.apply(ledger, profile_planner=profile)
        assert hasattr(profile, "archetype_prior_scores")
        assert "EXECUTIVE" in profile.archetype_prior_scores
        assert profile.archetype_prior_scores["EXECUTIVE"] > 0
        assert profile.archetype_prior_scores["SENIOR_TA"] < 0
        assert isinstance(report, PriorApplicationReport)
        assert "EXECUTIVE" in report.archetype_updates

    def test_skipped_when_profile_planner_missing(self) -> None:
        engine = ReplySignalFeedbackEngine()
        ledger = ReplyFeedbackLedger()
        _populate_promote_dim_neutral(engine, ledger)
        applier = PriorDeltaApplier(engine=engine)
        report = applier.apply(ledger)  # no planners passed
        skipped_axes = {axis for axis, _ in report.skipped}
        assert any(a.startswith("archetype:") for a in skipped_axes)


class TestApplyTemplateDeltas:
    def test_applies_to_message_planner_cadence_priors(self) -> None:
        engine = ReplySignalFeedbackEngine()
        ledger = ReplyFeedbackLedger()
        _populate_promote_dim_neutral(engine, ledger)
        applier = PriorDeltaApplier(engine=engine)
        planner = _StubMessagePlanner()
        applier.apply(ledger, message_planner=planner)
        # Section_templates structure preserved.
        assert "subject" in planner.section_templates
        assert "hook" in planner.section_templates
        # Cadence priors namespaced under a separate attribute.
        assert hasattr(planner, "cadence_prior_scores")
        assert "initial" in planner.cadence_prior_scores

    def test_section_templates_not_mutated(self) -> None:
        engine = ReplySignalFeedbackEngine()
        ledger = ReplyFeedbackLedger()
        _populate_promote_dim_neutral(engine, ledger)
        applier = PriorDeltaApplier(engine=engine)
        planner = _StubMessagePlanner()
        before_sections = dict(planner.section_templates)
        applier.apply(ledger, message_planner=planner)
        assert planner.section_templates == before_sections


class TestApplySubjectVariantDeltas:
    def test_applies_to_priors_map(self) -> None:
        engine = ReplySignalFeedbackEngine()
        ledger = ReplyFeedbackLedger()
        _populate_promote_dim_neutral(engine, ledger)
        applier = PriorDeltaApplier(engine=engine)
        priors: dict[str, float] = {}
        applier.apply(ledger, subject_variant_priors=priors)
        assert "question" in priors


class TestClamp:
    def test_clamp_extreme_positive(self) -> None:
        # Construct a ledger whose deltas exceed +1.0 by hand. Since the
        # engine's PROMOTE_PRIOR_DELTA is 0.10, we cannot exceed 1.0
        # via real verdicts. Instead, verify clamp logic directly with a
        # synthetic engine that returns a too-large delta.
        class _StubEngine:
            def emit_prior_deltas(self, ledger):
                return {
                    "archetype:EXECUTIVE": 5.0,
                    "archetype:SENIOR_TA": -7.0,
                    "template:initial": 0.5,
                }

        applier = PriorDeltaApplier(engine=_StubEngine())  # type: ignore[arg-type]
        profile = _StubProfilePlanner()
        planner = _StubMessagePlanner()
        report = applier.apply(
            ReplyFeedbackLedger(),
            profile_planner=profile,
            message_planner=planner,
        )
        assert profile.archetype_prior_scores["EXECUTIVE"] == PRIOR_SCORE_MAX
        assert profile.archetype_prior_scores["SENIOR_TA"] == PRIOR_SCORE_MIN
        # template 0.5 is in-range.
        assert planner.cadence_prior_scores["initial"] == 0.5
        clamped_axes = {axis for axis, _, _ in report.clamp_events}
        assert "archetype:EXECUTIVE" in clamped_axes
        assert "archetype:SENIOR_TA" in clamped_axes


class TestIdempotency:
    def test_repeat_apply_same_ledger_yields_same_state(self) -> None:
        engine = ReplySignalFeedbackEngine()
        ledger = ReplyFeedbackLedger()
        _populate_promote_dim_neutral(engine, ledger)
        applier = PriorDeltaApplier(engine=engine)
        profile = _StubProfilePlanner()
        applier.apply(ledger, profile_planner=profile)
        snapshot_1 = dict(profile.archetype_prior_scores)
        applier.apply(ledger, profile_planner=profile)
        snapshot_2 = dict(profile.archetype_prior_scores)
        assert snapshot_1 == snapshot_2


class TestEmptyLedger:
    def test_empty_ledger_produces_empty_report(self) -> None:
        applier = PriorDeltaApplier()
        ledger = ReplyFeedbackLedger()
        report = applier.apply(
            ledger,
            message_planner=_StubMessagePlanner(),
            profile_planner=_StubProfilePlanner(),
            subject_variant_priors={},
        )
        assert report.total_applied == 0
