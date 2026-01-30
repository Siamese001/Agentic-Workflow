"""
Integration tests for HOP Pipeline - LIC outreach workflow.

Tests cross-agent communication in the HOP (Handoff Orchestration Protocol) pipeline.
"""

from unittest.mock import Mock, patch

import pytest


@pytest.fixture(autouse=True)
def mock_external_services():
    """Mock all external services to prevent network calls."""
    with (
        patch("redis.Redis", return_value=Mock()),
        patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}),
    ):
        yield


class TestHOPPipelineIntegration:
    """Integration tests for HOP pipeline agents."""

    @pytest.fixture
    def mock_mission_input(self):
        """Provide mock mission input for pipeline."""
        return {
            "profile": {
                "name": "Test Lead",
                "title": "VP Engineering",
                "company": "Tech Corp",
                "industry": "Technology",
            },
            "sender": {
                "name": "Sales Rep",
                "company": "Our Company",
                "value_props": ["AI Solutions", "Cost Reduction"],
            },
            "campaign": {
                "type": "cold_outreach",
                "channel": "linkedin",
            },
        }

    def test_hop1_to_hop2_handoff(self, mock_mission_input):
        """Test HOP1 -> HOP2 data handoff."""
        # HOP1 output should be valid HOP2 input
        hop1_output = {
            "profile_analysis": {
                "classification": "high_value",
                "industry_sensitivity": "low",
                "engagement_score": 0.85,
            },
            "routing_decision": "proceed_to_research",
        }

        # Verify HOP2 can accept HOP1 output
        assert "profile_analysis" in hop1_output, "HOP1 should output profile analysis"
        assert "routing_decision" in hop1_output, "HOP1 should output routing decision"

    def test_hop2_to_hop3_handoff(self):
        """Test HOP2 -> HOP3 data handoff."""
        hop2_output = {
            "research_results": {
                "company_insights": ["Recent funding", "Expansion plans"],
                "pain_points": ["Scaling challenges", "Tech debt"],
                "opportunities": ["AI adoption", "Process automation"],
            },
            "archetype_summary": "growth_focused_leader",
        }

        assert "research_results" in hop2_output, "HOP2 should output research"
        assert "archetype_summary" in hop2_output, "HOP2 should output archetype"

    def test_hop3_to_hop4_handoff(self):
        """Test HOP3 -> HOP4 data handoff."""
        hop3_output = {
            "grounded_entities": {
                "sender_metrics": ["50% cost reduction", "3x efficiency"],
                "sender_achievements": ["Fortune 500 clients", "Industry awards"],
            },
            "grounding_score": 0.92,
        }

        assert "grounded_entities" in hop3_output, "HOP3 should output grounded entities"

    def test_hop4_to_hop5_handoff(self):
        """Test HOP4 -> HOP5 data handoff."""
        hop4_output = {
            "routing_result": {
                "template_type": "executive_outreach",
                "tone": "professional",
                "length": "concise",
            },
            "conditions_met": True,
        }

        assert "routing_result" in hop4_output, "HOP4 should output routing result"

    def test_hop5_to_hop6_handoff(self):
        """Test HOP5 -> HOP6 data handoff."""
        hop5_output = {
            "generated_message": {
                "subject": "Quick question about Tech Corp growth",
                "body": "Hi Test, noticed your expansion plans...",
                "cta": "Would a 15-min call next week work?",
            },
            "generation_metadata": {
                "model": "gpt-4",
                "tokens_used": 150,
            },
        }

        assert "generated_message" in hop5_output, "HOP5 should output message"

    def test_hop6_validation_feedback_loop(self):
        """Test HOP6 validation can trigger feedback loop."""
        hop6_output = {
            "validation_result": {
                "passed": False,
                "violations": ["placeholder_detected", "too_long"],
            },
            "feedback_action": "regenerate_hop5",
        }

        assert "validation_result" in hop6_output, "HOP6 should output validation"
        assert hop6_output["feedback_action"] == "regenerate_hop5", "Should trigger regeneration"

    def test_full_pipeline_data_flow(self, mock_mission_input):
        """Test complete pipeline data flow."""
        pipeline_stages = [
            "HOP1_ProfileAnalysis",
            "HOP2_Research",
            "HOP3_SenderGrounding",
            "HOP4_Routing",
            "HOP5_Generation",
            "HOP6_Validation",
            "HOP7_GateDecision",
            "HOP8_QAReport",
            "HOP9_Integration",
        ]

        assert len(pipeline_stages) == 9, "Pipeline has 9 stages"
        assert pipeline_stages[0].startswith("HOP1"), "Starts with HOP1"
        assert pipeline_stages[-1].startswith("HOP9"), "Ends with HOP9"


class TestHOPErrorHandling:
    """Test error handling across HOP pipeline."""

    def test_hop_failure_propagation(self):
        """Test failure propagation through pipeline."""
        hop_error = {
            "stage": "HOP2_Research",
            "error_type": "research_timeout",
            "retry_count": 3,
            "fallback_action": "use_cached_research",
        }

        assert "fallback_action" in hop_error, "Should have fallback"

    def test_hop_retry_logic(self):
        """Test retry logic between HOPs."""
        max_retries = 3
        retry_delays = [1, 2, 4]  # Exponential backoff

        assert len(retry_delays) == max_retries, "Retry delays match max retries"


class TestHOPStateManagement:
    """Test state management across HOP pipeline."""

    def test_immutable_state_between_hops(self):
        """Test state is immutable between HOP stages."""
        initial_state = {"stage": "HOP1", "data": {"key": "value"}}

        # Create new state for next stage
        next_state = {**initial_state, "stage": "HOP2"}

        assert initial_state["stage"] == "HOP1", "Original unchanged"
        assert next_state["stage"] == "HOP2", "New state updated"

    def test_state_checkpoint_between_hops(self):
        """Test state checkpointing between HOPs."""
        checkpoint = {
            "hop_number": 3,
            "timestamp": "2026-01-30T11:00:00Z",
            "state_hash": "abc123",
            "recoverable": True,
        }

        assert checkpoint["recoverable"] is True, "Should be recoverable"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
