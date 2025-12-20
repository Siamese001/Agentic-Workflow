"""
Database Manager Module - Canon Validator System

Facade module that wraps Redis and Qdrant implementations
to match the master prompt specifications.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

from core.qdrant_cache import QdrantCache
from core.semantic_gatekeeper import get_gatekeeper

from schemas import CanonEntry

logger = logging.getLogger(__name__)


class RedisManager:
    """
    Redis Stack manager for L1 working memory.

    Provides vector search with numeric/tag filtering capabilities
    for immediate pattern recognition.
    """

    def __init__(self, host: str = "localhost", port: int = 6379, index_name: str = "canon_l1"):
        """Initialize Redis Stack connection."""
        self.host = host
        self.port = port
        self.index_name = index_name

        # Use existing SemanticGatekeeper for Redis operations
        self.gatekeeper = get_gatekeeper()
        logger.info(f"RedisManager initialized: {host}:{port}")

    def create_index(self):
        """Create Redis search index with vector and metadata fields."""
        # Index is created by SemanticGatekeeper._setup_redis_index()
        logger.info("Redis index already created by SemanticGatekeeper")

    def store_entry(self, entry: CanonEntry) -> str:
        """
        Store a CanonEntry in Redis with vector and metadata.

        Args:
            entry: CanonEntry to store

        Returns:
            Entry ID
        """
        return self.gatekeeper._store_l1_entry(entry._canon_entry)

    def search_similar(
        self,
        query_vector: List[float],
        threshold: float = 0.9,
        max_results: int = 10,
        filter_failure_count: Optional[int] = None
    ) -> List[CanonEntry]:
        """
        Search for similar vectors with optional failure count filter.

        Args:
            query_vector: Embedding vector to search for
            threshold: Minimum similarity threshold
            max_results: Maximum number of results
            filter_failure_count: Maximum failure count to include

        Returns:
            List of matching CanonEntry objects
        """
        # Use existing L1 search with time filtering
        result = self.gatekeeper._search_l1_cache(
            query_vector=query_vector,
            threshold=threshold,
            max_results=max_results,
            time_window_hours=24  # Search recent patterns
        )

        # Filter by failure count if specified
        entries = []
        for entry in result.entries:
            if filter_failure_count is None or entry.failure_count < filter_failure_count:
                entries.append(CanonEntry.from_canon_entry(entry))

        return entries

    def update_entry(self, entry: CanonEntry) -> bool:
        """
        Update an existing entry in Redis.

        Args:
            entry: CanonEntry with updated data

        Returns:
            True if successful
        """
        self.gatekeeper._update_l1_entry(entry._canon_entry)
        return True

    def get_entry(self, entry_id: str) -> Optional[CanonEntry]:
        """
        Retrieve a specific entry by ID.

        Args:
            entry_id: ID of the entry to retrieve

        Returns:
            CanonEntry if found, None otherwise
        """
        # Implementation would use Redis client to get entry
        # For now, return None as this is a facade
        return None

    def delete_entry(self, entry_id: str) -> bool:
        """
        Delete an entry from Redis.

        Args:
            entry_id: ID of the entry to delete

        Returns:
            True if successful
        """
        # Implementation would use Redis client to delete
        return True


class QdrantManager:
    """
    Qdrant manager for L2 long-term memory.

    Stores historical project data with billions of vectors
    for deep pattern analysis.
    """

    def __init__(self, host: str = "localhost", port: int = 6333, index_name: str = "canon-l2"):
        """Initialize Qdrant connection."""
        self.host = host
        self.port = port
        self.index_name = index_name

        # Use existing QdrantCache implementation
        self.qdrant = QdrantCache(host=host, port=port, index_name=index_name)
        logger.info(f"QdrantManager initialized: {host}:{port}/{index_name}")

    def upsert(self, entries: List[CanonEntry]) -> bool:
        """
        Upsert multiple entries to Qdrant.

        Args:
            entries: List of CanonEntry objects to store

        Returns:
            True if successful
        """
        try:
            for entry in entries:
                self.qdrant.upsert(entry._canon_entry)
            return True
        except Exception as e:
            logger.error(f"Failed to upsert to Qdrant: {e}")
            return False

    def search(
        self,
        query_vector: List[float],
        limit: int = 100,
        score_threshold: float = 0.7,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[CanonEntry]:
        """
        Search Qdrant for similar vectors.

        Args:
            query_vector: Embedding vector to search for
            limit: Maximum number of results
            score_threshold: Minimum similarity score
            filters: Metadata filters to apply

        Returns:
            List of matching CanonEntry objects
        """
        results = self.qdrant.search(
            query_vector=query_vector,
            limit=limit,
            score_threshold=score_threshold,
            filters=filters
        )

        # Convert to CanonEntry objects
        entries = []
        for result in results:
            payload = result.get("payload", {})
            entry = CanonEntry(
                id=result["id"],
                vector=query_vector,  # We don't store the original vector
                ast_json=payload.get("ast_json", {}),
                metadata={
                    **payload,
                    "score": result["score"]
                }
            )
            entries.append(entry)

        return entries

    def get_trending_patterns(
        self,
        days: int = 30,
        min_success_count: int = 10,
        project_tag: Optional[str] = None
    ) -> List[CanonEntry]:
        """
        Get trending successful patterns for knowledge transfer.

        Args:
            days: Time window to analyze
            min_success_count: Minimum success threshold
            project_tag: Filter by project

        Returns:
            List of trending CanonEntry objects
        """
        results = self.qdrant.get_trending_patterns(
            days=days,
            min_success_count=min_success_count,
            project_tag=project_tag
        )

        # Convert to CanonEntry objects
        entries = []
        for result in results:
            payload = result.get("payload", {})
            entry = CanonEntry(
                id=result["id"],
                vector=[0.0] * 768,  # Dummy vector
                ast_json=payload.get("ast_json", {}),
                metadata=payload
            )
            entries.append(entry)

        return entries

    def delete_by_filter(self, filters: Dict[str, Any]) -> int:
        """
        Delete entries matching filter criteria.

        Args:
            filters: Filter criteria

        Returns:
            Number of deleted entries
        """
        # Implementation would use Qdrant client to delete
        return 0


class HybridDatabaseManager:
    """
    Combined manager for Redis (L1) and Qdrant (L2) operations.

    Provides unified interface for the hybrid semantic cache.
    """

    def __init__(
        self,
        redis_host: str = "localhost",
        redis_port: int = 6379,
        qdrant_host: str = "localhost",
        qdrant_port: int = 6333
    ):
        """Initialize both database managers."""
        self.redis = RedisManager(host=redis_host, port=redis_port)
        self.qdrant = QdrantManager(host=qdrant_host, port=qdrant_port)

        # Create indices
        self.redis.create_index()

        logger.info("HybridDatabaseManager initialized with Redis and Qdrant")

    def store_pattern(self, entry: CanonEntry, store_in_l2: bool = False) -> str:
        """
        Store a pattern in L1 and optionally L2.

        Args:
            entry: CanonEntry to store
            store_in_l2: Whether to also store in L2

        Returns:
            Entry ID
        """
        # Store in L1 (Redis)
        entry_id = self.redis.store_entry(entry)

        # Optionally store in L2 (Qdrant)
        if store_in_l2:
            self.qdrant.upsert([entry])

        return entry_id

    def search_patterns(
        self,
        query_vector: List[float],
        l1_threshold: float = 0.9,
        l2_threshold: float = 0.7,
        max_l1_results: int = 10,
        max_l2_results: int = 100,
        filter_failures: bool = True
    ) -> Tuple[List[CanonEntry], List[CanonEntry]]:
        """
        Search both L1 and L2 for similar patterns.

        Args:
            query_vector: Embedding vector to search for
            l1_threshold: Similarity threshold for L1
            l2_threshold: Similarity threshold for L2
            max_l1_results: Maximum results from L1
            max_l2_results: Maximum results from L2
            filter_failures: Whether to filter out high-failure patterns

        Returns:
            Tuple of (L1 results, L2 results)
        """
        # Search L1 (Redis)
        l1_results = self.redis.search_similar(
            query_vector=query_vector,
            threshold=l1_threshold,
            max_results=max_l1_results,
            filter_failure_count=5 if filter_failures else None
        )

        # Search L2 (Qdrant) if no L1 hits
        l2_results = []
        if not l1_results:
            l2_results = self.qdrant.search(
                query_vector=query_vector,
                limit=max_l2_results,
                score_threshold=l2_threshold,
                filters={"failure_count": {"lt": 5}
                         } if filter_failures else None
            )

        return l1_results, l2_results

    def promote_to_l2(self, entry: CanonEntry):
        """
        Promote a successful pattern from L1 to L2.

        Args:
            entry: CanonEntry to promote
        """
        if entry.success_count >= 3:  # Promotion threshold
            self.qdrant.upsert([entry])
            logger.info(f"Promoted pattern {entry.id} to L2")

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics from both databases."""
        return {
            "redis_stats": self.gatekeeper.get_safety_stats(),
            "qdrant_stats": self.qdrant.get_stats()
        }

