"""Phase 20 Tests: DNA Hardening - Singleton & MetaLearningMixin.

Tests for singleton enforcement, instinctive bypass, DNA segregation, and lobotomy resilience.
"""

from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

import pytest


class TestSingletonEnforcement:
    """Phase 20 Tests: Singleton pattern enforcement."""

    def test_singleton_get_instance(self):
        """[Phase 20] Verify get_instance returns the same instance."""
        from agentic_core.L4_state.memory.SemanticCacheManager import (
            SemanticCacheManager,
        )

        # Reset singleton for clean test
        SemanticCacheManager.reset_instance()

        # Use resilient mode for this test
        original_strict = os.environ.get("HIVE_MIND_STRICT_MODE")
        os.environ["HIVE_MIND_STRICT_MODE"] = "false"

        try:
            with patch("redis.from_url") as mock_redis:
                mock_redis.return_value.ping.side_effect = Exception("Redis unavailable")

                instance1 = SemanticCacheManager.get_instance()
                instance2 = SemanticCacheManager.get_instance()

                assert instance1 is instance2
        finally:
            if original_strict:
                os.environ["HIVE_MIND_STRICT_MODE"] = original_strict
            else:
                os.environ.pop("HIVE_MIND_STRICT_MODE", None)
            SemanticCacheManager.reset_instance()

    def test_singleton_direct_instantiation_blocked(self):
        """[Phase 20] Verify direct instantiation raises RuntimeError."""
        from agentic_core.L4_state.memory.SemanticCacheManager import (
            SemanticCacheManager,
        )

        # Reset singleton
        SemanticCacheManager.reset_instance()

        # Use resilient mode for this test
        original_strict = os.environ.get("HIVE_MIND_STRICT_MODE")
        os.environ["HIVE_MIND_STRICT_MODE"] = "false"

        try:
            with patch("redis.from_url") as mock_redis:
                mock_redis.return_value.ping.side_effect = Exception("Redis unavailable")

                # First, create via get_instance
                SemanticCacheManager.get_instance()

                # Now direct instantiation should fail
                with pytest.raises(RuntimeError) as exc_info:
                    SemanticCacheManager()

                assert "SINGLETON VIOLATION" in str(exc_info.value)
        finally:
            if original_strict:
                os.environ["HIVE_MIND_STRICT_MODE"] = original_strict
            else:
                os.environ.pop("HIVE_MIND_STRICT_MODE", None)
            SemanticCacheManager.reset_instance()

    def test_singleton_thread_safe(self):
        """[Phase 20] Verify singleton is thread-safe."""
        import threading

        from agentic_core.L4_state.memory.SemanticCacheManager import (
            SemanticCacheManager,
        )

        # Reset singleton
        SemanticCacheManager.reset_instance()

        # Use resilient mode for this test
        original_strict = os.environ.get("HIVE_MIND_STRICT_MODE")
        os.environ["HIVE_MIND_STRICT_MODE"] = "false"

        instances = []

        try:
            with patch("redis.from_url") as mock_redis:
                mock_redis.return_value.ping.side_effect = Exception("Redis unavailable")

                def get_instance():
                    instances.append(SemanticCacheManager.get_instance())

                threads = [threading.Thread(target=get_instance) for _ in range(10)]

                for t in threads:
                    t.start()
                for t in threads:
                    t.join()

            # All instances should be the same
            assert len({id(i) for i in instances}) == 1
        finally:
            if original_strict:
                os.environ["HIVE_MIND_STRICT_MODE"] = original_strict
            else:
                os.environ.pop("HIVE_MIND_STRICT_MODE", None)
            SemanticCacheManager.reset_instance()


class TestInstinctiveBypass:
    """Phase 20 Tests: recall_or_execute bypass behavior."""

    def test_instinctive_bypass_cached(self):
        """[Phase 20] Verify recall_or_execute returns cached result without executing."""
        from agentic_core.base_agents.meta_learning_mixin import (
            MetaLearningMixin,
        )
        from agentic_core.L4_state.memory.SemanticCacheManager import (
            SemanticCacheManager,
        )

        # Reset singleton and mixin state
        SemanticCacheManager.reset_instance()
        MetaLearningMixin._memory = None
        MetaLearningMixin._lobotomized = False

        # Create a test agent class
        class TestAgent(MetaLearningMixin):
            pass

        # Mock the memory
        mock_memory = MagicMock()
        mock_memory.recall.return_value = {"result": "cached_success"}

        with patch("redis.from_url") as mock_redis:
            mock_redis.return_value.ping.side_effect = Exception("Redis unavailable")

            agent = TestAgent()
            MetaLearningMixin._memory = mock_memory
            MetaLearningMixin._lobotomized = False  # Ensure not lobotomized

            # This should NOT be called
            def should_not_run():
                raise Exception("Should not run - cache should bypass")

            result = agent.recall_or_execute("Task A", should_not_run)

            assert result == {"result": "cached_success"}
            mock_memory.recall.assert_called_once()

        # Clean up
        SemanticCacheManager.reset_instance()
        MetaLearningMixin._memory = None
        MetaLearningMixin._lobotomized = False

    def test_instinctive_bypass_miss_executes(self):
        """[Phase 20] Verify recall_or_execute executes on cache miss."""
        from agentic_core.base_agents.meta_learning_mixin import (
            MetaLearningMixin,
        )
        from agentic_core.L4_state.memory.SemanticCacheManager import (
            SemanticCacheManager,
        )

        # Reset singleton and mixin state
        SemanticCacheManager.reset_instance()
        MetaLearningMixin._memory = None
        MetaLearningMixin._lobotomized = False

        class TestAgent(MetaLearningMixin):
            pass

        # Mock the memory to return None (cache miss)
        mock_memory = MagicMock()
        mock_memory.recall.return_value = None

        with patch("redis.from_url") as mock_redis:
            mock_redis.return_value.ping.side_effect = Exception("Redis unavailable")

            agent = TestAgent()
            MetaLearningMixin._memory = mock_memory
            MetaLearningMixin._lobotomized = False  # Ensure not lobotomized

            execution_count = {"count": 0}

            def execute_fn():
                execution_count["count"] += 1
                return {"result": "executed"}

            result = agent.recall_or_execute("Task B", execute_fn)

            assert result == {"result": "executed"}
            assert execution_count["count"] == 1
            mock_memory.learn.assert_called_once()

        # Clean up
        SemanticCacheManager.reset_instance()
        MetaLearningMixin._memory = None
        MetaLearningMixin._lobotomized = False


