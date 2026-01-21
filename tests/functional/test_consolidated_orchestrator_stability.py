#!/usr/bin/env python3
"""
Test Suite: CoreOrchestrationAgent Stability Gate & Metrics

Tests the 5 detailed test cases for:
1. Stability Gate: Execution Failure
2. Stability Gate: Dry-Run Safety
3. SSOT Key Extraction
4. Observability Duration
5. Critical Error Transparency
"""

import sys
import time
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L3_orchestration.unified.CoreOrchestrationAgent import CoreOrchestrationAgent


class MockAgent:
    """Mock agent for testing orchestrator behavior."""

    def __init__(self, return_value=None, raise_error=None, delay=0):
        self.return_value = return_value
        self.raise_error = raise_error
        self.delay = delay

    def heal_repository(self, dry_run=True, execute=False, **kwargs):
        # CANON: INTENTIONAL_CHAIN_BREAK - Test mock does not chain to super()
        if self.delay > 0:
            time.sleep(self.delay)
        if self.raise_error:
            raise self.raise_error
        return self.return_value


def test_1_stability_gate_execution_failure():
    """
    Test Case 1: Stability Gate - Execution Failure

    Provide an agent that returns violations: 5 and fixed: 0 with execute=True.
    Verify is_stable returns False.
    """
    print("\n" + "=" * 60)
    print("TEST 1: Stability Gate - Execution Failure")
    print("=" * 60)

    orchestrator = CoreOrchestrationAgent(PROJECT_ROOT)

    # Agent returns violations with execute=True
    mock_agent = MockAgent(return_value={"violations": 5, "fixed": 0})
    agents = [("ViolatingAgent", mock_agent)]
    context = {"execute": True, "dry_run": False}

    result = orchestrator.run_mission(agents, context)

    assert result["is_stable"] == False, f"Expected is_stable=False, got {result['is_stable']}"
    assert result["total_violations"] == 5, (
        f"Expected total_violations=5, got {result['total_violations']}"
    )

    print(f"✅ PASSED: is_stable={result['is_stable']} (expected False)")
    print(f"   total_violations={result['total_violations']}")
    return True


def test_2_stability_gate_dry_run_safety():
    """
    Test Case 2: Stability Gate - Dry-Run Safety

    Provide an agent that returns violations: 10 with execute=False (dry-run).
    Verify is_stable returns True (dry-runs are inherently "stable").
    """
    print("\n" + "=" * 60)
    print("TEST 2: Stability Gate - Dry-Run Safety")
    print("=" * 60)

    orchestrator = CoreOrchestrationAgent(PROJECT_ROOT)

    # Agent returns violations but in dry-run mode
    mock_agent = MockAgent(return_value={"violations": 10, "fixed": 0})
    agents = [("DryRunAgent", mock_agent)]
    context = {"execute": False, "dry_run": True}

    result = orchestrator.run_mission(agents, context)

    assert result["is_stable"] == True, f"Expected is_stable=True, got {result['is_stable']}"
    assert result["total_violations"] == 10, (
        f"Expected total_violations=10, got {result['total_violations']}"
    )

    print(f"✅ PASSED: is_stable={result['is_stable']} (expected True for dry-run)")
    print(
        f"   total_violations={result['total_violations']} (violations don't affect stability in dry-run)"
    )
    return True


def test_3_ssot_key_extraction():
    """
    Test Case 3: SSOT Key Extraction

    Execute an agent that uses legacy keys (e.g., violations_found: 3).
    Verify the orchestrator correctly maps this to total_violations: 3.
    """
    print("\n" + "=" * 60)
    print("TEST 3: SSOT Key Extraction")
    print("=" * 60)

    orchestrator = CoreOrchestrationAgent(PROJECT_ROOT)

    # Test various legacy key formats
    test_cases = [
        ("LegacyAgent1", {"violations_found": 3, "violations_fixed": 2}),
        ("LegacyAgent2", {"errors": 5, "renamed": 1}),
        ("StandardAgent", {"violations": 7, "fixed": 4}),
    ]

    agents = [(name, MockAgent(return_value=result)) for name, result in test_cases]
    context = {"execute": False, "dry_run": True}

    result = orchestrator.run_mission(agents, context)

    # Expected: 3 + 5 + 7 = 15 violations, 2 + 1 + 4 = 7 fixes
    expected_violations = 3 + 5 + 7
    expected_fixes = 2 + 1 + 4

    assert result["total_violations"] == expected_violations, (
        f"Expected total_violations={expected_violations}, got {result['total_violations']}"
    )
    assert result["total_fixes"] == expected_fixes, (
        f"Expected total_fixes={expected_fixes}, got {result['total_fixes']}"
    )

    # Verify individual mission_log entries
    log = result["mission_log"]
    assert log[0]["violations"] == 3, "LegacyAgent1 violations_found not mapped correctly"
    assert log[0]["fixed"] == 2, "LegacyAgent1 violations_fixed not mapped correctly"
    assert log[1]["violations"] == 5, "LegacyAgent2 errors not mapped correctly"
    assert log[1]["fixed"] == 1, "LegacyAgent2 renamed not mapped correctly"

    print("✅ PASSED: SSOT key extraction working")
    print(f"   total_violations={result['total_violations']} (expected {expected_violations})")
    print(f"   total_fixes={result['total_fixes']} (expected {expected_fixes})")
    print("   Legacy keys (violations_found, errors, violations_fixed, renamed) correctly mapped")
    return True


