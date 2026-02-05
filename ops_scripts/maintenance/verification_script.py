"""
Verification Script - V10 Infrastructure Validation (Fixed).

Updates:
- Added Test 1.5 to verify "Hung Query" termination via CircuitBreaker execution timeout.
- Confirms the thread-safe wrapper correctly handles local scope and non-local variables.
"""

import sys
import tempfile
import time
from pathlib import Path

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def test_circuit_breaker():
    """Test Circuit Breaker state machine, backoff, and timeouts."""
    print("\n" + "=" * 60)
    print("TEST 1: Circuit Breaker")
    print("=" * 60)

    from agentic_core.L5_safety.core.circuit_breaker import (
        CircuitBreaker,
        CircuitBreakerConfig,
        CircuitBreakerOpenError,
        CircuitBreakerTimeoutError,
        CircuitState,
        reset_registry,
    )

    # 1.1 State Transitions
    print("\n1.1 Testing state transitions...")
    breaker = CircuitBreaker(
        "test_1", CircuitBreakerConfig(failure_threshold=3, reset_timeout_seconds=0.1)
    )
    assert breaker.state == CircuitState.CLOSED
    for _ in range(3):
        breaker.record_failure(Exception("Fail"))
    assert breaker.state == CircuitState.OPEN
    print("   ✓ State transitions OK")

    # 1.2 Backoff
    print("\n1.2 Testing exponential backoff...")
    breaker2 = CircuitBreaker(
        "test_2",
        CircuitBreakerConfig(
            failure_threshold=1, backoff_multiplier=2.0, reset_timeout_seconds=0.1
        ),
    )
    breaker2.record_failure()  # Open
    assert breaker2._current_reset_timeout == 0.1
    time.sleep(0.15)
    breaker2.allow_request()  # Half-open
    breaker2.record_failure()  # Fail again -> Open + Backoff
    assert breaker2._current_reset_timeout == 0.2
    print("   ✓ Backoff OK")

    # 1.3 Recovery
    print("\n1.3 Testing recovery...")
    breaker3 = CircuitBreaker(
        "test_3",
        CircuitBreakerConfig(failure_threshold=1, success_threshold=1, reset_timeout_seconds=0.1),
    )
    breaker3.record_failure()
    time.sleep(0.15)
    breaker3.allow_request()
    breaker3.record_success()
    assert breaker3.state == CircuitState.CLOSED
    print("   ✓ Recovery OK")

    # 1.4 Decorator
    print("\n1.4 Testing decorator...")
    breaker4 = CircuitBreaker(
        "test_4", CircuitBreakerConfig(failure_threshold=2, execution_timeout_seconds=1.0)
    )
    count = 0

    @breaker4.protect
    def flaky():
        nonlocal count
        count += 1
        if count < 3:
            raise ValueError("Fail")
        return "OK"

    try:
        flaky()
    except ValueError:
        pass
    try:
        flaky()
    except ValueError:
        pass

    try:
        flaky()
        raise AssertionError("Should raise OpenError")
    except CircuitBreakerOpenError:
        print("   ✓ Decorator OpenError OK")

    # 1.5 Hung Query (Execution Timeout)
    print("\n1.5 Testing Hung Query Timeout...")
    breaker5 = CircuitBreaker("test_5", CircuitBreakerConfig(execution_timeout_seconds=0.5))

    @breaker5.protect
    def hung_task():
        time.sleep(2.0)  # Longer than timeout
        return "Should not see this"

    try:
        hung_task()
        raise AssertionError("Should have timed out")
    except CircuitBreakerTimeoutError:
        print("   ✓ Hung query terminated via Timeout OK")

    # Reset circuit breaker registry to prevent deadlock
    reset_registry()

    print("\n✅ Circuit Breaker tests PASSED")
    return True