class TestDNASegregation:
    """Phase 20 Tests: Namespace segregation between agent types."""

    def test_dna_segregation_different_agents(self):
        """[Phase 20] Verify different agents use different namespaces."""
        from agentic_core.base_agents.meta_learning_mixin import (
            MetaLearningMixin,
        )
        from agentic_core.L4_state.memory.SemanticCacheManager import (
            SemanticCacheManager,
        )

        # Reset singleton and mixin state
        SemanticCacheManager.reset_instance()
        MetaLearningMixin._memory = None
        MetaLearningMixin._lobotomized = False

        class GovernorAgent(MetaLearningMixin):
            pass

        class RouterAgent(MetaLearningMixin):
            pass

        # Mock memory that tracks namespace
        mock_memory = MagicMock()
        recall_calls = []

        def track_recall(context, namespace):
            recall_calls.append(namespace)
            # Only return result for Governor
            if namespace == "GovernorAgent":
                return {"result": "Governor Result"}
            return None

        mock_memory.recall.side_effect = track_recall

        with patch("redis.from_url") as mock_redis:
            mock_redis.return_value.ping.side_effect = Exception("Redis unavailable")

            governor = GovernorAgent()
            router = RouterAgent()
            MetaLearningMixin._memory = mock_memory
            MetaLearningMixin._lobotomized = False

            # Governor learns "Prompt X"
            governor.learn_experience("Prompt X", {"result": "Governor Result"})

            # Governor recalls "Prompt X" - should hit
            gov_result = governor.recall_experience("Prompt X")
            assert gov_result == {"result": "Governor Result"}

            # router recalls "Prompt X" - should miss (different namespace)
            router_result = router.recall_experience("Prompt X")
            assert router_result is None

            # Verify namespaces were different
            assert "GovernorAgent" in recall_calls
            assert "RouterAgent" in recall_calls

        # Clean up
        SemanticCacheManager.reset_instance()
        MetaLearningMixin._memory = None
        MetaLearningMixin._lobotomized = False

    def test_namespace_derived_from_class_name(self):
        """[Phase 20] Verify namespace is derived from class name."""
        from agentic_core.base_agents.meta_learning_mixin import (
            MetaLearningMixin,
        )

        class CustomAgentName(MetaLearningMixin):
            pass

        with patch("redis.from_url") as mock_redis:
            mock_redis.return_value.ping.side_effect = Exception("Redis unavailable")

            MetaLearningMixin._memory = None
            MetaLearningMixin._lobotomized = False
            agent = CustomAgentName()

            assert agent._namespace == "CustomAgentName"

        MetaLearningMixin._memory = None
        MetaLearningMixin._lobotomized = False


