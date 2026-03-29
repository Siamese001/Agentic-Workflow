"""
Test LIC Integrations.
"""
import unittest

from apps_lic.integrations import ExecutionAdapter, ObservabilityAdapter
from apps_lic.types import DraftPackage, ValidationResult


class TestExecutionAdapter(unittest.TestCase):
    """Test cases for ExecutionAdapter."""

    def setUp(self):
        self.adapter = ExecutionAdapter()

    def test_submit_draft_passed(self):
        """Test submitting passed draft."""
        draft = DraftPackage(
            draft="Test draft content",
            artifacts={"key": "value"},
        )
        validation = ValidationResult(
            passed=True,
            reasons=(),
            final_draft="test",
            attempts=1,
            qa_result={},
        )
        receipt = self.adapter.submit_draft(draft, validation)
        self.assertEqual(receipt["status"], "submitted")
        self.assertEqual(receipt["app"], "apps_lic")
        self.assertTrue(receipt["provenance"]["validation_passed"])

    def test_submit_draft_failed(self):
        """Test submitting failed draft."""
        draft = DraftPackage(draft="Bad draft", artifacts={})
        validation = ValidationResult(
            passed=False,
            reasons=("error",),
            final_draft="bad",
            attempts=1,
            qa_result={},
        )
        receipt = self.adapter.submit_draft(draft, validation)
        self.assertFalse(receipt["provenance"]["validation_passed"])

    def test_get_execution_log(self):
        """Test execution log retrieval."""
        draft = DraftPackage(draft="Test", artifacts={})
        validation = ValidationResult(
            passed=True, reasons=(), final_draft="test", attempts=1, qa_result={}
        )
        self.adapter.submit_draft(draft, validation)
        log = self.adapter.get_execution_log()
        self.assertEqual(len(log), 1)


class TestObservabilityAdapter(unittest.TestCase):
    """Test cases for ObservabilityAdapter."""

    def setUp(self):
        self.adapter = ObservabilityAdapter()

    def test_emit_draft_created(self):
        """Test draft created event."""
        draft = DraftPackage(
            draft="Test draft",
            artifacts={"a": "1", "b": "2"},
            total_latency_ms=1500,
        )
        event = self.adapter.emit_draft_created(draft)
        self.assertEqual(event["event_type"], "draft_created")
        self.assertEqual(event["draft_length"], 10)
        self.assertEqual(event["artifacts_count"], 2)

    def test_emit_validation_complete(self):
        """Test validation complete event."""
        result = ValidationResult(
            passed=True,
            reasons=(),
            final_draft="test",
            attempts=2,
            qa_result={},
        )
        event = self.adapter.emit_validation_complete(result)
        self.assertEqual(event["event_type"], "validation_complete")
        self.assertTrue(event["passed"])
        self.assertEqual(event["attempts"], 2)

    def test_emit_campaign_complete(self):
        """Test campaign complete event."""
        draft = DraftPackage(draft="Final draft", artifacts={"final": "true"})
        validation = ValidationResult(
            passed=True, reasons=(), final_draft="final", attempts=1, qa_result={}
        )
        event = self.adapter.emit_campaign_complete(draft, validation)
        self.assertEqual(event["event_type"], "campaign_complete")
        self.assertTrue(event["validation_passed"])

    def test_get_metrics(self):
        """Test metrics retrieval."""
        draft = DraftPackage(draft="Test", artifacts={})
        self.adapter.emit_draft_created(draft)
        metrics = self.adapter.get_metrics()
        self.assertEqual(len(metrics), 1)


if __name__ == "__main__":
    unittest.main()
