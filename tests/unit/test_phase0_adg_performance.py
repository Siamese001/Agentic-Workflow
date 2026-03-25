"""Phase 0 Test Suite - Bootstrap Emitter Cleanup and Session Fixtures.

Tests for Phase 0.1 (emitter stripping) and Phase 0.2 (session fixtures)
with proper verification and performance measurement.
"""

import pytest
import time
import ast
from pathlib import Path
from typing import List

# Import the tools we're testing
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))
from strip_test_emitters import find_emitter_calls, EMITTER_CALL_PATTERN


class TestBootstrapEmitterCleanup:
    """Test suite for Phase 0.1: Bootstrap emitter cleanup."""
    
    def test_find_emitter_calls_empty_file(self):
        """Test that empty files return no emitter calls."""
        content = ""
        calls = find_emitter_calls(content)
        assert calls == []
    
    def test_find_emitter_calls_no_emitters(self):
        """Test that files without emitters return empty list."""
        content = """
import pytest
from agentic_core.adg.extraction.static_scanner import ADGStaticScanner

def test_something():
    assert True
"""
        calls = find_emitter_calls(content)
        assert calls == []
    
    def test_find_emitter_calls_single_emitter(self):
        """Test detection of a single top-level emitter call."""
        content = """
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import _emit_records_execution_trace

_emit_records_execution_trace("test", "module", "action")

def test_something():
    assert True
"""
        calls = find_emitter_calls(content)
        assert len(calls) == 1
        assert calls[0][0] == 3  # Line number
        assert "_emit_records_execution_trace" in calls[0][1]
    
    def test_find_emitter_calls_multiple_emitters(self):
        """Test detection of multiple top-level emitter calls."""
        content = """
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_records_execution_trace,
    _emit_applies_guardrail,
    _emit_reads_policy_state
)

_emit_records_execution_trace("test", "module", "action1")
_emit_applies_guardrail("test", "file", "rule")
_emit_reads_policy_state("test", "module")

def test_something():
    assert True
"""
        calls = find_emitter_calls(content)
        assert len(calls) == 3
        assert calls[0][0] == 7
        assert calls[1][0] == 8
        assert calls[2][0] == 9
    
    def test_find_emitter_calls_ignores_function_calls(self):
        """Test that emitter calls inside functions are ignored."""
        content = """
def test_something():
    _emit_records_execution_trace("test", "module", "action")
    assert True

class TestClass:
    def test_method(self):
        _emit_applies_guardrail("test", "file", "rule")
"""
        calls = find_emitter_calls(content)
        assert len(calls) == 0
    
    def test_find_emitter_calls_ignores_comments(self):
        """Test that commented emitter calls are ignored."""
        content = """
# _emit_records_execution_trace("test", "module", "action")
# _emit_applies_guardrail("test", "file", "rule")
"""
        calls = find_emitter_calls(content)
        assert len(calls) == 0
    
    def test_emitter_pattern_matches(self):
        """Test that the emitter pattern matches correctly."""
        valid_calls = [
            "_emit_records_execution_trace('test', 'module', 'action')",
            "_emit_applies_guardrail(test_file, rule_name)",
            "_emit_reads_policy_state('test')",
            "_emit_snapshots_state('test', 'snapshot')"
        ]
        
        for call in valid_calls:
            assert EMITTER_CALL_PATTERN.match(call), f"Pattern should match: {call}"
    
    def test_emitter_pattern_rejects_invalid(self):
        """Test that the emitter pattern rejects invalid calls."""
        invalid_calls = [
            "emit_records_execution_trace('test', 'module')",  # Missing underscore
            "_emit_records_execution_trace(",  # Incomplete
            "def _emit_records_execution_trace():",  # Function definition
            "    _emit_records_execution_trace('test')",  # Indented
        ]
        
        for call in invalid_calls:
            assert not EMITTER_CALL_PATTERN.match(call), f"Pattern should reject: {call}"


