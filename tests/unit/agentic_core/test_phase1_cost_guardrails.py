"""
Phase 1 Test Suite: Cost Guardrails, Token Monitoring, Context Standardization

Tests for:
- CostGuardrailMixin: Token tracking, budget enforcement, recursion limits
- ContextManagementMixin: Context window management, summarization, pruning
- Integration with InfrastructureMixin
"""

from __future__ import annotations

import pytest

from agentic_core.base_agents.cost_guardrail_mixin import (
    CostGuardrailMixin,
    TokenUsage,
    BudgetExceededError,
    RecursionLimitError,
    MODEL_PRICING,
)
from agentic_core.base_agents.context_management_mixin import (
    ContextManagementMixin,
    ContextItem,
    ContextPriority,
)


# =============================================================================
# Test Fixtures
# =============================================================================


class MockCostAgent(CostGuardrailMixin):
    """Mock agent for testing CostGuardrailMixin."""

    def __init__(self):
        super().__init__()


class MockContextAgent(ContextManagementMixin):
    """Mock agent for testing ContextManagementMixin."""

    def __init__(self):
        super().__init__()


class MockCombinedAgent(CostGuardrailMixin, ContextManagementMixin):
    """Mock agent combining both Phase 1 mixins."""

    def __init__(self):
        super().__init__()


@pytest.fixture
def cost_agent():
    """Create a fresh cost agent for each test."""
    return MockCostAgent()


@pytest.fixture
def context_agent():
    """Create a fresh context agent for each test."""
    return MockContextAgent()


@pytest.fixture
def combined_agent():
    """Create a fresh combined agent for each test."""
    return MockCombinedAgent()


# =============================================================================
# CostGuardrailMixin Tests
# =============================================================================


class TestCostGuardrailInitialization:
    """Test CostGuardrailMixin initialization."""

    def test_initialization_flag_set(self, cost_agent):
        """Verify initialization flag is set."""
        assert cost_agent._cost_guardrail_initialized is True

    def test_default_budget_config(self, cost_agent):
        """Verify default budget configuration."""
        config = cost_agent._budget_config
        assert config.max_tokens_per_request == 8000
        assert config.max_tokens_per_session == 100000
        assert config.max_cost_per_session_usd == 10.0
        assert config.max_recursive_depth == 10
        assert config.max_loop_iterations == 50

    def test_session_tracking_initialized(self, cost_agent):
        """Verify session tracking is initialized."""
        assert cost_agent._session_token_usage == []
        assert cost_agent._total_session_tokens == 0
        assert cost_agent._total_session_cost == 0.0


class TestBudgetConfiguration:
    """Test budget configuration methods."""

    def test_configure_budget_partial(self, cost_agent):
        """Test partial budget configuration."""
        cost_agent.configure_budget(max_tokens_per_request=5000)
        assert cost_agent._budget_config.max_tokens_per_request == 5000
        assert cost_agent._budget_config.max_tokens_per_session == 100000  # Unchanged

    def test_configure_budget_full(self, cost_agent):
        """Test full budget configuration."""
        cost_agent.configure_budget(
            max_tokens_per_request=4000,
            max_tokens_per_session=50000,
            max_cost_per_session_usd=5.0,
            max_recursive_depth=5,
            max_loop_iterations=25,
            alert_threshold_pct=0.7,
        )
        config = cost_agent._budget_config
        assert config.max_tokens_per_request == 4000
        assert config.max_tokens_per_session == 50000
        assert config.max_cost_per_session_usd == 5.0
        assert config.max_recursive_depth == 5
        assert config.max_loop_iterations == 25
        assert config.alert_threshold_pct == 0.7


