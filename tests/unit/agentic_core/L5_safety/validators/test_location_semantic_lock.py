import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


# --- PRE-IMPORT MOCKING ---
# Create proper mock base classes to avoid metaclass conflicts
class MockSovereignBaseAgent:
    """Mock SovereignBaseAgent to avoid import dependencies."""

    def __init__(self, *args, **kwargs):
        pass


class MockL5Agent:
    """Mock L5Agent to avoid import dependencies."""

    pass


class MockLocationValidatorAgent:
    """Mock LocationValidatorAgent."""

    def __init__(self, *args, **kwargs):
        self.project_root = kwargs.get("project_root")

    def validate_file_location(self, file_path):
        return (True, "Mock valid")


# Mock the modules BEFORE importing LocationAgent
mock_sovereign_module = MagicMock()
mock_sovereign_module.SovereignBaseAgent = MockSovereignBaseAgent
sys.modules["agentic_core.base_agents.SovereignBaseAgent"] = mock_sovereign_module

mock_l5_module = MagicMock()
mock_l5_module.L5Agent = MockL5Agent
sys.modules["agentic_core.L5_safety.validators.L5Agent"] = mock_l5_module

mock_validator_module = MagicMock()
mock_validator_module.LocationValidatorAgent = MockLocationValidatorAgent
sys.modules["agentic_core.L5_safety.validators.LocationValidatorAgent"] = mock_validator_module

# Now safe to import
from agentic_core.L5_safety.validators.LocationAgent import LocationAgent


class TestLocationSemanticLock:
    """
    Verifies the [CONSTITUTIONAL OVERRIDE 2026-01-22] in LocationAgent.
    Ensures BaseAgents are rejected if not in base_agents/.
    """

    @pytest.fixture
    def location_agent(self):
        """Creates a lightweight LocationAgent with mocked init."""
        # Mock __init__ to avoid loading real Naming/Import agents
        with patch.object(LocationAgent, "__init__", return_value=None):
            agent = LocationAgent(project_root=Path("/fake/project"))
            # Manually set required attributes
            agent.project_root = Path("/fake/project")
            return agent

    def test_base_agent_valid_location(self, location_agent):
        """Should ALLOW SovereignBaseAgent in agentic_core/base_agents/"""
        # Setup path: /fake/project/agentic_core/base_agents/SovereignBaseAgent.py
        valid_path = Path("/fake/project/agentic_core/base_agents/SovereignBaseAgent.py")

        # Mock the import that happens inside validate_file_location method
        with patch(
            "agentic_core.L5_safety.validators.LocationValidatorAgent.LocationValidatorAgent"
        ) as MockValClass:
            mock_validator_instance = MockValClass.return_value
            mock_validator_instance.validate_file_location.return_value = (True, "Valid")

            # Execution
            is_valid, msg = location_agent.validate_file_location(valid_path)

            # Assertions
            assert is_valid is True, f"Should be valid, got: {msg}"
            # Verify it actually called the delegate (meaning it passed the semantic check)
            mock_validator_instance.validate_file_location.assert_called_once()

    def test_base_agent_invalid_location(self, location_agent):
        """Should REJECT SovereignBaseAgent in agentic_core/observability/"""
        # Setup path: /fake/project/agentic_core/observability/SovereignBaseAgent.py
        invalid_path = Path("/fake/project/agentic_core/observability/SovereignBaseAgent.py")

        with patch(
            "agentic_core.L5_safety.validators.LocationValidatorAgent.LocationValidatorAgent"
        ) as MockValClass:
            mock_validator_instance = MockValClass.return_value
            # Even if the validator says "True" (legacy rules), the override should say False
            mock_validator_instance.validate_file_location.return_value = (True, "Legacy Valid")

            # Execution
            is_valid, msg = location_agent.validate_file_location(invalid_path)

            # Assertions
            assert is_valid is False
            assert "CRITICAL" in msg
            assert "base_agents" in msg
            # Verify delegate was NEVER called (short-circuited)
            mock_validator_instance.validate_file_location.assert_not_called()

    def test_layer_base_agent_valid_location(self, location_agent):
        """Should ALLOW L1CognitionBaseAgent in agentic_core/base_agents/"""
        path = Path("/fake/project/agentic_core/base_agents/L1CognitionBaseAgent.py")

        with patch(
            "agentic_core.L5_safety.validators.LocationValidatorAgent.LocationValidatorAgent"
        ) as MockValClass:
            MockValClass.return_value.validate_file_location.return_value = (True, "Valid")
            assert location_agent.validate_file_location(path)[0] is True

    def test_layer_base_agent_invalid_location(self, location_agent):
        """Should REJECT L1CognitionBaseAgent in agentic_core/L1_cognition/"""
        path = Path("/fake/project/agentic_core/L1_cognition/L1CognitionBaseAgent.py")

        with patch(
            "agentic_core.L5_safety.validators.LocationValidatorAgent.LocationValidatorAgent"
        ) as MockValClass:
            # Short-circuit check
            is_valid, msg = location_agent.validate_file_location(path)
            assert is_valid is False
            assert "CRITICAL" in msg

    def test_standard_file_bypass(self, location_agent):
        """Standard files should bypass the lock and go to validator."""
        path = Path("/fake/project/agentic_core/L1_cognition/NormalAgent.py")

        with patch(
            "agentic_core.L5_safety.validators.LocationValidatorAgent.LocationValidatorAgent"
        ) as MockValClass:
            mock_validator_instance = MockValClass.return_value
            mock_validator_instance.validate_file_location.return_value = (True, "Valid")

            is_valid, _ = location_agent.validate_file_location(path)

            assert is_valid is True
            # MUST call delegate
            mock_validator_instance.validate_file_location.assert_called_once()
