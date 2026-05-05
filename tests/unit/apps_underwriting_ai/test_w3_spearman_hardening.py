"""W3 — Per-dim Spearman hardening tests.

Verifies the new dim-specific scoring signals added to rationale_quality_judge:
1. _score_feature_derivation — numeric formula / ratio signals
2. _score_extended_policy_citation — regulatory reference signals
3. _compute_score_for_dim — dim-aware routing (fdc / pc / baseline)
4. RationaleQualityJudge.grade — passes dim_id through for dim-aware scoring
"""
from __future__ import annotations

import pytest

from apps_underwriting_ai.engines.judges.rationale_quality_judge import (
    _score_feature_derivation,
    _score_extended_policy_citation,
    _compute_score_for_dim,
    RationaleQualityJudge,
)


# ---------------------------------------------------------------------------
# _score_feature_derivation
# ---------------------------------------------------------------------------

def test_fdc_numeric_hits_boost_score():
    text = "risk_dti: 38%. risk_ltv: 72%. risk_credit_score: 740 FICO."
    score = _score_feature_derivation(text)
    assert score > 0.0, f"Expected positive score, got {score}"


def test_fdc_formula_terms_boost_score():
    text = "risk_dti computed from total debt divided by monthly income."
    score = _score_feature_derivation(text)
    assert score > 0.0, f"Expected positive score, got {score}"


def test_fdc_no_signals_returns_zero():
    text = "Application reviewed."
    score = _score_feature_derivation(text)
    assert score == 0.0


def test_fdc_saturates_at_0_80():
    text = (
        "LTV ratio 72%. DTI ratio 38%. FICO score 740. Loan amount $320,000. "
        "Calculated as total debt divided by monthly income. Derived from bureau. "
        "Computed from appraised value and loan amount. Formula: principal balance "
        "divided by appraised value. Ratio of debt to income equals 0.38. "
        "Sum of monthly obligations: $2,850."
    )
    score = _score_feature_derivation(text)
    assert score <= 0.80, f"Signal should saturate at 0.80, got {score}"


# ---------------------------------------------------------------------------
# _score_extended_policy_citation
# ---------------------------------------------------------------------------

def test_policy_cite_detects_cfr():
    text = "Per 12 CFR part 1002, fair lending requirements satisfied."
    score = _score_extended_policy_citation(text)
    assert score > 0.0, f"Expected positive score, got {score}"


def test_policy_cite_detects_regulation_b():
    text = "Regulation B compliance confirmed. No adverse action required."
    score = _score_extended_policy_citation(text)
    assert score > 0.0, f"Expected positive score, got {score}"


def test_policy_cite_detects_tila():
    text = "TILA disclosure requirements met. APR clearly stated."
    score = _score_extended_policy_citation(text)
    assert score > 0.0


def test_policy_cite_detects_hmda():
    text = "HMDA reporting fields populated. No missing data."
    score = _score_extended_policy_citation(text)
    assert score > 0.0


def test_policy_cite_detects_ecoa():
    text = "ECOA compliance: all protected attributes excluded from decision."
    score = _score_extended_policy_citation(text)
    assert score > 0.0


def test_policy_cite_detects_policy_section():
    text = "Policy section 3.2 satisfied. Manual override per section 4.1 approved."
    score = _score_extended_policy_citation(text)
    assert score > 0.0


def test_policy_cite_no_signals_returns_zero():
    text = "Application reviewed. Decision: approve."
    score = _score_extended_policy_citation(text)
    assert score == 0.0


def test_policy_cite_saturates_at_0_60():
    text = (
        "12 CFR part 1002. Regulation B. ECOA compliance confirmed. "
        "TILA disclosure met. HMDA fields complete. Policy section 3.2. "
        "Ability to repay verified. Fair lending review passed. "
        "Fair credit reporting act requirements satisfied."
    )
    score = _score_extended_policy_citation(text)
    assert score <= 0.60, f"Should saturate at 0.60, got {score}"


# ---------------------------------------------------------------------------
# _compute_score_for_dim
# ---------------------------------------------------------------------------

