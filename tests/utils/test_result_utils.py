#!/usr/bin/env python3
"""
Test Suite: Result Normalization Utilities

Tests for agentic_core/utils/result_utils.py

All tests must pass 100% before proceeding to Phase 1.2.
"""
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import pytest
try:
    from agentic_core.utils.result_utils import (
        AgentResult,
        normalize_agent_result,
        aggregate_results,
        extract_violations,
        extract_fixes,
    )
except ImportError:
    # Fallback to archived location for legacy tests
    from archives.location_violations.result_utils import (
        AgentResult,
        normalize_agent_result,
        aggregate_results,
        extract_violations,
        extract_fixes,
    )


class TestAgentResult:
    """Tests for AgentResult dataclass."""
    
    def test_default_values(self):
        """Test AgentResult with default values."""
        result = AgentResult(agent_name="TestAgent")
        assert result.agent_name == "TestAgent"
        assert result.status == "UNKNOWN"
        assert result.violations_found == 0
        assert result.violations_fixed == 0
        assert result.execution_time_ms == 0
        assert result.error_message is None
        assert result.metadata == {}
    
    def test_is_success_property(self):
        """Test is_success property."""
        # Success case
        result = AgentResult(agent_name="Test", status="PASS", violations_found=0)
        assert result.is_success is True
        
        # Failure case
        result = AgentResult(agent_name="Test", status="FAIL", violations_found=5)
        assert result.is_success is False
        
        # PASS but with violations (edge case)
        result = AgentResult(agent_name="Test", status="PASS", violations_found=1)
        assert result.is_success is False
    
    def test_is_error_property(self):
        """Test is_error property."""
        result = AgentResult(agent_name="Test", status="ERROR")
        assert result.is_error is True
        
        result = AgentResult(agent_name="Test", status="PASS")
        assert result.is_error is False
    
    def test_is_skipped_property(self):
        """Test is_skipped property."""
        result = AgentResult(agent_name="Test", status="SKIPPED")
        assert result.is_skipped is True
        
        result = AgentResult(agent_name="Test", status="PASS")
        assert result.is_skipped is False
    
    def test_to_dict(self):
        """Test to_dict serialization."""
        result = AgentResult(
            agent_name="TestAgent",
            status="PASS",
            violations_found=3,
            violations_fixed=2,
            execution_time_ms=100,
            error_message=None,
            metadata={"key": "value"}
        )
        d = result.to_dict()
        assert d["agent_name"] == "TestAgent"
        assert d["status"] == "PASS"
        assert d["violations_found"] == 3
        assert d["violations_fixed"] == 2
        assert d["execution_time_ms"] == 100
        assert d["metadata"] == {"key": "value"}


class TestNormalizeAgentResult:
    """Tests for normalize_agent_result function."""
    
    def test_legacy_keys(self):
        """Test Case 1: Legacy Keys - violations_found and fixed."""
        raw = {"violations_found": 5, "fixed": 2}
        result = normalize_agent_result("TestAgent", raw)
        
        assert result.agent_name == "TestAgent"
        assert result.violations_found == 5
        assert result.violations_fixed == 2
        assert result.status == "FAIL"  # violations > 0
    
    def test_alternate_keys(self):
        """Test Case 2: Alternate Keys - errors and renamed."""
        raw = {"errors": 3, "renamed": 1}
        result = normalize_agent_result("TestAgent", raw)
        
        assert result.violations_found == 3
        assert result.violations_fixed == 1
        assert result.status == "FAIL"
    
    def test_none_result(self):
        """Test Case 3: None Result - should return SKIPPED."""
        result = normalize_agent_result("TestAgent", None)
        
        assert result.status == "SKIPPED"
        assert result.violations_found == 0
        assert result.violations_fixed == 0
        assert result.error_message == "Agent returned None"
    
    def test_zero_state(self):
        """Test Case 4: Zero State - no violations means PASS."""
        raw = {"violations": 0}
        result = normalize_agent_result("TestAgent", raw)
        
        assert result.status == "PASS"
        assert result.violations_found == 0
    
    def test_violations_key(self):
        """Test 'violations' key mapping."""
        raw = {"violations": 10, "violations_fixed": 5}
        result = normalize_agent_result("TestAgent", raw)
        
        assert result.violations_found == 10
        assert result.violations_fixed == 5
    
    def test_execution_time(self):
        """Test execution time is captured."""
        raw = {"violations": 0}
        result = normalize_agent_result("TestAgent", raw, execution_time_ms=500)
        
        assert result.execution_time_ms == 500
    
    def test_error_status(self):
        """Test error detection from status key."""
        raw = {"status": "ERROR", "error_message": "Something failed"}
        result = normalize_agent_result("TestAgent", raw)
        
        assert result.status == "ERROR"
        assert result.error_message == "Something failed"
    
    def test_error_from_error_key(self):
        """Test error detection from error key."""
        raw = {"error": "Import failed"}
        result = normalize_agent_result("TestAgent", raw)
        
        assert result.status == "ERROR"
        assert result.error_message == "Import failed"
    
    def test_non_dict_result(self):
        """Test handling of non-dict results."""
        result = normalize_agent_result("TestAgent", "string result")
        
        assert result.status == "ERROR"
        assert "Unexpected result type" in result.error_message
    
    def test_metadata_preservation(self):
        """Test that non-standard keys are preserved in metadata."""
        raw = {
            "violations": 1,
            "fixed": 1,
            "custom_key": "custom_value",
            "another_key": 42
        }
        result = normalize_agent_result("TestAgent", raw)
        
        assert result.metadata["custom_key"] == "custom_value"
        assert result.metadata["another_key"] == 42
    
    def test_string_number_conversion(self):
        """Test that string numbers are converted to int."""
        raw = {"violations": "5", "fixed": "3"}
        result = normalize_agent_result("TestAgent", raw)
        
        assert result.violations_found == 5
        assert result.violations_fixed == 3
    
    def test_invalid_number_handling(self):
        """Test handling of non-numeric values."""
        raw = {"violations": "not a number", "fixed": None}
        result = normalize_agent_result("TestAgent", raw)
        
        assert result.violations_found == 0
        assert result.violations_fixed == 0


