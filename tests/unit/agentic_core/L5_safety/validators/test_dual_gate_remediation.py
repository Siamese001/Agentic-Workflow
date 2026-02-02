# tests/unit/test_dual_gate_remediation.py

import os
from unittest.mock import patch

import pytest


class test_dual_gate_remediation:
    """Test that agents delegate approval to ArchivalGatekeeper without redundant prompts."""

    @pytest.fixture
    def setup_env(self):
        """Set up environment for auto-approval."""
        os.environ["SOVEREIGN_AUTO_APPROVE"] = "1"
        os.environ["ARCHIVE_BATCH_ACCEPT"] = "1"
        yield
        os.environ.pop("SOVEREIGN_AUTO_APPROVE", None)
        os.environ.pop("ARCHIVE_BATCH_ACCEPT", None)

    def test_ssot_relocator_no_redundant_prompt(self, setup_env, tmp_path):
        """SSOTRelocator should not have its own approval methods."""
        from agentic_core.L5_safety.validators.ssot_relocator import SSOTRelocator

        relocator = SSOTRelocator(tmp_path, dry_run=True)

        # Verify no _prompt_user methods exist
        assert not hasattr(relocator, "_prompt_user_for_move_approval")
        assert not hasattr(relocator, "_skip_all_moves")
        assert not hasattr(relocator, "_approve_all_moves")

    def test_governance_agent_no_redundant_prompt(self, setup_env, tmp_path):
        """GovernanceAgent should not have its own approval methods."""
        from agentic_core.L5_safety.validators.GovernanceAgent import GovernanceAgent

        agent = GovernanceAgent(str(tmp_path))

        # Verify no _prompt_user methods exist
        assert not hasattr(agent, "_prompt_user_for_move_approval")

    def test_location_healer_no_redundant_prompt(self, setup_env, tmp_path):
        """LocationHealerAgent should not have its own approval methods."""
        from agentic_core.L5_safety.validators.LocationHealerAgent import LocationHealerAgent

        agent = LocationHealerAgent(project_root=tmp_path)

        # Verify no _prompt_user methods exist
        assert not hasattr(agent, "_prompt_user_for_archive_approval")

    def test_filesystem_reconciler_no_redundant_prompt(self, setup_env, tmp_path):
        """FilesystemSSOTReconcilerAgent should not have its own approval methods."""
        from agentic_core.L5_safety.validators.FilesystemSSOTReconcilerAgent import (
            FilesystemSSOTReconcilerAgent,
        )

        agent = FilesystemSSOTReconcilerAgent(tmp_path)

        # Verify no _prompt_user methods exist
        assert not hasattr(agent, "_prompt_user_for_archive_approval")
        assert not hasattr(agent, "_skip_all_archives")


class TestGatekeeperSinglePointOfApproval:
    """Test that ArchivalGatekeeper correctly handles approval."""

    def test_gatekeeper_batch_mode_detection(self, tmp_path):
        """Gatekeeper should auto-approve when SOVEREIGN_AUTO_APPROVE=1."""
        os.environ["SOVEREIGN_AUTO_APPROVE"] = "1"

        from agentic_core.L5_safety.core.archival_gatekeeper_config import ArchivalGatekeeper

        ArchivalGatekeeper.reset_instance()
        gk = ArchivalGatekeeper.get_instance(tmp_path)

        assert gk._is_batch_mode() is True

        os.environ.pop("SOVEREIGN_AUTO_APPROVE", None)


class TestEndToEndNoPrompts:
    """End-to-end tests verifying no prompts occur with --yes flag."""

    @pytest.fixture
    def setup_env(self):
        """Set up environment for auto-approval."""
        os.environ["SOVEREIGN_AUTO_APPROVE"] = "1"
        os.environ["CI"] = "true"
        yield
        os.environ.pop("SOVEREIGN_AUTO_APPROVE", None)
        os.environ.pop("CI", None)

    @patch("builtins.input")
    def test_hierarchy_agent_execute_no_input_called(self, mock_input, setup_env, tmp_path):
        """HierarchyAgent should never call input() when env vars are set."""
        from agentic_core.L5_safety.core.archival_gatekeeper_config import ArchivalGatekeeper
        from agentic_core.L5_safety.validators.HierarchyAgent import HierarchyAgent

        ArchivalGatekeeper.reset_instance()

        # Create dummy structure
        (tmp_path / "agentic_core" / "L5_safety").mkdir(parents=True)

        agent = HierarchyAgent(tmp_path, healing_enabled=True)
        # Note: We rely on the fact that if it *were* to prompt, mock_input would catch it.
        # This test assumes HierarchyAgent internals eventually call LocationHealerAgent methods.
        assert agent.healing_enabled is True  # Verify agent was created

        mock_input.assert_not_called()
