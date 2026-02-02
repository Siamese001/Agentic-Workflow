"""
Phase 2 Advanced Features Test Suite.

Tests for context pruning, adaptive depth management, and performance optimization.

Author: Cascade
Date: February 2026
Phase: 2 - Advanced Features Testing
"""

import pytest

from agentic_core.L3_orchestration.workflow_engines.ContextPruningStrategy import (
    AdaptiveDepthManager,
    ContextPruningStrategy,
    CRITICAL_DNA_KEYS,
    PruningResult,
)


class TestContextPruningStrategy:
    """Test suite for ContextPruningStrategy."""

    @pytest.fixture
    def pruner(self):
        """Create test pruning strategy instance."""
        return ContextPruningStrategy(
            max_context_size=1000,  # Small size for testing
            prune_ratio=0.3,
            min_entries_to_keep=3,
            strategy="hybrid",
        )

    @pytest.fixture
    def large_context(self):
        """Create a large context for pruning tests."""
        return {
            "original_goal": "test_goal",  # Critical - should be preserved
            "dataset": "test_data",  # Critical - should be preserved
            "temp_data_1": "x" * 100,
            "temp_data_2": "y" * 100,
            "cache_value": "z" * 100,
            "result_1": "a" * 50,
            "debug_info": "b" * 100,
            "regular_key": "c" * 50,
        }

    def test_initialization(self, pruner):
        """Test pruner initializes correctly."""
        assert pruner.max_context_size == 1000
        assert pruner.prune_ratio == 0.3
        assert pruner.min_entries_to_keep == 3
        assert pruner.strategy == "hybrid"

    def test_prune_ratio_clamping(self):
        """Test that prune ratio is clamped to valid range."""
        # Test lower bound
        pruner_low = ContextPruningStrategy(prune_ratio=0.05)
        assert pruner_low.prune_ratio == 0.1

        # Test upper bound
        pruner_high = ContextPruningStrategy(prune_ratio=0.95)
        assert pruner_high.prune_ratio == 0.9

    def test_should_prune_below_threshold(self, pruner):
        """Test should_prune returns False for small contexts."""
        small_context = {"key": "value"}
        assert pruner.should_prune(small_context) is False

    def test_should_prune_above_threshold(self, pruner, large_context):
        """Test should_prune returns True for large contexts."""
        # Create context larger than threshold
        huge_context = {f"key_{i}": "x" * 200 for i in range(100)}
        assert pruner.should_prune(huge_context) is True

    def test_critical_keys_preserved(self, pruner):
        """Test that critical DNA keys are never pruned."""
        context = {
            "original_goal": "must_keep",
            "dataset": "must_keep",
            "mission_params": "must_keep",
            "temp_1": "x" * 500,
            "temp_2": "y" * 500,
            "temp_3": "z" * 500,
        }

        # Force pruning
        pruner.max_context_size = 100
        pruner.prune_context(context)

        # Critical keys should be preserved
        assert "original_goal" in context
        assert "dataset" in context
        assert "mission_params" in context

    def test_identify_preserved_keys(self, pruner):
        """Test preserved key identification."""
        context = {
            "original_goal": "goal",
            "_internal_meta": "meta",
            "mission_dna": "dna",
            "regular_key": "value",
        }

        preserved = pruner._identify_preserved_keys(context)

        assert "original_goal" in preserved
        assert "_internal_meta" in preserved
        assert "mission_dna" in preserved
        assert "regular_key" not in preserved

    def test_pruning_result_structure(self, pruner):
        """Test that pruning result has correct structure."""
        context = {"key": "value"}
        result = pruner.prune_context(context)

        assert isinstance(result, PruningResult)
        assert hasattr(result, "success")
        assert hasattr(result, "entries_removed")
        assert hasattr(result, "bytes_freed")
        assert hasattr(result, "preserved_keys")
        assert hasattr(result, "pruned_keys")

    def test_metrics_tracking(self, pruner):
        """Test that pruning metrics are tracked."""
        # Create context that needs pruning
        context = {f"key_{i}": "x" * 100 for i in range(50)}
        pruner.max_context_size = 100

        pruner.prune_context(context)

        metrics = pruner.get_metrics()
        assert metrics["total_prunes"] >= 1
        assert metrics["prune_triggers"] >= 1

    def test_record_access(self, pruner):
        """Test access recording for LRU."""
        pruner.record_access("test_key")
        assert "test_key" in pruner._access_timestamps

    def test_set_priority(self, pruner):
        """Test priority setting."""
        pruner.set_priority("high_priority", 90)
        pruner.set_priority("low_priority", 10)

        assert pruner._priority_scores["high_priority"] == 90
        assert pruner._priority_scores["low_priority"] == 10

    def test_priority_clamping(self, pruner):
        """Test priority values are clamped to 0-100."""
        pruner.set_priority("too_high", 150)
        pruner.set_priority("too_low", -50)

        assert pruner._priority_scores["too_high"] == 100
        assert pruner._priority_scores["too_low"] == 0

    def test_reset_metrics(self, pruner):
        """Test metrics reset."""
        pruner._metrics.total_prunes = 10
        pruner.reset_metrics()
        assert pruner._metrics.total_prunes == 0


