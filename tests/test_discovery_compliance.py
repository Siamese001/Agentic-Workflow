#!/usr/bin/env python3
"""
Test Suite for Discovery Compliance - SSOT Alignment Validation

This test suite validates that full_agent_discovery.py properly aligns with
the Single Source of Truth defined in structure_blueprint.py. Tests include
mocking SSOT paths, edge case handling, compliance validation, and error handling.

CRITICAL REQUIREMENT: All tests must achieve 100% pass rate to ensure
SSOT compliance and architectural integrity.

USAGE:
    pytest tests/test_discovery_compliance.py -v
    pytest tests/test_discovery_compliance.py::test_ssot_mocking_compliance -v
"""

from __future__ import annotations

import json
import logging
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

# Import the module under test
from agentic_core.L0_maintenance.scripts.full_agent_discovery import (
    check_compliance_gate,
    discover_all_agents,
    get_agent_discovery_summary,
    main,
    refresh_discovery_cache,
    validate_agent_structure,
)
from agentic_core.L5_safety.validators.structure_blueprint_config import (
    AGENT_DISCOVERY_JSON,
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    L0_MAINTENANCE_DIR,
)

# Configure test logging
logging.basicConfig(level=logging.DEBUG)
Logger = logging.getLogger(__name__)


class TestSSOTMockingCompliance:
    """
    Test Case 1: Mocking SSOT - Verify script respects mocked paths.

    CRITICAL: This test ensures the discovery script uses SSOT imports
    and doesn't hardcode any directory paths. It patches SSOT constants
    to a temporary directory and validates the script scans that location.
    """

    def test_mocked_ssot_directory_scanning(self):
        """Test that discovery script respects mocked SSOT directory paths."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create mock SSOT structure
            mock_dirs = [
                AGENTIC_CORE_DIR,
                APPS_RG_DIR,
                APPS_LIC_DIR,
                APPS_SHARED_DIR,
                L0_MAINTENANCE_DIR,
            ]

            for dir_name in mock_dirs:
                (temp_path / dir_name).mkdir(parents=True, exist_ok=True)

            # Create mock agent discovery JSON
            mock_agents = [
                {
                    "name": "TestAgent1",
                    "class_name": "TestAgent1",
                    "path": f"{AGENTIC_CORE_DIR}/L5_safety/TestAgent1.py",
                    "layer": "L5",
                    "has_healing": True,
                },
                {
                    "name": "TestAgent2",
                    "class_name": "TestAgent2",
                    "path": f"{APPS_RG_DIR}/engines/TestAgent2.py",
                    "layer": "Apps",
                    "has_healing": False,
                },
            ]

            discovery_file = temp_path / "mock_discovery.json"
            with open(discovery_file, "w", encoding="utf-8") as f:
                json.dump(mock_agents, f, indent=2)

            # Patch both modules to use temp directory and custom discovery file
            with patch(
                "agentic_core.L0_maintenance.scripts.full_agent_discovery.get_validated_project_root",
                return_value=temp_path,
            ):
                with patch(
                    "agentic_core.utils.ssot_discovery.get_validated_project_root",
                    return_value=temp_path,
                ):
                    with patch(
                        "agentic_core.utils.ssot_discovery.AGENT_DISCOVERY_JSON",
                        "mock_discovery.json",
                    ):
                        # Verify discovery uses mocked paths
                        agents = discover_all_agents()
                        assert len(agents) == 2, f"Expected 2 agents, got {len(agents)}"

                        # Verify agent paths use mocked directory structure
                        agent_paths = [agent.get("path", "") for agent in agents]
                        assert any(AGENTIC_CORE_DIR in path for path in agent_paths), (
                            "Agent paths should use mocked SSOT directories"
                        )
                        assert any(APPS_RG_DIR in path for path in agent_paths), (
                            "Agent paths should use mocked SSOT directories"
                        )

    def test_mocked_compliance_gate_validation(self):
        """Test that compliance gate respects mocked SSOT structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create incomplete SSOT structure (missing apps_lic)
            (temp_path / AGENTIC_CORE_DIR).mkdir(parents=True, exist_ok=True)
            (temp_path / APPS_RG_DIR).mkdir(parents=True, exist_ok=True)
            (temp_path / APPS_SHARED_DIR).mkdir(parents=True, exist_ok=True)
            (temp_path / L0_MAINTENANCE_DIR).mkdir(parents=True, exist_ok=True)
            # Intentionally NOT creating APPS_LIC_DIR

            # Create valid discovery file
            discovery_file = temp_path / "compliance_test_discovery.json"
            with open(discovery_file, "w", encoding="utf-8") as f:
                json.dump([], f)

            # Patch SSOT functions
            with patch(
                "agentic_core.L0_maintenance.scripts.full_agent_discovery.get_validated_project_root",
                return_value=temp_path,
            ):
                with patch(
                    "agentic_core.utils.ssot_discovery.AGENT_DISCOVERY_JSON",
                    "compliance_test_discovery.json",
                ):
                    # Compliance should fail due to missing directory
                    compliant = check_compliance_gate()
                    assert not compliant, (
                        "Compliance gate should fail when SSOT directories are missing"
                    )

    def test_mocked_project_root_isolation(self):
        """Test that operations are isolated to mocked project root."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create minimal mock structure
            (temp_path / AGENTIC_CORE_DIR).mkdir(parents=True, exist_ok=True)

            # Empty discovery file
            discovery_file = temp_path / "isolation_test_discovery.json"
            with open(discovery_file, "w", encoding="utf-8") as f:
                json.dump([], f)

            # Patch both modules to use temp directory and custom discovery file
            with patch(
                "agentic_core.L0_maintenance.scripts.full_agent_discovery.get_validated_project_root",
                return_value=temp_path,
            ):
                with patch(
                    "agentic_core.utils.ssot_discovery.get_validated_project_root",
                    return_value=temp_path,
                ):
                    with patch(
                        "agentic_core.utils.ssot_discovery.AGENT_DISCOVERY_JSON",
                        "isolation_test_discovery.json",
                    ):
                        # Verify summary uses mocked path
                        summary = get_agent_discovery_summary()
                        assert summary["project_root"] == str(temp_path), (
                            "Summary should use mocked project root"
                        )
                        assert "isolation_test_discovery.json" in summary["ssot_file"], (
                            "Summary should use mocked SSOT file path"
                        )


class TestEdgeCaseHandling:
    """
    Test Case 2: Edge Cases - Empty directories and malformed agent files.

    Validates graceful handling of edge cases like empty directories,
    malformed JSON files, missing agents, and corrupted data structures.
    """

    def test_empty_discovery_file_handling(self):
        """Test handling of empty or missing agent discovery file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create required directories but no discovery file
            for dir_name in [
                AGENTIC_CORE_DIR,
                APPS_RG_DIR,
                APPS_LIC_DIR,
                APPS_SHARED_DIR,
                L0_MAINTENANCE_DIR,
            ]:
                (temp_path / dir_name).mkdir(parents=True, exist_ok=True)

            # Mock both project root and the specific discovery file path
            with patch(
                "agentic_core.L0_maintenance.scripts.full_agent_discovery.get_validated_project_root",
                return_value=temp_path,
            ):
                with patch(
                    "agentic_core.utils.ssot_discovery.AGENT_DISCOVERY_JSON",
                    "nonexistent_discovery_file.json",
                ):
                    # Should handle missing discovery file gracefully
                    agents = discover_all_agents()
                    assert isinstance(agents, list), (
                        "Should return list even when discovery file is missing"
                    )
                    assert len(agents) == 0, (
                        "Should return empty list when discovery file is missing"
                    )

    def test_malformed_json_handling(self):
        """Test handling of malformed JSON in discovery file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create directories
            (temp_path / AGENTIC_CORE_DIR).mkdir(parents=True, exist_ok=True)

            # Create malformed JSON file with different name to avoid conflict
            malformed_file = temp_path / "malformed_discovery.json"
            with open(malformed_file, "w", encoding="utf-8") as f:
                f.write("{ invalid json content")

            # Mock both project root and the discovery file path
            with patch(
                "agentic_core.L0_maintenance.scripts.full_agent_discovery.get_validated_project_root",
                return_value=temp_path,
            ):
                with patch(
                    "agentic_core.utils.ssot_discovery.AGENT_DISCOVERY_JSON",
                    "malformed_discovery.json",
                ):
                    # Should handle malformed JSON gracefully
                    agents = discover_all_agents()
                    assert isinstance(agents, list), "Should return list even with malformed JSON"
                    assert len(agents) == 0, "Should return empty list with malformed JSON"

    def test_invalid_agent_data_structure(self):
        """Test handling of invalid agent data structures."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create directories
            (temp_path / AGENTIC_CORE_DIR).mkdir(parents=True, exist_ok=True)

            # Create discovery file with invalid structures
            invalid_agents = [
                {"name": "ValidAgent", "path": "valid/path.py"},  # Valid
                {"invalid": "structure"},  # Missing required fields
                None,  # Null entry
                "string_instead_of_dict",  # Wrong type
                {"path": ""},  # Empty path
            ]

            discovery_file = temp_path / AGENT_DISCOVERY_JSON
            with open(discovery_file, "w", encoding="utf-8") as f:
                json.dump(invalid_agents, f)

            with patch(
                "agentic_core.L0_maintenance.scripts.full_agent_discovery.get_validated_project_root",
                return_value=temp_path,
            ):
                # Should handle mixed valid/invalid data
                agents = discover_all_agents()
                assert isinstance(agents, list), "Should return list with mixed data"
                # Should not crash, even with invalid entries

    def test_empty_directories_compliance(self):
        """Test compliance check with empty but existing directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create all required directories but leave them empty
            for dir_name in [
                AGENTIC_CORE_DIR,
                APPS_RG_DIR,
                APPS_LIC_DIR,
                APPS_SHARED_DIR,
                L0_MAINTENANCE_DIR,
            ]:
                (temp_path / dir_name).mkdir(parents=True, exist_ok=True)

            # Create empty discovery file
            discovery_file = temp_path / AGENT_DISCOVERY_JSON
            with open(discovery_file, "w", encoding="utf-8") as f:
                json.dump([], f)

            with patch(
                "agentic_core.L0_maintenance.scripts.full_agent_discovery.get_validated_project_root",
                return_value=temp_path,
            ):
                # Empty directories should still pass compliance
                compliant = check_compliance_gate()
                assert compliant, "Empty directories should pass compliance check"


class TestComplianceValidation:
    """
    Test Case 3: Compliance - Ensure functions return expected types.

    Validates that all public functions return the correct data types
    according to their signatures and documentation.
    """

    def test_discover_all_agents_return_type(self):
        """Test discover_all_agents returns correct type."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create minimal setup
            (temp_path / AGENTIC_CORE_DIR).mkdir(parents=True, exist_ok=True)
            discovery_file = temp_path / AGENT_DISCOVERY_JSON
            with open(discovery_file, "w", encoding="utf-8") as f:
                json.dump([], f)

            with patch(
                "agentic_core.L0_maintenance.scripts.full_agent_discovery.get_validated_project_root",
                return_value=temp_path,
            ):
                result = discover_all_agents()
                assert isinstance(result, list), "discover_all_agents must return list"
                assert all(isinstance(agent, dict) for agent in result), (
                    "All agents must be dictionaries"
                )

    def test_check_compliance_gate_return_type(self):
        """Test check_compliance_gate returns correct type."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create minimal compliant setup
            for dir_name in [
                AGENTIC_CORE_DIR,
                APPS_RG_DIR,
                APPS_LIC_DIR,
                APPS_SHARED_DIR,
                L0_MAINTENANCE_DIR,
            ]:
                (temp_path / dir_name).mkdir(parents=True, exist_ok=True)
            discovery_file = temp_path / AGENT_DISCOVERY_JSON
            with open(discovery_file, "w", encoding="utf-8") as f:
                json.dump([], f)

            with patch(
                "agentic_core.L0_maintenance.scripts.full_agent_discovery.get_validated_project_root",
                return_value=temp_path,
            ):
                result = check_compliance_gate()
                assert isinstance(result, bool), "check_compliance_gate must return boolean"

    def test_get_agent_discovery_summary_return_type(self):
        """Test get_agent_discovery_summary returns correct type."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create minimal setup
            (temp_path / AGENTIC_CORE_DIR).mkdir(parents=True, exist_ok=True)
            discovery_file = temp_path / AGENT_DISCOVERY_JSON
            with open(discovery_file, "w", encoding="utf-8") as f:
                json.dump([], f)

            with patch(
                "agentic_core.L0_maintenance.scripts.full_agent_discovery.get_validated_project_root",
                return_value=temp_path,
            ):
                result = get_agent_discovery_summary()
                assert isinstance(result, dict), (
                    "get_agent_discovery_summary must return dictionary"
                )

                # Check required keys exist
                required_keys = [
                    "total_agents",
                    "layer_distribution",
                    "directory_distribution",
                    "healer_count",
                ]
                for key in required_keys:
                    assert key in result, f"Summary must contain key: {key}"

                assert isinstance(result["total_agents"], int), "total_agents must be integer"
                assert isinstance(result["layer_distribution"], dict), (
                    "layer_distribution must be dictionary"
                )
                assert isinstance(result["directory_distribution"], dict), (
                    "directory_distribution must be dictionary"
                )
                assert isinstance(result["healer_count"], int), "healer_count must be integer"

    def test_main_function_return_type(self):
        """Test main function returns correct type."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create fully compliant setup
            for dir_name in [
                AGENTIC_CORE_DIR,
                APPS_RG_DIR,
                APPS_LIC_DIR,
                APPS_SHARED_DIR,
                L0_MAINTENANCE_DIR,
            ]:
                (temp_path / dir_name).mkdir(parents=True, exist_ok=True)
            discovery_file = temp_path / AGENT_DISCOVERY_JSON
            with open(discovery_file, "w", encoding="utf-8") as f:
                json.dump([], f)

            with patch(
                "agentic_core.L0_maintenance.scripts.full_agent_discovery.get_validated_project_root",
                return_value=temp_path,
            ):
                result = main()
                assert isinstance(result, bool), "main must return boolean"

    def test_validate_agent_structure_return_type(self):
        """Test validate_agent_structure returns correct type."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Test with non-existent file
            non_existent = temp_path / "non_existent.py"
            result = validate_agent_structure(non_existent)
            assert isinstance(result, bool), "validate_agent_structure must return boolean"
            assert not result, "Non-existent file should return False"

            # Test with valid Python file
            valid_file = temp_path / "valid_agent.py"
            valid_file.write_text("# Valid Python file")
            result = validate_agent_structure(valid_file)
            assert isinstance(result, bool), "validate_agent_structure must return boolean"
            assert result, "Valid Python file should return True"