class TestLobotomyResilience:
    """Phase 20 Tests: Graceful degradation when memory is unavailable."""

    def test_lobotomy_resilience_redis_down(self):
        """[Phase 20] Verify agent works when Redis is down (resilient mode)."""
        from agentic_core.L4_state.memory.SemanticCacheManager import (
            SemanticCacheManager,
        )

        # Reset singleton
        SemanticCacheManager.reset_instance()

        # Use resilient mode for this test
        original_strict = os.environ.get("HIVE_MIND_STRICT_MODE")
        os.environ["HIVE_MIND_STRICT_MODE"] = "false"

        try:
            with patch("redis.from_url") as mock_redis:
                mock_redis.return_value.ping.side_effect = Exception("Connection refused")

                # Should not crash
                cache = SemanticCacheManager.get_instance()

                # Redis should be disabled
                assert cache.redis_enabled is False

                # Recall should return None gracefully
                result = cache.recall("test context", "TestAgent")
                assert result is None
        finally:
            if original_strict:
                os.environ["HIVE_MIND_STRICT_MODE"] = original_strict
            else:
                os.environ.pop("HIVE_MIND_STRICT_MODE", None)
            SemanticCacheManager.reset_instance()

    def test_lobotomy_resilience_execution_continues(self):
        """[Phase 20] Verify execution continues when memory is unavailable."""
        from agentic_core.base_agents.meta_learning_mixin import (
            MetaLearningMixin,
        )
        from agentic_core.L4_state.memory.SemanticCacheManager import (
            SemanticCacheManager,
        )

        # Reset singleton and mixin state
        SemanticCacheManager.reset_instance()
        MetaLearningMixin._memory = None
        MetaLearningMixin._lobotomized = False

        class TestAgent(MetaLearningMixin):
            pass

        with patch("redis.from_url") as mock_redis:
            mock_redis.return_value.ping.side_effect = Exception("Connection refused")

            agent = TestAgent()

            # Set lobotomized state to simulate complete failure
            MetaLearningMixin._lobotomized = True
            MetaLearningMixin._memory = None

            execution_count = {"count": 0}

            def execute_fn():
                execution_count["count"] += 1
                return {"result": "executed_despite_lobotomy"}

            # Should execute without crashing
            result = agent.recall_or_execute("Task", execute_fn)

            assert result == {"result": "executed_despite_lobotomy"}
            assert execution_count["count"] == 1

        # Clean up
        SemanticCacheManager.reset_instance()
        MetaLearningMixin._memory = None
        MetaLearningMixin._lobotomized = False

    def test_lobotomy_warning_logged(self, caplog):
        """[Phase 20] Verify STATELESS warning is logged when Redis unavailable (resilient mode)."""
        import logging

        from agentic_core.L4_state.memory.SemanticCacheManager import (
            SemanticCacheManager,
        )

        # Reset singleton
        SemanticCacheManager.reset_instance()

        # Use resilient mode for this test
        original_strict = os.environ.get("HIVE_MIND_STRICT_MODE")
        os.environ["HIVE_MIND_STRICT_MODE"] = "false"

        try:
            with caplog.at_level(logging.ERROR):
                with patch("redis.from_url") as mock_redis:
                    mock_redis.return_value.ping.side_effect = Exception("Connection refused")

                    SemanticCacheManager.get_instance()

            # Check for STATELESS warning (resilient mode logs this)
            assert any("STATELESS" in record.message for record in caplog.records)
        finally:
            if original_strict:
                os.environ["HIVE_MIND_STRICT_MODE"] = original_strict
            else:
                os.environ.pop("HIVE_MIND_STRICT_MODE", None)
            SemanticCacheManager.reset_instance()


class TestContextHashing:
    """Phase 20 Tests: Context hash generation."""

    def test_context_hash_consistency(self):
        """[Phase 20] Verify context hash is consistent."""
        from agentic_core.base_agents.meta_learning_mixin import (
            MetaLearningMixin,
        )

        class TestAgent(MetaLearningMixin):
            pass

        MetaLearningMixin._memory = None
        MetaLearningMixin._lobotomized = False

        with patch("redis.from_url") as mock_redis:
            mock_redis.return_value.ping.side_effect = Exception("Redis unavailable")

            agent = TestAgent()

            hash1 = agent._generate_context_hash("test context")
            hash2 = agent._generate_context_hash("test context")

            assert hash1 == hash2

        MetaLearningMixin._lobotomized = False

    def test_context_hash_includes_namespace(self):
        """[Phase 20] Verify context hash includes namespace for segregation."""
        from agentic_core.base_agents.meta_learning_mixin import (
            MetaLearningMixin,
        )

        class AgentA(MetaLearningMixin):
            pass

        class AgentB(MetaLearningMixin):
            pass

        MetaLearningMixin._memory = None
        MetaLearningMixin._lobotomized = False

        with patch("redis.from_url") as mock_redis:
            mock_redis.return_value.ping.side_effect = Exception("Redis unavailable")

            agent_a = AgentA()
            agent_b = AgentB()

            # Same context, different agents = different hashes
            hash_a = agent_a._generate_context_hash("same context")
            hash_b = agent_b._generate_context_hash("same context")

            assert hash_a != hash_b

        MetaLearningMixin._memory = None
        MetaLearningMixin._lobotomized = False


class TestCircuitBreaker:
    """Phase 20 Tests: Circuit breaker behavior."""

    def test_circuit_breaker_activates_on_failure(self):
        """[Phase 20] Verify circuit breaker activates when Hive Mind unavailable."""
        from agentic_core.base_agents.meta_learning_mixin import (
            MetaLearningMixin,
        )
        from agentic_core.L4_state.memory.SemanticCacheManager import (
            SemanticCacheManager,
        )

        # Reset state
        SemanticCacheManager.reset_instance()
        MetaLearningMixin._memory = None
        MetaLearningMixin._lobotomized = False

        class TestAgent(MetaLearningMixin):
            pass

        with patch("redis.from_url") as mock_redis:
            mock_redis.return_value.ping.side_effect = Exception("Connection refused")

            with patch.object(
                SemanticCacheManager, "get_instance", side_effect=Exception("Hive Mind down")
            ):
                TestAgent()

        # Circuit breaker should be active
        assert MetaLearningMixin._lobotomized is True

        # Clean up
        MetaLearningMixin._lobotomized = False
        MetaLearningMixin._memory = None

    def test_circuit_breaker_bypasses_memory_calls(self):
        """[Phase 20] Verify lobotomized state bypasses all memory operations."""
        from agentic_core.base_agents.meta_learning_mixin import (
            MetaLearningMixin,
        )

        class TestAgent(MetaLearningMixin):
            pass

        # Force lobotomized state
        MetaLearningMixin._lobotomized = True
        MetaLearningMixin._memory = MagicMock()  # Should NOT be called

        with patch("redis.from_url") as mock_redis:
            mock_redis.return_value.ping.side_effect = Exception("Redis unavailable")

            agent = TestAgent()

            # All memory operations should be bypassed
            assert agent.recall_experience("test") is None
            agent.learn_experience("test", {"result": "data"})
            assert agent.get_memory_stats() is None

            # Memory should NOT have been called
            MetaLearningMixin._memory.recall.assert_not_called()
            MetaLearningMixin._memory.learn.assert_not_called()

        # Clean up
        MetaLearningMixin._lobotomized = False
        MetaLearningMixin._memory = None

    def test_reset_lobotomy(self):
        """[Phase 20] Verify reset_lobotomy clears circuit breaker state."""
        from agentic_core.base_agents.meta_learning_mixin import (
            MetaLearningMixin,
        )

        # Set lobotomized state
        MetaLearningMixin._lobotomized = True
        MetaLearningMixin._memory = MagicMock()

        # Reset
        MetaLearningMixin.reset_lobotomy()

        assert MetaLearningMixin._lobotomized is False
        assert MetaLearningMixin._memory is None


