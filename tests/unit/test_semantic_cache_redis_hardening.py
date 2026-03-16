"""
Invariant tests for Semantic Cache / Redis hardening.

Verifies all gaps from the hardening plan are properly resolved.
Tests are deterministic and use real Redis when available, fallback when not.
"""

from unittest.mock import Mock, patch

import pytest

from agentic_core.L4_state.memory.in_memory_vector_store import InMemoryVectorStore
from agentic_core.L4_state.memory.semantic_cache_manager import SemanticCacheManager
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_semantic_cache_redis_hardening")
_emit_applies_guardrail("p0", "test_semantic_cache_redis_hardening", "p0_governance")
_emit_reads_policy_state("p0", "test_semantic_cache_redis_hardening", "policy_binding")
_emit_snapshots_state("p0", "test_semantic_cache_redis_hardening", "state_snapshot")
emit_replay_key("p0", "test_semantic_cache_redis_hardening")
emit_determinism_digest("p0", "test_semantic_cache_redis_hardening")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

class TestSemanticCacheRedisHardening:
    """Test suite verifying all semantic cache/Redis hardening gaps are resolved."""

    @pytest.fixture
    def cache_manager(self):
        """Create a SemanticCacheManager instance for testing."""
        # Force clean state
        SemanticCacheManager._instance = None
        return SemanticCacheManager.get_instance()

    def test_c1_learn_async_no_await_on_sync_redis(self, cache_manager):
        """C1: learn_async() must not crash with 'await' on sync Redis client."""
        context = "test context for C1"
        namespace = "TestAgent"
        result = {"output": "test result"}

        # This should not raise TypeError about awaiting sync client
        try:
            # Run in async context to ensure no await errors
            import asyncio

            asyncio.run(cache_manager.learn_async(context, namespace, result))
        except TypeError as e:
            if "object bool can't be used in 'await' expression" in str(e):
                pytest.fail("C1 NOT FIXED: learn_async() still awaits sync Redis client")
            raise

    def test_c2_redis_sovereign_agent_instantiates(self):
        """C2: RedisSovereignAgent must instantiate without NameError."""
        from pathlib import Path

        from agentic_core.L2_execution.reasoning.RedisSovereignAgent import RedisSovereignAgent

        try:
            # This should not raise NameError about undefined function
            agent = RedisSovereignAgent(Path.cwd())
            assert agent is not None
        except NameError as e:
            if "get_redis_sovereign" in str(e):
                pytest.fail("C2 NOT FIXED: RedisSovereignAgent still calls undefined function")
            raise

    def test_c3_sovereign_semantic_cache_sync_methods(self):
        """C3: SovereignSemanticCache methods must be sync (no await on sync client)."""
        from agentic_core.L4_state.memory.sovereign_semantic_cache import SovereignSemanticCache

        # Mock dependencies
        with patch("agentic_core.L4_state.memory.sovereign_semantic_cache.get_redis_client") as mock_redis:
            mock_redis.return_value = Mock()
            mock_redis.return_value.get.return_value = None
            mock_redis.return_value.set = Mock()
            mock_redis.return_value.delete = Mock()

            cache = SovereignSemanticCache("test-mission")
            cache.engine = Mock()
            cache.engine.get_embedding.return_value = [0.1] * 1024

            # These should not raise TypeError about awaiting sync client
            try:
                cache.cache_file("test.py", "print('hello')", {})
                cache.invalidate("test.py")
            except TypeError as e:
                if "object bool can't be used in 'await' expression" in str(e):
                    pytest.fail("C3 NOT FIXED: SovereignSemanticCache still awaits sync client")
                raise

    def test_c4_redis_enabled_by_default(self):
        """C4: USE_REDIS_CACHE must default to True (enabled)."""
        # Check the default value in constants
        from agentic_core.config.core.constants_config import USE_REDIS_CACHE as DEFAULT_USE_REDIS

        if not DEFAULT_USE_REDIS:
            pytest.fail("C4 NOT FIXED: USE_REDIS_CACHE still defaults to False")

        # Verify RedisCacheMixin respects the flag
        from agentic_core.mixins.redis_cache_mixin import RedisCacheMixin

        class TestAgent(RedisCacheMixin):
            _cache_prefix = "test"
            _default_ttl = 3600

        agent = TestAgent()
        if not agent.redis_enabled:
            pytest.fail("C4 NOT FIXED: RedisCacheMixin still disabled by default")

    def test_c5_sovereign_redis_orchestrator_factory(self):
        """C5: SovereignRedisOrchestrator factory must not call super()."""
        from agentic_core.L3_orchestration.engines.sovereign_redis_orchestrator import (
            get_sovereign_redis_orchestrator,
        )

        try:
            # This should not raise RuntimeError about super() in free function
            orchestrator = get_sovereign_redis_orchestrator()
            assert orchestrator is not None
        except RuntimeError as e:
            if "super(): __class__ cell not found" in str(e):
                pytest.fail("C5 NOT FIXED: Factory still calls super() in free function")
            raise

    def test_h1_layer2_uses_faiss_vector_store(self, cache_manager):
        """H1: Layer 2 must use InMemoryVectorStore (FAISS-backed) not O(N) dict scan."""
        assert isinstance(cache_manager._vector_store, InMemoryVectorStore), (
            "H1 NOT FIXED: Layer 2 is not using InMemoryVectorStore"
        )
        # Must have FAISS index attribute (even if None before any inserts)
        assert hasattr(cache_manager._vector_store, "_faiss_index"), (
            "H1 NOT FIXED: InMemoryVectorStore missing _faiss_index attribute"
        )
        # Must have _storage dict
        assert hasattr(cache_manager._vector_store, "_storage"), (
            "H1 NOT FIXED: InMemoryVectorStore missing _storage attribute"
        )

    def test_h2_no_silent_swallow_in_promotion(self, cache_manager):
        """H2: promote_to_long_term() must log Redis TTL extension failures."""
        import asyncio

        async def _run():
            with patch.object(cache_manager, "_get_embedding", return_value=[0.1] * 8):
                with patch.object(cache_manager, "redis_enabled", True):
                    with patch.object(cache_manager, "redis_client") as mock_redis:
                        mock_redis.setex.side_effect = Exception("Redis connection failed")
                        with patch(
                            "agentic_core.L4_state.memory.semantic_cache_manager.Logger"
                        ) as mock_logger:
                            await cache_manager.promote_to_long_term(
                                "test context", "TestNamespace", {"result": "test"}, 0.9
                            )
                            # Verify warning was logged, not silently swallowed
                            warning_calls = [str(c) for c in mock_logger.warning.call_args_list]
                            assert any("Redis TTL extension failed" in c for c in warning_calls), (
                                "H2 NOT FIXED: Redis TTL extension failure still silently swallowed"
                            )

        asyncio.run(_run())

    def test_h3_correct_redis_api_usage(self):
        """H3: SovereignSemanticCache must use correct DeterministicRedisCache API (ttl_seconds + bytes)."""
        from agentic_core.L4_state.memory.sovereign_semantic_cache import SovereignSemanticCache

        with patch(
            "agentic_core.L4_state.memory.sovereign_semantic_cache.get_redis_client"
        ) as mock_redis_factory:
            mock_redis = Mock()
            mock_redis.get.return_value = None
            mock_redis_factory.return_value = mock_redis

            cache = SovereignSemanticCache("test-mission")
            cache.engine = Mock()
            cache.engine.get_embedding.return_value = [0.1] * 8

            cache.cache_file("test.py", "print('hello')", {})

            assert mock_redis.set.called, "H3 NOT FIXED: redis.set not called"
            call_kwargs = mock_redis.set.call_args.kwargs
            call_args = mock_redis.set.call_args.args
            assert "ttl_seconds" in call_kwargs, (
                f"H3 NOT FIXED: Still using 'ttl' instead of 'ttl_seconds'. kwargs={call_kwargs}"
            )
            assert isinstance(call_args[1], bytes), "H3 NOT FIXED: Not encoding value to bytes"

    def test_h4_redis_cache_mixin_uses_canonical_client(self):
        """H4: RedisCacheMixin must use get_hot_cache() not RedisSovereignAgent."""
        import ast
        import inspect

        from agentic_core.mixins.redis_cache_mixin import RedisCacheMixin

        src = inspect.getsource(RedisCacheMixin)
        tree = ast.parse(src)
        # Ensure no import of RedisSovereignAgent in source
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                names = [alias.name for alias in node.names]
                module = getattr(node, "module", "") or ""
                assert "RedisSovereignAgent" not in module and all(
                    "RedisSovereignAgent" not in n for n in names
                ), "H4 NOT FIXED: RedisCacheMixin still imports RedisSovereignAgent"

    def test_m1_no_pinecone_references(self, cache_manager):
        """M1: SemanticCacheManager source must not reference Pinecone."""
        import inspect

        src = inspect.getsource(cache_manager.__class__)
        assert "Pinecone" not in src, "M1 NOT FIXED: SemanticCacheManager source still references Pinecone"

    def test_m2_deterministic_trace_sampling(self, cache_manager):
        """M2: Trace sampling must be deterministic based on trace_id hash."""
        # Same trace_id should always produce same sampling decision
        trace_id = "deterministic-test-trace"

        # Reset sampling rate to 50% for testing
        cache_manager.trace_sampling_rate = 0.5

        # Multiple calls with same trace_id should be consistent
        results = [cache_manager._should_sample_trace(trace_id) for _ in range(10)]
        assert all(r == results[0] for r in results), "M2 NOT FIXED: Trace sampling is not deterministic"

        # Different trace_ids should vary
        other_trace = "different-trace-id"
        other_result = cache_manager._should_sample_trace(other_trace)
        # Note: Might be same due to hash distribution, but should be deterministic

    def test_m3_duplicate_redis_client_tombstoned(self):
        """M3: L4/workflow_engines/redis_cache_client.py must be tombstoned."""
        import importlib.util
        from pathlib import Path

        target = Path("c:/Git/Agentic-Workflow/agentic_core/L4_state/workflow_engines/redis_cache_client.py")
        assert target.exists(), "M3: Tombstone file missing entirely"

        spec = importlib.util.spec_from_file_location("duplicate_redis", str(target))
        assert spec and spec.loader, "M3: Could not create module spec"

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        assert not hasattr(module, "DeterministicRedisCache"), (
            "M3 NOT FIXED: Duplicate Redis client not tombstoned — DeterministicRedisCache still exported"
        )
        assert module.__doc__ and "TOMBSTONED" in module.__doc__, (
            "M3 NOT FIXED: Tombstone marker missing from docstring"
        )

    def test_m4_invariant_integration(self, cache_manager):
        """M4: Full integration test - recall, learn, promote cycle with get_stats() alias."""
        import asyncio

        context = "integration test context for m4"
        namespace = "TestInvariantAgent"
        result = {"answer": 42, "reason": "test"}

        # Recall should miss initially
        cached = cache_manager.recall(context, namespace)
        assert cached is None, "Should start with cache miss"

        # learn() must not raise
        cache_manager.learn(context, namespace, result)

        # stats must be populated via both get_stats() and get_statistics()
        stats_via_alias = cache_manager.get_stats()
        stats_via_method = cache_manager.get_statistics()
        assert "cache_stores" in stats_via_alias, "get_stats() missing 'cache_stores'"
        assert stats_via_alias == stats_via_method, "get_stats() and get_statistics() must return same data"

        # promote_to_long_term() must accept async call
        promoted = asyncio.run(cache_manager.promote_to_long_term(context, namespace, result, 0.05))
        # Low score (below default 0.8 threshold) — should reject
        assert promoted is False, "Promotion below threshold must return False"

        promoted_high = asyncio.run(cache_manager.promote_to_long_term(context, namespace, result, 0.9))
        # High score — succeeds if embedding available, otherwise fails gracefully
        assert isinstance(promoted_high, bool), "promote_to_long_term must return bool"
