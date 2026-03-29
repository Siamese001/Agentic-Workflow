"""
Test Exec Types.
"""
import unittest

from apps_exec.types import (
    AudiencePersona,
    BriefTone,
    EmphasisArea,
    BriefStatus,
    CapabilityEvidence,
    BriefSection,
    ExecBriefRequest,
    ExecBriefResult,
    StyleViolation,
    RunSummary,
)


class TestExecTypes(unittest.TestCase):
    """Test cases for exec types."""

    def test_audience_persona_enum(self):
        """Test AudiencePersona enum values."""
        self.assertEqual(AudiencePersona.RECRUITER.value, "recruiter")
        self.assertEqual(AudiencePersona.CTO.value, "cto")
        self.assertEqual(AudiencePersona.SVP_ENG.value, "svp_eng")

    def test_brief_tone_enum(self):
        """Test BriefTone enum values."""
        self.assertEqual(BriefTone.TECHNICAL.value, "technical")
        self.assertEqual(BriefTone.BOARD_READY.value, "board-ready")

    def test_emphasis_area_enum(self):
        """Test EmphasisArea enum values."""
        self.assertEqual(EmphasisArea.GOVERNANCE.value, "governance")
        self.assertEqual(EmphasisArea.ORCHESTRATION.value, "orchestration")

    def test_brief_status_enum(self):
        """Test BriefStatus enum values."""
        self.assertEqual(BriefStatus.PENDING.value, "pending")
        self.assertEqual(BriefStatus.COMPLETE.value, "complete")

    def test_capability_evidence_creation(self):
        """Test CapabilityEvidence dataclass creation."""
        evidence = CapabilityEvidence(
            capability_id="cap-001",
            label="AI Governance",
            description="Comprehensive AI governance framework",
            evidence_anchors=("doc1.md", "doc2.md"),
            layer="L3",
            emphasis_area="governance",
        )
        self.assertEqual(evidence.capability_id, "cap-001")
        self.assertEqual(evidence.label, "AI Governance")

    def test_brief_section_creation(self):
        """Test BriefSection dataclass creation."""
        section = BriefSection(
            section_id="sec-001",
            heading="Executive Summary",
            body="This is the body...",
            word_count=150,
        )
        self.assertEqual(section.section_id, "sec-001")
        self.assertEqual(section.heading, "Executive Summary")
        self.assertTrue(section.is_deterministic)

    def test_exec_brief_request_defaults(self):
        """Test ExecBriefRequest default values."""
        request = ExecBriefRequest()
        self.assertEqual(request.audience, AudiencePersona.RECRUITER)
        self.assertEqual(request.tone, BriefTone.TECHNICAL)
        self.assertEqual(request.source_dirs, ["docs/architecture"])
        self.assertFalse(request.dry_run)
        self.assertEqual(request.industry, "")

    def test_exec_brief_result_passed_gate(self):
        """Test ExecBriefResult.passed_gate property."""
        # Complete with no violations should pass
        result_pass = ExecBriefResult(
            trace_id="trace-001",
            status=BriefStatus.COMPLETE,
            gate_violations=[],
        )
        self.assertTrue(result_pass.passed_gate)

        # With violations should fail
        result_fail = ExecBriefResult(
            trace_id="trace-002",
            status=BriefStatus.COMPLETE,
            gate_violations=["violation-1"],
        )
        self.assertFalse(result_fail.passed_gate)

    def test_style_violation_creation(self):
        """Test StyleViolation dataclass creation."""
        violation = StyleViolation(
            rule_id="STYLE-001",
            severity="warning",
            message="Section too long",
            section_id="sec-001",
        )
        self.assertEqual(violation.rule_id, "STYLE-001")
        self.assertEqual(violation.severity, "warning")

    def test_run_summary_to_dict(self):
        """Test RunSummary.to_dict method."""
        summary = RunSummary(
            trace_id="trace-001",
            app="apps_exec",
            version="1.0.0",
            status="complete",
            sections_generated=5,
            quality_score=0.92,
        )
        d = summary.to_dict()
        self.assertEqual(d["trace_id"], "trace-001")
        self.assertEqual(d["app"], "apps_exec")
        self.assertEqual(d["quality_score"], 0.92)


if __name__ == "__main__":
    unittest.main()
