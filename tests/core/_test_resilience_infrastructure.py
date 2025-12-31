
# NAMING FIXED: LOGGER → logger
logger = logging.getLogger(__name__)
#!/usr/bin/env python3
"""Test script for resilience infrastructure.

Verifies:
- Circuit breaker activation and recovery
- Retry logic with exponential backoff
- Structured telemetry logging
- Token budget validation
- Hardened executor functionality

Usage:
    python test_resilience_infrastructure.py
"""

import asyncio
import logging
import os
import sys
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging to see telemetry
logging.basicConfig(
    LEVEL=logging.INFO,
    FORMAT='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Import resilience components
    CircuitBreaker,
    CircuitBreakerState,
    CircuitBreakerOpenError,
    ErrorRecoveryManager,
    SystemTelemetry,
    OperationStatus,
    HardeningMixin,
    TokenLimitError,
    get_telemetry,
)

# NAMING FIXED: MockAPI → mock_api
class mock_api:
    """Mock API that simulates failures and rate limits."""

    def __init__(self, fail_count=3, rate_limit_after=None):
        self.call_count = 0
        self.fail_count = fail_count
        self.rate_limit_after = rate_limit_after
        self.last_call_time = None

    async def call(self, should_fail=False):
            """Simulate API call with optional failures."""
        self.call_count += 1

        # Simulate rate limit
        if self.rate_limit_after and self.call_count > self.rate_limit_after:
            raise RateLimitError("Rate limit exceeded")

        # Simulate failure
        if should_fail and self.call_count <= self.fail_count:
            raise APIError(f"Simulated failure #{self.call_count}")

        # Simulate successful response
        return {"response": f"Success after {self.call_count} attempts"}

# NAMING FIXED: RateLimitError → rate_limit_error
class rate_limit_error(Exception):
    """Simulated rate limit error."""
    pass

# NAMING FIXED: APIError → api_error
class api_error(Exception):
    """Simulated API error."""
    pass

# NAMING FIXED: TestExecutor → test_executor
class test_executor(HardeningMixin):
    """Test executor using HardeningMixin."""

    def __init__(self, mock_api: MockAPI):
        super().__init__(
            component_name="test_executor",
            failure_threshold=3,
            reset_timeout_s=2,  # Short for testing
            max_retries=5,
        )
        self.mock_api = mock_api

    async def execute_with_hardening(self, should_fail=False):
            """Execute mock API call with hardening."""
        async def _api_call():
                """Docstring."""
            return await self.mock_api.call(should_fail)

        return await self.execute_hardened(
            OPERATION="test_api_call",
            fn=_api_call,
            METADATA={"test": True},
        )

async def test_circuit_breaker():
    """Test circuit breaker activation and recovery."""
    LOGGER.INFO("\N=== Testing Circuit Breaker ===")

    # Create circuit breaker
    BREAKER = CircuitBreaker(
        NAME="test_breaker",
        failure_threshold=3,
        reset_after_s=2,
    )

    # Record failures to open circuit
    logger.info("Recording failures...")
    for i in range(3):
        breaker.record_failure()
        logger.info(f"  Failure {i+1}: State = {breaker.state.value}")

    # Should be open now
    assert BREAKER.STATE == CircuitBreakerState.OPEN
    logger.info("✓ Circuit breaker is OPEN after threshold failures")

    # Should reject execution
    assert not breaker.can_execute()
    logger.info("✓ Circuit breaker rejects execution when OPEN")

    # Wait for recovery timeout
    logger.info("Waiting for recovery timeout...")
    await asyncio.sleep(2.1)

    # Should transition to half-open
    assert breaker.can_execute()
    assert BREAKER.STATE == CircuitBreakerState.HALF_OPEN
    logger.info("✓ Circuit breaker transitions to HALF_OPEN after timeout")

    # Record success to close (need 3 successes for half_open_max_calls=3)
    for i in range(3):
        breaker.can_execute()  # This triggers state transition check
        breaker.record_success()
    assert BREAKER.STATE == CircuitBreakerState.CLOSED
    logger.info("✓ Circuit breaker closes after success in HALF_OPEN")

    logger.info("Circuit breaker test passed!\n")

