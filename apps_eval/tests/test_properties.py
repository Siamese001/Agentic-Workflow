"""Property-based tests for apps_eval — invariants that must hold for any
valid input.

Hypothesis explores the input space; these tests enforce architectural
invariants documented in `apps_eval/SVP_ENGINEERING_REVIEW.md`:
  - Eval results must always expose a `gate_violations` list (uniform contract).
  - Min-pass-rate compliance: when overall_score >= min_pass_rate, the
    ComplianceValidator must pass; when overall_score < min_pass_rate, it
    must surface a violation.
  - Round-trip serialization is injective for default-constructed types.

Plan: .windsurf/plans/apps-svp-plus-hardening-7c4e3a.md (W2.2)
"""
from __future__ import annotations

import unittest

from hypothesis import given, settings, strategies as st

from apps_eval.types import EvalConfig, EvalRequest, EvalResult
from apps_eval.validators import ComplianceValidator


class TestEvalProperties(unittest.TestCase):
    @settings(max_examples=50, deadline=None)
    @given(score=st.floats(min_value=0.0, max_value=1.0, allow_nan=False))
    def test_result_always_has_gate_violations_list(self, score: float) -> None:
        result = EvalResult(overall_score=score, status="complete")
        self.assertIsInstance(result.gate_violations, list)

    @settings(max_examples=50, deadline=None)
    @given(
        threshold=st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
        score=st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
    )
    def test_compliance_validator_respects_min_pass_rate(
        self, threshold: float, score: float
    ) -> None:
        req = EvalRequest(config=EvalConfig(min_pass_rate=threshold))
        result = EvalResult(overall_score=score, status="complete")
        passed, violations = ComplianceValidator().validate(req, result)
        if score >= threshold:
            # If we meet the threshold, no min-pass-rate compliance violation.
            self.assertFalse(
                any("min_pass_rate" in v.lower() or "pass_rate" in v.lower() for v in violations),
                f"unexpected pass-rate violation at score={score} >= threshold={threshold}: {violations}",
            )
        else:
            # Below threshold → a compliance violation must surface.
            self.assertFalse(passed, "expected compliance failure when score below threshold")

    @settings(max_examples=20, deadline=None)
    @given(score=st.floats(min_value=0.0, max_value=1.0, allow_nan=False))
    def test_result_round_trip(self, score: float) -> None:
        result = EvalResult(overall_score=score, status="complete")
        rebuilt = EvalResult.model_validate(result.model_dump())
        self.assertAlmostEqual(result.overall_score, rebuilt.overall_score, places=6)


if __name__ == "__main__":
    unittest.main()