class TestAggregateResults:
    """Tests for aggregate_results function."""
    
    def test_empty_list(self):
        """Test aggregation of empty list."""
        summary = aggregate_results([])
        
        assert summary["total_agents"] == 0
        assert summary["total_violations"] == 0
        assert summary["total_fixed"] == 0
        assert summary["is_stable"] is True
    
    def test_single_result(self):
        """Test aggregation of single result."""
        results = [
            AgentResult(
                agent_name="Agent1",
                status="FAIL",
                violations_found=5,
                violations_fixed=3,
                execution_time_ms=100
            )
        ]
        summary = aggregate_results(results)
        
        assert summary["total_agents"] == 1
        assert summary["total_violations"] == 5
        assert summary["total_fixed"] == 3
        assert summary["total_time_ms"] == 100
        assert summary["failed"] == 1
        assert summary["is_stable"] is False  # 5 - 3 = 2 unfixed
    
    def test_multiple_results(self):
        """Test aggregation of multiple results."""
        results = [
            AgentResult(agent_name="A1", status="PASS", violations_found=0, violations_fixed=0),
            AgentResult(agent_name="A2", status="FAIL", violations_found=10, violations_fixed=10),
            AgentResult(agent_name="A3", status="ERROR", violations_found=0, violations_fixed=0),
            AgentResult(agent_name="A4", status="SKIPPED", violations_found=0, violations_fixed=0),
        ]
        summary = aggregate_results(results)
        
        assert summary["total_agents"] == 4
        assert summary["passed"] == 1
        assert summary["failed"] == 1
        assert summary["errors"] == 1
        assert summary["skipped"] == 1
        assert summary["total_violations"] == 10
        assert summary["total_fixed"] == 10
    
    def test_is_stable_calculation(self):
        """Test is_stable calculation."""
        # All fixed -> stable
        results = [
            AgentResult(agent_name="A1", status="FAIL", violations_found=5, violations_fixed=5),
        ]
        assert aggregate_results(results)["is_stable"] is True
        
        # Not all fixed -> unstable
        results = [
            AgentResult(agent_name="A1", status="FAIL", violations_found=5, violations_fixed=3),
        ]
        assert aggregate_results(results)["is_stable"] is False
        
        # Error present -> unstable
        results = [
            AgentResult(agent_name="A1", status="ERROR", violations_found=0, violations_fixed=0),
        ]
        assert aggregate_results(results)["is_stable"] is False


class TestExtractViolations:
    """Tests for extract_violations helper."""
    
    def test_none_input(self):
        assert extract_violations(None) == 0
    
    def test_non_dict_input(self):
        assert extract_violations("string") == 0
        assert extract_violations(123) == 0
    
    def test_violations_found_key(self):
        assert extract_violations({"violations_found": 5}) == 5
    
    def test_violations_key(self):
        assert extract_violations({"violations": 3}) == 3
    
    def test_errors_key(self):
        assert extract_violations({"errors": 7}) == 7
    
    def test_priority_order(self):
        """violations_found takes priority over violations."""
        assert extract_violations({"violations_found": 10, "violations": 5}) == 10


class TestExtractFixes:
    """Tests for extract_fixes helper."""
    
    def test_none_input(self):
        assert extract_fixes(None) == 0
    
    def test_non_dict_input(self):
        assert extract_fixes("string") == 0
    
    def test_violations_fixed_key(self):
        assert extract_fixes({"violations_fixed": 5}) == 5
    
    def test_fixed_key(self):
        assert extract_fixes({"fixed": 3}) == 3
    
    def test_renamed_key(self):
        assert extract_fixes({"renamed": 7}) == 7
    
    def test_priority_order(self):
        """violations_fixed takes priority over fixed."""
        assert extract_fixes({"violations_fixed": 10, "fixed": 5}) == 10


def run_all_tests():
    """Run all tests and report results."""
    print("\n" + "#" * 60)
    print("# Result Utils Test Suite")
    print("#" * 60)
    
    # Run with pytest
    exit_code = pytest.main([__file__, "-v", "--tb=short"])
    
    if exit_code == 0:
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED (100%)")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ SOME TESTS FAILED")
        print("=" * 60)
    
    return exit_code


if __name__ == "__main__":
    sys.exit(run_all_tests())
