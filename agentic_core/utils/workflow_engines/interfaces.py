"""
Hybrid Retrieval Interfaces

Defines the contracts for lexical retrieval, vector retrieval,
candidate fusion, and reranking components.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Document:
    """Retrieved document with relevance score."""

    doc_id: str
    content: str
    score: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "doc_id": self.doc_id,
            "content": self.content,
            "score": self.score,
            "metadata": self.metadata,
        }


class IRetrieverLexical(ABC):
    """Interface for lexical (BM25-style) retrieval."""

    @abstractmethod
    def retrieve(self, query: str, top_k: int = 50) -> list[Document]:
        """Retrieve documents using lexical matching.

        Args:
            query: Search query string
            top_k: Maximum number of documents to retrieve

        Returns:
            Ranked list of Document objects with BM25 scores
        """
        ...


class IRetrieverVector(ABC):
    """Interface for dense vector (FAISS-style) retrieval."""

    @abstractmethod
    def retrieve(self, query_embedding: list[float], top_k: int = 50) -> list[Document]:
        """Retrieve documents by vector similarity.

        Args:
            query_embedding: Dense embedding of the query
            top_k: Maximum number of documents to retrieve

        Returns:
            Ranked list of Document objects with similarity scores
        """
        ...

    @abstractmethod
    def embed_query(self, query: str) -> list[float]:
        """Embed a query string into a dense vector.

        Args:
            query: Query string to embed

        Returns:
            Dense embedding vector
        """
        ...


class ICandidateFusion(ABC):
    """Interface for merging lexical and vector retrieval results."""

    @abstractmethod
    def merge(self, lexical_results: list[Document], vector_results: list[Document]) -> list[Document]:
        """Merge and deduplicate results from lexical and vector retrievers.

        Args:
            lexical_results: Documents from lexical retrieval
            vector_results: Documents from vector retrieval

        Returns:
            Merged, deduplicated, and scored list of Document objects
        """
        ...


class IReranker(ABC):
    """Interface for cross-encoder or heuristic reranking."""

    @abstractmethod
    def rerank(self, query: str, candidates: list[Document]) -> list[Document]:
        """Rerank candidate documents against a query.

        Args:
            query: Original search query
            candidates: Documents to rerank

        Returns:
            Reranked list of Document objects (highest score first)
        """
        ...


__all__ = ["Document", "IRetrieverLexical", "IRetrieverVector", "ICandidateFusion", "IReranker"]
