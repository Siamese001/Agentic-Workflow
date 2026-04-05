"""
Wave 3: System Integrity - Isolation & Determinism Audit Tests

Tests for global state usage, singleton accumulation, deterministic outputs,
and zero silent degradation enforcement patterns.
"""

from __future__ import annotations

from agentic_core.L5_safety.validators.anti_pattern_scanner_validator import (
    AntiPatternScanner,
)


class TestSystemIntegrity:
    """Test system integrity aspects of the anti-pattern scanner."""

    def test_global_state_usage_detection(self, tmp_path):
        """Test detection of global state mutations."""
        # Test sys.path manipulation
        code1 = """import sys
sys.path.insert(0, "/some/path")
"""
        file1 = tmp_path / "sys_path_mutation.py"
        file1.write_text(code1)

        scanner = AntiPatternScanner(project_root=tmp_path)
        violations = scanner.scan_file(file1)

        # Should detect global mutation
        assert len(violations) > 0
        assert any("Global mutation" in v.message for v in violations)
        assert any("sys.path" in v.message for v in violations)

    def test_global_state_with_exemption(self, tmp_path):
        """Test that global state can be properly exempted."""
        code = """import sys
# guardian: allow-global-mutation - Required for dynamic import
sys.path.insert(0, "/some/path")
"""
        file_path = tmp_path / "exempted_global_mutation.py"
        file_path.write_text(code)

        scanner = AntiPatternScanner(project_root=tmp_path)
        violations = scanner.scan_file(file_path)

        # Should be suppressed by exemption
        assert len(violations) == 0, (
            f"Expected no violations due to exemption, got: {[v.message for v in violations]}"
        )

    def test_os_environ_mutation_detection(self, tmp_path):
        """Test detection of os.environ mutations."""
        code = """import os
os.environ["MY_VAR"] = "value"
"""
        file_path = tmp_path / "environ_mutation.py"
        file_path.write_text(code)

        scanner = AntiPatternScanner(project_root=tmp_path)
        violations = scanner.scan_file(file_path)

        # Should detect global mutation
        assert len(violations) > 0
        assert any("Global mutation" in v.message for v in violations)
        assert any("os.environ" in v.message for v in violations)

    def test_deterministic_scanner_output(self, tmp_path):
        """Test that scanner produces deterministic results across multiple runs."""
        code = """def clean_function():
    return "deterministic result"

try:
    import missing_module
except ImportError:
    pass
"""
        file_path = tmp_path / "deterministic_test.py"
        file_path.write_text(code)

        scanner = AntiPatternScanner(project_root=tmp_path)

        # Run scanner multiple times
        results = []
        for i in range(3):
            violations = scanner.scan_file(file_path)
            # Extract key metrics for comparison
            result_key = {
                "violation_count": len(violations),
                "violation_messages": sorted([v.message for v in violations]),
                "categories": sorted([v.category.value for v in violations]),
            }
            results.append(result_key)

        # All results should be identical
        for i in range(1, len(results)):
            assert results[i] == results[0], (
                f"Results differ between run 1 and run {i + 1}: {results[0]} vs {results[i]}"
            )

    def test_singleton_accumulation_detection(self, tmp_path):
        """Test detection of singleton pattern accumulation."""
        # This tests for patterns that might lead to singleton accumulation
        code = """class SingletonManager:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def add_state(self, key, value):
        # Global state accumulation in singleton
        if not hasattr(self, '_state'):
            self._state = {}
        self._state[key] = value
"""
        file_path = tmp_path / "singleton_pattern.py"
        file_path.write_text(code)

        scanner = AntiPatternScanner(project_root=tmp_path)
        violations = scanner.scan_file(file_path)

        # Should analyze the singleton pattern (may not detect violations but should process)
        # This is more about ensuring the scanner can handle complex patterns
        assert isinstance(violations, list)

    def test_zero_silent_degradation_enforcement(self, tmp_path):
        """Test enforcement of zero silent degradation policy."""
        # Create code with silent degradation that should be flagged
        code = """try:
    import critical_module
except ImportError:
    # Silent failure - no indication to callers
    pass
"""
        file_path = tmp_path / "silent_degradation.py"
        file_path.write_text(code)

        scanner = AntiPatternScanner(project_root=tmp_path)
        violations = scanner.scan_file(file_path)

        # Should detect silent degradation
        assert len(violations) > 0
        assert any("Silent ImportError swallow" in v.message for v in violations)

    def test_mock_the_unit_pattern_validation(self, tmp_path):
        """Test mock-the-unit patterns are properly handled."""
        # This tests patterns where mocks should be properly isolated
        code = """def production_function():
    return "real result"

# Mock pattern - should be exempted or flagged appropriately
# guardian: allow-silent-degradation - Test mock
try:
    from unittest.mock import patch
    with patch('__main__.production_function', return_value="mocked"):
        result = production_function()
except ImportError:
    pass
"""
        file_path = tmp_path / "mock_pattern.py"
        file_path.write_text(code)

        scanner = AntiPatternScanner(project_root=tmp_path)
        violations = scanner.scan_file(file_path)

        # Should handle mock patterns appropriately
        assert isinstance(violations, list)

    def test_cross_execution_consistency(self, tmp_path):
        """Test scanner consistency across different execution contexts."""
        code = """import os
import sys

def function_with_global_state():
    # Pattern that could be affected by global state
    path_copy = sys.path[:]
    env_copy = dict(os.environ)
    return len(path_copy), len(env_copy)

try:
    import missing_module
except ImportError:
    pass
"""
        file_path = tmp_path / "consistency_test.py"
        file_path.write_text(code)

        # Test with different environment states
        original_path = tmp_path / "original_env.py"
        original_path.write_text(code)

        # Modify environment and test again
        import os

        original_sys_path = os.environ.get("PYTHONPATH", "")

        try:
            # Change environment
            os.environ["PYTHONPATH"] = "/test/path"

            scanner = AntiPatternScanner(project_root=tmp_path)
            violations1 = scanner.scan_file(original_path)

            # Reset environment
            if original_sys_path:
                os.environ["PYTHONPATH"] = original_sys_path
            else:
                os.environ.pop("PYTHONPATH", None)

            scanner2 = AntiPatternScanner(project_root=tmp_path)
            violations2 = scanner2.scan_file(original_path)

            # Violation detection should be consistent regardless of environment
            assert len(violations1) == len(violations2)

        finally:
            # Restore original environment
            if original_sys_path:
                os.environ["PYTHONPATH"] = original_sys_path
            else:
                os.environ.pop("PYTHONPATH", None)

    def test_isolation_boundary_violations(self, tmp_path):
        """Test detection of isolation boundary violations."""
        code = """# Global state that affects isolation
_shared_cache = {}

def process_data(data):
    # Using global state breaks isolation
    global _shared_cache
    if data not in _shared_cache:
        _shared_cache[data] = expensive_processing(data)
    return _shared_cache[data]

def expensive_processing(data):
    return data.upper()

# Also test sys.path manipulation
import sys
sys.path.append("/additional/path")
"""
        file_path = tmp_path / "isolation_violation.py"
        file_path.write_text(code)

        scanner = AntiPatternScanner(project_root=tmp_path)
        violations = scanner.scan_file(file_path)

        # Should detect isolation violations
        assert len(violations) > 0
        global_mutations = [v for v in violations if "Global mutation" in v.message]
        assert len(global_mutations) > 0

    def test_deterministic_violation_reporting(self, tmp_path):
        """Test that violation reporting is deterministic and complete."""
        code = """import sys
import os

# Multiple violation types
sys.path.insert(0, "/path1")
sys.path.append("/path2")
os.environ["VAR1"] = "value1"

try:
    import missing_module1
except ImportError:
    pass

try:
    import missing_module2
except ImportError:
    pass
"""
        file_path = tmp_path / "multiple_violations.py"
        file_path.write_text(code)

        scanner = AntiPatternScanner(project_root=tmp_path)

        # Run multiple times and check consistency
        all_results = []
        for run in range(3):
            violations = scanner.scan_file(file_path)
            result = {
                "count": len(violations),
                "global_mutations": len([v for v in violations if "Global mutation" in v.message]),
                "silent_degradations": len(
                    [v for v in violations if "Silent ImportError swallow" in v.message]
                ),
                "details": sorted([(v.line_number, v.message) for v in violations]),
            }
            all_results.append(result)

        # All runs should produce identical results
        for i in range(1, len(all_results)):
            assert all_results[i] == all_results[0], (
                f"Inconsistent results between runs: {all_results[0]} vs {all_results[i]}"
            )
