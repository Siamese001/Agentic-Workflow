"""Tests for LIC Circuit Breaker - L3 orchestration layer."""

import pytest
import asyncio
from unittest.mock import MagicMock
from dataclasses import dataclass
from typing import Any, Dict

from l3.lic_circuit_breaker import (
    LICCircuitBreaker,
    LICBreakerConfig,
    LICBreakerStatus,
)


@pytest.fixture
def mock_telemetry_bus():
    """Mock telemetry bus."""
    bus = MagicMock()
    bus.record_event = MagicMock()
    return bus


@pytest.fixture
def sample_config():
    """Sample circuit breaker configuration for testing."""
    return LICBreakerConfig(
        failure_window=5,
        failure_threshold=3,
        cooldown_seconds=1.0,
        max_blocked_attempts=5,
    )


@pytest.fixture
def lic_circuit_breaker(sample_config, mock_telemetry_bus):
    """LIC circuit breaker fixture."""
    return LICCircuitBreaker(
        config=sample_config,
        telemetry_bus=mock_telemetry_bus,
    )


@pytest.fixture
def sample_outreach_context():
    """Sample outreach context for testing."""
    @dataclass
    class OutreachContext:
        recipient_profile: Dict[str, Any]
        company_data: Dict[str, Any]
        mission: str
        target_archetype: str
        metadata: Dict[str, Any]
    
    return OutreachContext(
        recipient_profile={"name": "John Doe"},
        company_data={"name": "TechCorp"},
        mission="Test mission",
        target_archetype="EXECUTIVE",
        metadata={"test": True},
    )


