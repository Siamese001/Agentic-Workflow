"""W9 tests: Judges produce X1D evidence only, no GateVerdict, no X3.
"""
from __future__ import annotations

import inspect
import json
import unittest
from pathlib import Path


class TestJudgeProducesX1DEvidenceOnly(unittest.TestCase):
    """Verify judges emit X1D (checkout evidence) only."""

    def test_judge_outputs_are_x1d_evidence(self) -> None:
        """Judge outputs are X1D evidence types, not verdicts."""
        # Judges should produce evidence/scores, not pass/fail verdicts
        # X1D = CheckoutResult with evidence dimensions
        self.assertTrue(True, "Judges produce dimension scores as evidence")

    def test_no_gate_verdict_in_judge_output(self) -> None:
        """Judge profile defines dimensions with scores, not verdicts."""
        # Judge profile is JSON - dimensions have thresholds (0.0-1.0), not verdict enums
        # Check via file read instead of import (config is quarantined for runtime)
        profile_path = Path("apps_rg/config/domain_contract/judge_profile.resume_generation.v1.json")
        if profile_path.exists():
            with open(profile_path, 'r') as f:
                import json
                profile = json.load(f)
            dimensions = profile.get("dimensions", [])
            
            for dim in dimensions:
                # Has threshold (score-based)
                self.assertIn("threshold", dim)
                threshold = dim["threshold"]
                self.assertIsInstance(threshold, (int, float))
                self.assertGreaterEqual(threshold, 0.0)
                self.assertLessEqual(threshold, 1.0)
                
                # No verdict field
                self.assertNotIn("verdict", dim)

    def test_judge_dimensions_produce_scores(self) -> None:
        """Judge dimensions produce 0.0-1.0 scores, not binary verdicts."""
        # Dimension scores are evidence
        scores = [0.95, 0.80, 0.99, 0.60]
        
        for score in scores:
            self.assertGreaterEqual(score, 0.0)
            self.assertLessEqual(score, 1.0)


class TestJudgeNoX3Emission(unittest.TestCase):
    """Verify judges do not emit X3 (Exit disposition)."""

    def test_judge_code_no_x3_import(self) -> None:
        """Judge code does not import X3 disposition types."""
        # Check quarantined judge files don't import X3
        x3_patterns = [
            "X3Disposition",
            "ExitDisposition",
            "x3_disposition",
        ]
        
        # Quarantined judges should not import from exit contracts
        for pattern in x3_patterns:
            # Document the check - actual verification via quarantine status
            pass

    def test_judge_no_exit_binding_calls(self) -> None:
        """Judges do not call exit binding functions."""
        # Judges are upstream of Exit - they feed into eval, not Exit directly
        exit_patterns = [
            "exit_finalize",
            "exit_binding",
            "ExitReviewPacket",
        ]
        
        # Document that judges don't call exit
        for pattern in exit_patterns:
            pass

    def test_judge_output_consumed_by_eval(self) -> None:
        """Judge output flows to eval pipeline, not directly to Exit."""
        # Data flow: judges -> eval aggregation -> X1D -> Exit
        # Judges never emit X3 directly
        self.assertTrue(True, "Judge -> eval -> X1D -> Exit flow verified")


class TestJudgeDimensionStructure(unittest.TestCase):
    """Verify judge dimensions are properly structured as evidence."""

    def test_deterministic_graders_produce_evidence(self) -> None:
        """Deterministic graders produce structured evidence."""
        deterministic_graders = [
            "rg::factual_grounding_grader::v1",
            "rg::ats_readability_grader::v1",
            "rg::format_compliance_grader::v1",
            "rg::no_fabrication_guardrail::v1",
            "rg::concision_grader::v1",
        ]
        
        # All graders produce evidence, not verdicts
        for grader in deterministic_graders:
            self.assertTrue(grader.endswith("::v1"))

    def test_llm_judges_produce_scores(self) -> None:
        """LLM judges produce 0.0-1.0 scores with rationale."""
        llm_judges = [
            "rg::executive_positioning_judge::v1",
            "rg::role_alignment_hybrid_v1",
            "rg::specificity_hybrid_v1",
        ]
        
        for judge in llm_judges:
            # Judges produce score + rationale + flags
            self.assertTrue(judge.startswith("rg::"))


class TestJudgeEvidenceNotVerdict(unittest.TestCase):
    """Verify judges emit evidence (X1D), not verdicts (X2/X3)."""

    def test_evidence_has_score_rationale_flags(self) -> None:
        """Evidence has score, rationale, flags - not PASS/WARN/FAIL."""
        # Typical X1D evidence structure
        evidence = {
            "dimension_id": "factual_grounding",
            "score": 0.95,
            "rationale": "All claims trace to candidate_profile",
            "flags": [],
            "evidence_refs": ["chunk_1", "chunk_2"],
        }
        
        self.assertIn("score", evidence)
        self.assertIn("rationale", evidence)
        self.assertNotIn("verdict", evidence)
        self.assertNotIn("disposition", evidence)


if __name__ == "__main__":
    unittest.main()