class TestSerializationGuard:
    """Phase 20 Tests: Serialization guard behavior."""

    def test_non_dict_result_wrapped(self):
        """[Phase 20] Verify non-dict results are wrapped for storage."""
        from agentic_core.base_agents.meta_learning_mixin import (
            MetaLearningMixin,
        )

        class TestAgent(MetaLearningMixin):
            pass

        mock_memory = MagicMock()
        mock_memory.recall.return_value = None

        MetaLearningMixin._memory = mock_memory
        MetaLearningMixin._lobotomized = False

        with patch("redis.from_url") as mock_redis:
            mock_redis.return_value.ping.side_effect = Exception("Redis unavailable")

            agent = TestAgent()

            # Execute with string result (non-dict)
            result = agent.recall_or_execute("test", lambda: "string_result")

            assert result == "string_result"

            # Verify learn was called with wrapped payload
            call_args = mock_memory.learn.call_args
            payload = call_args[0][2]  # Third argument is the result
            assert payload == {"result": "string_result", "_wrapped": True}

        MetaLearningMixin._memory = None
        MetaLearningMixin._lobotomized = False

    def test_learning_failure_does_not_crash(self):
        """[Phase 20] Verify learning failure doesn't crash the agent."""
        from agentic_core.base_agents.meta_learning_mixin import (
            MetaLearningMixin,
        )

        class TestAgent(MetaLearningMixin):
            pass

        mock_memory = MagicMock()
        mock_memory.recall.return_value = None
        mock_memory.learn.side_effect = Exception("Serialization failed")

        MetaLearningMixin._memory = mock_memory
        MetaLearningMixin._lobotomized = False

        with patch("redis.from_url") as mock_redis:
            mock_redis.return_value.ping.side_effect = Exception("Redis unavailable")

            agent = TestAgent()

            # Should NOT raise despite learning failure
            result = agent.recall_or_execute("test", lambda: {"data": "value"})

            assert result == {"data": "value"}

        MetaLearningMixin._memory = None
        MetaLearningMixin._lobotomized = False


class TestStrictModeCompliance:
    """Phase 20 Tests: HIVE_MIND_STRICT_MODE compliance policy."""

    def test_strict_mode_raises_on_infrastructure_failure(self):
        """[Phase 20] Verify STRICT_MODE raises CriticalInfrastructureError when Redis down."""
        from agentic_core.L4_state.memory.SemanticCacheManager import (
            CriticalInfrastructureError,
            SemanticCacheManager,
        )

        # Reset singleton
        SemanticCacheManager.reset_instance()

        # Set STRICT_MODE
        original_strict = os.environ.get("HIVE_MIND_STRICT_MODE")
        original_pinecone = os.environ.get("PINECONE_API_KEY")
        os.environ["HIVE_MIND_STRICT_MODE"] = "true"
        os.environ.pop("PINECONE_API_KEY", None)  # Ensure Pinecone also fails

        try:
            with patch("redis.from_url") as mock_redis:
                mock_redis.return_value.ping.side_effect = Exception("Connection refused")

                # Should raise CriticalInfrastructureError
                with pytest.raises(CriticalInfrastructureError) as exc_info:
                    SemanticCacheManager.get_instance()

                assert "STRICT mode" in str(exc_info.value)
        finally:
            # Restore environment
            if original_strict:
                os.environ["HIVE_MIND_STRICT_MODE"] = original_strict
            else:
                os.environ.pop("HIVE_MIND_STRICT_MODE", None)
            if original_pinecone:
                os.environ["PINECONE_API_KEY"] = original_pinecone
            SemanticCacheManager.reset_instance()

    def test_resilient_mode_survives_infrastructure_failure(self):
        """[Phase 20] Verify non-STRICT_MODE degrades gracefully when Redis down."""
        from agentic_core.L4_state.memory.SemanticCacheManager import (
            SemanticCacheManager,
        )

        # Reset singleton
        SemanticCacheManager.reset_instance()

        # Set RESILIENT_MODE (strict=false)
        original_strict = os.environ.get("HIVE_MIND_STRICT_MODE")
        original_pinecone = os.environ.get("PINECONE_API_KEY")
        os.environ["HIVE_MIND_STRICT_MODE"] = "false"
        os.environ.pop("PINECONE_API_KEY", None)  # Ensure Pinecone also fails

        try:
            with patch("redis.from_url") as mock_redis:
                mock_redis.return_value.ping.side_effect = Exception("Connection refused")

                # Should NOT raise - should degrade gracefully
                cache = SemanticCacheManager.get_instance()

                # Should be in stateless mode
                assert cache.stateless_mode is True
                assert cache.redis_enabled is False
                assert cache.pinecone_enabled is False

                # Operations should work (return None/no-op)
                result = cache.recall("test", "TestAgent")
                assert result is None

                # Learn should be a no-op in stateless mode
                cache.learn("test", "TestAgent", {"result": "data"})
                # No exception = success
        finally:
            # Restore environment
            if original_strict:
                os.environ["HIVE_MIND_STRICT_MODE"] = original_strict
            else:
                os.environ.pop("HIVE_MIND_STRICT_MODE", None)
            if original_pinecone:
                os.environ["PINECONE_API_KEY"] = original_pinecone
            SemanticCacheManager.reset_instance()