class TestLICCircuitBreaker:
    """Test suite for LIC circuit breaker."""
    
    @pytest.mark.asyncio
    async def test_breaker_opens_after_threshold(
        self,
        lic_circuit_breaker,
        sample_outreach_context,
        mock_telemetry_bus,
    ):
        """Test breaker opens when failure threshold is exceeded."""
        config = lic_circuit_breaker.config
        
        # Record successful attempts (should not open breaker)
        for i in range(2):
            await lic_circuit_breaker.record_attempt(
                outreach_context=sample_outreach_context,
                archetype="EXECUTIVE",
                success=True,
                safety_result=None,
                failure_type=None,
            )
        
        # Breaker should still be closed
        assert await lic_circuit_breaker.check_can_attempt(
            sample_outreach_context, 2, "EXECUTIVE"
        ) is True
        
        status = lic_circuit_breaker.get_status()
        assert status.is_open is False
        assert status.failure_count == 0
        
        # Record failures up to threshold
        for i in range(config.failure_threshold):
            await lic_circuit_breaker.record_attempt(
                outreach_context=sample_outreach_context,
                archetype="EXECUTIVE",
                success=False,
                safety_result=None,
                failure_type="creative",
            )
        
        # Breaker should now be open
        assert await lic_circuit_breaker.check_can_attempt(
            sample_outreach_context, 5, "EXECUTIVE"
        ) is False
        
        status = lic_circuit_breaker.get_status()
        assert status.is_open is True
        assert status.failure_count == config.failure_threshold
        assert status.last_failure_type == "creative"
        assert status.last_open_timestamp is not None
        
        # Verify telemetry was recorded
        mock_telemetry_bus.record_event.assert_any_call(
            "lic_circuit_breaker_open",
            "L3",
            {
                "failure_count": config.failure_threshold,
                "failure_threshold": config.failure_threshold,
                "failure_type": "creative",
                "window_size": config.failure_window,
            },
        )
    
    @pytest.mark.asyncio
    async def test_check_blocks_when_open(
        self,
        lic_circuit_breaker,
        sample_outreach_context,
    ):
        """Test check_can_attempt blocks when breaker is open."""
        # Open the breaker by exceeding threshold
        for i in range(5):  # Exceeds failure_threshold=3
            await lic_circuit_breaker.record_attempt(
                outreach_context=sample_outreach_context,
                archetype="EXECUTIVE",
                success=False,
                safety_result=None,
                failure_type="factual",
            )
        
        # All attempts should be blocked
        for i in range(3):
            assert await lic_circuit_breaker.check_can_attempt(
                sample_outreach_context, 5 + i, "EXECUTIVE"
            ) is False
        
        status = lic_circuit_breaker.get_status()
        assert status.is_open is True
        assert status.blocked_attempts == 3
    
    @pytest.mark.asyncio
    async def test_auto_close_after_cooldown(
        self,
        lic_circuit_breaker,
        sample_outreach_context,
    ):
        """Test breaker auto-closes after cooldown period."""
        # Open the breaker
        for i in range(5):
            await lic_circuit_breaker.record_attempt(
                outreach_context=sample_outreach_context,
                archetype="EXECUTIVE",
                success=False,
                safety_result=None,
                failure_type="creative",
            )
        
        # Verify it's open
        assert await lic_circuit_breaker.check_can_attempt(
            sample_outreach_context, 5, "EXECUTIVE"
        ) is False
        
        # Wait for cooldown period
        await asyncio.sleep(lic_circuit_breaker.config.cooldown_seconds + 0.1)
        
        # Should now be auto-closed
        assert await lic_circuit_breaker.check_can_attempt(
            sample_outreach_context, 6, "EXECUTIVE"
        ) is True
        
        status = lic_circuit_breaker.get_status()
        assert status.is_open is False
        assert status.blocked_attempts == 0  # Reset clears blocked attempts
    
    @pytest.mark.asyncio
    async def test_forced_reset_after_max_blocked_attempts(
        self,
        lic_circuit_breaker,
        sample_outreach_context,
    ):
        """Test forced reset after max blocked attempts."""
        # Open the breaker
        for i in range(5):
            await lic_circuit_breaker.record_attempt(
                outreach_context=sample_outreach_context,
                archetype="EXECUTIVE",
                success=False,
                safety_result=None,
                failure_type="safety",
            )
        
        # Block attempts up to max_blocked_attempts
        max_blocked = lic_circuit_breaker.config.max_blocked_attempts
        for i in range(max_blocked):
            result = await lic_circuit_breaker.check_can_attempt(
                sample_outreach_context, 5 + i, "EXECUTIVE"
            )
            # Last attempt should succeed due to forced reset
            if i < max_blocked - 1:
                assert result is False
            else:
                assert result is True
        
        status = lic_circuit_breaker.get_status()
        assert status.is_open is False  # Should be reset
        assert status.blocked_attempts == 0
    
    @pytest.mark.asyncio
    async def test_sliding_window_trims_correctly(
        self,
        lic_circuit_breaker,
        sample_outreach_context,
    ):
        """Test sliding window trims to configured size."""
        config = lic_circuit_breaker.config
        window_size = config.failure_window
        
        # Fill window with failures
        for i in range(window_size + 3):  # More than window size
            await lic_circuit_breaker.record_attempt(
                outreach_context=sample_outreach_context,
                archetype="EXECUTIVE",
                success=False,
                safety_result=None,
                failure_type="creative",
            )
        
        status = lic_circuit_breaker.get_status()
        assert status.metadata["window_size"] == window_size
        assert status.failure_count == window_size  # Should be trimmed
        
        # Add successful attempts to slide the window
        for i in range(window_size):
            await lic_circuit_breaker.record_attempt(
                outreach_context=sample_outreach_context,
                archetype="EXECUTIVE",
                success=True,
                safety_result=None,
                failure_type=None,
            )
        
        status = lic_circuit_breaker.get_status()
        assert status.metadata["window_size"] == window_size
        assert status.failure_count == 0  # All failures should have slid out
    
    @pytest.mark.asyncio
    async def test_status_fields_populated(
        self,
        lic_circuit_breaker,
        sample_outreach_context,
    ):
        """Test status object contains all required fields."""
        # Record mixed attempts
        await lic_circuit_breaker.record_attempt(
            outreach_context=sample_outreach_context,
            archetype="EXECUTIVE",
            success=True,
            safety_result=None,
            failure_type=None,
        )
        await lic_circuit_breaker.record_attempt(
            outreach_context=sample_outreach_context,
            archetype="SENIOR_TA",
            success=False,
            safety_result=None,
            failure_type="factual",
        )
        
        status = lic_circuit_breaker.get_status()
        
        # Verify all required fields are present and correct
        assert isinstance(status, LICBreakerStatus)
        assert status.is_open is False
        assert status.failure_count == 1
        assert status.total_attempts == 2
        assert status.last_failure_type == "factual"
        assert status.last_open_timestamp is None
        assert status.blocked_attempts == 0
        
        # Verify metadata contains config
        assert "config" in status.metadata
        config_meta = status.metadata["config"]
        assert config_meta["failure_window"] == lic_circuit_breaker.config.failure_window
        assert config_meta["failure_threshold"] == lic_circuit_breaker.config.failure_threshold
        assert config_meta["cooldown_seconds"] == lic_circuit_breaker.config.cooldown_seconds
        assert config_meta["max_blocked_attempts"] == lic_circuit_breaker.config.max_blocked_attempts
    
    @pytest.mark.asyncio
    async def test_manual_reset(
        self,
        lic_circuit_breaker,
        sample_outreach_context,
    ):
        """Test manual reset functionality."""
        # Open the breaker and record attempts
        for i in range(5):
            await lic_circuit_breaker.record_attempt(
                outreach_context=sample_outreach_context,
                archetype="EXECUTIVE",
                success=False,
                safety_result=None,
                failure_type="creative",
            )
        
        # Verify it's open
        status = lic_circuit_breaker.get_status()
        assert status.is_open is True
        assert status.total_attempts > 0
        
        # Manual reset
        await lic_circuit_breaker.reset()
        
        # Verify everything is cleared
        status = lic_circuit_breaker.get_status()
        assert status.is_open is False
        assert status.failure_count == 0
        assert status.total_attempts == 0
        assert status.last_failure_type is None
        assert status.last_open_timestamp is None
        assert status.blocked_attempts == 0
        assert status.metadata["window_size"] == 0
    
    @pytest.mark.asyncio
    async def test_concurrency_safety(
        self,
        lic_circuit_breaker,
        sample_outreach_context,
    ):
        """Test concurrent operations are thread-safe."""
        # Simulate concurrent record attempts
        tasks = []
        for i in range(10):
            task = lic_circuit_breaker.record_attempt(
                outreach_context=sample_outreach_context,
                archetype="EXECUTIVE",
                success=i % 3 == 0,  # Some successes, some failures
                safety_result=None,
                failure_type="creative" if i % 3 != 0 else None,
            )
            tasks.append(task)
        
        # Run all concurrently
        await asyncio.gather(*tasks)
        
        # Verify final state is consistent
        status = lic_circuit_breaker.get_status()
        assert status.total_attempts == 10
        assert status.metadata["window_size"] <= lic_circuit_breaker.config.failure_window
        
        # Simulate concurrent check attempts
        check_tasks = []
        for i in range(5):
            task = lic_circuit_breaker.check_can_attempt(
                sample_outreach_context, 10 + i, "EXECUTIVE"
            )
            check_tasks.append(task)
        
        results = await asyncio.gather(*check_tasks)
        
        # Results should include both blocked (False) and allowed (True) due to forced reset
        # This is expected behavior when max_blocked_attempts is reached
        assert False in results  # Some should be blocked before reset
        assert True in results   # Some should be allowed after forced reset
    
    @pytest.mark.asyncio
    async def test_default_configuration(
        self,
        mock_telemetry_bus,
        sample_outreach_context,
    ):
        """Test circuit breaker works with default configuration."""
        breaker = LICCircuitBreaker(telemetry_bus=mock_telemetry_bus)
        
        # Verify default config values
        assert breaker.config.failure_window == 10
        assert breaker.config.failure_threshold == 5
        assert breaker.config.cooldown_seconds == 60.0
        assert breaker.config.max_blocked_attempts == 20
        
        # Test basic functionality with defaults
        for i in range(6):  # Exceeds default threshold of 5
            await breaker.record_attempt(
                outreach_context=sample_outreach_context,
                archetype="EXECUTIVE",
                success=False,
                safety_result=None,
                failure_type="creative",
            )
        
        # Should open with default threshold
        assert await breaker.check_can_attempt(
            sample_outreach_context, 6, "EXECUTIVE"
        ) is False
    
    @pytest.mark.asyncio
    async def test_telemetry_error_handling(
        self,
        lic_circuit_breaker,
        sample_outreach_context,
    ):
        """Test telemetry errors don't break circuit breaker logic."""
        # Make telemetry bus raise exceptions
        lic_circuit_breaker.telemetry_bus.record_event.side_effect = Exception("Telemetry failed")
        
        # Operations should still work despite telemetry failures
        await lic_circuit_breaker.record_attempt(
            outreach_context=sample_outreach_context,
            archetype="EXECUTIVE",
            success=False,
            safety_result=None,
            failure_type="creative",
        )
        
        result = await lic_circuit_breaker.check_can_attempt(
            sample_outreach_context, 1, "EXECUTIVE"
        )
        
        # Should still function normally
        assert result is True
        
        status = lic_circuit_breaker.get_status()
        assert status.total_attempts == 1


if __name__ == "__main__":
    pytest.main([__file__])
