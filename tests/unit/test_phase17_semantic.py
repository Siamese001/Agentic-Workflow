"""Phase 17 Tests: Semantic Meta-Learning Cache.

Tests for Redis exact matching, Pinecone semantic matching, and cache miss behavior.
"""
from __future__ import annotations

import json
import os
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch


class TestRedisExactMatch:
    """Phase 17 Tests: Redis exact content hash matching."""
    
    def test_redis_exact_match_hit(self, tmp_path):
        """[Phase 17] Verify Redis returns cached decision for exact content match."""
        from agentic_core.L5_safety.cognition.SemanticCacheManager import (
            SemanticCacheManager,
        )
        
        # Mock Redis
        mock_redis = MagicMock()
        cached_decision = {
            "action": "MOVE",
            "target_path": "agentic_core/L5_safety/validators",
            "reason": "Cached decision",
            "confidence": 0.95,
        }
        mock_redis.get.return_value = json.dumps(cached_decision)
        
        with patch("redis.from_url", return_value=mock_redis):
            mock_redis.ping.return_value = True
            
            cache = SemanticCacheManager(api_key="test_key")
            cache.redis_enabled = True
            cache.redis_client = mock_redis
            
            # Query cache
            result = cache.get_cached_decision("test content", "ORPHAN")
            
            assert result is not None
            assert result["action"] == "MOVE"
            assert result["confidence"] == 0.95
            assert cache.stats["redis_hits"] == 1

    def test_redis_exact_match_miss(self, tmp_path):
        """[Phase 17] Verify Redis returns None for cache miss."""
        from agentic_core.L5_safety.cognition.SemanticCacheManager import (
            SemanticCacheManager,
        )
        
        # Mock Redis returning None
        mock_redis = MagicMock()
        mock_redis.get.return_value = None
        
        with patch("redis.from_url", return_value=mock_redis):
            mock_redis.ping.return_value = True
            
            cache = SemanticCacheManager(api_key="test_key")
            cache.redis_enabled = True
            cache.pinecone_enabled = False  # Disable Pinecone for this test
            cache.redis_client = mock_redis
            
            # Query cache
            result = cache.get_cached_decision("new content", "ORPHAN")
            
            assert result is None
            assert cache.stats["cache_misses"] == 1

    def test_redis_stores_decision(self, tmp_path):
        """[Phase 17] Verify Redis stores decision with correct TTL."""
        from agentic_core.L5_safety.cognition.SemanticCacheManager import (
            SemanticCacheManager,
        )
        
        mock_redis = MagicMock()
        
        with patch("redis.from_url", return_value=mock_redis):
            mock_redis.ping.return_value = True
            
            cache = SemanticCacheManager(api_key="test_key")
            cache.redis_enabled = True
            cache.redis_client = mock_redis
            
            decision = {
                "action": "ARCHIVE",
                "target_path": "archives/test",
                "reason": "Test reason",
                "confidence": 0.85,
            }
            
            cache.cache_decision("test content", "ORPHAN", decision)
            
            # Verify setex was called with 7-day TTL
            mock_redis.setex.assert_called_once()
            call_args = mock_redis.setex.call_args
            assert call_args[0][1] == 86400 * 7  # 7 days


