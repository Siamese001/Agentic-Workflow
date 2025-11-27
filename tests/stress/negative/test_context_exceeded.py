"""
Phase 9 Negative Path Tests - Context Exceeded

Tests graceful failure handling when context size limits are exceeded
across all orchestration paths and large content scenarios.
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


class TestContextExceeded:
    """Test context size exceeded scenarios and graceful failure handling."""
    
    def setup_method(self):
        """Setup fresh budget manager for each test."""
        # Clear singleton to ensure clean state
        ExecutionBudgetManager._instance = None
        self.budget_manager = get_budget_manager()
        self.budget_manager.reset_usage()
        
        # Configure very low context limits for testing
        self.low_context_limits = BudgetLimits(max_context_size=1000)
        self.budget_manager.configure(self.low_context_limits)
    
    def test_context_size_within_limit_success(self):
        """Test that context size check passes when within limit."""
        result = self.budget_manager.check_context_size(500)
        
        assert result is True
    
    def test_context_size_exceeds_limit_failure(self):
        """Test that context size check fails when limit exceeded."""
        result = self.budget_manager.check_context_size(2000)
        
        assert result is False
    
    def test_context_size_exact_limit_boundary(self):
        """Test context size check at exact limit boundary."""
        # Should pass at exact limit
        result = self.budget_manager.check_context_size(1000)
        assert result is True
        
        # Should fail just over limit
        result = self.budget_manager.check_context_size(1001)
        assert result is False
    
    def test_context_size_zero_limit(self):
        """Test behavior when context size limit is zero."""
        # Configure zero context limit
        self.budget_manager.configure(BudgetLimits(max_context_size=0))
        
        # Any context size should fail except zero
        assert self.budget_manager.check_context_size(0) is True
        assert self.budget_manager.check_context_size(1) is False
        assert self.budget_manager.check_context_size(100) is False
    
    def test_context_size_negative_input(self):
        """Test context size check with negative input."""
        # Negative context size should be treated as within limit
        # (graceful handling of edge cases)
        result = self.budget_manager.check_context_size(-100)
        
        assert result is True  # Should handle gracefully
    
        
    def test_context_size_configuration_change_runtime(self):
        """Test changing context size limits during runtime."""
        # Start with low limit
        self.budget_manager.configure(BudgetLimits(max_context_size=100))
        
        # Should fail with larger context
        assert self.budget_manager.check_context_size(200) is False
        
        # Increase limit
        self.budget_manager.configure(BudgetLimits(max_context_size=500))
        
        # Should now pass
        assert self.budget_manager.check_context_size(200) is True
        
        # But still fail with even larger context
        assert self.budget_manager.check_context_size(600) is False
    
    def test_context_size_large_document_scenarios(self):
        """Test context size with realistic large document scenarios."""
        # Simulate different document sizes
        scenarios = {
            "short_message": 100,
            "medium_email": 2000,
            "long_report": 50000,
            "huge_document": 1000000
        }
        
        # Test each scenario
        for scenario_name, size in scenarios.items():
            result = self.budget_manager.check_context_size(size)
            
            if size <= 1000:  # Our test limit
                assert result is True, f"{scenario_name} should pass"
            else:
                assert result is False, f"{scenario_name} should fail"
    
    def test_context_size_concurrent_operations(self):
        """Test context size checking under concurrent operations."""
        results = []
        errors = []
        
        def worker(worker_id):
            try:
                # Each worker checks different context sizes
                context_sizes = [500, 1500, 2500, 3500, 4500]
                
                for size in context_sizes:
                    result = self.budget_manager.check_context_size(size)
                    results.append({
                        'worker_id': worker_id,
                        'context_size': size,
                        'allowed': result
                    })
            except Exception as e:
                errors.append((worker_id, e))
        
        # Run multiple threads checking context sizes
        import threading
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Verify no crashes and consistent results
        assert len(errors) == 0
        assert len(results) == 25  # 5 workers * 5 context sizes
        
        # All small contexts should be allowed, all large should be denied
        for result in results:
            if result['context_size'] <= 1000:
                assert result['allowed'] is True
            else:
                assert result['allowed'] is False
    
    def test_context_size_memory_efficiency(self):
        """Test that context size checking doesn't consume excessive memory."""
        # Test with very large size numbers
        large_sizes = [10**6, 10**7, 10**8, 10**9]
        
        for size in large_sizes:
            # Should not crash or consume excessive memory
            result = self.budget_manager.check_context_size(size)
            assert result is False  # All should exceed our 1000 limit
    
    def test_context_size_with_unicode_content(self):
        """Test context size with Unicode content (multi-byte characters)."""
        # Unicode content might have different byte vs character length
        unicode_text = "🚀" * 100  # Rocket emoji repeated
        ascii_text = "A" * 100
        
        # Test both types - should work the same way
        unicode_result = self.budget_manager.check_context_size(len(unicode_text))
        ascii_result = self.budget_manager.check_context_size(len(ascii_text))
        
        # Both should have same result since we check character length
        assert unicode_result == ascii_result
    
    def test_context_size_integration_with_other_limits(self):
        """Test context size checking alongside other budget limits."""
        # Configure multiple low limits
        self.budget_manager.configure(BudgetLimits(
            max_context_size=1000,
            max_tokens=500,
            max_requests=2
        ))
        
        # Use up other budget limits
        self.budget_manager.record_tokens("test", 600)  # Exceed token limit
        
        # Context size should still be checked independently
        context_result = self.budget_manager.check_context_size(500)
        budget_result = self.budget_manager.check_budget("test")
        
        # Context check should pass (within limit)
        assert context_result is True
        
        # Overall budget should fail (due to tokens)
        assert budget_result is False
    
    def test_context_size_error_handling_edge_cases(self):
        """Test context size error handling with edge cases."""
        edge_cases = [
            None,  # None input
            "not_a_number",  # String input
            [],  # List input
            {},  # Dict input
        ]
        
        for case in edge_cases:
            try:
                # Should handle gracefully or raise appropriate error
                result = self.budget_manager.check_context_size(case)
                # If it doesn't crash, that's acceptable behavior
            except (TypeError, ValueError):
                # Expected error types for invalid input
                pass
            except Exception as e:
                pytest.fail(f"Unexpected error for case {case}: {e}")
    
    def test_context_size_performance_under_load(self):
        """Test context size checking performance under high load."""
        import time
        
        # Measure performance of many context size checks
        start_time = time.time()
        
        for i in range(10000):
            # Mix of different sizes
            size = i % 2000
            self.budget_manager.check_context_size(size)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete quickly (less than 1 second for 10k checks)
        assert duration < 1.0, f"Context size checks too slow: {duration}s"
    
    def test_context_size_state_isolation(self):
        """Test that context size checking doesn't affect other budget state."""
        # Get initial state
        initial_usage = self.budget_manager.current_usage()
        
        # Perform many context size checks
        for i in range(100):
            self.budget_manager.check_context_size(i * 10)
        
        # State should be unchanged (context checking doesn't modify usage)
        final_usage = self.budget_manager.current_usage()
        
        assert initial_usage['tokens_used'] == final_usage['tokens_used']
        assert initial_usage['requests_made'] == final_usage['requests_made']
        assert initial_usage['current_depth'] == final_usage['current_depth']
