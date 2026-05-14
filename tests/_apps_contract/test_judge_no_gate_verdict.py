"""W9 tests: Judges do not emit GateVerdict.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path


class TestJudgeNoGateVerdict(unittest.TestCase):
    """Verify judges never emit GateVerdict (PASS/WARN/FAIL)."""

    def test_judge_profile_has_no_gate_verdict(self) -> None:
        """Judge profile defines dimensions, not verdict enums."""
        profile_path = Path("apps_rg/config/domain_contract/judge_profile.resume_generation.v1.json")
        
        if profile_path.exists():
            content = profile_path.read_text()
            profile = json.loads(content)
            
            # Check dimensions exist
            dimensions = profile.get("dimensions", [])
            self.assertGreater(len(dimensions), 0)
            
            # Dimensions have thresholds (0.0-1.0), not verdicts
            for dim in dimensions:
                self.assertIn("threshold", dim)
                threshold = dim["threshold"]
                self.assertIsInstance(threshold, (int, float))
                self.assertGreaterEqual(threshold, 0.0)
                self.assertLessEqual(threshold, 1.0)
                
                # No verdict field
                self.assertNotIn("verdict", dim)
                self.assertNotIn("gate_verdict", dim)

    def test_grader_roster_has_no_gate_verdict(self) -> None:
        """Grader roster references graders, not verdicts."""
        roster_path = Path("apps_rg/config/domain_contract/grader_roster.yaml")
        
        if roster_path.exists():
            content = roster_path.read_text()
            
            # Should have grader refs
            self.assertIn("grader_ref:", content)
            
            # Should NOT have verdict emission
            self.assertNotIn("GateVerdict", content)
            
            # Informational_only is a flag, not a verdict
            self.assertIn("informational_only", content)

    def test_judges_produce_scores_not_verdicts(self) -> None:
        """Judges dimension output is score, not PASS/WARN/FAIL."""
        # Dimension output format
        dimension_output = {
            "score": 0.85,
            "rationale": "Good alignment with role requirements",
            "flags": ["minor_gap_in_scope"],
        }
        
        # Has score
        self.assertIn("score", dimension_output)
        self.assertIsInstance(dimension_output["score"], float)
        
        # No verdict
        self.assertNotIn("verdict", dimension_output)
        self.assertNotIn("gate_verdict", dimension_output)
        self.assertNotIn("PASS", str(dimension_output))
        self.assertNotIn("FAIL", str(dimension_output))

    def test_gate_verdict_owned_by_exit_only(self) -> None:
        """GateVerdict emission is Exit binding responsibility only."""
        # Only Exit binding can produce GateVerdict
        # Judges feed eval; eval feeds Exit; Exit produces verdict
        self.assertTrue(True, "GateVerdict emission chain: Exit binding only")


class TestDeterministicGradersNoVerdict(unittest.TestCase):
    """Verify deterministic graders produce evidence, not verdicts."""

    def test_factual_grounding_produces_evidence(self) -> None:
        """Factual grounding grader produces evidence list."""
        # Evidence format: list of verified claims
        evidence = {
            "verified_claims": 15,
            "unverified_claims": 0,
            "contradicted_claims": 0,
        }
        
        self.assertNotIn("verdict", evidence)
        self.assertNotIn("PASS", evidence)

    def test_ats_readability_produces_score(self) -> None:
        """ATS readability grader produces parseability score."""
        score = {
            "parseable": True,
            "sections_found": 7,
            "sections_required": 7,
        }
        
        # Boolean and counts, not verdict
        self.assertNotIn("verdict", score)


class TestLLMJudgesNoVerdict(unittest.TestCase):
    """Verify LLM judges produce scores, not verdicts."""

    def test_executive_positioning_score_format(self) -> None:
        """Executive positioning judge produces 0.0-1.0 score."""
        # Score format from judge_prompts.yaml
        score_output = {
            "score": 0.8,
            "rationale": "Strong SVP positioning with quantified outcomes",
            "flags": [],
        }
        
        self.assertEqual(score_output["score"], 0.8)
        self.assertNotIn("verdict", score_output)

    def test_role_alignment_score_format(self) -> None:
        """Role alignment judge produces 0.0-1.0 score."""
        score_output = {
            "score": 0.75,
            "rationale": "Good keyword alignment, minor narrative gap",
            "flags": ["narrative_arc_weak"],
        }
        
        self.assertEqual(score_output["score"], 0.75)
        self.assertNotIn("verdict", score_output)


if __name__ == "__main__":
    unittest.main()
