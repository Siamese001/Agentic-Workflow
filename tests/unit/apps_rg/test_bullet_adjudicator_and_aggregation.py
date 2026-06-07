"""req-12 + adjudicator/aggregation tests for the section-orchestration redesign.

Covers the prompt's required test list (the half not covered by
test_section_orchestration_dependency_order.py):
  * competencies category-count contract (locked at 6; '8' in the prompt was illustrative)
  * IBM metric drift hard rejected (forbidden HOLD/DO_NOT_PROMOTE metric scan)
  * Unify / exec unsupported claim hard rejected
  * optional adjudicator ONLY runs on tie / low-confidence / material-risk (not on confident pass)
  * X2 aggregation accept / reject paths
  * narratives require finalized bullet dependencies (upstream gate)
"""
from __future__ import annotations

from pathlib import Path

import pytest

from apps_rg.runtime.judges.bullet_adjudicator import (
    TRIGGER_JUDGE_CONFIDENCE_LOW,
    TRIGGER_METRIC_BULLET_BORDERLINE,
    TRIGGER_X2_PASS_JUDGE_RISK,
    evaluate_bullet_adjudicator_trigger,
)
from apps_rg.runtime.judges.bullet_x2_aggregation import (
    AGG_ACCEPT,
    AGG_BORDERLINE,
    AGG_REJECT_JUDGE,
    AGG_REJECT_X2,
    aggregate_bullet_section,
)


def _judge(score: float, threshold: float = 0.8, **kw) -> dict:
    base = {
        "provider_key": kw.pop("provider_key", "anthropic_claude"),
        "evaluator_mode": kw.pop("evaluator_mode", "MODEL_BACKED"),
        "normalized_score": score,
        "normalized_threshold": threshold,
        "pass": kw.pop("pass_", score >= threshold),
        "decisive_failure": kw.pop("decisive_failure", False),
    }
    base.update(kw)
    return base


# --------------------------------------------------------------- adjudicator: only on borderline
def test_adjudicator_does_not_escalate_on_confident_pass() -> None:
    d = evaluate_bullet_adjudicator_trigger(
        section_id="ibm_bullets",
        composite_judges=[_judge(0.95)],
        x2_failed_gate_ids=[],
        bullets=[{"bullet_id": "b1", "has_metric": True, "metric_raw": "30%"}],
    )
    assert d.should_escalate is False
    assert d.triggers == ()


def test_adjudicator_escalates_on_low_confidence_borderline() -> None:
    d = evaluate_bullet_adjudicator_trigger(
        section_id="ibm_bullets",
        composite_judges=[_judge(0.81)],  # within band of threshold 0.8
        x2_failed_gate_ids=[],
        bullets=[],
    )
    assert d.should_escalate is True
    assert TRIGGER_JUDGE_CONFIDENCE_LOW in d.triggers


def test_adjudicator_escalates_when_x2_passes_but_judge_flags_risk() -> None:
    d = evaluate_bullet_adjudicator_trigger(
        section_id="unify_bullets",
        composite_judges=[_judge(0.95, findings=["vague ai strategy fluff"])],
        x2_failed_gate_ids=[],
        bullets=[],
    )
    assert d.should_escalate is True
    assert TRIGGER_X2_PASS_JUDGE_RISK in d.triggers


def test_adjudicator_metric_bullet_borderline_trigger_is_ibm_only() -> None:
    judges = [_judge(0.81)]
    metric_bullets = [{"bullet_id": "b1", "has_metric": True, "metric_raw": "30%"}]
    ibm = evaluate_bullet_adjudicator_trigger(
        section_id="ibm_bullets", composite_judges=judges, x2_failed_gate_ids=[], bullets=metric_bullets
    )
    assert TRIGGER_METRIC_BULLET_BORDERLINE in ibm.triggers
    unify = evaluate_bullet_adjudicator_trigger(
        section_id="unify_bullets", composite_judges=judges, x2_failed_gate_ids=[], bullets=metric_bullets
    )
    # Unify gets the confidence trigger but NOT the IBM-specific metric trigger.
    assert TRIGGER_METRIC_BULLET_BORDERLINE not in unify.triggers


def test_adjudicator_no_escalation_when_x2_hard_fails_and_score_high() -> None:
    # X2 hard failure is handled by X3 BLOCK, not by adjudication; a confident judge + x2 fail
    # should not spuriously escalate on the X2-pass-judge-risk trigger.
    d = evaluate_bullet_adjudicator_trigger(
        section_id="ibm_bullets",
        composite_judges=[_judge(0.95)],
        x2_failed_gate_ids=["x2_ibm_metrics_preserved"],
        bullets=[],
    )
    assert TRIGGER_X2_PASS_JUDGE_RISK not in d.triggers


# --------------------------------------------------------------- X2 aggregation accept/reject
def test_aggregation_accepts_confident_pass() -> None:
    a = aggregate_bullet_section(
        section_id="ibm_bullets", composite_judges=[_judge(0.95)], x2_failed_gate_ids=[]
    )
    assert a.decision == AGG_ACCEPT
    assert a.accepted is True
    assert a.should_adjudicate is False


