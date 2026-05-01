"""
Unit tests for HOP8QAReportAgent (V2).
Verifies aggregation, scoring, and file generation.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from apps_lic.utils.archetype_indicator_util import QAReportConfig
from apps_lic.types.ImmutableStagingBuffer import ImmutableStagingBuffer
from apps_lic.types.TraceRegistry import TraceRegistry

from apps_lic.engines.HOP8QAReportAgent import HOP8QAReportAgent


@pytest.fixture
def resources():
    return ImmutableStagingBuffer(), TraceRegistry()


@pytest.fixture
def populated_buffer(resources):
    buf, _ = resources
    # Minimal mock data for aggregation
    buf.write_once("hop1_analysis", {"recipient_name": "John Doe", "Archetype": "C_LEVEL"})
    buf.write_once("hop2_research", {"signal_score": 0.8})
    buf.write_once("hop3_sender_grounding", {})
    buf.write_once("hop4_routing", {"route": "INMAIL"})
    buf.write_once("hop5_generation", {"selected_draft": {"text": "Draft text", "score": 10}})
    buf.write_once(
        "hop6_validation_report", {"passed": True, "validation_results": [{"passed": True}]}
    )
    buf.write_once("hop7_gate_decision", {"decision": "PASS"})
    return buf, resources[1]


@pytest.fixture
def mock_specs(tmp_path):
    mock = MagicMock()
    mock.qa_report_agent = QAReportConfig(
        report_sections=["Summary"],
        output_directory=str(tmp_path),
        scoring_weights={"research": 0.3, "alignment": 0.2, "validation": 0.3, "generation": 0.2},
    )
    return mock


class TestHOP8ReportLogic:
    def test_report_generation_and_scoring(self, mock_specs, populated_buffer):
        """Verify score is calculated and file is saved."""
        buffer, registry = populated_buffer

        with patch("apps_lic.shared.core.agent_base.load_agent_specs", return_value=mock_specs):
            agent = HOP8QAReportAgent()
            agent.run_phase(buffer, registry)

        result = buffer.read("hop8_qa_report")

        # Check Score (Research 0.8*100*0.3=24 + Val 100*0.3=30 + Gen 10*10*0.2=20 + Align 1*1*100*0.2=20)
        # Total approx 94
        assert result["total_score"] > 90
        assert Path(result["report_path"]).exists()
        assert "QA_JohnDoe" in result["report_path"]

    def test_missing_data_resilience(self, mock_specs, resources):
        """Verify agent doesn't crash if upstream data is partial."""
        buffer, registry = resources
        # Only HOP-1 provided
        buffer.write_once("hop1_analysis", {"recipient_name": "Ghost"})

        with patch("apps_lic.shared.core.agent_base.load_agent_specs", return_value=mock_specs):
            agent = HOP8QAReportAgent()
            agent.run_phase(buffer, registry)

        result = buffer.read("hop8_qa_report")
        assert result["total_score"] == 0  # No data to score
        assert Path(result["report_path"]).exists()
