"""
Phase 2 Test Suite: Tool Reliability, Distributed Tracing, Vector Memory

Tests for:
- ToolReliabilityMixin: Retry logic, circuit breakers, fallback mechanisms
- TracingMixin: Span management, context propagation (existing)
- PineconeVectorMixin: Vector operations (existing)
"""

from __future__ import annotations

import pytest
import time

from agentic_core.base_agents.tool_reliability_mixin import (
    ToolReliabilityMixin,
    CircuitState,
    CircuitBreakerError,
    RetryExhaustedError,
)
from agentic_core.base_agents.tracing_mixin import (
    TracingMixin,
    SpanContext,
)


# =============================================================================
# Test Fixtures
# =============================================================================


class MockReliabilityAgent(ToolReliabilityMixin):
    """Mock agent for testing ToolReliabilityMixin."""

    def __init__(self):
        super().__init__()


class MockTracingAgent(TracingMixin):
    """Mock agent for testing TracingMixin."""

    def __init__(self):
        super().__init__(service_name="test_service")


class MockCombinedAgent(ToolReliabilityMixin, TracingMixin):
    """Mock agent combining Phase 2 mixins."""

    def __init__(self):
        super().__init__(service_name="combined_service")


@pytest.fixture
def reliability_agent():
    """Create a fresh reliability agent for each test."""
    return MockReliabilityAgent()


@pytest.fixture
def tracing_agent():
    """Create a fresh tracing agent for each test."""
    # Reset circuit breaker state between tests
    TracingMixin._circuit_breaker_open = False
    TracingMixin._circuit_breaker_failures = 0
    return MockTracingAgent()


@pytest.fixture
def combined_agent():
    """Create a fresh combined agent for each test."""
    TracingMixin._circuit_breaker_open = False
    TracingMixin._circuit_breaker_failures = 0
    return MockCombinedAgent()


# =============================================================================
# ToolReliabilityMixin Tests
# =============================================================================


class TestToolReliabilityInitialization:
    """Test ToolReliabilityMixin initialization."""

    def test_initialization_flag_set(self, reliability_agent):
        """Verify initialization flag is set."""
        assert reliability_agent._tool_reliability_initialized is True

    def test_empty_policies_on_init(self, reliability_agent):
        """Verify empty policies on initialization."""
        assert reliability_agent._retry_policies == {}
        assert reliability_agent._circuit_configs == {}
        assert reliability_agent._tool_health == {}


class TestRetryConfiguration:
    """Test retry policy configuration."""

    def test_configure_retry_basic(self, reliability_agent):
        """Test basic retry configuration."""
        reliability_agent.configure_tool_retry("test_tool", max_retries=5)
        policy = reliability_agent._retry_policies["test_tool"]
        assert policy.max_retries == 5
        assert policy.base_delay_seconds == 1.0

    def test_configure_retry_full(self, reliability_agent):
        """Test full retry configuration."""
        reliability_agent.configure_tool_retry(
            "test_tool",
            max_retries=3,
            base_delay_seconds=0.5,
            max_delay_seconds=10.0,
            exponential_base=3.0,
            jitter=False,
        )
        policy = reliability_agent._retry_policies["test_tool"]
        assert policy.max_retries == 3
        assert policy.base_delay_seconds == 0.5
        assert policy.max_delay_seconds == 10.0
        assert policy.exponential_base == 3.0
        assert policy.jitter is False

    def test_configure_creates_health_tracking(self, reliability_agent):
        """Test that configuration creates health tracking."""
        reliability_agent.configure_tool_retry("new_tool")
        assert "new_tool" in reliability_agent._tool_health


class TestCircuitBreakerConfiguration:
    """Test circuit breaker configuration."""

    def test_configure_circuit_breaker_basic(self, reliability_agent):
        """Test basic circuit breaker configuration."""
        reliability_agent.configure_circuit_breaker("test_tool")
        config = reliability_agent._circuit_configs["test_tool"]
        assert config.failure_threshold == 5
        assert config.timeout_seconds == 60.0

    def test_configure_circuit_breaker_full(self, reliability_agent):
        """Test full circuit breaker configuration."""
        reliability_agent.configure_circuit_breaker(
            "test_tool",
            failure_threshold=3,
            success_threshold=1,
            timeout_seconds=30.0,
            half_open_max_calls=2,
        )
        config = reliability_agent._circuit_configs["test_tool"]
        assert config.failure_threshold == 3
        assert config.success_threshold == 1
        assert config.timeout_seconds == 30.0
        assert config.half_open_max_calls == 2


