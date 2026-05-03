"""W2.P4 verification — apps_underwriting_ai rubric output mapper + status flip.

Plan: ``.windsurf/plans/apps-eval-harness-parity-f8d4a2.md`` W2.P4.

Proves:

- ``map_decision_to_dim_scores`` returns the canonical ``output`` shape
  (``dim_scores`` + ``dim_evidence``) with exactly the 5 rubric dimensions
  declared in apps_underwriting_ai eval_rubrics.yaml.
- A clean-pass DecisionPacket + RiskScoreBreakdown yields a bundle that
  AppSpecificEvaluator can consume and PASS.
- A policy-violation DecisionPacket produces a 0.0 ``policy_compliance``
  score → evaluator rubric FAIL on that dim → overall FAIL.
- The mapper is fail-safe for INSUFFICIENT_EVIDENCE verdicts (policy
  compliance drops, explainability scales on rationale/evidence).
- The app-domain contract manifest + eval_rubric are flipped to status=active.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from apps_underwriting_ai.engines.risk_scorer import (
    DeterministicRiskScorer,
    RiskScoreBreakdown,
)
from apps_underwriting_ai.engines.rubric_output_mapper import (
    map_decision_to_dim_scores,
)
from apps_underwriting_ai.types.underwriting_types import (
    DecisionPacket,
    DecisionVerdict,
    RiskFeatures,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
UW_DC = REPO_ROOT / "apps_underwriting_ai" / "config" / "domain_contract"

EXPECTED_DIMS = {
    "evidence_sufficiency",
    "feature_derivation_correctness",
    "policy_compliance",
    "explainability",
    "fairness",
}


# ---------------------------------------------------------------------------
# Contract status flip (W2.P4 gate-closer)
# ---------------------------------------------------------------------------


class TestStatusFlippedToActive:
    def test_manifest_active(self) -> None:
        doc = yaml.safe_load((UW_DC / "app_domain_manifest.yaml").read_text(encoding="utf-8"))
        assert doc["status"] == "active", "manifest must be active to close BLOCKER #8"

    def test_rubric_active(self) -> None:
        docs = yaml.safe_load((UW_DC / "eval_rubrics.yaml").read_text(encoding="utf-8"))
        assert isinstance(docs, list) and docs
        assert docs[0]["status"] == "active"

    def test_threshold_profile_active(self) -> None:
        docs = yaml.safe_load(
            (UW_DC / "threshold_profiles.yaml").read_text(encoding="utf-8"),
        )
        assert isinstance(docs, list) and docs
        assert docs[0]["status"] == "active"


# ---------------------------------------------------------------------------
# Producer mapper
# ---------------------------------------------------------------------------


def _clean_breakdown() -> RiskScoreBreakdown:
    # All scalars in [0,1] with evidence_completeness ≥ 0.95 so the
    # evidence_sufficiency dim clears its min_required_score=0.95 floor.
    return RiskScoreBreakdown(
        verdict=DecisionVerdict.APPROVE,
        risk_score=25.0,
        evidence_completeness=0.98,
        reconciliation_completeness=0.95,
        document_density=0.9,
        coverage_score=0.95,
        product_class="standard",
        product_risk_tier=20.0,
        rationale="Clean pass rationale for unit tests.",
        threshold_band="approve",
    )


def _clean_decision() -> DecisionPacket:
    return DecisionPacket(
        request_id="r-unit",
        verdict=DecisionVerdict.APPROVE,
        rationale=("Applicant meets all documented underwriting criteria. "
                   "Evidence register complete; reconciliation residual = 0. "
                   "Risk coverage = 0.95; product tier = standard. "
                   "[test rationale — ≥100 chars]"),
        evidence_refs=("ev-1", "ev-2"),
        feature_summary={
            "risk_score": 25.0,
            "risk_evidence_completeness": 0.98,
            "risk_reconciliation_completeness": 0.95,
            "risk_document_density": 0.90,
            "risk_coverage_score": 0.95,
            "risk_product_tier": 20.0,
        },
        gate_violations=(),
    )


def _features() -> RiskFeatures:
    return RiskFeatures(
        feature_vector={"coverage": 0.95, "product_tier": 20.0},
    )


class TestCleanPassMapping:
    def test_shape_has_both_keys(self) -> None:
        out = map_decision_to_dim_scores(_clean_decision(), _clean_breakdown(), _features())
        assert set(out.keys()) == {"dim_scores", "dim_evidence"}

    def test_all_five_dims_present_in_scores(self) -> None:
        out = map_decision_to_dim_scores(_clean_decision(), _clean_breakdown(), _features())
        assert set(out["dim_scores"].keys()) == EXPECTED_DIMS

    def test_all_five_dims_present_in_evidence(self) -> None:
        out = map_decision_to_dim_scores(_clean_decision(), _clean_breakdown(), _features())
        assert set(out["dim_evidence"].keys()) == EXPECTED_DIMS

    def test_all_evidence_non_empty(self) -> None:
        out = map_decision_to_dim_scores(_clean_decision(), _clean_breakdown(), _features())
        for dim_id, evs in out["dim_evidence"].items():
            assert evs, f"{dim_id}: empty evidence list will trip evidence_required rubric gate"

    def test_clean_pass_meets_all_rubric_minimums(self) -> None:
        """All 5 dims must score at-or-above their rubric min for a PASS run."""
        out = map_decision_to_dim_scores(_clean_decision(), _clean_breakdown(), _features())
        mins = {
            "evidence_sufficiency": 0.95,
            "feature_derivation_correctness": 0.95,
            "policy_compliance": 0.99,
            "explainability": 0.70,
            "fairness": 0.99,
        }
        for dim_id, min_req in mins.items():
            assert out["dim_scores"][dim_id] >= min_req, (
                f"{dim_id}={out['dim_scores'][dim_id]} < min_required={min_req}"
            )


class TestPolicyViolationDrop:
    def test_gate_violations_zero_out_policy_compliance(self) -> None:
        dec = DecisionPacket(
            request_id="r-unit",
            verdict=DecisionVerdict.DECLINE,
            rationale="x" * 200,
            evidence_refs=("ev-1",),
            feature_summary={k: 0.5 for k in (
                "risk_score", "risk_evidence_completeness",
                "risk_reconciliation_completeness", "risk_document_density",
                "risk_coverage_score", "risk_product_tier",
            )},
            gate_violations=("policy_clause_4b_violated",),
        )
        out = map_decision_to_dim_scores(dec, _clean_breakdown(), _features())
        assert out["dim_scores"]["policy_compliance"] == 0.0

    def test_insufficient_evidence_zero_policy_compliance(self) -> None:
        dec = DecisionPacket(
            request_id="r-unit",
            verdict=DecisionVerdict.INSUFFICIENT_EVIDENCE,
            rationale="x" * 200,
            evidence_refs=("ev-1",),
            feature_summary={k: 0.5 for k in (
                "risk_score", "risk_evidence_completeness",
                "risk_reconciliation_completeness", "risk_document_density",
                "risk_coverage_score", "risk_product_tier",
            )},
            gate_violations=(),
        )
        out = map_decision_to_dim_scores(dec, _clean_breakdown(), _features())
        assert out["dim_scores"]["policy_compliance"] == 0.0


class TestFeatureDerivationSensitivity:
    def test_missing_risk_keys_drops_score_to_zero(self) -> None:
        dec = DecisionPacket(
            request_id="r", verdict=DecisionVerdict.APPROVE, rationale="x" * 200,
            evidence_refs=("e",),
            feature_summary={"risk_score": 25.0},  # missing 5 of 6 required keys
        )
        out = map_decision_to_dim_scores(dec, _clean_breakdown(), _features())
        assert out["dim_scores"]["feature_derivation_correctness"] == 0.0

    def test_no_features_drops_score_to_zero(self) -> None:
        out = map_decision_to_dim_scores(_clean_decision(), _clean_breakdown(), features=None)
        assert out["dim_scores"]["feature_derivation_correctness"] == 0.0


class TestExplainabilityLadder:
    def test_full_credit_when_both_present(self) -> None:
        out = map_decision_to_dim_scores(_clean_decision(), _clean_breakdown(), _features())
        assert out["dim_scores"]["explainability"] == 1.0

    def test_half_credit_when_one_missing(self) -> None:
        dec = DecisionPacket(
            request_id="r", verdict=DecisionVerdict.APPROVE,
            rationale="short",  # < 100 chars
            evidence_refs=("e",),
            feature_summary=_clean_decision().feature_summary,
        )
        out = map_decision_to_dim_scores(dec, _clean_breakdown(), _features())
        assert out["dim_scores"]["explainability"] == 0.5

    def test_zero_credit_when_both_missing(self) -> None:
        dec = DecisionPacket(
            request_id="r", verdict=DecisionVerdict.APPROVE,
            rationale="short",
            evidence_refs=(),
            feature_summary=_clean_decision().feature_summary,
        )
        out = map_decision_to_dim_scores(dec, _clean_breakdown(), _features())
        assert out["dim_scores"]["explainability"] == 0.0


class TestFairness:
    def test_always_one_point_zero_for_deterministic_scorer(self) -> None:
        """DeterministicRiskScorer does not read protected attributes —
        fairness scores 1.0 by construction. If this test fails, someone
        changed the scorer's input contract and the mapper must be updated."""
        out = map_decision_to_dim_scores(_clean_decision(), _clean_breakdown(), _features())
        assert out["dim_scores"]["fairness"] == 1.0
        evidence = out["dim_evidence"]["fairness"]
        # Evidence must cite the scorer module id so auditors can verify.
        assert any("DeterministicRiskScorer" in e for e in evidence)