class TestTraceSampling:
    """Phase 20 Tests: Trace sampling rate configuration."""

    def test_trace_sampling_rate_zero_skips_all(self):
        """[Phase 20] Verify sampling_rate=0.0 skips all traces."""
        from agentic_core.L4_state.memory.SemanticCacheManager import (
            SemanticCacheManager,
        )

        # Reset singleton
        SemanticCacheManager.reset_instance()

        original_rate = os.environ.get("HIVE_MIND_TRACE_SAMPLING_RATE")
        original_strict = os.environ.get("HIVE_MIND_STRICT_MODE")
        os.environ["HIVE_MIND_TRACE_SAMPLING_RATE"] = "0.0"
        os.environ["HIVE_MIND_STRICT_MODE"] = "false"

        try:
            mock_redis = MagicMock()
            mock_redis.ping.return_value = True

            with patch("redis.from_url", return_value=mock_redis):
                cache = SemanticCacheManager.get_instance()
                cache.redis_enabled = True
                cache.redis_client = mock_redis

                # Learn multiple times
                for i in range(10):
                    cache.learn(f"context_{i}", "TestAgent", {"result": i})

                # All should be skipped
                assert cache.stats["traces_skipped"] == 10
                assert cache.stats["traces_sampled"] == 0
        finally:
            if original_rate:
                os.environ["HIVE_MIND_TRACE_SAMPLING_RATE"] = original_rate
            else:
                os.environ.pop("HIVE_MIND_TRACE_SAMPLING_RATE", None)
            if original_strict:
                os.environ["HIVE_MIND_STRICT_MODE"] = original_strict
            else:
                os.environ.pop("HIVE_MIND_STRICT_MODE", None)
            SemanticCacheManager.reset_instance()

    def test_trace_sampling_rate_one_captures_all(self):
        """[Phase 20] Verify sampling_rate=1.0 captures all traces."""
        from agentic_core.L4_state.memory.SemanticCacheManager import (
            SemanticCacheManager,
        )

        # Reset singleton
        SemanticCacheManager.reset_instance()

        original_rate = os.environ.get("HIVE_MIND_TRACE_SAMPLING_RATE")
        original_strict = os.environ.get("HIVE_MIND_STRICT_MODE")
        os.environ["HIVE_MIND_TRACE_SAMPLING_RATE"] = "1.0"
        os.environ["HIVE_MIND_STRICT_MODE"] = "false"

        try:
            mock_redis = MagicMock()
            mock_redis.ping.return_value = True

            with patch("redis.from_url", return_value=mock_redis):
                cache = SemanticCacheManager.get_instance()
                cache.redis_enabled = True
                cache.redis_client = mock_redis

                # Learn multiple times
                for i in range(10):
                    cache.learn(f"context_{i}", "TestAgent", {"result": i})

                # All should be sampled
                assert cache.stats["traces_sampled"] == 10
                assert cache.stats["traces_skipped"] == 0
        finally:
            if original_rate:
                os.environ["HIVE_MIND_TRACE_SAMPLING_RATE"] = original_rate
            else:
                os.environ.pop("HIVE_MIND_TRACE_SAMPLING_RATE", None)
            if original_strict:
                os.environ["HIVE_MIND_STRICT_MODE"] = original_strict
            else:
                os.environ.pop("HIVE_MIND_STRICT_MODE", None)
            SemanticCacheManager.reset_instance()


