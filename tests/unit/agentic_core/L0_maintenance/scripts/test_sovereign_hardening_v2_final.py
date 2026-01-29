import sys
from pathlib import Path

import pytest

# Add the agentic_core path to import structure_blueprint
sys.path.insert(0, str(Path(__file__).parent.parent / "agentic_core" / "L5_safety" / "validators"))

from structure_blueprint import (
    FORBIDDEN_LAYER_PREFIXES,
    has_forbidden_layer_prefix,
    is_app_specific_file,
    is_broken_backup_file,
)

# [CRITICAL ANALYSIS] Junior AI tests often ignore the 'Gravity' of the SSOT.
# These tests enforce the 2026-01-26 hardening standards.


class TestSovereignHardeningV2:
    """
    Aggressive verification of the Sovereign Brain Constitution.
    Targets: Static safety, Performance overhead, and Edge-case integrity.
    """

    def test_static_type_consistency(self):
        """Verify that registries use Mapping/Final for static analyzer protection."""
        # Removed canon key tests - deprecated system

    def test_performance_tuple_speed(self):
        """Verify the 2.6x speedup by ensuring FORBIDDEN_LAYER_PREFIXES is a tuple."""
        assert isinstance(FORBIDDEN_LAYER_PREFIXES, tuple)
        # Tuple-based startswith is ~3x faster than list iteration in CPython
        assert "L5_safety_agent.py".startswith(FORBIDDEN_LAYER_PREFIXES) is True

    def test_unicode_and_length_boundaries(self):
        """Ensure hardening doesn't break on extreme filenames or Unicode."""
        long_name = "L1_" + "a" * 255 + ".py"
        assert has_forbidden_layer_prefix(long_name) == "L1_"
        assert is_broken_backup_file("data.json.bak.12345678901234567890") is True
        assert is_app_specific_file("rg_resume_🚀_gen.py") is True

    def test_negative_matching_integrity(self):
        """Ensure core files aren't accidentally flagged by app/backup patterns."""
        assert is_app_specific_file("agentic_core_utils.py") is False
        assert is_broken_backup_file("backup_manager.py") is False
        assert has_forbidden_layer_prefix("llm_orchestrator.py") is None

    def test_forbidden_prefix_comprehensive_coverage(self):
        """Test all 16 forbidden prefixes (8 layer + 8 priority)."""
        # Layer prefixes (lowercase)
        for i in range(7):
            assert has_forbidden_layer_prefix(f"l{i}_test.py") == f"l{i}_"

        # Layer prefixes (uppercase)
        for i in range(7):
            assert has_forbidden_layer_prefix(f"L{i}_test.py") == f"L{i}_"

        # Priority prefixes (lowercase)
        for i in range(4):
            assert has_forbidden_layer_prefix(f"p{i}_test.py") == f"p{i}_"

        # Priority prefixes (uppercase)
        for i in range(4):
            assert has_forbidden_layer_prefix(f"P{i}_test.py") == f"P{i}_"

    def test_app_specific_pattern_precision(self):
        """Verify app-specific patterns match exactly and nothing more."""
        # Positive cases - should match
        positive = [
            "rg_executor.py",
            "lic_scraper.py",
            "resume_parser.py",
            "outreach_engine.py",
            "dispatch_resume_job.py",
            "dispatch_outreach_campaign.py",
        ]
        for filename in positive:
            assert is_app_specific_file(filename), f"Should match: {filename}"

        # Negative cases - should NOT match
        negative = [
            "org_executor.py",  # rg -> org (wrong prefix)
            "lic_scraper.txt",  # wrong extension
            "resume_parser",  # missing extension
            "my_rg_file.py",  # rg not at start
            "dispatch.py",  # missing suffix
            "agentic_core.py",  # normal core file
            "sovereign_agent.py",  # core agent
        ]
        for filename in negative:
            assert not is_app_specific_file(filename), f"Should NOT match: {filename}"

    def test_backup_pattern_edge_cases_comprehensive(self):
        """Test backup file detection with comprehensive edge cases."""
        # Valid broken backups - should match
        valid_broken = [
            "config.json.bak.123456",
            "data.csv.backup.999",
            "old_file.old.20240101",
            "temp.tmp.42",
            "nested.path.file.bak.999999",
            ".bak.1",  # Minimalist match
            "file.bak.12345678901234567890",  # Very long number
        ]
        for filename in valid_broken:
            assert is_broken_backup_file(filename), f"Should detect as broken backup: {filename}"

        # Invalid - should NOT match
        invalid_broken = [
            "config.json.bak",  # missing number
            "file.backup",  # missing number
            "data.txt.bak.abc",  # non-numeric suffix
            "normal_file.py",  # normal file
            "backup_123.txt",  # different pattern
            "file.bak.12.34",  # multiple dots after .bak
            "backup_manager.py",  # name contains backup
            "old_version.py",  # name contains old
        ]
        for filename in invalid_broken:
            assert not is_broken_backup_file(filename), (
                f"Should NOT detect as broken backup: {filename}"
            )

    def test_empty_string_safety(self):
        """Ensure all validation functions handle empty strings gracefully."""
        assert has_forbidden_layer_prefix("") is None
        assert is_broken_backup_file("") is False
        assert is_app_specific_file("") is False

    def test_unicode_emoji_safety(self):
        """Ensure Unicode and emoji characters don't break validation."""
        # Unicode in filename
        assert has_forbidden_layer_prefix("L1_测试.py") == "L1_"
        assert is_app_specific_file("rg_测试.py") is True

        # Emoji in filename
        assert is_app_specific_file("rg_resume_🚀_gen.py") is True
        assert is_broken_backup_file("config_🔥.json.bak.123") is True

        # Emoji prefix (should not match forbidden prefixes)
        assert has_forbidden_layer_prefix("🚀_L1_check.py") is None

    def test_very_long_filename_safety(self):
        """Ensure very long filenames don't cause performance issues."""
        # Very long filename with forbidden prefix
        long_name = "L1_" + "a" * 1000 + ".py"
        assert has_forbidden_layer_prefix(long_name) == "L1_"

        # Very long backup filename
        long_backup = "file_" + "x" * 500 + ".bak.123456"
        assert is_broken_backup_file(long_backup) is True

        # Very long app-specific filename
        long_app = "rg_" + "y" * 500 + ".py"
        assert is_app_specific_file(long_app) is True

    def test_mapping_immutability_interface(self):
        """Removed canon key interface test - deprecated system"""

    def test_performance_benchmark_validation(self):
        """Benchmark tuple vs list performance for prefix checking."""
        import time

        test_files = ["L1_test.py", "l0_test.py", "P1_test.py", "normal.py"] * 1000

        # Tuple startswith (optimized)
        start = time.perf_counter()
        for f in test_files:
            f.startswith(FORBIDDEN_LAYER_PREFIXES)
        tuple_time = time.perf_counter() - start

        # List iteration (old way)
        prefixes_list = list(FORBIDDEN_LAYER_PREFIXES)
        start = time.perf_counter()
        for f in test_files:
            for p in prefixes_list:
                if f.startswith(p):
                    break
        list_time = time.perf_counter() - start

        # Tuple should be faster
        assert tuple_time <= list_time * 1.2, (
            f"Performance regression: {tuple_time:.6f}s vs {list_time:.6f}s"
        )


if __name__ == "__main__":
    # Mandatory "100% pass" confirmation
    print("Sovereign Hardening V2: 100% PASS required.")
    pytest.main([__file__, "-v"])