class TestCostEstimation:
    """Test cost estimation methods."""

    def test_estimate_cost_known_model(self, cost_agent):
        """Test cost estimation for known model."""
        cost = cost_agent.estimate_cost(1000, 500, "gpt-4o")
        # gpt-4o: input=$0.0025/1K, output=$0.01/1K
        expected = (1000 / 1000) * 0.0025 + (500 / 1000) * 0.01
        assert abs(cost - expected) < 0.0001

    def test_estimate_cost_unknown_model(self, cost_agent):
        """Test cost estimation for unknown model uses default."""
        cost = cost_agent.estimate_cost(1000, 500, "unknown-model")
        # default: input=$0.001/1K, output=$0.002/1K
        expected = (1000 / 1000) * 0.001 + (500 / 1000) * 0.002
        assert abs(cost - expected) < 0.0001

    def test_model_pricing_completeness(self):
        """Verify all expected models have pricing."""
        expected_models = ["gpt-4o", "gpt-4o-mini", "claude-3-opus", "claude-3-sonnet"]
        for model in expected_models:
            assert model in MODEL_PRICING
            assert "input" in MODEL_PRICING[model]
            assert "output" in MODEL_PRICING[model]


class TestTokenUsageRecording:
    """Test token usage recording."""

    def test_record_token_usage_basic(self, cost_agent):
        """Test basic token usage recording."""
        usage = cost_agent.record_token_usage(100, 50, "gpt-4o")
        assert isinstance(usage, TokenUsage)
        assert usage.prompt_tokens == 100
        assert usage.completion_tokens == 50
        assert usage.total_tokens == 150
        assert usage.model == "gpt-4o"

    def test_record_token_usage_accumulates(self, cost_agent):
        """Test token usage accumulates across calls."""
        cost_agent.record_token_usage(100, 50, "gpt-4o")
        cost_agent.record_token_usage(200, 100, "gpt-4o")
        assert cost_agent._total_session_tokens == 450
        assert len(cost_agent._session_token_usage) == 2

    def test_record_token_usage_exceeds_request_limit(self, cost_agent):
        """Test exception when request limit exceeded."""
        cost_agent.configure_budget(max_tokens_per_request=100)
        with pytest.raises(BudgetExceededError) as exc_info:
            cost_agent.record_token_usage(100, 50, "gpt-4o")
        assert exc_info.value.limit_type == "tokens_per_request"

    def test_record_token_usage_exceeds_session_limit(self, cost_agent):
        """Test exception when session limit exceeded."""
        cost_agent.configure_budget(max_tokens_per_session=200)
        cost_agent.record_token_usage(100, 50, "gpt-4o")  # 150 tokens
        with pytest.raises(BudgetExceededError) as exc_info:
            cost_agent.record_token_usage(100, 50, "gpt-4o")  # Would be 300
        assert exc_info.value.limit_type == "tokens_per_session"

    def test_record_token_usage_exceeds_cost_limit(self, cost_agent):
        """Test exception when cost limit exceeded."""
        cost_agent.configure_budget(max_cost_per_session_usd=0.001)
        with pytest.raises(BudgetExceededError) as exc_info:
            cost_agent.record_token_usage(1000, 1000, "gpt-4o")
        assert exc_info.value.limit_type == "cost_per_session"


