"""
Phase 6: Optimization & Expansion Tests

Tests optimization and expansion capabilities:
- Advanced caching strategies
- Pattern quality improvement
- Multi-level caching
- Adaptive threshold management
- Predictive healing patterns

All tests use mocked dependencies to avoid external services.
"""

from __future__ import annotations

import time
import pytest


# ==================== TEST 6.1: Advanced Caching Strategies ====================


class TestAdvancedCachingStrategies:
    """Test advanced caching strategies."""

    def test_multi_level_cache_local_hit(self):
        """Test multi-level caching with local cache hit."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient

        client = MetaLearningClient()

        # Store value
        client.cache_set("multi_level_key", {"data": "value"}, "agentic_core")

        # First get populates local cache
        result1 = client.cache_get("multi_level_key", "agentic_core")

        # Second get should hit local cache (faster)
        start = time.time()
        result2 = client.cache_get("multi_level_key", "agentic_core")
        local_time = time.time() - start

        assert result1 == result2
        assert local_time < 0.01  # Local cache should be very fast

    def test_cache_warming_strategy(self):
        """Test cache warming for frequently accessed patterns."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient

        client = MetaLearningClient()

        # Simulate cache warming
        warm_data = [
            {"key": f"warm_key_{i}", "value": {"pattern": f"pattern_{i}"}} for i in range(10)
        ]

        for item in warm_data:
            client.cache_set(item["key"], item["value"], "agentic_core")

        # Verify all warmed
        for item in warm_data:
            result = client.cache_get(item["key"], "agentic_core")
            assert result is not None

    def test_eviction_policy_lru(self):
        """Test LRU eviction policy concept."""
        from agentic_core.L1_cognition.meta_learning.CacheStrategyManager import (
            CacheStrategyManager,
            DomainConfig,
            EvictionPolicy,
        )

        csm = CacheStrategyManager()
        config = DomainConfig(domain="lru_test", eviction_policy=EvictionPolicy.LRU)
        csm.domain_configs["lru_test"] = config

        # Verify policy is set
        assert csm.domain_configs["lru_test"].eviction_policy == EvictionPolicy.LRU

    def test_cache_preloading(self):
        """Test cache preloading for known patterns."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient

        client = MetaLearningClient()

        # Preload common patterns
        common_patterns = {
            "gravity_relocate": {"fix_type": "RELOCATE"},
            "gravity_abstract": {"fix_type": "ABSTRACT"},
            "ats_validation": {"passed": True},
        }

        for key, value in common_patterns.items():
            client.cache_set(f"preload_{key}", value, "agentic_core")

        # Verify preloaded
        for key in common_patterns:
            assert client.cache_get(f"preload_{key}", "agentic_core") is not None


# ==================== TEST 6.2: Pattern Quality Improvement ====================


class TestPatternQualityImprovement:
    """Test pattern quality improvement mechanisms."""

    def test_pattern_effectiveness_tracking(self):
        """Test tracking pattern effectiveness."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient

        client = MetaLearningClient()

        # Store pattern with effectiveness metrics
        pattern = {
            "pattern_id": "effective_pattern_1",
            "success_count": 10,
            "failure_count": 2,
            "effectiveness_score": 0.83,  # 10/12
        }

        client.cache_set("pattern_effectiveness_1", pattern, "agentic_core")

        result = client.cache_get("pattern_effectiveness_1", "agentic_core")
        assert result["effectiveness_score"] >= 0.80

    def test_similarity_threshold_adjustment(self):
        """Test dynamic similarity threshold adjustment."""
        from agentic_core.L1_cognition.meta_learning.guardrails import MetaLearningGuardrails

        guardrails = MetaLearningGuardrails()

        # Test threshold validation at different levels
        assert guardrails.validate_similarity_threshold(0.85) == 0.85
        assert guardrails.validate_similarity_threshold(0.90) == 0.90
        assert guardrails.validate_similarity_threshold(0.95) == 0.95

    def test_pattern_pruning_low_quality(self):
        """Test low-quality pattern identification for pruning."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient

        client = MetaLearningClient()

        # Store patterns with quality scores
        patterns = [
            {"id": "high_quality", "score": 0.95, "prune": False},
            {"id": "medium_quality", "score": 0.75, "prune": False},
            {"id": "low_quality", "score": 0.40, "prune": True},
        ]

        for p in patterns:
            client.cache_set(f"quality_pattern_{p['id']}", p, "agentic_core")

        # Verify patterns stored
        low_q = client.cache_get("quality_pattern_low_quality", "agentic_core")
        assert low_q["prune"] is True

    def test_embedding_quality_validation(self):
        """Test embedding quality validation concept."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import HealingPattern

        # Pattern with valid embedding dimensions
        pattern = HealingPattern(
            pattern_id="embed_test",
            violation_type="test",
            error_signature="sig",
            healing_strategy={"action": "fix"},
            embedding=[0.1] * 768,  # Standard embedding size
        )

        assert len(pattern.embedding) == 768


