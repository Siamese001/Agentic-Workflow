"""Contract tests for DS-1 W4: citation_quality_judge + Spearman calibration.

Plan: .windsurf/plans/apps-research-deferred-scope-b7e3d2.md W4 (DS-1).

Acceptance criteria:
- citation_quality dim wired to non-stub grader in apps_research rubric.
- IS_STUB=False, IS_CALIBRATED=True, GRADER_ID is canonical roster ID.
- grade() returns (float, list[str]) on valid run_context.
- grade() returns GRADER_UNKNOWN_SENTINEL on empty output.
- Spearman rho >= 0.80 on 60-pair holdout.
- judge_agreement_tracker reports non-null holdout_comparison with citation_quality entry.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
HOLDOUT_PATH = REPO_ROOT / "apps_eval" / "fixtures" / "holdout" / "citation_quality_holdout.json"


# ---------------------------------------------------------------------------
# 4.1 Judge module contract
# ---------------------------------------------------------------------------

class TestCitationQualityJudgeModule:
    def test_is_not_stub(self):
        from apps_research.engines.judges.citation_quality_judge import IS_STUB
        assert IS_STUB is False

    def test_is_calibrated(self):
        from apps_research.engines.judges.citation_quality_judge import IS_CALIBRATED
        assert IS_CALIBRATED is True

    def test_grader_id_canonical(self):
        from apps_research.engines.judges.citation_quality_judge import GRADER_ID
        assert GRADER_ID == "research::citation_quality_judge::v1"

    def test_grade_returns_float_on_rich_context(self):
        from apps_research.engines.judges.citation_quality_judge import grade
        rc = {
            "output": {
                "factual_grounding": {"cited_count": 8, "uncited_count": 2},
                "retrieval_sources": [
                    {"url": "https://arxiv.org/abs/1234"},
                    {"url": "https://research.google.com/doc/5"},
                    {"url": "https://nature.com/articles/abc"},
                    {"url": "https://pubmed.ncbi.nlm.nih.gov/12345"},
                    {"url": "https://acm.org/paper/xyz"},
                ],
                "text": "[1] [2] [3] Research shows that models improve. [4] See also [5].",
            }
        }
        score, evidence = grade(None, rc)
        assert isinstance(score, float), f"Expected float, got {type(score)}"
        assert 0.0 <= score <= 1.0
        assert isinstance(evidence, list) and len(evidence) > 0

    def test_grade_returns_unknown_on_empty_output(self):
        from apps_research.engines.judges.citation_quality_judge import grade
        from agentic_core.L3_orchestration.exit_eval.v6.app_grader_registry import GRADER_UNKNOWN_SENTINEL
        score, evidence = grade(None, {})
        assert score == GRADER_UNKNOWN_SENTINEL

    def test_grade_returns_unknown_on_missing_data(self):
        from apps_research.engines.judges.citation_quality_judge import grade
        from agentic_core.L3_orchestration.exit_eval.v6.app_grader_registry import GRADER_UNKNOWN_SENTINEL
        score, _ = grade(None, {"output": {}})
        assert score == GRADER_UNKNOWN_SENTINEL

    def test_grade_high_quality_brief_scores_above_midpoint(self):
        from apps_research.engines.judges.citation_quality_judge import grade
        rc = {
            "output": {
                "factual_grounding": {"cited_count": 10, "uncited_count": 0},
                "retrieval_sources": [
                    {"url": "https://arxiv.org/abs/1"},
                    {"url": "https://nature.com/abc"},
                    {"url": "https://ieee.org/paper/1"},
                    {"url": "https://pubmed.ncbi.nlm.nih.gov/1"},
                    {"url": "https://acm.org/dl/1"},
                ],
                "text": "[1] [2] [3] [4] [5] All claims cited and cross-verified.",
            }
        }
        score, _ = grade(None, rc)
        assert score > 0.5, f"High-quality brief scored {score}, expected > 0.5"

    def test_grade_low_quality_brief_scores_below_high_quality(self):
        from apps_research.engines.judges.citation_quality_judge import grade
        high_rc = {
            "output": {
                "factual_grounding": {"cited_count": 10, "uncited_count": 0},
                "retrieval_sources": [{"url": f"https://domain{i}.com/"} for i in range(5)],
                "text": "[1] [2] [3] [4] [5] text.",
            }
        }
        low_rc = {
            "output": {
                "factual_grounding": {"cited_count": 1, "uncited_count": 9},
                "retrieval_sources": [{"url": "https://reddit.com/r/tech"}],
                "text": "No anchors here.",
            }
        }
        high_score, _ = grade(None, high_rc)
        low_score, _ = grade(None, low_rc)
        assert high_score > low_score, f"Expected high_score ({high_score}) > low_score ({low_score})"

    def test_judge_importable_from_package(self):
        from apps_research.engines.judges import CitationQualityJudge, grade, IS_STUB, GRADER_ID
        assert IS_STUB is False
        assert GRADER_ID == "research::citation_quality_judge::v1"


# ---------------------------------------------------------------------------
# 4.2 Rubric + grader roster registration
# ---------------------------------------------------------------------------

class TestCitationQualityRubricRegistration:
    def _load_rubric(self) -> dict:
        import yaml
        rubric_path = REPO_ROOT / "apps_research" / "config" / "domain_contract" / "eval_rubrics.yaml"
        with open(rubric_path, encoding="utf-8") as f:
            rubrics = yaml.safe_load(f)
        return rubrics[0]

    def _load_roster(self) -> dict:
        import yaml
        roster_path = REPO_ROOT / "apps_research" / "config" / "domain_contract" / "grader_roster.yaml"
        with open(roster_path, encoding="utf-8") as f:
            rosters = yaml.safe_load(f)
        return rosters[0]

    def test_citation_quality_dim_in_rubric(self):
        rubric = self._load_rubric()
        dim_ids = [d["dimension_id"] for d in rubric["score_dimensions"]]
        assert "citation_quality" in dim_ids, f"citation_quality not found in: {dim_ids}"

    def test_citation_quality_dim_grader_type(self):
        rubric = self._load_rubric()
        dim = next(d for d in rubric["score_dimensions"] if d["dimension_id"] == "citation_quality")
        assert dim["grader_type"] == "llm_as_judge"

    def test_citation_quality_dim_weight_positive(self):
        rubric = self._load_rubric()
        dim = next(d for d in rubric["score_dimensions"] if d["dimension_id"] == "citation_quality")
        assert dim["weight"] > 0.0

    def test_citation_quality_judge_in_grader_roster(self):
        roster = self._load_roster()
        assert "research::citation_quality_judge::v1" in roster["llm_judge_graders"]


# ---------------------------------------------------------------------------
# 4.3 Holdout fixture
# ---------------------------------------------------------------------------

class TestCitationQualityHoldout:
    def test_holdout_fixture_exists(self):
        assert HOLDOUT_PATH.exists(), f"Holdout fixture missing: {HOLDOUT_PATH}"

    def test_holdout_has_60_pairs(self):
        data = json.loads(HOLDOUT_PATH.read_text(encoding="utf-8"))
        assert data["n"] >= 60
        assert len(data["pairs"]) >= 60

    def test_holdout_schema_valid(self):
        data = json.loads(HOLDOUT_PATH.read_text(encoding="utf-8"))
        assert data["dim_id"] == "citation_quality"
        assert data["grader_id"] == "research::citation_quality_judge::v1"
        for p in data["pairs"]:
            assert "pair_id" in p
            assert "model_score" in p
            assert "human_label" in p
            assert 0.0 <= p["model_score"] <= 1.0
            assert 0.0 <= p["human_label"] <= 1.0

    def test_holdout_spearman_meets_threshold(self):
        try:
            from scipy.stats import spearmanr
        except ImportError:
            pytest.skip("scipy not available")
        data = json.loads(HOLDOUT_PATH.read_text(encoding="utf-8"))
        model_scores = [p["model_score"] for p in data["pairs"]]
        human_labels = [p["human_label"] for p in data["pairs"]]
        result = spearmanr(model_scores, human_labels)
        rho = float(result.statistic)
        assert rho >= 0.80, f"Spearman rho={rho:.4f} below 0.80 threshold"


# ---------------------------------------------------------------------------
# 4.4 judge_agreement_tracker integration
# ---------------------------------------------------------------------------

class TestJudgeAgreementTrackerPromotion:
    def test_is_skeleton_false(self):
        from ops_scripts.calibration.judge_agreement_tracker import IS_SKELETON
        assert IS_SKELETON is False

    def test_holdout_fixtures_registered(self):
        from ops_scripts.calibration.judge_agreement_tracker import HOLDOUT_FIXTURES
        assert len(HOLDOUT_FIXTURES) >= 1
        names = [p.name for p in HOLDOUT_FIXTURES]
        assert "citation_quality_holdout.json" in names

    def test_load_holdout_comparisons_returns_nonempty(self):
        from ops_scripts.calibration.judge_agreement_tracker import _load_holdout_comparisons
        results = _load_holdout_comparisons()
        assert len(results) >= 1

    def test_holdout_comparison_has_citation_quality(self):
        from ops_scripts.calibration.judge_agreement_tracker import _load_holdout_comparisons
        results = _load_holdout_comparisons()
        dim_ids = [r["dim_id"] for r in results]
        assert "citation_quality" in dim_ids

    def test_holdout_comparison_meets_threshold(self):
        from ops_scripts.calibration.judge_agreement_tracker import _load_holdout_comparisons
        results = _load_holdout_comparisons()
        cq = next(r for r in results if r["dim_id"] == "citation_quality")
        assert cq["meets_threshold"] is True, f"rho={cq['spearman_rho']:.4f} below threshold"

    def test_build_report_holdout_not_none(self):
        from ops_scripts.calibration.judge_agreement_tracker import build_report
        report = build_report()
        assert report["holdout_comparison"] is not None
        assert len(report["holdout_comparison"]) >= 1