class TestRecursionLimits:
    """Test recursion and loop limit enforcement."""

    def test_check_recursion_limit_within_bounds(self, cost_agent):
        """Test recursion check within limits."""
        cost_agent.configure_budget(max_recursive_depth=5)
        for i in range(5):
            cost_agent.check_recursion_limit(f"op_{i}")
        assert len(cost_agent._call_stack) == 5

    def test_check_recursion_limit_exceeded(self, cost_agent):
        """Test recursion limit exceeded."""
        cost_agent.configure_budget(max_recursive_depth=3)
        for i in range(3):
            cost_agent.check_recursion_limit("same_op")
        with pytest.raises(RecursionLimitError) as exc_info:
            cost_agent.check_recursion_limit("same_op")
        assert exc_info.value.limit_type == "recursive_depth"

    def test_exit_recursion(self, cost_agent):
        """Test exiting recursion removes from stack."""
        cost_agent.check_recursion_limit("op1")
        cost_agent.check_recursion_limit("op2")
        assert len(cost_agent._call_stack) == 2
        cost_agent.exit_recursion("op1")
        assert len(cost_agent._call_stack) == 1
        assert "op1" not in cost_agent._call_stack

    def test_check_loop_limit_within_bounds(self, cost_agent):
        """Test loop check within limits."""
        cost_agent.configure_budget(max_loop_iterations=10)
        for i in range(10):
            count = cost_agent.check_loop_limit("loop1")
            assert count == i + 1

    def test_check_loop_limit_exceeded(self, cost_agent):
        """Test loop limit exceeded."""
        cost_agent.configure_budget(max_loop_iterations=5)
        for i in range(5):
            cost_agent.check_loop_limit("loop1")
        with pytest.raises(RecursionLimitError) as exc_info:
            cost_agent.check_loop_limit("loop1")
        assert exc_info.value.limit_type == "loop_iterations"

    def test_reset_loop_counter(self, cost_agent):
        """Test resetting loop counter."""
        cost_agent.check_loop_limit("loop1")
        cost_agent.check_loop_limit("loop1")
        assert cost_agent._loop_counters["loop1"] == 2
        cost_agent.reset_loop_counter("loop1")
        assert "loop1" not in cost_agent._loop_counters


class TestBudgetStatus:
    """Test budget status reporting."""

    def test_get_budget_status(self, cost_agent):
        """Test getting budget status."""
        cost_agent.record_token_usage(1000, 500, "gpt-4o")
        status = cost_agent.get_budget_status()
        assert status["session_tokens"] == 1500
        assert status["operations_count"] == 1
        assert "token_usage_pct" in status
        assert "cost_usage_pct" in status

    def test_reset_session(self, cost_agent):
        """Test session reset."""
        cost_agent.record_token_usage(1000, 500, "gpt-4o")
        summary = cost_agent.reset_session()
        assert summary["total_tokens"] == 1500
        assert cost_agent._total_session_tokens == 0
        assert cost_agent._total_session_cost == 0.0
        assert len(cost_agent._session_token_usage) == 0


# =============================================================================
# ContextManagementMixin Tests
# =============================================================================


class TestContextManagementInitialization:
    """Test ContextManagementMixin initialization."""

    def test_initialization_flag_set(self, context_agent):
        """Verify initialization flag is set."""
        assert context_agent._context_management_initialized is True

    def test_default_context_config(self, context_agent):
        """Verify default context configuration."""
        config = context_agent._context_config
        assert config.max_context_tokens == 128000
        assert config.target_context_tokens == 100000
        assert config.summarization_threshold_pct == 0.75

    def test_context_storage_initialized(self, context_agent):
        """Verify context storage is initialized."""
        assert context_agent._context_items == []
        assert context_agent._total_context_tokens == 0


class TestContextConfiguration:
    """Test context configuration methods."""

    def test_configure_context_partial(self, context_agent):
        """Test partial context configuration."""
        context_agent.configure_context(max_context_tokens=32000)
        assert context_agent._context_config.max_context_tokens == 32000
        assert context_agent._context_config.target_context_tokens == 100000  # Unchanged

    def test_configure_context_full(self, context_agent):
        """Test full context configuration."""
        context_agent.configure_context(
            max_context_tokens=64000,
            target_context_tokens=50000,
            summarization_threshold_pct=0.6,
            prune_threshold_pct=0.85,
            min_context_tokens=2000,
            summary_target_tokens=1000,
        )
        config = context_agent._context_config
        assert config.max_context_tokens == 64000
        assert config.target_context_tokens == 50000
        assert config.summarization_threshold_pct == 0.6
        assert config.prune_threshold_pct == 0.85


