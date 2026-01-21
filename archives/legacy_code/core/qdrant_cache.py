"""
Qdrant L2 Cache Implementation for Hybrid Semantic Search

Provides advanced hybrid search capabilities combining vector similarity
with complex metadata filtering for the L5 Meta-Learning system.
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    Range,
    VectorParams,
)

from schemas.canon_models import CanonEntry

logger = logging.getLogger(__name__)


class QdrantCache:
    """
    Qdrant-based L2 cache for long-term pattern storage.

    Supports hybrid search with complex metadata filtering
    for trend analysis and knowledge transfer.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6333,
        index_name: str = "canon-l2",
        vector_dim: int = 768
    ):
        """Initialize Qdrant client and index."""
        self.client = QdrantClient(host=host, port=port)
        self.index_name = index_name
        self.vector_dim = vector_dim

        # Create index if it doesn't exist
        self._setup_index()

        logger.info(f"Qdrant L2 cache initialized: {host}:{port}/{index_name}")

    def _setup_index(self):
        """Create the collection with proper schema."""
        try:
            # Check if collection exists
            collections = self.client.get_collections().collections
            exists = any(c.name == self.index_name for c in collections)

            if not exists:
                # Create collection with vector and payload schema
                self.client.create_collection(
                    collection_name=self.index_name,
                    vectors_config=VectorParams(
                        size=self.vector_dim,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Created Qdrant collection: {self.index_name}")
            else:
                logger.info(
                    f"Using existing Qdrant collection: {self.index_name}")

        except Exception as e:
logger.error(f"Failed to setup Qdrant index: {e}")
            raise

    def search(
        self,
        query_vector: List[float],
        limit: int = 20,
        score_threshold: float = 0.7,
        filters: Optional[Dict[str, Any]] = None,
        with_payload: bool = True
    ) -> List[Dict]:
        """
        Search with hybrid filtering capabilities.

        Args:
            query_vector: Vector to search for
            limit: Maximum number of results
            score_threshold: Minimum similarity score
            filters: Dict of field filters
            with_payload: Include payload in results

        Returns:
            List of matching points with scores
        """
        try:
            # Build filter from dict
            query_filter = self._build_filter(filters) if filters else None

            # Execute search
            results = self.client.search(
                collection_name=self.index_name,
                query_vector=query_vector,
                query_filter=query_filter,
                limit=limit,
                score_threshold=score_threshold,
                with_payload=with_payload,
                with_vectors=False
            )

            # Convert to dict format
            return [
                {
                    "id": str(point.id),
                    "score": point.score,
                    "payload": point.payload or {}
                }
                for point in results
            ]

        except Exception as e:
logger.error(f"Qdrant search failed: {e}")
            return []

    def _build_filter(self, filters: Dict[str, Any]) -> Filter:
        """Build Qdrant filter from dict specification."""
        conditions = []

        for field, value in filters.items():
            if isinstance(value, dict):
                # Range filter
                if "gte" in value or "lte" in value or "gt" in value or "lt" in value:
                    range_condition = {}
                    if "gte" in value:
                        range_condition["gte"] = value["gte"]
                    if "lte" in value:
                        range_condition["lte"] = value["lte"]
                    if "gt" in value:
                        range_condition["gt"] = value["gt"]
                    if "lt" in value:
                        range_condition["lt"] = value["lt"]

                    conditions.append(
                        FieldCondition(
                            key=field,
                            range=Range(**range_condition)
                        )
                    )

                # In list filter
                elif "in" in value:
                    conditions.append(
                        FieldCondition(
                            key=field,
                            match=MatchValue(any=value["in"])
                        )
                    )
            else:
                # Exact match
                conditions.append(
                    FieldCondition(
                        key=field,
                        match=MatchValue(value=value)
                    )
                )

        return Filter(must=conditions) if conditions else None

    def upsert(self, entry: CanonEntry, max_retries: int = 3) -> str:
        """
        Insert or update a pattern in L2 cache with retry logic.

        Args:
            entry: CanonEntry to store
            max_retries: Maximum number of retry attempts

        Returns:
            Point ID
        """
        last_error = None

        for attempt in range(max_retries + 1):
            try:
                # Prepare payload with all metadata
                payload = {
                    "ast_json": entry.ast_json,
                    "ast_hash": entry.ast_hash,
                    "policy_key": entry.policy_key,
                    "failure_count": entry.failure_count,
                    "success_count": entry.success_count,
                    "latency_ms": entry.latency_ms,
                    "last_validated": entry.last_validated.isoformat(),
                    "project_tag": entry.project_tag,
                    **entry.metadata
                }

                # Create point
                point = PointStruct(
                    id=str(entry.id),
                    vector=entry.vector,
                    payload=payload
                )

                # Upsert
                self.client.upsert(
                    collection_name=self.index_name,
                    points=[point]
                )

                if attempt > 0:
                    logger.info(
                        f"Upserted entry {entry.id} to Qdrant L2 after {attempt} retries")
                else:
                    logger.debug(f"Upserted entry {entry.id} to Qdrant L2")

                return str(entry.id)

            except Exception as e:
last_error = e
                if attempt < max_retries:
                    # Exponential backoff
                    delay = 2 ** attempt
                    logger.warning(
                        f"Qdrant upsert failed (attempt {attempt + 1}/{max_retries + 1}), retrying in {delay}s: {e}")
                    time.sleep(delay)
                else:
                    logger.error(
                        f"Failed to upsert to Qdrant after {max_retries + 1} attempts: {e}")

        raise last_error

    def get_trending_patterns(
        self,
        days: int = 30,
        min_success_count: int = 10,
        project_tag: Optional[str] = None
    ) -> List[Dict]:
        """
        Get trending successful patterns for knowledge transfer.

        Args:
            days: Time window to analyze
            min_success_count: Minimum success threshold
            project_tag: Filter by project

        Returns:
            List of trending patterns
        """
        try:
            # Build filter for trending patterns
            filters = {
                "success_count": {"gte": min_success_count},
                "last_validated": {
                    "gte": (datetime.utcnow() - timedelta(days=days)).isoformat()
                }
            }

            if project_tag:
                filters["project_tag"] = project_tag

            # Search with random vector to get all matching patterns
            import random
            random_vector = [random.random() for _ in range(self.vector_dim)]

            results = self.search(
                query_vector=random_vector,
                limit=100,
                score_threshold=0.0,  # No similarity filter
                filters=filters
            )

            # Sort by success rate
            for result in results:
                payload = result["payload"]
                total = payload.get("failure_count", 0) + \
                    payload.get("success_count", 0)
                result["success_rate"] = payload.get(
                    "success_count", 0) / total if total > 0 else 0

            results.sort(key=lambda x: x["success_rate"], reverse=True)

            return results[:20]  # Top 20 trending

        except Exception as e:
logger.error(f"Failed to get trending patterns: {e}")
            return []

    def analyze_failure_patterns(
        self,
        policy_key: Optional[str] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Analyze failure patterns for meta-learning insights.

        Args:
            policy_key: Filter by specific policy
            days: Time window to analyze

        Returns:
            Analysis results
        """
        try:
            # Build filter for failed patterns
            filters = {
                "failure_count": {"gt": 0},
                "last_validated": {
                    "gte": (datetime.utcnow() - timedelta(days=days)).isoformat()
                }
            }

            if policy_key:
                filters["policy_key"] = policy_key

            # Get all failed patterns
            import random
            random_vector = [random.random() for _ in range(self.vector_dim)]

            results = self.search(
                query_vector=random_vector,
                limit=500,
                score_threshold=0.0,
                filters=filters
            )

            # Analyze patterns
            analysis = {
                "total_failed": len(results),
                "by_policy": {},
                "by_project": {},
                "high_risk": []
            }

            for result in results:
                payload = result["payload"]

                # Group by policy
                policy = payload.get("policy_key", "unknown")
                if policy not in analysis["by_policy"]:
                    analysis["by_policy"][policy] = 0
                analysis["by_policy"][policy] += 1

                # Group by project
                project = payload.get("project_tag", "default")
                if project not in analysis["by_project"]:
                    analysis["by_project"][project] = 0
                analysis["by_project"][project] += 1

                # High risk patterns
                if payload.get("failure_count", 0) > 5:
                    analysis["high_risk"].append({
                        "id": result["id"],
                        "policy_key": policy,
                        "failure_count": payload.get("failure_count", 0),
                        "meta_prompt": payload.get("meta_prompt")
                    })

            return analysis

        except Exception as e:
logger.error(f"Failed to analyze failure patterns: {e}")
            return {"error": str(e)}

    def get_stats(self) -> Dict[str, Any]:
        """Get L2 cache statistics."""
        try:
            info = self.client.get_collection(self.index_name)

            return {
                "total_points": info.points_count,
                "vector_size": info.config.params.vectors.size,
                "distance_metric": info.config.params.vectors.distance.value,
                "status": info.status.value
            }

        except Exception as e:
logger.error(f"Failed to get Qdrant stats: {e}")
            return {"error": str(e)}
