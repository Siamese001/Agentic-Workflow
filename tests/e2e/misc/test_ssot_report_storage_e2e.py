"""
End-to-End Tests for SSOT Report Storage - All Phases.

Tests the complete workflow from discovery through enforcement:
- Phase 1: Foundation & Discovery
- Phase 2: Controlled Migration
- Phase 3: Enforcement Activation
- Phase 4: Agent Integration
- Phase 5: Hardening & Documentation

These tests verify the entire system works together correctly.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))


class TestE2EDiscoveryToEnforcement:
    """E2E tests for the complete discovery to enforcement workflow."""

    def test_full_workflow_empty_project(self) -> None:
        """Test full workflow on empty project."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            docs_reports = project_root / "docs" / "reports"
            docs_reports.mkdir(parents=True)

            from agentic_core.L5_safety.validators.ReportLocationAgent import (
                ReportLocationAgent,
            )

            # Step 1: Validate (should find no violations)
            agent = ReportLocationAgent(project_root=project_root)
            result = agent.validate()

            assert result["total_reports"] == 0
            assert result["misplaced_reports"] == 0

    def test_full_workflow_with_violations(self) -> None:
        """Test full workflow with violations present."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            docs_reports = project_root / "docs" / "reports"
            docs_reports.mkdir(parents=True)

            # Create misplaced reports
            (project_root / "PHASE1_REPORT.md").write_text("Phase 1")
            (project_root / "RCA_test.md").write_text("RCA")
            (project_root / "test_SUMMARY.md").write_text("Summary")

            from agentic_core.L5_safety.validators.ReportLocationAgent import (
                ReportLocationAgent,
            )

            # Step 1: Validate
            agent = ReportLocationAgent(project_root=project_root)
            result = agent.validate()

            assert result["total_reports"] == 3
            assert result["misplaced_reports"] == 3
            assert result["compliance_percentage"] == 0.0

            # Step 2: Heal
            agent = ReportLocationAgent(project_root=project_root, dry_run=False)
            heal_result = agent.heal()

            assert heal_result.healed_count == 3

            # Step 3: Verify
            agent = ReportLocationAgent(project_root=project_root)
            result = agent.validate()

            assert result["misplaced_reports"] == 0
            assert result["compliance_percentage"] == 100.0

    def test_full_workflow_mixed_compliance(self) -> None:
        """Test workflow with mixed compliant and non-compliant files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            docs_reports = project_root / "docs" / "reports"
            docs_reports.mkdir(parents=True)

            # Create compliant reports
            (docs_reports / "compliant_report.md").write_text("Compliant")

            # Create misplaced reports
            (project_root / "misplaced_report.md").write_text("Misplaced")

            from agentic_core.L5_safety.validators.ReportLocationAgent import (
                ReportLocationAgent,
            )

            # Validate
            agent = ReportLocationAgent(project_root=project_root)
            result = agent.validate()

            assert result["total_reports"] == 2
            assert result["compliant_reports"] == 1
            assert result["misplaced_reports"] == 1
            assert result["compliance_percentage"] == 50.0


class TestE2EMigrationWorkflow:
    """E2E tests for migration workflow."""

    def test_migration_with_rollback(self) -> None:
        """Test migration and rollback workflow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            docs_reports = project_root / "docs" / "reports"
            docs_reports.mkdir(parents=True)

            # Create misplaced report
            source = project_root / "test_report.md"
            source.write_text("Original content")

            # from ops_scripts.maintenance.migrate_reports_to_ssot  # Module removed import ReportMigrator

            # Migrate
            migrator = ReportMigrator(project_root, dry_run=False)
            manifest = migrator.run_migration()

            assert manifest.migrated_files == 1
            assert not source.exists()
            assert (docs_reports / "test_report.md").exists()

            # Rollback
            manifest_path = migrator.get_manifest_path()
            success = migrator.rollback(manifest_path)

            assert success
            assert source.exists()

    def test_migration_preserves_content(self) -> None:
        """Test that migration preserves file content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            docs_reports = project_root / "docs" / "reports"
            docs_reports.mkdir(parents=True)

            content = "Important report content with special chars: éàü"
            source = project_root / "test_report.md"
            source.write_text(content, encoding="utf-8")

            # from ops_scripts.maintenance.migrate_reports_to_ssot  # Module removed import ReportMigrator

            migrator = ReportMigrator(project_root, dry_run=False)
            migrator.run_migration()

            dest = docs_reports / "test_report.md"
            assert dest.read_text(encoding="utf-8") == content


