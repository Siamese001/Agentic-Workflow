"""Phase 20 Tests: DNA Hardening - Singleton & MetaLearningMixin.

Tests for singleton enforcement, instinctive bypass, DNA segregation, and lobotomy resilience.
"""
from __future__ import annotations

import json
import os
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch


class TestSingletonEnforcement:
    """Phase 20 Tests: Singleton pattern enforcement."""
    
    def test_singleton_get_instance(self):
        """[Phase 20] Verify get_instance returns the same instance."""
        from agentic_core.L4_state.memory.SemanticCacheManager import (
            SemanticCacheManager,
        )
        
        # Reset singleton for clean test
        SemanticCacheManager.reset_instance()
        
        with patch("redis.from_url") as mock_redis:
            mock_redis.return_value.ping.side_effect = Exception("Redis unavailable")
            
            instance1 = SemanticCacheManager.get_instance()
            instance2 = SemanticCacheManager.get_instance()
            
            assert instance1 is instance2
        
        # Clean up
        SemanticCacheManager.reset_instance()

    def test_singleton_direct_instantiation_blocked(self):
        """[Phase 20] Verify direct instantiation raises RuntimeError."""
        from agentic_core.L4_state.memory.SemanticCacheManager import (
            SemanticCacheManager,
        )
        
        # Reset singleton
        SemanticCacheManager.reset_instance()
        
        with patch("redis.from_url") as mock_redis:
            mock_redis.return_value.ping.side_effect = Exception("Redis unavailable")
            
            # First, create via get_instance
            SemanticCacheManager.get_instance()
            
            # Now direct instantiation should fail
            with pytest.raises(RuntimeError) as exc_info:
                SemanticCacheManager()
            
            assert "SINGLETON VIOLATION" in str(exc_info.value)
        
        # Clean up
        SemanticCacheManager.reset_instance()

    def test_singleton_thread_safe(self):
        """[Phase 20] Verify singleton is thread-safe."""
        import threading
        from agentic_core.L4_state.memory.SemanticCacheManager import (
            SemanticCacheManager,
        )
        
        # Reset singleton
        SemanticCacheManager.reset_instance()
        
        instances = []
        
        def get_instance():
            with patch("redis.from_url") as mock_redis:
                mock_redis.return_value.ping.side_effect = Exception("Redis unavailable")
                instances.append(SemanticCacheManager.get_instance())
        
        with patch("redis.from_url") as mock_redis:
            mock_redis.return_value.ping.side_effect = Exception("Redis unavailable")
            
            threads = [threading.Thread(target=get_instance) for _ in range(10)]
            
            for t in threads:
                t.start()
            for t in threads:
                t.join()
        
        # All instances should be the same
        assert len(set(id(i) for i in instances)) == 1
        
        # Clean up
        SemanticCacheManager.reset_instance()


class TestInstinctiveBypass:
    """Phase 20 Tests: recall_or_execute bypass behavior."""
    
    def test_instinctive_bypass_cached(self):
        """[Phase 20] Verify recall_or_execute returns cached result without executing."""
        from agentic_core.utils.core_extensions.meta_learning_mixin import (
            MetaLearningMixin,
        )
        from agentic_core.L4_state.memory.SemanticCacheManager import (
            SemanticCacheManager,
        )
        
        # Reset singleton
        SemanticCacheManager.reset_instance()
        MetaLearningMixin._memory = None
        
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
            
            # This should NOT be called
            def should_not_run():
                raise Exception("Should not run - cache should bypass")
            
            result = agent.recall_or_execute("Task A", should_not_run)
            
            assert result == {"result": "cached_success"}
            mock_memory.recall.assert_called_once()
        
        # Clean up
        SemanticCacheManager.reset_instance()
        MetaLearningMixin._memory = None

    def test_instinctive_bypass_miss_executes(self):
        """[Phase 20] Verify recall_or_execute executes on cache miss."""
        from agentic_core.utils.core_extensions.meta_learning_mixin import (
            MetaLearningMixin,
        )
        from agentic_core.L4_state.memory.SemanticCacheManager import (
            SemanticCacheManager,
        )
        
        # Reset singleton
        SemanticCacheManager.reset_instance()
        MetaLearningMixin._memory = None
        
        class TestAgent(MetaLearningMixin):
            pass
        
        # Mock the memory to return None (cache miss)
        mock_memory = MagicMock()
        mock_memory.recall.return_value = None
        
        with patch("redis.from_url") as mock_redis:
            mock_redis.return_value.ping.side_effect = Exception("Redis unavailable")
            
            agent = TestAgent()
            MetaLearningMixin._memory = mock_memory
            
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


