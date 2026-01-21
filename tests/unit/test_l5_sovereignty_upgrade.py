"""
L5 Safety Perimeter Universal Sovereignty Tests (Phase 4-6)

Tests verify:
1. Phase 4.1: LocationValidatorAgent scans all SOVEREIGN_REGISTRY roots
2. Phase 4.3: UnifiedStructureValidator gravity maps include tests/apps territories
3. Phase 5.1: FilesystemSSOTReconcilerAgent has sync CI verification
4. Phase 5.2: ssot_folder_check.py CLI works in headless mode
5. Phase 6: HygieneGuardianAgent focuses only on content hygiene
"""

import pytest
from unittest.mock import patch


class TestPhase4PerimeterDetection:
    """Phase 4: Perimeter Detection Upgrade Tests"""

    @pytest.fixture
    def mock_project(self, tmp_path):
        """Setup project with multiple sovereign roots."""
        # Create sovereign roots
        (tmp_path / "agentic_core" / "L0_maintenance").mkdir(parents=True)
        (tmp_path / "agentic_core" / "L5_safety").mkdir(parents=True)
        (tmp_path / "apps_shared").mkdir()
        (tmp_path / "apps_rg").mkdir()
        (tmp_path / "tests" / "unit").mkdir(parents=True)
        (tmp_path / "tests" / "e2e").mkdir(parents=True)

        # Create test files
        (tmp_path / "agentic_core" / "L0_maintenance" / "test.py").write_text("# Test")
        (tmp_path / "apps_shared" / "util.py").write_text("# Util")
        (tmp_path / "tests" / "unit" / "test_example.py").write_text("# Test")

        return tmp_path

    def test_location_validator_universal_scanning(self, mock_project):
        """Test 4.1: Verify LocationValidatorAgent scans all SOVEREIGN_REGISTRY roots."""
        from agentic_core.L5_safety.validators.LocationValidatorAgent import LocationValidatorAgent

        agent = LocationValidatorAgent(project_root=mock_project)
        results = agent.run()

        # Verify multiple roots were scanned
        roots_scanned = results.get("roots_scanned", [])
        assert "agentic_core" in roots_scanned
        assert "apps_shared" in roots_scanned or "apps_rg" in roots_scanned
        assert "tests" in roots_scanned

        # Verify files were scanned
        assert results["total_files_scanned"] >= 3

    def test_location_validator_scripts_isolation(self, mock_project):
        """Test 4.2: Verify AST import isolation for scripts/."""
        from agentic_core.L5_safety.validators.LocationValidatorAgent import LocationValidatorAgent

        # Create scripts folder with violating import
        scripts_dir = mock_project / "scripts"
        scripts_dir.mkdir()
        violating_script = scripts_dir / "bad_script.py"
        violating_script.write_text("from agentic_core.L5_safety import HierarchyAgent\n")

        agent = LocationValidatorAgent(project_root=mock_project)

        # Validate the violating script
        is_valid, reason = agent.validate_file_location(violating_script)

        # Should detect semantic violation
        assert not is_valid or "SEMANTIC VIOLATION" in reason or "forbidden" in reason.lower()


class TestPhase4GravityMaps:
    """Phase 4.3: Gravity Maps Update Tests"""

    def test_gravity_rules_include_apps_territories(self):
        """Test 4.3a: Verify gravity rules include apps_* territories."""
        from agentic_core.L5_safety.unified.UnifiedStructureValidatorAgent import GRAVITY_RULES

        assert "apps_shared" in GRAVITY_RULES
        assert "apps_rg" in GRAVITY_RULES
        assert "apps_lic" in GRAVITY_RULES

        # apps_rg can import from apps_shared
        assert "apps_shared" in GRAVITY_RULES["apps_rg"]

        # apps cannot import from each other's internal modules
        assert "apps_lic" not in GRAVITY_RULES["apps_rg"]

    def test_gravity_rules_include_test_territories(self):
        """Test 4.3b: Verify gravity rules include tests/* territories."""
        from agentic_core.L5_safety.unified.UnifiedStructureValidatorAgent import GRAVITY_RULES

        assert "tests_unit" in GRAVITY_RULES
        assert "tests_integration" in GRAVITY_RULES
        assert "tests_e2e" in GRAVITY_RULES
        assert "tests_functional" in GRAVITY_RULES
        assert "tests_fixtures" in GRAVITY_RULES

        # Tests can import from all core layers
        for layer in ["L0", "L1", "L2", "L3", "L4", "L5", "L6"]:
            assert layer in GRAVITY_RULES["tests_unit"]

    def test_test_isolation_rules_exist(self):
        """Test 4.3c: Verify test isolation rules are defined."""
        from agentic_core.L5_safety.unified.UnifiedStructureValidatorAgent import (
            TEST_ISOLATION_RULES,
        )

        # Unit tests should not import from integration/e2e
        assert "tests_integration" in TEST_ISOLATION_RULES["tests_unit"]
        assert "tests_e2e" in TEST_ISOLATION_RULES["tests_unit"]


