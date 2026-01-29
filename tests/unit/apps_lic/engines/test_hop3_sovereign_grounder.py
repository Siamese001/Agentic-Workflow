"""
HOP-3 Sovereign Grounder Test Suite.

MANDATORY REQUIREMENT: All tests must achieve a 100% PASS RATE for Windsurf execution.
"""

from apps_lic.shared.core.immutable_buffer import ImmutableStagingBuffer
from apps_lic.shared.core.trace_registry import TraceRegistry

from apps_lic.engines.HOP3SenderGroundingAgent import HOP3SenderGroundingAgent


class TestHOP3SovereignGrounder:
    """
    Sovereign Foundation Test Suite for HOP-3.
    MANDATORY REQUIREMENT: All tests must achieve a 100% PASS RATE for Windsurf execution.
    """

    def test_whitelist_extraction_purity(self):
        """
        Verify that only whitelisted categories are extracted.
        Ensures that non-target JSON keys do not pollute the grounding buffer.
        """
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        buffer.write_once("mission_input", {"id": "grounding_test"})

        agent = HOP3SenderGroundingAgent()

        # Mock _load_json_file to return test data
        mock_data = {
            "whitelisted_products": [{"name": "Product A"}, {"name": "Product B"}],
            "whitelisted_team_members": [{"name": "Alice"}, {"name": "Bob"}],
            "internal_notes": ["This should NOT be extracted"],
            "raw_data": {"secret": "value"},
        }
        agent._load_json_file = lambda f: mock_data

        agent.run_phase(buffer, registry)

        result = buffer.read("hop3_sender_grounding")
        whitelists = result["grounding_whitelists"]

        # Verify only whitelisted categories exist
        assert "products" in whitelists
        assert "team_members" in whitelists
        # Non-target keys should NOT be in whitelists
        assert "internal_notes" not in whitelists
        assert "raw_data" not in whitelists

    def test_metric_source_binding_verifiability(self):
        """
        Verify that extracted achievements are mapped to verifiable sources.
        Ensures compliance with LIC-QA-041 (Metric source binding).
        """
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()

        agent = HOP3SenderGroundingAgent()

        # Mock with achievements data
        mock_data = {
            "quantifiable_achievements": [
                "Increased revenue by $5 million",
                "Reduced costs by 30%",
                "Expanded team growth by 50%",
            ]
        }
        agent._load_json_file = lambda f: mock_data

        agent.run_phase(buffer, registry)

        result = buffer.read("hop3_sender_grounding")
        # Metric map should exist to support HOP-5 generation
        assert "metric_source_map" in result
        assert isinstance(result["metric_source_map"], dict)
        # Verify metric categories exist
        assert "revenue" in result["metric_source_map"]
        assert "efficiency" in result["metric_source_map"]
        assert "growth" in result["metric_source_map"]

    def test_trace_registry_extraction_audit(self):
        """
        Verify that every extraction target triggers an ENTITY_EXTRACTED trace.
        Ensures observability into which grounding categories are available for the mission.
        """
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()

        agent = HOP3SenderGroundingAgent()

        # Mock with multiple extraction targets
        mock_data = {
            "whitelisted_products": [{"name": "Widget"}],
            "quantifiable_achievements": ["Grew sales 100%"],
        }
        agent._load_json_file = lambda f: mock_data

        agent.run_phase(buffer, registry)

        traces = [
            t["details"]["category"]
            for t in registry.get_traces()
            if t["type"] == "ENTITY_EXTRACTED"
        ]
        # Should match targets in agent_specs.json
        assert "products" in traces
        assert "achievements" in traces

    def test_grounding_output_structure(self):
        """
        Verify that HOP-3 output has the correct structure.
        """
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()

        agent = HOP3SenderGroundingAgent()
        agent._load_json_file = lambda f: {"whitelisted_products": [{"name": "Test"}]}

        agent.run_phase(buffer, registry)

        result = buffer.read("hop3_sender_grounding")
        assert "grounding_whitelists" in result
        assert "metric_source_map" in result
        assert "metadata" in result
        assert "sources_loaded" in result["metadata"]

    def test_metric_categorization_revenue(self):
        """
        Verify that revenue-related achievements are correctly categorized.
        """
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()

        agent = HOP3SenderGroundingAgent()
        mock_data = {
            "quantifiable_achievements": [
                "Generated $10 million in new revenue",
                "Increased sales by 200%",
            ]
        }
        agent._load_json_file = lambda f: mock_data

        agent.run_phase(buffer, registry)

        result = buffer.read("hop3_sender_grounding")
        metric_map = result["metric_source_map"]
        # Both should be in revenue category
        assert len(metric_map["revenue"]) >= 1

    def test_metric_categorization_efficiency(self):
        """
        Verify that efficiency-related achievements are correctly categorized.
        """
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()

        agent = HOP3SenderGroundingAgent()
        mock_data = {
            "quantifiable_achievements": [
                "Reduced operational costs by 40%",
                "Saved $2 million annually",
            ]
        }
        agent._load_json_file = lambda f: mock_data

        agent.run_phase(buffer, registry)

        result = buffer.read("hop3_sender_grounding")
        metric_map = result["metric_source_map"]
        assert len(metric_map["efficiency"]) >= 1

    def test_decision_final_trace(self):
        """
        Verify that DECISION_FINAL trace is logged with GROUNDING_COMPLETE status.
        """
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()

        agent = HOP3SenderGroundingAgent()
        agent._load_json_file = lambda f: {}

        agent.run_phase(buffer, registry)

        final_traces = [t for t in registry.get_traces() if t["type"] == "DECISION_FINAL"]
        assert len(final_traces) >= 1
        assert final_traces[0]["details"]["status"] == "GROUNDING_COMPLETE"

    def test_empty_source_files_handling(self):
        """
        Verify that HOP-3 handles missing/empty source files gracefully.
        """
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()

        agent = HOP3SenderGroundingAgent()
        # Return None to simulate missing files
        agent._load_json_file = lambda f: None

        agent.run_phase(buffer, registry)

        result = buffer.read("hop3_sender_grounding")
        # Should still produce valid output structure
        assert "grounding_whitelists" in result
        assert result["metadata"]["sources_loaded"] == 0