def test_adapter_base():
    """Test Adapter delegation pattern."""
    print("\n" + "=" * 60)
    print("TEST 2: Adapter Base")
    print("=" * 60)

    from agentic_core.L5_safety.adapters.adapter_base import (
        AdapterBase,
    )

    # Test 2.1: Create a mock legacy agent and adapter
    print("\n2.1 Testing adapter wrapping...")

    class MockLegacyAgent:
        """Simulated orphan agent."""

        def process(self, data: str) -> str:
            return f"processed: {data}"

        def failing_process(self) -> str:
            raise RuntimeError("Legacy agent failure")

    class MockAdapter(AdapterBase[MockLegacyAgent]):
        def _execute_legacy(self, context, *args, **kwargs):
            return self._legacy_agent.process(*args, **kwargs)

        def _validate_input(self, context, *args, **kwargs):
            # V10 input validation
            if args and args[0] == "invalid":
                return False
            return True

    legacy = MockLegacyAgent()
    adapter = MockAdapter(
        legacy, "mock_service", circuit_breaker_config={"execution_timeout_seconds": 2.0}
    )

    # Test successful execution
    result = adapter.execute(None, "test_data")
    assert result.success, f"Should succeed: {result.error}"
    assert result.data == "processed: test_data"
    print("   ✓ Adapter wraps legacy agent correctly")

    # Test 2.2: Input validation
    print("\n2.2 Testing V10 input validation...")
    result = adapter.execute(None, "invalid")
    assert not result.success, "Should fail validation"
    assert result.skipped, "Should be marked as skipped"
    assert "validation" in result.skip_reason.lower()
    print("   ✓ Input validation rejects invalid input")

    # Test 2.3: Circuit breaker integration
    print("\n2.3 Testing circuit breaker integration...")

    class FailingAdapter(AdapterBase[MockLegacyAgent]):
        def _execute_legacy(self, context, *args, **kwargs):
            return self._legacy_agent.failing_process()

    failing_adapter = FailingAdapter(
        legacy,
        "failing_service",
        circuit_breaker_config={"failure_threshold": 2, "execution_timeout_seconds": 2.0},
    )

    # Record failures
    failing_adapter.execute()
    failing_adapter.execute()

    # Circuit should be open
    result = failing_adapter.execute()
    assert not result.success
    assert "circuit" in result.skip_reason.lower() or "circuit" in result.error.lower()
    print("   ✓ Circuit breaker integrates with adapter")

    # Test 2.4: Audit trail
    print("\n2.4 Testing audit trail...")
    audit_log = adapter.get_audit_log()
    assert len(audit_log) > 0, "Should have audit entries"
    print(f"   ✓ Audit log has {len(audit_log)} entries")

    print("\n✅ Adapter Base tests PASSED")
    return True


def test_atomic_execution():
    """Test Atomic Execution and rollback."""
    print("\n" + "=" * 60)
    print("TEST 3: Atomic Execution")
    print("=" * 60)

    from agentic_core.base_agents.atomic_execution_mixin import (
        AtomicExecutionError,
        AtomicExecutionMixin,
    )

    class TestAgent(AtomicExecutionMixin):
        def __init__(self):
            self.project_root = Path(tempfile.mkdtemp())

    agent = TestAgent()

    # Test 3.1: Successful transaction
    print("\n3.1 Testing successful transaction...")
    test_file = agent.project_root / "test_file.py"
    test_file.write_text("original content")

    with agent.atomic_transaction("test_write") as txn:
        agent.atomic_write(txn, test_file, "new content")

    assert test_file.read_text() == "new content"
    print("   ✓ Transaction commits successfully")

    # Test 3.2: Rollback on failure
    print("\n3.2 Testing rollback on failure...")
    test_file2 = agent.project_root / "test_file2.py"
    test_file2.write_text("original")

    try:
        with agent.atomic_transaction("failing_op") as txn:
            agent.atomic_write(txn, test_file2, "modified")
            raise ValueError("Simulated failure")
    except AtomicExecutionError as e:
        assert e.rolled_back, "Should be rolled back"

    assert test_file2.read_text() == "original", "Should be rolled back to original"
    print("   ✓ Rollback restores original content")

    # Test 3.3: Multiple file transaction
    print("\n3.3 Testing multi-file transaction...")
    file_a = agent.project_root / "file_a.py"
    file_b = agent.project_root / "file_b.py"
    file_a.write_text("a_original")
    file_b.write_text("b_original")

    try:
        with agent.atomic_transaction("multi_file") as txn:
            agent.atomic_write(txn, file_a, "a_modified")
            agent.atomic_write(txn, file_b, "b_modified")
            raise RuntimeError("Failure after both writes")
    except AtomicExecutionError:
        pass

    assert file_a.read_text() == "a_original", "File A should be rolled back"
    assert file_b.read_text() == "b_original", "File B should be rolled back"
    print("   ✓ Multi-file rollback works correctly")

    # Cleanup
    import shutil

    shutil.rmtree(agent.project_root, ignore_errors=True)

    print("\n✅ Atomic Execution tests PASSED")
    return True