class TestDNASegregation:
    """Phase 20 Tests: Namespace segregation between agent types."""
    
    def test_dna_segregation_different_agents(self):
        """[Phase 20] Verify different agents use different namespaces."""
        from agentic_core.utils.core_extensions.meta_learning_mixin import (
            MetaLearningMixin,
        )
        from agentic_core.L4_state.memory.SemanticCacheManager import (
            SemanticCacheManager,
        )
        
        # Reset singleton
        SemanticCacheManager.reset_instance()
        MetaLearningMixin._memory = None
        
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
            
            # Governor learns "Prompt X"
            governor.learn_experience("Prompt X", {"result": "Governor Result"})
            
            # Governor recalls "Prompt X" - should hit
            gov_result = governor.recall_experience("Prompt X")
            assert gov_result == {"result": "Governor Result"}
            
            # Router recalls "Prompt X" - should miss (different namespace)
            router_result = router.recall_experience("Prompt X")
            assert router_result is None
            
            # Verify namespaces were different
            assert "GovernorAgent" in recall_calls
            assert "RouterAgent" in recall_calls
        
        # Clean up
        SemanticCacheManager.reset_instance()
        MetaLearningMixin._memory = None

    def test_namespace_derived_from_class_name(self):
        """[Phase 20] Verify namespace is derived from class name."""
        from agentic_core.utils.core_extensions.meta_learning_mixin import (
            MetaLearningMixin,
        )
        
        class CustomAgentName(MetaLearningMixin):
            pass
        
        with patch("redis.from_url") as mock_redis:
            mock_redis.return_value.ping.side_effect = Exception("Redis unavailable")
            
            MetaLearningMixin._memory = None
            agent = CustomAgentName()
            
            assert agent._namespace == "CustomAgentName"
        
        MetaLearningMixin._memory = None


class TestLobotomyResilience:
    """Phase 20 Tests: Graceful degradation when memory is unavailable."""
    
    def test_lobotomy_resilience_redis_down(self):
        """[Phase 20] Verify agent works when Redis is down."""
        from agentic_core.L4_state.memory.SemanticCacheManager import (
            SemanticCacheManager,
        )
        
        # Reset singleton
        SemanticCacheManager.reset_instance()
        
        with patch("redis.from_url") as mock_redis:
            mock_redis.return_value.ping.side_effect = Exception("Connection refused")
            
            # Should not crash
            cache = SemanticCacheManager.get_instance()
            
            # Redis should be disabled
            assert cache.redis_enabled is False
            
            # Recall should return None gracefully
            result = cache.recall("test context", "TestAgent")
            assert result is None
        
        # Clean up
        SemanticCacheManager.reset_instance()

    def test_lobotomy_resilience_execution_continues(self):
        """[Phase 20] Verify execution continues when memory is unavailable."""
        from agentic_core.utils.core_extensions.meta_learning_mixin import (
            MetaLearningMixin,
        )
        from agentic_core.L4_state.memory.SemanticCacheManager import (
            SemanticCacheManager,
        )
        
        # Reset singleton
        SemanticCacheManager.reset_instance()
        MetaLearningMixin._memory = None
        
        class TestAgent(MetaLearningMixin):
            pass
        
        with patch("redis.from_url") as mock_redis:
            mock_redis.return_value.ping.side_effect = Exception("Connection refused")
            
            agent = TestAgent()
            
            # Set memory to None to simulate complete failure
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

    def test_lobotomy_warning_logged(self, caplog):
        """[Phase 20] Verify LOBOTOMY WARNING is logged when Redis unavailable."""
        import logging
        from agentic_core.L4_state.memory.SemanticCacheManager import (
            SemanticCacheManager,
        )
        
        # Reset singleton
        SemanticCacheManager.reset_instance()
        
        with caplog.at_level(logging.CRITICAL):
            with patch("redis.from_url") as mock_redis:
                mock_redis.return_value.ping.side_effect = Exception("Connection refused")
                
                SemanticCacheManager.get_instance()
        
        # Check for lobotomy warning
        assert any("LOBOTOMY" in record.message for record in caplog.records)
        
        # Clean up
        SemanticCacheManager.reset_instance()


class TestContextHashing:
    """Phase 20 Tests: Context hash generation."""
    
    def test_context_hash_consistency(self):
        """[Phase 20] Verify context hash is consistent."""
        from agentic_core.utils.core_extensions.meta_learning_mixin import (
            MetaLearningMixin,
        )
        
        class TestAgent(MetaLearningMixin):
            pass
        
        MetaLearningMixin._memory = None
        
        with patch("redis.from_url") as mock_redis:
            mock_redis.return_value.ping.side_effect = Exception("Redis unavailable")
            
            agent = TestAgent()
            
            hash1 = agent._generate_context_hash("test context")
            hash2 = agent._generate_context_hash("test context")
            
            assert hash1 == hash2

    def test_context_hash_includes_namespace(self):
        """[Phase 20] Verify context hash includes namespace for segregation."""
        from agentic_core.utils.core_extensions.meta_learning_mixin import (
            MetaLearningMixin,
        )
        
        class AgentA(MetaLearningMixin):
            pass
        
        class AgentB(MetaLearningMixin):
            pass
        
        MetaLearningMixin._memory = None
        
        with patch("redis.from_url") as mock_redis:
            mock_redis.return_value.ping.side_effect = Exception("Redis unavailable")
            
            agent_a = AgentA()
            agent_b = AgentB()
            
            # Same context, different agents = different hashes
            hash_a = agent_a._generate_context_hash("same context")
            hash_b = agent_b._generate_context_hash("same context")
            
            assert hash_a != hash_b
        
        MetaLearningMixin._memory = None
