"""
Tests for ReasoningChokepoint - reasoning gate enforcement and validation.

Coverage:
- Chokepoint initialization with policies
- Reasoning request validation
- Policy enforcement (budget, timeout, scope)
- Chokepoint trigger conditions
- Exception handling for invalid requests
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from agentic_core.L1_cognition.enforcement.reasoning_chokepoint import ReasoningChokepoint


class TestReasoningChokepoint:
    """Test suite for ReasoningChokepoint."""

    def test_init_with_valid_policies(self):
        """Test initialization with valid policy configuration."""
        policies = {
            "max_tokens": 10000,
            "timeout_seconds": 30,
            "allowed_scopes": ["reasoning", "planning"]
        }
        chokepoint = ReasoningChokepoint(policies=policies)
        assert chokepoint.policies == policies

    def test_init_with_missing_policies(self):
        """Test initialization fails with missing required policies."""
        policies = {}  # Missing required fields
        with pytest.raises(ValueError):
            ReasoningChokepoint(policies=policies)

    def test_validate_reasoning_request_success(self):
        """Test successful validation of reasoning request."""
        policies = {
            "max_tokens": 10000,
            "timeout_seconds": 30,
            "allowed_scopes": ["reasoning", "planning"]
        }
        chokepoint = ReasoningChokepoint(policies=policies)
        
        request = {
            "scope": "reasoning",
            "estimated_tokens": 5000,
            "timeout": 20
        }
        result = chokepoint.validate(request)
        
        assert result.valid is True

    def test_validate_exceeds_token_budget(self):
        """Test validation fails when exceeding token budget."""
        policies = {
            "max_tokens": 10000,
            "timeout_seconds": 30,
            "allowed_scopes": ["reasoning"]
        }
        chokepoint = ReasoningChokepoint(policies=policies)
        
        request = {
            "scope": "reasoning",
            "estimated_tokens": 15000,  # Exceeds max
            "timeout": 20
        }
        result = chokepoint.validate(request)
        
        assert result.valid is False
        assert "token" in result.violation_reason.lower()

    def test_validate_exceeds_timeout(self):
        """Test validation fails when exceeding timeout."""
        policies = {
            "max_tokens": 10000,
            "timeout_seconds": 30,
            "allowed_scopes": ["reasoning"]
        }
        chokepoint = ReasoningChokepoint(policies=policies)
        
        request = {
            "scope": "reasoning",
            "estimated_tokens": 5000,
            "timeout": 60  # Exceeds max
        }
        result = chokepoint.validate(request)
        
        assert result.valid is False
        assert "timeout" in result.violation_reason.lower()

    def test_validate_invalid_scope(self):
        """Test validation fails for disallowed scope."""
        policies = {
            "max_tokens": 10000,
            "timeout_seconds": 30,
            "allowed_scopes": ["reasoning"]
        }
        chokepoint = ReasoningChokepoint(policies=policies)
        
        request = {
            "scope": "execution",  # Not in allowed_scopes
            "estimated_tokens": 5000,
            "timeout": 20
        }
        result = chokepoint.validate(request)
        
        assert result.valid is False
        assert "scope" in result.violation_reason.lower()

    def test_chokepoint_trigger_conditions(self):
        """Test chokepoint trigger evaluation."""
        policies = {
            "max_tokens": 10000,
            "timeout_seconds": 30,
            "allowed_scopes": ["reasoning"],
            "trigger_conditions": {
                "high_complexity": True,
                "cross_layer": False
            }
        }
        chokepoint = ReasoningChokepoint(policies=policies)
        
        context = {
            "complexity": "high",
            "cross_layer": False
        }
        should_trigger = chokepoint.should_trigger(context)
        
        assert should_trigger is True

    def test_enforce_policy_blocks_invalid_request(self):
        """Test policy enforcement blocks invalid requests."""
        policies = {
            "max_tokens": 10000,
            "timeout_seconds": 30,
            "allowed_scopes": ["reasoning"]
        }
        chokepoint = ReasoningChokepoint(policies=policies)
        
        request = {
            "scope": "reasoning",
            "estimated_tokens": 20000,
            "timeout": 20
        }
        
        with pytest.raises(PermissionError):
            chokepoint.enforce(request)

    def test_enforce_policy_allows_valid_request(self):
        """Test policy enforcement allows valid requests."""
        policies = {
            "max_tokens": 10000,
            "timeout_seconds": 30,
            "allowed_scopes": ["reasoning"]
        }
        chokepoint = ReasoningChokepoint(policies=policies)
        
        request = {
            "scope": "reasoning",
            "estimated_tokens": 5000,
            "timeout": 20
        }
        
        # Should not raise
        result = chokepoint.enforce(request)
        assert result is None

    def test_update_policies_runtime(self):
        """Test updating policies at runtime."""
        policies = {
            "max_tokens": 10000,
            "timeout_seconds": 30,
            "allowed_scopes": ["reasoning"]
        }
        chokepoint = ReasoningChokepoint(policies=policies)
        
        new_policies = {
            "max_tokens": 20000,  # Increased
            "timeout_seconds": 30,
            "allowed_scopes": ["reasoning"]
        }
        chokepoint.update_policies(new_policies)
        
        assert chokepoint.policies["max_tokens"] == 20000

    def test_get_policy_status(self):
        """Test retrieving current policy status."""
        policies = {
            "max_tokens": 10000,
            "timeout_seconds": 30,
            "allowed_scopes": ["reasoning"]
        }
        chokepoint = ReasoningChokepoint(policies=policies)
        
        status = chokepoint.get_status()
        assert "max_tokens" in status
        assert "timeout_seconds" in status
