"""
LIC Vector Memory Store - ChromaDB-based vector store for research.

Ported from: archives/legacy_lic/Agentic LIC/memory_LIC.py
"""

import hashlib
from dataclasses import dataclass


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

@dataclass
class VectorDocument:
    """Document stored in vector memory."""

    id: str
    text: str
    metadata: dict[str, object]
    embedding: list[float] | None = None
    distance: float | None = None


@dataclass
class QueryResult:
    """Result from a vector memory query."""

    documents: list[VectorDocument]
    total_count: int
    query_text: str
    query_time_ms: float = 0.0


@dataclass
class MemoryStats:
    """Statistics about the vector memory store."""

    collection_name: str
    document_count: int
    persist_directory: str


class LICVectorMemory:
    """
    Persistent vector memory using ChromaDB.

    Stores pre-computed research findings with embeddings for semantic search.
    Used by:
    - IntelligenceLibrarian: Writes research findings
    - HOP-2 ResearchAgent: Queries for relevant context
    """

    def __init__(
        self,
        collection_name: str = "lic_intelligence",
        persist_directory: str = "./chroma_db",
    ) -> None:
        """
        Initialize vector memory store.

        Args:
            collection_name: Name of ChromaDB collection
            persist_directory: Directory for persistent storage
        """
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self._client: object = None
        self._collection: object = None
        self._initialized = False

    def initialize(self) -> bool:
        """
        Initialize the ChromaDB client and collection.

        Returns:
            True if initialization successful, False otherwise
        """
        try:
            import chromadb

            self._client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True,
                ),
            )

            self._collection = self._client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "LIC Intelligence Provider - Pre-computed research"},
            )

            self._initialized = True
            return True

        except ImportError:
            # ChromaDB not installed - use mock mode
            self._initialized = False
            return False
        except (ValueError, TypeError, RuntimeError, OSError):
            self._initialized = False
            return False

    def is_initialized(self) -> bool:
        """Check if the memory store is initialized."""
        return self._initialized

    def add_document(
        self,
        text: str,
        metadata: dict[str, object],
        embedding: list[float] | None = None,
        document_id: str | None = None,
    ) -> str:
        """Module implementation."""
        if document_id is None:
            # Generate ID from metadata
            id_string = f"{metadata.get('source_url', '')}_{metadata.get('extracted_at', '')}"
            document_id = hashlib.md5(id_string.encode()).hexdigest()

        if self._initialized and self._collection is not None:
            if embedding is not None:
                self._collection.add(
                    embeddings=[embedding],
                    documents=[text],
                    metadatas=[metadata],
                    ids=[document_id],
                )
            else:
                self._collection.add(
                    documents=[text],
                    metadatas=[metadata],
                    ids=[document_id],
                )

        return document_id

    def query_memory(
        self,
        query_text: str,
        n_results: int = 20,
        filter_metadata: dict[str, object] | None = None,
    ) -> QueryResult:
        """
        Query the vector store for relevant documents.

        Args:
            query_text: Query string to search for
            n_results: Number of results to return
            filter_metadata: Optional metadata filters

        Returns:
            QueryResult with matching documents
        """
        import time

        start_time = time.time()
        documents: list[VectorDocument] = []

        if self._initialized and self._collection is not None:
            results = self._collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where=filter_metadata if filter_metadata else None,
            )

            if results["ids"] and results["ids"][0]:
                for i in range(len(results["ids"][0])):
                    doc = VectorDocument(
                        id=results["ids"][0][i],
                        text=results["documents"][0][i],
                        metadata=results["metadatas"][0][i],
                        distance=(results["distances"][0][i] if "distances" in results else None),
                    )
                    documents.append(doc)

        query_time_ms = (time.time() - start_time) * 1000

        return QueryResult(
            documents=documents,
            total_count=len(documents),
            query_text=query_text,
            query_time_ms=query_time_ms,
        )

    def query_by_company(
        self,
        company_name: str,
        query_text: str,
        n_results: int = 20,
    ) -> QueryResult:
        """Query documents filtered by company name."""
        return self.query_memory(
            query_text=query_text,
            n_results=n_results,
            filter_metadata={"company_name": company_name},
        )

    def query_by_executive(
        self,
        executive_name: str,
        query_text: str,
        n_results: int = 10,
    ) -> QueryResult:
        """Query documents filtered by executive name."""
        return self.query_memory(
            query_text=query_text,
            n_results=n_results,
            filter_metadata={"executive_name": executive_name},
        )

    def get_strategic_briefs(
        self,
        company_name: str,
        max_age_days: int = 90,
    ) -> QueryResult:
        """Get strategic briefs for a company."""
        return self.query_memory(
            query_text=f"strategic brief {company_name}",
            n_results=5,
            filter_metadata={
                "company_name": company_name,
                "SourceType": "STRATEGIC_BRIEF",
            },
        )

    def get_stats(self) -> MemoryStats:
        """Get statistics about the memory store."""
        doc_count = 0
        if self._initialized and self._collection is not None:
            doc_count = self._collection.count()

        return MemoryStats(
            collection_name=self.collection_name,
            document_count=doc_count,
            persist_directory=self.persist_directory,
        )

    def delete_document(self, document_id: str) -> bool:
        """Delete a document by ID."""
        if self._initialized and self._collection is not None:
            try:
                self._collection.delete(ids=[document_id])
                return True
            except (ValueError, TypeError, RuntimeError, KeyError):
                return False
        return False

    def clear_collection(self) -> bool:
        """Clear all documents from the collection."""
        if self._initialized and self._client is not None:
            try:
                self._client.delete_collection(self.collection_name)
                self._collection = self._client.get_or_create_collection(
                    name=self.collection_name,
                    metadata={"description": "LIC Intelligence Provider - Pre-computed research"},
                )
                return True
            except (ValueError, TypeError, RuntimeError, KeyError):
                return False
        return False


