"""
Unit Tests for Phase 3: SSOT Structure Validation
==================================================
Tests the SSOT structure validator for path compliance.

USAGE:
    pytest tests/unit/agentic_core/L5_safety/validators/test_ssot_structure_validation.py -v
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).resolve().parents[5]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L5_safety.enforcement.registry_verification import AgentInfo
from agentic_core.L5_safety.enforcement.ssot_structure_validation import (
    SSOTStructureValidator,
    StructureValidationResult,
    StructureViolation,
    run_structure_validation,
)


class TestStructureViolation:
    """Tests for StructureViolation dataclass."""

    def test_violation_creation(self):
        """Test basic StructureViolation creation."""
        violation = StructureViolation(
            agent_class="TestAgent",
            agent_path="test/TestAgent.py",
            violation_type="test_violation",
            message="Test message",
        )
        assert violation.agent_class == "TestAgent"
        assert violation.violation_type == "test_violation"

    def test_violation_defaults(self):
        """Test StructureViolation default values."""
        violation = StructureViolation(
            agent_class="TestAgent",
            agent_path="test/TestAgent.py",
            violation_type="test",
            message="Test",
        )
        assert violation.severity == "warning"
        assert violation.suggested_fix == ""

    def test_violation_with_severity(self):
        """Test StructureViolation with custom severity."""
        violation = StructureViolation(
            agent_class="TestAgent",
            agent_path="test/TestAgent.py",
            violation_type="critical_test",
            message="Critical issue",
            severity="critical",
        )
        assert violation.severity == "critical"


class TestStructureValidationResult:
    """Tests for StructureValidationResult dataclass."""

    def test_result_defaults(self):
        """Test StructureValidationResult default values."""
        result = StructureValidationResult()
        assert result.total_agents == 0
        assert result.compliant_agents == 0
        assert result.violations == []

    def test_compliance_percentage_zero_agents(self):
        """Test compliance percentage with zero agents."""
        result = StructureValidationResult()
        assert result.compliance_percentage == 0.0

    def test_compliance_percentage_calculation(self):
        """Test compliance percentage calculation."""
        result = StructureValidationResult()
        result.total_agents = 10
        result.compliant_agents = 8
        assert result.compliance_percentage == 80.0

    def test_is_fully_compliant_true(self):
        """Test is_fully_compliant when no violations."""
        result = StructureValidationResult()
        result.total_agents = 5
        result.compliant_agents = 5
        assert result.is_fully_compliant is True

    def test_is_fully_compliant_false(self):
        """Test is_fully_compliant when violations exist."""
        result = StructureValidationResult()
        result.violations.append(
            StructureViolation(
                agent_class="Test",
                agent_path="test",
                violation_type="test",
                message="test",
            ),
        )
        assert result.is_fully_compliant is False


class TestSSOTStructureValidator:
    """Tests for SSOTStructureValidator class."""

    def test_validator_initialization(self):
        """Test validator initialization."""
        validator = SSOTStructureValidator(project_root=PROJECT_ROOT)
        assert validator.project_root == PROJECT_ROOT

    def test_normalize_path(self):
        """Test path normalization."""
        validator = SSOTStructureValidator(project_root=PROJECT_ROOT)
        assert validator._normalize_path("a\\b\\c") == "a/b/c"
        assert validator._normalize_path("a/b/c") == "a/b/c"

    def test_get_territory_agentic_core(self):
        """Test territory detection for agentic_core."""
        validator = SSOTStructureValidator(project_root=PROJECT_ROOT)
        territory = validator._get_territory("agentic_core/L5_safety/TestAgent.py")
        assert territory == "agentic_core"

    def test_get_territory_apps_rg(self):
        """Test territory detection for apps_rg."""
        validator = SSOTStructureValidator(project_root=PROJECT_ROOT)
        territory = validator._get_territory("apps_rg/engines/TestAgent.py")
        assert territory == "apps_rg"

    def test_get_territory_apps_lic(self):
        """Test territory detection for apps_lic."""
        validator = SSOTStructureValidator(project_root=PROJECT_ROOT)
        territory = validator._get_territory("apps_lic/engines/TestAgent.py")
        assert territory == "apps_lic"

    def test_get_territory_unknown(self):
        """Test territory detection for unknown path."""
        validator = SSOTStructureValidator(project_root=PROJECT_ROOT)
        territory = validator._get_territory("unknown_dir/TestAgent.py")
        assert territory is None

    def test_get_expected_depth_agentic_core(self):
        """Test expected depth for agentic_core."""
        validator = SSOTStructureValidator(project_root=PROJECT_ROOT)
        depth = validator._get_expected_depth("agentic_core")
        assert depth == 3

    def test_get_expected_depth_apps(self):
        """Test expected depth for apps."""
        validator = SSOTStructureValidator(project_root=PROJECT_ROOT)
        assert validator._get_expected_depth("apps_rg") == 2
        assert validator._get_expected_depth("apps_lic") == 2

    def test_get_actual_depth(self):
        """Test actual depth calculation."""
        validator = SSOTStructureValidator(project_root=PROJECT_ROOT)
        assert validator._get_actual_depth("a/b/c.py") == 3
        assert validator._get_actual_depth("a/b/c/d.py") == 4
        assert validator._get_actual_depth("a.py") == 1

    def test_is_base_agent_true(self):
        """Test base agent detection - positive case."""
        validator = SSOTStructureValidator(project_root=PROJECT_ROOT)
        assert validator._is_base_agent("SovereignBaseAgent") is True
        assert validator._is_base_agent("L0MaintenanceBaseAgent") is True

    def test_is_base_agent_false(self):
        """Test base agent detection - negative case."""
        validator = SSOTStructureValidator(project_root=PROJECT_ROOT)
        assert validator._is_base_agent("LocationAgent") is False
        assert validator._is_base_agent("TestAgent") is False

    def test_is_in_variable_depth_folder(self):
        """Test variable depth folder detection."""
        validator = SSOTStructureValidator(project_root=PROJECT_ROOT)
        assert validator._is_in_variable_depth_folder("agentic_core/base_agents/Test.py")
        assert validator._is_in_variable_depth_folder("agentic_core/L5_safety/Test.py")
        assert not validator._is_in_variable_depth_folder("apps_rg/engines/Test.py")

    def test_validate_base_agent_location_correct(self):
        """Test base agent in correct location."""
        validator = SSOTStructureValidator(project_root=PROJECT_ROOT)
        agent = AgentInfo(
            class_name="TestBaseAgent",
            file_path=Path("/test/TestBaseAgent.py"),
            relative_path="agentic_core/base_agents/TestBaseAgent.py",
        )
        violation = validator._validate_base_agent_location(agent)
        assert violation is None

    def test_validate_base_agent_location_incorrect(self):
        """Test base agent in incorrect location."""
        validator = SSOTStructureValidator(project_root=PROJECT_ROOT)
        agent = AgentInfo(
            class_name="TestBaseAgent",
            file_path=Path("/test/TestBaseAgent.py"),
            relative_path="agentic_core/L5_safety/TestBaseAgent.py",
        )
        violation = validator._validate_base_agent_location(agent)
        assert violation is not None
        assert violation.violation_type == "base_agent_location"
        assert violation.severity == "critical"

    def test_validate_base_agent_location_non_base(self):
        """Test non-base agent returns no violation."""
        validator = SSOTStructureValidator(project_root=PROJECT_ROOT)
        agent = AgentInfo(
            class_name="LocationAgent",
            file_path=Path("/test/LocationAgent.py"),
            relative_path="agentic_core/L5_safety/validators/LocationAgent.py",
        )
        violation = validator._validate_base_agent_location(agent)
        assert violation is None

    def test_validate_territory_valid(self):
        """Test valid territory."""
        validator = SSOTStructureValidator(project_root=PROJECT_ROOT)
        agent = AgentInfo(
            class_name="TestAgent",
            file_path=Path("/test/TestAgent.py"),
            relative_path="agentic_core/L5_safety/validators/TestAgent.py",
        )
        violation = validator._validate_territory(agent)
        assert violation is None

    def test_validate_territory_root_file(self):
        """Test root file violation."""
        validator = SSOTStructureValidator(project_root=PROJECT_ROOT)
        agent = AgentInfo(
            class_name="TestAgent",
            file_path=Path("/test/TestAgent.py"),
            relative_path="TestAgent.py",
        )
        violation = validator._validate_territory(agent)
        assert violation is not None
        assert violation.violation_type == "root_file"

    def test_validate_agent_compliant(self):
        """Test validating a compliant agent."""
        validator = SSOTStructureValidator(project_root=PROJECT_ROOT)
        agent = AgentInfo(
            class_name="LocationAgent",
            file_path=Path("/test/LocationAgent.py"),
            relative_path="agentic_core/L5_safety/validators/LocationAgent.py",
            layer="L5",
        )
        violations = validator.validate_agent(agent)
        assert len(violations) == 0

    def test_validate_structure_returns_result(self):
        """Test validate_structure returns StructureValidationResult."""
        validator = SSOTStructureValidator(project_root=PROJECT_ROOT)
        result = validator.validate_structure()
        assert isinstance(result, StructureValidationResult)
        assert result.total_agents > 0

    def test_validate_structure_finds_violations(self):
        """Test validate_structure categorizes violations."""
        validator = SSOTStructureValidator(project_root=PROJECT_ROOT)
        result = validator.validate_structure()
        # Result should have categorized violations
        assert isinstance(result.base_agent_violations, list)
        assert isinstance(result.layer_violations, list)
        assert isinstance(result.depth_violations, list)
        assert isinstance(result.territory_violations, list)

    def test_generate_report_format(self):
        """Test report generation format."""
        validator = SSOTStructureValidator(project_root=PROJECT_ROOT)
        result = validator.validate_structure()
        report = validator.generate_report(result)
        assert "# Phase 3: SSOT Structure Validation Report" in report
        assert "## Summary" in report
        assert "Violation Breakdown" in report


class TestRunStructureValidation:
    """Tests for run_structure_validation function."""

    def test_run_structure_validation_returns_result(self):
        """Test run_structure_validation convenience function."""
        result = run_structure_validation()
        assert isinstance(result, StructureValidationResult)


class TestBaseAgentLocationEnforcement:
    """Tests for base agent location constitutional rule."""

    def test_base_agents_in_correct_location(self):
        """Test that base agents in base_agents folder pass."""
        validator = SSOTStructureValidator(project_root=PROJECT_ROOT)
        result = validator.validate_structure()

        # Check for any base agent violations
        for v in result.base_agent_violations:
            # These are violations - base agents NOT in correct location
            assert v.violation_type == "base_agent_location"


class TestLayerValidation:
    """Tests for layer assignment validation."""

    def test_layer_patterns_defined(self):
        """Test that layer patterns are properly defined."""
        from agentic_core.L5_safety.enforcement.ssot_structure_validation import (
            LAYER_PATTERNS,
        )

        assert "L0" in LAYER_PATTERNS
        assert "L5" in LAYER_PATTERNS
        assert LAYER_PATTERNS["L0"] == "L0_maintenance"
        assert LAYER_PATTERNS["L5"] == "L5_safety"


class TestDepthValidation:
    """Tests for depth validation."""

    def test_depth_calculation_accuracy(self):
        """Test depth calculation is accurate."""
        validator = SSOTStructureValidator(project_root=PROJECT_ROOT)

        # Test various path depths
        assert validator._get_actual_depth("file.py") == 1
        assert validator._get_actual_depth("dir/file.py") == 2
        assert validator._get_actual_depth("a/b/c/file.py") == 4


class TestTerritoryValidation:
    """Tests for territory validation."""

    def test_all_territories_recognized(self):
        """Test that all major territories are recognized."""
        validator = SSOTStructureValidator(project_root=PROJECT_ROOT)

        territories = ["agentic_core", "apps_rg", "apps_lic", "apps_shared", "tests"]
        for territory in territories:
            result = validator._get_territory(f"{territory}/test.py")
            assert result == territory


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
