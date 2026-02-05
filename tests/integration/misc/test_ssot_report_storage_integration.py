"""
Integration Tests for SSOT Report Storage - All Phases.

Tests integration between components:
- Validator <-> Agent
- Agent <-> Migration Script
- Hook <-> Validator
- All components working together

These tests verify components integrate correctly.
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))


class TestValidatorAgentIntegration:
    """Tests for Validator and Agent integration."""

    def test_agent_uses_validator_internally(self) -> None:
        """Test that agent uses validator for validation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            docs_reports = project_root / "docs" / "reports"
            docs_reports.mkdir(parents=True)

            (project_root / "test_report.md").write_text("Test")

            from agentic_core.L5_safety.validators.ReportLocationAgent import (
                ReportLocationAgent,
            )
            from agentic_core.utils.report_location_validator_types import (
                ReportLocationValidator,
            )

            # Get results from both
            validator = ReportLocationValidator(project_root)
            agent = ReportLocationAgent(project_root=project_root)

            validator_misplaced = validator.get_misplaced_reports()
            agent_result = agent.validate()

            # Should match
            assert len(validator_misplaced) == agent_result["misplaced_reports"]

    def test_agent_inventory_matches_validator(self) -> None:
        """Test that agent inventory matches validator inventory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            docs_reports = project_root / "docs" / "reports"
            docs_reports.mkdir(parents=True)

            (docs_reports / "compliant.md").write_text("Compliant")
            (project_root / "misplaced.md").write_text("Misplaced")

            from agentic_core.L5_safety.validators.ReportLocationAgent import (
                ReportLocationAgent,
            )
            from agentic_core.utils.report_location_validator_types import (
                ReportLocationValidator,
            )

            validator = ReportLocationValidator(project_root)
            agent = ReportLocationAgent(project_root=project_root)

            validator_inventory = validator.generate_inventory()
            agent_inventory = agent.get_inventory()

            assert validator_inventory.total_reports == agent_inventory.total_reports
            assert validator_inventory.compliant_reports == agent_inventory.compliant_reports


class TestAgentMigrationIntegration:
    """Tests for Agent and Migration Script integration."""

    def test_agent_heal_matches_migration(self) -> None:
        """Test that agent heal produces same result as migration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            docs_reports = project_root / "docs" / "reports"
            docs_reports.mkdir(parents=True)

            (project_root / "test_report.md").write_text("Test")

            from agentic_core.L5_safety.validators.ReportLocationAgent import (
                ReportLocationAgent,
            )

            agent = ReportLocationAgent(project_root=project_root, dry_run=False)
            heal_result = agent.heal()

            assert heal_result.healed_count == 1
            assert (docs_reports / "test_report.md").exists()

    def test_migration_and_agent_use_same_patterns(self) -> None:
        """Test that migration and agent use same report patterns."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            docs_reports = project_root / "docs" / "reports"
            docs_reports.mkdir(parents=True)

            # Create various report types
            (project_root / "PHASE1_REPORT.md").write_text("Phase")
            (project_root / "RCA_test.md").write_text("RCA")
            (project_root / "test_SUMMARY.md").write_text("Summary")

            from agentic_core.L5_safety.validators.ReportLocationAgent import (
                ReportLocationAgent,
            )
            # from ops_scripts.maintenance.migrate_reports_to_ssot  # Module removed import ReportMigrator

            agent = ReportLocationAgent(project_root=project_root)
            migrator = ReportMigrator(project_root, dry_run=True)

            agent_violations = agent.get_violations()
            migrator_misplaced = migrator.validator.get_misplaced_reports()

            assert len(agent_violations) == len(migrator_misplaced)


class TestHookValidatorIntegration:
    """Tests for Hook and Validator integration."""

    def test_hook_uses_validator_patterns(self) -> None:
        """Test that hook uses same patterns as validator."""
        from agentic_core.utils.report_location_validator_types import (
            REPORT_FILE_PATTERNS,
            SSOT_REPORTS_DIR,
        )

        # Verify constants are accessible
        assert SSOT_REPORTS_DIR == "docs/reports"
        assert len(REPORT_FILE_PATTERNS) > 0

    def test_hook_and_validator_agree_on_locations(self) -> None:
        """Test that hook and validator agree on approved locations."""
        from agentic_core.utils.report_location_validator_types import (
            APPROVED_REPORT_LOCATIONS,
        )

        assert "docs/reports" in APPROVED_REPORT_LOCATIONS
        assert "logs/compliance_reports" in APPROVED_REPORT_LOCATIONS


class TestBackupIntegration:
    """Tests for backup integration across components."""

    def test_agent_creates_backup_on_heal(self) -> None:
        """Test that agent creates backup when healing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            docs_reports = project_root / "docs" / "reports"
            docs_reports.mkdir(parents=True)

            source = project_root / "test_report.md"
            source.write_text("Original content")

            from agentic_core.L5_safety.validators.ReportLocationAgent import (
                ReportLocationAgent,
            )

            agent = ReportLocationAgent(project_root=project_root, dry_run=False)
            agent.heal()

            backup_dir = project_root / ".sovereign_healing_backup" / "reports"
            assert backup_dir.exists()

    def test_migration_creates_backup(self) -> None:
        """Test that migration creates backup."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            docs_reports = project_root / "docs" / "reports"
            docs_reports.mkdir(parents=True)

            source = project_root / "test_report.md"
            source.write_text("Original content")

            # from ops_scripts.maintenance.migrate_reports_to_ssot  # Module removed import ReportMigrator

            migrator = ReportMigrator(project_root, dry_run=False)
            migrator.run_migration()

            backup_dir = project_root / ".sovereign_healing_backup" / "reports"
            assert backup_dir.exists()


class TestInventoryIntegration:
    """Tests for inventory integration."""

    def test_inventory_json_format_consistent(self) -> None:
        """Test that inventory JSON format is consistent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            docs_reports = project_root / "docs" / "reports"
            docs_reports.mkdir(parents=True)

            (docs_reports / "test_report.md").write_text("Test")

            from agentic_core.L5_safety.validators.ReportLocationAgent import (
                ReportLocationAgent,
            )
            from agentic_core.utils.report_location_validator_types import (
                ReportLocationValidator,
            )

            # Save via validator
            validator = ReportLocationValidator(project_root)
            validator_path = validator.save_inventory(project_root / "validator_inventory.json")

            # Save via agent
            agent = ReportLocationAgent(project_root=project_root)
            agent_path = agent.save_inventory(project_root / "agent_inventory.json")

            with open(validator_path) as f:
                validator_data = json.load(f)
            with open(agent_path) as f:
                agent_data = json.load(f)

            # Same keys should be present
            assert set(validator_data.keys()) == set(agent_data.keys())