class TestMemoryLifecycle:
    """Phase 20 Tests: Memory lifecycle with feedback score promotion."""

    def test_promotion_requires_feedback_threshold(self):
        """[Phase 20] Verify promotion requires feedback_score >= threshold."""
        from agentic_core.L4_state.memory.SemanticCacheManager import (
            SemanticCacheManager,
        )

        # Reset singleton
        SemanticCacheManager.reset_instance()

        original_strict = os.environ.get("HIVE_MIND_STRICT_MODE")
        original_threshold = os.environ.get("HIVE_MIND_PROMOTION_THRESHOLD")
        os.environ["HIVE_MIND_STRICT_MODE"] = "false"
        os.environ["HIVE_MIND_PROMOTION_THRESHOLD"] = "0.8"

        try:
            mock_redis = MagicMock()
            mock_redis.ping.return_value = True

            mock_pinecone = MagicMock()

            with patch("redis.from_url", return_value=mock_redis):
                cache = SemanticCacheManager.get_instance()
                cache.pinecone_enabled = True
                cache.pinecone_index = mock_pinecone

                # Try to promote with low score
                result = cache.promote_to_long_term(
                    "test context",
                    "TestAgent",
                    {"result": "data"},
                    feedback_score=0.5,  # Below threshold
                )

                # Should be rejected
                assert result is False
                assert cache.stats["promotions"] == 0
                mock_pinecone.upsert.assert_not_called()
        finally:
            if original_strict:
                os.environ["HIVE_MIND_STRICT_MODE"] = original_strict
            else:
                os.environ.pop("HIVE_MIND_STRICT_MODE", None)
            if original_threshold:
                os.environ["HIVE_MIND_PROMOTION_THRESHOLD"] = original_threshold
            else:
                os.environ.pop("HIVE_MIND_PROMOTION_THRESHOLD", None)
            SemanticCacheManager.reset_instance()

    def test_promotion_succeeds_with_high_feedback(self):
        """[Phase 20] Verify promotion succeeds with feedback_score >= threshold."""
        from agentic_core.L4_state.memory.SemanticCacheManager import (
            SemanticCacheManager,
        )

        # Reset singleton
        SemanticCacheManager.reset_instance()

        original_strict = os.environ.get("HIVE_MIND_STRICT_MODE")
        original_threshold = os.environ.get("HIVE_MIND_PROMOTION_THRESHOLD")
        os.environ["HIVE_MIND_STRICT_MODE"] = "false"
        os.environ["HIVE_MIND_PROMOTION_THRESHOLD"] = "0.8"

        try:
            mock_redis = MagicMock()
            mock_redis.ping.return_value = True

            mock_pinecone = MagicMock()

            # Mock embedding client
            mock_embedding = MagicMock()
            mock_embedding.embeddings = [MagicMock(values=[0.1] * 768)]

            mock_client = MagicMock()
            mock_client.models.embed_content.return_value = mock_embedding

            with patch("redis.from_url", return_value=mock_redis):
                cache = SemanticCacheManager.get_instance()
                cache.pinecone_enabled = True
                cache.pinecone_index = mock_pinecone
                cache._embedding_client = mock_client

                # Promote with high score
                result = cache.promote_to_long_term(
                    "test context",
                    "TestAgent",
                    {"result": "data"},
                    feedback_score=0.9,  # Above threshold
                )

                # Should succeed
                assert result is True
                assert cache.stats["promotions"] == 1
                mock_pinecone.upsert.assert_called_once()
        finally:
            if original_strict:
                os.environ["HIVE_MIND_STRICT_MODE"] = original_strict
            else:
                os.environ.pop("HIVE_MIND_STRICT_MODE", None)
            if original_threshold:
                os.environ["HIVE_MIND_PROMOTION_THRESHOLD"] = original_threshold
            else:
                os.environ.pop("HIVE_MIND_PROMOTION_THRESHOLD", None)
            SemanticCacheManager.reset_instance()


class TestPII_Sanitizer:
    """Phase 20 Tests: PII Sanitizer stub."""

    def test_pii_sanitizer_passthrough(self):
        """[Phase 20] Verify PII_Sanitizer is currently a pass-through."""
        from agentic_core.L4_state.memory.SemanticCacheManager import PII_Sanitizer

        test_content = "This is test content with email@example.com"

        # Currently pass-through
        sanitized = PII_Sanitizer.sanitize(test_content)
        assert sanitized == test_content

        # is_safe should return True
        assert PII_Sanitizer.is_safe(test_content) is True


