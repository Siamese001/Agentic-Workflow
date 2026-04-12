"""
Test LIC Integrations.
"""

import unittest

from apps_lic.integrations import ExecutionAdapter, ObservabilityAdapter
from apps_lic.types import CampaignConfig, CampaignRequest, CampaignResult, DraftPackage, ValidationResult


class TestExecutionAdapter(unittest.TestCase):
    """Test cases for ExecutionAdapter."""

    def setUp(self):
        self.adapter = ExecutionAdapter()

    def test_submit_campaign_passed(self):
        """Test submitting passed campaign."""
        config = CampaignConfig(name="Test", target_audience="devs")
        request = CampaignRequest(campaign_id="camp-001", config=config, trace_id="trace-001")
        result = CampaignResult(
            campaign_id="camp-001",
            status="complete",
            overall_score=8.5,
            gate_violations=[],
        )
        receipt = self.adapter.submit_campaign(request, result)
        self.assertEqual(receipt["status"], "submitted")
        self.assertEqual(receipt["app"], "apps_lic")
        self.assertTrue(receipt["provenance"]["gate_passed"])

    def test_submit_campaign_failed(self):
        """Test submitting failed campaign."""
        config = CampaignConfig(name="Test", target_audience="devs")
        request = CampaignRequest(campaign_id="camp-002", config=config)
        result = CampaignResult(
            campaign_id="camp-002",
            status="failed",
            gate_violations=["error"],
        )
        receipt = self.adapter.submit_campaign(request, result)
        self.assertFalse(receipt["provenance"]["gate_passed"])

    def test_submit_draft(self):
        """Test submitting draft."""
        draft = DraftPackage(draft="Test draft", artifacts={"key": "value"}, trace_id="trace-001")
        validation = ValidationResult(passed=True, reasons=[], final_draft="test", attempts=1, qa_result={})
        receipt = self.adapter.submit_draft(draft, validation)
        self.assertEqual(receipt["status"], "submitted")
        self.assertTrue(receipt["provenance"]["validation_passed"])

    def test_get_execution_log(self):
        """Test execution log retrieval."""
        draft = DraftPackage(draft="Test", artifacts={})
        validation = ValidationResult(passed=True, reasons=[], final_draft="test", attempts=1, qa_result={})
        self.adapter.submit_draft(draft, validation)
        log = self.adapter.get_execution_log()
        self.assertEqual(len(log), 1)


class TestObservabilityAdapter(unittest.TestCase):
    """Test cases for ObservabilityAdapter."""

    def setUp(self):
        self.adapter = ObservabilityAdapter()

    def test_emit_campaign_start(self):
        """Test campaign start event."""
        config = CampaignConfig(name="Test", target_audience="devs")
        request = CampaignRequest(campaign_id="camp-001", config=config, dry_run=True)
        event = self.adapter.emit_campaign_start(request)
        self.assertEqual(event["event_type"], "campaign_start")
        self.assertEqual(event["campaign_id"], "camp-001")
        self.assertTrue(event["dry_run"])

    def test_emit_campaign_complete(self):
        """Test campaign complete event."""
        result = CampaignResult(
            campaign_id="camp-001",
            status="complete",
            overall_score=8.5,
            gate_violations=[],
        )
        event = self.adapter.emit_campaign_complete(result)
        self.assertEqual(event["event_type"], "campaign_complete")
        self.assertEqual(event["overall_score"], 8.5)
        self.assertTrue(event["gate_passed"])

    def test_emit_draft_created(self):
        """Test draft created event."""
        draft = DraftPackage(draft="Test draft", artifacts={"a": "1", "b": "2"}, total_latency_ms=1500)
        event = self.adapter.emit_draft_created(draft)
        self.assertEqual(event["event_type"], "draft_created")
        self.assertEqual(event["draft_length"], 10)
        self.assertEqual(event["artifacts_count"], 2)

    def test_emit_validation_complete(self):
        """Test validation complete event."""
        result = ValidationResult(passed=True, reasons=[], final_draft="test", attempts=2, qa_result={})
        event = self.adapter.emit_validation_complete(result)
        self.assertEqual(event["event_type"], "validation_complete")
        self.assertTrue(event["passed"])
        self.assertEqual(event["attempts"], 2)

    def test_get_metrics(self):
        """Test metrics retrieval."""
        result = CampaignResult(campaign_id="camp-001", status="complete")
        self.adapter.emit_campaign_complete(result)
        metrics = self.adapter.get_metrics()
        self.assertEqual(len(metrics), 1)


if __name__ == "__main__":
    unittest.main()
