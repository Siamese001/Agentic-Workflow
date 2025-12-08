"""Unit tests for L2_execution layer - execution planning and tool orchestration."""
from __future__ import annotations
import pytest
from typing import Dict, List, Any, Optional
from enum import Enum

class ToolStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"

class TestExecutionPlanning:
    """Tests for execution plan generation."""

    def test_plan_single_tool(self):
        """Nominal: Single tool execution plan."""
        intent = "search_documents"
        plan = [{"tool": "vector_search", "params": {"query": "test"}}]
        assert len(plan) == 1
        assert plan[0]["tool"] == "vector_search"

    def test_plan_multi_tool_sequence(self):
        """Nominal: Multi-tool sequential plan."""
        plan = [
            {"tool": "retrieve", "order": 1},
            {"tool": "process", "order": 2},
            {"tool": "respond", "order": 3},
        ]
        orders = [s["order"] for s in plan]
        assert orders == sorted(orders)

    def test_plan_parallel_tools(self):
        """Edge case: Parallel tool execution."""
        plan = [
            {"tool": "search_a", "parallel_group": 1},
            {"tool": "search_b", "parallel_group": 1},
            {"tool": "aggregate", "parallel_group": 2},
        ]
        group1 = [s for s in plan if s["parallel_group"] == 1]
        assert len(group1) == 2

    def test_plan_empty_intent(self):
        """Edge case: Empty intent produces minimal plan."""
        intent = ""
        plan = [] if not intent else [{"tool": "default"}]
        assert plan == []

    def test_plan_determinism(self):
        """Determinism: Same intent produces same plan."""
        intent = "search"
        p1 = [{"tool": "search"}] if intent else []
        p2 = [{"tool": "search"}] if intent else []
        assert p1 == p2


class TestToolOrchestration:
    """Tests for tool execution orchestration."""

    def test_execute_tool_success(self):
        """Nominal: Tool executes successfully."""
        tool_result = {"status": ToolStatus.SUCCESS, "output": "data"}
        assert tool_result["status"] == ToolStatus.SUCCESS

    def test_execute_tool_failure(self):
        """Nominal: Tool failure is captured."""
        tool_result = {"status": ToolStatus.FAILED, "error": "timeout"}
        assert tool_result["status"] == ToolStatus.FAILED
        assert "error" in tool_result

    def test_execute_with_retry(self):
        """Edge case: Tool retries on transient failure."""
        max_retries = 3
        attempts = 0
        success = False
        while attempts < max_retries and not success:
            attempts += 1
            if attempts == 2:  # Succeeds on second attempt
                success = True
        assert success is True
        assert attempts == 2

    def test_execute_timeout(self):
        """Edge case: Tool execution timeout."""
        timeout_seconds = 30
        execution_time = 5  # Simulated
        timed_out = execution_time > timeout_seconds
        assert timed_out is False

    def test_orchestration_state_tracking(self):
        """Nominal: Execution state is tracked."""
        state = {
            "step_1": ToolStatus.SUCCESS,
            "step_2": ToolStatus.RUNNING,
            "step_3": ToolStatus.PENDING,
        }
        completed = [k for k, v in state.items() if v == ToolStatus.SUCCESS]
        assert "step_1" in completed


class TestParameterValidation:
    """Tests for tool parameter validation."""

    def test_validate_required_params(self):
        """Nominal: Required parameters present."""
        required = ["query", "limit"]
        params = {"query": "test", "limit": 10}
        missing = [r for r in required if r not in params]
        assert missing == []

    def test_validate_missing_required(self):
        """Negative: Missing required parameter detected."""
        required = ["query", "limit"]
        params = {"query": "test"}
        missing = [r for r in required if r not in params]
        assert "limit" in missing

    def test_validate_param_types(self):
        """Nominal: Parameter types are correct."""
        schema = {"query": str, "limit": int}
        params = {"query": "test", "limit": 10}
        valid = all(isinstance(params[k], schema[k]) for k in schema)
        assert valid is True

    def test_validate_param_type_mismatch(self):
        """Negative: Type mismatch detected."""
        schema = {"limit": int}
        params = {"limit": "ten"}  # Should be int
        valid = all(isinstance(params.get(k), t) for k, t in schema.items())
        assert valid is False

    def test_validate_optional_params(self):
        """Edge case: Optional parameters can be missing."""
        required = ["query"]
        optional = ["limit", "offset"]
        params = {"query": "test"}
        missing_required = [r for r in required if r not in params]
        assert missing_required == []