class TestPhase5HeadlessOrchestration:
    """Phase 5: Headless Orchestration Tests"""

    @pytest.fixture
    def mock_project(self, tmp_path):
        """Setup compliant project structure."""
        (tmp_path / "agentic_core" / "L0_maintenance").mkdir(parents=True)
        (tmp_path / "apps_shared").mkdir()
        (tmp_path / "tests" / "unit").mkdir(parents=True)
        return tmp_path

    def test_ci_verification_sync_method_exists(self, mock_project):
        """Test 5.1a: Verify run_ci_verification_sync() method exists."""
        from agentic_core.L5_safety.validators.FilesystemSSOTReconcilerAgent import (
            FilesystemSSOTReconcilerAgent,
        )

        agent = FilesystemSSOTReconcilerAgent(mock_project)

        # Verify method exists and is callable
        assert hasattr(agent, "run_ci_verification_sync")
        assert callable(agent.run_ci_verification_sync)

    def test_ci_verification_sync_returns_tuple(self, mock_project):
        """Test 5.1b: Verify run_ci_verification_sync() returns (bool, dict)."""
        from agentic_core.L5_safety.validators.FilesystemSSOTReconcilerAgent import (
            FilesystemSSOTReconcilerAgent,
        )

        agent = FilesystemSSOTReconcilerAgent(mock_project)
        result = agent.run_ci_verification_sync()

        # Should return tuple of (is_compliant, results_dict)
        assert isinstance(result, tuple)
        assert len(result) == 2

        is_compliant, results = result
        assert isinstance(is_compliant, bool)
        assert isinstance(results, dict)

        # Results should have expected keys
        assert "hierarchy_violations" in results
        assert "location_violations" in results
        assert "total_violations" in results
        assert "is_compliant" in results

    def test_ci_verification_headless_no_stdin(self, mock_project):
        """Test 5.1c: Verify CI verification works without stdin."""
        from agentic_core.L5_safety.validators.FilesystemSSOTReconcilerAgent import (
            FilesystemSSOTReconcilerAgent,
        )

        agent = FilesystemSSOTReconcilerAgent(mock_project)

        # Mock stdin to fail if accessed
        with patch("builtins.input", side_effect=Exception("Should not prompt!")):
            is_compliant, results = agent.run_ci_verification_sync()

        # Should complete without prompting
        assert isinstance(is_compliant, bool)


class TestPhase5CLITool:
    """Phase 5.2: CLI Tool Tests"""

    def test_ssot_folder_check_main_exists(self):
        """Test 5.2a: Verify ssot_folder_check has main() function."""
        from agentic_core.L5_safety.validators import ssot_folder_check

        assert hasattr(ssot_folder_check, "main")
        assert callable(ssot_folder_check.main)

    def test_ssot_folder_check_returns_int(self, tmp_path):
        """Test 5.2b: Verify ssot_folder_check.main() returns int exit code."""
        # Verify the main function signature returns int
        from agentic_core.L5_safety.validators import ssot_folder_check
        import inspect

        sig = inspect.signature(ssot_folder_check.main)
        # The return annotation should be int
        assert sig.return_annotation == int


class TestPhase6HygieneGuardian:
    """Phase 6: HygieneGuardianAgent SRP Tests"""

    def test_hygiene_guardian_no_structural_checks(self):
        """Test 6.1: Verify HygieneGuardianAgent has no structural/location checks."""
        from agentic_core.L5_safety.validators.HygieneGuardianAgent import HygieneGuardianAgent

        # Get methods defined directly on HygieneGuardianAgent (not inherited)
        own_methods = [
            m
            for m in dir(HygieneGuardianAgent)
            if not m.startswith("_") and callable(getattr(HygieneGuardianAgent, m, None))
        ]

        # Filter to methods actually defined on the class (not inherited from mixins)
        source_methods = []
        for m in own_methods:
            try:
                method = getattr(HygieneGuardianAgent, m)
                if (
                    hasattr(method, "__qualname__")
                    and "HygieneGuardianAgent" in method.__qualname__
                ):
                    source_methods.append(m)
            except Exception:
                pass

        # These structural keywords should NOT be in HygieneGuardianAgent's OWN method names
        structural_keywords = ["location", "folder", "structure", "territory"]
        # Note: "depth" excluded since it might be used for recursion depth, not structural depth

        for method in source_methods:
            method_name_lower = method.lower()
            for keyword in structural_keywords:
                assert keyword not in method_name_lower, (
                    f"HygieneGuardianAgent has structural method: {method}"
                )

    def test_hygiene_guardian_content_focus(self, tmp_path):
        """Test 6.2: Verify HygieneGuardianAgent focuses on content hygiene."""
        from agentic_core.L5_safety.validators.HygieneGuardianAgent import HygieneGuardianAgent

        # Create files with hygiene issues
        (tmp_path / "empty.py").write_text("")  # Empty file
        (tmp_path / "debug.py").write_text("print('debug')\n")  # Debug print
        (tmp_path / "backup.bak").write_text("old")  # Backup file

        agent = HygieneGuardianAgent(tmp_path, dry_run=True)
        agent._scan_directory(tmp_path)

        # Should detect content hygiene issues
        violation_types = {v.violation_type for v in agent.violations}

        # These are content hygiene checks (should be present)
        content_checks = {"empty_file", "debug_print", "stale_backup"}

        # At least some content violations should be detected
        assert len(violation_types & content_checks) > 0

    def test_hygiene_guardian_uses_canonical_keys(self, tmp_path):
        """Test 6.3: Verify HygieneGuardianAgent uses canonical heal_repository keys."""
        from agentic_core.L5_safety.validators.HygieneGuardianAgent import HygieneGuardianAgent

        agent = HygieneGuardianAgent(tmp_path, dry_run=True)
        result = agent.heal_repository(dry_run=True)

        # Should use canonical keys per @standard_heal decorator
        assert "violations_found" in result
        assert "violations_fixed" in result
