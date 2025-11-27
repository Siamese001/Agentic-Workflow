"""
Phase 9 Unit Tests for ExecutionBudgetManager

Comprehensive unit tests for budget tracking, limits enforcement, and
resource management across all ExecutionBudgetManager functionality.
"""

import pytest
import threading
import time
from typing import Dict, Any

from runtime.execution_budget_manager import (
    ExecutionBudgetManager,
    BudgetUsage,
    BudgetLimits,
    get_budget_manager,
    create_budget_limits_from_config
)


class TestExecutionBudgetManagerUnit:
    """Unit tests for ExecutionBudgetManager core functionality."""
    
    def setup_method(self):
        """Setup fresh budget manager for each test."""
        # Clear singleton to ensure clean state
        ExecutionBudgetManager._instance = None
        self.budget_manager = ExecutionBudgetManager()
        self.budget_manager.reset_usage()
    
    def test_singleton_pattern(self):
        """Test that ExecutionBudgetManager follows singleton pattern."""
        manager1 = ExecutionBudgetManager()
        manager2 = ExecutionBudgetManager()
        
        assert manager1 is manager2
        assert id(manager1) == id(manager2)
    
    def test_global_get_budget_manager(self):
        """Test global get_budget_manager function."""
        manager1 = get_budget_manager()
        manager2 = get_budget_manager()
        
        assert manager1 is manager2
        assert isinstance(manager1, ExecutionBudgetManager)
    
    def test_budget_limits_defaults(self):
        """Test default budget limits configuration."""
        limits = BudgetLimits()
        
        assert limits.max_tokens == 1000000
        assert limits.max_requests == 1000
        assert limits.max_depth == 10
        assert limits.max_parallel == 5
        assert limits.max_context_size == 500000
        assert limits.max_message_length == 10000
        assert limits.executor_timeout == 30.0
    
    def test_budget_usage_initialization(self):
        """Test budget usage starts with clean state."""
        usage = BudgetUsage()
        
        assert usage.tokens_used == 0
        assert usage.requests_made == 0
        assert usage.current_depth == 0
        assert usage.active_concurrent == 0
        assert usage.stages_completed == {}
        assert usage.last_activity > 0
    
    def test_configure_budget_limits(self):
        """Test budget limits configuration."""
        new_limits = BudgetLimits(
            max_tokens=500000,
            max_requests=500,
            max_depth=5,
            max_parallel=3
        )
        
        self.budget_manager.configure(new_limits)
        
        retrieved_limits = self.budget_manager.get_limits()
        assert retrieved_limits['max_tokens'] == 500000
        assert retrieved_limits['max_requests'] == 500
        assert retrieved_limits['max_depth'] == 5
        assert retrieved_limits['max_parallel'] == 3
    
    def test_start_stage_success(self):
        """Test successful stage start with available budget."""
        result = self.budget_manager.start_stage("test_stage")
        
        assert result is True
        
        usage = self.budget_manager.current_usage()
        assert usage['stages_completed']['test_stage'] == 1
    
    def test_start_stage_multiple_calls(self):
        """Test multiple calls to start_stage increment counter."""
        self.budget_manager.start_stage("test_stage")
        self.budget_manager.start_stage("test_stage")
        self.budget_manager.start_stage("test_stage")
        
        usage = self.budget_manager.current_usage()
        assert usage['stages_completed']['test_stage'] == 3
    
    def test_start_stage_different_stages(self):
        """Test starting different stages tracks them separately."""
        self.budget_manager.start_stage("stage_a")
        self.budget_manager.start_stage("stage_b")
        self.budget_manager.start_stage("stage_a")
        
        usage = self.budget_manager.current_usage()
        assert usage['stages_completed']['stage_a'] == 2
        assert usage['stages_completed']['stage_b'] == 1
    
    def test_check_budget_available(self):
        """Test budget check when resources are available."""
        result = self.budget_manager.check_budget("test_operation")
        
        assert result is True
    
    def test_check_budget_token_limit_exceeded(self):
        """Test budget check when token limit is exceeded."""
        # Configure very low token limit
        limits = BudgetLimits(max_tokens=10)
        self.budget_manager.configure(limits)
        
        # Use all tokens
        self.budget_manager.record_tokens("test", 10)
        
        result = self.budget_manager.check_budget("test_operation")
        
        assert result is False
    
    def test_check_budget_request_limit_exceeded(self):
        """Test budget check when request limit is exceeded."""
        # Configure very low request limit
        limits = BudgetLimits(max_requests=1)
        self.budget_manager.configure(limits)
        
        # Use all requests
        self.budget_manager.record_request()
        
        result = self.budget_manager.check_budget("test_operation")
        
        assert result is False
    
    def test_check_budget_depth_limit_exceeded(self):
        """Test budget check when depth limit is exceeded."""
        # Configure very low depth limit
        limits = BudgetLimits(max_depth=1)
        self.budget_manager.configure(limits)
        
        # Use all depth
        self.budget_manager.increment_depth("test")
        
        result = self.budget_manager.check_budget("test_operation")
        
        assert result is False
    
    def test_acquire_concurrent_slot_success(self):
        """Test successful concurrent slot acquisition."""
        result = self.budget_manager.acquire_concurrent_slot()
        
        assert result is True
        
        usage = self.budget_manager.current_usage()
        assert usage['active_concurrent'] == 1
    
    def test_acquire_concurrent_slot_limit_exceeded(self):
        """Test concurrent slot acquisition when limit exceeded."""
        # Configure single slot limit
        limits = BudgetLimits(max_parallel=1)
        self.budget_manager.configure(limits)
        
        # Acquire the only available slot
        assert self.budget_manager.acquire_concurrent_slot() is True
        
        # Try to acquire second slot (should fail)
        assert self.budget_manager.acquire_concurrent_slot(timeout=0.1) is False
    
    def test_release_concurrent_slot(self):
        """Test concurrent slot release."""
        # Acquire and release slot
        self.budget_manager.acquire_concurrent_slot()
        usage_before = self.budget_manager.current_usage()
        assert usage_before['active_concurrent'] == 1
        
        self.budget_manager.release_concurrent_slot()
        usage_after = self.budget_manager.current_usage()
        assert usage_after['active_concurrent'] == 0
    
    def test_release_concurrent_slot_over_release(self):
        """Test releasing more slots than acquired (graceful handling)."""
        # Try to release without acquiring (should not crash)
        self.budget_manager.release_concurrent_slot()
        
        usage = self.budget_manager.current_usage()
        assert usage['active_concurrent'] == 0
    
    def test_record_tokens(self):
        """Test token usage recording."""
        self.budget_manager.record_tokens("test_stage", 1000)
        self.budget_manager.record_tokens("test_stage", 2000)
        
        usage = self.budget_manager.current_usage()
        assert usage['tokens_used'] == 3000
        assert usage['tokens_remaining'] == 997000  # Default 1M tokens
    
    def test_increment_depth_success(self):
        """Test successful depth increment."""
        result = self.budget_manager.increment_depth("test_operation")
        
        assert result is True
        
        usage = self.budget_manager.current_usage()
        assert usage['current_depth'] == 1
    
    def test_increment_depth_limit_exceeded(self):
        """Test depth increment when limit exceeded."""
        # Configure very low depth limit
        limits = BudgetLimits(max_depth=1)
        self.budget_manager.configure(limits)
        
        # Use all depth
        assert self.budget_manager.increment_depth("test") is True
        assert self.budget_manager.increment_depth("test") is False
        
        usage = self.budget_manager.current_usage()
        assert usage['current_depth'] == 1
    
    def test_decrement_depth(self):
        """Test depth decrement."""
        # Increment then decrement
        self.budget_manager.increment_depth("test")
        self.budget_manager.increment_depth("test")
        
        usage_before = self.budget_manager.current_usage()
        assert usage_before['current_depth'] == 2
        
        self.budget_manager.decrement_depth("test")
        usage_after = self.budget_manager.current_usage()
        assert usage_after['current_depth'] == 1
    
    def test_decrement_depth_below_zero(self):
        """Test decrementing depth below zero (graceful handling)."""
        # Decrement without incrementing
        self.budget_manager.decrement_depth("test")
        
        usage = self.budget_manager.current_usage()
        assert usage['current_depth'] == 0
    
    def test_check_context_size_within_limit(self):
        """Test context size check within limits."""
        result = self.budget_manager.check_context_size(1000)
        
        assert result is True
    
    def test_check_context_size_exceeds_limit(self):
        """Test context size check exceeds limit."""
        # Configure low context limit
        limits = BudgetLimits(max_context_size=100)
        self.budget_manager.configure(limits)
        
        result = self.budget_manager.check_context_size(1000)
        
        assert result is False
    
    def test_check_message_length_within_limit(self):
        """Test message length check within limits."""
        result = self.budget_manager.check_message_length(100)
        
        assert result is True
    
    def test_check_message_length_exceeds_limit(self):
        """Test message length check exceeds limit."""
        # Configure low message limit
        limits = BudgetLimits(max_message_length=50)
        self.budget_manager.configure(limits)
        
        result = self.budget_manager.check_message_length(100)
        
        assert result is False
    
    def test_record_request(self):
        """Test request recording."""
        self.budget_manager.record_request()
        self.budget_manager.record_request()
        self.budget_manager.record_request()
        
        usage = self.budget_manager.current_usage()
        assert usage['requests_made'] == 3
        assert usage['requests_remaining'] == 997  # Default 1000 requests
    
    def test_current_usage_comprehensive(self):
        """Test comprehensive current usage reporting."""
        # Setup some usage
        self.budget_manager.record_tokens("test", 5000)
        self.budget_manager.record_request()
        self.budget_manager.increment_depth("test")
        self.budget_manager.acquire_concurrent_slot()
        self.budget_manager.start_stage("test_stage")
        
        usage = self.budget_manager.current_usage()
        
        # Check all fields are present and reasonable
        assert usage['tokens_used'] == 5000
        assert usage['tokens_remaining'] == 995000
        assert usage['requests_made'] == 1
        assert usage['requests_remaining'] == 999
        assert usage['current_depth'] == 1
        assert usage['max_depth'] == 10
        assert usage['active_concurrent'] == 1
        assert usage['max_parallel'] == 5
        assert usage['stages_completed']['test_stage'] == 1
        assert usage['last_activity'] > 0
        assert isinstance(usage['budget_exceeded'], dict)
    
    def test_get_budget_exceeded_reason_none(self):
        """Test budget exceeded reason when no limits exceeded."""
        reason = self.budget_manager.get_budget_exceeded_reason()
        
        assert reason is None
    
    def test_get_budget_exceeded_reason_tokens(self):
        """Test budget exceeded reason for tokens."""
        # Configure low token limit and exceed it
        limits = BudgetLimits(max_tokens=100)
        self.budget_manager.configure(limits)
        self.budget_manager.record_tokens("test", 150)
        
        reason = self.budget_manager.get_budget_exceeded_reason()
        
        assert reason == "Token budget exceeded"
    
    def test_get_budget_exceeded_reason_requests(self):
        """Test budget exceeded reason for requests."""
        # Configure low request limit and exceed it
        limits = BudgetLimits(max_requests=1)
        self.budget_manager.configure(limits)
        self.budget_manager.record_request()
        self.budget_manager.record_request()
        
        reason = self.budget_manager.get_budget_exceeded_reason()
        
        assert reason == "Request budget exceeded"
    
    def test_get_budget_exceeded_reason_depth(self):
        """Test budget exceeded reason for depth."""
        # Configure low depth limit and exceed it
        limits = BudgetLimits(max_depth=1)
        self.budget_manager.configure(limits)
        self.budget_manager.increment_depth("test")
        self.budget_manager.increment_depth("test")
        
        reason = self.budget_manager.get_budget_exceeded_reason()
        
        assert reason == "Recursion depth exceeded"
    
    def test_get_budget_exceeded_reason_concurrent(self):
        """Test budget exceeded reason for concurrent execution."""
        # Configure low parallel limit and exceed it
        limits = BudgetLimits(max_parallel=1)
        self.budget_manager.configure(limits)
        
        # Simulate concurrent limit exceeded
        self.budget_manager._usage.active_concurrent = 2
        
        reason = self.budget_manager.get_budget_exceeded_reason()
        
        assert reason == "Concurrent execution limit exceeded"
    
    def test_reset_usage(self):
        """Test usage statistics reset."""
        # Create some usage
        self.budget_manager.record_tokens("test", 1000)
        self.budget_manager.record_request()
        self.budget_manager.increment_depth("test")
        self.budget_manager.start_stage("test_stage")
        
        # Verify usage exists
        usage_before = self.budget_manager.current_usage()
        assert usage_before['tokens_used'] == 1000
        assert usage_before['requests_made'] == 1
        assert usage_before['current_depth'] == 1
        assert usage_before['stages_completed']['test_stage'] == 1
        
        # Reset usage
        self.budget_manager.reset_usage()
        
        # Verify usage is reset
        usage_after = self.budget_manager.current_usage()
        assert usage_after['tokens_used'] == 0
        assert usage_after['requests_made'] == 0
        assert usage_after['current_depth'] == 0
        assert usage_after['stages_completed'] == {}
    
    def test_create_budget_limits_from_config_defaults(self):
        """Test creating budget limits from config with defaults."""
        config = {}
        
        limits = create_budget_limits_from_config(config)
        
        assert limits.max_tokens == 1000000
        assert limits.max_requests == 1000
        assert limits.max_depth == 10
        assert limits.max_parallel == 5
        assert limits.max_context_size == 500000
        assert limits.max_message_length == 10000
        assert limits.executor_timeout == 30.0
    
    def test_create_budget_limits_from_config_custom(self):
        """Test creating budget limits from config with custom values."""
        config = {
            "max_tokens": 500000,
            "max_requests": 500,
            "max_depth": 5,
            "max_parallel": 3,
            "max_context_size": 250000,
            "max_message_length": 5000,
            "executor_timeout": 15.0
        }
        
        limits = create_budget_limits_from_config(config)
        
        assert limits.max_tokens == 500000
        assert limits.max_requests == 500
        assert limits.max_depth == 5
        assert limits.max_parallel == 3
        assert limits.max_context_size == 250000
        assert limits.max_message_length == 5000
        assert limits.executor_timeout == 15.0
    
    def test_create_budget_limits_backward_compatibility(self):
        """Test backward compatibility with old config names."""
        config = {
            "max_fallback_attempts": 7,  # Old name for max_depth
            "max_parallel_research": 3,   # Old name for max_parallel
            "max_executor_timeout": 45.0  # Old name for executor_timeout
        }
        
        limits = create_budget_limits_from_config(config)
        
        assert limits.max_depth == 7
        assert limits.max_parallel == 3
        assert limits.executor_timeout == 45.0
    
    def test_thread_safety_basic(self):
        """Test basic thread safety of budget manager operations."""
        results = []
        errors = []
        
        def worker(worker_id):
            try:
                for i in range(10):
                    # Test various operations
                    self.budget_manager.start_stage(f"worker_{worker_id}")
                    self.budget_manager.record_tokens(f"worker_{worker_id}", 100)
                    self.budget_manager.record_request()
                    
                    if i % 2 == 0:
                        depth_ok = self.budget_manager.increment_depth(f"worker_{worker_id}")
                        if depth_ok:
                            self.budget_manager.decrement_depth(f"worker_{worker_id}")
            except Exception as e:
                errors.append((worker_id, e))
            
            # Add result only once per worker after all operations complete
            results.append(worker_id)
        
        # Run multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Verify no errors and all workers completed
        assert len(errors) == 0
        assert len(results) == 5
        
        # Verify final state is consistent
        usage = self.budget_manager.current_usage()
        assert usage['tokens_used'] == 5000  # 5 workers * 10 operations * 100 tokens
        assert usage['requests_made'] == 50   # 5 workers * 10 operations
        assert usage['current_depth'] == 0   # All depths decremented
    
    def test_configure_limits_without_active_slots(self):
        """Test configuring limits when no slots are actively held."""
        # Start with default limits
        initial_limits = self.budget_manager.get_limits()
        assert initial_limits['max_parallel'] == 5
        
        # Configure new limits without any active slots
        new_limits = BudgetLimits(max_parallel=2, max_tokens=500000)
        self.budget_manager.configure(new_limits)
        
        # Verify new limits are applied
        updated_limits = self.budget_manager.get_limits()
        assert updated_limits['max_parallel'] == 2
        assert updated_limits['max_tokens'] == 500000
        
        # Test that new parallel limit is enforced
        assert self.budget_manager.acquire_concurrent_slot(timeout=0.1) is True
        assert self.budget_manager.acquire_concurrent_slot(timeout=0.1) is True
        assert self.budget_manager.acquire_concurrent_slot(timeout=0.1) is False
        
        # Clean up
        self.budget_manager.release_concurrent_slot()
        self.budget_manager.release_concurrent_slot()