def test_context_session():
    """Test Context Session and Working Memory."""
    print("\n" + "=" * 60)
    print("TEST 4: Context Session")
    print("=" * 60)

    from agentic_core.L5_safety.core.context_session import (
        RiskLevel,
        classify_risk,
        get_session_manager,
    )

    # Test 4.1: Risk classification
    print("\n4.1 Testing risk classification...")
    assert classify_risk(file_count=1) == RiskLevel.LOW
    assert classify_risk(file_count=5) == RiskLevel.MEDIUM
    assert classify_risk(file_count=15) == RiskLevel.HIGH
    assert classify_risk(is_base_agent=True) == RiskLevel.HIGH
    assert classify_risk(has_external_touch=True) == RiskLevel.HIGH
    print("   ✓ Risk classification works correctly")

    # Test 4.2: Session management
    print("\n4.2 Testing session management...")
    manager = get_session_manager()
    session = manager.create_session(RiskLevel.MEDIUM)

    assert session.risk_level == RiskLevel.MEDIUM
    session.set("test_key", "test_value")
    assert session.get("test_key") == "test_value"
    print("   ✓ Session state management works")

    # Test 4.3: Risk escalation
    print("\n4.3 Testing risk escalation...")
    session.escalate_risk(RiskLevel.HIGH)
    assert session.risk_level == RiskLevel.HIGH

    # Should not de-escalate
    session.escalate_risk(RiskLevel.LOW)
    assert session.risk_level == RiskLevel.HIGH, "Risk should not decrease"
    print("   ✓ Risk escalation (never decrease) works")

    # Test 4.4: Session scope
    print("\n4.4 Testing session scope...")
    with manager.session_scope(RiskLevel.LOW) as scoped_session:
        assert manager.current_session == scoped_session
        scoped_session.add_focus_file("/test/file.py")

    assert manager.current_session is None or manager.current_session != scoped_session
    print("   ✓ Session scope lifecycle works")

    print("\n✅ Context Session tests PASSED")
    return True


def test_contextual_router():
    """Test Contextual Router and Guardian integration."""
    print("\n" + "=" * 60)
    print("TEST 5: Contextual Router")
    print("=" * 60)

    from agentic_core.L3_orchestration.contextual_router import (
        ContextualRouter,
        RouteDecision,
        RoutingRequest,
        get_guardian_signal_bus,
    )

    # Test 5.1: Low risk bypass
    print("\n5.1 Testing low risk bypass (V10 blue arrow)...")
    router = ContextualRouter()

    low_risk_request = RoutingRequest(
        request_id="test_1",
        action_type="heal",
        target_files=[Path("/test/simple.py")],
        cyclomatic_complexity=5,
        has_external_touch=False,
        is_base_agent=False,
    )

    result = router.route(low_risk_request)
    assert result.decision == RouteDecision.BYPASS, f"Should bypass, got {result.decision}"
    assert result.bypass_validation, "Should have bypass flag"
    print("   ✓ Low risk requests bypass validation")

    # Test 5.2: High risk routing
    print("\n5.2 Testing high risk routing...")
    high_risk_request = RoutingRequest(
        request_id="test_2",
        action_type="heal",
        target_files=[Path("/agentic_core/base_agents/SovereignBaseAgent.py")],
        is_base_agent=True,
    )

    result = router.route(high_risk_request)
    assert result.decision == RouteDecision.HUMAN_REVIEW
    assert result.requires_human_approval
    print("   ✓ Base agent modifications require human review")

    # Test 5.3: Guardian signal integration
    print("\n5.3 Testing guardian signal integration...")
    signal_bus = get_guardian_signal_bus()
    signal_bus.clear_signals()

    # Emit a critical signal
    signal_bus.emit_signal(
        "mro_violation",
        {"agent_name": "TestAgent", "file": "/test/agent.py"},
        severity="critical",
    )

    active_signals = signal_bus.get_active_signals()
    assert len(active_signals) > 0, "Should have active signals"
    print(f"   ✓ Guardian signal emitted ({len(active_signals)} active)")

    # Test 5.4: Router metrics
    print("\n5.4 Testing router metrics...")
    metrics = router.get_metrics()
    assert "total_requests" in metrics
    assert metrics["total_requests"] >= 2
    print(f"   ✓ Router metrics: {metrics['total_requests']} total requests")

    print("\n✅ Contextual Router tests PASSED")
    return True


def main():
    """Run all verification tests."""
    print("\n" + "=" * 60)
    print("V10 INFRASTRUCTURE VERIFICATION")
    print("=" * 60)
    print("Testing Wave 1 components for Agentic Process V10 compliance")

    results = []

    try:
        results.append(("Circuit Breaker", test_circuit_breaker()))
    except Exception as e:
        print(f"\n❌ Circuit Breaker tests FAILED: {e}")
        import traceback

        traceback.print_exc()
        results.append(("Circuit Breaker", False))

    try:
        results.append(("Adapter Base", test_adapter_base()))
    except Exception as e:
        print(f"\n❌ Adapter Base tests FAILED: {e}")
        results.append(("Adapter Base", False))

    try:
        results.append(("Atomic Execution", test_atomic_execution()))
    except Exception as e:
        print(f"\n❌ Atomic Execution tests FAILED: {e}")
        results.append(("Atomic Execution", False))

    try:
        results.append(("Context Session", test_context_session()))
    except Exception as e:
        print(f"\n❌ Context Session tests FAILED: {e}")
        results.append(("Context Session", False))

    try:
        results.append(("Contextual Router", test_contextual_router()))
    except Exception as e:
        print(f"\n❌ Contextual Router tests FAILED: {e}")
        results.append(("Contextual Router", False))

    # Summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status}: {name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All V10 infrastructure tests PASSED!")
        print("Wave 1 components are ready for integration.")
        return 0
    else:
        print("\n⚠️  Some tests FAILED. Review and fix before proceeding.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
