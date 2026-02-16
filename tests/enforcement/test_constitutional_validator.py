"""
Tests for ConstitutionalValidator - deterministic validation contracts.

Pure function validation only. No mocks, no monkeypatch, no filesystem writes.
"""

import pytest

from ops_scripts.enforcement.constitutional_validator import (
    ConstitutionalValidator,
    ValidationResult,
)


def test_validation_result_deterministic_repr():
    """Result repr must be deterministic without timestamps."""
    result = ValidationResult(is_valid=True, violations=[])
    expected = "ValidationResult(is_valid=True, violations=[])"
    assert repr(result) == expected


def test_validation_result_deterministic_repr_with_violations():
    """Result repr with violations must be deterministic."""
    result = ValidationResult(is_valid=False, violations=["error1", "error2"])
    expected = "ValidationResult(is_valid=False, violations=['error1', 'error2'])"
    assert repr(result) == expected


def test_validation_result_frozen_dataclass():
    """ValidationResult must be immutable."""
    result = ValidationResult(is_valid=True, violations=[])
    with pytest.raises(AttributeError):
        result.is_valid = False


def test_multiple_evidence_files_fail():
    """Multiple evidence files should fail validation."""
    validator = ConstitutionalValidator()
    phase_data = {"phase_id": "phase1", "evidence_files": ["file1.md", "file2.md"]}
    result = validator.validate_phase_execution(phase_data)
    assert not result.is_valid
    assert "Exactly 1 evidence file required, found 2" in result.violations


def test_exactly_one_evidence_file_pass():
    """Exactly one evidence file should pass validation."""
    validator = ConstitutionalValidator()
    phase_data = {"phase_id": "phase1", "evidence_files": ["evidence.md"]}
    result = validator.validate_phase_execution(phase_data)
    assert result.is_valid
    assert result.violations == []


def test_missing_phase_id_key_fail():
    """Missing phase_id key should fail."""
    validator = ConstitutionalValidator()
    phase_data = {"evidence_files": ["evidence.md"]}
    result = validator.validate_phase_execution(phase_data)
    assert not result.is_valid
    assert "Missing required key: phase_id" in result.violations


def test_missing_evidence_files_key_fail():
    """Missing evidence_files key should fail."""
    validator = ConstitutionalValidator()
    phase_data = {"phase_id": "phase1"}
    result = validator.validate_phase_execution(phase_data)
    assert not result.is_valid
    assert "Missing required key: evidence_files" in result.violations


def test_evidence_files_not_list_fail():
    """evidence_files must be a list."""
    validator = ConstitutionalValidator()
    phase_data = {"phase_id": "phase1", "evidence_files": "not-a-list"}
    result = validator.validate_phase_execution(phase_data)
    assert not result.is_valid
    assert "evidence_files must be a list" in result.violations


def test_empty_evidence_files_list_fail():
    """Empty evidence_files list should fail."""
    validator = ConstitutionalValidator()
    phase_data = {"phase_id": "phase1", "evidence_files": []}
    result = validator.validate_phase_execution(phase_data)
    assert not result.is_valid
    assert "Exactly 1 evidence file required, found 0" in result.violations


def test_acceptance_met_true_continued_true_fail():
    """acceptance_met=True and continued_execution=True should fail."""
    validator = ConstitutionalValidator()
    execution_result = {"acceptance_met": True, "continued_execution": True}
    result = validator.validate_stop_at_criteria(execution_result)
    assert not result.is_valid
    assert "Execution continued after acceptance met" in result.violations


def test_acceptance_met_true_continued_false_pass():
    """acceptance_met=True and continued_execution=False should pass."""
    validator = ConstitutionalValidator()
    execution_result = {"acceptance_met": True, "continued_execution": False}
    result = validator.validate_stop_at_criteria(execution_result)
    assert result.is_valid
    assert result.violations == []


def test_acceptance_met_false_continued_true_pass():
    """acceptance_met=False and continued_execution=True should pass."""
    validator = ConstitutionalValidator()
    execution_result = {"acceptance_met": False, "continued_execution": True}
    result = validator.validate_stop_at_criteria(execution_result)
    assert result.is_valid
    assert result.violations == []


def test_missing_acceptance_met_key_fail():
    """Missing acceptance_met key should fail."""
    validator = ConstitutionalValidator()
    execution_result = {"continued_execution": False}
    result = validator.validate_stop_at_criteria(execution_result)
    assert not result.is_valid
    assert "Missing required key: acceptance_met" in result.violations


def test_missing_continued_execution_key_fail():
    """Missing continued_execution key should fail."""
    validator = ConstitutionalValidator()
    execution_result = {"acceptance_met": True}
    result = validator.validate_stop_at_criteria(execution_result)
    assert not result.is_valid
    assert "Missing required key: continued_execution" in result.violations


def test_acceptance_met_not_bool_fail():
    """acceptance_met must be a bool."""
    validator = ConstitutionalValidator()
    execution_result = {"acceptance_met": "true", "continued_execution": False}
    result = validator.validate_stop_at_criteria(execution_result)
    assert not result.is_valid
    assert "acceptance_met must be a bool" in result.violations


def test_continued_execution_not_bool_fail():
    """continued_execution must be a bool."""
    validator = ConstitutionalValidator()
    execution_result = {"acceptance_met": True, "continued_execution": "false"}
    result = validator.validate_stop_at_criteria(execution_result)
    assert not result.is_valid
    assert "continued_execution must be a bool" in result.violations


def test_empty_dict_input_phase_fail():
    """Empty dict should fail phase validation."""
    validator = ConstitutionalValidator()
    result = validator.validate_phase_execution({})
    assert not result.is_valid
    assert "Missing required key: phase_id" in result.violations
    assert "Missing required key: evidence_files" in result.violations


def test_empty_dict_input_stop_fail():
    """Empty dict should fail stop-at validation."""
    validator = ConstitutionalValidator()
    result = validator.validate_stop_at_criteria({})
    assert not result.is_valid
    assert "Missing required key: acceptance_met" in result.violations
    assert "Missing required key: continued_execution" in result.violations


def test_deterministic_behavior_across_runs():
    """Validator must produce identical results across multiple runs."""
    validator = ConstitutionalValidator()
    phase_data = {"phase_id": "phase1", "evidence_files": ["evidence.md"]}
    execution_result = {"acceptance_met": True, "continued_execution": False}

    # Run multiple times
    results1 = validator.validate_phase_execution(phase_data)
    results2 = validator.validate_phase_execution(phase_data)
    results3 = validator.validate_stop_at_criteria(execution_result)
    results4 = validator.validate_stop_at_criteria(execution_result)

    # Results must be identical
    assert results1 == results2
    assert results3 == results4
    assert repr(results1) == repr(results2)
    assert repr(results3) == repr(results4)