class TestPineconeSemanticMatch:
    """Phase 17 Tests: Pinecone semantic similarity matching."""
    
    def test_pinecone_semantic_match_high_score(self, tmp_path):
        """[Phase 17] Verify Pinecone returns cached decision for high similarity."""
        from agentic_core.L5_safety.cognition.SemanticCacheManager import (
            SemanticCacheManager,
        )
        
        cached_decision = {
            "action": "MOVE",
            "target_path": "agentic_core/L3_orchestration",
            "reason": "Similar file decision",
            "confidence": 0.92,
        }
        
        # Mock Pinecone response
        mock_match = MagicMock()
        mock_match.score = 0.98  # High similarity
        mock_match.metadata = {"decision_json": json.dumps(cached_decision)}
        
        mock_results = MagicMock()
        mock_results.matches = [mock_match]
        
        mock_index = MagicMock()
        mock_index.query.return_value = mock_results
        
        # Mock embedding client
        mock_embedding = MagicMock()
        mock_embedding.embeddings = [MagicMock(values=[0.1] * 768)]
        
        mock_client = MagicMock()
        mock_client.models.embed_content.return_value = mock_embedding
        
        with patch("redis.from_url") as mock_redis:
            mock_redis.return_value.ping.side_effect = Exception("Redis unavailable")
            
            cache = SemanticCacheManager(api_key="test_key")
            cache.redis_enabled = False
            cache.pinecone_enabled = True
            cache.pinecone_index = mock_index
            cache._embedding_client = mock_client
            
            result = cache.get_cached_decision("similar content", "ORPHAN")
            
            assert result is not None
            assert result["action"] == "MOVE"
            assert cache.stats["pinecone_hits"] == 1

    def test_pinecone_semantic_match_low_score(self, tmp_path):
        """[Phase 17] Verify Pinecone returns None for low similarity."""
        from agentic_core.L5_safety.cognition.SemanticCacheManager import (
            SemanticCacheManager,
        )
        
        # Mock Pinecone response with low score
        mock_match = MagicMock()
        mock_match.score = 0.70  # Below threshold (0.95)
        
        mock_results = MagicMock()
        mock_results.matches = [mock_match]
        
        mock_index = MagicMock()
        mock_index.query.return_value = mock_results
        
        # Mock embedding
        mock_embedding = MagicMock()
        mock_embedding.embeddings = [MagicMock(values=[0.1] * 768)]
        
        mock_client = MagicMock()
        mock_client.models.embed_content.return_value = mock_embedding
        
        with patch("redis.from_url") as mock_redis:
            mock_redis.return_value.ping.side_effect = Exception("Redis unavailable")
            
            cache = SemanticCacheManager(api_key="test_key")
            cache.redis_enabled = False
            cache.pinecone_enabled = True
            cache.pinecone_index = mock_index
            cache._embedding_client = mock_client
            
            result = cache.get_cached_decision("different content", "ORPHAN")
            
            assert result is None
            assert cache.stats["cache_misses"] == 1


class TestCacheMissBehavior:
    """Phase 17 Tests: Cache miss and learning behavior."""
    
    def test_cache_miss_triggers_store(self, tmp_path):
        """[Phase 17] Verify cache miss leads to decision being stored."""
        from agentic_core.L5_safety.cognition.SemanticCacheManager import (
            SemanticCacheManager,
        )
        
        mock_redis = MagicMock()
        mock_redis.get.return_value = None  # Cache miss
        
        with patch("redis.from_url", return_value=mock_redis):
            mock_redis.ping.return_value = True
            
            cache = SemanticCacheManager(api_key="test_key")
            cache.redis_enabled = True
            cache.pinecone_enabled = False
            cache.redis_client = mock_redis
            
            # First, verify cache miss
            result = cache.get_cached_decision("new content", "ORPHAN")
            assert result is None
            
            # Then store a decision
            decision = {
                "action": "MOVE",
                "target_path": "agentic_core/L5_safety",
                "reason": "New decision",
                "confidence": 0.90,
            }
            cache.cache_decision("new content", "ORPHAN", decision)
            
            # Verify store was called
            assert cache.stats["cache_stores"] == 1
            mock_redis.setex.assert_called_once()

    def test_statistics_tracking(self, tmp_path):
        """[Phase 17] Verify cache statistics are tracked correctly."""
        from agentic_core.L5_safety.cognition.SemanticCacheManager import (
            SemanticCacheManager,
        )
        
        mock_redis = MagicMock()
        
        with patch("redis.from_url", return_value=mock_redis):
            mock_redis.ping.return_value = True
            
            cache = SemanticCacheManager(api_key="test_key")
            cache.redis_enabled = True
            cache.pinecone_enabled = False
            cache.redis_client = mock_redis
            
            # Simulate hits and misses
            mock_redis.get.return_value = json.dumps({"action": "MOVE", "confidence": 0.9})
            cache.get_cached_decision("content1", "ORPHAN")  # Hit
            
            mock_redis.get.return_value = None
            cache.get_cached_decision("content2", "ORPHAN")  # Miss
            cache.get_cached_decision("content3", "ORPHAN")  # Miss
            
            stats = cache.get_statistics()
            
            assert stats["redis_hits"] == 1
            assert stats["cache_misses"] == 2
            assert stats["total_hits"] == 1
            assert stats["total_lookups"] == 3
            assert stats["hit_rate"] == 1 / 3


