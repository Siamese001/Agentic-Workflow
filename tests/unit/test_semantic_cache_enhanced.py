"""Test enhanced semantic cache with semantic matching."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pytest
from unittest.mock import patch, MagicMock
import numpy as np

from agentic_core.runtime.shared_runtime.semantic_cache import (
    SemanticCache,
    CacheEntry,
    SemanticCacheHit,
    CacheMiss,
    create_semantic_cache,
    SIMILARITY_THRESHOLD,
)


class TestSemanticCacheExactMatch:
    """Test exact match caching (no embeddings)."""

    def test_cache_set_and_get_exact_match(self):
        """Test basic set and get with exact match."""
        cache = SemanticCache(enable_semantic_matching=False)
        cache.set("test prompt", "test response")
        result = cache.get("test prompt")
        
        assert isinstance(result, SemanticCacheHit)
        assert result.response == "test response"
        assert result.match_type == "exact"
        assert result.similarity_score == 1.0

    def test_cache_miss(self):
        """Test cache miss for non-existent prompt."""
        cache = SemanticCache(enable_semantic_matching=False)
        result = cache.get("non-existent prompt")
        
        assert isinstance(result, CacheMiss)
        assert result.reason == "not_found"

    def test_cache_with_context(self):
        """Test caching with context dict."""
        cache = SemanticCache(enable_semantic_matching=False)
        context = {"user_id": "123", "session": "abc"}
        cache.set("prompt", "response", context=context)
        
        # Same context should hit
        result = cache.get("prompt", context=context)
        assert isinstance(result, SemanticCacheHit)
        
        # Different context should miss
        result2 = cache.get("prompt", context={"user_id": "456"})
        assert isinstance(result2, CacheMiss)

    def test_cache_stats(self):
        """Test cache statistics tracking."""
        cache = SemanticCache(enable_semantic_matching=False)
        cache.set("prompt1", "response1")
        cache.get("prompt1")  # hit
        cache.get("prompt1")  # hit
        cache.get("missing")  # miss
        
        stats = cache.get_stats()
        assert stats["exact_hits"] == 2
        assert stats["misses"] == 1
        assert stats["semantic_hits"] == 0
        assert stats["current_size"] == 1

    def test_cache_eviction(self):
        """Test LRU eviction when max entries reached."""
        cache = SemanticCache(max_entries=2, enable_semantic_matching=False)
        cache.set("prompt1", "response1")
        cache.set("prompt2", "response2")
        cache.set("prompt3", "response3")  # Should evict prompt1
        
        assert isinstance(cache.get("prompt1"), CacheMiss)
        assert isinstance(cache.get("prompt2"), SemanticCacheHit)
        assert isinstance(cache.get("prompt3"), SemanticCacheHit)


class TestSemanticCacheSemanticMatching:
    """Test semantic similarity matching with embeddings."""

    @patch("agentic_core.runtime.shared_runtime.semantic_cache.get_embedding")
    def test_semantic_match(self, mock_get_embedding):
        """Test semantic matching finds similar prompts."""
        # Create normalized embeddings that are similar
        emb1 = np.array([1.0, 0.0, 0.0])
        emb2 = np.array([0.99, 0.14, 0.0])  # cosine ~0.99
        emb2 = emb2 / np.linalg.norm(emb2)
        
        call_count = [0]
        def mock_embed(text, model=None):
            call_count[0] += 1
            if call_count[0] == 1:
                return emb1.tolist()
            return emb2.tolist()
        
        mock_get_embedding.side_effect = mock_embed
        
        cache = SemanticCache(
            enable_semantic_matching=True,
            similarity_threshold=0.9
        )
        cache.set("What is the capital of France?", "Paris")
        
        # Query with semantically similar prompt
        result = cache.get("What's France's capital city?")
        
        assert isinstance(result, SemanticCacheHit)
        assert result.response == "Paris"
        assert result.match_type == "semantic"
        assert result.similarity_score >= 0.9

    @patch("agentic_core.runtime.shared_runtime.semantic_cache.get_embedding")
    def test_semantic_no_match_below_threshold(self, mock_get_embedding):
        """Test semantic matching rejects low similarity."""
        emb1 = np.array([1.0, 0.0, 0.0])
        emb2 = np.array([0.0, 1.0, 0.0])  # orthogonal, cosine = 0
        
        call_count = [0]
        def mock_embed(text, model=None):
            call_count[0] += 1
            if call_count[0] == 1:
                return emb1.tolist()
            return emb2.tolist()
        
        mock_get_embedding.side_effect = mock_embed
        
        cache = SemanticCache(
            enable_semantic_matching=True,
            similarity_threshold=0.9
        )
        cache.set("What is the capital of France?", "Paris")
        
        # Query with very different prompt
        result = cache.get("What is quantum physics?")
        
        assert isinstance(result, CacheMiss)

    @patch("agentic_core.runtime.shared_runtime.semantic_cache.get_embedding")
    def test_stats_track_semantic_hits(self, mock_get_embedding):
        """Test that semantic hits are tracked separately."""
        emb = np.array([1.0, 0.0, 0.0])
        mock_get_embedding.return_value = emb.tolist()
        
        cache = SemanticCache(
            enable_semantic_matching=True,
            similarity_threshold=0.9
        )
        cache.set("prompt1", "response1")
        cache.get("prompt1")  # exact hit
        cache.get("similar prompt")  # semantic hit (same embedding = 1.0)
        
        stats = cache.get_stats()
        assert stats["exact_hits"] == 1
        assert stats["semantic_hits"] == 1


class TestFactoryFunction:
    """Test the factory function."""

    def test_create_semantic_cache_defaults(self):
        """Test factory creates cache with defaults."""
        cache = create_semantic_cache()
        assert cache.ttl == 3600
        assert cache.max_entries == 10000
        assert cache.enable_semantic_matching is True

    def test_create_semantic_cache_custom(self):
        """Test factory with custom params."""
        cache = create_semantic_cache(
            ttl=1800,
            max_entries=500,
            enable_semantic_matching=False,
            similarity_threshold=0.95
        )
        assert cache.ttl == 1800
        assert cache.max_entries == 500
        assert cache.enable_semantic_matching is False
        assert cache.similarity_threshold == 0.95


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