class TestContextPruningStrategies:
    """Test different pruning strategies."""

    def test_lru_strategy(self):
        """Test LRU pruning strategy."""
        pruner = ContextPruningStrategy(strategy="lru", max_context_size=100)

        # Record access for some keys
        pruner.record_access("recently_accessed")

        context = {
            "recently_accessed": "x" * 100,
            "old_key": "y" * 100,
        }

        score_recent = pruner._calculate_key_score(
            "recently_accessed", context["recently_accessed"]
        )
        score_old = pruner._calculate_key_score("old_key", context["old_key"])

        # Recently accessed should have higher score (pruned later)
        assert score_recent > score_old

    def test_priority_strategy(self):
        """Test priority-based pruning strategy."""
        pruner = ContextPruningStrategy(strategy="priority", max_context_size=100)

        pruner.set_priority("high", 90)
        pruner.set_priority("low", 10)

        score_high = pruner._calculate_key_score("high", "value")
        score_low = pruner._calculate_key_score("low", "value")

        assert score_high > score_low

    def test_size_strategy(self):
        """Test size-based pruning strategy."""
        pruner = ContextPruningStrategy(strategy="size", max_context_size=100)

        score_large = pruner._calculate_key_score("large", "x" * 10000)
        score_small = pruner._calculate_key_score("small", "x")

        # Larger entries should have lower score (pruned first)
        assert score_large < score_small

    def test_hybrid_strategy(self):
        """Test hybrid pruning strategy combines factors."""
        pruner = ContextPruningStrategy(strategy="hybrid", max_context_size=100)

        # Set up various factors
        pruner.record_access("accessed_key")
        pruner.set_priority("high_priority", 90)

        # Calculate scores
        score_accessed = pruner._calculate_key_score("accessed_key", "value")
        score_temp = pruner._calculate_key_score("temp_data", "value")

        # Temp data should have lower score
        assert score_temp < score_accessed


class TestAdaptiveDepthManager:
    """Test suite for AdaptiveDepthManager."""

    @pytest.fixture
    def manager(self):
        """Create test adaptive depth manager."""
        return AdaptiveDepthManager(
            base_limit=50,
            max_limit=200,
            min_limit=10,
            enable_adaptive=True,
        )

    def test_initialization(self, manager):
        """Test manager initializes correctly."""
        assert manager.base_limit == 50
        assert manager.max_limit == 200
        assert manager.min_limit == 10
        assert manager.enable_adaptive is True

    def test_non_adaptive_returns_base(self):
        """Test non-adaptive mode returns base limit."""
        manager = AdaptiveDepthManager(base_limit=50, enable_adaptive=False)

        limit = manager.calculate_adaptive_limit({})
        assert limit == 50

    def test_low_complexity_limit(self, manager):
        """Test low complexity results in base limit."""
        simple_context = {"key": "value"}

        limit = manager.calculate_adaptive_limit(simple_context)

        # Should be close to base limit for simple context
        assert limit >= manager.min_limit
        assert limit <= manager.base_limit * 1.5

    def test_high_complexity_increases_limit(self, manager):
        """Test high complexity increases depth limit."""
        complex_context = {
            "successor_chain": list(range(15)),
            "accumulated_context": {f"key_{i}": f"value_{i}" for i in range(40)},
            "mission_params": {f"param_{i}": i for i in range(8)},
        }

        limit = manager.calculate_adaptive_limit(complex_context)

        # Should be higher than base for complex context
        assert limit >= manager.base_limit

    def test_limit_clamping(self, manager):
        """Test that limits are clamped to allowed range."""
        # Very complex context
        huge_context = {
            "successor_chain": list(range(100)),
            "accumulated_context": {f"key_{i}": "x" * 1000 for i in range(100)},
        }

        limit = manager.calculate_adaptive_limit(huge_context)

        assert limit >= manager.min_limit
        assert limit <= manager.max_limit

    def test_complexity_assessment(self, manager):
        """Test complexity assessment returns valid range."""
        context = {"key": "value"}
        complexity = manager._assess_complexity(context)

        assert 0.0 <= complexity <= 1.0

    def test_complexity_with_metrics(self, manager):
        """Test complexity assessment with metrics."""
        context = {"key": "value"}
        metrics = {"errors": 5, "total_spawns": 10}

        complexity = manager._assess_complexity(context, metrics)

        # Should be higher due to 50% error rate
        assert complexity > 0.0

    def test_should_extend_limit(self, manager):
        """Test limit extension decision."""
        # Near limit, high success rate
        should_extend = manager.should_extend_limit(
            current_depth=45,
            current_limit=50,
            success_rate=0.95,
        )
        assert should_extend is True

        # Not near limit
        should_not_extend = manager.should_extend_limit(
            current_depth=10,
            current_limit=50,
            success_rate=0.95,
        )
        assert should_not_extend is False

        # Low success rate
        should_not_extend_low = manager.should_extend_limit(
            current_depth=45,
            current_limit=50,
            success_rate=0.5,
        )
        assert should_not_extend_low is False

    def test_extension_amount(self, manager):
        """Test limit extension amount calculation."""
        # High success rate
        extension_high = manager.get_extension_amount(50, 0.95)
        assert extension_high > 0

        # Medium success rate
        extension_medium = manager.get_extension_amount(50, 0.9)
        assert extension_medium > 0
        assert extension_medium <= extension_high

        # Near max limit
        extension_near_max = manager.get_extension_amount(190, 0.95)
        assert extension_near_max <= 10  # Can't exceed max

    def test_statistics(self, manager):
        """Test statistics retrieval."""
        # Generate some history
        manager.calculate_adaptive_limit({"key": "value"})
        manager.calculate_adaptive_limit({"successor_chain": [1, 2, 3]})

        stats = manager.get_statistics()

        assert "base_limit" in stats
        assert "complexity_history_length" in stats
        assert stats["complexity_history_length"] == 2

    def test_reset_history(self, manager):
        """Test history reset."""
        manager._complexity_history = [0.5, 0.6, 0.7]
        manager._depth_history = [50, 60, 70]

        manager.reset_history()

        assert len(manager._complexity_history) == 0
        assert len(manager._depth_history) == 0