class TestKnowledgeGraphBridge:
    """Phase 20+ Tests: Knowledge Graph Bridge for Meta-Learning DNA."""

    def test_kg_bridge_singleton(self):
        """[Phase 20+] Verify KnowledgeGraphBridge is a singleton."""
        from agentic_core.base_agents.knowledge_graph_bridge import (
            KnowledgeGraphBridge,
        )

        KnowledgeGraphBridge.reset_instance()

        instance1 = KnowledgeGraphBridge.get_instance()
        instance2 = KnowledgeGraphBridge.get_instance()

        assert instance1 is instance2

        KnowledgeGraphBridge.reset_instance()

    def test_kg_bridge_register_agent(self):
        """[Phase 20+] Verify agent registration creates entity."""
        from agentic_core.base_agents.knowledge_graph_bridge import (
            KnowledgeGraphBridge,
        )

        KnowledgeGraphBridge.reset_instance()
        bridge = KnowledgeGraphBridge.get_instance()

        result = bridge.register_agent("TestAgent", "Agent")

        assert result is True
        assert bridge.stats["entities_created"] == 1

        KnowledgeGraphBridge.reset_instance()

    def test_kg_bridge_create_relation(self):
        """[Phase 20+] Verify relation creation."""
        from agentic_core.base_agents.knowledge_graph_bridge import (
            KnowledgeGraphBridge,
        )

        KnowledgeGraphBridge.reset_instance()
        bridge = KnowledgeGraphBridge.get_instance()

        result = bridge.create_relation(
            from_entity="GovernorAgent",
            to_entity="RouterAgent",
            relation_type=KnowledgeGraphBridge.RELATION_INTERACTS_WITH,
        )

        assert result is True
        assert bridge.stats["relations_created"] == 1

        KnowledgeGraphBridge.reset_instance()

    def test_kg_bridge_add_observation(self):
        """[Phase 20+] Verify observation addition."""
        from agentic_core.base_agents.knowledge_graph_bridge import (
            KnowledgeGraphBridge,
        )

        KnowledgeGraphBridge.reset_instance()
        bridge = KnowledgeGraphBridge.get_instance()

        result = bridge.add_observation(
            entity_name="GovernorAgent",
            observation="Tends to fail when RouterAgent timeout is < 500ms",
        )

        assert result is True
        assert bridge.stats["observations_added"] == 1

        KnowledgeGraphBridge.reset_instance()

    def test_kg_bridge_reflect_on_success(self):
        """[Phase 20+] Verify reflection on successful execution."""
        from agentic_core.base_agents.knowledge_graph_bridge import (
            ExecutionTrace,
            KnowledgeGraphBridge,
        )

        KnowledgeGraphBridge.reset_instance()
        bridge = KnowledgeGraphBridge.get_instance()

        trace = ExecutionTrace(
            agent_name="TestAgent",
            task_id="task_123",
            status="success",
            duration_ms=100,
        )

        bridge.reflect_on_execution(trace)

        # Should create SUCCESSFULLY_COMPLETED relation
        assert bridge.stats["relations_created"] == 1

        KnowledgeGraphBridge.reset_instance()

    def test_kg_bridge_reflect_on_failure(self):
        """[Phase 20+] Verify reflection on failed execution."""
        from agentic_core.base_agents.knowledge_graph_bridge import (
            ExecutionTrace,
            KnowledgeGraphBridge,
        )

        KnowledgeGraphBridge.reset_instance()
        bridge = KnowledgeGraphBridge.get_instance()

        trace = ExecutionTrace(
            agent_name="TestAgent",
            task_id="task_456",
            status="failure",
            error_type="TimeoutError",
            error_message="Connection timed out",
        )

        bridge.reflect_on_execution(trace)

        # Should create FAILED_CALL relation and add observation
        assert bridge.stats["relations_created"] == 1
        assert bridge.stats["observations_added"] == 1

        KnowledgeGraphBridge.reset_instance()

    def test_kg_bridge_record_agent_interaction(self):
        """[Phase 20+] Verify agent interaction recording."""
        from agentic_core.base_agents.knowledge_graph_bridge import (
            KnowledgeGraphBridge,
        )

        KnowledgeGraphBridge.reset_instance()
        bridge = KnowledgeGraphBridge.get_instance()

        # Record successful interaction
        bridge.record_agent_interaction(
            caller_agent="GovernorAgent",
            callee_agent="RouterAgent",
            success=True,
        )

        # Should create INTERACTS_WITH relation
        assert bridge.stats["relations_created"] == 1

        # Record failed interaction
        bridge.record_agent_interaction(
            caller_agent="GovernorAgent",
            callee_agent="RouterAgent",
            success=False,
            error_type="TimeoutError",
        )

        # Should create INTERACTS_WITH and FAILED_CALL relations + observation
        # First call: 1 relation, Second call: 2 relations (INTERACTS_WITH + FAILED_CALL)
        assert bridge.stats["relations_created"] == 3  # 1 + 2
        assert bridge.stats["observations_added"] == 1

        KnowledgeGraphBridge.reset_instance()

    def test_kg_bridge_establish_inheritance(self):
        """[Phase 20+] Verify rule inheritance establishment."""
        from agentic_core.base_agents.knowledge_graph_bridge import (
            KnowledgeGraphBridge,
        )

        KnowledgeGraphBridge.reset_instance()
        bridge = KnowledgeGraphBridge.get_instance()

        bridge.establish_inheritance(
            child_entity="RouterAgent",
            parent_entity="Global_Safety_Protocol",
        )

        # Should create INHERITS_RULES_FROM relation
        assert bridge.stats["relations_created"] == 1

        KnowledgeGraphBridge.reset_instance()

    def test_kg_bridge_mark_incompatibility(self):
        """[Phase 20+] Verify incompatibility marking."""
        from agentic_core.base_agents.knowledge_graph_bridge import (
            KnowledgeGraphBridge,
        )

        KnowledgeGraphBridge.reset_instance()
        bridge = KnowledgeGraphBridge.get_instance()

        bridge.mark_incompatibility(
            entity_a="AgentX",
            entity_b="PromptY",
            reason="Causes infinite loop",
        )

        # Should create INCOMPATIBLE_WITH relation and add observation
        assert bridge.stats["relations_created"] == 1
        assert bridge.stats["observations_added"] == 1

        KnowledgeGraphBridge.reset_instance()


