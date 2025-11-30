"""
RAG Provider Module
LEVEL 5 - Retrieval-Augmented Generation provider for memory operations
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
import logging
from enum import Enum

class RetrievalMode(Enum):
    SIMILARITY = "similarity"
    HYBRID = "hybrid"
    SEMANTIC = "semantic"
    KEYWORD = "keyword"

@dataclass
class RAGDocument:
    """Represents a document in RAG system"""
    doc_id: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    tags: List[str] = field(default_factory=list)

@dataclass
class RetrievalResult:
    """Result of document retrieval"""
    documents: List[RAGDocument]
    scores: List[float]
    query: str
    retrieval_time: float
    total_found: int

@dataclass
class RAGConfig:
    """Configuration for RAG provider"""
    embedding_model: str = "text-embedding-ada-002"
    vector_dimension: int = 1536
    max_retrieved_docs: int = 10
    similarity_threshold: float = 0.7
    enable_caching: bool = True
    cache_ttl_seconds: int = 3600

class RAGProvider:
    """Retrieval-Augmented Generation provider for memory operations"""

    def __init__(self, config: RAGConfig = None):
        self.config = config or RAGConfig()
        self.logger = logging.getLogger(__name__)
        self.documents: Dict[str, RAGDocument] = {}
        self.document_cache: Dict[str, RetrievalResult] = {}
        self._embedding_cache: Dict[str, List[float]] = {}

    async def add_document(self, document: RAGDocument) -> str:
        """Add a document to the RAG system"""
        try:
            # Generate embedding if not provided
            if document.embedding is None:
                document.embedding = await self._generate_embedding(document.content)

            # Store document
            self.documents[document.doc_id] = document

            # Clear relevant cache entries
            self._clear_cache_for_document(document.doc_id)

            self.logger.info(f"Added document {document.doc_id} to RAG system")
            return document.doc_id

        except Exception as e:
            self.logger.error(f"Failed to add document: {str(e)}")
            raise e

    async def retrieve_documents(
        self,
        query: str,
        mode: RetrievalMode = RetrievalMode.SIMILARITY,
        max_results: int = None
    ) -> RetrievalResult:
        """Retrieve documents based on query"""
        try:
            start_time = datetime.utcnow()
            max_results = max_results or self.config.max_retrieved_docs

            # Check cache first
            cache_key = f"{query}_{mode.value}_{max_results}"
            if self.config.enable_caching and cache_key in self.document_cache:
                cached_result = self.document_cache[cache_key]
                self.logger.debug(f"Retrieved {len(cached_result.documents)} documents from cache")
                return cached_result

            # Generate query embedding
            query_embedding = await self._generate_embedding(query)

            # Retrieve based on mode
            if mode == RetrievalMode.SIMILARITY:
                documents, scores = await self._similarity_search(query_embedding, max_results)
            elif mode == RetrievalMode.HYBRID:
                documents, scores = await self._hybrid_search(query, query_embedding, max_results)
            elif mode == RetrievalMode.SEMANTIC:
                documents, scores = await self._semantic_search(query_embedding, max_results)
            else:  # KEYWORD
                documents, scores = await self._keyword_search(query, max_results)

            # Filter by similarity threshold
            filtered_docs = []
            filtered_scores = []
            for doc, score in zip(documents, scores):
                if score >= self.config.similarity_threshold:
                    filtered_docs.append(doc)
                    filtered_scores.append(score)

            retrieval_time = (datetime.utcnow() - start_time).total_seconds()

            result = RetrievalResult(
                documents=filtered_docs,
                scores=filtered_scores,
                query=query,
                retrieval_time=retrieval_time,
                total_found=len(filtered_docs)
            )

            # Cache result
            if self.config.enable_caching:
                self.document_cache[cache_key] = result

            self.logger.info(f"Retrieved {len(filtered_docs)} documents in {retrieval_time:.3f}s")
            return result

        except Exception as e:
            self.logger.error(f"Document retrieval failed: {str(e)}")
            raise e

    async def update_document(self, doc_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing document"""
        try:
            if doc_id not in self.documents:
                return False

            document = self.documents[doc_id]

            # Update fields
            if "content" in updates:
                document.content = updates["content"]
                document.embedding = await self._generate_embedding(document.content)

            if "metadata" in updates:
                document.metadata.update(updates["metadata"])

            if "tags" in updates:
                document.tags = updates["tags"]

            # Clear cache
            self._clear_cache_for_document(doc_id)

            self.logger.info(f"Updated document {doc_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to update document: {str(e)}")
            return False

    async def delete_document(self, doc_id: str) -> bool:
        """Delete a document from the RAG system"""
        try:
            if doc_id not in self.documents:
                return False

            del self.documents[doc_id]

            # Clear cache
            self._clear_cache_for_document(doc_id)

            self.logger.info(f"Deleted document {doc_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to delete document: {str(e)}")
            return False

    async def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text"""
        # Check cache first
        if text in self._embedding_cache:
            return self._embedding_cache[text]

        # Mock embedding generation
        await asyncio.sleep(0.01)  # Simulate API call

        # Generate mock embedding (normalized random vector)
        import random
        embedding = [random.random() for _ in range(self.config.vector_dimension)]

        # Normalize embedding
        magnitude = sum(x**2 for x in embedding) ** 0.5
        embedding = [x / magnitude for x in embedding]

        # Cache embedding
        self._embedding_cache[text] = embedding

        return embedding

    async def _similarity_search(
        self, query_embedding: List[float], max_results: int
    ) -> tuple[List[RAGDocument], List[float]]:
        """Perform similarity search"""
        similarities = []

        for doc in self.documents.values():
            if doc.embedding:
                similarity = self._calculate_cosine_similarity(query_embedding, doc.embedding)
                similarities.append((doc, similarity))

        # Sort by similarity and return top results
        similarities.sort(key=lambda x: x[1], reverse=True)

        documents = [doc for doc, _ in similarities[:max_results]]
        scores = [score for _, score in similarities[:max_results]]

        return documents, scores

    async def _hybrid_search(
        self, query: str, query_embedding: List[float], max_results: int
    ) -> tuple[List[RAGDocument], List[float]]:
        """Perform hybrid search (similarity + keyword)"""
        # Get similarity results
        sim_docs, sim_scores = await self._similarity_search(query_embedding, max_results * 2)

        # Get keyword results
        kw_docs, kw_scores = await self._keyword_search(query, max_results * 2)

        # Combine results
        combined_scores = {}
        for doc, score in zip(sim_docs, sim_scores):
            combined_scores[doc.doc_id] = {"doc": doc, "sim_score": score, "kw_score": 0.0}

        for doc, score in zip(kw_docs, kw_scores):
            if doc.doc_id in combined_scores:
                combined_scores[doc.doc_id]["kw_score"] = score
            else:
                combined_scores[doc.doc_id] = {"doc": doc, "sim_score": 0.0, "kw_score": score}

        # Calculate hybrid scores
        final_results = []
        for doc_data in combined_scores.values():
            hybrid_score = 0.7 * doc_data["sim_score"] + 0.3 * doc_data["kw_score"]
            final_results.append((doc_data["doc"], hybrid_score))

        # Sort and return top results
        final_results.sort(key=lambda x: x[1], reverse=True)

        documents = [doc for doc, _ in final_results[:max_results]]
        scores = [score for _, score in final_results[:max_results]]

        return documents, scores

    async def _semantic_search(
        self, query_embedding: List[float], max_results: int
    ) -> tuple[List[RAGDocument], List[float]]:
        """Perform semantic search (similar to similarity but with semantic weighting)"""
        # For now, use similarity search
        return await self._similarity_search(query_embedding, max_results)

    async def _keyword_search(
        self, query: str, max_results: int
    ) -> tuple[List[RAGDocument], List[float]]:
        """Perform keyword search"""
        query_terms = query.lower().split()
        scores = []

        for doc in self.documents.values():
            content_lower = doc.content.lower()

            # Calculate keyword match score
            matched_terms = sum(1 for term in query_terms if term in content_lower)
            score = matched_terms / len(query_terms) if query_terms else 0.0

            scores.append((doc, score))

        # Sort by score and return top results
        scores.sort(key=lambda x: x[1], reverse=True)

        documents = [doc for doc, _ in scores[:max_results]]
        keyword_scores = [score for _, score in scores[:max_results]]

        return documents, keyword_scores

    def _calculate_cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        if len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = sum(a**2 for a in vec1) ** 0.5
        magnitude2 = sum(b**2 for b in vec2) ** 0.5

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)

    def _clear_cache_for_document(self, doc_id: str) -> None:
        """Clear cache entries related to a document"""
        # Remove document from embedding cache
        if doc_id in self.documents:
            doc = self.documents[doc_id]
            if doc.content in self._embedding_cache:
                del self._embedding_cache[doc.content]

        # Clear retrieval cache (simplified - in production would be more selective)
        self.document_cache.clear()

    def get_statistics(self) -> Dict[str, Any]:
        """Get RAG system statistics"""
        return {
            "total_documents": len(self.documents),
            "cached_embeddings": len(self._embedding_cache),
            "cached_retrievals": len(self.document_cache),
            "config": {
                "embedding_model": self.config.embedding_model,
                "vector_dimension": self.config.vector_dimension,
                "max_retrieved_docs": self.config.max_retrieved_docs,
                "similarity_threshold": self.config.similarity_threshold
            }
        }

    def clear_cache(self) -> None:
        """Clear all caches"""
        self.document_cache.clear()
        self._embedding_cache.clear()
        self.logger.info("Cleared all caches")

__all__ = [
    "RAGProvider", "RAGDocument", "RetrievalResult",
    "RAGConfig", "RetrievalMode"
]
