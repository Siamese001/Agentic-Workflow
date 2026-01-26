# File: vector_memory.py
# Description: Vector Memory Store for persistent intelligence - v13.0
# Provides interface to ChromaDB for storing and querying pre-computed research
# HARDENED: 2026-01-01 - Environment variable support for paths

__version__ = "13.1"

import os
from datetime import datetime
from typing import Any

# ChromaDB for vector storage
try:
    import chromadb

    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    print("WARNING: ChromaDB not installed. Install with: pip install chromadb")

# Gemini embeddings


class VectorMemoryStore:
    """
    v13.0: Persistent vector memory using ChromaDB

    Stores pre-computed research findings with embeddings for semantic search.
    Used by:
    - IntelligenceLibrarian: Writes research findings
    - HOP-2 ResearchAgent: Queries for relevant context
    """

    def __init__(self, collection_name: str = None, persist_directory: str = None):
        """
        Initialize vector memory store

        Args:
            collection_name: Name of ChromaDB collection (defaults to CHROMA_COLLECTION_NAME env var or 'lic_intelligence')
            persist_directory: Directory for persistent storage (defaults to CHROMA_PERSIST_DIR env var or './chroma_db')
        """
        if not CHROMADB_AVAILABLE:
            raise ImportError("ChromaDB not installed. Install with: pip install chromadb")

        # Use environment variables for portability
        self.collection_name = collection_name or os.getenv(
            "CHROMA_COLLECTION_NAME", "lic_intelligence"
        )
        self.persist_directory = persist_directory or os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=Settings(anonymized_telemetry=False, allow_reset=True),
        )

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "LIC Intelligence Service - Pre-computed research"},
        )

        # Configure Gemini embedding
        self.embedding_model = "models/embedding-001"

        print(
            f"[VectorMemory] Initialized collection '{self.collection_name}' at {self.persist_directory}"
        )
        print(f"[VectorMemory] Current document count: {self.collection.count()}")

    def add_document(
        self,
        text: str,
        embedding: list[float],
        metadata: dict[str, Any],
        document_id: str | None = None,
    ):
        """
        Add a document to the vector store

        Args:
            text: Document text content
            embedding: Pre-computed embedding vector
            metadata: Document metadata (SourceType, company, etc.)
            document_id: Optional unique ID (auto-generated if None)
        """
        if document_id is None:
            # Generate ID from metadata
            import hashlib

            id_string = f"{metadata.get('source_url', '')}_{metadata.get('extracted_at', '')}"
            document_id = hashlib.md5(id_string.encode()).hexdigest()

        # Add to collection
        self.collection.add(
            embeddings=[embedding], documents=[text], metadatas=[metadata], ids=[document_id]
        )

        print(
            f"[VectorMemory] Added document: {metadata.get('SourceType', 'UNKNOWN')} - {metadata.get('title', '')[:50]}..."
        )

    def query_memory(
        self, query_text: str, n_results: int = 20, filter_metadata: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """
        Query the vector store for relevant documents

        Args:
            query_text: Query string to search for
            n_results: Number of results to return
            filter_metadata: Optional metadata filters (e.g., {"company_name": "Tech Giants Corp"})

        Returns:
            List of result dictionaries with text, metadata, and distance
        """
        print(f"[VectorMemory] Querying for: '{query_text[:50]}...'")

        # Generate query embedding
        query_embedding = self._embed_query(query_text)

        # Query collection
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=filter_metadata if filter_metadata else None,
        )

        # Format results
        formatted_results = []

        if results["ids"] and results["ids"][0]:
            for i in range(len(results["ids"][0])):
                formatted_results.append(
                    {
                        "id": results["ids"][0][i],
                        "text": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "distance": results["distances"][0][i] if "distances" in results else None,
                    }
                )

        print(f"[VectorMemory] Found {len(formatted_results)} results")

        return formatted_results

    def query_by_company(
        self, company_name: str, query_text: str, n_results: int = 20
    ) -> list[dict[str, Any]]:
        """
        Query for documents about a specific company

        Args:
            company_name: Company name to filter by
            query_text: Query string
            n_results: Number of results

        Returns:
            List of result dictionaries
        """
        return self.query_memory(
            query_text=query_text,
            n_results=n_results,
            filter_metadata={"company_name": company_name},
        )

    def query_by_executive(
        self, executive_name: str, query_text: str, n_results: int = 10
    ) -> list[dict[str, Any]]:
        """
        Query for documents about a specific executive

        Args:
            executive_name: Executive name to filter by
            query_text: Query string
            n_results: Number of results

        Returns:
            List of result dictionaries
        """
        return self.query_memory(
            query_text=query_text,
            n_results=n_results,
            filter_metadata={"executive_name": executive_name},
        )

    def get_strategic_briefs(
        self, company_name: str, max_age_days: int = 90
    ) -> list[dict[str, Any]]:
        """
        Get all strategic briefs for a company

        Args:
            company_name: Company name
            max_age_days: Maximum age of documents in days

        Returns:
            List of strategic brief documents
        """
        # Query without embedding - just filter by metadata
        all_docs = self.collection.get(
            where={"$and": [{"company_name": company_name}, {"SourceType": "STRATEGIC_BRIEF"}]}
        )

        # Filter by age
        results = []
        for i in range(len(all_docs["ids"])):
            metadata = all_docs["metadatas"][i]
            age_days = metadata.get("age_days", 0)

            if age_days <= max_age_days:
                results.append(
                    {
                        "id": all_docs["ids"][i],
                        "text": all_docs["documents"][i],
                        "metadata": metadata,
                    }
                )

        print(f"[VectorMemory] Found {len(results)} strategic briefs for {company_name}")
        return results

    def _embed_query(self, query_text: str) -> list[float]:
        """
        Generate embedding for query text

        Args:
            query_text: Text to embed

        Returns:
            Embedding vector
        """
        try:
            result = genai.embed_content(
                model=self.embedding_model, content=query_text, TaskType="retrieval_query"
            )
            return result["embedding"]
        except Exception as e:
            print(f"[VectorMemory] Error generating embedding: {e}")
            # Return zero vector as fallback
            return [0.0] * 768  # Gemini embedding dimension

    def get_collection_stats(self) -> dict[str, Any]:
        """
        Get statistics about the collection

        Returns:
            Dictionary with collection statistics
        """
        total_count = self.collection.count()

        # Get source type breakdown
        source_types = {}

        # Sample documents to get source type distribution
        sample_size = min(100, total_count)
        if sample_size > 0:
            sample = self.collection.get(limit=sample_size)

            for metadata in sample["metadatas"]:
                SourceType = metadata.get("SourceType", "UNKNOWN")
                source_types[SourceType] = source_types.get(SourceType, 0) + 1

        return {
            "total_documents": total_count,
            "source_type_distribution": source_types,
            "collection_name": self.collection_name,
            "persist_directory": self.persist_directory,
        }

    def reset_collection(self):
        """
        DANGER: Delete all documents in the collection
        """
        print(f"[VectorMemory] WARNING: Resetting collection '{self.collection_name}'")
        self.client.delete_collection(name=self.collection_name)

        # Recreate empty collection
        self.collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"description": "LIC Intelligence Service - Pre-computed research"},
        )

        print("[VectorMemory] Collection reset complete")

    def delete_by_company(self, company_name: str):
        """
        Delete all documents for a specific company

        Args:
            company_name: Company name to delete
        """
        print(f"[VectorMemory] Deleting documents for company: {company_name}")

        # Get all documents for this company
        docs = self.collection.get(where={"company_name": company_name})

        if docs["ids"]:
            self.collection.delete(ids=docs["ids"])
            print(f"[VectorMemory] Deleted {len(docs['ids'])} documents")
        else:
            print(f"[VectorMemory] No documents found for {company_name}")

    def delete_old_documents(self, max_age_days: int = 180):
        """
        Delete documents older than specified age

        Args:
            max_age_days: Maximum age in days
        """
        print(f"[VectorMemory] Deleting documents older than {max_age_days} days")

        # Get all documents
        all_docs = self.collection.get()

        delete_ids = []

        for i in range(len(all_docs["ids"])):
            metadata = all_docs["metadatas"][i]
            age_days = metadata.get("age_days", 0)

            if age_days > max_age_days:
                delete_ids.append(all_docs["ids"][i])

        if delete_ids:
            self.collection.delete(ids=delete_ids)
            print(f"[VectorMemory] Deleted {len(delete_ids)} old documents")
        else:
            print("[VectorMemory] No old documents found")