class TestRetryLogic:
    """Test retry execution logic."""

    @pytest.mark.asyncio
    async def test_successful_operation_no_retry(self, reliability_agent):
        """Test successful operation doesn't retry."""
        reliability_agent.configure_tool_retry("test_tool", max_retries=3)
        call_count = 0

        async def operation():
            nonlocal call_count
            call_count += 1
            return "success"

        result = await reliability_agent.with_retry("test_tool", operation)
        assert result == "success"
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_retry_on_failure(self, reliability_agent):
        """Test retry on transient failure."""
        reliability_agent.configure_tool_retry("test_tool", max_retries=3, base_delay_seconds=0.01)
        call_count = 0

        async def operation():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Transient error")
            return "success"

        result = await reliability_agent.with_retry("test_tool", operation)
        assert result == "success"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_retry_exhausted_raises(self, reliability_agent):
        """Test RetryExhaustedError when all retries fail."""
        reliability_agent.configure_tool_retry("test_tool", max_retries=2, base_delay_seconds=0.01)

        async def operation():
            raise ValueError("Persistent error")

        with pytest.raises(RetryExhaustedError) as exc_info:
            await reliability_agent.with_retry("test_tool", operation)

        assert exc_info.value.tool_name == "test_tool"
        assert exc_info.value.attempts == 3  # Initial + 2 retries

    @pytest.mark.asyncio
    async def test_fallback_on_exhaustion(self, reliability_agent):
        """Test fallback is called when retries exhausted."""
        reliability_agent.configure_tool_retry("test_tool", max_retries=1, base_delay_seconds=0.01)

        async def operation():
            raise ValueError("Error")

        def fallback():
            return "fallback_result"

        result = await reliability_agent.with_retry("test_tool", operation, fallback=fallback)
        assert result == "fallback_result"

    @pytest.mark.asyncio
    async def test_on_retry_callback(self, reliability_agent):
        """Test on_retry callback is called."""
        reliability_agent.configure_tool_retry("test_tool", max_retries=2, base_delay_seconds=0.01)
        retry_attempts = []

        async def operation():
            if len(retry_attempts) < 2:
                raise ValueError("Error")
            return "success"

        def on_retry(attempt, error):
            retry_attempts.append((attempt, str(error)))

        result = await reliability_agent.with_retry("test_tool", operation, on_retry=on_retry)
        assert result == "success"
        assert len(retry_attempts) == 2


class TestCircuitBreakerLogic:
    """Test circuit breaker execution logic."""

    def test_circuit_opens_after_failures(self, reliability_agent):
        """Test circuit opens after threshold failures."""
        reliability_agent.configure_circuit_breaker("test_tool", failure_threshold=3)

        # Record failures
        for _ in range(3):
            reliability_agent._record_failure("test_tool", ValueError("Error"))

        health = reliability_agent._tool_health["test_tool"]
        assert health.circuit_state == CircuitState.OPEN

    def test_circuit_breaker_blocks_calls(self, reliability_agent):
        """Test open circuit blocks calls."""
        reliability_agent.configure_circuit_breaker(
            "test_tool", failure_threshold=2, timeout_seconds=60.0
        )

        # Open the circuit
        for _ in range(2):
            reliability_agent._record_failure("test_tool", ValueError("Error"))

        with pytest.raises(CircuitBreakerError) as exc_info:
            reliability_agent._check_circuit_breaker("test_tool")

        assert exc_info.value.tool_name == "test_tool"

    def test_circuit_transitions_to_half_open(self, reliability_agent):
        """Test circuit transitions to half-open after timeout."""
        reliability_agent.configure_circuit_breaker(
            "test_tool", failure_threshold=2, timeout_seconds=0.01
        )

        # Open the circuit
        for _ in range(2):
            reliability_agent._record_failure("test_tool", ValueError("Error"))

        # Wait for timeout
        time.sleep(0.02)

        # Should transition to half-open
        reliability_agent._check_circuit_breaker("test_tool")
        health = reliability_agent._tool_health["test_tool"]
        assert health.circuit_state == CircuitState.HALF_OPEN

    def test_circuit_closes_after_success(self, reliability_agent):
        """Test circuit closes after successful calls in half-open."""
        reliability_agent.configure_circuit_breaker(
            "test_tool",
            failure_threshold=2,
            success_threshold=2,
            timeout_seconds=0.01,
        )

        # Open the circuit
        for _ in range(2):
            reliability_agent._record_failure("test_tool", ValueError("Error"))

        # Wait and transition to half-open
        time.sleep(0.02)
        reliability_agent._check_circuit_breaker("test_tool")

        # Record successes
        for _ in range(2):
            reliability_agent._record_success("test_tool")

        health = reliability_agent._tool_health["test_tool"]
        assert health.circuit_state == CircuitState.CLOSED

    def test_reset_circuit_breaker(self, reliability_agent):
        """Test manual circuit breaker reset."""
        reliability_agent.configure_circuit_breaker("test_tool", failure_threshold=2)

        # Open the circuit
        for _ in range(2):
            reliability_agent._record_failure("test_tool", ValueError("Error"))

        # Reset
        reliability_agent.reset_circuit_breaker("test_tool")

        health = reliability_agent._tool_health["test_tool"]
        assert health.circuit_state == CircuitState.CLOSED
        assert health.consecutive_failures == 0


