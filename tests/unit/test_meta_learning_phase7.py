"""
Test Suite for Meta-Learning Phase 7: Observability and Optimization

Tests for:
- MetaLearningObservability functionality
- Metrics collection
- Health checks
- Performance tracking
- Dashboard data generation
"""

from __future__ import annotations

from unittest.mock import patch

import pytest


def reset_all_singletons():
    """Reset all meta-learning singletons for test isolation."""
    import agentic_core.L1_cognition.meta_learning.MetaLearningClient as mlc
    import agentic_core.L1_cognition.meta_learning.HealingMemoryEmbedder as hme
    import agentic_core.L1_cognition.meta_learning.CacheStrategyManager as csm
    import agentic_core.L1_cognition.meta_learning.DomainContextManager as dcm
    import agentic_core.L1_cognition.meta_learning.MetaLearningObservability as mlo
    from agentic_core.base_agents.meta_learning_client_mixin import (
        MetaLearningClientMixin,
    )

    mlc._meta_learning_client = None
    mlc._singleton_instance = None
    hme._healing_memory_embedder = None
    hme._embedder_singleton = None
    csm._cache_strategy_manager = None
    csm._csm_singleton = None
    dcm._domain_context_manager = None
    mlo._observability_instance = None
    MetaLearningClientMixin._ml_client = None
    MetaLearningClientMixin._ml_embedder = None
    MetaLearningClientMixin._ml_cache_manager = None


class TestMetaLearningObservability:
    """Tests for MetaLearningObservability functionality."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset singletons before each test."""
        reset_all_singletons()
        yield
        reset_all_singletons()

    def test_singleton_pattern(self):
        """Test that MetaLearningObservability follows singleton pattern."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningObservability import (
            get_meta_learning_observability,
        )

        obs1 = get_meta_learning_observability()
        obs2 = get_meta_learning_observability()

        assert obs1 is obs2

    def test_initial_health_checks_registered(self):
        """Test that initial health checks are registered."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningObservability import (
            get_meta_learning_observability,
        )

        obs = get_meta_learning_observability()

        assert "MetaLearningClient" in obs._health_status
        assert "CacheStrategyManager" in obs._health_status
        assert "DomainContextManager" in obs._health_status
        assert "Redis" in obs._health_status
        assert "Pinecone" in obs._health_status


class TestMetricsCollection:
    """Tests for metrics collection."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset singletons before each test."""
        reset_all_singletons()
        yield
        reset_all_singletons()

    def test_record_metric(self):
        """Test recording a metric."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningObservability import (
            get_meta_learning_observability,
        )

        obs = get_meta_learning_observability()

        obs.record_metric("cache_hit_rate", 0.85, tags={"domain": "apps_lic"})

        metrics = obs.get_metrics("cache_hit_rate")
        assert len(metrics) == 1
        assert metrics[0].value == 0.85
        assert metrics[0].tags["domain"] == "apps_lic"

    def test_metrics_limit(self):
        """Test that metrics are limited to max size."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningObservability import (
            get_meta_learning_observability,
        )

        obs = get_meta_learning_observability()
        obs._max_metrics = 10

        # Record more than max
        for i in range(15):
            obs.record_metric("test_metric", float(i))

        # Should be limited
        assert len(obs._metrics) == 10

    def test_get_metrics_with_filter(self):
        """Test getting metrics with name filter."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningObservability import (
            get_meta_learning_observability,
        )

        obs = get_meta_learning_observability()

        obs.record_metric("metric_a", 1.0)
        obs.record_metric("metric_b", 2.0)
        obs.record_metric("metric_a", 3.0)

        metrics_a = obs.get_metrics("metric_a")
        assert len(metrics_a) == 2

        metrics_b = obs.get_metrics("metric_b")
        assert len(metrics_b) == 1


class TestHealthChecks:
    """Tests for health check functionality."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset singletons before each test."""
        reset_all_singletons()
        yield
        reset_all_singletons()

    def test_check_health_returns_status(self):
        """Test that check_health returns status for all components."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import (
            MetaLearningClient,
        )
        from agentic_core.L1_cognition.meta_learning.MetaLearningObservability import (
            get_meta_learning_observability,
        )

        with (
            patch.object(MetaLearningClient, "_initialize_redis"),
            patch.object(MetaLearningClient, "_initialize_pinecone"),
        ):
            obs = get_meta_learning_observability()
            health = obs.check_health()

            assert "MetaLearningClient" in health
            assert "CacheStrategyManager" in health
            assert "DomainContextManager" in health

    def test_get_health_summary(self):
        """Test health summary generation."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import (
            MetaLearningClient,
        )
        from agentic_core.L1_cognition.meta_learning.MetaLearningObservability import (
            get_meta_learning_observability,
        )

        with (
            patch.object(MetaLearningClient, "_initialize_redis"),
            patch.object(MetaLearningClient, "_initialize_pinecone"),
        ):
            obs = get_meta_learning_observability()
            summary = obs.get_health_summary()

            assert "overall_healthy" in summary
            assert "healthy_components" in summary
            assert "total_components" in summary
            assert "components" in summary