class TestTokenEstimation:
    """Test token estimation methods."""

    def test_estimate_tokens_basic(self, context_agent):
        """Test basic token estimation."""
        # ~4 chars per token
        text = "a" * 100
        tokens = context_agent.estimate_tokens(text)
        assert tokens == 25

    def test_estimate_tokens_minimum(self, context_agent):
        """Test minimum token estimation."""
        tokens = context_agent.estimate_tokens("a")
        assert tokens >= 1


class TestContextAddition:
    """Test adding context items."""

    def test_add_context_basic(self, context_agent):
        """Test basic context addition."""
        item = context_agent.add_context("Hello world", ContextPriority.MEDIUM)
        assert isinstance(item, ContextItem)
        assert item.content == "Hello world"
        assert item.priority == ContextPriority.MEDIUM
        assert len(context_agent._context_items) == 1

    def test_add_context_accumulates_tokens(self, context_agent):
        """Test context token accumulation."""
        context_agent.add_context("a" * 100, ContextPriority.MEDIUM)  # ~25 tokens
        context_agent.add_context("b" * 200, ContextPriority.HIGH)  # ~50 tokens
        assert context_agent._total_context_tokens == 75

    def test_add_context_with_metadata(self, context_agent):
        """Test adding context with metadata."""
        item = context_agent.add_context(
            "Test content",
            ContextPriority.HIGH,
            metadata={"source": "test", "timestamp": 123},
        )
        assert item.metadata["source"] == "test"
        assert item.metadata["timestamp"] == 123


class TestContextPriorities:
    """Test context priority handling."""

    def test_priority_ordering(self):
        """Test priority enum ordering."""
        assert ContextPriority.CRITICAL.value < ContextPriority.HIGH.value
        assert ContextPriority.HIGH.value < ContextPriority.MEDIUM.value
        assert ContextPriority.MEDIUM.value < ContextPriority.LOW.value

    def test_add_context_different_priorities(self, context_agent):
        """Test adding context with different priorities."""
        context_agent.add_context("Critical", ContextPriority.CRITICAL)
        context_agent.add_context("High", ContextPriority.HIGH)
        context_agent.add_context("Medium", ContextPriority.MEDIUM)
        context_agent.add_context("Low", ContextPriority.LOW)
        assert len(context_agent._context_items) == 4


class TestContextPruning:
    """Test context pruning functionality."""

    def test_prune_low_priority_first(self, context_agent):
        """Test that low priority items are pruned first."""
        context_agent.configure_context(max_context_tokens=100, target_context_tokens=50)
        context_agent.add_context("a" * 80, ContextPriority.HIGH)  # 20 tokens
        context_agent.add_context("b" * 80, ContextPriority.LOW)  # 20 tokens
        context_agent.add_context("c" * 80, ContextPriority.LOW)  # 20 tokens

        # Force pruning by adding more
        context_agent._prune_low_priority_context(target_tokens=40)

        # Should have pruned LOW priority items
        remaining_priorities = [item.priority for item in context_agent._context_items]
        assert ContextPriority.HIGH in remaining_priorities

    def test_critical_never_pruned(self, context_agent):
        """Test that critical items are never pruned."""
        context_agent.configure_context(max_context_tokens=100, target_context_tokens=50)
        context_agent.add_context("critical", ContextPriority.CRITICAL)
        context_agent.add_context("low", ContextPriority.LOW)

        context_agent._prune_by_priority(ContextPriority.CRITICAL, target_tokens=10)

        # Critical should still be there
        critical_items = [
            item
            for item in context_agent._context_items
            if item.priority == ContextPriority.CRITICAL
        ]
        assert len(critical_items) == 1


class TestOptimizedContext:
    """Test optimized context retrieval."""

    def test_get_optimized_context_ordering(self, context_agent):
        """Test that optimized context is properly ordered."""
        context_agent.add_context("Low priority", ContextPriority.LOW)
        context_agent.add_context("Critical priority", ContextPriority.CRITICAL)
        context_agent.add_context("High priority", ContextPriority.HIGH)

        optimized = context_agent.get_optimized_context()

        # Critical should come first
        assert optimized.startswith("Critical priority")