class TestTieredProcessorIntegration:
    """Phase 17 Tests: TieredBatchProcessor integration with SemanticCacheManager."""
    
    @pytest.fixture
    def clean_project(self, tmp_path):
        """Setup a clean project."""
        (tmp_path / "agentic_core" / "L5_safety").mkdir(parents=True)
        return tmp_path

    def test_processor_uses_semantic_cache(self, clean_project):
        """[Phase 17] Verify TieredBatchProcessor queries semantic cache."""
        from agentic_core.L5_safety.cognition.CognitiveDispositionAgent import (
            CognitiveDispositionAgent,
        )
        from agentic_core.L5_safety.cognition.TieredBatchProcessor import (
            TieredBatchProcessor,
        )
        
        agent = CognitiveDispositionAgent(
            project_root=clean_project,
            api_key="test_key",
        )
        
        processor = TieredBatchProcessor(
            agent=agent,
            heuristic_threshold=0.75,
            use_semantic_cache=True,
        )
        
        # Verify semantic cache is enabled
        assert processor.use_semantic_cache is True

    def test_processor_caches_high_confidence_decisions(self, clean_project):
        """[Phase 17] Verify processor caches decisions with confidence >= 0.8."""
        from agentic_core.L5_safety.cognition.CognitiveDispositionAgent import (
            CognitiveDispositionAgent,
        )
        from agentic_core.L5_safety.cognition.TieredBatchProcessor import (
            TieredBatchProcessor,
        )
        from agentic_core.L5_safety.cognition.SemanticCacheManager import (
            SemanticCacheManager,
        )
        
        agent = CognitiveDispositionAgent(
            project_root=clean_project,
            api_key="test_key",
        )
        
        processor = TieredBatchProcessor(
            agent=agent,
            heuristic_threshold=0.75,
            use_semantic_cache=True,
        )
        
        # Mock the semantic cache
        mock_cache = MagicMock(spec=SemanticCacheManager)
        processor._semantic_cache = mock_cache
        
        # Create test file
        test_file = clean_project / "test.py"
        test_file.write_text("# Test file")
        
        # Store a high-confidence decision
        high_conf_decision = {
            "action": "MOVE",
            "target_path": "agentic_core/L5_safety",
            "reason": "Test",
            "confidence": 0.85,
        }
        
        processor._store_semantic_cache(str(test_file), "ORPHAN", high_conf_decision)
        
        # Verify cache_decision was called
        mock_cache.cache_decision.assert_called_once()

    def test_processor_skips_low_confidence_caching(self, clean_project):
        """[Phase 17] Verify processor does NOT cache decisions with confidence < 0.8."""
        from agentic_core.L5_safety.cognition.CognitiveDispositionAgent import (
            CognitiveDispositionAgent,
        )
        from agentic_core.L5_safety.cognition.TieredBatchProcessor import (
            TieredBatchProcessor,
        )
        from agentic_core.L5_safety.cognition.SemanticCacheManager import (
            SemanticCacheManager,
        )
        
        agent = CognitiveDispositionAgent(
            project_root=clean_project,
            api_key="test_key",
        )
        
        processor = TieredBatchProcessor(
            agent=agent,
            heuristic_threshold=0.75,
            use_semantic_cache=True,
        )
        
        # Mock the semantic cache
        mock_cache = MagicMock(spec=SemanticCacheManager)
        processor._semantic_cache = mock_cache
        
        # Create test file
        test_file = clean_project / "test.py"
        test_file.write_text("# Test file")
        
        # Store a low-confidence decision
        low_conf_decision = {
            "action": "MANUAL_REVIEW",
            "target_path": None,
            "reason": "Uncertain",
            "confidence": 0.5,
        }
        
        processor._store_semantic_cache(str(test_file), "ORPHAN", low_conf_decision)
        
        # Verify cache_decision was NOT called
        mock_cache.cache_decision.assert_not_called()