class TestToolHealth:
    """Test tool health tracking."""

    def test_health_tracking_success(self, reliability_agent):
        """Test health tracking on success."""
        reliability_agent._ensure_tool_health("test_tool")
        reliability_agent._record_success("test_tool")

        health = reliability_agent._tool_health["test_tool"]
        assert health.total_calls == 1
        assert health.successful_calls == 1
        assert health.success_rate == 1.0
        assert health.is_healthy is True

    def test_health_tracking_failure(self, reliability_agent):
        """Test health tracking on failure."""
        reliability_agent._ensure_tool_health("test_tool")
        reliability_agent._record_failure("test_tool", ValueError("Error"))

        health = reliability_agent._tool_health["test_tool"]
        assert health.total_calls == 1
        assert health.failed_calls == 1
        assert health.success_rate == 0.0
        assert health.last_error == "Error"

    def test_get_tool_health(self, reliability_agent):
        """Test getting tool health status."""
        reliability_agent.configure_tool_retry("test_tool")
        reliability_agent._record_success("test_tool")
        reliability_agent._record_failure("test_tool", ValueError("Error"))

        status = reliability_agent.get_tool_health("test_tool")
        assert status["total_calls"] == 2
        assert status["successful_calls"] == 1
        assert status["failed_calls"] == 1
        assert status["success_rate"] == 0.5

    def test_get_all_tool_health(self, reliability_agent):
        """Test getting all tool health."""
        reliability_agent.configure_tool_retry("tool1")
        reliability_agent.configure_tool_retry("tool2")

        all_health = reliability_agent.get_all_tool_health()
        assert "tool1" in all_health
        assert "tool2" in all_health


class TestSyncRetry:
    """Test synchronous retry logic."""

    def test_sync_retry_success(self, reliability_agent):
        """Test synchronous retry on success."""
        reliability_agent.configure_tool_retry("test_tool")
        call_count = 0

        def operation():
            nonlocal call_count
            call_count += 1
            return "success"

        result = reliability_agent.with_retry_sync("test_tool", operation)
        assert result == "success"
        assert call_count == 1

    def test_sync_retry_with_fallback(self, reliability_agent):
        """Test synchronous retry with fallback."""
        reliability_agent.configure_tool_retry("test_tool", max_retries=1, base_delay_seconds=0.01)

        def operation():
            raise ValueError("Error")

        def fallback():
            return "fallback"

        result = reliability_agent.with_retry_sync("test_tool", operation, fallback=fallback)
        assert result == "fallback"


# =============================================================================
# TracingMixin Tests
# =============================================================================


class TestTracingInitialization:
    """Test TracingMixin initialization."""

    def test_initialization_sets_service_name(self, tracing_agent):
        """Verify service name is set."""
        assert tracing_agent._tracing_service_name == "test_service"

    def test_initialization_creates_empty_span_stack(self, tracing_agent):
        """Verify empty span stack on init."""
        assert tracing_agent._span_stack == []

    def test_initialization_with_circuit_breaker(self, tracing_agent):
        """Verify circuit breaker state is initialized."""
        assert hasattr(tracing_agent, "_tracing_initialized")


class TestSpanManagement:
    """Test span creation and management."""

    def test_start_span_creates_context(self, tracing_agent):
        """Test span creation."""
        with tracing_agent.start_span("test_operation") as span:
            assert isinstance(span, SpanContext)
            assert span.operation_name == "test_operation"
            assert span.service_name == "test_service"

    def test_span_has_trace_id(self, tracing_agent):
        """Test span has trace ID."""
        with tracing_agent.start_span("test_operation") as span:
            assert span.trace_id is not None
            assert len(span.trace_id) > 0

    def test_nested_spans_share_trace_id(self, tracing_agent):
        """Test nested spans share trace ID."""
        with tracing_agent.start_span("outer") as outer:
            with tracing_agent.start_span("inner") as inner:
                assert inner.trace_id == outer.trace_id
                assert inner.parent_span_id == outer.span_id

    def test_span_attributes(self, tracing_agent):
        """Test span attributes."""
        with tracing_agent.start_span("test_operation", attributes={"key": "value"}) as span:
            assert span.attributes["key"] == "value"

    def test_span_records_error(self, tracing_agent):
        """Test span records error on exception."""
        try:
            with tracing_agent.start_span("test_operation") as span:
                raise ValueError("Test error")
        except ValueError:
            pass

        assert span.status == "ERROR"
        assert "error" in span.attributes


