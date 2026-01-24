"""
Phase 1 Core Infrastructure Test Runner.

Runs the core infrastructure tests directly, bypassing pytest configuration issues.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import time


def run_tests():
    """Run all Phase 1 core infrastructure tests."""
    print("=" * 70)
    print("PHASE 1 CORE INFRASTRUCTURE TESTS")
    print("=" * 70)
    
    from apps_rg.shared.core.immutable_buffer import ImmutableStagingBuffer
    from apps_rg.shared.core.trace_registry import TraceRegistry
    
    passed = 0
    failed = 0
    
    # Test 1: Buffer Ghost Mutation Prevention
    print("\n[TEST 1] test_buffer_ghost_mutation_prevention")
    try:
        buffer = ImmutableStagingBuffer()
        secret_config = {"access_level": "admin", "nested": {"param": 1}}
        buffer.write("config", secret_config, source_agent="Setup")
        leaked_ref = buffer.read("config")
        leaked_ref["access_level"] = "hacker"
        leaked_ref["nested"]["param"] = 999
        safe_data = buffer.read("config")
        assert safe_data["access_level"] == "admin", f"Expected 'admin', got '{safe_data['access_level']}'"
        assert safe_data["nested"]["param"] == 1, f"Expected 1, got {safe_data['nested']['param']}"
        print("  ✅ PASSED")
        passed += 1
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        failed += 1
    
    # Test 2: Buffer Write Once Locking
    print("\n[TEST 2] test_buffer_write_once_locking")
    try:
        buffer = ImmutableStagingBuffer()
        buffer.write("key", "value1", "AgentA")
        try:
            buffer.write("key", "value2", "AgentB")
            print("  ❌ FAILED: Expected PermissionError")
            failed += 1
        except PermissionError:
            print("  ✅ PASSED")
            passed += 1
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        failed += 1
    
    # Test 3: Buffer Transaction History
    print("\n[TEST 3] test_buffer_transaction_history")
    try:
        buffer = ImmutableStagingBuffer()
        buffer.set_cycle("CYCLE_001")
        buffer.write("data1", {"value": 1}, source_agent="Agent1")
        buffer.write("data2", {"value": 2}, source_agent="Agent2")
        history = buffer.get_history()
        assert len(history) == 2, f"Expected 2 transactions, got {len(history)}"
        assert history[0].key == "data1"
        assert history[0].source_agent == "Agent1"
        assert history[0].cycle_id == "CYCLE_001"
        assert history[1].key == "data2"
        assert history[1].source_agent == "Agent2"
        print("  ✅ PASSED")
        passed += 1
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        failed += 1
    
    # Test 4: Buffer Read Default
    print("\n[TEST 4] test_buffer_read_default")
    try:
        buffer = ImmutableStagingBuffer()
        result = buffer.read("nonexistent", default="fallback")
        assert result == "fallback", f"Expected 'fallback', got '{result}'"
        print("  ✅ PASSED")
        passed += 1
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        failed += 1
    
    # Test 5: Buffer Snapshot Isolation
    print("\n[TEST 5] test_buffer_snapshot_isolation")
    try:
        buffer = ImmutableStagingBuffer()
        buffer.write("key", {"nested": {"value": 1}}, "Test")
        snapshot = buffer.get_snapshot()
        snapshot["key"]["nested"]["value"] = 999
        assert buffer.read("key")["nested"]["value"] == 1
        print("  ✅ PASSED")
        passed += 1
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        failed += 1
    
    # Test 6: Trace Span Lifecycle
    print("\n[TEST 6] test_trace_span_lifecycle")
    try:
        registry = TraceRegistry()
        span = registry.start_span("trace_123", "Orchestrator", "Plan")
        time.sleep(0.01)
        registry.end_span(span, status="SUCCESS")
        summary = registry.get_summary()
        assert summary["total_spans"] == 1, f"Expected 1 span, got {summary['total_spans']}"
        assert summary["avg_latency_ms"] > 0, f"Expected latency > 0, got {summary['avg_latency_ms']}"
        print("  ✅ PASSED")
        passed += 1
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        failed += 1
    
    # Test 7: Trace Span Failure Tracking
    print("\n[TEST 7] test_trace_span_failure_tracking")
    try:
        registry = TraceRegistry()
        span = registry.start_span("trace_456", "Validator", "Validate")
        registry.end_span(span, status="FAILURE", error="Validation failed")
        summary = registry.get_summary()
        assert summary["failures"] == 1
        assert summary["completed"] == 1
        print("  ✅ PASSED")
        passed += 1
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        failed += 1
    
    # Test 8: Trace Token Tracking
    print("\n[TEST 8] test_trace_token_tracking")
    try:
        registry = TraceRegistry()
        span = registry.start_span("trace_789", "Generator", "Generate")
        registry.end_span(span, status="SUCCESS", tokens=1500)
        summary = registry.get_summary()
        assert summary["total_tokens"] == 1500
        print("  ✅ PASSED")
        passed += 1
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        failed += 1
    
    # Test 9: Trace Legacy API
    print("\n[TEST 9] test_trace_legacy_api")
    try:
        registry = TraceRegistry()
        registry.add_trace("PHASE_START", {"agent": "TestAgent"})
        traces = registry.get_traces()
        assert len(traces) == 1
        assert traces[0]["action"] == "PHASE_START"
        print("  ✅ PASSED")
        passed += 1
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        failed += 1
    
    # Test 10: Trace Count By Type
    print("\n[TEST 10] test_trace_count_by_type")
    try:
        registry = TraceRegistry()
        registry.add_trace("PHASE_START", {"agent": "Agent1"})
        registry.add_trace("PHASE_START", {"agent": "Agent2"})
        registry.add_trace("PHASE_END", {"agent": "Agent1"})
        assert registry.count("PHASE_START") == 2
        assert registry.count("PHASE_END") == 1
        print("  ✅ PASSED")
        passed += 1
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        failed += 1
    
    # Test 11: Trace Get Latest
    print("\n[TEST 11] test_trace_get_latest")
    try:
        registry = TraceRegistry()
        registry.add_trace("ACTION", {"agent": "First"})
        time.sleep(0.001)
        registry.add_trace("ACTION", {"agent": "Second"})
        latest = registry.get_latest("ACTION")
        assert latest is not None
        print("  ✅ PASSED")
        passed += 1
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        failed += 1
    
    # Test 12: Buffer Write Once Legacy API
    print("\n[TEST 12] test_buffer_write_once_legacy_api")
    try:
        buffer = ImmutableStagingBuffer()
        buffer.write_once("legacy_key", "legacy_value")
        assert buffer.read("legacy_key") == "legacy_value"
        assert buffer.is_locked("legacy_key")
        print("  ✅ PASSED")
        passed += 1
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        failed += 1
    
    # Summary
    print("\n" + "=" * 70)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 70)
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED - Phase 1 Core Infrastructure is HARDENED")
        return 0
    else:
        print(f"\n❌ {failed} TESTS FAILED - Fix before proceeding to Phase 2")
        return 1


if __name__ == "__main__":
    sys.exit(run_tests())
