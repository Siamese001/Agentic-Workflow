"""
Test LIC Pydantic Types.
"""

import unittest

from pydantic import ValidationError

from apps_lic.types import (
    CampaignConfig,
    CampaignRequest,
    CampaignResult,
    CampaignRunSummary,
    Draft,
    DraftPackage,
    ValidationResult,
)


class TestValidationResult(unittest.TestCase):
    """Test cases for ValidationResult Pydantic model."""

    def test_validation_passed(self):
        """Test passed validation result."""
        result = ValidationResult(
            passed=True,
            reasons=[],
            final_draft="test draft",
            attempts=1,
            qa_result={"check": "passed"},
        )
        self.assertTrue(result.passed)
        self.assertEqual(result.reasons, [])
        self.assertEqual(result.attempts, 1)

    def test_validation_failed(self):
        """Test failed validation result."""
        result = ValidationResult(
            passed=False,
            reasons=["error1", "error2"],
            final_draft="bad draft",
            attempts=3,
            qa_result={"check": "failed"},
        )
        self.assertFalse(result.passed)
        self.assertEqual(len(result.reasons), 2)
        self.assertEqual(result.attempts, 3)

    def test_attempts_validation(self):
        """Test attempts must be >= 1."""
        with self.assertRaises(ValidationError):
            ValidationResult(passed=True, attempts=0)

    def test_latency_validation(self):
        """Test latency must be >= 0."""
        with self.assertRaises(ValidationError):
            ValidationResult(passed=True, latency_ms=-1)


class TestDraft(unittest.TestCase):
    """Test cases for Draft Pydantic model."""

    def test_draft_creation(self):
        """Test Draft creation."""
        draft = Draft(
            subject="Test Subject",
            body="Test body content",
            tone="professional",
        )
        self.assertEqual(draft.subject, "Test Subject")
        self.assertEqual(draft.body, "Test body content")
        self.assertEqual(draft.tone, "professional")

    def test_draft_render(self):
        """Test draft render method."""
        draft = Draft(
            subject="Test Subject",
            body="Test body content",
        )
        rendered = draft.render()
        self.assertIn("Subject: Test Subject", rendered)
        self.assertIn("Test body content", rendered)

    def test_subject_validation_empty(self):
        """Test subject cannot be empty."""
        with self.assertRaises(ValidationError):
            Draft(subject="", body="Valid body")

    def test_body_validation_empty(self):
        """Test body cannot be empty."""
        with self.assertRaises(ValidationError):
            Draft(subject="Valid subject", body="")


class TestDraftPackage(unittest.TestCase):
    """Test cases for DraftPackage Pydantic model."""

    def test_draft_package_creation(self):
        """Test DraftPackage creation."""
        package = DraftPackage(
            draft="Test draft content",
            artifacts={"meta": "data"},
            total_latency_ms=1500,
            trace_id="trace-001",
        )
        self.assertEqual(package.draft, "Test draft content")
        self.assertEqual(package.artifacts, {"meta": "data"})
        self.assertEqual(package.total_latency_ms, 1500)
        self.assertEqual(package.trace_id, "trace-001")

    def test_with_draft(self):
        """Test with_draft method."""
        package = DraftPackage(
            draft="Original",
            artifacts={"key": "value"},
            total_latency_ms=1000,
        )
        new_package = package.with_draft("Modified")
        self.assertEqual(new_package.draft, "Modified")
        self.assertEqual(new_package.artifacts, {"key": "value"})
        self.assertEqual(new_package.total_latency_ms, 1000)

    def test_draft_required(self):
        """Test draft is required."""
        with self.assertRaises(ValidationError):
            DraftPackage(draft="")


class TestCampaignConfig(unittest.TestCase):
    """Test cases for CampaignConfig Pydantic model."""

    def test_config_defaults(self):
        """Test config default values."""
        config = CampaignConfig(
            name="Test Campaign",
            target_audience="developers",
        )
        self.assertEqual(config.compliance_level, "standard")
        self.assertEqual(config.max_recipients, 1000)
        self.assertEqual(config.min_quality_score, 5)
        self.assertTrue(config.require_approval)

    def test_max_recipients_bounds(self):
        """Test max_recipients bounds."""
        # Valid
        config = CampaignConfig(
            name="Test",
            target_audience="all",
            max_recipients=50000,
        )
        self.assertEqual(config.max_recipients, 50000)

        # Invalid - too high
        with self.assertRaises(ValidationError):
            CampaignConfig(
                name="Test",
                target_audience="all",
                max_recipients=200000,
            )

    def test_min_quality_score_bounds(self):
        """Test min_quality_score bounds."""
        with self.assertRaises(ValidationError):
            CampaignConfig(
                name="Test",
                target_audience="all",
                min_quality_score=15,
            )


class TestCampaignRequest(unittest.TestCase):
    """Test cases for CampaignRequest Pydantic model."""

    def test_request_creation(self):
        """Test request creation."""
        config = CampaignConfig(name="Test", target_audience="devs")
        request = CampaignRequest(
            campaign_id="camp-001",
            config=config,
            trace_id="trace-001",
            dry_run=False,
        )
        self.assertEqual(request.campaign_id, "camp-001")
        self.assertEqual(request.trace_id, "trace-001")
        self.assertFalse(request.dry_run)

    def test_campaign_id_required(self):
        """Test campaign_id is required and non-empty."""
        with self.assertRaises(ValidationError):
            CampaignRequest(campaign_id="", config=CampaignConfig(name="Test", target_audience="all"))


class TestCampaignResult(unittest.TestCase):
    """Test cases for CampaignResult Pydantic model."""

    def test_result_creation(self):
        """Test result creation."""
        result = CampaignResult(
            campaign_id="camp-001",
            status="complete",
            overall_score=8.5,
        )
        self.assertEqual(result.campaign_id, "camp-001")
        self.assertEqual(result.status, "complete")
        self.assertEqual(result.overall_score, 8.5)

    def test_passed_gate_property(self):
        """Test passed_gate property."""
        result_pass = CampaignResult(
            status="complete",
            gate_violations=[],
        )
        self.assertTrue(result_pass.passed_gate)

        result_fail = CampaignResult(
            status="complete",
            gate_violations=["violation"],
        )
        self.assertFalse(result_fail.passed_gate)

    def test_overall_score_bounds(self):
        """Test overall_score bounds."""
        with self.assertRaises(ValidationError):
            CampaignResult(overall_score=15)


class TestCampaignRunSummary(unittest.TestCase):
    """Test cases for CampaignRunSummary Pydantic model."""

    def test_summary_creation(self):
        """Test summary creation."""
        summary = CampaignRunSummary(
            trace_id="trace-001",
            campaign_id="camp-001",
            status="complete",
            drafts_generated=5,
            drafts_validated=5,
            overall_score=8.5,
        )
        self.assertEqual(summary.trace_id, "trace-001")
        self.assertEqual(summary.app, "apps_lic")
        self.assertEqual(summary.drafts_generated, 5)

    def test_to_dict(self):
        """Test to_dict method."""
        summary = CampaignRunSummary(
            trace_id="trace-001",
            overall_score=8.5,
        )
        d = summary.to_dict()
        self.assertEqual(d["trace_id"], "trace-001")
        self.assertEqual(d["overall_score"], 8.5)


if __name__ == "__main__":
    unittest.main()
