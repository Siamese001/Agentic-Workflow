"""
Unit tests for HOP6ValidationAgent (V2).
Verifies QA logic, error handling, and reporting.
"""

from unittest.mock import MagicMock, patch

import pytest
from apps_lic.utils.archetype_indicator_util import ValidationConfig
from apps_lic.types.ImmutableStagingBuffer import ImmutableStagingBuffer
from apps_lic.types.TraceRegistry import TraceRegistry

from apps_lic.engines.HOP6ValidationAgent import HOP6ValidationAgent


@pytest.fixture
def resources():
    return ImmutableStagingBuffer(), TraceRegistry()


@pytest.fixture
def mock_specs():
    mock = MagicMock()
    mock.validation_agent = ValidationConfig(severity_threshold="WARNING", rule_categories=[])
    return mock


class TestHOP6Validation:
    def test_clean_draft_passes(self, mock_specs, resources):
        """Verify a clean draft passes validation."""
        buffer, registry = resources

        # Setup clean inputs - longer draft with strategic keywords
        draft_text = "Hello, I noticed your work on Artificial Intelligence and machine learning. Your roadmap for implementing intelligent systems is impressive."
        buffer.write_once("hop5_generation", {"selected_draft": {"text": draft_text}})
        buffer.write_once("hop2_research", {"strategic_brief": "Artificial Intelligence roadmap"})
        buffer.write_once("hop3_sender_grounding", {})

        with patch("apps_lic.shared.core.agent_base.load_agent_specs", return_value=mock_specs):
            agent = HOP6ValidationAgent()
            agent.run_phase(buffer, registry)

        result = buffer.read("hop6_validation_report")

        # Debug: Print validation results if test fails
        if not result["passed"]:
            print(f"\nValidation failed. Results: {result['validation_results']}")
            print(f"Stats: {result['stats']}")

        assert result["passed"] is True
        assert result["stats"]["critical"] == 0

    def test_placeholder_detection(self, mock_specs, resources):
        """Verify placeholders trigger critical failure."""
        buffer, registry = resources

        # Draft with placeholder
        buffer.write_once(
            "hop5_generation", {"selected_draft": {"text": "Hi [Name], check this out."}}
        )
        buffer.write_once("hop2_research", {"strategic_brief": ""})
        buffer.write_once("hop3_sender_grounding", {})

        with patch("apps_lic.shared.core.agent_base.load_agent_specs", return_value=mock_specs):
            agent = HOP6ValidationAgent()
            agent.run_phase(buffer, registry)

        result = buffer.read("hop6_validation_report")
        assert result["passed"] is False

        # Check trace
        traces = registry.get_traces()
        decision = next(t for t in traces if t["type"] == "DECISION_FINAL")
        assert decision["details"]["status"] == "FAIL"

    def test_missing_inputs(self, mock_specs, resources):
        """Verify crash on missing inputs."""
        buffer, registry = resources

        with patch("apps_lic.shared.core.agent_base.load_agent_specs", return_value=mock_specs):
            agent = HOP6ValidationAgent()
            with pytest.raises(RuntimeError):
                agent.run_phase(buffer, registry)
