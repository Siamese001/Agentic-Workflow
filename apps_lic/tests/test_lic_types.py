"""
Test LIC Types.
"""
import unittest

from apps_lic.types import (
    Draft,
    DraftPackage,
    ValidationResult,
    check_content_compliance,
    score_quality,
    validate_schema_policy,
)


class TestValidationResult(unittest.TestCase):
    """Test cases for ValidationResult."""

    def test_validation_passed(self):
        """Test passed validation result."""
        result = ValidationResult(
            passed=True,
            reasons=(),
            final_draft="test draft",
            attempts=1,
            qa_result={"check": "passed"},
        )
        self.assertTrue(result.passed)
        self.assertEqual(result.reasons, ())
        self.assertEqual(result.attempts, 1)

    def test_validation_failed(self):
        """Test failed validation result."""
        result = ValidationResult(
            passed=False,
            reasons=("error1", "error2"),
            final_draft="bad draft",
            attempts=3,
            qa_result={"check": "failed"},
        )
        self.assertFalse(result.passed)
        self.assertEqual(len(result.reasons), 2)
        self.assertEqual(result.attempts, 3)


class TestDraft(unittest.TestCase):
    """Test cases for Draft."""

    def test_draft_render(self):
        """Test draft render method."""
        draft = Draft(
            subject="Test Subject",
            body="Test body content",
        )
        rendered = draft.render()
        self.assertIn("Subject: Test Subject", rendered)
        self.assertIn("Test body content", rendered)


class TestDraftPackage(unittest.TestCase):
    """Test cases for DraftPackage."""

    def test_draft_package_creation(self):
        """Test DraftPackage creation."""
        package = DraftPackage(
            draft="Test draft content",
            artifacts={"meta": "data"},
            total_latency_ms=1500,
        )
        self.assertEqual(package.draft, "Test draft content")
        self.assertEqual(package.artifacts, {"meta": "data"})
        self.assertEqual(package.total_latency_ms, 1500)

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


class TestValidationFunctions(unittest.TestCase):
    """Test cases for validation functions."""

    def test_validate_schema_policy_pass(self):
        """Test schema validation pass."""
        data = {"name": "Test", "value": 123}
        schema = {"required": ["name", "value"]}
        result = validate_schema_policy(data, schema)
        self.assertTrue(result.passed)
        self.assertEqual(result.reasons, ())

    def test_validate_schema_policy_fail(self):
        """Test schema validation fail."""
        data = {"name": "Test"}
        schema = {"required": ["name", "value"]}
        result = validate_schema_policy(data, schema)
        self.assertFalse(result.passed)
        self.assertIn("value", result.reasons)

    def test_check_content_compliance_pass(self):
        """Test content compliance pass."""
        content = "This is a safe message"
        prohibited = ["badword", "spam"]
        result = check_content_compliance(content, prohibited)
        self.assertTrue(result.passed)
        self.assertEqual(result.reasons, ())

    def test_check_content_compliance_fail(self):
        """Test content compliance fail."""
        content = "This contains badword and spam"
        prohibited = ["badword", "spam"]
        result = check_content_compliance(content, prohibited)
        self.assertFalse(result.passed)

    def test_score_quality(self):
        """Test quality scoring."""
        score = score_quality("This has value proposition", reflexion=True)
        self.assertGreater(score, 0)


if __name__ == "__main__":
    unittest.main()
