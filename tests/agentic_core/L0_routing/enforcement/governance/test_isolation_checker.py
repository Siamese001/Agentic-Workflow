"""Tests for isolation_checker.py module."""

from __future__ import annotations

import pytest

from agentic_core.L0_routing.enforcement.governance.isolation_checker import (
    LayerViolation,
    BoundaryCheck,
    IsolationChecker,
)


class TestLayerViolation:
    """Tests for LayerViolation enum."""

    def test_layer_violation_values(self):
        """Test LayerViolation has expected values."""
        assert LayerViolation.L0_ROUTING_RETRIEVAL is not None
        assert LayerViolation.L1_REASONING_EXECUTION is not None
        assert LayerViolation.L1_REASONING_ROUTING is not None
        assert LayerViolation.L2_EXECUTION_ROUTING is not None
        assert LayerViolation.L2_EXECUTION_WRITE is not None
        assert LayerViolation.L3_HEALING_UNBOUND is not None
        assert LayerViolation.L6_LEARNING_MUTATION is not None

    def test_layer_violation_count(self):
        """Test LayerViolation has 7 values."""
        assert len(LayerViolation) == 7


class TestBoundaryCheck:
    """Tests for BoundaryCheck dataclass."""

    def test_boundary_check_valid(self):
        """Test BoundaryCheck with is_valid=True."""
        check = BoundaryCheck(
            is_valid=True,
            layer="L0",
            attempted_operation="routing",
        )
        assert check.is_valid is True
        assert check.layer == "L0"
        assert check.attempted_operation == "routing"
        assert check.violation is None
        assert check.reason == ""

    def test_boundary_check_invalid(self):
        """Test BoundaryCheck with is_valid=False."""
        check = BoundaryCheck(
            is_valid=False,
            layer="L0",
            attempted_operation="retrieval",
            violation=LayerViolation.L0_ROUTING_RETRIEVAL,
            reason="Layer L0 cannot perform retrieval",
        )
        assert check.is_valid is False
        assert check.layer == "L0"
        assert check.attempted_operation == "retrieval"
        assert check.violation == LayerViolation.L0_ROUTING_RETRIEVAL
        assert check.reason == "Layer L0 cannot perform retrieval"

    def test_boundary_check_defaults(self):
        """Test BoundaryCheck default values."""
        check = BoundaryCheck(
            is_valid=True,
            layer="L0",
            attempted_operation="routing",
        )
        assert check.violation is None
        assert check.reason == ""