class TestCriticalDNAKeys:
    """Test critical DNA key definitions."""

    def test_critical_keys_defined(self):
        """Test that critical keys are properly defined."""
        assert "original_goal" in CRITICAL_DNA_KEYS
        assert "dataset" in CRITICAL_DNA_KEYS
        assert "mission_params" in CRITICAL_DNA_KEYS
        assert "task_dna" in CRITICAL_DNA_KEYS

    def test_critical_keys_immutable(self):
        """Test that critical keys set is immutable."""
        assert isinstance(CRITICAL_DNA_KEYS, frozenset)


class TestIntegrationScenarios:
    """Integration tests combining pruning and depth management."""

    def test_pruning_with_depth_context(self):
        """Test pruning preserves depth-related context."""
        pruner = ContextPruningStrategy(max_context_size=100)

        context = {
            "original_goal": "test",
            "_predecessor_chain": ["a", "b", "c"],
            "successor_chain": ["d", "e"],
            "temp_data": "x" * 500,
        }

        pruner.prune_context(context)

        # Depth-related keys should be preserved
        assert "original_goal" in context
        assert "_predecessor_chain" in context

    def test_adaptive_depth_with_pruned_context(self):
        """Test adaptive depth works with pruned context."""
        pruner = ContextPruningStrategy(max_context_size=500)
        manager = AdaptiveDepthManager()

        # Large context
        context = {
            "original_goal": "test",
            "successor_chain": list(range(10)),
            "temp": "x" * 1000,
        }

        # Prune context
        pruner.prune_context(context)

        # Calculate depth with pruned context
        limit = manager.calculate_adaptive_limit(context)

        # Should still work and return valid limit
        assert manager.min_limit <= limit <= manager.max_limit

    def test_end_to_end_memory_management(self):
        """Test complete memory management flow."""
        pruner = ContextPruningStrategy(
            max_context_size=500,
            prune_ratio=0.4,
            strategy="hybrid",
        )
        manager = AdaptiveDepthManager(base_limit=50)

        # Simulate growing context over iterations
        context = {
            "original_goal": "complete_mission",
            "dataset": "production",
        }

        for i in range(20):
            # Add data each iteration
            context[f"iteration_{i}"] = f"data_{i}" * 50

            # Check if pruning needed
            if pruner.should_prune(context):
                result = pruner.prune_context(context)
                assert result.success
                assert "original_goal" in context  # DNA preserved

            # Calculate adaptive limit
            limit = manager.calculate_adaptive_limit(context)
            assert limit >= manager.min_limit

        # Verify final state
        assert "original_goal" in context
        assert "dataset" in context


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