def test_aggregation_rejects_on_x2_hard_failure() -> None:
    a = aggregate_bullet_section(
        section_id="ibm_bullets",
        composite_judges=[_judge(0.99)],
        x2_failed_gate_ids=["x2_ibm_metrics_preserved"],
    )
    assert a.decision == AGG_REJECT_X2
    assert a.accepted is False


def test_aggregation_rejects_on_judge_decisive_failure() -> None:
    a = aggregate_bullet_section(
        section_id="ibm_bullets",
        composite_judges=[_judge(0.4, pass_=False, decisive_failure=True)],
        x2_failed_gate_ids=[],
    )
    assert a.decision == AGG_REJECT_JUDGE
    assert a.accepted is False


def test_aggregation_borderline_flags_adjudicate() -> None:
    # Above pass floor (0.72) but within margin_threshold (0.05) of its own threshold.
    a = aggregate_bullet_section(
        section_id="ibm_bullets",
        composite_judges=[_judge(0.82, threshold=0.8)],
        x2_failed_gate_ids=[],
    )
    assert a.decision == AGG_BORDERLINE
    assert a.accepted is True
    assert a.should_adjudicate is True


def test_aggregation_rejects_below_pass_threshold() -> None:
    a = aggregate_bullet_section(
        section_id="ibm_bullets",
        composite_judges=[_judge(0.5, threshold=0.4)],  # passes own threshold but below 0.72 floor
        x2_failed_gate_ids=[],
    )
    assert a.decision == AGG_REJECT_JUDGE
    assert a.accepted is False


# --------------------------------------------------------------- competencies category count (6)
def test_competencies_category_count_locked_at_six() -> None:
    from apps_rg.runtime.sections.competencies_rigor import (
        MAX_CATEGORY_COUNT,
        MIN_CATEGORY_COUNT,
        check_competencies_category_count,
    )

    # The prompt said "8" but the locked rigor contract is exactly 6.
    assert MIN_CATEGORY_COUNT == 6
    assert MAX_CATEGORY_COUNT == 6
    six = [{"category_label": f"C{i}", "terms": []} for i in range(6)]
    ok, _ = check_competencies_category_count(six)
    assert ok is True
    eight = [{"category_label": f"C{i}", "terms": []} for i in range(8)]
    bad, reason = check_competencies_category_count(eight)
    assert bad is False
    assert "category_count=8" in (reason or "")


# --------------------------------------------------------------- IBM metric drift hard rejected
def test_ibm_forbidden_hold_metric_hard_rejected() -> None:
    from apps_rg.runtime.sections.ibm_role_episode_evidence import scan_forbidden_metrics_in_text

    # $15M is a HOLD/DO_NOT_PROMOTE metric — must be detected in bullet text.
    hits = scan_forbidden_metrics_in_text("Drove a $15M cost reduction across the enterprise.")
    assert hits, "forbidden HOLD metric ($15M) must be detected"


def test_ibm_clean_text_has_no_forbidden_metric_hits() -> None:
    from apps_rg.runtime.sections.ibm_role_episode_evidence import scan_forbidden_metrics_in_text

    hits = scan_forbidden_metrics_in_text(
        "Led enterprise AI platform modernization for a global insurer."
    )
    assert not hits


# --------------------------------------------------------------- exec unsupported claim rejected
def test_exec_summary_unsupported_industry_claim_rejected() -> None:
    from apps_rg.runtime.validators.executive_summary_x2 import check_unsupported_industry_claims

    # Claim references an industry not present in any selected fact.
    ok, reason = check_unsupported_industry_claims(
        "Transformed healthcare delivery systems at national scale.",
        selected_facts=[{"claim_text": "Led insurance platform work", "achievement_summary": ""}],
    )
    assert ok is False
    assert "healthcare" in (reason or "").lower()


def test_exec_summary_supported_claim_passes() -> None:
    from apps_rg.runtime.validators.executive_summary_x2 import check_unsupported_industry_claims

    ok, _ = check_unsupported_industry_claims(
        "Led insurance platform modernization.",
        selected_facts=[{"claim_text": "insurance platform program", "achievement_summary": ""}],
    )
    assert ok is True


# --------------------------------------------------------------- narratives require finalized bullets
def test_narrative_upstream_gate_blocks_when_bullets_not_finalized(tmp_path: Path, monkeypatch) -> None:
    from apps_rg.runtime.validators import companion_bullet_finalization as cbf
    from apps_rg.runtime.runtime_proof_layout import MODULAR_R4_SECTIONS_ROOT_ENV

    # Force the non-test-harness product path so the gate actually evaluates (no waiver).
    monkeypatch.setattr(cbf, "companion_allow_legacy_stale_fallback", lambda: False)
    # Point the modular sections root at an empty dir => no accepted upstream bullets.
    monkeypatch.setenv(MODULAR_R4_SECTIONS_ROOT_ENV, str(tmp_path))
    status, upstream_lane, reason = cbf.evaluate_narrative_upstream_bullets_gate(
        "unify_narrative", repo=tmp_path
    )
    assert status == "BLOCKED"
    assert upstream_lane == "unify_bullets"


def test_narrative_upstream_gate_not_applicable_for_non_narrative() -> None:
    from apps_rg.runtime.validators.companion_bullet_finalization import (
        evaluate_narrative_upstream_bullets_gate,
    )

    status, _, _ = evaluate_narrative_upstream_bullets_gate("competencies")
    assert status == "NOT_APPLICABLE"
