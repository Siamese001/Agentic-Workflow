"""
Tests for ExecutionGuardrailChokepoint - execution safety gate enforcement.

Coverage:
- Guardrail initialization with policies
- Pre-execution validation
- Guardrail trigger conditions
- Policy enforcement and blocking
- Exception handling for policy violations
- Runtime behavior monitoring
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from agentic_core.L2_execution.enforcement.execution_guardrail_chokepoint import ExecutionGuardrailChokepoint


class TestExecutionGuardrailChokepoint:
    """Test suite for ExecutionGuardrailChokepoint."""

    def test_init_with_valid_policies(self):
        """Test initialization with valid guardrail policies."""
        policies = {
            "max_execution_time": 300,
            "allowed_operations": ["read", "write"],
            "require_approval": False
        }
        chokepoint = ExecutionGuardrailChokepoint(policies=policies)
        assert chokepoint.policies == policies

    def test_init_with_missing_policies(self):
        """Test initialization fails with missing required policies."""
        policies = {}  # Missing required fields
        with pytest.raises(ValueError):
            ExecutionGuardrailChokepoint(policies=policies)

    def test_pre_execution_validation_success(self):
        """Test successful pre-execution validation."""
        policies = {
            "max_execution_time": 300,
            "allowed_operations": ["read", "write"],
            "require_approval": False
        }
        chokepoint = ExecutionGuardrailChokepoint(policies=policies)
        
        execution_context = {
            "operation": "read",
            "estimated_time": 60,
            "requires_approval": False
        }
        result = chokepoint.pre_validate(execution_context)
        
        assert result.valid is True

    def test_pre_execution_validation_disallowed_operation(self):
        """Test validation fails for disallowed operation."""
        policies = {
            "max_execution_time": 300,
            "allowed_operations": ["read"],
            "require_approval": False
        }
        chokepoint = ExecutionGuardrailChokepoint(policies=policies)
        
        execution_context = {
            "operation": "delete",  # Not allowed
            "estimated_time": 60,
            "requires_approval": False
        }
        result = chokepoint.pre_validate(execution_context)
        
        assert result.valid is False
        assert "operation" in result.violation_reason.lower()

    def test_pre_execution_validation_exceeds_time_limit(self):
        """Test validation fails when exceeding time limit."""
        policies = {
            "max_execution_time": 300,
            "allowed_operations": ["read", "write"],
            "require_approval": False
        }
        chokepoint = ExecutionGuardrailChokepoint(policies=policies)
        
        execution_context = {
            "operation": "read",
            "estimated_time": 600,  # Exceeds 300s limit
            "requires_approval": False
        }
        result = chokepoint.pre_validate(execution_context)
        
        assert result.valid is False
        assert "time" in result.violation_reason.lower()

    def test_guardrail_trigger_conditions(self):
        """Test guardrail trigger evaluation."""
        policies = {
            "max_execution_time": 300,
            "allowed_operations": ["read", "write"],
            "require_approval": True,
            "trigger_conditions": {
                "high_risk_operation": True,
                "external_network_access": False
            }
        }
        chokepoint = ExecutionGuardrailChokepoint(policies=policies)
        
        context = {
            "operation": "write",
            "high_risk": True,
            "network_access": False
        }
        should_trigger = chokepoint.should_trigger(context)
        
        assert should_trigger is True

    def test_enforce_policy_blocks_invalid_execution(self):
        """Test policy enforcement blocks invalid executions."""
        policies = {
            "max_execution_time": 300,
            "allowed_operations": ["read"],
            "require_approval": False
        }
        chokepoint = ExecutionGuardrailChokepoint(policies=policies)
        
        execution_context = {
            "operation": "write",  # Not allowed
            "estimated_time": 60
        }
        
        with pytest.raises(PermissionError):
            chokepoint.enforce(execution_context)

    def test_enforce_policy_allows_valid_execution(self):
        """Test policy enforcement allows valid executions."""
        policies = {
            "max_execution_time": 300,
            "allowed_operations": ["read", "write"],
            "require_approval": False
        }
        chokepoint = ExecutionGuardrailChokepoint(policies=policies)
        
        execution_context = {
            "operation": "read",
            "estimated_time": 60
        }
        
        # Should not raise
        result = chokepoint.enforce(execution_context)
        assert result is None

    def test_runtime_behavior_monitoring(self):
        """Test runtime behavior monitoring."""
        policies = {
            "max_execution_time": 300,
            "allowed_operations": ["read", "write"],
            "require_approval": False
        }
        chokepoint = ExecutionGuardrailChokepoint(policies=policies)
        
        monitor = Mock()
        chokepoint.set_monitor(monitor)
        
        execution_context = {"operation": "read"}
        chokepoint.enforce(execution_context)
        
        monitor.log.assert_called_once()

    def test_handle_policy_violation(self):
        """Test handling of policy violations."""
        policies = {
            "max_execution_time": 300,
            "allowed_operations": ["read"],
            "require_approval": False
        }
        chokepoint = ExecutionGuardrailChokepoint(policies=policies)
        
        execution_context = {"operation": "write"}
        
        with pytest.raises(PermissionError) as exc_info:
            chokepoint.enforce(execution_context)
        
        assert "policy" in str(exc_info.value).lower()

    def test_update_policies_runtime(self):
        """Test updating policies at runtime."""
        policies = {
            "max_execution_time": 300,
            "allowed_operations": ["read"],
            "require_approval": False
        }
        chokepoint = ExecutionGuardrailChokepoint(policies=policies)
        
        new_policies = {
            "max_execution_time": 600,  # Increased
            "allowed_operations": ["read", "write"],
            "require_approval": False
        }
        chokepoint.update_policies(new_policies)
        
        assert chokepoint.policies["max_execution_time"] == 600

    def test_get_policy_status(self):
        """Test retrieving current policy status."""
        policies = {
            "max_execution_time": 300,
            "allowed_operations": ["read", "write"],
            "require_approval": False
        }
        chokepoint = ExecutionGuardrailChokepoint(policies=policies)
        
        status = chokepoint.get_status()
        assert "max_execution_time" in status
        assert "allowed_operations" in status
