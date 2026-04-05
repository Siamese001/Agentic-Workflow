"""Validation Tests for Hardened Qwen vLLM Components.

Tests the hardened client, circuit breaker, and retry logic
without requiring a live vLLM server (uses mocking).
"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from apps_qwen import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitBreakerOpenError,
    CircuitState,
    HardenedVLLMClient,
    RetryConfig,
    VLLMRequest,
    VLLMResponse,
)


class TestCircuitBreaker:
    """Test circuit breaker pattern."""

    @pytest.mark.asyncio
    async def test_circuit_starts_closed(self):
        """Circuit should start in CLOSED state."""
        config = CircuitBreakerConfig(failure_threshold=3)
        cb = CircuitBreaker(config)

        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 0

    @pytest.mark.asyncio
    async def test_circuit_opens_after_failures(self):
        """Circuit should open after threshold failures."""
        config = CircuitBreakerConfig(failure_threshold=3)
        cb = CircuitBreaker(config)

        # Record failures
        for _ in range(3):
            await cb._record_failure()

        assert cb.state == CircuitState.OPEN
        assert cb.failure_count == 3

    @pytest.mark.asyncio
    async def test_circuit_allows_calls_when_closed(self):
        """Calls should succeed when circuit is closed."""
        config = CircuitBreakerConfig(failure_threshold=3)
        cb = CircuitBreaker(config)

        async def success_op():
            return "success"

        result = await cb.call(success_op)
        assert result == "success"

    @pytest.mark.asyncio
    async def test_circuit_blocks_calls_when_open(self):
        """Calls should be rejected when circuit is open."""
        config = CircuitBreakerConfig(failure_threshold=1)
        cb = CircuitBreaker(config)

        # Open the circuit
        await cb._record_failure()
        assert cb.state == CircuitState.OPEN

        # Next call should be blocked
        with pytest.raises(CircuitBreakerOpenError):
            await cb.call(lambda: asyncio.sleep(0))

    @pytest.mark.asyncio
    async def test_circuit_half_open_after_timeout(self):
        """Circuit should enter half-open after recovery timeout."""
        config = CircuitBreakerConfig(
            failure_threshold=1,
            recovery_timeout_sec=0.1,  # Short for testing
        )
        cb = CircuitBreaker(config)

        # Open the circuit
        await cb._record_failure()
        assert cb.state == CircuitState.OPEN

        # Wait for recovery timeout
        await asyncio.sleep(0.15)

        # Call should trigger half-open
        try:
            await cb.call(lambda: asyncio.sleep(0))
        except CircuitBreakerOpenError:
            pass  # Expected if half_open_max_calls exceeded

        # Circuit should be in half-open state
        assert cb.state == CircuitState.HALF_OPEN

    @pytest.mark.asyncio
    async def test_circuit_closes_on_success_in_half_open(self):
        """Circuit should close after successes in half-open."""
        config = CircuitBreakerConfig(
            failure_threshold=1,
            recovery_timeout_sec=0.1,
            success_threshold=2,
        )
        cb = CircuitBreaker(config)

        # Open circuit
        await cb._record_failure()
        assert cb.state == CircuitState.OPEN

        # Wait for recovery timeout
        await asyncio.sleep(0.15)

        # Manually set to half-open to test success recording
        async with cb._lock:
            cb.state = CircuitState.HALF_OPEN
            cb.success_count = 0
            cb.half_open_calls = 0

        # Record successes to close circuit
        await cb._record_success()
        await cb._record_success()

        assert cb.state == CircuitState.CLOSED


class TestRetryLogic:
    """Test retry logic with exponential backoff."""

    @pytest.mark.asyncio
    async def test_retry_on_transient_failure(self):
        """Should retry on transient failures."""
        config = RetryConfig(max_retries=2, base_delay_sec=0.01)

        mock_client = MagicMock()
        mock_client.infer = AsyncMock()

        # First two calls fail, third succeeds
        mock_client.infer.side_effect = [
            VLLMResponse(
                success=False,
                text="",
                model="",
                tokens_used=0,
                latency_ms=0,
                error_message="transient error",
            ),
            VLLMResponse(
                success=False,
                text="",
                model="",
                tokens_used=0,
                latency_ms=0,
                error_message="transient error",
            ),
            VLLMResponse(
                success=True,
                text="success",
                model="qwen",
                tokens_used=10,
                latency_ms=100,
            ),
        ]

        hardened = HardenedVLLMClient(
            base_client=mock_client,
            retry_config=config,
        )

        req = VLLMRequest(prompt="test", max_tokens=10)
        resp = await hardened.infer(req)

        assert resp.success is True
        assert resp.text == "success"
        assert mock_client.infer.call_count == 3

    @pytest.mark.asyncio
    async def test_no_retry_on_client_error(self):
        """Should not retry on client errors (4xx)."""
        config = RetryConfig(max_retries=2, base_delay_sec=0.01)

        mock_client = MagicMock()
        mock_client.infer = AsyncMock(return_value=VLLMResponse(
            success=False,
            text="",
            model="",
            tokens_used=0,
            latency_ms=0,
            error_message="invalid request: bad prompt format",
        ))

        hardened = HardenedVLLMClient(
            base_client=mock_client,
            retry_config=config,
        )

        req = VLLMRequest(prompt="test", max_tokens=10)
        resp = await hardened.infer(req)

        assert resp.success is False
        # Should not retry on client error
        assert mock_client.infer.call_count == 1

    @pytest.mark.asyncio
    async def test_max_retries_exceeded(self):
        """Should fail after max retries exceeded."""
        config = RetryConfig(max_retries=2, base_delay_sec=0.01)

        mock_client = MagicMock()
        mock_client.infer = AsyncMock(return_value=VLLMResponse(
            success=False,
            text="",
            model="",
            tokens_used=0,
            latency_ms=0,
            error_message="server error",
        ))

        hardened = HardenedVLLMClient(
            base_client=mock_client,
            retry_config=config,
        )

        req = VLLMRequest(prompt="test", max_tokens=10)
        resp = await hardened.infer(req)

        assert resp.success is False
        assert "Max retries exceeded" in resp.error_message
        # Initial + 2 retries = 3 calls
        assert mock_client.infer.call_count == 3

    @pytest.mark.asyncio
    async def test_exponential_backoff_delays(self):
        """Retry delays should increase exponentially."""
        config = RetryConfig(
            max_retries=3,
            base_delay_sec=1.0,
            exponential_base=2.0,
            jitter=False,  # Disable jitter for predictable test
        )

        hardened = HardenedVLLMClient(
            base_client=MagicMock(),
            retry_config=config,
        )

        # Calculate delays
        delay_0 = hardened._calculate_delay(0)  # First retry
        delay_1 = hardened._calculate_delay(1)  # Second retry
        delay_2 = hardened._calculate_delay(2)  # Third retry

        assert delay_0 == 1.0  # 1.0 * 2^0
        assert delay_1 == 2.0  # 1.0 * 2^1
        assert delay_2 == 4.0  # 1.0 * 2^2

    @pytest.mark.asyncio
    async def test_delay_capped_at_max(self):
        """Retry delay should not exceed max_delay_sec."""
        config = RetryConfig(
            max_retries=10,
            base_delay_sec=1.0,
            exponential_base=2.0,
            max_delay_sec=5.0,
            jitter=False,
        )

        hardened = HardenedVLLMClient(
            base_client=MagicMock(),
            retry_config=config,
        )

        # Calculate delay for high retry count
        delay = hardened._calculate_delay(10)

        # Should be capped at max_delay_sec
        assert delay <= 5.0


class TestGPUOOMHandling:
    """Test GPU OOM handling and graceful degradation."""

    @pytest.mark.asyncio
    async def test_oom_detection(self):
        """Should detect OOM errors."""
        mock_client = MagicMock()
        hardened = HardenedVLLMClient(base_client=mock_client)

        oom_errors = [
            "CUDA out of memory",
            "OOM error occurred",
            "GPU memory exceeded",
            "out of memory allocation failed",
        ]

        for error in oom_errors:
            assert hardened._is_oom_error(error) is True

        # Non-OOM errors
        non_oom_errors = [
            "network timeout",
            "invalid request",
            "server busy",
        ]

        for error in non_oom_errors:
            assert hardened._is_oom_error(error) is False

    @pytest.mark.asyncio
    async def test_degraded_mode_on_oom(self):
        """Should enter degraded mode on OOM."""
        mock_client = MagicMock()
        mock_client.infer = AsyncMock(return_value=VLLMResponse(
            success=False,
            text="",
            model="",
            tokens_used=0,
            latency_ms=0,
            error_message="CUDA out of memory",
        ))
        mock_client.batch_size = 8

        hardened = HardenedVLLMClient(base_client=mock_client)

        req = VLLMRequest(prompt="test", max_tokens=10)
        await hardened.infer(req)

        assert hardened._degraded_mode is True
        assert hardened.metrics.gpu_oom_events == 1


class TestMetricsCollection:
    """Test metrics collection."""

    @pytest.mark.asyncio
    async def test_metrics_recorded(self):
        """Should record request metrics."""
        mock_client = MagicMock()
        mock_client.infer = AsyncMock(return_value=VLLMResponse(
            success=True,
            text="success",
            model="qwen",
            tokens_used=10,
            latency_ms=100,
        ))

        hardened = HardenedVLLMClient(base_client=mock_client)

        req = VLLMRequest(prompt="test", max_tokens=10)
        await hardened.infer(req)

        metrics = hardened.get_metrics()

        assert metrics["requests_total"] == 1
        assert metrics["requests_success"] == 1
        assert metrics["success_rate"] == 1.0
        assert metrics["latency_p50_ms"] == 100.0

    @pytest.mark.asyncio
    async def test_latency_percentiles(self):
        """Should calculate latency percentiles correctly."""
        mock_client = MagicMock()

        # Return different latencies
        latencies = [50, 100, 150, 200, 250, 300, 350, 400, 450, 500]
        mock_client.infer = AsyncMock(side_effect=[
            VLLMResponse(
                success=True,
                text="success",
                model="qwen",
                tokens_used=10,
                latency_ms=lat,
            )
            for lat in latencies
        ])

        hardened = HardenedVLLMClient(base_client=mock_client)

        for i in range(10):
            req = VLLMRequest(prompt=f"test {i}", max_tokens=10)
            await hardened.infer(req)

        metrics = hardened.get_metrics()

        # p50 should be around 275 (median)
        assert 250 <= metrics["latency_p50_ms"] <= 300
        # p99 should be near max
        assert metrics["latency_p99_ms"] >= 450


class TestIntegration:
    """Integration tests for hardened client."""

    @pytest.mark.asyncio
    async def test_successful_request_flow(self):
        """Test complete successful request flow."""
        mock_client = MagicMock()
        mock_client.infer = AsyncMock(return_value=VLLMResponse(
            success=True,
            text="The answer is 4",
            model="Qwen/Qwen2.5-14B-Instruct-AWQ",
            tokens_used=15,
            latency_ms=150,
        ))
        mock_client.health_check = AsyncMock(return_value={
            "healthy": True,
            "models": ["Qwen/Qwen2.5-14B-Instruct-AWQ"],
        })
        mock_client.get_metrics = MagicMock(return_value={
            "requests_total": 1,
        })
        mock_client.batch_size = 4

        hardened = HardenedVLLMClient(
            base_client=mock_client,
            retry_config=RetryConfig(max_retries=2),
            circuit_config=CircuitBreakerConfig(failure_threshold=5),
        )

        req = VLLMRequest(
            prompt="What is 2+2?",
            max_tokens=10,
            temperature=0.0,
        )

        resp = await hardened.infer(req)

        assert resp.success is True
        assert resp.text == "The answer is 4"
        assert resp.model == "Qwen/Qwen2.5-14B-Instruct-AWQ"

        # Check circuit still closed
        assert hardened.circuit.state == CircuitState.CLOSED

        # Check metrics
        metrics = hardened.get_metrics()
        assert metrics["requests_total"] == 1
        assert metrics["requests_success"] == 1

    @pytest.mark.asyncio
    async def test_circuit_opens_after_consecutive_failures(self):
        """Circuit should open after consecutive failures."""
        mock_client = MagicMock()
        mock_client.infer = AsyncMock(return_value=VLLMResponse(
            success=False,
            text="",
            model="",
            tokens_used=0,
            latency_ms=0,
            error_message="server error",
        ))

        hardened = HardenedVLLMClient(
            base_client=mock_client,
            retry_config=RetryConfig(max_retries=0),  # No retries for faster test
            circuit_config=CircuitBreakerConfig(failure_threshold=3),
        )

        # Make requests until circuit opens
        req = VLLMRequest(prompt="test", max_tokens=10)

        # Directly record failures to test circuit breaker logic
        for i in range(3):
            await hardened.circuit._record_failure()
            # Check state after each failure
            if i == 2:  # After 3rd failure
                assert hardened.circuit.state == CircuitState.OPEN

        # Circuit should now be open
        assert hardened.circuit.state == CircuitState.OPEN

        # Next request should be blocked by circuit
        resp = await hardened.infer(req)
        assert resp.success is False
        assert "Circuit breaker open" in resp.error_message


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
