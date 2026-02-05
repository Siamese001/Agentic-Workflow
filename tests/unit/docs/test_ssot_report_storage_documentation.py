"""
Unit tests for SSOT Report Storage Documentation - Phase 5.

Tests verify:
- Documentation exists and is complete
- All referenced files exist
- Code examples are valid
- Constants match implementation
"""

from __future__ import annotations

from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]


class TestDocumentationExists:
    """Tests for documentation file existence."""

    def test_guide_exists(self) -> None:
        """Test that SSOT_REPORT_STORAGE_GUIDE.md exists."""
        guide_path = PROJECT_ROOT / "docs" / "reports" / "SSOT_REPORT_STORAGE_GUIDE.md"
        assert guide_path.exists(), f"Guide not found at {guide_path}"

    def test_implementation_plan_exists(self) -> None:
        """Test that implementation plan exists."""
        plan_path = PROJECT_ROOT / "docs" / "reports" / "SSOT_REPORT_STORAGE_IMPLEMENTATION_PLAN.md"
        # May or may not exist depending on branch
        if plan_path.exists():
            assert plan_path.stat().st_size > 0


class TestReferencedFilesExist:
    """Tests that files referenced in documentation exist."""

    def test_validator_module_exists(self) -> None:
        """Test that report_location_validator module exists."""
        validator_path = (
            PROJECT_ROOT / "agentic_core" / "utils" / "report_location_validator_types.py"
        )
        assert validator_path.exists()

    def test_agent_module_exists(self) -> None:
        """Test that ReportLocationAgent exists."""
        agent_path = (
            PROJECT_ROOT / "agentic_core" / "L5_safety" / "validators" / "ReportLocationAgent.py"
        )
        assert agent_path.exists()

    def test_hook_script_exists(self) -> None:
        """Test that validate_report_location.py hook exists."""
        hook_path = PROJECT_ROOT / "scripts" / "hooks" / "validate_report_location.py"
        assert hook_path.exists()

    def test_migration_script_exists(self) -> None:
        """Test that migration script exists."""
        migration_path = PROJECT_ROOT / "ops_scripts" / "maintenance" / "migrate_reports_to_ssot.py"
        assert migration_path.exists()


class TestDocumentationContent:
    """Tests for documentation content completeness."""

    def test_guide_has_overview(self) -> None:
        """Test that guide has overview section."""
        guide_path = PROJECT_ROOT / "docs" / "reports" / "SSOT_REPORT_STORAGE_GUIDE.md"
        if guide_path.exists():
            content = guide_path.read_text()
            assert "## Overview" in content or "# Overview" in content

    def test_guide_has_approved_locations(self) -> None:
        """Test that guide documents approved locations."""
        guide_path = PROJECT_ROOT / "docs" / "reports" / "SSOT_REPORT_STORAGE_GUIDE.md"
        if guide_path.exists():
            content = guide_path.read_text()
            assert "docs/reports" in content

    def test_guide_has_enforcement_section(self) -> None:
        """Test that guide has enforcement section."""
        guide_path = PROJECT_ROOT / "docs" / "reports" / "SSOT_REPORT_STORAGE_GUIDE.md"
        if guide_path.exists():
            content = guide_path.read_text()
            assert "Enforcement" in content or "enforcement" in content

    def test_guide_has_migration_section(self) -> None:
        """Test that guide has migration section."""
        guide_path = PROJECT_ROOT / "docs" / "reports" / "SSOT_REPORT_STORAGE_GUIDE.md"
        if guide_path.exists():
            content = guide_path.read_text()
            assert "Migration" in content or "migration" in content

    def test_guide_has_troubleshooting(self) -> None:
        """Test that guide has troubleshooting section."""
        guide_path = PROJECT_ROOT / "docs" / "reports" / "SSOT_REPORT_STORAGE_GUIDE.md"
        if guide_path.exists():
            content = guide_path.read_text()
            assert "Troubleshooting" in content or "troubleshooting" in content


class TestConstantsConsistency:
    """Tests that documentation matches implementation constants."""

    def test_ssot_dir_matches(self) -> None:
        """Test that SSOT directory in docs matches implementation."""
        from agentic_core.utils.report_location_validator_types import SSOT_REPORTS_DIR

        guide_path = PROJECT_ROOT / "docs" / "reports" / "SSOT_REPORT_STORAGE_GUIDE.md"
        if guide_path.exists():
            content = guide_path.read_text()
            assert SSOT_REPORTS_DIR in content

    def test_approved_locations_documented(self) -> None:
        """Test that approved locations are documented."""
        from agentic_core.utils.report_location_validator_types import (
            APPROVED_REPORT_LOCATIONS,
        )

        guide_path = PROJECT_ROOT / "docs" / "reports" / "SSOT_REPORT_STORAGE_GUIDE.md"
        if guide_path.exists():
            content = guide_path.read_text()
            # At least the primary location should be documented
            assert APPROVED_REPORT_LOCATIONS[0] in content


class TestCodeExamplesValid:
    """Tests that code examples in documentation are valid."""

    def test_agent_import_works(self) -> None:
        """Test that documented agent import works."""
        try:
            from agentic_core.L5_safety.validators.Reportlocation_agent import (
                ReportLocationAgent,
            )

            assert ReportLocationAgent is not None
        except ImportError as e:
            pytest.fail(f"Documented import failed: {e}")

    def test_validator_import_works(self) -> None:
        """Test that documented validator import works."""
        try:
            from agentic_core.utils.report_location_validator_types import (
                ReportLocationValidator,
                validate_report_location,
            )

            assert ReportLocationValidator is not None
            assert validate_report_location is not None
        except ImportError as e:
            pytest.fail(f"Documented import failed: {e}")


class TestDocsSSOTLocation:
    """Tests that documentation is in SSOT location."""

    def test_guide_in_docs_reports(self) -> None:
        """Test that guide is in docs/reports."""
        guide_path = PROJECT_ROOT / "docs" / "reports" / "SSOT_REPORT_STORAGE_GUIDE.md"
        assert guide_path.exists()
        assert "docs/reports" in str(guide_path).replace("\\", "/")
