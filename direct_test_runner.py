import sys

sys.path.insert(0, '.')

from tests.enforcement.test_constitutional_validator import TestConstitutionalValidator, TestValidationResult


def run_tests():
    print("Running ConstitutionalValidator tests...")

    # ValidationResult tests
    test_result = TestValidationResult()
    try:
        test_result.test_deterministic_repr()
        print("✓ test_deterministic_repr")
    except Exception as e:
        print(f"✗ test_deterministic_repr: {e}")
        return False

    try:
        test_result.test_deterministic_repr_with_violations()
        print("✓ test_deterministic_repr_with_violations")
    except Exception as e:
        print(f"✗ test_deterministic_repr_with_violations: {e}")
        return False

    try:
        test_result.test_frozen_dataclass()
        print("✓ test_frozen_dataclass")
    except Exception as e:
        print(f"✗ test_frozen_dataclass: {e}")
        return False

    # ConstitutionalValidator tests
    test_constitutional = TestConstitutionalValidator()
    test_constitutional.setup_method()

    phase_tests = [
        "test_multiple_evidence_files_fail",
        "test_exactly_one_evidence_file_pass",
        "test_missing_phase_id_key_fail",
        "test_missing_evidence_files_key_fail",
        "test_evidence_files_not_list_fail",
        "test_empty_evidence_files_list_fail"
    ]

    stop_tests = [
        "test_acceptance_met_true_continued_true_fail",
        "test_acceptance_met_true_continued_false_pass",
        "test_acceptance_met_false_continued_true_pass",
        "test_missing_acceptance_met_key_fail",
        "test_missing_continued_execution_key_fail",
        "test_acceptance_met_not_bool_fail",
        "test_continued_execution_not_bool_fail"
    ]

    boundary_tests = [
        "test_empty_dict_input_phase_fail",
        "test_empty_dict_input_stop_fail",
        "test_deterministic_behavior_across_runs"
    ]

    for test_name in phase_tests + stop_tests + boundary_tests:
        try:
            getattr(test_constitutional, test_name)()
            print(f"✓ {test_name}")
        except Exception as e:
            print(f"✗ {test_name}: {e}")
            return False

    print("\nAll 19 tests passed!")
    return True

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