class TestTraceContext:
    """Test trace context propagation."""

    def test_get_trace_context(self, tracing_agent):
        """Test getting trace context."""
        with tracing_agent.start_span("test_operation"):
            context = tracing_agent.get_trace_context()
            assert "trace_id" in context
            assert "span_id" in context
            assert context["service_name"] == "test_service"

    def test_inject_trace_context(self, tracing_agent):
        """Test injecting external trace context."""
        tracing_agent.inject_trace_context(
            {"trace_id": "external-trace-123", "span_id": "external-span-456"}
        )
        assert tracing_agent._current_trace_id == "external-trace-123"
        assert tracing_agent._current_span_id == "external-span-456"


class TestTraceBuffer:
    """Test trace buffering."""

    def test_spans_buffered(self, tracing_agent):
        """Test completed spans are buffered."""
        with tracing_agent.start_span("test_operation"):
            pass

        assert len(tracing_agent._trace_buffer) == 1

    def test_flush_traces(self, tracing_agent):
        """Test flushing trace buffer."""
        with tracing_agent.start_span("test_operation"):
            pass

        traces = tracing_agent.flush_traces()
        assert len(traces) == 1
        assert len(tracing_agent._trace_buffer) == 0

    def test_buffer_overflow_protection(self, tracing_agent):
        """Test buffer doesn't grow unbounded."""
        tracing_agent._trace_buffer_max = 10

        for i in range(15):
            with tracing_agent.start_span(f"operation_{i}"):
                pass

        assert len(tracing_agent._trace_buffer) <= 10


class TestTracingStatus:
    """Test tracing status reporting."""

    def test_get_tracing_status(self, tracing_agent):
        """Test getting tracing status."""
        status = tracing_agent.get_tracing_status()
        assert "enabled" in status
        assert "sample_rate" in status
        assert status["service_name"] == "test_service"


# =============================================================================
# Combined Agent Tests
# =============================================================================


class TestCombinedPhase2Agent:
    """Test combined Phase 2 functionality."""

    def test_combined_initialization(self, combined_agent):
        """Test combined agent initializes both mixins."""
        assert combined_agent._tool_reliability_initialized is True
        assert hasattr(combined_agent, "_tracing_service_name")

    @pytest.mark.asyncio
    async def test_retry_with_tracing(self, combined_agent):
        """Test retry operations are traced."""
        combined_agent.configure_tool_retry("traced_tool", max_retries=1)

        async def operation():
            return "success"

        with combined_agent.start_span("retry_test"):
            result = await combined_agent.with_retry("traced_tool", operation)

        assert result == "success"
        assert len(combined_agent._trace_buffer) >= 1


# =============================================================================
# Edge Cases and Error Handling
# =============================================================================


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_unconfigured_tool_no_retry(self, reliability_agent):
        """Test unconfigured tool uses default policy."""
        call_count = 0

        def operation():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("Error")
            return "success"

        # Should use default RetryPolicy
        result = reliability_agent.with_retry_sync("unknown_tool", operation)
        assert result == "success"

    def test_tool_health_unknown_tool(self, reliability_agent):
        """Test getting health for unknown tool."""
        status = reliability_agent.get_tool_health("unknown_tool")
        assert status["status"] == "unknown"

    def test_delay_calculation_respects_max(self, reliability_agent):
        """Test delay calculation respects maximum."""
        # Configure with valid parameters where max > base
        reliability_agent.configure_tool_retry(
            "test_tool",
            base_delay_seconds=1.0,
            max_delay_seconds=5.0,
            exponential_base=2.0,
            jitter=False,
        )

        # After 5 attempts: 1.0 * 2^5 = 32.0, but should be capped at 5.0
        delay = reliability_agent._calculate_delay("test_tool", 5)
        assert delay <= 5.0

    @pytest.mark.asyncio
    async def test_async_fallback(self, reliability_agent):
        """Test async fallback function."""
        reliability_agent.configure_tool_retry("test_tool", max_retries=0, base_delay_seconds=0.01)

        async def operation():
            raise ValueError("Error")

        async def async_fallback():
            return "async_fallback"

        result = await reliability_agent.with_retry("test_tool", operation, fallback=async_fallback)
        assert result == "async_fallback"

    def test_span_context_to_dict(self):
        """Test SpanContext serialization."""
        span = SpanContext(
            trace_id="trace-123",
            span_id="span-456",
            service_name="test",
            operation_name="op",
        )
        span.end_time = span.start_time + 0.5

        data = span.to_dict()
        assert data["trace_id"] == "trace-123"
        assert data["span_id"] == "span-456"
        assert data["duration_ms"] is not None
        assert abs(data["duration_ms"] - 500) < 10
