"""
File: tests/integration/agentic_core/L0_maintenance/test_ssot_orchestration.py
Description: Tests for Dynamic Loading, Signal Handling, and Main Orchestration.
Mandate: 100% Pass.
"""

import pytest
import signal
import sys
from unittest.mock import patch, MagicMock
from agentic_core.L0_maintenance.scripts.execute_ssot import (
    load_agents,
    GracefulExitHandler,
    RuntimeStateManager,
)


class TestOrchestrationLayers:
    @pytest.fixture
    def mock_project_root(self, tmp_path):
        """Creates a dummy project structure with agents."""
        root = tmp_path / "project"
        root.mkdir()

        # Create agentic_core/L5_safety/validators
        validators = root / "agentic_core/L5_safety/validators"
        validators.mkdir(parents=True)

        # Valid Agent
        (validators / "ValidAgent.py").write_text("""
class ValidAgent:
    def heal(self, v): pass
""")

        # Invalid Agent (No heal)
        (validators / "InvalidAgent.py").write_text("""
class InvalidAgent:
    pass
""")

        # Non-Agent Script
        (validators / "script.py").write_text("x = 1")

        return root

    def test_dynamic_agent_discovery(self, mock_project_root):
        """
        Critical: load_agents must only load classes with 'heal' method.
        """
        # Patch sys.modules to avoid polluting real global state
        with patch.dict(sys.modules):
            agents = load_agents(mock_project_root)

        assert "ValidAgent" in agents
        assert "InvalidAgent" not in agents
        assert "script" not in agents
        assert hasattr(agents["ValidAgent"], "heal")

    def test_graceful_exit_handler(self, tmp_path):
        """
        Critical: Signal handler must update state but not crash immediately.
        """
        state_mgr = RuntimeStateManager(tmp_path)
        handler = GracefulExitHandler(state_mgr)

        # Simulate SIGINT
        with patch("sys.exit") as mock_exit:
            handler.exit_gracefully(signal.SIGINT, None)

            # Should set flag
            assert handler.kill_now is True
            # Should update state
            assert state_mgr.state["status"] == "aborted_by_user"
            # Should NOT exit on first signal
            mock_exit.assert_not_called()

            # Simulate Second SIGINT (Force Kill)
            handler.exit_gracefully(signal.SIGINT, None)
            mock_exit.assert_called_with(1)

    def test_main_arg_parsing_validation(self):
        """
        Critical: Main must reject invalid args before starting.
        """
        # We test via the validation function directly since we can't easily capture argparse exit in unit test
        from agentic_core.L0_maintenance.scripts.execute_ssot import validate_territory_input

        valid, msg = validate_territory_input("../traversal")
        assert valid is False

        valid, msg = validate_territory_input("valid_scope")
        assert valid is True

    @patch("agentic_core.L0_maintenance.scripts.execute_ssot.execute_phase1_discovery")
    @patch("agentic_core.L0_maintenance.scripts.execute_ssot.load_agents")
    @patch("agentic_core.L0_maintenance.scripts.execute_ssot.RuntimeStateManager")
    def test_main_flow_aborts_on_empty_agents(self, mock_state_mgr, mock_load, mock_p1, tmp_path):
        """
        Critical: If no agents loaded, abort immediately.
        """
        mock_load.return_value = {}  # Empty

        # Mock the state manager instance
        mock_state_instance = MagicMock()
        mock_state_mgr.return_value = mock_state_instance

        from agentic_core.L0_maintenance.scripts.execute_ssot import main

        with patch("sys.argv", ["script", "--territory", "test"]), patch("sys.exit") as mock_exit:
            # Mock sys.exit to actually raise SystemExit to stop execution
            mock_exit.side_effect = SystemExit(1)

            with pytest.raises(SystemExit):
                main()

            # Should exit 1
            mock_exit.assert_called_with(1)
            # Phase 1 should NOT run
            mock_p1.assert_not_called()