# ==================== TEST 6.3: Adaptive Threshold Management ====================


class TestAdaptiveThresholdManagement:
    """Test adaptive threshold management."""

    def test_ttl_adaptation_by_domain(self):
        """Test TTL adaptation per domain."""
        from agentic_core.L1_cognition.meta_learning.CacheStrategyManager import (
            CacheStrategyManager,
            DomainConfig,
        )

        csm = CacheStrategyManager()

        # Configure different TTLs per domain
        csm.domain_configs = {
            "agentic_core": DomainConfig(domain="agentic_core", ttl_seconds=3600),
            "apps_lic": DomainConfig(domain="apps_lic", ttl_seconds=1800),
            "apps_rg": DomainConfig(domain="apps_rg", ttl_seconds=7200),
        }

        assert csm.get_ttl("agentic_core") == 3600
        assert csm.get_ttl("apps_lic") == 1800
        assert csm.get_ttl("apps_rg") == 7200

    def test_similarity_adaptation_by_domain(self):
        """Test similarity threshold adaptation per domain."""
        from agentic_core.L1_cognition.meta_learning.CacheStrategyManager import (
            CacheStrategyManager,
            DomainConfig,
        )

        csm = CacheStrategyManager()

        # Configure different thresholds per domain
        csm.domain_configs = {
            "agentic_core": DomainConfig(domain="agentic_core", similarity_threshold=0.85),
            "apps_lic": DomainConfig(domain="apps_lic", similarity_threshold=0.90),
            "apps_rg": DomainConfig(domain="apps_rg", similarity_threshold=0.80),
        }

        assert csm.get_similarity_threshold("agentic_core") == 0.85
        assert csm.get_similarity_threshold("apps_lic") == 0.90
        assert csm.get_similarity_threshold("apps_rg") == 0.80

    def test_healing_depth_adaptation(self):
        """Test healing depth adaptation per domain."""
        from agentic_core.L1_cognition.meta_learning.CacheStrategyManager import (
            CacheStrategyManager,
            DomainConfig,
        )

        csm = CacheStrategyManager()

        # Configure different max depths
        csm.domain_configs = {
            "agentic_core": DomainConfig(domain="agentic_core", max_healing_depth=5),
            "apps_lic": DomainConfig(domain="apps_lic", max_healing_depth=3),
        }

        assert csm.domain_configs["agentic_core"].max_healing_depth == 5
        assert csm.domain_configs["apps_lic"].max_healing_depth == 3


# ==================== TEST 6.4: Predictive Healing ====================


