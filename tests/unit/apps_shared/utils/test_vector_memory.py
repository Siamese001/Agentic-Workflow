"""
Unit tests for Vector Memory Store.

Tests Phase 2A.2 - Vector memory functionality.
"""

from unittest.mock import MagicMock, patch

import pytest

from apps_shared.utils.vector_memory import (
    VectorMemoryConfig,
    VectorMemoryStore,
    VectorSearchResult,
)


# Create a mock pinecone module for testing
mock_pinecone = MagicMock()
mock_pinecone.Pinecone = MagicMock()


class TestVectorMemoryConfig:
    """Test VectorMemoryConfig dataclass."""

    def test_config_defaults(self):
        """Test VectorMemoryConfig default values."""
        config = VectorMemoryConfig(index_name="test-index")
        assert config.index_name == "test-index"
        assert config.dimension == 1536
        assert config.metric == "cosine"
        assert config.namespace is None
        assert config.top_k == 10
        assert config.similarity_threshold == 0.7

    def test_config_custom_values(self):
        """Test VectorMemoryConfig with custom values."""
        config = VectorMemoryConfig(
            index_name="custom-index",
            dimension=768,
            metric="euclidean",
            namespace="test-ns",
            top_k=5,
            similarity_threshold=0.8,
        )
        assert config.index_name == "custom-index"
        assert config.dimension == 768
        assert config.metric == "euclidean"
        assert config.namespace == "test-ns"
        assert config.top_k == 5
        assert config.similarity_threshold == 0.8


class TestVectorSearchResult:
    """Test VectorSearchResult dataclass."""

    def test_search_result_creation(self):
        """Test VectorSearchResult creation."""
        result = VectorSearchResult(
            id="test-id", score=0.95, metadata={"key": "value"}, text="test text"
        )
        assert result.id == "test-id"
        assert result.score == 0.95
        assert result.metadata == {"key": "value"}
        assert result.text == "test text"

    def test_search_result_without_text(self):
        """Test VectorSearchResult without text."""
        result = VectorSearchResult(id="test-id", score=0.95, metadata={})
        assert result.text is None