class TestPerformanceTracking:
    """Tests for performance tracking."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset singletons before each test."""
        reset_all_singletons()
        yield
        reset_all_singletons()

    def test_record_operation_time(self):
        """Test recording operation time."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningObservability import (
            get_meta_learning_observability,
        )

        obs = get_meta_learning_observability()

        obs.record_operation_time("cache_get", 5.0)
        obs.record_operation_time("cache_get", 10.0)
        obs.record_operation_time("cache_get", 15.0)

        stats = obs.get_operation_stats("cache_get")

        assert stats["samples"] == 3
        assert stats["avg_ms"] == 10.0
        assert stats["min_ms"] == 5.0
        assert stats["max_ms"] == 15.0

    def test_operation_timer_context_manager(self):
        """Test OperationTimer context manager."""
        import time

        from agentic_core.L1_cognition.meta_learning.MetaLearningObservability import (
            get_meta_learning_observability,
            OperationTimer,
        )

        obs = get_meta_learning_observability()

        with OperationTimer("test_operation"):
            time.sleep(0.01)  # 10ms

        stats = obs.get_operation_stats("test_operation")
        assert stats["samples"] == 1
        assert stats["avg_ms"] >= 10  # At least 10ms

    def test_operation_samples_limit(self):
        """Test that operation samples are limited."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningObservability import (
            get_meta_learning_observability,
        )

        obs = get_meta_learning_observability()
        obs._max_operation_samples = 5

        for i in range(10):
            obs.record_operation_time("limited_op", float(i))

        assert len(obs._operation_times["limited_op"]) == 5


class TestStatTracking:
    """Tests for statistics tracking."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset singletons before each test."""
        reset_all_singletons()
        yield
        reset_all_singletons()

    def test_increment_stat(self):
        """Test incrementing statistics."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningObservability import (
            get_meta_learning_observability,
        )

        obs = get_meta_learning_observability()

        initial = obs.stats["cache_hits"]
        obs.increment_stat("cache_hits", 5)

        assert obs.stats["cache_hits"] == initial + 5

    def test_get_stats(self):
        """Test getting all statistics."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningObservability import (
            get_meta_learning_observability,
        )

        obs = get_meta_learning_observability()
        stats = obs.get_stats()

        assert "total_operations" in stats
        assert "cache_hits" in stats
        assert "cache_misses" in stats
        assert "uptime_seconds" in stats
        assert "metrics_count" in stats


class TestDashboardData:
    """Tests for dashboard data generation."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset singletons before each test."""
        reset_all_singletons()
        yield
        reset_all_singletons()

    def test_get_dashboard_data(self):
        """Test dashboard data generation."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import (
            MetaLearningClient,
        )
        from agentic_core.L1_cognition.meta_learning.MetaLearningObservability import (
            get_meta_learning_observability,
        )

        with (
            patch.object(MetaLearningClient, "_initialize_redis"),
            patch.object(MetaLearningClient, "_initialize_pinecone"),
        ):
            obs = get_meta_learning_observability()

            # Add some data
            obs.record_metric("test_metric", 1.0)
            obs.record_operation_time("test_op", 5.0)
            obs.increment_stat("cache_hits")

            dashboard = obs.get_dashboard_data()

            assert "health" in dashboard
            assert "stats" in dashboard
            assert "performance" in dashboard
            assert "recent_metrics" in dashboard

    def test_dashboard_data_structure(self):
        """Test dashboard data has correct structure."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import (
            MetaLearningClient,
        )
        from agentic_core.L1_cognition.meta_learning.MetaLearningObservability import (
            get_meta_learning_observability,
        )

        with (
            patch.object(MetaLearningClient, "_initialize_redis"),
            patch.object(MetaLearningClient, "_initialize_pinecone"),
        ):
            obs = get_meta_learning_observability()
            dashboard = obs.get_dashboard_data()

            # Health section
            assert "overall_healthy" in dashboard["health"]
            assert "components" in dashboard["health"]

            # Stats section
            assert "total_operations" in dashboard["stats"]
            assert "uptime_seconds" in dashboard["stats"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
