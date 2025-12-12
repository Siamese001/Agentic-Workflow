"""
L4 hybrid search for resume job alignment workflows.

Combines dense embeddings with sparse search for resume enhancement.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence
from datetime import datetime, UTC


@dataclass
class SearchFilter:
    """Metadata filter for resume workflow vector search."""
    
    field: str
    operator: str  # "eq", "ne", "gt", "gte", "lt", "lte", "in", "nin"
    value: Any


@dataclass
class TemporalFilter:
    """Temporal filter for resume workflow time-based queries."""
    
    field: str = "timestamp"
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    recent_only: bool = False
    recent_days: int = 90


@dataclass
class HybridSearchConfig:
    """Configuration for resume workflow hybrid search."""
    
    # Dense search config
    dense_weight: float = 0.7
    dense_top_k: int = 20
    
    # Sparse search config (BM25-style)
    sparse_weight: float = 0.3
    sparse_top_k: int = 20
    
    # Fusion config
    final_top_k: int = 10
    score_threshold: float = 0.7
    
    # Metadata filtering
    filters: List[SearchFilter] = field(default_factory=list)
    temporal_filter: Optional[TemporalFilter] = None
    
    # Reranking
    enable_rerank: bool = False
    rerank_model: str = "pinecone-rerank-v0"


@dataclass
class SearchResult:
    """Search result for resume workflow job alignment processing."""
    
    id: str
    score: float
    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    dense_score: float = 0.0
    sparse_score: float = 0.0
    fused_score: float = 0.0


class HybridSearchExecutor:
    """Executes hybrid search for resume job alignment workflows."""
    
    def __init__(self, pinecone_adapter: Any):
        """Initializes resume workflow hybrid search executor.
        
        Args:
            pinecone_adapter: L4 PineconeAdapter instance
        """
        self.adapter = pinecone_adapter
    
    def search(
        self,
        query: str,
        namespace: str,
        config: Optional[HybridSearchConfig] = None,
    ) -> List[SearchResult]:
        """Executes hybrid search for resume job alignment processing.
        
        Args:
            query: Search query text
            namespace: Pinecone namespace
            config: Hybrid search configuration
            
        Returns:
            List of search results sorted by fused score
        """
        if config is None:
            config = HybridSearchConfig()
        
        # Build metadata filter
        metadata_filter = self._build_metadata_filter(config)
        
        # Execute dense search
        dense_results = self._dense_search(
            query=query,
            namespace=namespace,
            top_k=config.dense_top_k,
            metadata_filter=metadata_filter,
        )
        
        # Execute sparse search (if supported)
        sparse_results = self._sparse_search(
            query=query,
            namespace=namespace,
            top_k=config.sparse_top_k,
            metadata_filter=metadata_filter,
        )
        
        # Fuse results using weighted RRF (Reciprocal Rank Fusion)
        fused_results = self._fuse_results(
            dense_results=dense_results,
            sparse_results=sparse_results,
            dense_weight=config.dense_weight,
            sparse_weight=config.sparse_weight,
        )
        
        # Apply score threshold
        filtered_results = [
            r for r in fused_results
            if r.fused_score >= config.score_threshold
        ]
        
        # Rerank if enabled
        if config.enable_rerank and filtered_results:
            filtered_results = self._rerank_results(
                query=query,
                results=filtered_results,
                model=config.rerank_model,
            )
        
        # Return top K
        return filtered_results[:config.final_top_k]
    
    def temporal_search(
        self,
        query: str,
        namespace: str,
        temporal_filter: TemporalFilter,
        config: Optional[HybridSearchConfig] = None,
    ) -> List[SearchResult]:
        """Executes temporal search for resume job alignment processing.
        
        Args:
            query: Search query text
            namespace: Pinecone namespace
            temporal_filter: Temporal filter configuration
            config: Hybrid search configuration
            
        Returns:
            List of search results filtered by time
        """
        if config is None:
            config = HybridSearchConfig()
        
        # Add temporal filter to config
        config.temporal_filter = temporal_filter
        
        # Execute hybrid search with temporal filter
        return self.search(query, namespace, config)
    
    def _dense_search(
        self,
        query: str,
        namespace: str,
        top_k: int,
        metadata_filter: Optional[Dict[str, Any]],
    ) -> List[SearchResult]:
        """Performs dense vector search for resume job alignment."""
        try:
            # Use L4 adapter for dense search
            l4_results = self.adapter.query_by_text(
                query_text=query,
                namespace=namespace,
                top_k=top_k,
                filter_dict=metadata_filter,
            )
            
            # Convert to SearchResult
            results = []
            for r in l4_results:
                results.append(SearchResult(
                    id=r.id,
                    score=r.score,
                    text=r.metadata.get("text", ""),
                    metadata=r.metadata,
                    dense_score=r.score,
                    sparse_score=0.0,
                    fused_score=r.score,
                ))
            
            return results
        except Exception:
            return []
    
    def _sparse_search(
        self,
        query: str,
        namespace: str,
        top_k: int,
        metadata_filter: Optional[Dict[str, Any]],
    ) -> List[SearchResult]:
        """Executes sparse search for resume job alignment processing.
        
        Note: This requires Pinecone sparse vectors support.
        For now, returns empty list as fallback.
        """
        # TODO: Implement sparse search when Pinecone sparse vectors are available
        # This would use the pinecone-sparse-english-v0 model
        return []
    
    def _fuse_results(
        self,
        dense_results: List[SearchResult],
        sparse_results: List[SearchResult],
        dense_weight: float,
        sparse_weight: float,
    ) -> List[SearchResult]:
        """Fuses dense and sparse results for resume job alignment.
        
        Reciprocal Rank Fusion (RRF):
        score = sum(weight / (k + rank)) for each result list
        where k is a constant (typically 60)
        """
        k = 60  # RRF constant
        
        # Build rank maps
        dense_ranks = {r.id: i + 1 for i, r in enumerate(dense_results)}
        sparse_ranks = {r.id: i + 1 for i, r in enumerate(sparse_results)}
        
        # Collect all unique IDs
        all_ids = set(dense_ranks.keys()) | set(sparse_ranks.keys())
        
        # Build result map
        result_map: Dict[str, SearchResult] = {}
        for r in dense_results + sparse_results:
            if r.id not in result_map:
                result_map[r.id] = r
        
        # Compute fused scores
        fused_results = []
        for doc_id in all_ids:
            result = result_map.get(doc_id)
            if result is None:
                continue
            
            # RRF score
            dense_rrf = dense_weight / (k + dense_ranks.get(doc_id, 1000))
            sparse_rrf = sparse_weight / (k + sparse_ranks.get(doc_id, 1000))
            fused_score = dense_rrf + sparse_rrf
            
            # Update result
            result.fused_score = fused_score
            fused_results.append(result)
        
        # Sort by fused score (descending)
        fused_results.sort(key=lambda x: x.fused_score, reverse=True)
        
        return fused_results
    
    def _rerank_results(
        self,
        query: str,
        results: List[SearchResult],
        model: str,
    ) -> List[SearchResult]:
        """Reranks results for resume job alignment processing.
        
        Note: This requires Pinecone reranking API.
        For now, returns results unchanged as fallback.
        """
        # TODO: Implement reranking when Pinecone rerank API is integrated
        # This would use models like:
        # - pinecone-rerank-v0
        # - cohere-rerank-3.5
        # - bge-reranker-v2-m3
        return results
    
    def _build_metadata_filter(
        self,
        config: HybridSearchConfig,
    ) -> Optional[Dict[str, Any]]:
        """Builds Pinecone metadata filter for resume job alignment."""
        if not config.filters and not config.temporal_filter:
            return None
        
        filter_dict: Dict[str, Any] = {}
        
        # Add custom filters
        for f in config.filters:
            if f.operator == "eq":
                filter_dict[f.field] = {"$eq": f.value}
            elif f.operator == "ne":
                filter_dict[f.field] = {"$ne": f.value}
            elif f.operator == "gt":
                filter_dict[f.field] = {"$gt": f.value}
            elif f.operator == "gte":
                filter_dict[f.field] = {"$gte": f.value}
            elif f.operator == "lt":
                filter_dict[f.field] = {"$lt": f.value}
            elif f.operator == "lte":
                filter_dict[f.field] = {"$lte": f.value}
            elif f.operator == "in":
                filter_dict[f.field] = {"$in": f.value}
            elif f.operator == "nin":
                filter_dict[f.field] = {"$nin": f.value}
        
        # Add temporal filter
        if config.temporal_filter:
            tf = config.temporal_filter
            
            if tf.recent_only:
                # Recent N days
                from datetime import timedelta
                now = datetime.now(UTC)
                start = now - timedelta(days=tf.recent_days)
                filter_dict[tf.field] = {"$gte": start.isoformat()}
            else:
                # Custom time range
                if tf.start_time and tf.end_time:
                    filter_dict[tf.field] = {
                        "$gte": tf.start_time.isoformat(),
                        "$lte": tf.end_time.isoformat(),
                    }
                elif tf.start_time:
                    filter_dict[tf.field] = {"$gte": tf.start_time.isoformat()}
                elif tf.end_time:
                    filter_dict[tf.field] = {"$lte": tf.end_time.isoformat()}
        
        return filter_dict if filter_dict else None


# =============================================================================
# Convenience Functions
# =============================================================================


def create_category_filter(category: str) -> SearchFilter:
    """Creates category filter for resume workflow documents."""
    return SearchFilter(field="category", operator="eq", value=category)


def create_recent_filter(days: int = 90) -> TemporalFilter:
    """Creates recent filter for resume workflow documents."""
    return TemporalFilter(recent_only=True, recent_days=days)


def create_date_range_filter(
    start: datetime,
    end: datetime,
) -> TemporalFilter:
    """Creates date range filter for resume workflow documents."""
    return TemporalFilter(start_time=start, end_time=end)



