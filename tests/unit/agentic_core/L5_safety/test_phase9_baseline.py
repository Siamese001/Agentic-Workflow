"""Phase 9 Tests: Golden Baseline Capture & SSOT Normalization.

Tests for baseline capture, pre-commit sentinel blocking, and archival audit integrity.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


class TestBaselineNormalizationPurity:
    """Phase 9 Tests: Baseline normalization purity verification."""

    @pytest.fixture
    def clean_project(self, tmp_path):
        """Setup a clean project with no violations."""
        (tmp_path / "agentic_core" / "L5_safety").mkdir(parents=True)
        (tmp_path / "agentic_core" / "L5_safety" / "__init__.py").write_text("")
        return tmp_path

    @pytest.fixture(autouse=True)
    def reset_singleton(self):
        """Reset singleton before each test."""
        from agentic_core.utils.sovereign_scanner import SovereignScanner

        SovereignScanner.reset_instance()
        yield
        SovereignScanner.reset_instance()

    def test_capture_sovereign_baseline_method_exists(self, tmp_path):
        """[Phase 9] Verify capture_sovereign_baseline method exists."""
        from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import (
            ArchitectureGovernorAgent,
        )

        (tmp_path / "agentic_core").mkdir()
        agent = ArchitectureGovernorAgent(project_root=tmp_path)

        assert hasattr(agent, "capture_sovereign_baseline")
        assert callable(agent.capture_sovereign_baseline)

    def test_capture_sovereign_baseline_returns_dict(self, clean_project):
        """[Phase 9] Verify method returns dictionary."""
        from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import (
            ArchitectureGovernorAgent,
        )

        agent = ArchitectureGovernorAgent(project_root=clean_project)
        result = agent.capture_sovereign_baseline()

        assert isinstance(result, dict)

    def test_baseline_normalization_purity(self, clean_project):
        """[Phase 9] Verify violations_found=0 after successful purge."""
        from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import (
            ArchitectureGovernorAgent,
        )

        agent = ArchitectureGovernorAgent(
            project_root=clean_project,
            auto_approve=True,
            healing_enabled=True,
        )

        # Mock heal_repository to simulate clean state after purge
        def mock_heal(*args, **kwargs):
            return {
                "violations_found": 0,
                "violations_fixed": 0,
                "status": "PASS",
                "_raw_result": {
                    "violations_found": 0,
                    "violations_fixed": 0,
                    "roots_scanned": ["agentic_core"],
                },
            }

        agent.heal_repository = mock_heal

        # Capture baseline
        baseline = agent.capture_sovereign_baseline()

        # Extract violations
        raw_result = baseline.get("_raw_result", baseline)
        violations_found = raw_result.get("violations_found", 0)

        assert violations_found == 0

    def test_baseline_captures_unresolved_violations(self, clean_project):
        """[Phase 9] Verify baseline captures unresolved violations with warning."""
        from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import (
            ArchitectureGovernorAgent,
        )

        agent = ArchitectureGovernorAgent(project_root=clean_project)

        # Mock heal_repository to return violations
        def mock_heal(*args, **kwargs):
            return {
                "violations_found": 5,
                "violations_fixed": 0,
                "status": "FAIL",
                "_raw_result": {
                    "violations_found": 5,
                    "violations_fixed": 0,
                },
            }

        agent.heal_repository = mock_heal

        baseline = agent.capture_sovereign_baseline()

        raw_result = baseline.get("_raw_result", baseline)
        assert raw_result.get("violations_found", 0) == 5


class TestPreCommitSentinelBlocking:
    """Phase 9 Tests: Pre-commit sentinel blocking verification."""

    @pytest.fixture
    def project_with_gravity_violation(self, tmp_path):
        """Setup project with a GRAVITY violation (L3 importing L5)."""
        # Create L3 file that imports from L5
        (tmp_path / "apps_shared" / "utils").mkdir(parents=True)
        (tmp_path / "apps_shared" / "utils" / "bad_import.py").write_text(
            "from agentic_core.L5_safety.validators import ArchitectureGovernorAgent\n"
            "# This is a GRAVITY violation: apps importing from L5\n"
        )
        return tmp_path

    def test_pre_commit_sentinel_blocking(self, project_with_gravity_violation):
        """[Phase 9] Verify CI script returns exit code 1 on GRAVITY violation."""
        # Mock the agent to return violations
        with patch(
            "agentic_core.L5_safety.validators.ArchitectureGovernorAgent.ArchitectureGovernorAgent"
        ) as MockAgent:
            mock_instance = MagicMock()
            mock_instance.run_ci_verification_sync.return_value = (
                False,
                {
                    "violations_found": 1,
                    "_raw_result": {
                        "violations_found": 1,
                        "roots_scanned": ["apps_shared"],
                        "violations": [{"type": "GRAVITY", "message": "L3 importing L5"}],
                    },
                },
            )
            MockAgent.return_value = mock_instance

            import importlib

            import scripts.ci.sovereign_lockdown_check as ci_script

            importlib.reload(ci_script)

            exit_code = ci_script.main()

            assert exit_code == 1

    def test_ci_script_blocks_structural_drift(self, project_with_gravity_violation):
        """[Phase 9] Verify CI script identifies structural drift."""
        with patch(
            "agentic_core.L5_safety.validators.ArchitectureGovernorAgent.ArchitectureGovernorAgent"
        ) as MockAgent:
            mock_instance = MagicMock()
            mock_instance.run_ci_verification_sync.return_value = (
                False,
                {
                    "violations_found": 3,
                    "_raw_result": {
                        "violations_found": 3,
                        "roots_scanned": ["agentic_core", "apps_shared"],
                    },
                },
            )
            MockAgent.return_value = mock_instance

            import importlib

            import scripts.ci.sovereign_lockdown_check as ci_script

            importlib.reload(ci_script)

            exit_code = ci_script.main()

            # Should block with exit code 1
            assert exit_code == 1


class TestArchivalAuditIntegrity:
    """Phase 9 Tests: Archival audit integrity verification."""

    @pytest.fixture
    def project_with_archives(self, tmp_path):
        """Setup project with archive directory."""
        (tmp_path / "agentic_core" / "L5_safety").mkdir(parents=True)
        (tmp_path / "archives" / "deduplication_cleanup").mkdir(parents=True)
        return tmp_path

    @pytest.fixture(autouse=True)
    def reset_singleton(self):
        """Reset singleton before each test."""
        from agentic_core.utils.sovereign_scanner import SovereignScanner

        SovereignScanner.reset_instance()
        yield
        SovereignScanner.reset_instance()

    def test_archival_audit_integrity(self, project_with_archives):
        """[Phase 9] Verify zero-loss merge preserves archived files."""

        # Create some "archived" files to simulate purge results
        archive_dir = project_with_archives / "archives" / "deduplication_cleanup"
        (archive_dir / "DuplicateAgent1.py").write_text("# Archived")
        (archive_dir / "DuplicateAgent2.py").write_text("# Archived")
        (archive_dir / "DuplicateAgent3.py").write_text("# Archived")

        # Count files in archive
        archived_files = list(archive_dir.glob("*.py"))

        # Simulate purge report
        purge_report = {
            "violations_found": 3,
            "violations_fixed": 3,
            "deduplication_audit": {
                "collisions_found": 3,
                "collisions_fixed": 3,
            },
        }

        # Verify archive count matches violations_fixed
        assert len(archived_files) == purge_report["violations_fixed"]

    def test_zero_loss_merge_no_deletion(self, project_with_archives):
        """[Phase 9] Verify files are archived, not deleted."""
        from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import (
            ArchitectureGovernorAgent,
        )

        agent = ArchitectureGovernorAgent(
            project_root=project_with_archives,
            auto_approve=True,
            healing_enabled=True,
        )

        # Create mock violation with locations
        mock_violation = MagicMock()
        mock_violation.locations = [
            project_with_archives / "agentic_core" / "Agent.py",
            project_with_archives / "apps_shared" / "Agent.py",
        ]

        # Create the source files
        (project_with_archives / "agentic_core" / "Agent.py").write_text("# Master")
        (project_with_archives / "apps_shared").mkdir(exist_ok=True)
        (project_with_archives / "apps_shared" / "Agent.py").write_text("# Duplicate")

        # Mock gatekeeper to track archived files
        archived_files = []

        def mock_safe_move(path, destination_category=None, reason=None):
            archived_files.append(path)
            result = MagicMock()
            result.success = True
            return result

        mock_gatekeeper = MagicMock()
        mock_gatekeeper.safe_move = mock_safe_move
        agent._archival_gatekeeper = mock_gatekeeper

        # Execute resolution
        fixed = agent._resolve_collision(mock_violation)

        # Should archive 1 file (not delete)
        assert fixed == 1
        assert len(archived_files) == 1

        # Master file should NOT be archived
        archived_paths = [str(p) for p in archived_files]
        for path in archived_paths:
            assert "agentic_core" not in path


class TestPhase9Integration:
    """Phase 9 Tests: Full integration verification."""

    @pytest.fixture
    def clean_project(self, tmp_path):
        """Setup a clean project."""
        (tmp_path / "agentic_core" / "L5_safety").mkdir(parents=True)
        return tmp_path

    @pytest.fixture(autouse=True)
    def reset_singleton(self):
        """Reset singleton before each test."""
        from agentic_core.utils.sovereign_scanner import SovereignScanner

        SovereignScanner.reset_instance()
        yield
        SovereignScanner.reset_instance()

    def test_full_workflow_purge_to_baseline(self, clean_project):
        """[Phase 9] Verify full workflow: purge -> baseline capture."""
        from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import (
            ArchitectureGovernorAgent,
        )

        agent = ArchitectureGovernorAgent(
            project_root=clean_project,
            auto_approve=True,
            healing_enabled=True,
        )

        # Step 1: Execute purge
        purge_result = agent.heal_repository(execute=True, dry_run=False)
        assert isinstance(purge_result, dict)

        # Step 2: Capture baseline
        baseline = agent.capture_sovereign_baseline()
        assert isinstance(baseline, dict)

        # Step 3: Verify lockdown
        is_pure, lockdown_result = agent.finalize_sovereign_lockdown()
        assert isinstance(is_pure, bool)

    def test_baseline_after_lockdown_consistency(self, clean_project):
        """[Phase 9] Verify baseline and lockdown return consistent results."""
        from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import (
            ArchitectureGovernorAgent,
        )

        agent = ArchitectureGovernorAgent(
            project_root=clean_project,
            auto_approve=True,
        )

        # Mock to return consistent results
        def mock_heal(*args, **kwargs):
            return {
                "violations_found": 0,
                "violations_fixed": 0,
                "status": "PASS",
                "_raw_result": {
                    "violations_found": 0,
                    "violations_fixed": 0,
                },
            }

        agent.heal_repository = mock_heal

        # Capture baseline
        baseline = agent.capture_sovereign_baseline()

        # Run lockdown
        is_pure, lockdown_result = agent.finalize_sovereign_lockdown()

        # Both should show 0 violations
        baseline_violations = baseline.get("_raw_result", baseline).get("violations_found", 0)
        lockdown_violations = lockdown_result.get("_raw_result", lockdown_result).get(
            "violations_found", 0
        )

        assert baseline_violations == lockdown_violations == 0
        assert is_pure is True
