#!/usr/bin/env python3
"""test_circuit_breaker.py — Unit tests for _notion_circuit_breaker module."""
import time
from unittest.mock import MagicMock

import pytest

from tools.notion._notion_circuit_breaker import (
    FAILURE_THRESHOLD,
    OPEN_TIMEOUT_SECONDS,
    SUCCESS_THRESHOLD,
    CircuitBreaker,
    CircuitBreakerOpenError,
    CircuitState,
    get_all_circuit_states,
    get_circuit_breaker,
    reset_all_circuits,
    with_circuit_breaker,
)


class TestCircuitBreakerBasic:
    """Tests for basic circuit breaker functionality."""
    
    def setup_method(self):
        reset_all_circuits()
    
    def teardown_method(self):
        reset_all_circuits()
    
    def test_initial_state_is_closed(self):
        cb = CircuitBreaker("test")
        assert cb.state == CircuitState.CLOSED
    
    def test_record_success_in_closed_state(self):
        cb = CircuitBreaker("test")
        cb.record_success()
        assert cb.state == CircuitState.CLOSED
        assert cb.stats.consecutive_successes == 1
        assert cb.stats.consecutive_failures == 0
    
    def test_record_failure_in_closed_state(self):
        cb = CircuitBreaker("test")
        cb.record_failure()
        assert cb.state == CircuitState.CLOSED
        assert cb.stats.consecutive_failures == 1
        assert cb.stats.consecutive_successes == 0
    
    def test_opens_after_failure_threshold(self):
        cb = CircuitBreaker("test", failure_threshold=3)
        
        # 3 consecutive failures should open
        cb.record_failure()
        assert cb.state == CircuitState.CLOSED
        cb.record_failure()
        assert cb.state == CircuitState.CLOSED
        cb.record_failure()
        assert cb.state == CircuitState.OPEN
    
    def test_blocks_calls_when_open(self):
        cb = CircuitBreaker("test", failure_threshold=1)
        cb.record_failure()  # Opens immediately
        
        assert cb.state == CircuitState.OPEN
        assert cb.can_execute() is False
    
    def test_transitions_to_half_open_after_timeout(self):
        cb = CircuitBreaker("test", failure_threshold=1, open_timeout=0.01)
        cb.record_failure()  # Opens
        
        assert cb.state == CircuitState.OPEN
        
        # Wait for timeout
        time.sleep(0.02)
        
        # can_execute checks timeout and transitions
        assert cb.can_execute() is True
        assert cb.state == CircuitState.HALF_OPEN
    
    def test_closes_after_success_threshold_in_half_open(self):
        cb = CircuitBreaker("test", failure_threshold=1, open_timeout=0.01, success_threshold=2)
        cb.record_failure()  # Opens
        time.sleep(0.02)
        
        # First probe
        assert cb.can_execute() is True
        cb.record_success()
        assert cb.state == CircuitState.HALF_OPEN  # Need 2 successes
        
        # Second probe
        assert cb.can_execute() is True
        cb.record_success()
        assert cb.state == CircuitState.CLOSED  # Now closed


class TestCircuitBreakerReset:
    """Tests for circuit breaker reset functionality."""
    
    def test_reset_to_closed(self):
        cb = CircuitBreaker("test", failure_threshold=1)
        cb.record_failure()  # Opens
        assert cb.state == CircuitState.OPEN
        
        cb.reset()
        assert cb.state == CircuitState.CLOSED
        assert cb.stats.consecutive_failures == 0
        assert cb.stats.consecutive_successes == 0


class TestCircuitBreakerStats:
    """Tests for circuit breaker statistics."""
    
    def test_stats_tracking(self):
        cb = CircuitBreaker("test")
        
        cb.record_success()
        cb.record_success()
        cb.record_failure()
        
        stats = cb.stats
        assert stats.successes == 2
        assert stats.failures == 1
        assert stats.consecutive_successes == 0  # Reset by failure
        assert stats.consecutive_failures == 1
    
    def test_to_dict_serialization(self):
        cb = CircuitBreaker("test", failure_threshold=5, success_threshold=3)
        cb.record_success()
        
        d = cb.to_dict()
        assert d["name"] == "test"
        assert d["state"] == "CLOSED"
        assert d["failure_threshold"] == 5
        assert d["success_threshold"] == 3
        assert d["stats"]["successes"] == 1


