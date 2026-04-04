"""
Unit Tests for architecture_governor_validator_util - Micro-wave 10E

Tests the architecture governor validator utility including:
- GovernanceValidationResult dataclass
- ArchitectureGovernorValidator class initialization
- Error handling when agent is not available
- Convenience functions
"""

from __future__ import annotations

import pytest

from agentic_core.L5_safety.utils.architecture_governor_validator_util import (
    CHECK_ID,
    ArchitectureGovernorValidator,
    GovernanceValidationResult,
    scan_governance,
    validate_architecture_governance,
)


class TestGovernanceValidationResultDataclass:
    """Tests for GovernanceValidationResult dataclass."""

    def test_governance_validation_result_creation(self):
        """Test GovernanceValidationResult can be created."""
        result = GovernanceValidationResult(
            check_id="test_check",
            violations_count=5,
            evidence={"detail": "test"},
            territory="test_territory",
            repo_root="/test/repo",
        )

        assert result.check_id == "test_check"
        assert result.violations_count == 5
        assert result.evidence == {"detail": "test"}
        assert result.territory == "test_territory"
        assert result.repo_root == "/test/repo"

    def test_governance_validation_result_defaults(self):
        """Test GovernanceValidationResult with defaults."""
        result = GovernanceValidationResult(
            check_id=CHECK_ID,
            violations_count=0,
            evidence={},
            territory=None,
            repo_root="/test",
        )

        assert result.check_id == "architecture_governance"
        assert result.violations_count == 0
        assert result.territory is None

    def test_governance_validation_result_to_dict(self):
        """Test GovernanceValidationResult to_dict method."""
        result = GovernanceValidationResult(
            check_id=CHECK_ID,
            violations_count=0,
            evidence={},
            territory=None,
            repo_root="/test",
        )

        d = result.to_dict()
        assert d["check_id"] == CHECK_ID
        assert d["violations_count"] == 0
        assert d["evidence"] == {}
        assert d["territory"] is None
        assert d["repo_root"] == "/test"


class TestArchitectureGovernorValidatorInit:
    """Tests for ArchitectureGovernorValidator initialization."""

    def test_validator_init_with_path(self, tmp_path):
        """Test validator initialization with Path."""
        validator = ArchitectureGovernorValidator(tmp_path)

        assert validator.project_root == tmp_path.resolve()

    def test_validator_init_with_string(self, tmp_path):
        """Test validator initialization with string."""
        validator = ArchitectureGovernorValidator(str(tmp_path))

        assert validator.project_root == tmp_path.resolve()

    def test_validator_init_absolute_path(self, tmp_path):
        """Test validator resolves to absolute path."""
        validator = ArchitectureGovernorValidator(tmp_path)

        assert validator.project_root.is_absolute()


class TestArchitectureGovernorValidatorScan:
    """Tests for ArchitectureGovernorValidator.scan method."""

    def test_scan_runs_without_crash(self, tmp_path):
        """Test scan runs without crashing.

        The scan may succeed or fail depending on project structure,
        but it should not raise an exception.
        """
        validator = ArchitectureGovernorValidator(tmp_path)
        result = validator.scan()

        # Should return a dict with expected keys
        assert isinstance(result, dict)
        assert "violations_found" in result or "errors" in result

    def test_scan_with_territory(self, tmp_path):
        """Test scan with territory parameter."""
        validator = ArchitectureGovernorValidator(tmp_path)
        result = validator.scan(target_territory="L5_safety")

        # Should return a dict
        assert isinstance(result, dict)


class TestArchitectureGovernorValidatorToCheckDict:
    """Tests for ArchitectureGovernorValidator.to_check_dict method."""

    def test_to_check_dict_agent_not_available(self, tmp_path):
        """Test to_check_dict when agent not available."""
        validator = ArchitectureGovernorValidator(tmp_path)
        result = validator.to_check_dict()

        # Should return structure even when agent errors
        assert result["check_id"] == CHECK_ID
        assert "evidence" in result
        assert "violations_count" in result
        assert result["repo_root"] == str(tmp_path.resolve())

    def test_to_check_dict_with_territory(self, tmp_path):
        """Test to_check_dict with territory."""
        validator = ArchitectureGovernorValidator(tmp_path)
        result = validator.to_check_dict(target_territory="test_territory")

        assert result["territory"] == "test_territory"
        assert result["check_id"] == CHECK_ID


class TestArchitectureGovernorValidatorRun:
    """Tests for ArchitectureGovernorValidator.run method."""

    def test_run_alias_agent_not_available(self, tmp_path):
        """Test run is alias for to_check_dict."""
        validator = ArchitectureGovernorValidator(tmp_path)
        run_result = validator.run()
        check_dict_result = validator.to_check_dict()

        # Both should return same structure
        assert run_result["check_id"] == check_dict_result["check_id"]
        assert run_result["repo_root"] == check_dict_result["repo_root"]


class TestArchitectureGovernorValidatorValidate:
    """Tests for ArchitectureGovernorValidator.validate method."""

    def test_validate_returns_result_agent_not_available(self, tmp_path):
        """Test validate returns GovernanceValidationResult even when agent not available."""
        validator = ArchitectureGovernorValidator(tmp_path)
        result = validator.validate()

        assert isinstance(result, GovernanceValidationResult)
        assert result.check_id == CHECK_ID
        assert result.repo_root == str(tmp_path.resolve())

    def test_validate_with_territory(self, tmp_path):
        """Test validate with target territory."""
        validator = ArchitectureGovernorValidator(tmp_path)
        result = validator.validate(target_territory="L0_routing")

        assert result.territory == "L0_routing"
        assert isinstance(result, GovernanceValidationResult)


class TestValidateArchitectureGovernance:
    """Tests for validate_architecture_governance convenience function."""

    def test_convenience_function_agent_not_available(self, tmp_path):
        """Test convenience function works even when agent not available."""
        result = validate_architecture_governance(tmp_path)

        assert isinstance(result, GovernanceValidationResult)
        assert result.check_id == CHECK_ID
        assert result.repo_root == str(tmp_path.resolve())

    def test_convenience_function_with_territory(self, tmp_path):
        """Test convenience function with territory."""
        result = validate_architecture_governance(tmp_path, target_territory="L1_cognition")

        assert result.territory == "L1_cognition"


class TestScanGovernance:
    """Tests for scan_governance convenience function."""

    def test_scan_convenience_function(self, tmp_path):
        """Test scan convenience function."""
        result = scan_governance(tmp_path)

        # Should return dict
        assert isinstance(result, dict)


class TestCheckIdConstant:
    """Tests for CHECK_ID constant."""

    def test_check_id_value(self):
        """Test CHECK_ID has expected value."""
        assert CHECK_ID == "architecture_governance"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
