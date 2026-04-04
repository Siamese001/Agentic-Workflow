"""
Test LIC Outputs.
"""
import unittest

from apps_lic.outputs import (
    CampaignRenderer,
    CampaignSummaryRenderer,
    DraftRenderer,
    ValidationReportRenderer,
)
from apps_lic.types import CampaignResult, CampaignRunSummary, DraftPackage, ValidationResult


class TestCampaignRenderer(unittest.TestCase):
    """Test cases for CampaignRenderer."""

    def setUp(self):
        self.renderer = CampaignRenderer()

    def test_render_json(self):
        """Test JSON rendering."""
        result = CampaignResult(campaign_id="camp-001", status="complete", overall_score=8.5)
        json_output = self.renderer.render_json(result)
        self.assertIn("camp-001", json_output)
        self.assertIn("complete", json_output)

    def test_render_markdown(self):
        """Test Markdown rendering."""
        result = CampaignResult(
            campaign_id="camp-001",
            status="complete",
            overall_score=8.5,
            gate_violations=[],
        )
        md_output = self.renderer.render_markdown(result)
        self.assertIn("camp-001", md_output)
        self.assertIn("8.5", md_output)
        self.assertIn("PASSED", md_output)

    def test_render_compact(self):
        """Test compact rendering."""
        result = CampaignResult(campaign_id="camp-001", status="complete", overall_score=8.5)
        compact = self.renderer.render_compact(result)
        self.assertEqual(compact["campaign_id"], "camp-001")
        self.assertEqual(compact["score"], 8.5)


class TestCampaignSummaryRenderer(unittest.TestCase):
    """Test cases for CampaignSummaryRenderer."""

    def setUp(self):
        self.renderer = CampaignSummaryRenderer()

    def test_render_json(self):
        """Test JSON rendering."""
        summary = CampaignRunSummary(trace_id="trace-001", overall_score=8.5)
        json_output = self.renderer.render_json(summary)
        self.assertIn("trace-001", json_output)

    def test_render_markdown(self):
        """Test Markdown rendering."""
        summary = CampaignRunSummary(
            trace_id="trace-001",
            campaign_id="camp-001",
            status="complete",
            drafts_generated=5,
        )
        md_output = self.renderer.render_markdown(summary)
        self.assertIn("trace-001", md_output)
        self.assertIn("apps_lic", md_output)


class TestDraftRenderer(unittest.TestCase):
    """Test cases for DraftRenderer."""

    def setUp(self):
        self.renderer = DraftRenderer()

    def test_render_json(self):
        """Test JSON rendering."""
        draft = DraftPackage(draft="Test content", artifacts={"meta": "data"})
        json_output = self.renderer.render_json(draft)
        self.assertIn("Test content", json_output)

    def test_render_markdown(self):
        """Test Markdown rendering."""
        draft = DraftPackage(draft="Test content", artifacts={"key": "value"})
        md_output = self.renderer.render_markdown(draft)
        self.assertIn("Test content", md_output)

    def test_render_compact(self):
        """Test compact rendering."""
        draft = DraftPackage(draft="Test content", artifacts={"key": "value"})
        compact = self.renderer.render_compact(draft)
        self.assertEqual(compact["artifacts_count"], 1)


class TestValidationReportRenderer(unittest.TestCase):
    """Test cases for ValidationReportRenderer."""

    def setUp(self):
        self.renderer = ValidationReportRenderer()

    def test_render_json(self):
        """Test JSON rendering."""
        result = ValidationResult(passed=True, reasons=[], final_draft="test", attempts=1, qa_result={})
        json_output = self.renderer.render_json(result)
        self.assertIn("true", json_output.lower())

    def test_render_markdown_passed(self):
        """Test Markdown rendering for passed validation."""
        result = ValidationResult(passed=True, reasons=[], final_draft="test", attempts=1, qa_result={})
        md_output = self.renderer.render_markdown(result)
        self.assertIn("PASSED", md_output)

    def test_render_markdown_failed(self):
        """Test Markdown rendering for failed validation."""
        result = ValidationResult(passed=False, reasons=["error"], final_draft="test", attempts=1, qa_result={})
        md_output = self.renderer.render_markdown(result)
        self.assertIn("FAILED", md_output)
        self.assertIn("error", md_output)


if __name__ == "__main__":
    unittest.main()
