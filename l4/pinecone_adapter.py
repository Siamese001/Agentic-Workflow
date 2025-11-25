"""L4 - Pinecone Vector Store Adapter

This module centralizes all Pinecone operations in the L4 state layer.

Layer: L4 (State & Memory)
Responsibilities:
- Manage Pinecone index/namespace configuration
- Handle all vector upsert/query/delete operations
- Enforce consistent ID schemas and metadata
- Provide temporal query support
- Manage embedding pipelines

Non-responsibilities:
- Planning what to query (L1)
- Executing business logic (L2)
- Orchestration (L3)
- Safety decisions (L5)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence
from datetime import datetime, UTC
import hashlib
import os


@dataclass
class PineconeConfig:
    """Configuration for Pinecone vector store."""
    
    api_key: str
    index_name: str
    namespace_prefix: str = "agentic_workflow"
    embedding_model: str = "text-embedding-3-small"
    dimension: int = 1536


@dataclass
class VectorRecord:
    """Typed vector record for Pinecone operations."""
    
    id: str
    values: List[float]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class VectorQueryResult:
    """Result from vector similarity search."""
    
    id: str
    score: float
    metadata: Dict[str, Any]
    text: Optional[str] = None


class PineconeAdapter:
    """L4 adapter for Pinecone vector operations.
    
    This adapter ensures all Pinecone access goes through L4, maintaining
    proper layer boundaries. It provides:
    - Namespace management per user/job/workflow
    - Consistent ID schemas
    - Metadata filtering
    - Temporal queries
    - Centralized embedding
    """
    
    def __init__(self, config: PineconeConfig):
        """Initialize Pinecone adapter with configuration."""
        self.config = config
        self._client: Optional[Any] = None
        self._index: Optional[Any] = None
        
    def _ensure_client(self) -> Any:
        """Lazy initialization of Pinecone client."""
        if self._client is None:
            # Always use provider client to maintain SDK isolation
            from providers.pinecone_client import PineconeClient
            client = PineconeClient(
                    api_key=self.config.api_key,
                    index_name=self.config.index_name
                )
                self._client = client
                self._index = client.index
        return self._client
    
    def build_namespace(
        self,
        user_id: Optional[str] = None,
        job_id: Optional[str] = None,
        workflow_id: Optional[str] = None,
    ) -> str:
        """Build a namespace string from context identifiers.
        
        Namespaces follow pattern: {prefix}_{user}_{job}_{workflow}
        This ensures clean separation of data per context.
        """
        parts = [self.config.namespace_prefix]
        if user_id:
            parts.append(f"user_{user_id}")
        if job_id:
            parts.append(f"job_{job_id}")
        if workflow_id:
            parts.append(f"wf_{workflow_id}")
        return "_".join(parts)
    
    def build_id(
        self,
        record_type: str,
        content_hash: Optional[str] = None,
        timestamp: Optional[datetime] = None,
    ) -> str:
        """Build a consistent ID for vector records.
        
        ID pattern: {type}_{hash}_{timestamp}
        This ensures uniqueness and enables temporal queries.
        """
        parts = [record_type]
        
        if content_hash:
            parts.append(content_hash[:16])  # Truncate hash
        else:
            parts.append("auto")
            
        if timestamp:
            parts.append(timestamp.strftime("%Y%m%d%H%M%S"))
        else:
            parts.append(datetime.now(UTC).strftime("%Y%m%d%H%M%S"))
            
        return "_".join(parts)
    
    def hash_content(self, content: str) -> str:
        """Generate a stable hash for content."""
        return hashlib.sha256(content.encode()).hexdigest()
    
    def embed_text(self, text: str) -> List[float]:
        """Generate embeddings for text using configured model.
        
        This centralizes embedding generation to ensure consistency.
        """
        # Placeholder implementation - in production would use OpenAI/embeddings
        # For now, return a deterministic hash-based vector for testing
        import random
        hash_val = int(hashlib.sha256(text.encode()).hexdigest()[:16], 16)
        random.seed(hash_val % (2**32))
        return [float(random.random()) for _ in range(self.config.dimension)]
    
    async def retrieve_evidence(
        self,
        query: str,
        ctx: Any,
        retrieval_cfg: Any,
        hyde_query: Optional[str] = None,
        council_vote: Optional[Any] = None,
    ) -> List[Any]:
        """
        Retrieve evidence from vector store using DI-compatible interface.
        
        This method provides the same interface as run_rag_retrieval but
        operates through the L4 adapter, maintaining proper layer boundaries.
        
        Args:
            query: Base query string
            ctx: Execution context
            retrieval_cfg: Retrieval configuration
            hyde_query: Optional HYDE-generated query
            council_vote: Optional council vote for weighting
            
        Returns:
            List of Evidence objects
        """
        try:
            # Build namespace from context
            namespace = self.build_namespace(
                user_id=getattr(ctx, 'user_id', None),
                job_id=getattr(ctx, 'job_id', None),
                workflow_id=getattr(ctx, 'workflow_id', None)
            )
            
            # Use HYDE query if provided, otherwise base query
            search_query = hyde_query or query
            
            # Generate embedding for the query
            query_embedding = self.embed_text(search_query)
            
            # Perform similarity search
            self._ensure_client()
            if self._index is None:
                return []
            
            # Query Pinecone for similar vectors
            results = self._index.query(
                vector=query_embedding,
                namespace=namespace,
                top_k=getattr(retrieval_cfg, 'top_k', 10),
                include_metadata=True
            )
            
            # Convert results to Evidence objects
            from core.models.models import Evidence
            evidence_list = []
            
            for match in results.get('matches', []):
                evidence = Evidence(
                    text=match.get('metadata', {}).get('text', ''),
                    score=match.get('score', 0.0),
                    source=match.get('metadata', {}).get('source', 'pinecone'),
                    metadata={
                        'id': match.get('id'),
                        'namespace': namespace,
                        'retrieval_method': 'vector_similarity'
                    }
                )
                evidence_list.append(evidence)
            
            return evidence_list
            
        except Exception as e:
            # Log error but return empty list to maintain flow
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"PineconeAdapter retrieval failed: {e}")
            return []
    
    def upsert_records(
        self,
        records: Sequence[VectorRecord],
        namespace: str,
    ) -> None:
        """Upsert vector records to Pinecone.
        
        Args:
            records: Vector records to upsert
            namespace: Target namespace
        """
        self._ensure_client()
        
        # Convert to Pinecone format (tuples for new SDK)
        vectors = [
            (r.id, r.values, r.metadata)
            for r in records
        ]
        
        self._index.upsert(vectors=vectors, namespace=namespace)
    
    def query_vectors(
        self,
        query_vector: List[float],
        namespace: str,
        top_k: int = 10,
        metadata_filter: Optional[Dict[str, Any]] = None,
        score_threshold: Optional[float] = None,
    ) -> List[VectorQueryResult]:
        """Query vectors by similarity.
        
        Args:
            query_vector: Query embedding
            namespace: Target namespace
            top_k: Number of results to return
            metadata_filter: Optional metadata filters
            score_threshold: Optional minimum score threshold
            
        Returns:
            List of query results with scores and metadata
        """
        self._ensure_client()
        
        # Build query kwargs
        query_kwargs: Dict[str, Any] = {}
        if metadata_filter:
            query_kwargs["filter"] = metadata_filter
        
        # Execute query
        response = self._index.query(
            vector=query_vector,
            top_k=top_k,
            namespace=namespace,
            include_metadata=True,
            **query_kwargs
        )
        
        # Convert to typed results
        typed_results = []
        matches = response.matches if hasattr(response, 'matches') else response.get('matches', [])
        
        for match in matches:
            # Handle both object and dict formats
            if hasattr(match, 'score'):
                score = match.score
                match_id = match.id
                metadata = match.metadata or {}
            else:
                score = match.get("score", 0.0)
                match_id = match.get("id", "")
                metadata = match.get("metadata", {})
            
            # Apply score threshold if specified
            if score_threshold is not None and score < score_threshold:
                continue
                
            typed_results.append(
                VectorQueryResult(
                    id=match_id,
                    score=score,
                    metadata=metadata,
                    text=metadata.get("text"),
                )
            )
        
        return typed_results
    
    def query_by_text(
        self,
        query_text: str,
        namespace: str,
        top_k: int = 10,
        metadata_filter: Optional[Dict[str, Any]] = None,
        score_threshold: Optional[float] = None,
    ) -> List[VectorQueryResult]:
        """Query vectors using text (auto-embeds).
        
        Convenience method that embeds query text and performs vector search.
        """
        query_vector = self.embed_text(query_text)
        return self.query_vectors(
            query_vector=query_vector,
            namespace=namespace,
            top_k=top_k,
            metadata_filter=metadata_filter,
            score_threshold=score_threshold,
        )
    
    def query_temporal(
        self,
        query_vector: List[float],
        namespace: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        top_k: int = 10,
        metadata_filter: Optional[Dict[str, Any]] = None,
    ) -> List[VectorQueryResult]:
        """Query vectors with temporal constraints.
        
        Args:
            query_vector: Query embedding
            namespace: Target namespace
            start_time: Optional start of time range
            end_time: Optional end of time range
            top_k: Number of results
            metadata_filter: Additional metadata filters
            
        Returns:
            Filtered query results within time range
        """
        # Build temporal filter
        temporal_filter = metadata_filter.copy() if metadata_filter else {}
        
        if start_time:
            temporal_filter["timestamp"] = {"$gte": start_time.isoformat()}
        if end_time:
            if "timestamp" in temporal_filter:
                temporal_filter["timestamp"]["$lte"] = end_time.isoformat()
            else:
                temporal_filter["timestamp"] = {"$lte": end_time.isoformat()}
        
        return self.query_vectors(
            query_vector=query_vector,
            namespace=namespace,
            top_k=top_k,
            metadata_filter=temporal_filter if temporal_filter else None,
        )
    
    def delete_records(
        self,
        ids: Sequence[str],
        namespace: str,
    ) -> None:
        """Delete vector records by ID.
        
        Args:
            ids: Record IDs to delete
            namespace: Target namespace
        """
        self._ensure_client()
        self._index.delete(ids=list(ids), namespace=namespace)
    
    def upsert_text_records(
        self,
        texts: Sequence[str],
        namespace: str,
        record_type: str = "doc",
        metadata_list: Optional[Sequence[Dict[str, Any]]] = None,
    ) -> List[str]:
        """Convenience method to upsert text records with auto-embedding.
        
        Args:
            texts: Text content to embed and upsert
            namespace: Target namespace
            record_type: Type prefix for IDs
            metadata_list: Optional metadata for each text
            
        Returns:
            List of generated record IDs
        """
        if metadata_list and len(metadata_list) != len(texts):
            raise ValueError("metadata_list length must match texts length")
        
        records = []
        ids = []
        
        for i, text in enumerate(texts):
            # Generate embedding
            embedding = self.embed_text(text)
            
            # Build ID
            content_hash = self.hash_content(text)
            record_id = self.build_id(
                record_type=record_type,
                content_hash=content_hash,
            )
            ids.append(record_id)
            
            # Build metadata
            metadata = metadata_list[i].copy() if metadata_list else {}
            metadata["text"] = text
            metadata["timestamp"] = datetime.now(UTC).isoformat()
            metadata["record_type"] = record_type
            
            records.append(
                VectorRecord(
                    id=record_id,
                    values=embedding,
                    metadata=metadata,
                )
            )
        
        self.upsert_records(records=records, namespace=namespace)
        return ids