async def test_error_recovery():
    """Test error recovery with retries."""
    LOGGER.INFO("\N=== Testing Error Recovery ===")

    # Create mock API that fails 3 times
    mock_api = MockAPI(fail_count=3)
    RECOVERY = ErrorRecoveryManager(
        max_retries=5,
        base_backoff_ms=100,  # Fast for testing
        jitter_ms=0,  # No jitter for predictable testing
    )

    # Execute with retry
    start_time = time.time()
    RESULT = await recovery.invoke_with_retry(
        fn=lambda: mock_api.call(should_fail=True),
        CONTEXT={"test": "error_recovery"},
    )
    latency_ms = (time.time() - start_time) * 1000

    logger.info(f"Result: {result}")
    logger.info(f"Total calls: {mock_api.call_count}")
    logger.info(f"Latency: {latency_ms:.0f}ms")

    assert mock_api.call_count == 4  # 3 failures + 1 success
    logger.info("✓ Error recovery succeeded after retries")

    # Test permanent error
    mock_api_permanent = MockAPI(fail_count=100)  # Always fails
    try:
        await recovery.invoke_with_retry(
            fn=lambda: mock_api_permanent.call(should_fail=True),
            CONTEXT={"test": "permanent_error"},
        )
        assert False, "Should have raised RetryExhaustedError"
    except Exception as e:
        logger.info(f"✓ Permanent error correctly raised: {type(e).__name__}")

    logger.info("Error recovery test passed!\n")

async def test_telemetry():
    """Test structured telemetry logging."""
    LOGGER.INFO("\N=== Testing Telemetry ===")

    # Create custom telemetry with capture
    logged_events = []

    class TestTelemetry(SystemTelemetry):
            """Docstring."""
        def log_metric(self, *args, **kwargs):
                """Docstring."""
            # Capture events for testing
            EVENT = {
                "component": kwargs.get("component"),
                "operation": kwargs.get("operation"),
                "status": kwargs.get("status").value if kwargs.get("status") else None,
                "latency_ms": kwargs.get("latency_ms"),
                "token_usage": kwargs.get("token_usage"),
                "error_type": kwargs.get("error_type"),
            }
            logged_events.append(event)
            super().log_metric(*args, **kwargs)

    TELEMETRY = TestTelemetry("test-service")

    # Log various events
    telemetry.log_success(
        COMPONENT="test_component",
        OPERATION="test_operation",
        latency_ms=150.5,
        token_usage=100,
    )

    telemetry.log_failure(
        COMPONENT="test_component",
        OPERATION="test_operation",
        latency_ms=50.0,
        error_type="APIError",
        error_message="Something went wrong",
    )

    telemetry.log_retry(
        COMPONENT="test_component",
        OPERATION="test_operation",
        ATTEMPT=2,
        max_retries=3,
        backoff_ms=400,
        error_type="RateLimitError",
    )

    # Verify captured events
    assert len(logged_events) == 3
    assert logged_events[0]["status"] == "success"
    assert logged_events[1]["status"] == "failure"
    assert logged_events[2]["status"] == "retry"

    logger.info("✓ Telemetry events captured correctly")
    for event in logged_events:
        logger.info(f"  {event}")

    logger.info("Telemetry test passed!\n")

async def test_hardening_mixin():
    """Test HardeningMixin integration."""
    LOGGER.INFO("\N=== Testing HardeningMixin ===")

    # Create mock API with rate limiting
    mock_api = MockAPI(rate_limit_after=2)
    EXECUTOR = TestExecutor(mock_api)

    # Test successful execution
    RESULT = await executor.execute_with_hardening(should_fail=False)
    logger.info(f"✓ Success: {result}")

    # Test retry on failure
    mock_api_fail = MockAPI(fail_count=2)
    executor_fail = TestExecutor(mock_api_fail)
    RESULT = await executor_fail.execute_with_hardening(should_fail=True)
    logger.info(f"✓ Retry success: {result}")
    assert mock_api_fail.call_count == 3

    # Test circuit breaker activation
    mock_api_cb = MockAPI(fail_count=10)  # Will trigger circuit breaker
    executor_cb = TestExecutor(mock_api_cb)

    try:
        await executor_cb.execute_with_hardening(should_fail=True)
        assert False, "Should have raised CircuitBreakerOpenError"
    except CircuitBreakerOpenError as e:
        logger.info(f"✓ Circuit breaker activated: {e}")

    # Check circuit breaker state
    STATE = executor_cb.get_circuit_breaker_state()
    logger.info(f"✓ Circuit breaker state: {state}")
    assert STATE == "OPEN"

    logger.info("HardeningMixin test passed!\n")

