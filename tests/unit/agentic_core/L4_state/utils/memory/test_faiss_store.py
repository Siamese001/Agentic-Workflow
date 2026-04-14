"""Tests for FAISS Vector Store implementation."""

from __future__ import annotations

from unittest.mock import patch

import numpy as np
import pytest

try:
    from agentic_core.L4_state.utils.memory.faiss_store import (
        FaissEmbeddingStore,
        FaissVectorStore,
        VectorDocument,
        get_global_faiss_store,
    )
except ImportError:
    pytest.skip("FAISS store not available", allow_module_level=True)


class TestFAISSVectorStore:
    """Test FAISS Vector Store functionality."""

    def setup_method(self) -> None:
        """Setup test fixtures."""
        self.store = FaissVectorStore(dimension=128, index_type="Flat")

    def test_initialization(self) -> None:
        """Test store initialization."""
        assert self.store.dimension == 128
        assert self.store.index_type == "Flat"
        assert self.store._index is not None
        assert len(self.store._documents) == 0

    def test_add_documents(self) -> None:
        """Test adding documents."""
        docs = [
            VectorDocument(
                id="doc1",
                vector=np.random.random(128),
                content="test content 1",
                metadata={"type": "test"},
            ),
            VectorDocument(
                id="doc2",
                vector=np.random.random(128),
                content="test content 2",
                metadata={"type": "test"},
            ),
        ]

        self.store.add_documents(docs)
        assert len(self.store._documents) == 2
        assert "doc1" in self.store._documents
        assert "doc2" in self.store._documents

    def test_search(self) -> None:
        """Test vector search."""
        docs = [
            VectorDocument(
                id="doc1",
                vector=np.random.random(128),
                content="similar content",
                metadata={"type": "test"},
            ),
            VectorDocument(
                id="doc2",
                vector=np.random.random(128),
                content="different content",
                metadata={"type": "test"},
            ),
        ]

        self.store.add_documents(docs)
        query_vector = docs[0].vector + np.random.normal(0, 0.01, 128)
        results = self.store.search(query_vector, k=2)

        assert len(results) == 2
        assert results[0]["id"] in ["doc1", "doc2"]
        assert results[0]["score"] >= 0.0

    def test_delete_document(self) -> None:
        """Test document deletion."""
        doc = VectorDocument(
            id="doc1",
            vector=np.random.random(128),
            content="test content",
            metadata={},
        )

        self.store.add_documents([doc])
        assert len(self.store._documents) == 1

        self.store.delete_document("doc1")
        assert len(self.store._documents) == 0

    def test_get_document(self) -> None:
        """Test document retrieval."""
        doc = VectorDocument(
            id="doc1",
            vector=np.random.random(128),
            content="test content",
            metadata={"type": "test"},
        )

        self.store.add_documents([doc])
        retrieved = self.store.get_document("doc1")

        assert retrieved is not None
        assert retrieved.id == "doc1"
        assert retrieved.content == "test content"
        assert retrieved.metadata["type"] == "test"

    def test_stats(self) -> None:
        """Test statistics."""
        doc = VectorDocument(
            id="doc1",
            vector=np.random.random(128),
            content="test content",
            metadata={},
        )

        self.store.add_documents([doc])
        stats = self.store.get_stats()

        assert stats["document_count"] == 1
        assert stats["dimension"] == 128
        assert stats["index_type"] == "Flat"

    def test_global_instance(self) -> None:
        """Test global store instance."""
        store = get_global_faiss_store()
        assert store is not None
        assert isinstance(store, FaissEmbeddingStore)

    @patch("faiss.IndexFlat")
    def test_ivf_index(self, mock_index) -> None:
        """Test IVF index creation."""
        store = FaissVectorStore(dimension=64, index_type="IVF")
        assert store.index_type == "IVF"

    def test_normalization(self) -> None:
        """Test vector normalization."""
        store = FaissVectorStore(dimension=4, normalize=True)

        vector = np.array([1.0, 2.0, 3.0, 4.0])
        normalized = store._normalize_vector(vector)

        norm = np.linalg.norm(normalized)
        assert abs(norm - 1.0) < 1e-6
