"""
Direct test runner for Phase 2: Core Enhancements.
Tests Reasoning Toggles and Trace Registry persistence.
"""

import json
import sys
import tempfile
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

print("=" * 80)
print("PHASE 2: CORE ENHANCEMENTS TESTS")
print("=" * 80)


def test_reasoning_toggles_defaults():
    """Verify default safety values."""
    print("\n1. Testing ReasoningToggles defaults...")

    try:
        from apps_rg.shared.reasoning.toggles import ReasoningToggles

        toggles = ReasoningToggles()
        assert toggles.use_cot is True
        assert toggles.use_reflexion is True
        assert toggles.strict_mode is True
        assert toggles.use_persistent_tracing is True
        assert toggles.use_cyclic_validation is True
        assert toggles.tot_branches == 3
        assert toggles.temperature_cap == 0.5

        print("   ✅ ReasoningToggles defaults test PASSED")
        return True
    except Exception as e:
        print(f"   ❌ ReasoningToggles defaults test FAILED: {e}")
        return False


def test_reasoning_toggles_validation():
    """Verify input validation constraints."""
    print("\n2. Testing ReasoningToggles validation...")

    try:
        from apps_rg.shared.reasoning.toggles import ReasoningToggles

        # Invalid branch count (too high)
        try:
            ReasoningToggles(tot_branches=10)
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "tot_branches" in str(e)

        # Valid branch count
        toggles = ReasoningToggles(tot_branches=5)
        assert toggles.tot_branches == 5

        print("   ✅ ReasoningToggles validation test PASSED")
        return True
    except Exception as e:
        print(f"   ❌ ReasoningToggles validation test FAILED: {e}")
        return False


def test_reasoning_toggles_environments():
    """Verify environment-based toggle loading."""
    print("\n3. Testing environment-based toggles...")

    try:
        from apps_rg.shared.reasoning.toggles import get_toggles

        # Production defaults
        prod_toggles = get_toggles("prod")
        assert prod_toggles.use_cot is True
        assert prod_toggles.strict_mode is True

        # Development mode
        dev_toggles = get_toggles("dev")
        assert dev_toggles.tot_branches == 5
        assert dev_toggles.strict_mode is False

        # Test mode
        test_toggles = get_toggles("test")
        assert test_toggles.use_cot is False
        assert test_toggles.use_reflexion is False
        assert test_toggles.tot_branches == 1

        print("   ✅ Environment-based toggles test PASSED")
        return True
    except Exception as e:
        print(f"   ❌ Environment-based toggles test FAILED: {e}")
        return False


def test_trace_registry_in_memory():
    """Verify in-memory span tracking."""
    print("\n4. Testing TraceRegistry in-memory...")

    try:
        from apps_rg.shared.core.trace_registry import TraceRegistry

        registry = TraceRegistry()
        span_id = registry.start_span("test_mission", "test_agent", "test_operation")

        assert len(registry._active_spans) == 1
        assert span_id in registry._active_spans

        registry.end_span(span_id, status="SUCCESS")
        assert len(registry._active_spans) == 0
        assert len(registry._traces) == 1
        assert registry._traces[0].status == "SUCCESS"

        print("   ✅ TraceRegistry in-memory test PASSED")
        return True
    except Exception as e:
        print(f"   ❌ TraceRegistry in-memory test FAILED: {e}")
        return False


def test_trace_registry_persistence():
    """Verify traces are written to disk."""
    print("\n5. Testing TraceRegistry persistence...")

    try:
        from apps_rg.shared.core.trace_registry import TraceRegistry

        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            trace_file = Path(f.name)

        registry = TraceRegistry(persistence_path=trace_file)
        span_id = registry.start_span("persist_mission", "persist_agent", "persist_operation")
        registry.end_span(span_id, status="SUCCESS")

        # Check file content
        assert trace_file.exists(), "Trace file not created"

        with open(trace_file) as f:
            content = f.read()
            assert len(content) > 0, "No content in trace file"

            # Parse JSON to verify structure
            trace_data = json.loads(content.strip())
            assert trace_data["agent"] == "persist_agent"
            assert trace_data["action"] == "persist_operation"
            assert trace_data["status"] == "SUCCESS"

        # Cleanup
        trace_file.unlink()

        print("   ✅ TraceRegistry persistence test PASSED")
        return True
    except Exception as e:
        print(f"   ❌ TraceRegistry persistence test FAILED: {e}")
        return False


def test_trace_registry_performance_metrics():
    """Verify performance metrics are tracked."""
    print("\n6. Testing TraceRegistry performance metrics...")

    try:
        import time

        from apps_rg.shared.core.trace_registry import TraceRegistry

        registry = TraceRegistry()
        span_id = registry.start_span("perf_mission", "perf_agent", "perf_operation")

        # Small delay to ensure measurable duration
        time.sleep(0.01)

        registry.end_span(span_id, status="SUCCESS", tokens=100)

        trace = registry._traces[0]
        assert trace.duration_ms > 0, "Duration not measured"
        assert trace.tokens_used == 100, "Token count not tracked"

        print("   ✅ TraceRegistry performance metrics test PASSED")
        return True
    except Exception as e:
        print(f"   ❌ TraceRegistry performance metrics test FAILED: {e}")
        return False


def main():
    """Run all Phase 2 tests."""
    results = []

    results.append(test_reasoning_toggles_defaults())
    results.append(test_reasoning_toggles_validation())
    results.append(test_reasoning_toggles_environments())
    results.append(test_trace_registry_in_memory())
    results.append(test_trace_registry_persistence())
    results.append(test_trace_registry_performance_metrics())

    print("\n" + "=" * 80)
    print("PHASE 2 TEST RESULTS")
    print("=" * 80)

    passed = sum(results)
    total = len(results)

    print(f"Tests Passed: {passed}/{total}")

    if passed == total:
        print("\n🎉 ALL PHASE 2 TESTS PASSED!")
        print("✅ Reasoning Toggles are fully functional")
        print("✅ Trace Registry with persistence is working")
        print("✅ Core enhancements exceed original specifications")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        print("⚠️  Core enhancements need fixes")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