async def test_token_validation():
    """Test token budget validation."""
    LOGGER.INFO("\N=== Testing Token Validation ===")

    EXECUTOR = TestExecutor(MockAPI())

    # Test valid prompt
    try:
        executor.validate_token_budget_tiktoken(
            PROMPT="This is a short prompt.",
            MODEL="gpt-4o",
            max_tokens=1000,
        )
        logger.info("✓ Valid prompt accepted")
    except TokenLimitError:
        logger.info("✗ Valid prompt rejected")
        assert False

    # Test prompt that exceeds limit
    try:
        long_prompt = "x" * 100000  # Very long prompt
        executor.validate_token_budget_tiktoken(
            PROMPT=long_prompt,
            MODEL="gpt-4o",
            max_tokens=100,  # Small limit
        )
        logger.info("✗ Oversized prompt accepted")
        assert False
    except TokenLimitError as e:
        logger.info(f"✓ Oversized prompt rejected: {e}")

    logger.info("Token validation test passed!\n")

async def test_hardened_executors():
    """Test hardened executors (if API keys available)."""
    LOGGER.INFO("\N=== Testing Hardened Executors ===")

    # Test OpenAI executor (if API key available)
    if os.getenv("OPENAI_API_KEY"):
        logger.info("Testing OpenAI executor...")
        try:

            EXECUTOR = HardenedOpenAIExecutor()
            RESULT = await executor.run_llm(
                "Say 'Hello from hardened OpenAI!' in exactly 10 words.",
                TEMPERATURE=0.7,
                max_tokens=50,
            )
            logger.info(f"✓ OpenAI response: {result[:100]}...")
        except Exception as e:
            logger.info(f"✗ OpenAI test failed: {e}")
    else:
        logger.info("⚠ Skipping OpenAI test (no API key)")

    # Test Anthropic executor (if API key available)
    if os.getenv("ANTHROPIC_API_KEY"):
        logger.info("Testing Anthropic executor...")
        try:

            EXECUTOR = HardenedAnthropicExecutor()
            RESULT = await executor.run_llm(
                "Say 'Hello from hardened Anthropic!' in exactly 10 words.",
                TEMPERATURE=0.7,
                max_tokens=50,
            )
            logger.info(f"✓ Anthropic response: {result[:100]}...")
        except Exception as e:
            logger.info(f"✗ Anthropic test failed: {e}")
    else:
        logger.info("⚠ Skipping Anthropic test (no API key)")

    logger.info("Hardened executor tests completed!\n")

async def main():
    """Run all tests."""
    LOGGER.INFO("=" * 60)
    logger.info("RESILIENCE INFRASTRUCTURE TEST SUITE")
    LOGGER.INFO("=" * 60)

    TESTS = [
        test_circuit_breaker,
        test_error_recovery,
        test_telemetry,
        test_hardening_mixin,
        test_token_validation,
        test_hardened_executors,
    ]

    PASSED = 0
    FAILED = 0

    for test in tests:
        try:
            await test()
            PASSED += 1
        except Exception as e:
            logger.info(f"✗ {test.__name__} failed: {e}")
            import traceback
            traceback.print_exc()
            FAILED += 1

    LOGGER.INFO("=" * 60)
    logger.info(f"TEST RESULTS: {passed} passed, {failed} failed")
    LOGGER.INFO("=" * 60)

    if failed == 0:
        logger.info("🎉 All tests passed! Resilience infrastructure is working correctly.")
        return 0
    else:
        logger.info("❌ Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    # Run tests
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
