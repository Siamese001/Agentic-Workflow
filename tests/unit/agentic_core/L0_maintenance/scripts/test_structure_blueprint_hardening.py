import pytest
import re
import sys
from pathlib import Path

# Add the agentic_core path to import structure_blueprint
sys.path.insert(0, str(Path(__file__).parent.parent / "agentic_core" / "L5_safety" / "validators"))

from structure_blueprint import (
    has_forbidden_layer_prefix,
    is_broken_backup_file,
    is_app_specific_file,
    validate_no_duplicate_prefix,
    FORBIDDEN_LAYER_PREFIXES,
    APP_SPECIFIC_PATTERNS,
    FORBIDDEN_BACKUP_PATTERNS,
)


class TestStructureBlueprintHardening:
    """
    Aggressive verification of structure_blueprint.py logic.
    Target: 100% pass rate on all structural constraints.
    """

    def test_forbidden_layer_prefix_optimization(self):
        """
        Verify the tuple-based startswith optimization works correctly.
        """
        # Edge Case: Exact match
        assert has_forbidden_layer_prefix("L1_cognition.py") == "L1_"

        # Edge Case: Lowercase match
        assert has_forbidden_layer_prefix("l0_boot.py") == "l0_"

        # Edge Case: Priority prefix
        assert has_forbidden_layer_prefix("P1_core_agent.py") == "P1_"

        # Safe Case: No prefix
        assert has_forbidden_layer_prefix("my_agent.py") is None

        # Edge Case: Prefix inside name (should pass)
        assert has_forbidden_layer_prefix("valid_L1_file.py") is None

    def test_broken_backup_regex_compilation(self):
        """
        Verify regex compilation handles various backup patterns.
        """
        # Critical: Standard broken backup
        assert is_broken_backup_file("config.json.bak.123456") is True

        # Critical: .backup variant
        assert is_broken_backup_file("data.csv.backup.999") is True

        # Edge Case: Valid file ending in number (should pass)
        assert is_broken_backup_file("version_1.py") is False

        # Edge Case: .bak without number (should pass logic, though suspicious)
        # The regex requires \.\d+ at end
        assert is_broken_backup_file("file.bak") is False

    def test_app_specific_pattern_compilation(self):
        """
        Verify app-specific patterns are correctly compiled and matched.
        """
        # Regex Check: Resume Gen
        assert is_app_specific_file("rg_executor.py") is True

        # Regex Check: LinkedIn Connector
        assert is_app_specific_file("lic_scraper.py") is True

        # Regex Check: Dispatch tools
        assert is_app_specific_file("dispatch_resume_job.py") is True

        # Negative Check: Agentic Core file
        assert is_app_specific_file("agentic_core_logic.py") is False

    def test_duplicate_prefix_detection(self):
        """
        Verify the prefix stutter detection logic.
        """
        # Violation: Stutter
        has_viol, msg = validate_no_duplicate_prefix("healing_healing_strategies.py")
        assert has_viol is True
        assert "healing_" in msg

        # Violation: Triple stutter
        has_viol, msg = validate_no_duplicate_prefix("core_core_core.py")
        assert has_viol is True

        # Valid: Single prefix
        has_viol, msg = validate_no_duplicate_prefix("healing_strategies.py")
        assert has_viol is False

        # Valid: Distinct parts
        has_viol, msg = validate_no_duplicate_prefix("apps_rg_engine.py")
        assert has_viol is False

    def test_regex_compilation_integrity(self):
        """
        Ensure all patterns in the module are actually compiled Pattern objects.
        """
        for pattern in APP_SPECIFIC_PATTERNS:
            assert isinstance(pattern, re.Pattern), (
                "APP_SPECIFIC_PATTERNS must contain compiled regex objects"
            )

        for pattern in FORBIDDEN_BACKUP_PATTERNS:
            assert isinstance(pattern, re.Pattern), (
                "FORBIDDEN_BACKUP_PATTERNS must contain compiled regex objects"
            )

    def test_immutability_of_prefixes(self):
        """
        Ensure critical constants are immutable.
        """
        assert isinstance(FORBIDDEN_LAYER_PREFIXES, tuple), (
            "FORBIDDEN_LAYER_PREFIXES must be an immutable tuple"
        )

    def test_performance_optimization_validation(self):
        """
        Verify that the tuple-based startswith is actually faster than list iteration.
        This test ensures the optimization is working as intended.
        """
        import time

        # Test data
        test_files = ["L1_test.py", "l0_test.py", "P1_test.py", "normal_file.py"] * 1000

        # Test tuple startswith (optimized version)
        start_time = time.perf_counter()
        for filename in test_files:
            filename.startswith(FORBIDDEN_LAYER_PREFIXES)
        tuple_time = time.perf_counter() - start_time

        # Test list iteration (old version)
        prefixes_list = list(FORBIDDEN_LAYER_PREFIXES)
        start_time = time.perf_counter()
        for filename in test_files:
            for prefix in prefixes_list:
                if filename.startswith(prefix):
                    break
        list_time = time.perf_counter() - start_time

        # Tuple should be faster (or at least not significantly slower)
        assert tuple_time <= list_time * 1.1, (
            f"Tuple optimization failed: {tuple_time:.6f}s vs {list_time:.6f}s"
        )

    def test_edge_case_filenames(self):
        """
        Test edge cases that could break the validation logic.
        """
        # Empty string
        assert has_forbidden_layer_prefix("") is None
        assert is_app_specific_file("") is False
        assert is_broken_backup_file("") is False

        # Only extension
        assert has_forbidden_layer_prefix(".py") is None
        assert is_app_specific_file(".py") is False
        assert is_broken_backup_file(".py") is False

        # Unicode characters (should not crash)
        assert has_forbidden_layer_prefix("L1_测试.py") == "L1_"
        assert is_app_specific_file("rg_测试.py") is True

        # Very long filename
        long_name = "L1_" + "a" * 1000 + ".py"
        assert has_forbidden_layer_prefix(long_name) == "L1_"

    def test_regex_pattern_accuracy(self):
        """
        Verify regex patterns match exactly what they should and nothing more.
        """
        # Test APP_SPECIFIC_PATTERNS
        positive_cases = [
            "rg_executor.py",
            "lic_scraper.py",
            "resume_parser.py",
            "outreach_engine.py",
            "dispatch_resume_job.py",
            "dispatch_outreach_campaign.py",
        ]

        negative_cases = [
            "org_executor.py",  # rg -> org
            "lic_scraper.txt",  # wrong extension
            "resume_parser",  # missing extension
            "my_rg_file.py",  # rg not at start
            "dispatch.py",  # missing suffix
            "agentic_core.py",  # normal core file
        ]

        for case in positive_cases:
            assert is_app_specific_file(case), f"Should match: {case}"

        for case in negative_cases:
            assert not is_app_specific_file(case), f"Should not match: {case}"

    def test_backup_pattern_edge_cases(self):
        """
        Test backup file detection with various edge cases.
        """
        # Valid broken backups
        valid_broken = [
            "config.json.bak.123456",
            "data.csv.backup.999",
            "old_file.old.20240101",
            "temp.tmp.42",
            "nested.path.file.bak.999999",
        ]

        # Invalid (should not match)
        invalid_broken = [
            "config.json.bak",  # missing number
            "file.backup",  # missing number
            "data.txt.bak.abc",  # non-numeric suffix
            "normal_file.py",
            "backup_123.txt",  # different pattern
            "file.bak.12.34",  # multiple dots after .bak
        ]

        for case in valid_broken:
            assert is_broken_backup_file(case), f"Should detect as broken backup: {case}"

        for case in invalid_broken:
            assert not is_broken_backup_file(case), f"Should not detect as broken backup: {case}"

    def test_comprehensive_prefix_coverage(self):
        """
        Ensure all forbidden prefixes are properly tested.
        """
        # Test all layer prefixes
        layer_prefixes = ["l0_", "l1_", "l2_", "l3_", "l4_", "l5_", "l6_"]
        for prefix in layer_prefixes:
            filename = f"{prefix}test_file.py"
            assert has_forbidden_layer_prefix(filename) == prefix, f"Failed for {prefix}"

        # Test uppercase layer prefixes
        layer_prefixes_upper = ["L0_", "L1_", "L2_", "L3_", "L4_", "L5_", "L6_"]
        for prefix in layer_prefixes_upper:
            filename = f"{prefix}test_file.py"
            assert has_forbidden_layer_prefix(filename) == prefix, f"Failed for {prefix}"

        # Test priority prefixes
        priority_prefixes = ["p0_", "p1_", "p2_", "p3_"]
        for prefix in priority_prefixes:
            filename = f"{prefix}test_file.py"
            assert has_forbidden_layer_prefix(filename) == prefix, f"Failed for {prefix}"

        # Test uppercase priority prefixes
        priority_prefixes_upper = ["P0_", "P1_", "P2_", "P3_"]
        for prefix in priority_prefixes_upper:
            filename = f"{prefix}test_file.py"
            assert has_forbidden_layer_prefix(filename) == prefix, f"Failed for {prefix}"


if __name__ == "__main__":
    pytest.main(["-v", __file__])
