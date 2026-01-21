"""
Phase 2 Tests for HierarchyAgent Apps Flattening and Test Categorization

Tests verify:
1. Apps files are flattened to target depth
2. Test files are categorized by naming patterns
3. Auto-approve sovereignty switch applies to Phase 2 logic
"""

from unittest.mock import patch

import pytest

from agentic_core.L5_safety.validators.HierarchyAgent import HierarchyAgent


class TestHierarchyAgentPhase2:
    @pytest.fixture
    def mock_project(self, tmp_path):
        """Setup project with apps and tests violations."""
        # 1. Setup apps_shared violation (Too deep)
        apps_dir = tmp_path / "apps_shared" / "utils" / "deep_nesting"
        apps_dir.mkdir(parents=True)
        (apps_dir / "deep_script.py").write_text("# Deep script")

        # 2. Setup tests violation (Uncategorized)
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_login_e2e.py").write_text("# E2E test")
        (tests_dir / "test_math_unit.py").write_text("# Unit test")
        (tests_dir / "test_api_integration.py").write_text("# Integration test")

        # 3. Setup whitelisted root file (should not be moved)
        (tests_dir / "conftest.py").write_text("# Pytest config")

        return tmp_path

    def test_apps_flattening(self, mock_project):
        """Test Case 2.1: Verify apps files are flattened to target depth."""
        agent = HierarchyAgent(mock_project, healing_enabled=True, auto_approve=True)
        results = agent.relocate_misplaced_files()

        # apps_shared depth is 2.
        # Source: apps_shared/utils/deep_nesting/deep_script.py (Depth 3)
        # Target: apps_shared/utils/deep_script.py (Depth 2)
        target_file = mock_project / "apps_shared" / "utils" / "deep_script.py"
        source_file = mock_project / "apps_shared" / "utils" / "deep_nesting" / "deep_script.py"

        assert target_file.exists(), "File was not flattened to target depth"
        assert not source_file.exists(), "Source file still exists after flattening"
        assert results["violations_found"] >= 1
        assert results["files_relocated"] >= 1

    def test_test_categorization(self, mock_project):
        """Test Case 2.2: Verify test files are moved to type-specific subfolders."""
        agent = HierarchyAgent(mock_project, healing_enabled=True, auto_approve=True)
        results = agent.relocate_misplaced_files()

        # Verify e2e move
        assert (mock_project / "tests" / "e2e" / "test_login_e2e.py").exists(), (
            "E2E test not categorized"
        )
        # Verify default unit move
        assert (mock_project / "tests" / "unit" / "test_math_unit.py").exists(), (
            "Unit test not categorized"
        )
        # Verify integration move
        assert (mock_project / "tests" / "integration" / "test_api_integration.py").exists(), (
            "Integration test not categorized"
        )

        # Ensure root is clean
        assert not (mock_project / "tests" / "test_login_e2e.py").exists()
        assert not (mock_project / "tests" / "test_math_unit.py").exists()
        assert not (mock_project / "tests" / "test_api_integration.py").exists()

        # Verify whitelisted file stays at root
        assert (mock_project / "tests" / "conftest.py").exists(), "Whitelisted file was moved"

        assert results["violations_found"] >= 3
        assert results["files_relocated"] >= 3

    def test_auto_approve_honored_in_phase2(self, mock_project):
        """Test Case 2.3: Verify sovereignty switch applies to new Phase 2 logic."""
        # This confirms that logic added in Phase 2 still respects the Phase 1 auto_approve flag.
        agent = HierarchyAgent(mock_project, healing_enabled=True, auto_approve=True)

        with patch("builtins.input", side_effect=Exception("Should not prompt!")):
            results = agent.relocate_misplaced_files()

        # Should have moved apps file + test files without prompting
        assert results["files_relocated"] >= 4, (
            f"Expected at least 4 relocations, got {results['files_relocated']}"
        )

    def test_test_categorization_patterns(self, mock_project):
        """Test Case 2.4: Verify different naming patterns are categorized correctly."""
        tests_dir = mock_project / "tests"

        # Create various test patterns
        (tests_dir / "test_functional_checkout.py").write_text("# Functional test")
        (tests_dir / "fixture_data.py").write_text("# Fixture")
        (tests_dir / "test_e2e_workflow.py").write_text("# E2E by pattern")

        agent = HierarchyAgent(mock_project, healing_enabled=True, auto_approve=True)
        agent.relocate_misplaced_files()

        # Verify categorization
        assert (mock_project / "tests" / "functional" / "test_functional_checkout.py").exists()
        assert (mock_project / "tests" / "fixtures" / "fixture_data.py").exists()
        assert (mock_project / "tests" / "e2e" / "test_e2e_workflow.py").exists()

    def test_apps_multiple_roots(self, mock_project):
        """Test Case 2.5: Verify apps flattening works across multiple apps_* roots."""
        # Setup apps_rg violation
        apps_rg_dir = mock_project / "apps_rg" / "engines" / "utils" / "nested"
        apps_rg_dir.mkdir(parents=True)
        (apps_rg_dir / "nested_tool.py").write_text("# Nested tool")

        agent = HierarchyAgent(mock_project, healing_enabled=True, auto_approve=True)
        results = agent.relocate_misplaced_files()

        # Should flatten both apps_shared and apps_rg
        assert (mock_project / "apps_rg" / "engines" / "nested_tool.py").exists()
        apps_roots = [r for r in results["roots_processed"] if r.startswith("apps_")]
        assert len(apps_roots) >= 2

    def test_dry_run_phase2(self, mock_project):
        """Test Case 2.6: Verify dry-run prevents Phase 2 moves."""
        agent = HierarchyAgent(mock_project, healing_enabled=False, auto_approve=True)

        results = agent.relocate_misplaced_files()

        # Should detect violations but not move
        # Note: Only apps violations are detected in dry-run since test categorization requires healing_enabled
        assert results["violations_found"] >= 1
        assert results["files_relocated"] == 0

        # Files should still be at original locations
        assert (mock_project / "apps_shared" / "utils" / "deep_nesting" / "deep_script.py").exists()
        assert (mock_project / "tests" / "test_login_e2e.py").exists()
