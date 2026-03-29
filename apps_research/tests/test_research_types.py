"""
Test Research Types.
"""
import unittest

from apps_research.types import (
    ResearchStatus,
    ArtifactMode,
    ClaimType,
    AudienceStyle,
    SourceEntry,
    ComparisonRow,
    ResearchSection,
    ResearchRequest,
    ResearchResult,
    ResearchRunSummary,
)


class TestResearchTypes(unittest.TestCase):
    """Test cases for research types."""

    def test_research_status_enum(self):
        """Test ResearchStatus enum values."""
        self.assertEqual(ResearchStatus.PENDING.value, "pending")
        self.assertEqual(ResearchStatus.COMPLETE.value, "complete")
        self.assertEqual(ResearchStatus.FAILED.value, "failed")

    def test_artifact_mode_enum(self):
        """Test ArtifactMode enum values."""
        self.assertEqual(ArtifactMode.BRIEF.value, "brief")
        self.assertEqual(ArtifactMode.COMPARISON.value, "comparison")

    def test_claim_type_enum(self):
        """Test ClaimType enum values."""
        self.assertEqual(ClaimType.DIRECT_EVIDENCE.value, "direct_evidence")
        self.assertEqual(ClaimType.INTERPRETATION.value, "interpretation")

    def test_audience_style_enum(self):
        """Test AudienceStyle enum values."""
        self.assertEqual(AudienceStyle.TECHNICAL.value, "technical")
        self.assertEqual(AudienceStyle.EXECUTIVE.value, "executive")

    def test_source_entry_creation(self):
        """Test SourceEntry dataclass creation."""
        entry = SourceEntry(
            source_id="src-001",
            title="AI Research Paper",
            claim_type=ClaimType.DIRECT_EVIDENCE,
            confidence=0.95,
            summary="Key findings...",
            url="https://example.com",
        )
        self.assertEqual(entry.source_id, "src-001")
        self.assertEqual(entry.confidence, 0.95)

    def test_comparison_row_creation(self):
        """Test ComparisonRow dataclass creation."""
        row = ComparisonRow(
            subject="Subject A",
            dimensions={"speed": "fast", "cost": "low"},
        )
        self.assertEqual(row.subject, "Subject A")
        self.assertEqual(row.dimensions["speed"], "fast")

    def test_research_section_creation(self):
        """Test ResearchSection dataclass creation."""
        section = ResearchSection(
            section_id="sec-001",
            heading="Introduction",
            body="Research findings...",
            word_count=500,
        )
        self.assertEqual(section.section_id, "sec-001")
        self.assertTrue(section.is_deterministic)

    def test_research_request_defaults(self):
        """Test ResearchRequest default values."""
        request = ResearchRequest()
        self.assertEqual(request.topic, "")
        self.assertEqual(request.mode, ArtifactMode.BRIEF)
        self.assertEqual(request.audience_style, AudienceStyle.TECHNICAL)
        self.assertFalse(request.dry_run)

    def test_research_result_passed_gate(self):
        """Test ResearchResult.passed_gate property."""
        # Complete with no violations should pass
        result_pass = ResearchResult(
            trace_id="trace-001",
            status=ResearchStatus.COMPLETE,
            gate_violations=[],
        )
        self.assertTrue(result_pass.passed_gate)

        # With violations should fail
        result_fail = ResearchResult(
            trace_id="trace-002",
            status=ResearchStatus.COMPLETE,
            gate_violations=["violation-1"],
        )
        self.assertFalse(result_fail.passed_gate)

    def test_research_run_summary_to_dict(self):
        """Test ResearchRunSummary.to_dict method."""
        summary = ResearchRunSummary(
            trace_id="trace-001",
            app="apps_research",
            version="1.0.0",
            status="complete",
            topic="AI Safety",
            quality_score=0.92,
        )
        d = summary.to_dict()
        self.assertEqual(d["trace_id"], "trace-001")
        self.assertEqual(d["topic"], "AI Safety")


if __name__ == "__main__":
    unittest.main()