def test_4_observability_duration():
    """
    Test Case 4: Observability Duration

    Verify that both individual mission_log entries and the final summary
    report accurate execution times in seconds.
    """
    print("\n" + "=" * 60)
    print("TEST 4: Observability Duration")
    print("=" * 60)

    orchestrator = CoreOrchestrationAgent(PROJECT_ROOT)

    # Create agents with known delays
    delay_1 = 0.1  # 100ms
    delay_2 = 0.2  # 200ms

    agents = [
        ("FastAgent", MockAgent(return_value={"violations": 0, "fixed": 0}, delay=delay_1)),
        ("SlowAgent", MockAgent(return_value={"violations": 0, "fixed": 0}, delay=delay_2)),
    ]
    context = {"execute": False, "dry_run": True}

    result = orchestrator.run_mission(agents, context)

    # Verify mission duration exists and is reasonable
    assert "duration_sec" in result, "Missing duration_sec in result"
    assert result["duration_sec"] >= (delay_1 + delay_2), (
        f"Mission duration {result['duration_sec']} should be >= {delay_1 + delay_2}"
    )

    # Verify individual agent durations
    log = result["mission_log"]
    assert "duration_sec" in log[0], "Missing duration_sec in FastAgent log"
    assert "duration_sec" in log[1], "Missing duration_sec in SlowAgent log"

    # Allow 50ms tolerance for timing variance
    tolerance = 0.05
    assert log[0]["duration_sec"] >= delay_1 - tolerance, (
        f"FastAgent duration {log[0]['duration_sec']} should be >= {delay_1}"
    )
    assert log[1]["duration_sec"] >= delay_2 - tolerance, (
        f"SlowAgent duration {log[1]['duration_sec']} should be >= {delay_2}"
    )

    print("✅ PASSED: Duration tracking working")
    print(f"   Mission duration_sec={result['duration_sec']}")
    print(f"   FastAgent duration_sec={log[0]['duration_sec']} (expected ~{delay_1})")
    print(f"   SlowAgent duration_sec={log[1]['duration_sec']} (expected ~{delay_2})")
    return True


def test_5_critical_error_transparency():
    """
    Test Case 5: Critical Error Transparency

    Force an agent to raise a RuntimeError. Verify the mission_log records
    status: "failed" and includes the error string, while the mission
    continues to the next agent.
    """
    print("\n" + "=" * 60)
    print("TEST 5: Critical Error Transparency")
    print("=" * 60)

    orchestrator = CoreOrchestrationAgent(PROJECT_ROOT)

    error_message = "Simulated critical failure for testing"

    agents = [
        ("HealthyAgent1", MockAgent(return_value={"violations": 0, "fixed": 1})),
        ("FailingAgent", MockAgent(raise_error=RuntimeError(error_message))),
        ("HealthyAgent2", MockAgent(return_value={"violations": 0, "fixed": 2})),
    ]
    context = {"execute": False, "dry_run": True}

    result = orchestrator.run_mission(agents, context)

    log = result["mission_log"]

    # Verify all 3 agents were processed (mission continued after failure)
    assert len(log) == 3, f"Expected 3 log entries, got {len(log)}"

    # Verify first agent succeeded
    assert log[0]["status"] == "success", "HealthyAgent1 should have status=success"
    assert log[0]["fixed"] == 1, "HealthyAgent1 should have fixed=1"

    # Verify failing agent recorded correctly
    assert log[1]["status"] == "failed", "FailingAgent should have status=failed"
    assert "error" in log[1], "FailingAgent should have error field"
    assert error_message in log[1]["error"], "Error message not recorded correctly"
    assert "duration_sec" in log[1], "FailingAgent should have duration_sec even on failure"

    # Verify third agent still executed (mission continued)
    assert log[2]["status"] == "success", "HealthyAgent2 should have status=success"
    assert log[2]["fixed"] == 2, "HealthyAgent2 should have fixed=2"

    # Verify total_fixes only counts successful agents
    assert result["total_fixes"] == 3, f"Expected total_fixes=3 (1+2), got {result['total_fixes']}"

    print("✅ PASSED: Critical error transparency working")
    print(f"   FailingAgent status={log[1]['status']}")
    print(f"   Error recorded: '{log[1]['error'][:50]}...'")
    print(f"   Mission continued: HealthyAgent2 executed with fixed={log[2]['fixed']}")
    print(f"   total_fixes={result['total_fixes']} (only from successful agents)")
    return True


def run_all_tests():
    """Run all test cases."""
    print("\n" + "#" * 60)
    print("# CoreOrchestrationAgent Test Suite")
    print("# Testing: Stability Gate & Standardized Metrics")
    print("#" * 60)

    tests = [
        ("Test 1: Stability Gate - Execution Failure", test_1_stability_gate_execution_failure),
        ("Test 2: Stability Gate - Dry-Run Safety", test_2_stability_gate_dry_run_safety),
        ("Test 3: SSOT Key Extraction", test_3_ssot_key_extraction),
        ("Test 4: Observability Duration", test_4_observability_duration),
        ("Test 5: Critical Error Transparency", test_5_critical_error_transparency),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except AssertionError as e:
            print(f"❌ FAILED: {name}")
            print(f"   Error: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ ERROR: {name}")
            print(f"   Exception: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"RESULTS: {passed}/{len(tests)} tests passed")
    print("=" * 60)

    if failed > 0:
        print(f"❌ {failed} test(s) FAILED")
        return 1
    else:
        print("✅ ALL TESTS PASSED")
        return 0


if __name__ == "__main__":
    sys.exit(run_all_tests())
