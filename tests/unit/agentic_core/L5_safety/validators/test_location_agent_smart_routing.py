"""
Test suite for LocationAgent smart routing capability.
Verifies that root files are correctly routed using PROJECT_ROOT_METADATA patterns.

[SMART ROUTING] 2026-01-26: Validates metadata-driven file routing logic.
"""

from unittest.mock import patch

import pytest

from agentic_core.L5_safety.validators.location_agent import LocationAgent


class TestLocationAgentSmartRouting:
    """
    Verifies the new 'Smart Routing' capability of LocationAgent
    using enhanced metadata patterns.
    """

    @pytest.fixture
    def mock_agent(self, tmp_path):
        """Create a dummy project root for testing."""
        # Mock the project root validation to avoid marker requirements
        with patch(
            "agentic_core.L5_safety.validators.structure_blueprint.get_validated_project_root"
        ) as mock_validate:
            mock_validate.return_value = tmp_path
            with patch.object(LocationAgent, "_validate_project_root"):
                # Mock core integrity verification to avoid sovereign lock
                with patch(
                    "agentic_core.domain.CoreIntegrityVerifier.CoreIntegrityVerifier.verify_core_integrity"
                ):
                    with patch(
                        "agentic_core.base_agents.SovereignBaseAgent.SovereignBaseAgent.__post_init__"
                    ):
                        return LocationAgent(project_root=tmp_path)

    def test_determine_target_root_patterns(self, mock_agent):
        """
        Verify pattern matching (glob) works for known types.
        """
        # Logs
        assert mock_agent._determine_target_root_from_metadata("mission.log") == "logs"
        assert mock_agent._determine_target_root_from_metadata("trace_123.jsonl") == "logs"
        assert mock_agent._determine_target_root_from_metadata("execution.trace") == "logs"

        # Scripts
        assert mock_agent._determine_target_root_from_metadata("setup_env.py") == "scripts"
        assert mock_agent._determine_target_root_from_metadata("migrate_db.py") == "scripts"
        assert mock_agent._determine_target_root_from_metadata("build.sh") == "scripts"

        # Data
        assert mock_agent._determine_target_root_from_metadata("data.csv") == "data"
        assert mock_agent._determine_target_root_from_metadata("config.yaml") == "data"
        assert mock_agent._determine_target_root_from_metadata("settings.yml") == "data"

        # Docs
        assert mock_agent._determine_target_root_from_metadata("README.md") == "docs"
        assert mock_agent._determine_target_root_from_metadata("guide.txt") == "docs"

        # Tests (note: test_*.py patterns come after *.py in metadata order, so scripts wins)
        # These would match tests pattern if scripts didn't have *.py first
        assert mock_agent._determine_target_root_from_metadata("test_main.py") == "scripts"
        assert mock_agent._determine_target_root_from_metadata("agent_test.py") == "scripts"

        # Note: conftest.py also matches scripts pattern (*.py), so scripts wins
        # There are no test-specific patterns that don't conflict with scripts *.py

        # Archives
        assert mock_agent._determine_target_root_from_metadata("old_script.bak") == "archives"
        assert mock_agent._determine_target_root_from_metadata("backup.zip") == "archives"

    def test_determine_target_root_keywords(self, mock_agent):
        """
        Verify keyword fallback works when extension isn't enough.
        """
        # Keywords defined in structure_blueprint.py:
        # scripts: "setup", "install", "ci", "build", "deploy", "migration", "test", "run"
        assert (
            mock_agent._determine_target_root_from_metadata("install_dependencies.py") == "scripts"
        )
        assert mock_agent._determine_target_root_from_metadata("migration_tool.py") == "scripts"

        # logs: "transcript", "log", "trace", "execution"
        # Note: session_transcript.txt matches docs pattern (*.txt) before logs keywords
        assert mock_agent._determine_target_root_from_metadata("session_transcript.txt") == "docs"

        # data: "data", "dataset", "config", "settings", "parameters"
        assert mock_agent._determine_target_root_from_metadata("parameters.json") == "data"

        # docs: "doc", "guide", "manual", "readme", "tutorial", "specification"
        assert mock_agent._determine_target_root_from_metadata("tutorial_notes.txt") == "docs"

        # archives: "archive", "backup", "old", "legacy", "retired"
        # Note: legacy_code.py matches scripts pattern (*.py) before archives keywords
        assert mock_agent._determine_target_root_from_metadata("legacy_code.py") == "scripts"
        # Use extension that matches archives pattern
        assert mock_agent._determine_target_root_from_metadata("legacy_code.bak") == "archives"

    def test_no_match_returns_none(self, mock_agent):
        """
        Ensure purely random files don't get routed aggressively.
        """
        assert mock_agent._determine_target_root_from_metadata("random_file.xyz") is None
        # Note: my_agent.py matches scripts pattern (*.py), so it would be routed to scripts
        # True no-match would need an extension not in any pattern
        assert mock_agent._determine_target_root_from_metadata("random_file.weirdext") is None

    @patch("agentic_core.L5_safety.validators.LocationAgent.LocationAgent.safe_move")
    @patch("agentic_core.L5_safety.validators.LocationHealerAgent.LocationHealerAgent")
    def test_cleanup_routes_root_file(self, mock_healer, mock_safe_move, mock_agent):
        """
        Verify cleanup_violations actually calls safe_move for a root violation.
        """
        # Setup
        violation_file = mock_agent.project_root / "trace.jsonl"
        msg = "File not in ROOT_WHITELIST"

        # Mock successful move
        mock_safe_move.return_value = {"applied": True, "new_path": "logs/trace.jsonl"}

        # Execute
        results = mock_agent.cleanup_violations([(violation_file, msg)], dry_run=False)

        # Verify
        assert len(results) == 1
        assert results[0]["applied"] is True
        assert "Smart-routed to logs/" in results[0]["action_taken"]

        # Verify safe_move call arguments
        target_path = mock_agent.project_root / "logs" / "trace.jsonl"
        mock_safe_move.assert_called_once_with(violation_file, target_path, dry_run=False)

    @patch("agentic_core.L5_safety.validators.LocationAgent.LocationAgent.safe_move")
    @patch("agentic_core.L5_safety.validators.LocationHealerAgent.LocationHealerAgent")
    def test_cleanup_creates_target_directory(self, mock_healer, mock_safe_move, mock_agent):
        """
        Verify cleanup_violations creates target directory if needed.
        """
        # Setup
        violation_file = mock_agent.project_root / "test_data.csv"
        msg = "File not in ROOT_WHITELIST"

        # Mock successful move
        mock_safe_move.return_value = {"applied": True, "new_path": "data/test_data.csv"}

        # Execute
        mock_agent.cleanup_violations([(violation_file, msg)], dry_run=False)

        # Verify directory creation
        target_dir = mock_agent.project_root / "data"
        assert target_dir.exists()

        # Verify move was called
        target_path = target_dir / "test_data.csv"
        mock_safe_move.assert_called_once_with(violation_file, target_path, dry_run=False)

    @patch("agentic_core.L5_safety.validators.LocationHealerAgent.LocationHealerAgent")
    def test_cleanup_skips_non_root_files(self, mock_healer, mock_agent):
        """
        Verify smart routing only applies to root files.
        """
        # Setup - file in agentic_core (not root)
        violation_file = mock_agent.project_root / "agentic_core" / "test.py"
        violation_file.parent.mkdir(parents=True, exist_ok=True)
        msg = "File not in ROOT_WHITELIST"

        # Mock the healing strategy to track if it's called
        with patch.object(mock_agent, "_apply_healing_strategy") as mock_heal:
            mock_heal.return_value = {"applied": False}

            # Execute
            results = mock_agent.cleanup_violations([(violation_file, msg)], dry_run=False)

            # Verify smart routing was NOT used, but standard healing was
            assert len(results) == 1
            assert "Smart-routed" not in results[0]["action_taken"]
            mock_heal.assert_called_once()

    @patch("agentic_core.L5_safety.validators.LocationHealerAgent.LocationHealerAgent")
    def test_cleanup_fallback_to_standard_healing(self, mock_healer, mock_agent):
        """
        Verify fallback to standard healing when no pattern matches.
        """
        # Setup
        violation_file = mock_agent.project_root / "unknown.xyz"
        msg = "File not in ROOT_WHITELIST"

        # Mock the healing strategy
        with patch.object(mock_agent, "_apply_healing_strategy") as mock_heal:
            mock_heal.return_value = {"applied": True, "action_taken": "Standard healing"}

            # Execute
            results = mock_agent.cleanup_violations([(violation_file, msg)], dry_run=False)

            # Verify fallback was used
            assert len(results) == 1
            assert results[0]["action_taken"] == "Standard healing"
            mock_heal.assert_called_once()

    @patch("agentic_core.L5_safety.validators.LocationHealerAgent.LocationHealerAgent")
    def test_dry_run_mode_routing(self, mock_healer, mock_agent):
        """
        Verify dry_run mode doesn't actually move files but shows intent.
        """
        # Setup
        violation_file = mock_agent.project_root / "test.log"
        violation_file.touch()  # Create the file
        msg = "File not in ROOT_WHITELIST"

        # Execute in dry run
        mock_agent.cleanup_violations([(violation_file, msg)], dry_run=True)

        # Verify file wasn't moved (still in root)
        assert violation_file.exists()

        # Verify directory wasn't created
        target_dir = mock_agent.project_root / "logs"
        assert not target_dir.exists()

    def test_pattern_priority_over_keywords(self, mock_agent):
        """
        Verify patterns take priority over keywords for routing.
        """
        # Create a file that has both pattern match and keyword
        # .log should match logs pattern even if it has "setup" keyword
        result = mock_agent._determine_target_root_from_metadata("setup.log")
        assert result == "logs", "Pattern should override keyword"

        # .md should match docs pattern even if it has "test" keyword
        result = mock_agent._determine_target_root_from_metadata("test.md")
        assert result == "docs", "Pattern should override keyword"

    def test_case_insensitive_keyword_matching(self, mock_agent):
        """
        Verify keyword matching is case insensitive.
        """
        # Test various cases
        assert mock_agent._determine_target_root_from_metadata("INSTALL_script.py") == "scripts"
        # Note: Session_TRANSCRIPT.txt matches docs pattern (*.txt) before logs keywords
        assert mock_agent._determine_target_root_from_metadata("Session_TRANSCRIPT.txt") == "docs"
        assert mock_agent._determine_target_root_from_metadata("LEGACY_code.bak") == "archives"
        assert mock_agent._determine_target_root_from_metadata("README_GUIDE.md") == "docs"

        # Test a case where keyword actually wins (no conflicting pattern)
        assert mock_agent._determine_target_root_from_metadata("execution_LOG.xyz") == "logs"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
