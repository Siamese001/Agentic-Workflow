"""
Test Research Pydantic Types.
"""
import unittest

from pydantic import ValidationError

from apps_research.types import (
    ComparisonRow,
    ResearchConfig,
    ResearchRequest,
    ResearchResult,
    ResearchRunSummary,
    ResearchSection,
    SourceEntry,
)


class TestSourceEntry(unittest.TestCase):
    """Test cases for SourceEntry Pydantic model."""

    def test_source_creation(self):
        """Test source creation."""
        source = SourceEntry(
            source_id="src-001",
            title="AI Governance Report 2024",
            claim_type="direct_evidence",
            confidence=0.85,
            url="https://example.com/report",
        )
        self.assertEqual(source.source_id, "src-001")
        self.assertEqual(source.confidence, 0.85)

    def test_confidence_bounds(self):
        """Test confidence bounds."""
        with self.assertRaises(ValidationError):
            SourceEntry(source_id="s1", title="Test", confidence=1.5)


class TestComparisonRow(unittest.TestCase):
    """Test cases for ComparisonRow Pydantic model."""

    def test_row_creation(self):
        """Test row creation."""
        row = ComparisonRow(
            subject="Product A",
            dimensions={"price": "$100", "features": "10"},
        )
        self.assertEqual(row.subject, "Product A")
        self.assertEqual(row.dimensions["price"], "$100")


class TestResearchSection(unittest.TestCase):
    """Test cases for ResearchSection Pydantic model."""

    def test_section_creation(self):
        """Test section creation."""
        section = ResearchSection(
            section_id="sec-001",
            heading="Evidence Review",
            body="This section provides a comprehensive review of evidence that meets the minimum length requirement.",
            word_count=200,
            claim_type="direct_evidence",
        )
        self.assertEqual(section.section_id, "sec-001")
        self.assertEqual(section.word_count, 200)

    def test_body_validation(self):
        """Test body minimum length (50 chars)."""
        with self.assertRaises(ValidationError):
            ResearchSection(section_id="s1", heading="Test", body="Too short")


class TestResearchConfig(unittest.TestCase):
    """Test cases for ResearchConfig Pydantic model."""

    def test_config_defaults(self):
        """Test config default values."""
        config = ResearchConfig()
        self.assertEqual(config.min_quality_score, 0.7)
        self.assertEqual(config.max_sections, 10)
        self.assertTrue(config.require_evidence_based)

    def test_quality_score_bounds(self):
        """Test quality score bounds."""
        with self.assertRaises(ValidationError):
            ResearchConfig(min_quality_score=1.5)

    def test_max_sections_bounds(self):
        """Test max sections bounds."""
        with self.assertRaises(ValidationError):
            ResearchConfig(max_sections=50)


class TestResearchRequest(unittest.TestCase):
    """Test cases for ResearchRequest Pydantic model."""

    def test_request_creation(self):
        """Test request creation."""
        request = ResearchRequest(
            topic="AI Governance Trends",
            mode="brief",
            audience_style="executive",
        )
        self.assertEqual(request.topic, "AI Governance Trends")
        self.assertEqual(request.mode, "brief")

    def test_topic_validation(self):
        """Test topic validation."""
        with self.assertRaises(ValidationError):
            ResearchRequest(topic="")

    def test_config_nested(self):
        """Test nested config."""
        request = ResearchRequest(
            topic="Test",
            config=ResearchConfig(min_quality_score=0.8),
        )
        self.assertEqual(request.config.min_quality_score, 0.8)


class TestResearchResult(unittest.TestCase):
    """Test cases for ResearchResult Pydantic model."""

    def test_result_creation(self):
        """Test result creation."""
        result = ResearchResult(
            trace_id="res-001",
            topic="AI Governance",
            mode="brief",
            status="complete",
            quality_score=0.85,
        )
        self.assertEqual(result.trace_id, "res-001")
        self.assertEqual(result.quality_score, 0.85)

    def test_passed_gate_property(self):
        """Test passed_gate property."""
        result_pass = ResearchResult(status="complete", gate_violations=[])
        self.assertTrue(result_pass.passed_gate)

        result_fail = ResearchResult(status="complete", gate_violations=["error"])
        self.assertFalse(result_fail.passed_gate)

    def test_quality_score_bounds(self):
        """Test quality score bounds."""
        with self.assertRaises(ValidationError):
            ResearchResult(quality_score=1.5)


class TestResearchRunSummary(unittest.TestCase):
    """Test cases for ResearchRunSummary Pydantic model."""

    def test_summary_creation(self):
        """Test summary creation."""
        summary = ResearchRunSummary(
            trace_id="trace-001",
            topic="AI Governance",
            status="complete",
            sections_generated=5,
            quality_score=0.82,
        )
        self.assertEqual(summary.trace_id, "trace-001")
        self.assertEqual(summary.app, "apps_research")

    def test_to_dict(self):
        """Test to_dict method."""
        summary = ResearchRunSummary(trace_id="trace-001", quality_score=0.82)
        d = summary.to_dict()
        self.assertEqual(d["trace_id"], "trace-001")
        self.assertEqual(d["quality_score"], 0.82)


if __name__ == "__main__":
    unittest.main()
