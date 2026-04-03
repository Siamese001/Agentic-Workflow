"""
Sovereign ChromaDB Client
Persistent semantic memory client aligned with Library OS SSOT principles.
"""

import chromadb
from typing import List, Dict, Any, Optional
import logging
from pathlib import Path
import hashlib

logger = logging.getLogger(__name__)


class SovereignChromaClient:
    """
    Sovereign ChromaDB client for semantic memory layer.

    Provides persistent storage and retrieval of semantic embeddings.
    For Wave 1, we'll use simple text-based embeddings as a fallback.
    """

    def __init__(self, persist_dir: str = "artifacts/chromadb"):
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

        logger.info("ChromaDB client initialized (using fallback embeddings)")

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
                metadata={"description": f"Semantic collection for {name}"}
            )
        return self._collections[name]

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate simple fallback embeddings for texts.

        Args:
            texts: List of text strings to embed

        Returns:
            List of embedding vectors (384-dim each)
        """
        if not texts:
            return []

        # Simple hash-based embedding as fallback
        embeddings = []
        for text in texts:
            # Create a deterministic embedding from text hash
            text_hash = hashlib.sha256(text.encode()).hexdigest()
            # Convert hash to 384-dim vector
            vector = []
            for i in range(0, len(text_hash), 2):
                hex_pair = text_hash[i:i+2]
                val = int(hex_pair, 16) / 255.0  # Normalize to 0-1
                vector.append(val)
            # Pad or truncate to 384 dimensions
            while len(vector) < 384:
                vector.append(0.0)
            embeddings.append(vector[:384])

        logger.debug(f"Generated {len(embeddings)} fallback embeddings of dimension 384")
        return embeddings

    def add_documents(
        self,
        collection_name: str,
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: Optional[List[str]] = None
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

        # Add documents
        collection.add(
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings,
            ids=ids or [f"doc_{i}" for i in range(len(documents))]
        )

        logger.info(f"Added {len(documents)} documents to collection '{collection_name}'")

    def query(
        self,
        collection_name: str,
        query_texts: List[str],
        n_results: int = 10,
        where: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
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
            where_document=where_document
        )

        logger.info(f"Queried collection '{collection_name}' with {len(query_texts)} queries, returned {len(results['ids'][0])} results")
        return results

    def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
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
            "persist_dir": str(self.persist_dir)
        }

    def list_collections(self) -> List[str]:
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
        except Exception as e:
            logger.error(f"Failed to delete collection '{collection_name}': {e}")
            raise
