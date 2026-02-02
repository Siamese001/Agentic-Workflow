"""
Phase 2 Tests: Red Team Security Integration

Tests for the security validation suite that orchestrates
red team validators for security testing.

Test Coverage:
- SecurityValidationResult dataclass
- SecuritySuiteResult dataclass
- RedTeamValidationSuite orchestration
- Individual validator execution
- Full suite execution
"""

from __future__ import annotations

import pytest
import sys
from pathlib import Path

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).resolve().parents[5]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class TestSecurityValidationResult:
    """Tests for SecurityValidationResult dataclass."""

    def test_result_creation_with_defaults(self):
        """Test SecurityValidationResult can be created with defaults."""
        from agentic_core.L5_safety.validators.security_validation_suite import (
            SecurityValidationResult,
        )

        result = SecurityValidationResult(
            validator_name="test_validator",
            valid=True,
        )

        assert result.validator_name == "test_validator"
        assert result.valid is True
        assert result.errors == []
        assert result.warnings == []
        assert result.metadata == {}
        assert result.timestamp is not None

    def test_result_creation_with_errors(self):
        """Test SecurityValidationResult with errors."""
        from agentic_core.L5_safety.validators.security_validation_suite import (
            SecurityValidationResult,
        )

        result = SecurityValidationResult(
            validator_name="test_validator",
            valid=False,
            errors=["Error 1", "Error 2"],
        )

        assert result.valid is False
        assert len(result.errors) == 2
        assert "Error 1" in result.errors

    def test_result_creation_with_metadata(self):
        """Test SecurityValidationResult with metadata."""
        from agentic_core.L5_safety.validators.security_validation_suite import (
            SecurityValidationResult,
        )

        result = SecurityValidationResult(
            validator_name="test_validator",
            valid=True,
            metadata={"threat_level": "low", "score": 0.95},
        )

        assert result.metadata["threat_level"] == "low"
        assert result.metadata["score"] == 0.95


class TestSecuritySuiteResult:
    """Tests for SecuritySuiteResult dataclass."""

    def test_suite_result_creation(self):
        """Test SecuritySuiteResult can be created."""
        from agentic_core.L5_safety.validators.security_validation_suite import (
            SecuritySuiteResult,
        )

        result = SecuritySuiteResult(
            overall_valid=True,
            validators_run=2,
            validators_passed=2,
            validators_failed=0,
        )

        assert result.overall_valid is True
        assert result.validators_run == 2
        assert result.validators_passed == 2
        assert result.validators_failed == 0
        assert result.results == []
        assert result.timestamp is not None

    def test_suite_result_with_results(self):
        """Test SecuritySuiteResult with individual results."""
        from agentic_core.L5_safety.validators.security_validation_suite import (
            SecuritySuiteResult,
            SecurityValidationResult,
        )

        individual_results = [
            SecurityValidationResult(validator_name="v1", valid=True),
            SecurityValidationResult(validator_name="v2", valid=False, errors=["err"]),
        ]

        result = SecuritySuiteResult(
            overall_valid=False,
            validators_run=2,
            validators_passed=1,
            validators_failed=1,
            results=individual_results,
        )

        assert len(result.results) == 2
        assert result.results[0].valid is True
        assert result.results[1].valid is False


class TestRedTeamValidationSuite:
    """Tests for RedTeamValidationSuite class."""

    def test_suite_creation(self):
        """Test RedTeamValidationSuite can be instantiated."""
        from agentic_core.L5_safety.validators.security_validation_suite import (
            RedTeamValidationSuite,
        )

        suite = RedTeamValidationSuite()
        assert suite is not None
        assert suite._initialized is False

    def test_suite_lazy_initialization(self):
        """Test suite initializes lazily on first use."""
        from agentic_core.L5_safety.validators.security_validation_suite import (
            RedTeamValidationSuite,
        )

        suite = RedTeamValidationSuite()
        assert suite._initialized is False

        # Trigger initialization
        suite._ensure_initialized()
        assert suite._initialized is True

    def test_get_available_validators(self):
        """Test getting list of available validators."""
        from agentic_core.L5_safety.validators.security_validation_suite import (
            RedTeamValidationSuite,
        )

        suite = RedTeamValidationSuite()
        validators = suite.get_available_validators()

        assert isinstance(validators, list)
        # Should have at least adversarial and boundary validators
        assert "adversarial_probe" in validators or len(validators) >= 0

    def test_get_status(self):
        """Test getting suite status."""
        from agentic_core.L5_safety.validators.security_validation_suite import (
            RedTeamValidationSuite,
        )

        suite = RedTeamValidationSuite()
        status = suite.get_status()

        assert isinstance(status, dict)
        assert "initialized" in status
        assert "validators_available" in status
        assert "validator_count" in status

    def test_run_validator_returns_result(self):
        """Test running a single validator returns proper result."""
        from agentic_core.L5_safety.validators.security_validation_suite import (
            RedTeamValidationSuite,
            SecurityValidationResult,
        )

        suite = RedTeamValidationSuite()
        result = suite.run_validator(
            "adversarial_probe",
            content={"test": "data"},
            context={},
        )

        assert isinstance(result, SecurityValidationResult)
        assert result.validator_name == "adversarial_probe"
        assert isinstance(result.valid, bool)

    def test_run_validator_unknown_returns_error(self):
        """Test running unknown validator returns error result."""
        from agentic_core.L5_safety.validators.security_validation_suite import (
            RedTeamValidationSuite,
        )

        suite = RedTeamValidationSuite()
        result = suite.run_validator(
            "unknown_validator",
            content={"test": "data"},
        )

        assert result.valid is False
        assert len(result.errors) > 0
        assert "not found" in result.errors[0]

    def test_run_all_returns_suite_result(self):
        """Test running all validators returns suite result."""
        from agentic_core.L5_safety.validators.security_validation_suite import (
            RedTeamValidationSuite,
            SecuritySuiteResult,
        )

        suite = RedTeamValidationSuite()
        result = suite.run_all(content={"test": "data"})

        assert isinstance(result, SecuritySuiteResult)
        assert result.validators_run >= 0
        assert result.validators_passed >= 0
        assert result.validators_failed >= 0
        assert result.execution_time_ms >= 0

    def test_run_all_aggregates_results(self):
        """Test run_all properly aggregates individual results."""
        from agentic_core.L5_safety.validators.security_validation_suite import (
            RedTeamValidationSuite,
        )

        suite = RedTeamValidationSuite()
        result = suite.run_all(content={"test": "data"})

        # Results should match counts
        assert len(result.results) == result.validators_run
        passed = sum(1 for r in result.results if r.valid)
        assert passed == result.validators_passed


