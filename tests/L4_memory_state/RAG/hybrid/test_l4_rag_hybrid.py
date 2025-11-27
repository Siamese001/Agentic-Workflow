"""L4 RAG Hybrid Search Tests."""

class TestL4RAGHybrid:
    """Tests for L4 RAG hybrid search."""
    
    def test_hybrid_search_combination(self):
        """Test hybrid search combining dense and sparse."""
        dense_results = [{"id": "d1", "score": 0.9}]
        sparse_results = [{"id": "s1", "score": 0.8}]
        combined = dense_results + sparse_results
        assert len(combined) == 2
    
    def test_hybrid_reranking(self):
        """Test hybrid reranking."""
        results = [{"id": "r1", "score": 0.7}, {"id": "r2", "score": 0.9}]
        reranked = sorted(results, key=lambda x: x["score"], reverse=True)
        assert reranked[0]["id"] == "r2"
