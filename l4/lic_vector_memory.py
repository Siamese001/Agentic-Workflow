"""LIC Vector Memory - L4 Memory/State Layer

Implements vector memory abstraction aligned with Temporal KG.
Provides interface to vector stores for cached intelligence retrieval.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import hashlib


logger = logging.getLogger(__name__)


@dataclass
class VectorQueryResult:
    """Result from vector memory query"""
    id: str
    text: str
    metadata: Dict[str, Any]
    distance: float
    relevance_score: float


@dataclass
class VectorMemoryStats:
    """Vector memory statistics"""
    total_documents: int
    query_count: int
    avg_query_time_ms: float
    cache_hit_rate: float


class VectorMemoryStore:
    """
    L4 Vector Memory Store for LIC Intelligence
    
    Provides vector-based memory abstraction for cached research
    and intelligence data. Aligned with Temporal KG architecture.
    """
    
    def __init__(
        self,
        collection_name: str = "lic_intelligence",
        persist_directory: str = "./chroma_db",
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize vector memory store
        
        Args:
            collection_name: Name of vector collection
            persist_directory: Directory for persistent storage
            config: Optional configuration
        """
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self.config = config or self._get_default_config()
        
        # Initialize mock storage for now (would integrate with actual vector DB)
        self._mock_storage: Dict[str, VectorQueryResult] = {}
        self._stats = VectorMemoryStats(
            total_documents=0,
            query_count=0,
            avg_query_time_ms=0.0,
            cache_hit_rate=0.0
        )
        
        logger.info(f"VectorMemoryStore initialized for collection '{collection_name}'")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "query": {
                "default_n_results": 20,
                "similarity_threshold": 0.7,
                "max_query_time_ms": 5000
            },
            "storage": {
                "max_documents": 10000,
                "retention_days": 365
            }
        }
    
    async def query_memory(
        self,
        query_text: str,
        n_results: int = 20,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Query vector memory for relevant documents
        
        Args:
            query_text: Query string
            n_results: Number of results to return
            filter_metadata: Optional metadata filters
            
        Returns:
            List of query results as dictionaries
        """
        start_time = datetime.now()
        
        try:
            # Simulate vector query with mock data
            results = await self._execute_mock_query(query_text, n_results, filter_metadata)
            
            # Update statistics
            query_time = int((datetime.now() - start_time).total_seconds() * 1000)
            self._update_stats(query_time)
            
            logger.info(f"Vector query completed in {query_time}ms with {len(results)} results")
            
            return results
            
        except Exception as e:
            logger.error(f"Vector query failed: {str(e)}")
            return []
    
    async def query_by_company(
        self,
        company_name: str,
        query_text: str,
        n_results: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Query vector memory by company name
        
        Args:
            company_name: Company name to filter by
            query_text: Query string
            n_results: Number of results to return
            
        Returns:
            List of company-specific query results
        """
        filter_metadata = {"company_name": company_name}
        return await self.query_memory(query_text, n_results, filter_metadata)
    
    async def add_document(
        self,
        text: str,
        embedding: List[float],
        metadata: Dict[str, Any],
        document_id: Optional[str] = None
    ) -> str:
        """
        Add document to vector memory
        
        Args:
            text: Document text
            embedding: Document embedding vector
            metadata: Document metadata
            document_id: Optional document ID
            
        Returns:
            Document ID
        """
        if document_id is None:
            # Generate ID from content hash
            content_string = f"{text}_{metadata.get('source_url', '')}_{datetime.now().isoformat()}"
            document_id = hashlib.md5(content_string.encode()).hexdigest()
        
        # Create vector query result
        result = VectorQueryResult(
            id=document_id,
            text=text,
            metadata=metadata,
            distance=0.0,  # Not applicable for storage
            relevance_score=1.0  # Not applicable for storage
        )
        
        # Store in mock storage
        self._mock_storage[document_id] = result
        self._stats.total_documents += 1
        
        logger.debug(f"Added document {document_id} to vector memory")
        
        return document_id
    
    async def update_document(
        self,
        document_id: str,
        text: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update existing document in vector memory
        
        Args:
            document_id: Document ID to update
            text: Optional new text
            metadata: Optional new metadata
            
        Returns:
            True if updated successfully
        """
        if document_id not in self._mock_storage:
            logger.warning(f"Document {document_id} not found for update")
            return False
        
        existing = self._mock_storage[document_id]
        
        if text is not None:
            existing.text = text
        
        if metadata is not None:
            existing.metadata.update(metadata)
        
        logger.debug(f"Updated document {document_id} in vector memory")
        
        return True
    
    async def delete_document(self, document_id: str) -> bool:
        """
        Delete document from vector memory
        
        Args:
            document_id: Document ID to delete
            
        Returns:
            True if deleted successfully
        """
        if document_id not in self._mock_storage:
            logger.warning(f"Document {document_id} not found for deletion")
            return False
        
        del self._mock_storage[document_id]
        self._stats.total_documents -= 1
        
        logger.debug(f"Deleted document {document_id} from vector memory")
        
        return True
    
    async def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Get document by ID
        
        Args:
            document_id: Document ID
            
        Returns:
            Document data or None if not found
        """
        if document_id not in self._mock_storage:
            return None
        
        result = self._mock_storage[document_id]
        
        return {
            "id": result.id,
            "text": result.text,
            "metadata": result.metadata,
            "distance": result.distance,
            "relevance_score": result.relevance_score
        }
    
    async def list_documents(
        self,
        filter_metadata: Optional[Dict[str, Any]] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        List documents with optional filtering
        
        Args:
            filter_metadata: Optional metadata filters
            limit: Maximum number of documents to return
            
        Returns:
            List of documents
        """
        documents = []
        
        for result in self._mock_storage.values():
            # Apply metadata filter if provided
            if filter_metadata:
                matches = True
                for key, value in filter_metadata.items():
                    if result.metadata.get(key) != value:
                        matches = False
                        break
                if not matches:
                    continue
            
            documents.append({
                "id": result.id,
                "text": result.text,
                "metadata": result.metadata
            })
            
            if len(documents) >= limit:
                break
        
        return documents
    
    def get_stats(self) -> VectorMemoryStats:
        """Get vector memory statistics"""
        return self._stats
    
    async def clear_collection(self) -> bool:
        """Clear all documents from collection"""
        self._mock_storage.clear()
        self._stats.total_documents = 0
        
        logger.info("Cleared vector memory collection")
        
        return True
    
    async def _execute_mock_query(
        self,
        query_text: str,
        n_results: int,
        filter_metadata: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Execute mock vector query (simulates vector DB behavior)"""
        # Generate mock results based on query
        mock_results = []
        
        # Create some mock results for demonstration
        for i in range(min(n_results, 5)):  # Limit to 5 mock results
            document_id = f"mock_doc_{i}_{hashlib.md5(query_text.encode()).hexdigest()[:8]}"
            
            # Simulate relevance based on query keywords
            relevance_score = 0.9 - (i * 0.1)  # Decreasing relevance
            
            mock_result = {
                "id": document_id,
                "text": f"Mock document {i} relevant to '{query_text}' containing strategic information about company priorities and initiatives.",
                "metadata": {
                    "source_type": "company_intelligence",
                    "company_name": "Example Corp",
                    "retrieved_at": datetime.now().isoformat(),
                    "quality_score": relevance_score
                },
                "distance": 1.0 - relevance_score,  # Convert to distance
                "relevance_score": relevance_score
            }
            
            # Apply filter if provided
            if filter_metadata:
                matches = True
                for key, value in filter_metadata.items():
                    if mock_result["metadata"].get(key) != value:
                        matches = False
                        break
                if not matches:
                    continue
            
            mock_results.append(mock_result)
        
        return mock_results
    
    def _update_stats(self, query_time_ms: int):
        """Update query statistics"""
        self._stats.query_count += 1
        
        # Update average query time
        total_time = self._stats.avg_query_time_ms * (self._stats.query_count - 1) + query_time_ms
        self._stats.avg_query_time_ms = total_time / self._stats.query_count
        
        # Update cache hit rate (mock calculation)
        if self._stats.total_documents > 0:
            self._stats.cache_hit_rate = min(0.8, self._stats.query_count / (self._stats.total_documents + self._stats.query_count))
