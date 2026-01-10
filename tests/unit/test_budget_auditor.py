"""
Unit tests for BudgetAuditor primitive.
Phase 7: Sub-atomic Refactor - Test Generation
"""
import pytest
from agentic_core.L0_maintenance.primitives.budget_auditor import BudgetAuditor


class TestBudgetAuditor:
    """Comprehensive test suite for BudgetAuditor."""
    
    def test_initialization_default(self):
        """Test BudgetAuditor initializes with default limit."""
        auditor = BudgetAuditor()
        
        assert auditor.limit == 2.0
        assert auditor.spent == 0.0
        assert auditor.input_tokens == 0
        assert auditor.output_tokens == 0
    
    def test_initialization_custom_limit(self):
        """Test BudgetAuditor initializes with custom limit."""
        auditor = BudgetAuditor(limit_usd=5.0)
        
        assert auditor.limit == 5.0
        assert auditor.spent == 0.0
    
    def test_track_tokens_and_cost(self):
        """Test tracking prompt/response updates tokens and cost."""
        auditor = BudgetAuditor(limit_usd=10.0)
        
        # Track a small interaction
        prompt = "Test prompt " * 100  # ~1100 chars = ~275 tokens
        response = "Test response " * 200  # ~2600 chars = ~650 tokens
        
        auditor.track(prompt, response)
        
        # Verify tokens tracked
        assert auditor.input_tokens > 0
        assert auditor.output_tokens > 0
        assert auditor.spent > 0
        
        # Verify cost calculation (rough check)
        expected_cost = (275 / 1_000_000 * 0.5) + (650 / 1_000_000 * 1.5)
        assert abs(auditor.spent - expected_cost) < 0.0001
    
    def test_track_multiple_interactions(self):
        """Test tracking accumulates across multiple calls."""
        auditor = BudgetAuditor(limit_usd=10.0)
        
        # First interaction
        auditor.track("prompt1" * 50, "response1" * 100)
        first_spent = auditor.spent
        first_input = auditor.input_tokens
        
        # Second interaction
        auditor.track("prompt2" * 50, "response2" * 100)
        
        # Verify accumulation
        assert auditor.spent > first_spent
        assert auditor.input_tokens > first_input
    
    def test_check_budget_within_limit(self):
        """Test check_budget returns True when within limit."""
        auditor = BudgetAuditor(limit_usd=10.0)
        
        # Small usage
        auditor.track("small prompt", "small response")
        
        assert auditor.check_budget() is True
    
    def test_check_budget_exceeded(self):
        """Test check_budget returns False when limit exceeded."""
        auditor = BudgetAuditor(limit_usd=0.001)  # Very small limit
        
        # Large usage to exceed limit
        large_prompt = "x" * 100000  # ~25k tokens
        large_response = "y" * 100000
        auditor.track(large_prompt, large_response)
        
        assert auditor.check_budget() is False
    
    def test_get_status_format(self):
        """Test get_status returns properly formatted string."""
        auditor = BudgetAuditor(limit_usd=5.0)
        auditor.track("test" * 100, "response" * 200)
        
        status = auditor.get_status()
        
        assert "$" in status
        assert "/" in status
        assert "in" in status
        assert "out" in status
        assert "5.0" in status
    
    def test_get_metrics_structure(self):
        """Test get_metrics returns complete metrics dictionary."""
        auditor = BudgetAuditor(limit_usd=3.0)
        auditor.track("prompt" * 50, "response" * 100)
        
        metrics = auditor.get_metrics()
        
        assert 'spent_usd' in metrics
        assert 'limit_usd' in metrics
        assert 'utilization_pct' in metrics
        assert 'input_tokens' in metrics
        assert 'output_tokens' in metrics
        assert 'total_tokens' in metrics
        
        # Verify calculations
        assert metrics['limit_usd'] == 3.0
        assert metrics['total_tokens'] == metrics['input_tokens'] + metrics['output_tokens']
        assert 0 <= metrics['utilization_pct'] <= 100
    
    def test_get_metrics_utilization_calculation(self):
        """Test utilization percentage is calculated correctly."""
        auditor = BudgetAuditor(limit_usd=2.0)
        
        # Spend exactly half the budget
        # Need to track enough to spend ~$1.00
        # With 4 chars/token: 1M input tokens = 4M chars
        # Cost: 1M tokens * $0.50 = $0.50
        # Need 2M input tokens for $1.00 = 8M chars
        large_prompt = "x" * 8_000_000
        auditor.track(large_prompt, "")
        
        metrics = auditor.get_metrics()
        
        # Should be approximately 50% utilization
        assert 45 <= metrics['utilization_pct'] <= 55
    
    def test_reset_clears_all_counters(self):
        """Test reset() clears all tracking data."""
        auditor = BudgetAuditor(limit_usd=5.0)
        
        # Track some usage
        auditor.track("prompt" * 100, "response" * 200)
        
        # Verify data exists
        assert auditor.spent > 0
        assert auditor.input_tokens > 0
        assert auditor.output_tokens > 0
        
        # Reset
        auditor.reset()
        
        # Verify all cleared
        assert auditor.spent == 0.0
        assert auditor.input_tokens == 0
        assert auditor.output_tokens == 0
        assert auditor.limit == 5.0  # Limit unchanged
    
    def test_zero_limit_edge_case(self):
        """Test behavior with zero budget limit."""
        auditor = BudgetAuditor(limit_usd=0.0)
        
        metrics = auditor.get_metrics()
        
        # Should handle division by zero gracefully
        assert metrics['utilization_pct'] == 0
    
    def test_empty_strings_tracking(self):
        """Test tracking with empty strings."""
        auditor = BudgetAuditor()
        
        auditor.track("", "")
        
        # Should not crash, tokens should be 0
        assert auditor.input_tokens == 0
        assert auditor.output_tokens == 0
        assert auditor.spent == 0.0
    
    def test_large_scale_tracking(self):
        """Test tracking with very large inputs."""
        auditor = BudgetAuditor(limit_usd=100.0)
        
        # Simulate 100 interactions
        for i in range(100):
            auditor.track(f"prompt {i}" * 50, f"response {i}" * 100)
        
        # Verify accumulation works at scale (adjusted expectations)
        assert auditor.input_tokens > 10000
        assert auditor.output_tokens > 20000
        assert auditor.spent > 0
        
        metrics = auditor.get_metrics()
        assert metrics['total_tokens'] > 30000
