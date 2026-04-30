"""Contract test seed for apps_eval.

Purpose: assert the public type contract holds — input request, config, result
all round-trip through Pydantic, the gate_violations field exists, and the
validator chain produces a structured (passed, violations) verdict.

This is a SEED — it does not exercise the full eval flow. The full
golden-corpus contract suite is W4.4 (deferred).

Plan: .windsurf/plans/apps-svp-plus-hardening-7c4e3a.md (W2.1)
"""
from __future__ import annotations

import unittest

from apps_eval.types import EvalConfig, EvalRequest, EvalResult
from apps_eval.validators import ComplianceValidator, QualityGateValidator


class TestApppsEvalContract(unittest.TestCase):
    """Contract assertions about the apps_eval public surface."""

    def test_default_request_round_trips(self) -> None:
        req = EvalRequest()
        dumped = req.model_dump()
        rebuilt = EvalRequest.model_validate(dumped)
        self.assertEqual(req.model_dump(), rebuilt.model_dump())

    def test_default_config_round_trips(self) -> None:
        cfg = EvalConfig()
        rebuilt = EvalConfig.model_validate(cfg.model_dump())
        self.assertEqual(cfg.model_dump(), rebuilt.model_dump())

    def test_default_result_has_gate_violations_field(self) -> None:
        result = EvalResult()
        self.assertTrue(
            hasattr(result, "gate_violations"),
            "Every domain Result MUST expose `gate_violations` per platform contract",
        )
        self.assertIsInstance(result.gate_violations, list)

    def test_compliance_validator_returns_tuple(self) -> None:
        passed, violations = ComplianceValidator().validate(
            EvalRequest(config=EvalConfig(min_pass_rate=0.0)),
            EvalResult(overall_score=1.0, status="complete"),
        )
        self.assertIsInstance(passed, bool)
        self.assertIsInstance(violations, list)
        self.assertEqual((passed, violations), (True, []))

    def test_quality_gate_validator_returns_tuple(self) -> None:
        passed, violations = QualityGateValidator(
            config={"min_scenarios": 0, "max_latency_ms": 10_000}
        ).validate(EvalResult(status="complete"))
        self.assertIsInstance(passed, bool)
        self.assertIsInstance(violations, list)

    def test_min_pass_rate_violation_surfaces(self) -> None:
        passed, violations = ComplianceValidator().validate(
            EvalRequest(config=EvalConfig(min_pass_rate=0.99)),
            EvalResult(overall_score=0.10, status="complete"),
        )
        self.assertFalse(passed)
        self.assertTrue(any("COMPLIANCE" in v for v in violations))


if __name__ == "__main__":
    unittest.main()