def test_fdc_dim_uses_feature_derivation_signal():
    rich_fdc = (
        "risk_dti computed from verified income: DTI 38%. risk_credit_score from bureau: "
        "FICO 740. risk_ltv calculated from appraised value and loan amount: 72%. "
        "All risk_* features derived correctly."
    )
    poor_fdc = "Feature derivation complete."
    refs = ["features::risk_dti", "features::risk_credit"]

    rich_score = _compute_score_for_dim(rich_fdc, refs, "feature_derivation_correctness")
    poor_score = _compute_score_for_dim(poor_fdc, [], "feature_derivation_correctness")
    assert rich_score > poor_score, (
        f"Rich FDC rationale ({rich_score:.3f}) should score higher than poor ({poor_score:.3f})"
    )


def test_pc_dim_uses_extended_citation_signal():
    rich_pc = (
        "Policy review: PASS. 12 CFR part 1002 satisfied. ECOA compliance confirmed. "
        "Policy section 3.1 and 4.2 both satisfied. No violations detected."
    )
    poor_pc = "Policy check complete."
    refs = ["policy::pass"]

    rich_score = _compute_score_for_dim(rich_pc, refs, "policy_compliance")
    poor_score = _compute_score_for_dim(poor_pc, [], "policy_compliance")
    assert rich_score > poor_score, (
        f"Rich PC rationale ({rich_score:.3f}) should score higher than poor ({poor_score:.3f})"
    )


def test_baseline_dim_falls_through():
    text = "Decision approved based on verified income and good credit history."
    refs = ["income::verified"]
    baseline = _compute_score_for_dim(text, refs, "evidence_sufficiency")
    from apps_underwriting_ai.engines.judges.rationale_quality_judge import _compute_score
    direct = _compute_score(text, refs)
    assert abs(baseline - direct) < 1e-9, (
        f"Non-special dim should use baseline: got {baseline:.4f} vs {direct:.4f}"
    )


# ---------------------------------------------------------------------------
# RationaleQualityJudge.grade — dim_id forwarding
# ---------------------------------------------------------------------------

class _FakeDim:
    dimension_id: str

    def __init__(self, dim_id: str) -> None:
        self.dimension_id = dim_id


def test_grade_fdc_dim_routes_correctly():
    judge = RationaleQualityJudge()
    fdc_text = (
        "risk_dti computed from verified income: DTI 38%. risk_credit_score: FICO 740. "
        "risk_ltv calculated from appraised value and loan amount. All features validated."
    )
    ctx = {"output": {"rationale": fdc_text, "evidence_refs": ["features::risk_dti"]}}
    score, evidence = judge.grade(_FakeDim("feature_derivation_correctness"), ctx)
    assert 0.0 <= score <= 1.0
    assert any("dim=feature_derivation_correctness" in e for e in evidence)


def test_grade_pc_dim_routes_correctly():
    judge = RationaleQualityJudge()
    pc_text = (
        "Policy status: PASS. 12 CFR part 1002 satisfied. ECOA compliance confirmed. "
        "Policy section 3.1: passed. No violations detected."
    )
    ctx = {"output": {"rationale": pc_text, "evidence_refs": ["policy::pass"]}}
    score, evidence = judge.grade(_FakeDim("policy_compliance"), ctx)
    assert 0.0 <= score <= 1.0
    assert any("dim=policy_compliance" in e for e in evidence)


def test_grade_fdc_scores_higher_with_numeric_text():
    judge = RationaleQualityJudge()
    dim = _FakeDim("feature_derivation_correctness")

    rich = {"output": {"rationale": (
        "risk_dti 38% computed from verified monthly income $7,500 and total debt $2,850. "
        "risk_credit_score 740 FICO from Experian bureau report. "
        "risk_ltv 72% calculated from appraised value $320,000 and loan amount $230,000. "
        "All risk_* features derived and cross-validated."
    )}}
    poor = {"output": {"rationale": "Feature derivation complete. No errors."}}

    r_score, _ = judge.grade(dim, rich)
    p_score, _ = judge.grade(dim, poor)
    assert r_score > p_score, (
        f"Rich FDC rationale ({r_score:.3f}) should score higher than poor ({p_score:.3f})"
    )