class TestMetaLearningKGIntegration:
    """Phase 20+ Tests: MetaLearningMixin Knowledge Graph integration."""

    def test_mixin_kg_connection_on_init(self):
        """[Phase 20+] Verify KG connection is established on agent init."""
        from agentic_core.base_agents.knowledge_graph_bridge import (
            KnowledgeGraphBridge,
        )
        from agentic_core.base_agents.meta_learning_mixin import (
            MetaLearningMixin,
        )
        from agentic_core.L4_state.memory.SemanticCacheManager import (
            SemanticCacheManager,
        )

        # Reset state
        SemanticCacheManager.reset_instance()
        MetaLearningMixin._memory = None
        MetaLearningMixin._lobotomized = False
        MetaLearningMixin._kg_bridge = None
        KnowledgeGraphBridge.reset_instance()

        original_strict = os.environ.get("HIVE_MIND_STRICT_MODE")
        os.environ["HIVE_MIND_STRICT_MODE"] = "false"

        try:
            with patch("redis.from_url") as mock_redis:
                mock_redis.return_value.ping.side_effect = Exception("Redis unavailable")

                class TestAgent(MetaLearningMixin):
                    pass

                agent = TestAgent()

                # KG bridge should be connected
                assert MetaLearningMixin._kg_bridge is not None

                # Agent should have discovered context
                assert hasattr(agent, "_discovered_context")
        finally:
            if original_strict:
                os.environ["HIVE_MIND_STRICT_MODE"] = original_strict
            else:
                os.environ.pop("HIVE_MIND_STRICT_MODE", None)
            SemanticCacheManager.reset_instance()
            MetaLearningMixin._memory = None
            MetaLearningMixin._lobotomized = False
            MetaLearningMixin._kg_bridge = None
            KnowledgeGraphBridge.reset_instance()

    def test_mixin_reflect_on_execution(self):
        """[Phase 20+] Verify reflect_on_execution creates KG entries."""
        from agentic_core.base_agents.knowledge_graph_bridge import (
            KnowledgeGraphBridge,
        )
        from agentic_core.base_agents.meta_learning_mixin import (
            MetaLearningMixin,
        )
        from agentic_core.L4_state.memory.SemanticCacheManager import (
            SemanticCacheManager,
        )

        # Reset state
        SemanticCacheManager.reset_instance()
        MetaLearningMixin._memory = None
        MetaLearningMixin._lobotomized = False
        MetaLearningMixin._kg_bridge = None
        KnowledgeGraphBridge.reset_instance()

        original_strict = os.environ.get("HIVE_MIND_STRICT_MODE")
        os.environ["HIVE_MIND_STRICT_MODE"] = "false"

        try:
            with patch("redis.from_url") as mock_redis:
                mock_redis.return_value.ping.side_effect = Exception("Redis unavailable")

                class TestAgent(MetaLearningMixin):
                    pass

                agent = TestAgent()

                # Reflect on a successful execution
                agent.reflect_on_execution(
                    task_id="task_789",
                    status="success",
                    duration_ms=150,
                )

                # Should have created a relation
                kg_stats = agent.get_kg_stats()
                assert kg_stats is not None
                assert kg_stats["relations_created"] >= 1
        finally:
            if original_strict:
                os.environ["HIVE_MIND_STRICT_MODE"] = original_strict
            else:
                os.environ.pop("HIVE_MIND_STRICT_MODE", None)
            SemanticCacheManager.reset_instance()
            MetaLearningMixin._memory = None
            MetaLearningMixin._lobotomized = False
            MetaLearningMixin._kg_bridge = None
            KnowledgeGraphBridge.reset_instance()

    def test_mixin_add_architectural_observation(self):
        """[Phase 20+] Verify architectural observations are recorded."""
        from agentic_core.base_agents.knowledge_graph_bridge import (
            KnowledgeGraphBridge,
        )
        from agentic_core.base_agents.meta_learning_mixin import (
            MetaLearningMixin,
        )
        from agentic_core.L4_state.memory.SemanticCacheManager import (
            SemanticCacheManager,
        )

        # Reset state
        SemanticCacheManager.reset_instance()
        MetaLearningMixin._memory = None
        MetaLearningMixin._lobotomized = False
        MetaLearningMixin._kg_bridge = None
        KnowledgeGraphBridge.reset_instance()

        original_strict = os.environ.get("HIVE_MIND_STRICT_MODE")
        os.environ["HIVE_MIND_STRICT_MODE"] = "false"

        try:
            with patch("redis.from_url") as mock_redis:
                mock_redis.return_value.ping.side_effect = Exception("Redis unavailable")

                class TestAgent(MetaLearningMixin):
                    pass

                agent = TestAgent()

                # Add an architectural observation
                agent.add_architectural_observation(
                    "Tends to fail when RouterAgent timeout is < 500ms"
                )

                # Should have added an observation
                kg_stats = agent.get_kg_stats()
                assert kg_stats is not None
                assert kg_stats["observations_added"] >= 1
        finally:
            if original_strict:
                os.environ["HIVE_MIND_STRICT_MODE"] = original_strict
            else:
                os.environ.pop("HIVE_MIND_STRICT_MODE", None)
            SemanticCacheManager.reset_instance()
            MetaLearningMixin._memory = None
            MetaLearningMixin._lobotomized = False
            MetaLearningMixin._kg_bridge = None
            KnowledgeGraphBridge.reset_instance()

    def test_mixin_kg_resilient_mode(self):
        """[Phase 20+] Verify KG unavailability doesn't crash agent."""
        from agentic_core.base_agents.knowledge_graph_bridge import (
            KnowledgeGraphBridge,
        )
        from agentic_core.base_agents.meta_learning_mixin import (
            MetaLearningMixin,
        )
        from agentic_core.L4_state.memory.SemanticCacheManager import (
            SemanticCacheManager,
        )

        # Reset state
        SemanticCacheManager.reset_instance()
        MetaLearningMixin._memory = None
        MetaLearningMixin._lobotomized = False
        MetaLearningMixin._kg_bridge = None
        KnowledgeGraphBridge.reset_instance()

        original_strict = os.environ.get("HIVE_MIND_STRICT_MODE")
        os.environ["HIVE_MIND_STRICT_MODE"] = "false"

        try:
            with patch("redis.from_url") as mock_redis:
                mock_redis.return_value.ping.side_effect = Exception("Redis unavailable")

                # Force KG to be unavailable
                with patch(
                    "agentic_core.utils.core_extensions.knowledge_graph_bridge.KnowledgeGraphBridge.get_instance",
                    side_effect=Exception("MCP unavailable"),
                ):

                    class TestAgent(MetaLearningMixin):
                        pass

                    # Should NOT crash
                    agent = TestAgent()

                    # KG operations should be no-ops
                    agent.reflect_on_execution("task", "success")
                    agent.add_architectural_observation("test")
                    agent.record_agent_interaction("OtherAgent", True)

                    # All should complete without error
                    assert True
        finally:
            if original_strict:
                os.environ["HIVE_MIND_STRICT_MODE"] = original_strict
            else:
                os.environ.pop("HIVE_MIND_STRICT_MODE", None)
            SemanticCacheManager.reset_instance()
            MetaLearningMixin._memory = None
            MetaLearningMixin._lobotomized = False
            MetaLearningMixin._kg_bridge = None
            KnowledgeGraphBridge.reset_instance()