class TestErrorHandling:
    """
    Test Case 4: Error Handling - Verify graceful failure on errors.

    Tests permission errors, missing files, corrupted data, and other
    error conditions to ensure graceful degradation.
    """

    def test_permission_error_handling(self):
        """Test graceful handling of permission errors."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create directories
            (temp_path / AGENTIC_CORE_DIR).mkdir(parents=True, exist_ok=True)

            # Create discovery file
            discovery_file = temp_path / "permission_test_discovery.json"
            with open(discovery_file, "w", encoding="utf-8") as f:
                json.dump([], f)

            # Mock permission error on file access
            with patch(
                "agentic_core.L0_maintenance.scripts.full_agent_discovery.get_validated_project_root",
                return_value=temp_path,
            ):
                with patch(
                    "agentic_core.utils.ssot_discovery.AGENT_DISCOVERY_JSON",
                    "permission_test_discovery.json",
                ):
                    with patch("builtins.open", side_effect=PermissionError("Permission denied")):
                        # Should handle permission error gracefully
                        agents = discover_all_agents()
                        assert isinstance(agents, list), (
                            "Should return list even with permission error"
                        )
                        assert len(agents) == 0, "Should return empty list with permission error"

    def test_missing_project_root_handling(self):
        """Test handling when project root validation fails."""
        # Mock get_validated_project_root to raise exception
        with patch(
            "agentic_core.L0_maintenance.scripts.full_agent_discovery.get_validated_project_root",
            side_effect=Exception("Project root not found"),
        ):
            # Also mock the ssot_discovery module to prevent it from using real project root
            with patch(
                "agentic_core.utils.ssot_discovery.get_validated_project_root",
                side_effect=Exception("Project root not found"),
            ):
                # Should handle missing project root gracefully
                agents = discover_all_agents()
                assert isinstance(agents, list), (
                    "Should return list even when project root is missing"
                )
                assert len(agents) == 0, "Should return empty list when project root is missing"

    def test_corrupted_discovery_data_handling(self):
        """Test handling of corrupted or inconsistent discovery data."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create directories
            (temp_path / AGENTIC_CORE_DIR).mkdir(parents=True, exist_ok=True)

            # Create discovery file with corrupted data
            corrupted_data = {
                "agents": [
                    {"name": "Agent1", "path": "path1.py", "layer": None},
                    {"name": None, "path": "path2.py", "layer": "L5"},
                    {"name": "Agent3", "path": None, "layer": "L3"},
                ],
                "metadata": "corrupted",
                "unexpected_field": [1, 2, 3],
            }

            discovery_file = temp_path / AGENT_DISCOVERY_JSON
            with open(discovery_file, "w", encoding="utf-8") as f:
                json.dump(corrupted_data, f)

            with patch(
                "agentic_core.L0_maintenance.scripts.full_agent_discovery.get_validated_project_root",
                return_value=temp_path,
            ):
                # Should handle corrupted data gracefully
                agents = discover_all_agents()
                assert isinstance(agents, list), "Should return list with corrupted data"
                # Should not crash

    def test_cache_refresh_error_handling(self):
        """Test error handling in cache refresh operations."""
        with patch(
            "agentic_core.L0_maintenance.scripts.full_agent_discovery.invalidate_cache",
            side_effect=Exception("Cache error"),
        ):
            # Should handle cache refresh error gracefully
            result = refresh_discovery_cache()
            assert isinstance(result, bool), "refresh_discovery_cache must return boolean"
            assert not result, "Should return False when cache refresh fails"

    def test_logging_error_suppression(self):
        """Test that logging errors don't crash main operations."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create minimal setup
            (temp_path / AGENTIC_CORE_DIR).mkdir(parents=True, exist_ok=True)
            discovery_file = temp_path / AGENT_DISCOVERY_JSON
            with open(discovery_file, "w", encoding="utf-8") as f:
                json.dump([], f)

            # Mock logging to raise exception
            with patch(
                "agentic_core.L0_maintenance.scripts.full_agent_discovery.get_validated_project_root",
                return_value=temp_path,
            ):
                with patch("logging.Logger.error", side_effect=Exception("Logging error")):
                    # Should not crash even if logging fails
                    try:
                        agents = discover_all_agents()
                        assert isinstance(agents, list), "Should return list even if logging fails"
                    except Exception as e:
                        pytest.fail(f"Should not crash on logging error: {e}")


class TestIntegrationScenarios:
    """
    Additional integration tests for complex scenarios.
    """

    def test_full_discovery_workflow_integration(self):
        """Test complete discovery workflow end-to-end."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create complete SSOT structure
            for dir_name in [
                AGENTIC_CORE_DIR,
                APPS_RG_DIR,
                APPS_LIC_DIR,
                APPS_SHARED_DIR,
                L0_MAINTENANCE_DIR,
            ]:
                (temp_path / dir_name).mkdir(parents=True, exist_ok=True)

            # Create comprehensive agent data
            mock_agents = [
                {
                    "name": "SovereignBaseAgent",
                    "class_name": "SovereignBaseAgent",
                    "path": f"{AGENTIC_CORE_DIR}/base_agents/SovereignBaseAgent.py",
                    "layer": "Base",
                    "has_healing": False,
                    "last_updated": "2026-01-31T12:00:00Z",
                },
                {
                    "name": "TestHealerAgent",
                    "class_name": "TestHealerAgent",
                    "path": f"{AGENTIC_CORE_DIR}/L5_safety/TestHealerAgent.py",
                    "layer": "L5",
                    "has_healing": True,
                    "last_updated": "2026-01-31T12:00:00Z",
                },
                {
                    "name": "AppRGAgent",
                    "class_name": "AppRGAgent",
                    "path": f"{APPS_RG_DIR}/engines/AppRGAgent.py",
                    "layer": "Apps",
                    "has_healing": False,
                    "last_updated": "2026-01-31T12:00:00Z",
                },
            ]

            discovery_file = temp_path / "integration_test_discovery.json"
            with open(discovery_file, "w", encoding="utf-8") as f:
                json.dump(mock_agents, f)

            with patch(
                "agentic_core.L0_maintenance.scripts.full_agent_discovery.get_validated_project_root",
                return_value=temp_path,
            ):
                with patch(
                    "agentic_core.utils.ssot_discovery.get_validated_project_root",
                    return_value=temp_path,
                ):
                    with patch(
                        "agentic_core.utils.ssot_discovery.AGENT_DISCOVERY_JSON",
                        "integration_test_discovery.json",
                    ):
                        # Test complete workflow
                        assert check_compliance_gate(), "Compliance check should pass"

                        agents = discover_all_agents()
                        assert len(agents) == 3, f"Expected 3 agents, got {len(agents)}"

                        summary = get_agent_discovery_summary()
                        assert summary["total_agents"] == 3, "Summary should show 3 agents"
                        assert summary["healer_count"] == 1, "Summary should show 1 healer"
                        assert "L5" in summary["layer_distribution"], "Should have L5 layer"
                        assert "Apps" in summary["layer_distribution"], "Should have Apps layer"

                        result = main()
                        assert result, "Main function should succeed"

    def test_base_agent_location_validation(self):
        """Test validation of base agent location rules."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Test base agent in correct location
            correct_base_agent = temp_path / "agentic_core" / "base_agents" / "TestBaseAgent.py"
            correct_base_agent.parent.mkdir(parents=True, exist_ok=True)
            correct_base_agent.write_text("# Base Agent")

            result = validate_agent_structure(correct_base_agent)
            assert result, "Base agent in correct location should validate"

            # Test base agent in incorrect location
            incorrect_base_agent = temp_path / "agentic_core" / "L5_safety" / "TestBaseAgent.py"
            incorrect_base_agent.parent.mkdir(parents=True, exist_ok=True)
            incorrect_base_agent.write_text("# Base Agent in wrong location")

            result = validate_agent_structure(incorrect_base_agent)
            assert not result, "Base agent in incorrect location should not validate"


# Test configuration and markers
pytest_plugins = []


def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line("markers", "ssot_compliance: Tests for SSOT compliance validation")
    config.addinivalue_line("markers", "edge_case: Tests for edge case handling")
    config.addinivalue_line("markers", "error_handling: Tests for error handling scenarios")
    config.addinivalue_line("markers", "integration: Integration test scenarios")


# Apply markers to test classes
TestSSOTMockingCompliance = pytest.mark.ssot_compliance(TestSSOTMockingCompliance)
TestEdgeCaseHandling = pytest.mark.edge_case(TestEdgeCaseHandling)
TestComplianceValidation = pytest.mark.ssot_compliance(TestComplianceValidation)
TestErrorHandling = pytest.mark.error_handling(TestErrorHandling)
TestIntegrationScenarios = pytest.mark.integration(TestIntegrationScenarios)


if __name__ == "__main__":
    # Run tests with detailed output
    pytest.main([__file__, "-v", "--tb=short"])