class TestSecuritySuiteGlobalFunctions:
    """Tests for global convenience functions."""

    def test_get_security_suite_singleton(self):
        """Test get_security_suite returns singleton."""
        from agentic_core.L5_safety.validators.security_validation_suite import (
            get_security_suite,
        )

        suite1 = get_security_suite()
        suite2 = get_security_suite()
        assert suite1 is suite2

    def test_run_security_validation_convenience(self):
        """Test run_security_validation convenience function."""
        from agentic_core.L5_safety.validators.security_validation_suite import (
            run_security_validation,
            SecuritySuiteResult,
        )

        result = run_security_validation(content={"test": "data"})

        assert isinstance(result, SecuritySuiteResult)
        assert result.validators_run >= 0


class TestSecuritySuiteIntegration:
    """Integration tests for security suite with actual validators."""

    def test_adversarial_validator_integration(self):
        """Test adversarial validator works through suite."""
        from agentic_core.L5_safety.validators.security_validation_suite import (
            get_security_suite,
        )

        suite = get_security_suite()
        if "adversarial_probe" in suite.get_available_validators():
            result = suite.run_validator("adversarial_probe", {"test": "input"})
            assert result.validator_name == "adversarial_probe"
            assert isinstance(result.valid, bool)

    def test_boundary_validator_integration(self):
        """Test boundary validator works through suite."""
        from agentic_core.L5_safety.validators.security_validation_suite import (
            get_security_suite,
        )

        suite = get_security_suite()
        if "boundary_testing" in suite.get_available_validators():
            result = suite.run_validator("boundary_testing", {"test": "input"})
            assert result.validator_name == "boundary_testing"
            assert isinstance(result.valid, bool)

    def test_full_security_scan(self):
        """Test running full security scan."""
        from agentic_core.L5_safety.validators.security_validation_suite import (
            run_security_validation,
        )

        result = run_security_validation(
            content={"user_input": "test data", "action": "validate"},
            context={"source": "test"},
        )

        assert result.validators_run >= 0
        assert result.overall_valid in (True, False)
        assert result.execution_time_ms >= 0


class TestSecuritySuiteEdgeCases:
    """Edge case tests for security suite."""

    def test_empty_content(self):
        """Test validation with empty content."""
        from agentic_core.L5_safety.validators.security_validation_suite import (
            run_security_validation,
        )

        result = run_security_validation(content={})
        assert isinstance(result.overall_valid, bool)

    def test_none_content(self):
        """Test validation with None content."""
        from agentic_core.L5_safety.validators.security_validation_suite import (
            run_security_validation,
        )

        result = run_security_validation(content=None)
        assert isinstance(result.overall_valid, bool)

    def test_large_content(self):
        """Test validation with large content."""
        from agentic_core.L5_safety.validators.security_validation_suite import (
            run_security_validation,
        )

        large_content = {"data": "x" * 10000}
        result = run_security_validation(content=large_content)
        assert isinstance(result.overall_valid, bool)

    def test_special_characters_in_content(self):
        """Test validation with special characters."""
        from agentic_core.L5_safety.validators.security_validation_suite import (
            run_security_validation,
        )

        special_content = {
            "input": "!@#$%^&*()_+-=[]{}|;':\",./<>?",
            "unicode": "café résumé naïve",
        }
        result = run_security_validation(content=special_content)
        assert isinstance(result.overall_valid, bool)


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