class TestIsolationChecker:
    """Tests for IsolationChecker class."""

    def test_checker_init(self):
        """Test IsolationChecker initialization."""
        checker = IsolationChecker()
        assert checker._violation_count == 0

    def test_layer_authority_structure(self):
        """Test LAYER_AUTHORITY has all expected layers."""
        checker = IsolationChecker()
        assert "L0" in checker.LAYER_AUTHORITY
        assert "L1" in checker.LAYER_AUTHORITY
        assert "L2" in checker.LAYER_AUTHORITY
        assert "L3" in checker.LAYER_AUTHORITY
        assert "L4" in checker.LAYER_AUTHORITY
        assert "L5" in checker.LAYER_AUTHORITY
        assert "L6" in checker.LAYER_AUTHORITY
        assert "C0" in checker.LAYER_AUTHORITY

    def test_violation_patterns_structure(self):
        """Test VIOLATION_PATTERNS has expected patterns."""
        checker = IsolationChecker()
        assert ("L0", "retrieval") in checker.VIOLATION_PATTERNS
        assert ("L1", "execution") in checker.VIOLATION_PATTERNS
        assert ("L1", "routing") in checker.VIOLATION_PATTERNS
        assert ("L2", "routing") in checker.VIOLATION_PATTERNS
        assert ("L2", "direct_write") in checker.VIOLATION_PATTERNS

    def test_check_allowed_operation(self):
        """Test check returns valid for allowed operation."""
        checker = IsolationChecker()
        
        result = checker.check("L0", "routing")
        
        assert result.is_valid is True
        assert result.layer == "L0"
        assert result.attempted_operation == "routing"

    def test_check_l0_retrieval_violation(self):
        """Test check detects L0 retrieval violation."""
        checker = IsolationChecker()
        
        result = checker.check("L0", "retrieval")
        
        assert result.is_valid is False
        assert result.violation == LayerViolation.L0_ROUTING_RETRIEVAL
        assert "cannot perform retrieval" in result.reason

    def test_check_l1_execution_violation(self):
        """Test check detects L1 execution violation."""
        checker = IsolationChecker()
        
        result = checker.check("L1", "execute_tool")
        
        assert result.is_valid is False
        assert result.violation == LayerViolation.L1_REASONING_EXECUTION
        assert "cannot perform execution" in result.reason

    def test_check_l1_routing_violation(self):
        """Test check detects L1 routing violation."""
        checker = IsolationChecker()
        
        result = checker.check("L1", "dispatch_route")
        
        assert result.is_valid is False
        assert result.violation == LayerViolation.L1_REASONING_ROUTING
        assert "cannot perform routing" in result.reason

    def test_check_l2_routing_violation(self):
        """Test check detects L2 routing violation."""
        checker = IsolationChecker()
        
        result = checker.check("L2", "routing")
        
        assert result.is_valid is False
        assert result.violation == LayerViolation.L2_EXECUTION_ROUTING
        assert "cannot perform routing" in result.reason

    def test_check_l2_direct_write_violation(self):
        """Test check detects L2 direct write violation."""
        checker = IsolationChecker()
        
        result = checker.check("L2", "direct_write")
        
        assert result.is_valid is False
        assert result.violation == LayerViolation.L2_EXECUTION_WRITE
        assert "cannot perform direct_write" in result.reason

    def test_check_unknown_layer(self):
        """Test check with unknown layer returns invalid."""
        checker = IsolationChecker()
        
        result = checker.check("LX", "routing")
        
        assert result.is_valid is False
        assert result.violation is None
        assert "cannot perform" in result.reason

    def test_check_increments_violation_count(self):
        """Test check increments violation count on violation."""
        checker = IsolationChecker()
        
        checker.check("L0", "routing")
        assert checker.get_violation_count() == 0
        
        checker.check("L0", "retrieval")
        assert checker.get_violation_count() == 1
        
        checker.check("L1", "execute_tool")
        assert checker.get_violation_count() == 2

    def test_categorize_operation_routing(self):
        """Test _categorize_operation detects routing operations."""
        checker = IsolationChecker()
        
        assert checker._categorize_operation("route_request") == "routing"
        assert checker._categorize_operation("dispatch_to") == "routing"
        assert checker._categorize_operation("direct_call") == "routing"

    def test_categorize_operation_reasoning(self):
        """Test _categorize_operation detects reasoning operations."""
        checker = IsolationChecker()
        
        assert checker._categorize_operation("reason_about") == "reasoning"
        assert checker._categorize_operation("plan_step") == "reasoning"
        assert checker._categorize_operation("synthesize_response") == "reasoning"
        assert checker._categorize_operation("infer_intent") == "reasoning"

    def test_categorize_operation_execution(self):
        """Test _categorize_operation detects execution operations."""
        checker = IsolationChecker()
        
        assert checker._categorize_operation("execute_tool") == "execution"
        assert checker._categorize_operation("invoke_function") == "execution"
        assert checker._categorize_operation("run_command") == "execution"
        assert checker._categorize_operation("take_action") == "execution"

    def test_categorize_operation_healing(self):
        """Test _categorize_operation detects healing operations."""
        checker = IsolationChecker()
        
        assert checker._categorize_operation("heal_system") == "healing"
        assert checker._categorize_operation("repair_issue") == "healing"
        assert checker._categorize_operation("remediate_error") == "healing"
        assert checker._categorize_operation("fix_bug") == "healing"

    def test_categorize_operation_retrieval(self):
        """Test _categorize_operation detects retrieval operations."""
        checker = IsolationChecker()
        
        assert checker._categorize_operation("retrieve_data") == "retrieval"
        assert checker._categorize_operation("fetch_evidence") == "retrieval"
        assert checker._categorize_operation("rag_search") == "retrieval"
        assert checker._categorize_operation("search_index") == "retrieval"

    def test_categorize_operation_direct_write(self):
        """Test _categorize_operation detects direct write operations."""
        checker = IsolationChecker()
        
        assert checker._categorize_operation("write_file") == "direct_write"
        assert checker._categorize_operation("commit_changes") == "direct_write"
        assert checker._categorize_operation("mutate_state") == "direct_write"
        assert checker._categorize_operation("persist_data") == "direct_write"

    def test_categorize_operation_observation(self):
        """Test _categorize_operation detects observation operations."""
        checker = IsolationChecker()
        
        assert checker._categorize_operation("observe_system") == "observation"
        assert checker._categorize_operation("evaluate_performance") == "observation"
        assert checker._categorize_operation("telemetry_log") == "observation"
        assert checker._categorize_operation("shadow_mode") == "observation"

    def test_categorize_operation_unknown(self):
        """Test _categorize_operation returns unknown for unclassified operations."""
        checker = IsolationChecker()
        
        assert checker._categorize_operation("random_operation") == "unknown"

    def test_get_violation_count(self):
        """Test get_violation_count returns correct count."""
        checker = IsolationChecker()
        
        assert checker.get_violation_count() == 0
        
        checker.check("L0", "retrieval")
        assert checker.get_violation_count() == 1
        
        checker.check("L1", "execute_tool")
        assert checker.get_violation_count() == 2