def test_vector_memory():
    """
    Test the vector memory store
    """
    print("\n=== Testing Vector Memory Store ===\n")

    # Initialize
    store = VectorMemoryStore(collection_name="lic_test")

    # Add test documents
    test_docs = [
        {
            "text": "Tech Giants Corp announced new AI platform focused on enterprise scalability",
            "metadata": {
                "SourceType": "NEWS_ARTICLE_COMPANY",
                "company_name": "Tech Giants Corp",
                "title": "Tech Giants Launches Enterprise AI",
                "age_days": 5,
                "extracted_at": datetime.now().isoformat(),
            },
        },
        {
            "text": "Sarah Johnson, VP of Engineering, discusses strategic priorities including cloud migration and team expansion",
            "metadata": {
                "SourceType": "STRATEGIC_BRIEF",
                "company_name": "Tech Giants Corp",
                "executive_name": "Sarah Johnson",
                "title": "VP Engineering Roadmap",
                "age_days": 10,
                "extracted_at": datetime.now().isoformat(),
            },
        },
    ]

    for doc in test_docs:
        # Generate embedding
        embedding = genai.embed_content(
            model="models/embedding-001", content=doc["text"], TaskType="retrieval_document"
        )["embedding"]

        store.add_document(text=doc["text"], embedding=embedding, metadata=doc["metadata"])

    # Test queries
    print("\n--- Test Query 1: AI platform ---")
    results = store.query_by_company(
        company_name="Tech Giants Corp", query_text="AI platform scalability", n_results=5
    )

    for result in results:
        print(f"  - {result['metadata']['title']}: {result['text'][:80]}...")

    print("\n--- Test Query 2: Strategic priorities ---")
    results = store.query_by_executive(
        executive_name="Sarah Johnson", query_text="strategic priorities", n_results=5
    )

    for result in results:
        print(f"  - {result['metadata']['title']}: {result['text'][:80]}...")

    # Stats
    print("\n--- Collection Stats ---")
    stats = store.get_collection_stats()
    print(f"Total documents: {stats['total_documents']}")
    print(f"Source types: {stats['source_type_distribution']}")

    # Cleanup
    print("\n--- Cleanup ---")
    store.reset_collection()
    print("Test complete\n")


if __name__ == "__main__":
    """
    Test the vector memory store

    Usage:
        python memory_LIC.py
    """
    test_vector_memory()
