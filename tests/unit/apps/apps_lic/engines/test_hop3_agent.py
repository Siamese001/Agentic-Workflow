"""
Unit tests for HOP3SenderGroundingAgent (V2).
Verifies static file extraction and buffer integration.
"""

import json
from unittest.mock import MagicMock, mock_open, patch

import pytest
from apps_lic.utils.archetype_indicator_util import SenderGroundingConfig
from apps_lic.types.ImmutableStagingBuffer import ImmutableStagingBuffer
from apps_lic.types.TraceRegistry import TraceRegistry

from apps_lic.engines.HOP3SenderGroundingAgent import HOP3SenderGroundingAgent

# --- Mock Data ---

MOCK_KB_JSON = json.dumps(
    {
        "whitelisted_products": [{"name": "AgenticCore"}, {"name": "ReachoutBot"}],
        "quantifiable_achievements": ["Increased ROI by 50%"],
    }
)

MOCK_RESUME_JSON = json.dumps(
    {
        "professional_experience": [
            {
                "company": "Tech Corp",
                "bullet_pool": ["Built a thing", "Scaled a thing", "Fixed a thing"],
            }
        ]
    }
)

# --- Fixtures ---


@pytest.fixture
def resources():
    return ImmutableStagingBuffer(), TraceRegistry()


@pytest.fixture
def mock_config(monkeypatch):
    """Inject mock config into the agent."""
    # We mock the LICAgentBase configuration loading to return our test config
    mock_specs = MagicMock()
    mock_specs.sender_grounding_agent = SenderGroundingConfig(
        source_files=["kb.json", "resume.json"], extraction_targets=["products", "achievements"]
    )

    # Patch the load_agent_specs used by LICAgentBase
    with patch("apps_lic.shared.core.agent_base.load_agent_specs", return_value=mock_specs):
        yield mock_specs


# --- Tests ---


class TestHOP3Extraction:
    def test_successful_extraction(self, mock_config, resources):
        """Verify data is extracted from valid files."""
        buffer, registry = resources

        # Mock file system
        def file_side_effect(filename, *args, **kwargs):
            if "kb.json" in str(filename):
                return mock_open(read_data=MOCK_KB_JSON).return_value
            if "resume.json" in str(filename):
                return mock_open(read_data=MOCK_RESUME_JSON).return_value
            raise FileNotFoundError(filename)

        with patch("builtins.open", side_effect=file_side_effect):
            with patch("pathlib.Path.exists", return_value=True):
                agent = HOP3SenderGroundingAgent()
                agent.run_phase(buffer, registry)

        # Verify Output
        result = buffer.read("hop3_sender_grounding")
        assert result is not None

        # Check KB extraction
        assert "AgenticCore" in result["sender_grounding"]["products"]
        assert "Increased ROI by 50%" in result["sender_grounding"]["quantifiable_achievements"]

        # Check Resume extraction
        assert "Tech Corp" in result["sender_grounding"]["raw_evidence"]["companies"]
        assert len(result["sender_grounding"]["raw_evidence"]["achievements"]) == 3

        # Check Traces
        traces = [t["type"] for t in registry.get_traces()]
        assert "PHASE_STEP" in traces
        assert "DECISION_FINAL" in traces

    def test_missing_files_handled_gracefully(self, mock_config, resources):
        """Verify agent proceeds if a file is missing."""
        buffer, registry = resources

        # Mock Path.exists to fail for one file
        def exists_side_effect(self):
            return "kb.json" in str(self)  # Only kb.json exists

        with patch("pathlib.Path.exists", side_effect=exists_side_effect, autospec=True):
            with patch("builtins.open", mock_open(read_data=MOCK_KB_JSON)):
                agent = HOP3SenderGroundingAgent()
                agent.run_phase(buffer, registry)

        # Verify Output contains partial data
        result = buffer.read("hop3_sender_grounding")
        assert "AgenticCore" in result["sender_grounding"]["products"]
        assert "resume.json" not in result["source_files_loaded"]

        # Verify Trace for missing file
        traces = registry.get_traces()
        missing_trace = next(t for t in traces if t["type"] == "SOURCE_MISSING")
        assert "resume.json" in missing_trace["details"]["file"]

    def test_malformed_json_handling(self, mock_config, resources):
        """Verify invalid JSON doesn't crash the agent."""
        buffer, registry = resources

        with patch("pathlib.Path.exists", return_value=True):
            # Mock open to return garbage
            with patch("builtins.open", mock_open(read_data="{ invalid json ")):
                agent = HOP3SenderGroundingAgent()
                agent.run_phase(buffer, registry)

        # Result should exist but be empty/partial
        result = buffer.read("hop3_sender_grounding")
        assert result["source_files_loaded"] == []

        # Verify Error Trace
        traces = registry.get_traces()
        error_trace = next(t for t in traces if t["type"] == "DATA_ERROR")
        assert "Invalid JSON" in error_trace["details"]["error"]
