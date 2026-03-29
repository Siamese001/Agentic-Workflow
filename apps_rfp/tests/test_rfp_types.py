"""
Test RFP Types.
"""
import unittest

from apps_rfp.types import (
    ProposalStatus,
    ArchitecturePosture,
    RiskSeverity,
    RoadmapPhase,
    RiskItem,
    AssumptionItem,
    ProposalSection,
    RfpRequest,
    RfpResult,
    RfpRunSummary,
)


class TestRfpTypes(unittest.TestCase):
    """Test cases for RFP types."""

    def test_proposal_status_enum(self):
        """Test ProposalStatus enum values."""
        self.assertEqual(ProposalStatus.PENDING.value, "pending")
        self.assertEqual(ProposalStatus.COMPLETE.value, "complete")
        self.assertEqual(ProposalStatus.FAILED.value, "failed")

    def test_architecture_posture_enum(self):
        """Test ArchitecturePosture enum values."""
        self.assertEqual(ArchitecturePosture.CLOUD_FIRST.value, "cloud-first")
        self.assertEqual(ArchitecturePosture.HYBRID.value, "hybrid")

    def test_risk_severity_enum(self):
        """Test RiskSeverity enum values."""
        self.assertEqual(RiskSeverity.LOW.value, "LOW")
        self.assertEqual(RiskSeverity.HIGH.value, "HIGH")
        self.assertEqual(RiskSeverity.CRITICAL.value, "CRITICAL")

    def test_roadmap_phase_creation(self):
        """Test RoadmapPhase dataclass creation."""
        phase = RoadmapPhase(
            phase_id="phase-001",
            name="Phase 1: Foundation",
            duration_weeks=4,
            objectives=("Setup", "Integration"),
            deliverables=("Doc", "Config"),
        )
        self.assertEqual(phase.phase_id, "phase-001")
        self.assertEqual(phase.duration_weeks, 4)

    def test_risk_item_creation(self):
        """Test RiskItem dataclass creation."""
        risk = RiskItem(
            risk_id="risk-001",
            category="Security",
            description="Data breach risk",
            severity=RiskSeverity.HIGH,
            mitigation="Encryption",
        )
        self.assertEqual(risk.risk_id, "risk-001")
        self.assertEqual(risk.severity, RiskSeverity.HIGH)

    def test_assumption_item_creation(self):
        """Test AssumptionItem dataclass creation."""
        assumption = AssumptionItem(
            assumption_id="asm-001",
            statement="Customer has existing cloud infra",
            basis="interview",
        )
        self.assertEqual(assumption.assumption_id, "asm-001")

    def test_proposal_section_creation(self):
        """Test ProposalSection dataclass creation."""
        section = ProposalSection(
            section_id="sec-001",
            heading="Executive Summary",
            body="Proposal overview...",
            word_count=500,
        )
        self.assertEqual(section.section_id, "sec-001")
        self.assertTrue(section.is_deterministic)

    def test_rfp_request_defaults(self):
        """Test RfpRequest default values."""
        request = RfpRequest()
        self.assertEqual(request.problem_statement, "")
        self.assertEqual(request.industry, "technology")
        self.assertEqual(request.architecture_posture, ArchitecturePosture.CLOUD_FIRST)
        self.assertFalse(request.dry_run)

    def test_rfp_result_passed_gate(self):
        """Test RfpResult.passed_gate property."""
        # Complete with no violations should pass
        result_pass = RfpResult(
            trace_id="trace-001",
            status=ProposalStatus.COMPLETE,
            gate_violations=[],
        )
        self.assertTrue(result_pass.passed_gate)

        # With violations should fail
        result_fail = RfpResult(
            trace_id="trace-002",
            status=ProposalStatus.COMPLETE,
            gate_violations=["violation-1"],
        )
        self.assertFalse(result_fail.passed_gate)

    def test_rfp_run_summary_to_dict(self):
        """Test RfpRunSummary.to_dict method."""
        summary = RfpRunSummary(
            trace_id="trace-001",
            app="apps_rfp",
            version="1.0.0",
            status="complete",
            industry="Healthcare",
            quality_score=0.92,
        )
        d = summary.to_dict()
        self.assertEqual(d["trace_id"], "trace-001")
        self.assertEqual(d["industry"], "Healthcare")


if __name__ == "__main__":
    unittest.main()
