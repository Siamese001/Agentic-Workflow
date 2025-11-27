"""
Phase 9 Negative Path Tests - Depth Exceeded

Tests graceful failure handling when recursion depth limits are exceeded
across all orchestration paths and meta-loop scenarios.
"""

import pytest
import asyncio
from typing import Dict, Any

from runtime.execution_budget_manager import (
    ExecutionBudgetManager,
    BudgetLimits,
    get_budget_manager
)
from l3.outreach_orchestrator import OutreachOrchestrator


class TestDepthExceeded:
    """Test depth exceeded scenarios and graceful failure handling."""
    
    def setup_method(self):
        """Setup fresh budget manager for each test."""
        # Clear singleton to ensure clean state
        ExecutionBudgetManager._instance = None
        self.budget_manager = get_budget_manager()
        self.budget_manager.reset_usage()
        
        # Configure very low depth limits for testing
        self.low_depth_limits = BudgetLimits(max_depth=2)
        self.budget_manager.configure(self.low_depth_limits)
    
    def test_depth_increment_exceeds_limit_graceful_failure(self):
        """Test that depth increment fails gracefully when limit exceeded."""
        # Increment to max depth
        assert self.budget_manager.increment_depth("test_operation") is True
        assert self.budget_manager.increment_depth("test_operation") is True
        
        # Try to increment beyond limit
        result = self.budget_manager.increment_depth("test_operation")
        
        # Should fail gracefully, not crash
        assert result is False
        
        # Verify depth is still at max
        usage = self.budget_manager.current_usage()
        assert usage['current_depth'] == 2
        assert usage['budget_exceeded']['depth'] is True
    
    def test_depth_check_prevents_stage_start(self):
        """Test that budget check prevents stage start when depth exceeded."""
        # Increment to max depth
        self.budget_manager.increment_depth("test_operation")
        self.budget_manager.increment_depth("test_operation")
        
        # Try to start new stage
        result = self.budget_manager.check_budget("new_stage")
        
        # Should fail due to depth exceeded
        assert result is False
        
        # Verify reason is depth exceeded
        reason = self.budget_manager.get_budget_exceeded_reason()
        assert reason == "Recursion depth exceeded"
    
    def test_depth_decrement_restores_functionality(self):
        """Test that depth decrement restores ability to increment."""
        # Increment to max depth
        self.budget_manager.increment_depth("test_operation")
        self.budget_manager.increment_depth("test_operation")
        
        # Verify we can't increment further
        assert self.budget_manager.increment_depth("test_operation") is False
        
        # Decrement one level
        self.budget_manager.decrement_depth("test_operation")
        
        # Should be able to increment again
        assert self.budget_manager.increment_depth("test_operation") is True
        
        # But not beyond limit again
        assert self.budget_manager.increment_depth("test_operation") is False
    
    def test_depth_tracking_across_multiple_operations(self):
        """Test depth tracking across different operation types."""
        # Increment depth for different operations
        self.budget_manager.increment_depth("operation_a")
        self.budget_manager.increment_depth("operation_b")
        
        # Should be at max depth
        usage = self.budget_manager.current_usage()
        assert usage['current_depth'] == 2
        
        # Any operation should fail to increment
        assert self.budget_manager.increment_depth("operation_c") is False
        
        # Decrement from any operation should work
        self.budget_manager.decrement_depth("operation_c")  # Even though it didn't increment
        
        usage = self.budget_manager.current_usage()
        assert usage['current_depth'] == 1
    
        
    def test_concurrent_operations_depth_isolation(self):
        """Test that depth tracking works correctly under concurrent operations."""
        results = []
        errors = []
        
        def worker(worker_id):
            try:
                # Each worker tries to increment depth
                depth_ok = self.budget_manager.increment_depth(f"worker_{worker_id}")
                if depth_ok:
                    # Simulate some work
                    import time
                    time.sleep(0.01)
                    self.budget_manager.decrement_depth(f"worker_{worker_id}")
                    results.append(f"worker_{worker_id}_success")
                else:
                    results.append(f"worker_{worker_id}_depth_exceeded")
            except Exception as e:
                errors.append((worker_id, e))
        
        # Run multiple threads trying to use depth
        import threading
        threads = []
        for i in range(10):  # More workers than depth limit
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Verify no crashes and some operations succeeded
        assert len(errors) == 0
        assert len(results) == 10
        
        # Some should have succeeded, some failed due to depth
        successes = [r for r in results if "_success" in r]
        failures = [r for r in results if "_depth_exceeded" in r]
        
        assert len(successes) > 0
        assert len(failures) > 0
        
        # Final depth should be 0 (all properly decremented)
        usage = self.budget_manager.current_usage()
        assert usage['current_depth'] == 0
    
    def test_depth_exceeded_error_message_consistency(self):
        """Test that depth exceeded error messages are consistent."""
        # Exceed depth limit
        self.budget_manager.increment_depth("test")
        self.budget_manager.increment_depth("test")
        
        # Check various error reporting methods
        reason = self.budget_manager.get_budget_exceeded_reason()
        usage = self.budget_manager.current_usage()
        
        assert reason == "Recursion depth exceeded"
        assert usage['budget_exceeded']['depth'] is True
        assert usage['current_depth'] == 2
        assert usage['max_depth'] == 2
    
    def test_depth_limit_configuration_change_runtime(self):
        """Test changing depth limits during runtime."""
        # Start with low limit
        self.budget_manager.configure(BudgetLimits(max_depth=1))
        
        # Increment to limit
        assert self.budget_manager.increment_depth("test") is True
        assert self.budget_manager.increment_depth("test") is False
        
        # Increase limit
        self.budget_manager.configure(BudgetLimits(max_depth=3))
        
        # Should now be able to increment further
        assert self.budget_manager.increment_depth("test") is True
        assert self.budget_manager.increment_depth("test") is True
        assert self.budget_manager.increment_depth("test") is False
        
        # Clean up
        for _ in range(3):
            self.budget_manager.decrement_depth("test")
    
    def test_depth_exceeded_with_zero_limit(self):
        """Test behavior when depth limit is set to zero."""
        # Configure zero depth limit
        self.budget_manager.configure(BudgetLimits(max_depth=0))
        
        # Any depth increment should fail
        result = self.budget_manager.increment_depth("test")
        assert result is False
        
        # Budget check should also fail
        budget_ok = self.budget_manager.check_budget("test")
        assert budget_ok is False
        
        # Reason should be depth exceeded
        reason = self.budget_manager.get_budget_exceeded_reason()
        assert reason == "Recursion depth exceeded"
    
    def test_depth_exceeded_meta_loop_scenario(self):
        """Test depth exceeded in meta-loop fallback scenario."""
        # Simulate meta-loop behavior with multiple attempts
        max_attempts = 5
        successful_attempts = 0
        
        for attempt in range(max_attempts):
            # Check if we can start a new attempt
            if self.budget_manager.check_budget(f"meta_attempt_{attempt}"):
                if self.budget_manager.increment_depth(f"meta_attempt_{attempt}"):
                    successful_attempts += 1
                    # Simulate some work
                    pass
                    # Don't decrement - we want to test depth accumulation
            else:
                # Should stop when depth exceeded
                break
        
        # Should have limited successful attempts due to depth constraint
        assert successful_attempts <= 2  # Our max depth limit
        
        # Clean up depth after test
        for _ in range(successful_attempts):
            self.budget_manager.decrement_depth("cleanup")
        
        # Final state should be clean
        usage = self.budget_manager.current_usage()
        assert usage['current_depth'] == 0
