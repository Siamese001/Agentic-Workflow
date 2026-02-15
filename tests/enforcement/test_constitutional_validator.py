"""
Tests for ConstitutionalValidator - deterministic validation contracts.

Pure function validation only. No mocks, no monkeypatch, no filesystem writes.
"""

import pytest

from ops_scripts.enforcement.constitutional_validator import (
    ConstitutionalValidator,
    ValidationResult,
)


class TestValidationResult:
    """Test ValidationResult deterministic behavior."""

    def test_deterministic_repr(self):
        """Result repr must be deterministic without timestamps."""
        result = ValidationResult(is_valid=True, violations=[])
        expected = "ValidationResult(is_valid=True, violations=[])"
        assert repr(result) == expected

    def test_deterministic_repr_with_violations(self):
        """Result repr with violations must be deterministic."""
        result = ValidationResult(is_valid=False, violations=["error1", "error2"])
        expected = "ValidationResult(is_valid=False, violations=['error1', 'error2'])"
        assert repr(result) == expected

    def test_frozen_dataclass(self):
        """ValidationResult must be immutable."""
        result = ValidationResult(is_valid=True, violations=[])
        with pytest.raises(AttributeError):
            result.is_valid = False


class TestConstitutionalValidator:
    """Test ConstitutionalValidator enforcement rules."""

    def setup_method(self):
        """Create fresh validator for each test."""
        self.validator = ConstitutionalValidator()

    # Phase execution validation tests
    def test_multiple_evidence_files_fail(self):
        """Multiple evidence files should fail validation."""
        phase_data = {
            "phase_id": "phase1",
            "evidence_files": ["file1.md", "file2.md"]
        }
        result = self.validator.validate_phase_execution(phase_data)
        assert not result.is_valid
        assert "Exactly 1 evidence file required, found 2" in result.violations

    def test_exactly_one_evidence_file_pass(self):
        """Exactly one evidence file should pass validation."""
        phase_data = {
            "phase_id": "phase1",
            "evidence_files": ["evidence.md"]
        }
        result = self.validator.validate_phase_execution(phase_data)
        assert result.is_valid
        assert result.violations == []

    def test_missing_phase_id_key_fail(self):
        """Missing phase_id key should fail."""
        phase_data = {
            "evidence_files": ["evidence.md"]
        }
        result = self.validator.validate_phase_execution(phase_data)
        assert not result.is_valid
        assert "Missing required key: phase_id" in result.violations

    def test_missing_evidence_files_key_fail(self):
        """Missing evidence_files key should fail."""
        phase_data = {
            "phase_id": "phase1"
        }
        result = self.validator.validate_phase_execution(phase_data)
        assert not result.is_valid
        assert "Missing required key: evidence_files" in result.violations

    def test_evidence_files_not_list_fail(self):
        """evidence_files must be a list."""
        phase_data = {
            "phase_id": "phase1",
            "evidence_files": "not-a-list"
        }
        result = self.validator.validate_phase_execution(phase_data)
        assert not result.is_valid
        assert "evidence_files must be a list" in result.violations

    def test_empty_evidence_files_list_fail(self):
        """Empty evidence_files list should fail."""
        phase_data = {
            "phase_id": "phase1",
            "evidence_files": []
        }
        result = self.validator.validate_phase_execution(phase_data)
        assert not result.is_valid
        assert "Exactly 1 evidence file required, found 0" in result.violations

    # Stop-at criteria validation tests
    def test_acceptance_met_true_continued_true_fail(self):
        """acceptance_met=True and continued_execution=True should fail."""
        execution_result = {
            "acceptance_met": True,
            "continued_execution": True
        }
        result = self.validator.validate_stop_at_criteria(execution_result)
        assert not result.is_valid
        assert "Execution continued after acceptance met" in result.violations

    def test_acceptance_met_true_continued_false_pass(self):
        """acceptance_met=True and continued_execution=False should pass."""
        execution_result = {
            "acceptance_met": True,
            "continued_execution": False
        }
        result = self.validator.validate_stop_at_criteria(execution_result)
        assert result.is_valid
        assert result.violations == []

    def test_acceptance_met_false_continued_true_pass(self):
        """acceptance_met=False and continued_execution=True should pass."""
        execution_result = {
            "acceptance_met": False,
            "continued_execution": True
        }
        result = self.validator.validate_stop_at_criteria(execution_result)
        assert result.is_valid
        assert result.violations == []

    def test_missing_acceptance_met_key_fail(self):
        """Missing acceptance_met key should fail."""
        execution_result = {
            "continued_execution": False
        }
        result = self.validator.validate_stop_at_criteria(execution_result)
        assert not result.is_valid
        assert "Missing required key: acceptance_met" in result.violations

    def test_missing_continued_execution_key_fail(self):
        """Missing continued_execution key should fail."""
        execution_result = {
            "acceptance_met": True
        }
        result = self.validator.validate_stop_at_criteria(execution_result)
        assert not result.is_valid
        assert "Missing required key: continued_execution" in result.violations

    def test_acceptance_met_not_bool_fail(self):
        """acceptance_met must be a bool."""
        execution_result = {
            "acceptance_met": "true",
            "continued_execution": False
        }
        result = self.validator.validate_stop_at_criteria(execution_result)
        assert not result.is_valid
        assert "acceptance_met must be a bool" in result.violations

    def test_continued_execution_not_bool_fail(self):
        """continued_execution must be a bool."""
        execution_result = {
            "acceptance_met": True,
            "continued_execution": "false"
        }
        result = self.validator.validate_stop_at_criteria(execution_result)
        assert not result.is_valid
        assert "continued_execution must be a bool" in result.violations

    # Boundary tests
    def test_empty_dict_input_phase_fail(self):
        """Empty dict should fail phase validation."""
        result = self.validator.validate_phase_execution({})
        assert not result.is_valid
        assert "Missing required key: phase_id" in result.violations
        assert "Missing required key: evidence_files" in result.violations

    def test_empty_dict_input_stop_fail(self):
        """Empty dict should fail stop-at validation."""
        result = self.validator.validate_stop_at_criteria({})
        assert not result.is_valid
        assert "Missing required key: acceptance_met" in result.violations
        assert "Missing required key: continued_execution" in result.violations

    def test_deterministic_behavior_across_runs(self):
        """Validator must produce identical results across multiple runs."""
        phase_data = {
            "phase_id": "phase1",
            "evidence_files": ["evidence.md"]
        }
        execution_result = {
            "acceptance_met": True,
            "continued_execution": False
        }

        # Run multiple times
        results1 = self.validator.validate_phase_execution(phase_data)
        results2 = self.validator.validate_phase_execution(phase_data)
        results3 = self.validator.validate_stop_at_criteria(execution_result)
        results4 = self.validator.validate_stop_at_criteria(execution_result)

        # Results must be identical
        assert results1 == results2
        assert results3 == results4
        assert repr(results1) == repr(results2)
        assert repr(results3) == repr(results4)
