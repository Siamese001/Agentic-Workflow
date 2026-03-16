import pytest

from agentic_core.L5_safety.reasoning.HygieneGuardianAgent import HygieneGuardianAgent
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_hygiene_guardian_enhanced")
_emit_applies_guardrail("p0", "test_hygiene_guardian_enhanced", "p0_governance")
_emit_reads_policy_state("p0", "test_hygiene_guardian_enhanced", "policy_binding")
_emit_snapshots_state("p0", "test_hygiene_guardian_enhanced", "state_snapshot")
emit_replay_key("p0", "test_hygiene_guardian_enhanced")
emit_determinism_digest("p0", "test_hygiene_guardian_enhanced")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

# MANDATORY: 100% TEST PASS REQUIRED


@pytest.fixture
def disable_path_shield():
    return True


class TestHygieneGuardianNamingEnhanced:
    def setup_method(self):
        self.tmp_path = None

    def test_camel_case_splitting(self, tmp_path, disable_path_shield):
        """
        Ensures CamelCase files are counted correctly.
        'MyVeryLongFileNameDetector.py' should be 6 words, not 1.
        """
        guardian = HygieneGuardianAgent(project_root=tmp_path)

        # "My", "Very", "Long", "File", "Name", "Detector" = 6 words
        filename = "MyVeryLongFileNameDetector.py"
        test_file = tmp_path / filename
        test_file.write_text("# Test", encoding="utf-8")

        guardian._check_filename_length(test_file)

        assert len(guardian.naming_violations) == 1, "Failed to detect violation in CamelCase file"
        assert guardian.naming_violations[0]["current_count"] == 6
        print("✅ PASS: CamelCase Splitting")

    def test_mixed_delimiters(self, tmp_path, disable_path_shield):
        """
        Ensures mixed delimiters (hyphens and underscores) are handled.
        """
        guardian = HygieneGuardianAgent(project_root=tmp_path)

        # "scripts", "deploy", "cluster", "east", "us", "region" = 6 words
        filename = "scripts-deploy_cluster-east_us_region.py"
        test_file = tmp_path / filename
        test_file.write_text("# Test", encoding="utf-8")

        guardian._check_filename_length(test_file)

        assert len(guardian.naming_violations) == 1, "Failed to detect violation in mixed delimiter file"
        assert guardian.naming_violations[0]["current_count"] == 6
        print("✅ PASS: Mixed Delimiters")

    def test_test_file_leniency(self, tmp_path, disable_path_shield):
        """
        Ensures test files have a higher word limit (8) than standard files (5).
        """
        guardian = HygieneGuardianAgent(project_root=tmp_path)

        # 7 words: "test", "user", "login", "fails", "with", "invalid", "password"
        # Standard limit (5) would fail, Test limit (8) should pass.
        filename = "test_user_login_fails_with_invalid_password.py"
        test_file = tmp_path / filename
        test_file.write_text("# Test", encoding="utf-8")

        guardian._check_filename_length(test_file)
        assert len(guardian.naming_violations) == 0, (
            "Test file flagged incorrectly. Should allow 7 words with limit 8"
        )

        # 10 words: should fail (exceeds limit of 8)
        long_filename = "test_user_login_fails_with_invalid_password_and_username_retry.py"
        long_file = tmp_path / long_filename
        long_file.write_text("# Test", encoding="utf-8")

        guardian._check_filename_length(long_file)
        assert len(guardian.naming_violations) == 1
        assert guardian.naming_violations[0]["current_count"] == 10
        print("✅ PASS: Test File Leniency")

    def test_smart_suggestion_preservation(self, tmp_path, disable_path_shield):
        """
        Verifies that the suggestion engine removes stop words before truncation.
        """
        guardian = HygieneGuardianAgent(project_root=tmp_path)

        # 6 words: "payment", "gateway", "service", "implementation", "stripe", "connector"
        # "service" and "implementation" are in REDUNDANT_TERMS
        words = ["payment", "gateway", "service", "implementation", "stripe", "connector"]
        suggestion = guardian._generate_concise_suggestion(words, ".py")

        assert "service" not in suggestion
        assert "implementation" not in suggestion
        assert suggestion == "payment_gateway_stripe_connector.py"
        print("✅ PASS: Smart Suggestion Logic")

    def test_standard_file_strict_limit(self, tmp_path, disable_path_shield):
        """
        Verifies that non-test files are held to the 5-word limit.
        """
        guardian = HygieneGuardianAgent(project_root=tmp_path)

        # 6 words: should fail for standard files
        filename = "user_authentication_service_manager_handler_utils.py"
        test_file = tmp_path / filename
        test_file.write_text("# Test", encoding="utf-8")

        guardian._check_filename_length(test_file)

        assert len(guardian.naming_violations) == 1
        assert guardian.naming_violations[0]["current_count"] == 6
        assert guardian.naming_violations[0]["limit"] == 5
        print("✅ PASS: Standard File Strict Limit")

    def test_redundant_term_removal(self, tmp_path, disable_path_shield):
        """
        Verifies that redundant terms are removed from suggestions.
        """
        guardian = HygieneGuardianAgent(project_root=tmp_path)

        # Test with multiple redundant terms
        words = ["data", "management", "service", "implementation", "utility", "handler"]
        # Should remove: management, service, implementation, utility
        # Remaining: data, handler (2 words)
        suggestion = guardian._generate_concise_suggestion(words, ".py")

        assert "management" not in suggestion
        assert "service" not in suggestion
        assert "implementation" not in suggestion
        assert "utility" not in suggestion
        assert suggestion == "data_handler.py"
        print("✅ PASS: Redundant Term Removal")


# MANDATORY: 100% TEST PASS REQUIRED
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