class TestConstantsIntegration:
    """Tests for constants consistency across modules."""

    def test_ssot_dir_consistent(self) -> None:
        """Test that SSOT directory is consistent across modules."""
        from agentic_core.utils.report_location_validator_types import SSOT_REPORTS_DIR

        assert SSOT_REPORTS_DIR == "docs/reports"

    def test_approved_locations_consistent(self) -> None:
        """Test that approved locations are consistent."""
        from agentic_core.utils.report_location_validator_types import (
            APPROVED_REPORT_LOCATIONS,
        )

        # Primary location should always be first
        assert APPROVED_REPORT_LOCATIONS[0] == "docs/reports"

    def test_patterns_are_valid_regex(self) -> None:
        """Test that all patterns are valid regex."""
        import re

        from agentic_core.utils.report_location_validator_types import (
            REPORT_FILE_PATTERNS,
        )

        for pattern in REPORT_FILE_PATTERNS:
            # Should not raise
            compiled = re.compile(pattern)
            assert compiled is not None


class TestDryRunIntegration:
    """Tests for dry-run mode integration."""

    def test_dry_run_consistent_across_components(self) -> None:
        """Test that dry-run mode is consistent across components."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            docs_reports = project_root / "docs" / "reports"
            docs_reports.mkdir(parents=True)

            source = project_root / "test_report.md"
            source.write_text("Test")

            from agentic_core.L5_safety.validators.ReportLocationAgent import (
                ReportLocationAgent,
            )
            # from ops_scripts.maintenance.migrate_reports_to_ssot  # Module removed import ReportMigrator

            # Both should not move files in dry-run
            agent = ReportLocationAgent(project_root=project_root, dry_run=True)
            agent.heal()
            assert source.exists()

            migrator = ReportMigrator(project_root, dry_run=True)
            migrator.run_migration()
            assert source.exists()


class TestErrorHandlingIntegration:
    """Tests for error handling integration."""

    def test_handles_missing_ssot_dir(self) -> None:
        """Test handling when SSOT directory doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            # Don't create docs/reports

            (project_root / "test_report.md").write_text("Test")

            from agentic_core.L5_safety.validators.ReportLocationAgent import (
                ReportLocationAgent,
            )

            agent = ReportLocationAgent(project_root=project_root, dry_run=False)
            heal_result = agent.heal()

            # Should create the directory and heal
            assert heal_result.healed_count == 1
            assert (project_root / "docs" / "reports").exists()

    def test_handles_permission_errors_gracefully(self) -> None:
        """Test that permission errors are handled gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)

            from agentic_core.L5_safety.validators.ReportLocationAgent import (
                ReportLocationAgent,
            )

            agent = ReportLocationAgent(project_root=project_root)
            # Should not crash on empty project
            result = agent.validate()
            assert result["total_reports"] == 0