class TestE2EPreCommitHook:
    """E2E tests for pre-commit hook integration."""

    def test_hook_dry_run_mode(self) -> None:
        """Test hook in dry-run mode."""
        result = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "hooks" / "validate_report_location.py"),
                "--mode",
                "dry-run",
                "--quiet",
            ],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )
        # Dry-run should always succeed
        assert result.returncode == 0

    def test_hook_staged_only_mode(self) -> None:
        """Test hook in staged-only mode."""
        result = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "hooks" / "validate_report_location.py"),
                "--staged-only",
                "--mode",
                "strict",
            ],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )
        # With no staged report files, should pass
        assert result.returncode == 0


class TestE2EAgentIntegration:
    """E2E tests for agent integration."""

    def test_agent_standard_heal_interface(self) -> None:
        """Test agent standard heal interface."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            docs_reports = project_root / "docs" / "reports"
            docs_reports.mkdir(parents=True)

            (project_root / "test_report.md").write_text("Test")

            from agentic_core.L5_safety.validators.ReportLocationAgent import (
                ReportLocationAgent,
            )

            agent = ReportLocationAgent(project_root=project_root, dry_run=True)
            result = agent.standard_heal()

            assert "violations_found" in result
            assert "violations_fixed" in result
            assert "errors" in result
            assert "skipped" in result
            assert result["violations_found"] == 1

    def test_agent_inventory_generation(self) -> None:
        """Test agent inventory generation and saving."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            docs_reports = project_root / "docs" / "reports"
            docs_reports.mkdir(parents=True)

            (docs_reports / "report1.md").write_text("Report 1")
            (project_root / "report2.md").write_text("Report 2")

            from agentic_core.L5_safety.validators.ReportLocationAgent import (
                ReportLocationAgent,
            )

            agent = ReportLocationAgent(project_root=project_root)
            output_path = agent.save_inventory()

            assert output_path.exists()

            with open(output_path) as f:
                data = json.load(f)

            assert data["total_reports"] == 2
            assert data["compliant_reports"] == 1
            assert data["misplaced_reports"] == 1


class TestE2EDocumentation:
    """E2E tests for documentation completeness."""

    def test_all_documentation_exists(self) -> None:
        """Test that all required documentation exists."""
        guide_path = PROJECT_ROOT / "docs" / "reports" / "SSOT_REPORT_STORAGE_GUIDE.md"
        assert guide_path.exists()

    def test_documentation_references_valid(self) -> None:
        """Test that documentation references valid files."""
        guide_path = PROJECT_ROOT / "docs" / "reports" / "SSOT_REPORT_STORAGE_GUIDE.md"

        if guide_path.exists():
            # Check referenced modules exist
            assert (
                PROJECT_ROOT / "agentic_core" / "utils" / "report_location_validator_types.py"
            ).exists()
            assert (
                PROJECT_ROOT
                / "agentic_core"
                / "L5_safety"
                / "validators"
                / "ReportLocationAgent.py"
            ).exists()
            assert (PROJECT_ROOT / "scripts" / "hooks" / "validate_report_location.py").exists()


class TestE2ECompleteSystem:
    """E2E tests for complete system integration."""

    def test_complete_ssot_enforcement_cycle(self) -> None:
        """Test complete SSOT enforcement cycle."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            docs_reports = project_root / "docs" / "reports"
            docs_reports.mkdir(parents=True)

            # Create initial state with violations
            (project_root / "PHASE1_SUMMARY.md").write_text("Phase 1")
            (project_root / "subdir").mkdir()
            (project_root / "subdir" / "nested_report.md").write_text("Nested")

            from agentic_core.L5_safety.validators.ReportLocationAgent import (
                ReportLocationAgent,
            )
            from agentic_core.utils.report_location_validator_types import (
                ReportLocationValidator,
            )

            # Phase 1: Discovery
            validator = ReportLocationValidator(project_root)
            misplaced = validator.get_misplaced_reports()
            assert len(misplaced) == 2

            # Phase 2: Migration (via agent)
            agent = ReportLocationAgent(project_root=project_root, dry_run=False)
            heal_result = agent.heal()
            assert heal_result.healed_count == 2

            # Phase 3: Enforcement verification
            validator = ReportLocationValidator(project_root)
            misplaced = validator.get_misplaced_reports()
            assert len(misplaced) == 0

            # Phase 4: Agent validation
            agent = ReportLocationAgent(project_root=project_root)
            result = agent.validate()
            assert result["compliance_percentage"] == 100.0

            # Phase 5: Inventory saved
            inventory_path = agent.save_inventory()
            assert inventory_path.exists()

            with open(inventory_path) as f:
                inventory = json.load(f)
            assert inventory["misplaced_reports"] == 0