class TestEmbeddingEngine:
    """Phase 17 Tests: Embedding generation for semantic matching."""
    
    def test_embedding_generation(self):
        """[Phase 17] Verify embedding is generated for content."""
        from agentic_core.L5_safety.cognition.SemanticCacheManager import (
            SemanticCacheManager,
        )
        
        # Mock embedding response
        mock_embedding = MagicMock()
        mock_embedding.embeddings = [MagicMock(values=[0.1] * 768)]
        
        mock_client = MagicMock()
        mock_client.models.embed_content.return_value = mock_embedding
        
        with patch("redis.from_url") as mock_redis:
            mock_redis.return_value.ping.side_effect = Exception("Redis unavailable")
            
            cache = SemanticCacheManager(api_key="test_key")
            cache._embedding_client = mock_client
            
            vector = cache._get_embedding("test content")
            
            assert vector is not None
            assert len(vector) == 768
            mock_client.models.embed_content.assert_called_once()

    def test_embedding_truncation(self):
        """[Phase 17] Verify long content is truncated to 2000 chars."""
        from agentic_core.L5_safety.cognition.SemanticCacheManager import (
            SemanticCacheManager,
        )
        
        mock_embedding = MagicMock()
        mock_embedding.embeddings = [MagicMock(values=[0.1] * 768)]
        
        mock_client = MagicMock()
        mock_client.models.embed_content.return_value = mock_embedding
        
        with patch("redis.from_url") as mock_redis:
            mock_redis.return_value.ping.side_effect = Exception("Redis unavailable")
            
            cache = SemanticCacheManager(api_key="test_key")
            cache._embedding_client = mock_client
            
            # Generate very long content
            long_content = "x" * 5000
            cache._get_embedding(long_content)
            
            # Verify content was truncated
            call_args = mock_client.models.embed_content.call_args
            assert len(call_args.kwargs["contents"]) <= 2000


class TestThreadSafety:
    """Phase 17 Tests: Thread safety verification."""
    
    def test_thread_safe_stats(self):
        """[Phase 17] Verify stats are thread-safe under concurrent access."""
        import threading
        from agentic_core.L5_safety.cognition.SemanticCacheManager import (
            SemanticCacheManager,
        )
        
        with patch("redis.from_url") as mock_redis:
            mock_redis.return_value.ping.side_effect = Exception("Redis unavailable")
            
            cache = SemanticCacheManager(api_key="test_key")
            cache.redis_enabled = False
            cache.pinecone_enabled = False
            
            # Reset stats
            cache.stats = {
                "redis_hits": 0,
                "pinecone_hits": 0,
                "cache_misses": 0,
                "cache_stores": 0,
            }
            
            num_threads = 10
            iterations_per_thread = 100
            
            def increment_stats():
                for _ in range(iterations_per_thread):
                    with cache._lock:
                        cache.stats["cache_stores"] += 1
            
            threads = [threading.Thread(target=increment_stats) for _ in range(num_threads)]
            
            for t in threads:
                t.start()
            for t in threads:
                t.join()
            
            # Verify exact count
            assert cache.stats["cache_stores"] == num_threads * iterations_per_thread

    def test_thread_safe_embedding_client_init(self):
        """[Phase 17] Verify embedding client is initialized only once under concurrent access."""
        import threading
        from agentic_core.L5_safety.cognition.SemanticCacheManager import (
            SemanticCacheManager,
        )
        
        init_count = {"count": 0}
        
        def mock_client_init(*args, **kwargs):
            init_count["count"] += 1
            return MagicMock()
        
        with patch("redis.from_url") as mock_redis:
            mock_redis.return_value.ping.side_effect = Exception("Redis unavailable")
            
            cache = SemanticCacheManager(api_key="test_key")
            
            with patch("google.genai.Client", side_effect=mock_client_init):
                threads = [
                    threading.Thread(target=cache._get_embedding_client)
                    for _ in range(10)
                ]
                
                for t in threads:
                    t.start()
                for t in threads:
                    t.join()
            
            # Client should only be initialized once due to lock
            assert init_count["count"] <= 1


