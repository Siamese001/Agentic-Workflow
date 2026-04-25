"""
Tests for SearchFusionEngine - multi-source search result fusion.

Coverage:
- Search result aggregation from multiple engines
- Result deduplication
- Relevance scoring and ranking
- Fusion strategy selection
- Timeout handling for slow engines
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from agentic_core.L1_cognition.reasoning.search_fusion_engine import SearchFusionEngine


class TestSearchFusionEngine:
    """Test suite for SearchFusionEngine."""

    def test_init_with_search_engines(self):
        """Test initialization with search engines."""
        engine1 = Mock()
        engine2 = Mock()
        
        fusion_engine = SearchFusionEngine(engines=[engine1, engine2])
        assert len(fusion_engine.engines) == 2

    def test_fuse_search_results(self):
        """Test fusion of search results from multiple engines."""
        engine1 = Mock()
        engine1.search.return_value = [
            {"id": "1", "content": "Result A", "score": 0.9}
        ]
        
        engine2 = Mock()
        engine2.search.return_value = [
            {"id": "2", "content": "Result B", "score": 0.8}
        ]
        
        fusion_engine = SearchFusionEngine(engines=[engine1, engine2])
        fused = fusion_engine.fuse("test query")
        
        assert len(fused) == 2

    def test_deduplicate_results(self):
        """Test deduplication of identical results."""
        engine1 = Mock()
        engine1.search.return_value = [
            {"id": "1", "content": "Result A", "score": 0.9}
        ]
        
        engine2 = Mock()
        engine2.search.return_value = [
            {"id": "1", "content": "Result A", "score": 0.85}  # Duplicate
        ]
        
        fusion_engine = SearchFusionEngine(engines=[engine1, engine2])
        fused = fusion_engine.fuse("test query")
        
        # Should have only one entry for duplicate
        assert len(fused) == 1

    def test_rank_results_by_fused_score(self):
        """Test results are ranked by fused relevance score."""
        engine1 = Mock()
        engine1.search.return_value = [
            {"id": "1", "content": "A", "score": 0.9},
            {"id": "2", "content": "B", "score": 0.7}
        ]
        
        engine2 = Mock()
        engine2.search.return_value = [
            {"id": "3", "content": "C", "score": 0.95}
        ]
        
        fusion_engine = SearchFusionEngine(engines=[engine1, engine2])
        fused = fusion_engine.fuse("test query")
        
        # Results should be sorted by score
        scores = [r.get("fused_score", r.get("score", 0)) for r in fused]
        assert scores == sorted(scores, reverse=True)

    def test_weighted_fusion_strategy(self):
        """Test weighted fusion strategy."""
        engine1 = Mock()
        engine1.weight = 0.7
        engine1.search.return_value = [{"id": "1", "score": 0.8}]
        
        engine2 = Mock()
        engine2.weight = 0.3
        engine2.search.return_value = [{"id": "1", "score": 0.6}]
        
        fusion_engine = SearchFusionEngine(
            engines=[engine1, engine2],
            strategy="weighted"
        )
        fused = fusion_engine.fuse("test query")
        
        # Weighted score should be closer to engine1
        assert 0.7 < fused[0]["fused_score"] < 0.8

    def test_reciprocal_rank_fusion(self):
        """Test reciprocal rank fusion strategy."""
        engine1 = Mock()
        engine1.search.return_value = [
            {"id": "1", "score": 0.9},
            {"id": "2", "score": 0.8}
        ]
        
        engine2 = Mock()
        engine2.search.return_value = [
            {"id": "2", "score": 0.95},
            {"id": "3", "score": 0.7}
        ]
        
        fusion_engine = SearchFusionEngine(
            engines=[engine1, engine2],
            strategy="rrf"
        )
        fused = fusion_engine.fuse("test query")
        
        # RRF should promote items appearing in multiple engines
        assert any(r["id"] == "2" for r in fused)

    def test_timeout_handling(self):
        """Test timeout handling for slow engines."""
        slow_engine = Mock()
        slow_engine.search.side_effect = lambda q: (_ for _ in ()).throw(
            TimeoutError("Engine timeout")
        )
        
        fast_engine = Mock()
        fast_engine.search.return_value = [{"id": "1", "score": 0.9}]
        
        fusion_engine = SearchFusionEngine(
            engines=[slow_engine, fast_engine],
            timeout_seconds=1
        )
        
        # Should not crash, return results from fast engine
        fused = fusion_engine.fuse("test query")
        assert len(fused) == 1

    def test_add_search_engine(self):
        """Test adding a search engine at runtime."""
        fusion_engine = SearchFusionEngine(engines=[])
        
        new_engine = Mock()
        fusion_engine.add_engine(new_engine)
        
        assert len(fusion_engine.engines) == 1

    def test_remove_search_engine(self):
        """Test removing a search engine."""
        engine = Mock()
        fusion_engine = SearchFusionEngine(engines=[engine])
        
        fusion_engine.remove_engine(engine)
        assert len(fusion_engine.engines) == 0

    def test_get_engine_status(self):
        """Test retrieving status of all engines."""
        engine1 = Mock()
        engine1.is_healthy.return_value = True
        engine2 = Mock()
        engine2.is_healthy.return_value = False
        
        fusion_engine = SearchFusionEngine(engines=[engine1, engine2])
        status = fusion_engine.get_engine_status()
        
        assert len(status) == 2
        assert status[0]["healthy"] is True
        assert status[1]["healthy"] is False

    def test_empty_query_handling(self):
        """Test handling of empty query."""
        fusion_engine = SearchFusionEngine(engines=[])
        
        with pytest.raises(ValueError):
            fusion_engine.fuse("")
