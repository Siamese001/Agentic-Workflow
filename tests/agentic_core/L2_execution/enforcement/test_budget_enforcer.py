"""
Tests for BudgetEnforcer - resource budget enforcement for execution.

Coverage:
- Budget initialization with limits
- Resource consumption tracking
- Budget violation detection
- Quota enforcement
- Budget reset and management
- Exception handling for over-budget scenarios
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from agentic_core.L2_execution.enforcement.budget_enforcer import BudgetEnforcer


class TestBudgetEnforcer:
    """Test suite for BudgetEnforcer."""

    def test_init_with_valid_budget_config(self):
        """Test initialization with valid budget configuration."""
        config = {
            "max_tokens": 100000,
            "max_cost_usd": 10.0,
            "max_requests": 1000
        }
        enforcer = BudgetEnforcer(budget_config=config)
        assert enforcer.budget_config == config

    def test_init_with_missing_budget_config(self):
        """Test initialization fails with missing budget config."""
        config = {}  # Missing required fields
        with pytest.raises(ValueError):
            BudgetEnforcer(budget_config=config)

    def test_track_resource_consumption(self):
        """Test tracking of resource consumption."""
        config = {
            "max_tokens": 100000,
            "max_cost_usd": 10.0,
            "max_requests": 1000
        }
        enforcer = BudgetEnforcer(budget_config=config)
        
        enforcer.track_consumption(
            tokens=1000,
            cost_usd=0.1,
            requests=1
        )
        
        assert enforcer.consumed_tokens == 1000
        assert enforcer.consumed_cost == 0.1
        assert enforcer.consumed_requests == 1

    def test_detect_budget_violation(self):
        """Test detection of budget violation."""
        config = {
            "max_tokens": 1000,
            "max_cost_usd": 1.0,
            "max_requests": 10
        }
        enforcer = BudgetEnforcer(budget_config=config)
        
        # Consume up to limit
        enforcer.track_consumption(tokens=1000, cost_usd=1.0, requests=10)
        
        violation = enforcer.check_violation()
        assert violation is not None
        assert violation["type"] in ["tokens", "cost", "requests"]

    def test_no_violation_within_budget(self):
        """Test no violation when within budget."""
        config = {
            "max_tokens": 100000,
            "max_cost_usd": 10.0,
            "max_requests": 1000
        }
        enforcer = BudgetEnforcer(budget_config=config)
        
        # Consume small amount
        enforcer.track_consumption(tokens=1000, cost_usd=0.1, requests=1)
        
        violation = enforcer.check_violation()
        assert violation is None

    def test_enforce_quota_blocks_over_budget(self):
        """Test quota enforcement blocks over-budget requests."""
        config = {
            "max_tokens": 1000,
            "max_cost_usd": 1.0,
            "max_requests": 10
        }
        enforcer = BudgetEnforcer(budget_config=config)
        
        # Consume to limit
        enforcer.track_consumption(tokens=1000, cost_usd=1.0, requests=10)
        
        request = {"tokens": 100, "cost_usd": 0.01}
        
        with pytest.raises(QuotaExceededError):
            enforcer.enforce(request)

    def test_enforce_quota_allows_within_budget(self):
        """Test quota enforcement allows within-budget requests."""
        config = {
            "max_tokens": 100000,
            "max_cost_usd": 10.0,
            "max_requests": 1000
        }
        enforcer = BudgetEnforcer(budget_config=config)
        
        request = {"tokens": 1000, "cost_usd": 0.1}
        
        # Should not raise
        enforcer.enforce(request)

    def test_reset_budget(self):
        """Test budget reset."""
        config = {
            "max_tokens": 100000,
            "max_cost_usd": 10.0,
            "max_requests": 1000
        }
        enforcer = BudgetEnforcer(budget_config=config)
        
        enforcer.track_consumption(tokens=50000, cost_usd=5.0, requests=500)
        assert enforcer.consumed_tokens == 50000
        
        enforcer.reset()
        assert enforcer.consumed_tokens == 0
        assert enforcer.consumed_cost == 0
        assert enforcer.consumed_requests == 0

    def test_get_budget_status(self):
        """Test retrieving budget status."""
        config = {
            "max_tokens": 100000,
            "max_cost_usd": 10.0,
            "max_requests": 1000
        }
        enforcer = BudgetEnforcer(budget_config=config)
        
        enforcer.track_consumption(tokens=50000, cost_usd=5.0, requests=500)
        
        status = enforcer.get_status()
        assert status["consumed_tokens"] == 50000
        assert status["remaining_tokens"] == 50000
        assert status["utilization_pct"] == 0.5

    def test_update_budget_config(self):
        """Test updating budget configuration."""
        config = {
            "max_tokens": 100000,
            "max_cost_usd": 10.0,
            "max_requests": 1000
        }
        enforcer = BudgetEnforcer(budget_config=config)
        
        new_config = {
            "max_tokens": 200000,  # Doubled
            "max_cost_usd": 20.0,
            "max_requests": 2000
        }
        enforcer.update_config(new_config)
        
        assert enforcer.budget_config["max_tokens"] == 200000

    def test_handle_budget_violation_gracefully(self):
        """Test graceful handling of budget violations."""
        config = {
            "max_tokens": 1000,
            "max_cost_usd": 1.0,
            "max_requests": 10
        }
        enforcer = BudgetEnforcer(budget_config=config)
        
        enforcer.track_consumption(tokens=1000, cost_usd=1.0, requests=10)
        
        # Should raise specific error, not generic exception
        with pytest.raises(QuotaExceededError):
            enforcer.enforce({"tokens": 1})