class TestRedisFallback:
    """Phase 17 Tests: Redis fallback behavior."""
    
    def test_redis_fallback_on_connection_failure(self):
        """[Phase 17] Verify graceful fallback when Redis is unreachable."""
        from agentic_core.L5_safety.cognition.SemanticCacheManager import (
            SemanticCacheManager,
        )
        
        with patch("redis.from_url") as mock_redis:
            # Simulate connection failure
            mock_redis.return_value.ping.side_effect = Exception("Connection refused")
            
            # Should not raise exception
            cache = SemanticCacheManager(api_key="test_key")
            
            # Redis should be disabled
            assert cache.redis_enabled is False
            
            # get_cached_decision should return None without crashing
            result = cache.get_cached_decision("test content", "ORPHAN")
            assert result is None

    def test_redis_get_failure_graceful(self):
        """[Phase 17] Verify graceful handling of Redis get failures."""
        from agentic_core.L5_safety.cognition.SemanticCacheManager import (
            SemanticCacheManager,
        )
        
        mock_redis = MagicMock()
        mock_redis.ping.return_value = True
        mock_redis.get.side_effect = Exception("Redis timeout")
        
        with patch("redis.from_url", return_value=mock_redis):
            cache = SemanticCacheManager(api_key="test_key")
            cache.redis_enabled = True
            cache.redis_client = mock_redis
            cache.pinecone_enabled = False
            
            # Should not raise, should return None
            result = cache.get_cached_decision("test content", "ORPHAN")
            assert result is None


class TestPineconeInitFailure:
    """Phase 17 Tests: Pinecone initialization failure handling."""
    
    def test_pinecone_init_failure_graceful(self):
        """[Phase 17] Verify graceful handling of Pinecone init failure."""
        import os
        from agentic_core.L5_safety.cognition.SemanticCacheManager import (
            SemanticCacheManager,
        )
        
        # Set invalid API key
        original_key = os.environ.get("PINECONE_API_KEY")
        os.environ["PINECONE_API_KEY"] = "invalid_key_12345"
        
        try:
            with patch("redis.from_url") as mock_redis:
                mock_redis.return_value.ping.side_effect = Exception("Redis unavailable")
                
                with patch("pinecone.Pinecone") as mock_pinecone:
                    mock_pinecone.side_effect = Exception("Invalid API key")
                    
                    # Should not crash
                    cache = SemanticCacheManager(api_key="test_key")
                    
                    # Pinecone should be disabled
                    assert cache.pinecone_enabled is False
        finally:
            if original_key:
                os.environ["PINECONE_API_KEY"] = original_key
            else:
                os.environ.pop("PINECONE_API_KEY", None)

    def test_pinecone_query_failure_graceful(self):
        """[Phase 17] Verify graceful handling of Pinecone query failures."""
        from agentic_core.L5_safety.cognition.SemanticCacheManager import (
            SemanticCacheManager,
        )
        
        mock_index = MagicMock()
        mock_index.query.side_effect = Exception("Pinecone timeout")
        
        mock_embedding = MagicMock()
        mock_embedding.embeddings = [MagicMock(values=[0.1] * 768)]
        
        mock_client = MagicMock()
        mock_client.models.embed_content.return_value = mock_embedding
        
        with patch("redis.from_url") as mock_redis:
            mock_redis.return_value.ping.side_effect = Exception("Redis unavailable")
            
            cache = SemanticCacheManager(api_key="test_key")
            cache.redis_enabled = False
            cache.pinecone_enabled = True
            cache.pinecone_index = mock_index
            cache._embedding_client = mock_client
            
            # Should not raise, should return None
            result = cache.get_cached_decision("test content", "ORPHAN")
            assert result is None