class MockVectorMemory(LICVectorMemory):
    """Mock implementation for testing without ChromaDB."""

    def __init__(
        self,
        collection_name: str = "lic_intelligence",
        persist_directory: str = "./chroma_db",
    ) -> None:
        """Initialize mock vector memory."""
        super().__init__(collection_name, persist_directory)
        self._documents: dict[str, VectorDocument] = {}
        self._initialized = True

    def initialize(self) -> bool:
        """Mock initialization always succeeds."""
        self._initialized = True
        return True

    def add_document(
        self,
        text: str,
        metadata: dict[str, object],
        embedding: list[float] | None = None,
        document_id: str | None = None,
    ) -> str:
        """Add document to mock store."""
        if document_id is None:
            id_string = f"{metadata.get('source_url', '')}_{metadata.get('extracted_at', '')}"
            document_id = hashlib.md5(id_string.encode()).hexdigest()

        self._documents[document_id] = VectorDocument(
            id=document_id,
            text=text,
            metadata=metadata,
            embedding=embedding,
        )

        return document_id

    def query_memory(
        self,
        query_text: str,
        n_results: int = 20,
        filter_metadata: dict[str, object] | None = None,
    ) -> QueryResult:
        """Query mock store with simple text matching."""
        import time

        start_time = time.time()
        results: list[VectorDocument] = []

        query_lower = query_text.lower()
        for doc in self._documents.values():
            # Simple text matching
            if query_lower in doc.text.lower():
                # Check metadata filter
                if filter_metadata:
                    match = all(doc.metadata.get(k) == v for k, v in filter_metadata.items())
                    if not match:
                        continue
                results.append(doc)

            if len(results) >= n_results:
                break

        query_time_ms = (time.time() - start_time) * 1000

        return QueryResult(
            documents=results,
            total_count=len(results),
            query_text=query_text,
            query_time_ms=query_time_ms,
        )

    def get_stats(self) -> MemoryStats:
        """Get mock store statistics."""
        return MemoryStats(
            collection_name=self.collection_name,
            document_count=len(self._documents),
            persist_directory=self.persist_directory,
        )

    def delete_document(self, document_id: str) -> bool:
        """Delete from mock store."""
        if document_id in self._documents:
            del self._documents[document_id]
            return True
        return False

    def clear_collection(self) -> bool:
        """Clear mock store."""
        self._documents.clear()
        return True


def create_vector_memory(
    collection_name: str = "lic_intelligence",
    persist_directory: str = "./chroma_db",
    use_mock: bool = False,
) -> LICVectorMemory:
    """
    builder function to create a vector memory store.

    Args:
        collection_name: Name of the collection
        persist_directory: Directory for persistence
        use_mock: If True, use mock implementation

    Returns:
        LICVectorMemory instance
    """
    if use_mock:
        return MockVectorMemory(collection_name, persist_directory)

    memory = LICVectorMemory(collection_name, persist_directory)
    if not memory.initialize():
        # Fall back to mock if ChromaDB not available
        return MockVectorMemory(collection_name, persist_directory)

    return memory
