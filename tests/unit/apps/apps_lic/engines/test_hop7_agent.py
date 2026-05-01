"""
Unit tests for HOP7GateDecisionAgent (V2).
Ensures failure classification and workflow direction logic.
"""

from unittest.mock import MagicMock, patch

import pytest
from apps_lic.utils.archetype_indicator_util import GateConfig
from apps_lic.types.ImmutableStagingBuffer import ImmutableStagingBuffer
from apps_lic.types.TraceRegistry import TraceRegistry

from apps_lic.engines.HOP7GateDecisionAgent import HOP7GateDecisionAgent


@pytest.fixture
def resources():
    return ImmutableStagingBuffer(), TraceRegistry()


@pytest.fixture
def mock_specs():
    mock = MagicMock()
    mock.gate_decision_agent = GateConfig(
        factual_failure_rules=["STRATEGIC_ALIGNMENT", "FACTUAL_INACCURACY"],
        max_factual_loops=2,
        max_creative_retries=3,
    )
    return mock


class TestHOP7GateLogic:
    def test_pass_decision(self, mock_specs, resources):
        """Verify PASS decision leads to PROCEED."""
        buffer, registry = resources
        # Mock a passing report
        buffer.write_once("hop6_validation_report", {"passed": True, "validation_results": []})

        with patch("apps_lic.shared.core.agent_base.load_agent_specs", return_value=mock_specs):
            agent = HOP7GateDecisionAgent()
            agent.run_phase(buffer, registry)

        result = buffer.read("hop7_gate_decision")
        assert result["decision"] == "PASS"
        assert result["action"] == "PROCEED"

    def test_factual_failure_retry_hop2(self, mock_specs, resources):
        """Verify Factual failure triggers RETRY_HOP2."""
        buffer, registry = resources
        report = {
            "passed": False,
            "validation_results": [
                {"rule_id": "STRATEGIC_ALIGNMENT", "severity": "CRITICAL", "passed": False}
            ],
        }
        buffer.write_once("hop6_validation_report", report)

        with patch("apps_lic.shared.core.agent_base.load_agent_specs", return_value=mock_specs):
            agent = HOP7GateDecisionAgent()
            agent.run_phase(buffer, registry)

        result = buffer.read("hop7_gate_decision")
        assert result["decision"] == "FAIL_FACTUAL"
        assert result["action"] == "RETRY_HOP2"

    def test_creative_failure_retry_hop5(self, mock_specs, resources):
        """Verify Creative/Compliance failure triggers RETRY_HOP5."""
        buffer, registry = resources
        report = {
            "passed": False,
            "validation_results": [
                {"rule_id": "PLACEHOLDERS", "severity": "CRITICAL", "passed": False}
            ],
        }
        buffer.write_once("hop6_validation_report", report)

        with patch("apps_lic.shared.core.agent_base.load_agent_specs", return_value=mock_specs):
            agent = HOP7GateDecisionAgent()
            agent.run_phase(buffer, registry)

        result = buffer.read("hop7_gate_decision")
        assert result["decision"] == "FAIL_CREATIVE"
        assert result["action"] == "RETRY_HOP5"

    def test_missing_input_error(self, mock_specs, resources):
        """Verify crash on missing validation report."""
        buffer, registry = resources
        # No validation report written

        with patch("apps_lic.shared.core.agent_base.load_agent_specs", return_value=mock_specs):
            agent = HOP7GateDecisionAgent()
            with pytest.raises(RuntimeError):
                agent.run_phase(buffer, registry)
