"""
Sovereign ChromaDB Client
Persistent semantic memory client aligned with Library OS SSOT principles.
"""

import json
import logging
import os
from pathlib import Path
from typing import Any

import chromadb

logger = logging.getLogger(__name__)


class SovereignChromaClient:
    """
    Sovereign ChromaDB client for semantic memory layer.

    Provides persistent storage and retrieval of semantic embeddings.
    For Wave 1, we'll use simple text-based embeddings as a fallback.
    """

    def __init__(self, persist_dir: str = "data/cache/chromadb"):
        """
        Initialize ChromaDB client.

        Args:
            persist_dir: Directory for persistent ChromaDB storage
        """
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)

        # Initialize persistent ChromaDB client
        self.client = chromadb.PersistentClient(path=str(self.persist_dir))

        # Cache for collections
        self._collections = {}

        logger.info("ChromaDB client initialized")

    def get_collection(self, name: str):
        """
        Get or create a ChromaDB collection.

        Args:
            name: Collection name

        Returns:
            ChromaDB collection object
        """
        if name not in self._collections:
            self._collections[name] = self.client.get_or_create_collection(
                name=name,
                metadata={"hnsw:space": "cosine", "description": f"Semantic collection for {name}"},
            )
        return self._collections[name]

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """
        Generate BGE-M3 embeddings for texts.

        Args:
            texts: List of text strings to embed

        Returns:
            List of embedding vectors (1024-dim each)

        Raises:
            RuntimeError: If EMBEDDING_ENABLED is not set to 'true'
        """
        if not texts:
            return []

        if os.getenv("EMBEDDING_ENABLED", "").lower() != "true":
            raise RuntimeError(
                "embed_texts() called but EMBEDDING_ENABLED is not 'true'. "
                "Set EMBEDDING_ENABLED=true to enable BGE-M3 embedding."
            )

        from agentic_core.embeddings.bge_runtime import bge_embed_batch

        embeddings = bge_embed_batch(texts)
        logger.debug(f"Generated {len(embeddings)} BGE-M3 embeddings of dimension 1024")
        return embeddings

    @staticmethod
    def _sanitize_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
        """Coerce metadata values to ChromaDB v2 scalar types.

        ChromaDB v2 rejects non-scalar metadata values (lists, dicts, None).
        This normalizer:
          - JSON-encodes list/dict values into a string
          - Replaces None with an empty string
          - Leaves str/int/float/bool unchanged
        """
        sanitized: dict[str, Any] = {}
        for key, value in metadata.items():
            if isinstance(value, (str, int, float, bool)):
                sanitized[key] = value
            elif value is None:
                sanitized[key] = ""
            elif isinstance(value, (list, tuple, dict)):
                sanitized[key] = json.dumps(value, ensure_ascii=False, sort_keys=True)
            else:
                sanitized[key] = str(value)
        return sanitized

    def add_documents(
        self,
        collection_name: str,
        documents: list[str],
        metadatas: list[dict[str, Any]],
        ids: list[str] | None = None,
    ):
        """
        Add documents to a ChromaDB collection.

        Args:
            collection_name: Name of the collection
            documents: List of document texts
            metadatas: List of metadata dictionaries
            ids: Optional list of document IDs
        """
        if len(documents) != len(metadatas):
            raise ValueError("Documents and metadatas must have same length")

        if ids and len(ids) != len(documents):
            raise ValueError("IDs must match documents length")

        # Generate embeddings
        embeddings = self.embed_texts(documents)

        # Get collection
        collection = self.get_collection(collection_name)

        # Sanitize metadata for ChromaDB v2 (scalar values only)
        sanitized_metadatas = [self._sanitize_metadata(m) for m in metadatas]

        # Add documents
        collection.add(
            documents=documents,
            metadatas=sanitized_metadatas,
            embeddings=embeddings,
            ids=ids or [f"doc_{i}" for i in range(len(documents))],
        )

        logger.info(f"Added {len(documents)} documents to collection '{collection_name}'")

    def query(
        self,
        collection_name: str,
        query_texts: list[str],
        n_results: int = 10,
        where: dict[str, Any] | None = None,
        where_document: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Query a ChromaDB collection.

        Args:
            collection_name: Name of the collection
            query_texts: List of query texts
            n_results: Number of results to return
            where: Metadata filter conditions
            where_document: Document content filter conditions

        Returns:
            Query results with documents, metadatas, and distances
        """
        # Generate query embeddings
        query_embeddings = self.embed_texts(query_texts)

        # Get collection
        collection = self.get_collection(collection_name)

        # Query collection
        results = collection.query(
            query_embeddings=query_embeddings,
            n_results=n_results,
            where=where,
            where_document=where_document,
        )

        logger.info(
            f"Queried collection '{collection_name}' with {len(query_texts)} queries, returned {len(results['ids'][0])} results"
        )
        return results

    def get_collection_stats(self, collection_name: str) -> dict[str, Any]:
        """
        Get statistics for a collection.

        Args:
            collection_name: Name of the collection

        Returns:
            Collection statistics
        """
        collection = self.get_collection(collection_name)
        count = collection.count()

        return {
            "name": collection_name,
            "document_count": count,
            "persist_dir": str(self.persist_dir),
        }

    def list_collections(self) -> list[str]:
        """
        List all collection names.

        Returns:
            List of collection names
        """
        return [col.name for col in self.client.list_collections()]

    def delete_collection(self, collection_name: str):
        """
        Delete a collection.

        Args:
            collection_name: Name of the collection to delete
        """
        try:
            self.client.delete_collection(name=collection_name)
            if collection_name in self._collections:
                del self._collections[collection_name]
            logger.info(f"Deleted collection '{collection_name}'")
        except (AttributeError, RuntimeError, TypeError, ValueError) as e:
            logger.error(f"Failed to delete collection '{collection_name}': {e}")
            raise
