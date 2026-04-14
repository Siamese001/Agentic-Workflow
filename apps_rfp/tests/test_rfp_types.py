"""
Test RFP Pydantic Types.
"""

import unittest

from pydantic import ValidationError

from apps_rfp.types import (
    AssumptionItem,
    ProposalSection,
    RfpConfig,
    RfpRequest,
    RfpResult,
    RfpRunSummary,
    RiskItem,
    RoadmapPhase,
)


class TestRoadmapPhase(unittest.TestCase):
    """Test cases for RoadmapPhase Pydantic model."""

    def test_phase_creation(self):
        """Test phase creation."""
        phase = RoadmapPhase(
            phase_id="phase-001",
            name="Discovery",
            duration_weeks=4,
            objectives=["Understand requirements"],
        )
        self.assertEqual(phase.phase_id, "phase-001")
        self.assertEqual(phase.duration_weeks, 4)

    def test_duration_bounds(self):
        """Test duration bounds (1-52 weeks)."""
        with self.assertRaises(ValidationError):
            RoadmapPhase(phase_id="p1", name="Test", duration_weeks=0)

        with self.assertRaises(ValidationError):
            RoadmapPhase(phase_id="p1", name="Test", duration_weeks=100)


class TestRiskItem(unittest.TestCase):
    """Test cases for RiskItem Pydantic model."""

    def test_risk_creation(self):
        """Test risk creation."""
        risk = RiskItem(
            risk_id="risk-001",
            category="security",
            description="Potential data breach vulnerability in authentication flow",
            severity="HIGH",
            mitigation="Implement multi-factor authentication and audit logging",
        )
        self.assertEqual(risk.risk_id, "risk-001")
        self.assertEqual(risk.severity, "HIGH")

    def test_description_validation(self):
        """Test description minimum length."""
        with self.assertRaises(ValidationError):
            RiskItem(
                risk_id="r1",
                category="test",
                description="short",
                severity="LOW",
                mitigation="Implement proper mitigation strategy here",
            )


class TestAssumptionItem(unittest.TestCase):
    """Test cases for AssumptionItem Pydantic model."""

    def test_assumption_creation(self):
        """Test assumption creation."""
        assumption = AssumptionItem(
            assumption_id="asm-001",
            statement="User base will grow 20% annually",
            basis="market analysis",
        )
        self.assertEqual(assumption.assumption_id, "asm-001")

    def test_statement_validation(self):
        """Test statement minimum length."""
        with self.assertRaises(ValidationError):
            AssumptionItem(assumption_id="a1", statement="x")


class TestProposalSection(unittest.TestCase):
    """Test cases for ProposalSection Pydantic model."""

    def test_section_creation(self):
        """Test section creation."""
        section = ProposalSection(
            section_id="sec-001",
            heading="Executive Summary",
            body="This is a comprehensive executive summary that meets the minimum length requirement for testing purposes.",
            word_count=150,
        )
        self.assertEqual(section.section_id, "sec-001")
        self.assertEqual(section.word_count, 150)

    def test_body_validation(self):
        """Test body minimum length (50 chars)."""
        with self.assertRaises(ValidationError):
            ProposalSection(section_id="s1", heading="Test", body="Too short")


class TestRfpConfig(unittest.TestCase):
    """Test cases for RfpConfig Pydantic model."""

    def test_config_defaults(self):
        """Test config default values."""
        config = RfpConfig()
        self.assertEqual(config.min_quality_score, 0.7)
        self.assertEqual(config.max_sections, 10)
        self.assertTrue(config.require_architecture_review)

    def test_quality_score_bounds(self):
        """Test quality score bounds."""
        with self.assertRaises(ValidationError):
            RfpConfig(min_quality_score=1.5)

    def test_max_sections_bounds(self):
        """Test max sections bounds."""
        with self.assertRaises(ValidationError):
            RfpConfig(max_sections=100)


class TestRfpRequest(unittest.TestCase):
    """Test cases for RfpRequest Pydantic model."""

    def test_request_creation(self):
        """Test request creation."""
        request = RfpRequest(
            problem_statement="We need to modernize our legacy infrastructure to support cloud-native workloads",
            industry="technology",
            architecture_posture="cloud-first",
        )
        self.assertEqual(request.industry, "technology")
        self.assertEqual(request.architecture_posture, "cloud-first")

    def test_problem_statement_validation(self):
        """Test problem statement minimum length."""
        with self.assertRaises(ValidationError):
            RfpRequest(problem_statement="Too short")

    def test_timeline_bounds(self):
        """Test delivery timeline bounds."""
        with self.assertRaises(ValidationError):
            RfpRequest(problem_statement="Valid problem statement here", delivery_timeline_weeks=200)


class TestRfpResult(unittest.TestCase):
    """Test cases for RfpResult Pydantic model."""

    def test_result_creation(self):
        """Test result creation."""
        result = RfpResult(
            trace_id="rfp-001",
            industry="technology",
            status="complete",
            quality_score=0.85,
        )
        self.assertEqual(result.trace_id, "rfp-001")
        self.assertEqual(result.quality_score, 0.85)

    def test_passed_gate_property(self):
        """Test passed_gate property."""
        result_pass = RfpResult(status="complete", gate_violations=[])
        self.assertTrue(result_pass.passed_gate)

        result_fail = RfpResult(status="complete", gate_violations=["error"])
        self.assertFalse(result_fail.passed_gate)

    def test_quality_score_bounds(self):
        """Test quality score bounds."""
        with self.assertRaises(ValidationError):
            RfpResult(quality_score=1.5)


class TestRfpRunSummary(unittest.TestCase):
    """Test cases for RfpRunSummary Pydantic model."""

    def test_summary_creation(self):
        """Test summary creation."""
        summary = RfpRunSummary(
            trace_id="trace-001",
            industry="technology",
            status="complete",
            sections_generated=8,
            quality_score=0.85,
        )
        self.assertEqual(summary.trace_id, "trace-001")
        self.assertEqual(summary.app, "apps_rfp")

    def test_to_dict(self):
        """Test to_dict method returns a dict with all required keys."""
        summary = RfpRunSummary(trace_id="trace-001", quality_score=0.85)
        d = summary.to_dict()
        self.assertIsInstance(d, dict)
        self.assertEqual(d["trace_id"], "trace-001")
        self.assertEqual(d["quality_score"], 0.85)
        self.assertEqual(d["app"], "apps_rfp")
        self.assertEqual(d["version"], "1.0.0")
        self.assertEqual(d["status"], "pending")
        self.assertIn("dry_run", d)
        self.assertIn("gate_violations", d)


if __name__ == "__main__":
    unittest.main()