class TestSessionADGFixtures:
    """Test suite for Phase 0.2: Session-scoped ADG fixtures."""
    
    def test_session_adg_cache_dir_created(self, session_adg_cache_dir):
        """Test that session cache directory is created properly."""
        assert session_adg_cache_dir.exists()
        assert session_adg_cache_dir.is_dir()
    
    def test_session_adg_scan_structure(self, session_adg_scan):
        """Test that session ADG scan has required structure."""
        assert isinstance(session_adg_scan, dict)
        assert "result" in session_adg_scan
        assert "scan_time" in session_adg_scan
        assert "edge_count" in session_adg_scan
        assert "node_count" in session_adg_scan
        assert "digest" in session_adg_scan
        
        # Check result object
        result = session_adg_scan["result"]
        assert hasattr(result, "edges")
        assert hasattr(result, "modules")
        assert hasattr(result, "digest")
    
    def test_session_adg_scan_performance(self, session_adg_scan):
        """Test that session ADG scan completes in reasonable time."""
        scan_time = session_adg_scan["scan_time"]
        # Should complete in under 300 seconds (5 minutes)
        assert scan_time < 300.0, f"Scan took too long: {scan_time:.2f}s"
        
        # Should have processed significant number of modules
        node_count = session_adg_scan["node_count"]
        assert node_count > 1000, f"Too few modules processed: {node_count}"
    
    def test_session_adg_scan_cached(self, session_adg_scan):
        """Test that session ADG scan is properly cached."""
        # The scan should be cached in _session_adg_cache global
        from tests.conftest_adg_phase0 import _session_adg_cache
        assert _session_adg_cache is not None
        assert _session_adg_cache["digest"] == session_adg_scan["digest"]
    
    def test_fast_adg_scan_structure(self, fast_adg_scan):
        """Test that fast ADG scan has required structure."""
        assert isinstance(fast_adg_scan, dict)
        assert "result" in fast_adg_scan
        assert "mode" in fast_adg_scan
        assert fast_adg_scan["mode"] == "structural_only"
    
    def test_mock_adg_structure(self, mock_adg):
        """Test that mock ADG provides expected interface."""
        assert isinstance(mock_adg, dict)
        assert "result" in mock_adg
        assert mock_adg["edge_count"] == 0
        assert mock_adg["node_count"] == 0
        assert mock_adg["mode"] == "mock"
        
        # Check mock result
        result = mock_adg["result"]
        assert hasattr(result, "edges")
        assert hasattr(result, "modules")
        assert hasattr(result, "digest")
        assert len(result.edges) == 0
        assert len(result.modules) == 0
    
    def test_mock_adg_performance(self, mock_adg):
        """Test that mock ADG is essentially instant."""
        scan_time = mock_adg["scan_time"]
        assert scan_time < 0.01, f"Mock ADG took too long: {scan_time:.3f}s"


class TestPerformanceLogger:
    """Test suite for ADG performance logging fixture."""
    
    def test_performance_logger_timing(self, adg_performance_logger):
        """Test that performance logger accurately measures time."""
        with adg_performance_logger.time("test_operation"):
            time.sleep(0.1)  # Sleep for 100ms
        
        assert "test_operation" in adg_performance_logger.timings
        assert len(adg_performance_logger.timings["test_operation"]) == 1
        assert adg_performance_logger.counts["test_operation"] == 1
        
        duration = adg_performance_logger.timings["test_operation"][0]
        assert 0.09 < duration < 0.15  # Allow some tolerance
    
    def test_performance_logger_multiple_operations(self, adg_performance_logger):
        """Test performance logger with multiple operations."""
        with adg_performance_logger.time("op1"):
            time.sleep(0.05)
        
        with adg_performance_logger.time("op2"):
            time.sleep(0.03)
        
        with adg_performance_logger.time("op1"):
            time.sleep(0.02)
        
        assert len(adg_performance_logger.timings["op1"]) == 2
        assert len(adg_performance_logger.timings["op2"]) == 1
        assert adg_performance_logger.counts["op1"] == 2
        assert adg_performance_logger.counts["op2"] == 1
    
    def test_performance_logger_summary(self, adg_performance_logger):
        """Test that performance logger generates proper summary."""
        # Add some test data
        adg_performance_logger.timings["test"] = [0.1, 0.2, 0.15]
        adg_performance_logger.counts["test"] = 3
        
        # This should not raise an exception
        adg_performance_logger.summary()


class TestPhase0Integration:
    """Integration tests for Phase 0 changes."""
    
    @pytest.mark.slow_adg
    def test_session_vs_mock_performance(self, session_adg_scan, mock_adg, adg_performance_logger):
        """Compare performance between session ADG and mock ADG."""
        # Time session ADG access
        with adg_performance_logger.time("session_access"):
            edges = session_adg_scan["edge_count"]
            nodes = session_adg_scan["node_count"]
        
        # Time mock ADG access
        with adg_performance_logger.time("mock_access"):
            mock_edges = mock_adg["edge_count"]
            mock_nodes = mock_adg["node_count"]
        
        # Verify data integrity
        assert edges > 0
        assert nodes > 0
        assert mock_edges == 0
        assert mock_nodes == 0
        
        # Performance summary
        adg_performance_logger.summary()
    
    @pytest.mark.fast_adg
    def test_fast_adg_vs_mock_structure(self, fast_adg_scan, mock_adg):
        """Compare structure between fast ADG and mock ADG."""
        # Both should have same interface
        for key in ["result", "scan_time", "edge_count", "node_count", "digest", "mode"]:
            assert key in fast_adg_scan
            assert key in mock_adg
        
        # But different data
        assert fast_adg_scan["mode"] != mock_adg["mode"]
        assert fast_adg_scan["edge_count"] != mock_adg["edge_count"]


# Performance benchmarks
@pytest.mark.benchmark
class TestPhase0Benchmarks:
    """Benchmark tests for Phase 0 performance improvements."""
    
    def test_mock_adg_creation_time(self, mock_adg):
        """Benchmark mock ADG creation time."""
        # Should be essentially instant
        assert mock_adg["scan_time"] < 0.001
    
    @pytest.mark.slow_adg
    def test_session_adg_reuse_time(self, session_adg_scan, adg_performance_logger):
        """Benchmark session ADG reuse time."""
        # First access (should use cached result)
        with adg_performance_logger.time("first_access"):
            edges1 = session_adg_scan["edge_count"]
        
        # Second access (should be instant)
        with adg_performance_logger.time("second_access"):
            edges2 = session_adg_scan["edge_count"]
        
        assert edges1 == edges2
        
        # Both accesses should be fast due to caching
        adg_performance_logger.summary()
