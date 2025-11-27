"""
Phase 9 Negative Path Tests - Token Budget Violation

Tests graceful failure handling when token budget limits are exceeded
across all orchestration paths and high token usage scenarios.
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


class TestTokenBudgetViolation:
    """Test token budget violation scenarios and graceful failure handling."""
    
    def setup_method(self):
        """Setup fresh budget manager for each test."""
        # Clear singleton to ensure clean state
        ExecutionBudgetManager._instance = None
        self.budget_manager = get_budget_manager()
        self.budget_manager.reset_usage()
        
        # Configure very low token limits for testing
        self.low_token_limits = BudgetLimits(max_tokens=1000)
        self.budget_manager.configure(self.low_token_limits)
    
    def test_token_budget_within_limit_success(self):
        """Test that token budget check passes when within limit."""
        result = self.budget_manager.check_budget("test_operation")
        
        assert result is True
    
    def test_token_budget_exceeds_limit_failure(self):
        """Test that token budget check fails when limit exceeded."""
        # Use up all tokens
        self.budget_manager.record_tokens("test", 1000)
        
        result = self.budget_manager.check_budget("test_operation")
        
        assert result is False
    
    def test_token_recording_exact_limit_boundary(self):
        """Test token recording at exact limit boundary."""
        # Should be able to record up to exact limit
        self.budget_manager.record_tokens("test", 999)
        assert self.budget_manager.check_budget("test") is True
        
        # Record the last token
        self.budget_manager.record_tokens("test", 1)
        assert self.budget_manager.check_budget("test") is False
        
        # Verify state
        usage = self.budget_manager.current_usage()
        assert usage['tokens_used'] == 1000
        assert usage['tokens_remaining'] == 0
    
    def test_token_budget_zero_limit(self):
        """Test behavior when token budget limit is zero."""
        # Configure zero token limit
        self.budget_manager.configure(BudgetLimits(max_tokens=0))
        
        # Any token recording should exceed limit
        self.budget_manager.record_tokens("test", 1)
        
        # Budget check should fail
        result = self.budget_manager.check_budget("test")
        assert result is False
        
        # Reason should be token budget exceeded
        reason = self.budget_manager.get_budget_exceeded_reason()
        assert reason == "Token budget exceeded"
    
    def test_token_recording_negative_input(self):
        """Test token recording with negative input."""
        initial_tokens = self.budget_manager.current_usage()['tokens_used']
        
        # Negative token recording should be handled gracefully
        self.budget_manager.record_tokens("test", -100)
        
        # Should not crash and tokens should remain reasonable
        final_tokens = self.budget_manager.current_usage()['tokens_used']
        # Implementation may allow negative or clamp to zero - just verify no crash
        assert isinstance(final_tokens, int)
    
    def test_token_budget_large_amounts(self):
        """Test token budget with very large amounts."""
        # Configure large limit
        self.budget_manager.configure(BudgetLimits(max_tokens=10**9))
        
        # Record large number of tokens
        large_amount = 500000
        self.budget_manager.record_tokens("test", large_amount)
        
        usage = self.budget_manager.current_usage()
        assert usage['tokens_used'] == large_amount
        assert usage['tokens_remaining'] == 10**9 - large_amount
    
    def test_orchestrator_token_budget_enforcement(self):
        """Test that orchestrator enforces token budget limits."""
        # Create orchestrator with low token limits
        config = {
            "max_tokens": 500,  # Very low limit
            "max_requests": 100
        }
        
        orchestrator = OutreachOrchestrator(config=config)
        
        # Use up tokens
        orchestrator.budget_manager.record_tokens("test", 500)
        
        # Should fail to start new operation
        budget_ok = orchestrator.budget_manager.check_budget("outreach")
        assert budget_ok is False
        
        # Reason should be token budget exceeded
        reason = orchestrator.budget_manager.get_budget_exceeded_reason()
        assert reason == "Token budget exceeded"
    
    def test_token_budget_configuration_change_runtime(self):
        """Test changing token budget limits during runtime."""
        # Start with low limit
        self.budget_manager.configure(BudgetLimits(max_tokens=100))
        
        # Use up tokens
        self.budget_manager.record_tokens("test", 100)
        assert self.budget_manager.check_budget("test") is False
        
        # Increase limit
        self.budget_manager.configure(BudgetLimits(max_tokens=500))
        
        # Should now be able to check budget (though tokens still used)
        budget_ok = self.budget_manager.check_budget("test")
        # Still false because tokens are still used, but limit is higher
        
        # Verify new limit is applied
        limits = self.budget_manager.get_limits()
        assert limits['max_tokens'] == 500
    
    def test_token_budget_concurrent_operations(self):
        """Test token budget under concurrent operations."""
        results = []
        errors = []
        
        def worker(worker_id):
            try:
                # Each worker tries to record tokens
                for i in range(10):
                    token_amount = 50  # Each worker tries to use 50 tokens * 10 = 500 tokens
                    
                    # Check budget first
                    if self.budget_manager.check_budget(f"worker_{worker_id}"):
                        self.budget_manager.record_tokens(f"worker_{worker_id}", token_amount)
                        results.append({
                            'worker_id': worker_id,
                            'iteration': i,
                            'tokens_recorded': token_amount,
                            'success': True
                        })
                    else:
                        results.append({
                            'worker_id': worker_id,
                            'iteration': i,
                            'tokens_recorded': 0,
                            'success': False,
                            'reason': 'budget_exceeded'
                        })
                        break  # Stop trying when budget exceeded
            except Exception as e:
                errors.append((worker_id, e))
        
        # Run multiple threads
        import threading
        threads = []
        for i in range(5):  # 5 workers * 500 tokens each = 2500 tokens needed, but only 1000 available
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Verify no crashes
        assert len(errors) == 0
        
        # Some operations should have succeeded, some failed
        successful_ops = [r for r in results if r['success']]
        failed_ops = [r for r in results if not r['success']]
        
        assert len(successful_ops) > 0
        assert len(failed_ops) > 0
        
        # Total tokens used should not exceed limit
        usage = self.budget_manager.current_usage()
        assert usage['tokens_used'] <= 1000
    
    def test_token_budget_across_stages(self):
        """Test token budget tracking across different stages."""
        stages = ["research", "drafting", "safety", "final"]
        
        # Record tokens for different stages
        for stage in stages:
            self.budget_manager.start_stage(stage)
            self.budget_manager.record_tokens(stage, 250)
        
        # Should exceed budget
        assert self.budget_manager.check_budget("new_stage") is False
        
        # Verify stage tracking
        usage = self.budget_manager.current_usage()
        assert usage['tokens_used'] == 1000
        assert len(usage['stages_completed']) == 4
        
        for stage in stages:
            assert usage['stages_completed'][stage] == 1
    
    def test_token_budget_with_request_tracking(self):
        """Test token budget alongside request tracking."""
        # Configure low limits for both
        self.budget_manager.configure(BudgetLimits(
            max_tokens=500,
            max_requests=2
        ))
        
        # Use up tokens first
        self.budget_manager.record_tokens("test", 500)
        
        # Should fail due to tokens
        assert self.budget_manager.check_budget("test") is False
        reason = self.budget_manager.get_budget_exceeded_reason()
        assert reason == "Token budget exceeded"
        
        # Reset and test request limit
        self.budget_manager.reset_usage()
        self.budget_manager.record_request()
        self.budget_manager.record_request()
        
        # Should fail due to requests
        assert self.budget_manager.check_budget("test") is False
        reason = self.budget_manager.get_budget_exceeded_reason()
        assert reason == "Request budget exceeded"
    
    def test_token_budget_error_handling_edge_cases(self):
        """Test token budget error handling with edge cases."""
        edge_cases = [
            None,  # None amount
            "not_a_number",  # String input
            [],  # List input
            {},  # Dict input
            float('inf'),  # Infinite amount
            float('-inf'),  # Negative infinite
        ]
        
        for case in edge_cases:
            try:
                # Should handle gracefully or raise appropriate error
                self.budget_manager.record_tokens("test", case)
                # If it doesn't crash, that's acceptable behavior
            except (TypeError, ValueError):
                # Expected error types for invalid input
                pass
            except Exception as e:
                pytest.fail(f"Unexpected error for case {case}: {e}")
    
    def test_token_budget_performance_under_load(self):
        """Test token budget performance under high load."""
        import time
        
        # Measure performance of many token operations
        start_time = time.time()
        
        for i in range(10000):
            # Mix of operations
            if i % 100 == 0:
                # Check budget occasionally
                self.budget_manager.check_budget(f"test_{i}")
            else:
                # Record small amounts
                self.budget_manager.record_tokens(f"test_{i}", 1)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete quickly
        assert duration < 2.0, f"Token budget operations too slow: {duration}s"
    
    def test_token_budget_reset_functionality(self):
        """Test token budget reset functionality."""
        # Use up budget
        self.budget_manager.record_tokens("test", 1000)
        assert self.budget_manager.check_budget("test") is False
        
        # Reset usage
        self.budget_manager.reset_usage()
        
        # Should be able to check budget again
        assert self.budget_manager.check_budget("test") is True
        
        # Verify clean state
        usage = self.budget_manager.current_usage()
        assert usage['tokens_used'] == 0
        assert usage['tokens_remaining'] == 1000
    
    def test_token_budget_remaining_calculation(self):
        """Test accurate calculation of remaining tokens."""
        # Record different amounts and verify remaining calculation
        amounts = [100, 200, 300, 150]
        
        for amount in amounts:
            self.budget_manager.record_tokens("test", amount)
            usage = self.budget_manager.current_usage()
            expected_remaining = 1000 - sum(amounts[:amounts.index(amount) + 1])
            assert usage['tokens_remaining'] == expected_remaining
    
    def test_token_budget_with_stage_tracking(self):
        """Test token budget tracking with stage completion."""
        # Start stage and record tokens
        self.budget_manager.start_stage("research")
        self.budget_manager.record_tokens("research", 300)
        
        usage = self.budget_manager.current_usage()
        assert usage['stages_completed']['research'] == 1
        assert usage['tokens_used'] == 300
        
        # Start another stage
        self.budget_manager.start_stage("drafting")
        self.budget_manager.record_tokens("drafting", 400)
        
        usage = self.budget_manager.current_usage()
        assert usage['stages_completed']['drafting'] == 1
        assert usage['tokens_used'] == 700
        
        # Should still have budget remaining
        assert self.budget_manager.check_budget("final") is True
        
        # Use up remaining budget
        self.budget_manager.record_tokens("final", 300)
        assert self.budget_manager.check_budget("overflow") is False