class TestCircuitBreakerSingleton:
    """Tests for global circuit breaker registry."""
    
    def setup_method(self):
        reset_all_circuits()
    
    def teardown_method(self):
        reset_all_circuits()
    
    def test_get_circuit_breaker_creates_new(self):
        cb = get_circuit_breaker("new_circuit")
        assert cb.name == "new_circuit"
        assert cb.state == CircuitState.CLOSED
    
    def test_get_circuit_breaker_returns_same_instance(self):
        cb1 = get_circuit_breaker("same_circuit")
        cb2 = get_circuit_breaker("same_circuit")
        assert cb1 is cb2
    
    def test_reset_all_circuits_clears_all(self):
        cb1 = get_circuit_breaker("circuit_1")
        cb2 = get_circuit_breaker("circuit_2")
        
        cb1.record_failure()
        cb1.record_failure()
        cb1.record_failure()
        cb1.record_failure()
        cb1.record_failure()  # Opens
        
        reset_all_circuits()
        
        # Get new instances
        cb1_new = get_circuit_breaker("circuit_1")
        assert cb1_new.state == CircuitState.CLOSED
    
    def test_get_all_circuit_states(self):
        cb1 = get_circuit_breaker("circuit_1")
        cb2 = get_circuit_breaker("circuit_2")
        
        states = get_all_circuit_states()
        assert "circuit_1" in states
        assert "circuit_2" in states
        assert states["circuit_1"]["state"] == "CLOSED"


class TestCircuitBreakerDecorator:
    """Tests for @with_circuit_breaker decorator."""
    
    def setup_method(self):
        reset_all_circuits()
    
    def teardown_method(self):
        reset_all_circuits()
    
    def test_decorator_passes_through_when_closed(self):
        @with_circuit_breaker("decorated_circuit")
        def success_func():
            return "success"
        
        result = success_func()
        assert result == "success"
    
    def test_decorator_records_success(self):
        @with_circuit_breaker("decorated_circuit")
        def success_func():
            return "success"
        
        success_func()
        
        cb = get_circuit_breaker("decorated_circuit")
        assert cb.stats.successes == 1
    
    def test_decorator_records_failure(self):
        @with_circuit_breaker("decorated_circuit")
        def fail_func():
            raise ValueError("Error")
        
        with pytest.raises(ValueError):
            fail_func()
        
        cb = get_circuit_breaker("decorated_circuit")
        assert cb.stats.failures == 1
    
    def test_decorator_raises_when_open(self):
        # First open the circuit
        cb = get_circuit_breaker("open_circuit")
        for _ in range(FAILURE_THRESHOLD):
            cb.record_failure()
        
        @with_circuit_breaker("open_circuit")
        def should_not_run():
            return "success"
        
        with pytest.raises(CircuitBreakerOpenError):
            should_not_run()
    
    def test_decorator_calls_on_open_callback(self):
        # First open the circuit
        cb = get_circuit_breaker("callback_circuit")
        for _ in range(FAILURE_THRESHOLD):
            cb.record_failure()
        
        fallback_result = {"fallback": True}
        
        @with_circuit_breaker("callback_circuit", on_open=lambda: fallback_result)
        def should_not_run():
            return "success"
        
        result = should_not_run()
        assert result == fallback_result


class TestCircuitBreakerConcurrency:
    """Basic thread-safety tests."""
    
    def setup_method(self):
        reset_all_circuits()
    
    def test_thread_safe_state_access(self):
        import threading
        
        cb = CircuitBreaker("concurrent", failure_threshold=100)
        
        def record_successes():
            for _ in range(50):
                cb.record_success()
        
        threads = [
            threading.Thread(target=record_successes)
            for _ in range(4)
        ]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert cb.stats.successes == 200