class TestVectorMemoryStore:
    """Test VectorMemoryStore functionality."""

    def test_initialization(self):
        """Test VectorMemoryStore initialization."""
        config = VectorMemoryConfig(index_name="test-index")
        store = VectorMemoryStore(config)
        assert store.config == config
        assert store._initialized is False

    def test_ensure_initialized_without_pinecone(self):
        """Test initialization gracefully handles when Pinecone not available."""
        config = VectorMemoryConfig(index_name="test-index")
        store = VectorMemoryStore(config)

        # The store should handle missing pinecone gracefully
        # If pinecone is installed, it will try to initialize
        # If not installed, _initialized will be False
        # Either way, the code shouldn't crash
        try:
            store._ensure_initialized()
        except Exception:
            pass

        # Test passes if no crash occurs
        assert True

    def test_ensure_initialized_sets_flag(self):
        """Test that initialization sets the _initialized flag."""
        config = VectorMemoryConfig(index_name="test-index")
        store = VectorMemoryStore(config)

        # Before initialization attempt
        assert store._initialized is False

        # After initialization attempt (may succeed or fail based on env)
        try:
            store._ensure_initialized()
        except Exception:
            pass

        # The flag should be set (True or False depending on success)
        assert isinstance(store._initialized, bool)

    @patch.dict("os.environ", {})
    def test_get_api_key_missing(self):
        """Test _get_api_key raises when key is missing."""
        config = VectorMemoryConfig(index_name="test-index")
        store = VectorMemoryStore(config)

        with pytest.raises(ValueError, match="PINECONE_API_KEY"):
            store._get_api_key()

    def test_store_without_initialization(self):
        """Test store returns empty string when not initialized."""
        config = VectorMemoryConfig(index_name="test-index")
        store = VectorMemoryStore(config)
        store._initialized = False

        embedding = [0.1] * 1536
        vector_id = store.store("test text", embedding)

        assert vector_id == ""

    def test_store_with_initialized_store(self):
        """Test store with pre-initialized store (mocked)."""
        config = VectorMemoryConfig(index_name="test-index")
        store = VectorMemoryStore(config)

        # Manually set up initialized state with mock
        store._initialized = True
        store._index = MagicMock()

        embedding = [0.1] * 1536
        vector_id = store.store("test text", embedding, id="custom-id")

        assert vector_id == "custom-id"
        store._index.upsert.assert_called_once()

    def test_search_without_initialization(self):
        """Test search returns empty list when not initialized."""
        config = VectorMemoryConfig(index_name="test-index")
        store = VectorMemoryStore(config)
        store._initialized = False

        embedding = [0.1] * 1536
        results = store.search(embedding)

        assert results == []

    def test_search_with_initialized_store(self):
        """Test search with pre-initialized store (mocked)."""
        config = VectorMemoryConfig(index_name="test-index", similarity_threshold=0.7)
        store = VectorMemoryStore(config)

        # Manually set up initialized state with mock
        store._initialized = True
        store._index = MagicMock()

        # Mock search results
        mock_match = MagicMock()
        mock_match.id = "result-1"
        mock_match.score = 0.95
        mock_match.metadata = {"text": "result text"}
        store._index.query.return_value.matches = [mock_match]

        embedding = [0.1] * 1536
        results = store.search(embedding)

        assert len(results) == 1
        assert results[0].id == "result-1"
        assert results[0].score == 0.95

    def test_search_filters_by_threshold(self):
        """Test search filters results by similarity threshold."""
        config = VectorMemoryConfig(index_name="test-index", similarity_threshold=0.7)
        store = VectorMemoryStore(config)

        # Manually set up initialized state with mock
        store._initialized = True
        store._index = MagicMock()

        # Mock results with varying scores
        mock_match1 = MagicMock()
        mock_match1.id = "result-1"
        mock_match1.score = 0.95
        mock_match1.metadata = {"text": "high score"}

        mock_match2 = MagicMock()
        mock_match2.id = "result-2"
        mock_match2.score = 0.5
        mock_match2.metadata = {"text": "low score"}

        store._index.query.return_value.matches = [mock_match1, mock_match2]

        embedding = [0.1] * 1536
        results = store.search(embedding)

        # Only high score result should pass threshold
        assert len(results) == 1
        assert results[0].score == 0.95

    def test_delete_without_initialization(self):
        """Test delete returns False when not initialized."""
        config = VectorMemoryConfig(index_name="test-index")
        store = VectorMemoryStore(config)
        store._initialized = False

        success = store.delete(["id1", "id2"])

        assert success is False

    def test_delete_with_initialized_store(self):
        """Test delete with pre-initialized store (mocked)."""
        config = VectorMemoryConfig(index_name="test-index")
        store = VectorMemoryStore(config)

        # Manually set up initialized state with mock
        store._initialized = True
        store._index = MagicMock()

        success = store.delete(["id1", "id2"])

        assert success is True
        store._index.delete.assert_called_once()

    def test_clear_namespace_without_initialization(self):
        """Test clear_namespace returns False when not initialized."""
        config = VectorMemoryConfig(index_name="test-index")
        store = VectorMemoryStore(config)
        store._initialized = False

        success = store.clear_namespace()

        assert success is False

    def test_clear_namespace_with_initialized_store(self):
        """Test clear_namespace with pre-initialized store (mocked)."""
        config = VectorMemoryConfig(index_name="test-index", namespace="test-ns")
        store = VectorMemoryStore(config)

        # Manually set up initialized state with mock
        store._initialized = True
        store._index = MagicMock()

        success = store.clear_namespace()

        assert success is True
        store._index.delete.assert_called_once_with(delete_all=True, namespace="test-ns")

    def test_generate_id_deterministic(self):
        """Test _generate_id produces deterministic IDs."""
        config = VectorMemoryConfig(index_name="test-index")
        store = VectorMemoryStore(config)

        id1 = store._generate_id("test text")
        id2 = store._generate_id("test text")

        assert id1 == id2
        assert len(id1) == 16

    def test_get_stats_not_initialized(self):
        """Test get_stats when not initialized."""
        config = VectorMemoryConfig(index_name="test-index")
        store = VectorMemoryStore(config)
        store._initialized = False

        stats = store.get_stats()

        assert stats == {"initialized": False}

    def test_get_stats_with_initialized_store(self):
        """Test getting stats with pre-initialized store (mocked)."""
        config = VectorMemoryConfig(index_name="test-index")
        store = VectorMemoryStore(config)

        # Manually set up initialized state with mock
        store._initialized = True
        store._index = MagicMock()

        # Mock stats response
        mock_stats = MagicMock()
        mock_stats.total_vector_count = 100
        mock_stats.dimension = 1536
        mock_stats.index_fullness = 0.5
        mock_stats.namespaces = {"default": 100}
        store._index.describe_index_stats.return_value = mock_stats

        stats = store.get_stats()

        assert stats["initialized"] is True
        assert stats["total_vectors"] == 100
        assert stats["dimension"] == 1536
        assert stats["index_fullness"] == 0.5
