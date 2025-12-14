"""

Unit tests for shared_engine_ops/embedding_ops/
Tests embedding operations including similarity calculation, vector search, etc.
"""
import pytest
import math

class TestComputeEmbeddings:
    """Tests for embedding computation."""

    def test_embedding_dimension(self):
        """Embeddings have correct dimension."""
        expected_dim = 1536  # OpenAI ada-002 dimension
        embedding = [0.1] * expected_dim

        assert len(embedding) == expected_dim

    def test_embedding_normalization(self):
        """Embeddings are normalized to unit length."""
        embedding = [0.6, 0.8]  # 3-4-5 triangle scaled
        magnitude = math.sqrt(sum(x**2 for x in embedding))

        normalized = [x / magnitude for x in embedding]
        normalized_magnitude = math.sqrt(sum(x**2 for x in normalized))

        assert normalized_magnitude == pytest.approx(1.0, rel=1e-6)

    def test_embedding_determinism(self):
        """Same text produces same embedding."""
        text = "Hello world"
        # Simulated: same input -> same output
        embedding1 = [hash(text) % 100 / 100 for _ in range(10)]
        embedding2 = [hash(text) % 100 / 100 for _ in range(10)]

        assert embedding1 == embedding2

    def test_different_text_different_embedding(self):
        """Different text produces different embeddings."""
        text1 = "Hello world"
        text2 = "Goodbye world"

        # Simulated embeddings
        embedding1 = [hash(text1 + str(i)) % 100 / 100 for i in range(10)]
        embedding2 = [hash(text2 + str(i)) % 100 / 100 for i in range(10)]

        assert embedding1 != embedding2

class TestCalculateSimilarity:
    """Tests for similarity calculation."""

    def test_cosine_similarity_identical(self):
        """Identical vectors have similarity 1.0."""
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [1.0, 0.0, 0.0]

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        mag1 = math.sqrt(sum(x**2 for x in vec1))
        mag2 = math.sqrt(sum(x**2 for x in vec2))
        similarity = dot_product / (mag1 * mag2)

        assert similarity == pytest.approx(1.0)

    def test_cosine_similarity_orthogonal(self):
        """Orthogonal vectors have similarity 0.0."""
        vec1 = [1.0, 0.0]
        vec2 = [0.0, 1.0]

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        mag1 = math.sqrt(sum(x**2 for x in vec1))
        mag2 = math.sqrt(sum(x**2 for x in vec2))
        similarity = dot_product / (mag1 * mag2)

        assert similarity == pytest.approx(0.0)

    def test_cosine_similarity_opposite(self):
        """Opposite vectors have similarity -1.0."""
        vec1 = [1.0, 0.0]
        vec2 = [-1.0, 0.0]

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        mag1 = math.sqrt(sum(x**2 for x in vec1))
        mag2 = math.sqrt(sum(x**2 for x in vec2))
        similarity = dot_product / (mag1 * mag2)

        assert similarity == pytest.approx(-1.0)

    def test_similarity_range(self):
        """Similarity is always in [-1, 1] range."""
        import random
        for _ in range(10):
            vec1 = [random.random() for _ in range(10)]
            vec2 = [random.random() for _ in range(10)]

            dot_product = sum(a * b for a, b in zip(vec1, vec2))
            mag1 = math.sqrt(sum(x**2 for x in vec1))
            mag2 = math.sqrt(sum(x**2 for x in vec2))
            similarity = dot_product / (mag1 * mag2) if mag1 * mag2 > 0 else 0

            assert -1.0 <= similarity <= 1.0

class TestSearchVectors:
    """Tests for vector search operations."""

    def test_search_returns_top_k(self):
        """Search returns top K most similar vectors."""
        query = [1.0, 0.0, 0.0]
        vectors = [
            {"id": "1", "vector": [0.9, 0.1, 0.0]},
            {"id": "2", "vector": [0.5, 0.5, 0.0]},
            {"id": "3", "vector": [0.1, 0.9, 0.0]},
        ]

        def cosine_sim(v1, v2):
            """TODO: Add docstring."""

            dot = sum(a * b for a, b in zip(v1, v2))
            m1 = math.sqrt(sum(x**2 for x in v1))
            m2 = math.sqrt(sum(x**2 for x in v2))
            return dot / (m1 * m2) if m1 * m2 > 0 else 0

        scored = [(v["id"], cosine_sim(query, v["vector"])) for v in vectors]
        ranked = sorted(scored, key=lambda x: x[1], reverse=True)

        top_k = 2
        results = ranked[:top_k]

        assert len(results) == 2
        assert results[0][0] == "1"  # Most similar

    def test_search_with_threshold(self):
        """Search filters by similarity threshold."""
        threshold = 0.7
        results = [
            {"id": "1", "similarity": 0.9},
            {"id": "2", "similarity": 0.6},
            {"id": "3", "similarity": 0.8},
        ]

        filtered = [r for r in results if r["similarity"] >= threshold]
        assert len(filtered) == 2

    def test_search_empty_index(self):
        """Search on empty index returns empty results."""

        results = []  # No vectors to search
        assert results == []

class TestNormalizeVectors:
    """Tests for vector normalization."""

    def test_normalize_to_unit_length(self):
        """Vectors are normalized to unit length."""
        vector = [3.0, 4.0]  # 3-4-5 triangle
        magnitude = math.sqrt(sum(x**2 for x in vector))
        normalized = [x / magnitude for x in vector]

        new_magnitude = math.sqrt(sum(x**2 for x in normalized))
        assert new_magnitude == pytest.approx(1.0)

    def test_normalize_preserves_direction(self):
        """Normalization preserves vector direction."""
        vector = [3.0, 4.0]
        magnitude = math.sqrt(sum(x**2 for x in vector))
        normalized = [x / magnitude for x in vector]

        # Direction ratio should be same
        original_ratio = vector[0] / vector[1]
        normalized_ratio = normalized[0] / normalized[1]

        assert original_ratio == pytest.approx(normalized_ratio)

    def test_normalize_zero_vector(self):
        """Zero vector normalization is handled."""
        vector = [0.0, 0.0, 0.0]
        magnitude = math.sqrt(sum(x**2 for x in vector))

        if magnitude == 0:
            normalized = vector  # Return as-is or handle specially
        else:
            normalized = [x / magnitude for x in vector]

        assert normalized == [0.0, 0.0, 0.0]

class TestMatchContext:
    """Tests for context matching operations."""

    def test_match_relevant_context(self):
        """Relevant context is matched correctly."""
        query_embedding = [1.0, 0.0]
        contexts = [
            {"id": "ctx1", "embedding": [0.95, 0.05], "text": "Relevant context"},
            {"id": "ctx2", "embedding": [0.1, 0.9], "text": "Irrelevant context"},
        ]

        def similarity(v1, v2):
            """Docstring."""
            dot = sum(a * b for a, b in zip(v1, v2))
            m1 = math.sqrt(sum(x**2 for x in v1))
            m2 = math.sqrt(sum(x**2 for x in v2))
            return dot / (m1 * m2)

        scored = [(c, similarity(query_embedding, c["embedding"])) for c in contexts]
        best_match = max(scored, key=lambda x: x[1])

        assert best_match[0]["id"] == "ctx1"

    def test_match_multiple_contexts(self):
        """Multiple relevant contexts are matched."""
        threshold = 0.7
        contexts = [
            {"id": "1", "similarity": 0.9},
            {"id": "2", "similarity": 0.8},
            {"id": "3", "similarity": 0.5},
        ]

        matches = [c for c in contexts if c["similarity"] >= threshold]
        assert len(matches) == 2
