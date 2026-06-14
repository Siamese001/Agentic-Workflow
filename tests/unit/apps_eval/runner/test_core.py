"""Wave 5 ADG testing-hotspots — apps_eval.runner.core pure helpers.

Substitution note: the plan listed ``apps_eval/engines/scenario_runner.py``
which does not exist. The nearest untested equivalent — the snapshot-first
scenario/eval runner — is ``apps_eval/runner/core.py``. The full ``run_eval``
needs on-disk fixtures/registries, so this module targets its *pure*
deterministic helpers: stable record-id hashing, the scorecard reducer
``_score`` (driven through the real thresholds registry), and
``compare_record_to_baseline`` regression verdict logic.
"""

from __future__ import annotations

import pytest

from apps_eval.contracts import GraderFinding
from apps_eval.runner.core import (
    _score,
    _stable_record_id,
    compare_record_to_baseline,
)


def _finding(grader_id: str, passed: bool, severity: str = "block", score: float = 1.0):
    return GraderFinding(
        grader_id=grader_id,
        scenario_id="sc1",
        passed=passed,
        severity=severity,
        score=score,
        message="",
    )


class TestStableRecordId:
    def test_deterministic_for_same_payload(self):
        a = _stable_record_id({"a": 1, "b": 2})
        b = _stable_record_id({"b": 2, "a": 1})  # key order irrelevant
        assert a == b

    def test_length_is_16_hex(self):
        rid = _stable_record_id({"x": 1})
        assert len(rid) == 16
        assert all(c in "0123456789abcdef" for c in rid)

    def test_differs_with_payload(self):
        assert _stable_record_id({"x": 1}) != _stable_record_id({"x": 2})


class TestCompareRecordToBaseline:
    def test_regression_when_current_lower(self):
        summary = compare_record_to_baseline(
            {"scorecard": {"score": 0.8}}, {"scorecard": {"score": 1.0}}
        )
        assert summary.verdict == "regression"
        assert summary.delta == pytest.approx(-0.2)
        assert summary.compared is True

    def test_pass_when_equal(self):
        summary = compare_record_to_baseline(
            {"scorecard": {"score": 1.0}}, {"scorecard": {"score": 1.0}}
        )
        assert summary.verdict == "pass"
        assert summary.delta == 0.0

    def test_pass_when_improved(self):
        summary = compare_record_to_baseline(
            {"scorecard": {"score": 1.0}}, {"scorecard": {"score": 0.5}}
        )
        assert summary.verdict == "pass"
        assert summary.delta == pytest.approx(0.5)

    def test_baseline_top_level_score_fallback(self):
        # Baseline may be a bare scorecard dict (no nested "scorecard" key).
        summary = compare_record_to_baseline(
            {"scorecard": {"score": 0.9}}, {"score": 0.9}
        )
        assert summary.verdict == "pass"
        assert summary.baseline_score == pytest.approx(0.9)


class TestScore:
    def test_all_pass_no_block_failures(self):
        findings = [_finding("schema", True), _finding("provenance", True)]
        card = _score("any_suite", "apps_rg", scenario_count=1, findings=findings)
        assert card.passed_findings == 2
        assert card.failed_findings == 0
        assert card.block_failures == 0
        assert card.score == 1.0

    def test_block_failure_forces_fail_verdict(self):
        findings = [_finding("schema", False, severity="block", score=0.0)]
        card = _score("any_suite", "apps_rg", scenario_count=1, findings=findings)
        assert card.block_failures == 1
        assert card.verdict == "fail"

    def test_warn_failure_not_counted_as_block(self):
        findings = [
            _finding("schema", True),
            _finding("length_bounds", False, severity="warn", score=0.0),
        ]
        card = _score("any_suite", "apps_rg", scenario_count=1, findings=findings)
        assert card.block_failures == 0
        assert card.passed_findings == 1
        assert card.failed_findings == 1

    def test_empty_findings_perfect_score(self):
        card = _score("any_suite", "apps_rg", scenario_count=0, findings=[])
        assert card.score == 1.0
        assert card.finding_count == 0

    def test_dimension_scores_averaged_per_grader(self):
        findings = [
            _finding("schema", True, score=1.0),
            _finding("schema", True, score=0.0),
            _finding("provenance", True, score=0.5),
        ]
        card = _score("any_suite", "apps_rg", scenario_count=1, findings=findings)
        assert card.dimension_scores["schema"] == pytest.approx(0.5)
        assert card.dimension_scores["provenance"] == pytest.approx(0.5)

    def test_score_is_passed_over_total(self):
        findings = [
            _finding("schema", True),
            _finding("provenance", False, severity="warn", score=0.0),
        ]
        card = _score("any_suite", "apps_rg", scenario_count=1, findings=findings)
        assert card.score == pytest.approx(0.5)