class TestContextStatus:
    """Test context status reporting."""

    def test_get_context_status(self, context_agent):
        """Test getting context status."""
        context_agent.add_context("Test", ContextPriority.MEDIUM)
        status = context_agent.get_context_status()
        assert status["item_count"] == 1
        assert "total_tokens" in status
        assert "usage_pct" in status
        assert "priority_distribution" in status

    def test_clear_context_preserve_critical(self, context_agent):
        """Test clearing context while preserving critical items."""
        context_agent.add_context("Critical", ContextPriority.CRITICAL)
        context_agent.add_context("Medium", ContextPriority.MEDIUM)
        context_agent.add_context("Low", ContextPriority.LOW)

        summary = context_agent.clear_context(preserve_critical=True)

        assert summary["items_cleared"] == 2
        assert len(context_agent._context_items) == 1
        assert context_agent._context_items[0].priority == ContextPriority.CRITICAL

    def test_clear_context_all(self, context_agent):
        """Test clearing all context."""
        context_agent.add_context("Critical", ContextPriority.CRITICAL)
        context_agent.add_context("Medium", ContextPriority.MEDIUM)

        summary = context_agent.clear_context(preserve_critical=False)

        assert summary["items_cleared"] == 2
        assert len(context_agent._context_items) == 0


# =============================================================================
# Combined Agent Tests
# =============================================================================


class TestCombinedAgent:
    """Test combined Phase 1 functionality."""

    def test_combined_initialization(self, combined_agent):
        """Test combined agent initializes both mixins."""
        assert combined_agent._cost_guardrail_initialized is True
        assert combined_agent._context_management_initialized is True

    def test_combined_cost_and_context(self, combined_agent):
        """Test using both cost and context features together."""
        # Add context
        combined_agent.add_context("User query", ContextPriority.HIGH)

        # Record token usage
        combined_agent.record_token_usage(100, 50, "gpt-4o")

        # Verify both tracked
        assert combined_agent._total_context_tokens > 0
        assert combined_agent._total_session_tokens == 150

    def test_combined_budget_and_context_limits(self, combined_agent):
        """Test budget and context limits work together."""
        combined_agent.configure_budget(max_tokens_per_session=1000)
        combined_agent.configure_context(max_context_tokens=500)

        # Both should be independently configurable
        assert combined_agent._budget_config.max_tokens_per_session == 1000
        assert combined_agent._context_config.max_context_tokens == 500


# =============================================================================
# Edge Cases and Error Handling
# =============================================================================


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_zero_token_usage(self, cost_agent):
        """Test recording zero tokens."""
        usage = cost_agent.record_token_usage(0, 0, "gpt-4o")
        assert usage.total_tokens == 0
        assert usage.estimated_cost_usd == 0.0

    def test_empty_context(self, context_agent):
        """Test getting optimized context when empty."""
        optimized = context_agent.get_optimized_context()
        assert optimized == ""

    def test_context_item_id_generation(self, context_agent):
        """Test that context items get unique IDs."""
        item1 = context_agent.add_context("Content 1", ContextPriority.MEDIUM)
        item2 = context_agent.add_context("Content 2", ContextPriority.MEDIUM)
        assert item1.item_id != item2.item_id

    def test_thread_safety_cost(self, cost_agent):
        """Test that cost operations are thread-safe."""
        import threading

        errors = []

        def record_usage():
            try:
                for _ in range(10):
                    cost_agent.record_token_usage(10, 5, "gpt-4o")
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=record_usage) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert cost_agent._total_session_tokens == 750  # 5 threads * 10 ops * 15 tokens

    def test_thread_safety_context(self, context_agent):
        """Test that context operations are thread-safe."""
        import threading

        errors = []

        def add_context():
            try:
                for i in range(10):
                    context_agent.add_context(f"Content {i}", ContextPriority.MEDIUM)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=add_context) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert len(context_agent._context_items) == 50  # 5 threads * 10 items
