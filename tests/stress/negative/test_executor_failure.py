"""
Phase 9 Negative Path Tests - Executor Failure

Tests graceful failure handling when executor operations fail,
timeout scenarios, and resilience under executor stress.
"""

import pytest
import asyncio
import threading
import time
from typing import Dict, Any
from unittest.mock import Mock, patch

from runtime.execution_budget_manager import (
    ExecutionBudgetManager,
    BudgetLimits,
    get_budget_manager
)
from l3.outreach_orchestrator import OutreachOrchestrator


class TestExecutorFailure:
    """Test executor failure scenarios and graceful failure handling."""
    
    def setup_method(self):
        """Setup fresh budget manager for each test."""
        # Clear singleton to ensure clean state
        ExecutionBudgetManager._instance = None
        self.budget_manager = get_budget_manager()
        self.budget_manager.reset_usage()
        
        # Configure low timeout for testing failures
        self.low_timeout_limits = BudgetLimits(executor_timeout=0.1)
        self.budget_manager.configure(self.low_timeout_limits)
    
    def test_concurrent_slot_timeout_failure(self):
        """Test concurrent slot acquisition timeout."""
        # Configure very low parallel limit
        self.budget_manager.configure(BudgetLimits(
            max_parallel=1,
            executor_timeout=0.1  # Very short timeout
        ))
        
        # Acquire the only available slot
        assert self.budget_manager.acquire_concurrent_slot() is True
        
        # Try to acquire another slot with short timeout - should fail
        result = self.budget_manager.acquire_concurrent_slot(timeout=0.05)
        assert result is False
        
        # Clean up
        self.budget_manager.release_concurrent_slot()
    
    def test_concurrent_slot_timeout_with_zero_timeout(self):
        """Test concurrent slot acquisition with zero timeout."""
        # Acquire all slots
        for _ in range(5):
            assert self.budget_manager.acquire_concurrent_slot() is True
        
        # Try to acquire with zero timeout - should fail immediately
        result = self.budget_manager.acquire_concurrent_slot(timeout=0)
        assert result is False
        
        # Clean up
        for _ in range(5):
            self.budget_manager.release_concurrent_slot()
    
    def test_concurrent_slot_timeout_negative_timeout(self):
        """Test concurrent slot acquisition with negative timeout."""
        # Acquire all slots
        for _ in range(5):
            assert self.budget_manager.acquire_concurrent_slot() is True
        
        # Try to acquire with negative timeout - should fail gracefully
        result = self.budget_manager.acquire_concurrent_slot(timeout=-1)
        # Should handle gracefully (either return False or raise appropriate error)
        assert result is False
        
        # Clean up
        for _ in range(5):
            self.budget_manager.release_concurrent_slot()
    
    def test_executor_timeout_configuration_change(self):
        """Test executor timeout configuration changes."""
        # Start with very short timeout
        self.budget_manager.configure(BudgetLimits(executor_timeout=0.01))
        
        # Acquire slot and try another with short timeout
        assert self.budget_manager.acquire_concurrent_slot() is True
        result = self.budget_manager.acquire_concurrent_slot(timeout=0.02)
        assert result is False
        
        # Increase timeout
        self.budget_manager.configure(BudgetLimits(executor_timeout=1.0))
        
        # Should still fail because slot is held, but timeout is longer
        result = self.budget_manager.acquire_concurrent_slot(timeout=0.1)
        assert result is False
        
        # Clean up
        self.budget_manager.release_concurrent_slot()
    
    def test_concurrent_slot_release_after_timeout(self):
        """Test releasing slots after timeout scenarios."""
        # Acquire a slot
        assert self.budget_manager.acquire_concurrent_slot() is True
        
        # Try to acquire another (will timeout)
        result = self.budget_manager.acquire_concurrent_slot(timeout=0.1)
        assert result is False
        
        # Release the original slot
        self.budget_manager.release_concurrent_slot()
        
        # Should now be able to acquire
        result = self.budget_manager.acquire_concurrent_slot(timeout=0.1)
        assert result is True
        
        # Clean up
        self.budget_manager.release_concurrent_slot()
    
    def test_concurrent_slot_over_release_handling(self):
        """Test graceful handling of releasing more slots than acquired."""
        # Try to release without acquiring
        self.budget_manager.release_concurrent_slot()
        
        # Should not crash and usage should remain valid
        usage = self.budget_manager.current_usage()
        assert usage['active_concurrent'] == 0
        
        # Acquire and release normally
        assert self.budget_manager.acquire_concurrent_slot() is True
        self.budget_manager.release_concurrent_slot()
        
        # Usage should still be valid
        usage = self.budget_manager.current_usage()
        assert usage['active_concurrent'] == 0
    
    def test_concurrent_slot_semaphore_corruption_resilience(self):
        """Test resilience against semaphore corruption scenarios."""
        # Acquire and release multiple times rapidly
        for _ in range(100):
            acquired = self.budget_manager.acquire_concurrent_slot(timeout=0.01)
            if acquired:
                self.budget_manager.release_concurrent_slot()
        
        # Final state should be consistent
        usage = self.budget_manager.current_usage()
        assert usage['active_concurrent'] == 0
        
        # Should still be able to acquire slots normally
        assert self.budget_manager.acquire_concurrent_slot(timeout=0.1) is True
        self.budget_manager.release_concurrent_slot()
    
    def test_executor_failure_with_thread_safety(self):
        """Test executor failure scenarios under concurrent load."""
        results = []
        errors = []
        
        def worker(worker_id):
            try:
                for i in range(10):
                    # Try to acquire slot with short timeout
                    acquired = self.budget_manager.acquire_concurrent_slot(timeout=0.01)
                    if acquired:
                        # Simulate brief work
                        time.sleep(0.001)
                        self.budget_manager.release_concurrent_slot()
                        results.append(f"worker_{worker_id}_success_{i}")
                    else:
                        results.append(f"worker_{worker_id}_timeout_{i}")
            except Exception as e:
                errors.append((worker_id, e))
        
        # Run many threads competing for limited slots
        threads = []
        for i in range(20):  # More workers than slots
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Verify no crashes
        assert len(errors) == 0
        assert len(results) > 0
        
        # Final state should be clean
        usage = self.budget_manager.current_usage()
        assert usage['active_concurrent'] == 0
    
    def test_orchestrator_executor_timeout_integration(self):
        """Test orchestrator integration with executor timeout."""
        # Create orchestrator with very short timeout
        config = {
            "executor_timeout": 0.01,  # Very short timeout
            "max_parallel": 1
        }
        
        orchestrator = OutreachOrchestrator(config=config)
        
        # Mock a scenario that requires concurrent execution
        # Test the timeout integration point
        timeout = orchestrator.budget_manager.get_limits()['executor_timeout']
        assert timeout == 0.01
        
        # Test slot acquisition with timeout
        acquired = orchestrator.budget_manager.acquire_concurrent_slot(timeout=timeout)
        assert acquired is True
        
        # Try to acquire another - should timeout
        second_acquired = orchestrator.budget_manager.acquire_concurrent_slot(timeout=timeout)
        assert second_acquired is False
        
        # Clean up
        orchestrator.budget_manager.release_concurrent_slot()
    
    def test_executor_failure_recovery_mechanisms(self):
        """Test recovery mechanisms after executor failures."""
        # Simulate various failure scenarios and verify recovery
        
        # 1. Timeout recovery
        assert self.budget_manager.acquire_concurrent_slot() is True
        assert self.budget_manager.acquire_concurrent_slot(timeout=0.01) is False
        
        # Should recover after releasing
        self.budget_manager.release_concurrent_slot()
        assert self.budget_manager.acquire_concurrent_slot(timeout=0.01) is True
        self.budget_manager.release_concurrent_slot()
        
        # 2. State consistency recovery
        usage_before = self.budget_manager.current_usage()
        assert usage_before['active_concurrent'] == 0
        
        # 3. Budget state should be unaffected by executor failures
        budget_before = self.budget_manager.check_budget("test")
        assert budget_before is True
        
        # After timeout scenarios, budget should still work
        budget_after = self.budget_manager.check_budget("test")
        assert budget_after is True
    
    def test_executor_failure_with_budget_integration(self):
        """Test executor failures alongside budget constraints."""
        # Configure both low parallel and low token limits
        self.budget_manager.configure(BudgetLimits(
            max_parallel=1,
            max_tokens=100,
            executor_timeout=0.01
        ))
        
        # Use up token budget
        self.budget_manager.record_tokens("test", 100)
        
        # Should fail due to budget, not executor
        budget_ok = self.budget_manager.check_budget("test")
        assert budget_ok is False
        
        # But executor slots should still work independently
        acquired = self.budget_manager.acquire_concurrent_slot(timeout=0.01)
        assert acquired is True
        self.budget_manager.release_concurrent_slot()
    
    def test_executor_failure_error_propagation(self):
        """Test that executor failures don't cause unhandled exceptions."""
        # Test various edge cases that might cause exceptions
        
        # 1. Invalid timeout values
        try:
            self.budget_manager.acquire_concurrent_slot(timeout=None)
        except Exception as e:
            # Should handle gracefully or raise sensible error
            assert not isinstance(e, UnboundLocalError)
        
        # 2. Very large timeout values
        try:
            self.budget_manager.acquire_concurrent_slot(timeout=10**6)
        except Exception as e:
            # Should handle gracefully
            assert not isinstance(e, OverflowError)
        
        # 3. Release operations
        try:
            self.budget_manager.release_concurrent_slot()
            self.budget_manager.release_concurrent_slot()
            self.budget_manager.release_concurrent_slot()
        except Exception as e:
            # Should handle over-release gracefully
            assert not isinstance(e, ValueError)
    
    def test_executor_failure_performance_degradation(self):
        """Test performance under executor failure conditions."""
        import time
        
        # Measure performance with many timeout scenarios
        start_time = time.time()
        
        # Acquire all slots
        for _ in range(5):
            self.budget_manager.acquire_concurrent_slot()
        
        # Try many acquisitions that will timeout
        timeout_count = 0
        for _ in range(100):
            acquired = self.budget_manager.acquire_concurrent_slot(timeout=0.001)
            if not acquired:
                timeout_count += 1
        
        # Release all slots
        for _ in range(5):
            self.budget_manager.release_concurrent_slot()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete in reasonable time despite timeouts
        assert duration < 5.0, f"Executor failure performance too slow: {duration}s"
        assert timeout_count > 90  # Most should have timed out
    
    def test_executor_failure_resource_cleanup(self):
        """Test proper resource cleanup after executor failures."""
        # Get initial state
        initial_usage = self.budget_manager.current_usage()
        
        # Simulate failure scenarios
        for _ in range(10):
            # Acquire and timeout attempts
            acquired = self.budget_manager.acquire_concurrent_slot(timeout=0.001)
            if acquired:
                self.budget_manager.release_concurrent_slot()
        
        # Force some over-releases
        for _ in range(5):
            self.budget_manager.release_concurrent_slot()
        
        # Final state should be clean
        final_usage = self.budget_manager.current_usage()
        assert final_usage['active_concurrent'] == 0
        assert final_usage['active_concurrent'] >= 0  # Should not be negative
        
        # Should still be able to acquire slots normally
        assert self.budget_manager.acquire_concurrent_slot(timeout=0.1) is True
        self.budget_manager.release_concurrent_slot()
    
    def test_executor_failure_with_async_context(self):
        """Test executor failure in async context."""
        async def async_worker():
            # Test concurrent slot acquisition in async context
            acquired = self.budget_manager.acquire_concurrent_slot(timeout=0.01)
            if acquired:
                await asyncio.sleep(0.001)  # Simulate async work
                self.budget_manager.release_concurrent_slot()
                return True
            return False
        
        # Run async workers
        async def run_async_test():
            tasks = [async_worker() for _ in range(10)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Verify no exceptions and some successes
            exceptions = [r for r in results if isinstance(r, Exception)]
            successes = [r for r in results if r is True]
            failures = [r for r in results if r is False]
            
            assert len(exceptions) == 0
            assert len(successes) > 0
            assert len(failures) > 0  # Some should timeout
            
            return len(successes), len(failures)
        
        # Run the async test
        success_count, failure_count = asyncio.run(run_async_test())
        
        # Verify reasonable distribution
        assert success_count + failure_count == 10
        assert success_count <= 5  # Can't exceed parallel limit