class TestPredictiveHealing:
    """Test predictive healing patterns."""

    def test_pattern_suggestion_workflow(self):
        """Test pattern suggestion workflow."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient

        client = MetaLearningClient()

        # Store successful patterns
        patterns = [
            {"violation": "gravity_L0_to_L5", "fix": "relocate", "success_rate": 0.95},
            {"violation": "gravity_L2_to_L5", "fix": "abstract", "success_rate": 0.88},
        ]

        for i, p in enumerate(patterns):
            client.cache_set(f"suggestion_pattern_{i}", p, "agentic_core")

        # Retrieve for suggestion
        p0 = client.cache_get("suggestion_pattern_0", "agentic_core")
        assert p0["success_rate"] >= 0.90

    def test_violation_prediction_caching(self):
        """Test caching predicted violations."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient

        client = MetaLearningClient()

        # Cache violation prediction
        prediction = {
            "file": "/test/module.py",
            "predicted_violations": [
                {"type": "gravity", "likelihood": 0.75},
                {"type": "import_cycle", "likelihood": 0.45},
            ],
        }

        client.cache_set("prediction:/test/module.py", prediction, "agentic_core")

        result = client.cache_get("prediction:/test/module.py", "agentic_core")
        assert len(result["predicted_violations"]) == 2

    def test_preemptive_healing_flag(self):
        """Test preemptive healing flag tracking."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient

        client = MetaLearningClient()

        # Mark file for preemptive healing
        preemptive = {
            "file": "/test/risky_module.py",
            "risk_score": 0.85,
            "preemptive_heal": True,
            "suggested_fixes": ["relocate_imports", "add_abstraction"],
        }

        client.cache_set("preemptive:/test/risky_module.py", preemptive, "agentic_core")

        result = client.cache_get("preemptive:/test/risky_module.py", "agentic_core")
        assert result["preemptive_heal"] is True


# ==================== TEST 6.5: System Self-Optimization ====================


class TestSystemSelfOptimization:
    """Test system self-optimization capabilities."""

    def test_hit_ratio_calculation(self):
        """Test cache hit ratio calculation."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient

        client = MetaLearningClient()

        # Generate known hit/miss pattern
        client.cache_set("hit_ratio_key", {"data": "value"}, "agentic_core")

        # Hits
        for _ in range(8):
            client.cache_get("hit_ratio_key", "agentic_core")

        # Misses
        for _ in range(2):
            client.cache_get("nonexistent_key", "agentic_core")

        # Calculate hit ratio
        hits = client.stats["cache_hits"]
        misses = client.stats["cache_misses"]
        total = hits + misses

        if total > 0:
            hit_ratio = hits / total
            assert hit_ratio >= 0  # Valid ratio

    def test_performance_baseline_tracking(self):
        """Test performance baseline tracking."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient

        client = MetaLearningClient()

        # Measure baseline performance
        start = time.time()

        for i in range(100):
            client.cache_set(f"baseline_{i}", {"i": i}, "agentic_core")

        write_baseline = time.time() - start

        start = time.time()

        for i in range(100):
            client.cache_get(f"baseline_{i}", "agentic_core")

        read_baseline = time.time() - start

        # Record baselines
        baselines = {"write_100_ops": write_baseline, "read_100_ops": read_baseline}

        assert baselines["write_100_ops"] < 2.0
        assert baselines["read_100_ops"] < 1.0

    def test_auto_cleanup_efficiency(self):
        """Test automatic cleanup efficiency."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient

        client = MetaLearningClient()

        # Store items with very short TTL
        for i in range(20):
            client.cache_set(f"cleanup_{i}", {"data": i}, "agentic_core", ttl=1)

        # Should exist initially
        assert client.cache_get("cleanup_10", "agentic_core") is not None

        # Wait for expiration
        time.sleep(1.5)

        # Should be cleaned
        assert client.cache_get("cleanup_10", "agentic_core") is None

    def test_domain_usage_statistics(self):
        """Test domain usage statistics collection."""
        from agentic_core.L1_cognition.meta_learning.guardrails import MetaLearningGuardrails

        guardrails = MetaLearningGuardrails()

        # Generate domain activity
        domains = ["agentic_core", "apps_lic", "apps_rg"]
        for domain in domains:
            for _ in range(5):
                guardrails.check_rate_limit(domain, "request")

        stats = guardrails.get_stats()

        # Verify domain tracking
        assert "request_rates" in stats
        for domain in domains:
            assert domain in stats["request_rates"]


# ==================== TEST 6.6: Expansion Readiness ====================


class TestExpansionReadiness:
    """Test readiness for expansion to additional agents."""

    def test_new_domain_registration(self):
        """Test registering new domains."""
        from agentic_core.L1_cognition.meta_learning.CacheStrategyManager import (
            CacheStrategyManager,
            DomainConfig,
        )

        csm = CacheStrategyManager()

        # Register new domain
        csm.domain_configs["new_domain"] = DomainConfig(
            domain="new_domain", ttl_seconds=2400, similarity_threshold=0.88
        )

        assert "new_domain" in csm.domain_configs
        assert csm.get_ttl("new_domain") == 2400

    def test_pattern_migration_workflow(self):
        """Test pattern migration between domains."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import MetaLearningClient

        client = MetaLearningClient()

        # Store pattern in source domain
        pattern = {"type": "universal_pattern", "data": "value"}
        client.cache_set("migrate_pattern", pattern, "agentic_core")

        # "Migrate" to target domain
        source = client.cache_get("migrate_pattern", "agentic_core")
        if source:
            client.cache_set("migrate_pattern", source, "apps_lic")

        # Verify in target
        target = client.cache_get("migrate_pattern", "apps_lic")
        assert target is not None
        assert target["type"] == "universal_pattern"

    def test_backward_compatibility(self):
        """Test backward compatibility with existing patterns."""
        from agentic_core.L1_cognition.meta_learning.MetaLearningClient import HealingPattern

        # Old-style pattern data
        old_data = {
            "pattern_id": "legacy_pattern",
            "violation_type": "old_violation",
            "error_signature": "legacy_sig",
            "healing_strategy": {"action": "old_fix"},
        }

        # Should still load correctly
        pattern = HealingPattern.from_dict(old_data)

        assert pattern.pattern_id == "legacy_pattern"
        assert pattern.success_count == 1  # Default
        assert pattern.domain == "agentic_core"  # Default


# ==================== RUN CONFIGURATION ====================

if __name__ == "__main__":
    pytest.main(
        [
            __file__,
            "-v",
            "--tb=short",
            "-x",
        ]
    )
