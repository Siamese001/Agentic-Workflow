"""
Semantic Gatekeeper - L5 Safety Protocol Enforcement

The Semantic Gatekeeper acts as the "Brain" for agents, storing and retrieving
patterns from a hybrid semantic cache. It prevents dangerous operations by
consulting historical patterns and their failure rates.

This implements the L5 Safety Protocol by:
1. Embedding planned actions
2. Querying Redis for similar past actions
3. Blocking actions with high failure rates or risk scores
"""

import asyncio
import hashlib
import logging
import time
from collections import deque
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from core.etl_pipeline import ContinuousIngester
from core.llm_judger import get_judger
from core.qdrant_cache import QdrantCache
from redisvl.index import SearchIndex
from redisvl.query import VectorQuery
from redisvl.redis.connection import RedisConnection
from sentence_transformers import SentenceTransformer

from schemas.canon_models import CanonEntry, CanonSearchResult

logger = logging.getLogger(__name__)


class SemanticGatekeeper:
    """
    Hybrid Semantic Gatekeeper with L1 (Redis) and L2 (Pinecone) Caches.

    Implements meta-learning by:
    - L1 Cache (Redis): Fast working memory for recent patterns
    - L2 Cache (Pinecone): Long-term memory for historical patterns
    - Promotion/demotion based on success/failure patterns
    """

    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        qdrant_host: str = "localhost",
        qdrant_port: int = 6333,
        model_name: str = "all-MiniLM-L6-v2",
        redis_index_name: str = "canon_l1",
        qdrant_index_name: str = "canon-l2",
        vector_dim: int = 768,
        redis_max_size: int = 10000,
        promotion_threshold: int = 3  # Promote to L2 after N successes
    ):
        """Initialize the Hybrid Semantic Gatekeeper."""
        # Configuration
        self.redis_url = redis_url
        self.qdrant_host = qdrant_host
        self.qdrant_port = qdrant_port
        self.redis_index_name = redis_index_name
        self.qdrant_index_name = qdrant_index_name
        self.vector_dim = vector_dim
        self.redis_max_size = redis_max_size
        self.promotion_threshold = promotion_threshold

        # Initialize sentence transformer for embeddings
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)

        # Initialize L1 Cache (Redis)
        self.redis = RedisConnection(redis_url)
        self._setup_redis_index()

        # Initialize L2 Cache (Qdrant)
        self.qdrant = None
        self._setup_qdrant()

        # Promotion queue for async writes to Qdrant
        self._promotion_queue = asyncio.Queue()
        self._promotion_task = None

        # Continuous ingester for real-time L2 updates (initialized after qdrant)
        self.continuous_ingester = None
        if self.qdrant:
            self.continuous_ingester = ContinuousIngester(
                self,
                self.qdrant,
                failure_retention_days=90
            )

        # Latency tracking for performance monitoring
        self._latency_history = deque(maxlen=1000)  # Track last 1000 queries
        self._latency_threshold_ms = 10  # 10ms target

        logger.info("Hybrid SemanticGatekeeper initialized successfully")
        logger.info(f"  L1 Cache (Redis): {redis_url}")
        logger.info(
            f"  L2 Cache (Qdrant): {qdrant_host}:{qdrant_port}/{qdrant_index_name if self.qdrant else 'DISABLED'}")
        logger.info(
            f"  Latency Target: <{self._latency_threshold_ms}ms for 90% of queries")

    def _setup_redis_index(self):
        """Create or load the Redis search index for L1 cache."""
        index_schema = {
            "index": {
                "name": self.redis_index_name,
                "prefix": "canon_l1:",
                "storage_type": "hash"
            },
            "fields": [
                {"name": "vector", "type": "vector",
                 "attrs": {"dims": self.vector_dim, "distance_metric": "cosine", "algorithm": "flat"}},
                {"name": "ast_hash", "type": "tag"},
                {"name": "risk_score", "type": "numeric"},
                {"name": "failure_count", "type": "numeric"},
                {"name": "success_count", "type": "numeric"},
                {"name": "max_files_touched", "type": "numeric"},
                {"name": "validation_status", "type": "tag"},
                {"name": "pattern_type", "type": "tag"},
                {"name": "agent_name", "type": "tag"},
                {"name": "created_at", "type": "numeric"},
                {"name": "last_seen", "type": "numeric"},
                # Track if promoted to Pinecone
                {"name": "promoted_to_l2", "type": "tag"}
            ]
        }

        try:
            self.redis_index = SearchIndex.from_dict(index_schema)
            self.redis_index.set_client(self.redis.client)

            # Create index if it doesn't exist
            if not self.redis_index.exists():
                self.redis_index.create()
                logger.info(f"Created new L1 index: {self.redis_index_name}")
            else:
                logger.info(
                    f"Loaded existing L1 index: {self.redis_index_name}")

        except Exception as e:
logger.error(f"Failed to setup Redis L1 index: {e}")
            raise

    def _setup_qdrant(self):
        """Initialize Qdrant connection for L2 cache."""
        try:
            # Initialize Qdrant cache
            self.qdrant = QdrantCache(
                host=self.qdrant_host,
                port=self.qdrant_port,
                index_name=self.qdrant_index_name,
                vector_dim=self.vector_dim
            )

            logger.info(
                f"Connected to Qdrant L2 cache: {self.qdrant_host}:{self.qdrant_port}")

            # Start async promotion task
            self._promotion_task = asyncio.create_task(
                self._promotion_worker())

        except Exception as e:
logger.error(f"Failed to setup Qdrant L2 cache: {e}")
            self.qdrant = None

    def embed_action(self, action: str) -> List[float]:
        """
        Convert a planned action description into a vector embedding.

        Args:
            action: Text description of the planned action

        Returns:
            768-dimensional vector embedding
        """
        embedding = self.model.encode(action, convert_to_numpy=True)
        return embedding.tolist()

    def calculate_ast_hash(self, code: str) -> str:
        """
        Calculate SHA-256 hash of AST structure to detect syntax drift.

        Args:
            code: Python code to analyze

        Returns:
            SHA-256 hash string
        """
        import ast

        try:
            # Parse AST and normalize
            tree = ast.parse(code)

            # Convert to normalized string representation
            ast_str = ast.dump(tree, sort_keys=True)

            # Calculate hash
            return hashlib.sha256(ast_str.encode()).hexdigest()

        except SyntaxError as e:
# For invalid code, hash the error and code
            combined = f"SYNTAX_ERROR:{e}:{code}"
            return hashlib.sha256(combined.encode()).hexdigest()

    def consult_canon(
        self,
        planned_action: str,
        code: Optional[str] = None,
        policy_key: Optional[str] = None,
        context: Optional[str] = None
    ) -> Tuple[bool, Optional[CanonEntry]]:
        """
        Consult the hybrid canon with LLM-based semantic validation.

        Implements the full L5 retrieval pipeline:
        1. L1 Cache Check (Redis) - 24-hour window + Canon Keys
        2. L2 Cache Check (Qdrant) - Historical patterns
        3. LLM Judgement - Semantic equivalence validation

        Args:
            planned_action: Description of the planned action
            code: Optional code snippet to analyze
            policy_key: The specific Canon rule being evaluated
            context: Additional context for validation

        Returns:
            Tuple of (is_safe, best_matching_pattern)
        """
        # Track latency for performance monitoring
        start_time = time.perf_counter()

        logger.info(f"Consulting hybrid canon for action: {planned_action}")

        # Generate AST for new code
        new_ast = None
        if code:
            try:
                tree = ast.parse(code)
                new_ast = ast.dump(tree, include_attributes=True)
            except SyntaxError as e:
logger.error(f"Failed to parse code: {e}")
                return False, None

        # Embed the planned action
        query_vector = self.embed_action(planned_action)

        # Initialize LLM Judger
        judger = get_judger()

        # L1 Cache Check (Redis) - Fast path with 24-hour filter
        l1_result = self._search_l1_cache(
            query_vector,
            threshold=0.95,  # Tight threshold for L1
            max_results=5,
            time_window_hours=24
        )

        if l1_result.entries:
            logger.info(f"Found {l1_result.total_found} patterns in L1 cache")

            # Use LLM Judger for semantic validation
            best_match, judgement = judger.judge_pattern_equivalence(
                l1_result.entries,
                code or "",
                new_ast,
                context
            )

            if judgement.is_equivalent and best_match:
                logger.info(
                    f"LLM validated pattern {best_match.id} as equivalent (confidence: {judgement.confidence})")

                # Check safety
                if best_match.is_safe_to_execute():
                    logger.info(
                        "Action approved by L1 cache with LLM validation")
                    latency_ms = int((time.perf_counter() - start_time) * 1000)
                    self._track_latency(latency_ms)
                    return True, best_match
                else:
                    logger.warning(
                        f"BLOCKING action - L1 pattern {best_match.id} marked as unsafe")
                    latency_ms = int((time.perf_counter() - start_time) * 1000)
                    self._track_latency(latency_ms)
                    return False, best_match
            else:
                logger.info(
                    f"LLM judged no equivalent patterns in L1 (confidence: {judgement.confidence})")

        # L2 Cache Check (Qdrant) - Deep dive
        if self.qdrant:
            logger.info("No matches in L1, checking L2 cache...")
            l2_result = self._search_l2_cache(
                query_vector,
                threshold=0.7,  # Looser threshold for L2
                top_k=20
            )

            if l2_result:
                logger.info(f"Found {len(l2_result)} patterns in L2 cache")

                # Convert L2 results to CanonEntry objects for judgement
                l2_entries = []
                for match in l2_result:
                    payload = match.get('payload', {})
                    entry = CanonEntry(
                        id=match['id'],
                        vector=query_vector,
                        ast_json=payload.get('ast_json', {}),
                        ast_hash=payload.get('ast_hash', ''),
                        policy_key=payload.get('policy_key', ''),
                        failure_count=payload.get('failure_count', 0),
                        success_count=payload.get('success_count', 0),
                        latency_ms=payload.get('latency_ms', 0),
                        project_tag=payload.get('project_tag', 'default'),
                        metadata=payload
                    )
                    l2_entries.append(entry)

                # Use LLM Judger for semantic validation
                best_match, judgement = judger.judge_pattern_equivalence(
                    l2_entries,
                    code or "",
                    new_ast,
                    context
                )

                if judgement.is_equivalent and best_match:
                    logger.info(
                        f"LLM validated L2 pattern {best_match.id} as equivalent")

                    # Check safety
                    if best_match.is_safe_to_execute():
                        logger.info(
                            "Action approved by L2 cache with LLM validation - promoting to L1")
                        # Promote to L1
                        self._promote_to_l1(best_match, query_vector)
                        latency_ms = int(
                            (time.perf_counter() - start_time) * 1000)
                        self._track_latency(latency_ms)
                        return True, best_match
                    else:
                        logger.warning(
                            f"BLOCKING action - L2 pattern {best_match.id} marked as unsafe")
                        latency_ms = int(
                            (time.perf_counter() - start_time) * 1000)
                        self._track_latency(latency_ms)
                        return False, best_match
                else:
                    logger.info(f"LLM judged no equivalent patterns in L2")

        # No patterns found - allow with caution
        logger.info(
            "No equivalent patterns found in L1 or L2 - allowing action with caution")

        # Track latency before returning
        latency_ms = int((time.perf_counter() - start_time) * 1000)
        self._track_latency(latency_ms)

        return True, None

    def _search_l1_cache(
        self,
        query_vector: List[float],
        threshold: float = 0.8,
        max_results: int = 10,
        time_window_hours: int = 24,
        include_canon_keys: bool = True
    ) -> CanonSearchResult:
        """Search L1 cache (Redis) for similar patterns with time filtering."""
        start_time = time.time()

        # Build filter for time window and Canon Keys
        cutoff_timestamp = int(
            (datetime.utcnow() - timedelta(hours=time_window_hours)).timestamp())

        # Create filter expression
        filter_parts = []

        # Include recent patterns (last 24 hours)
        filter_parts.append(f"@last_seen:[{cutoff_timestamp} inf]")

        # Always include Canon Keys (golden patterns)
        if include_canon_keys:
            filter_parts.append("@is_canon_key:{true}")

        # Combine with OR
        filter_expression = "(" + " | ".join(filter_parts) + ")"

        # Create vector query for Redis with filter
        query = VectorQuery(
            vector=query_vector,
            vector_field_name="vector",
            return_fields=[
                "id", "ast_hash", "ast_json", "policy_key", "risk_score",
                "failure_count", "success_count", "max_files_touched",
                "validation_status", "pattern_type", "agent_name",
                "created_at", "last_seen", "promoted_to_l2", "latency_ms",
                "project_tag", "is_canon_key"
            ],
            num_results=max_results,
            distance_threshold=1 - threshold,
            filter_expression=filter_expression
        )

        # Execute search in Redis
        results = self.redis_index.query(query)

        # Parse results
        entries = []
        safe_count = 0
        blocked_count = 0

        for result in results:
            metadata = {
                "risk_score": int(result.get("risk_score", 0)),
                "failure_count": int(result.get("failure_count", 0)),
                "success_count": int(result.get("success_count", 0)),
                "max_files_touched": int(result.get("max_files_touched", 0)),
                "validation_status": result.get("validation_status", "pending"),
                "pattern_type": result.get("pattern_type", "unknown"),
                "agent_name": result.get("agent_name", "unknown"),
                "created_at": result.get("created_at", ""),
                "last_seen": result.get("last_seen", "")
            }

            entry = CanonEntry(
                id=result.get("id", ""),
                vector=query_vector,
                ast_hash=result.get("ast_hash", ""),
                metadata=metadata
            )

            entries.append(entry)

            if entry.is_safe_to_execute():
                safe_count += 1
            else:
                blocked_count += 1

        query_time = (time.time() - start_time) * 1000

        return CanonSearchResult(
            entries=entries,
            total_found=len(entries),
            query_time_ms=query_time,
            safe_count=safe_count,
            blocked_count=blocked_count
        )

    def _search_l2_cache(
        self,
        query_vector: List[float],
        threshold: float = 0.7,
        top_k: int = 20,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict]:
        """Search L2 cache (Qdrant) for historical patterns."""
        if not self.qdrant:
            return []

        try:
            # Query Qdrant with hybrid search
            results = self.qdrant.search(
                query_vector=query_vector,
                limit=top_k,
                score_threshold=threshold,
                filters=filters,
                with_payload=True
            )

            return results

        except Exception as e:
logger.error(f"Failed to search L2 cache: {e}")
            return []

    def _promote_to_l1(self, l2_match: CanonEntry, query_vector: List[float]):
        """Promote a pattern from L2 to L1 cache."""
        try:
            # Update metadata for L1
            l2_match.metadata['last_seen'] = datetime.utcnow().isoformat()
            l2_match.metadata['promoted_to_l2'] = 'true'

            # Store in L1 (Redis)
            self._store_l1_entry(l2_match)
            logger.info(f"Promoted pattern {l2_match.id} from L2 to L1")

        except Exception as e:
logger.error(f"Failed to promote to L1: {e}")

    def record_pattern(
        self,
        action: str,
        code: str,
        policy_key: str,
        agent_name: str,
        pattern_type: str,
        files_touched: int,
        latency_ms: int = 0,
        success: bool = True,
        project_tag: str = "default",
        meta_prompt: Optional[str] = None,
        error_trace: Optional[str] = None
    ) -> str:
        """
        Record a pattern execution in the hybrid canon for meta-learning.

        Stores in L1 (Redis) immediately, queues for L2 (Qdrant) if successful.

        Args:
            action: Description of the action performed
            code: Code that was executed
            policy_key: The specific Canon rule key triggered
            agent_name: Name of the agent that performed the action
            pattern_type: Type of pattern (e.g., "refactor", "format", "analyze")
            files_touched: Number of files modified
            latency_ms: Time taken to resolve the issue
            success: Whether the execution was successful
            project_tag: Project identifier for cross-project knowledge transfer
            meta_prompt: Refined instruction set from failed runs

        Returns:
            ID of the created/updated entry
        """
        # Generate embedding and AST
        vector = self.embed_action(action)

        # Parse AST
        try:
            tree = ast.parse(code)
            ast_json = ast.dump(tree, include_attributes=True)
            ast_hash = hashlib.sha256(ast_json.encode()).hexdigest()
        except SyntaxError as e:
logger.error(f"Failed to parse code for AST: {e}")
            ast_json = {"error": str(e)}
            ast_hash = hashlib.sha256(f"SYNTAX_ERROR:{e}".encode()).hexdigest()

        # Check L1 cache for existing pattern
        existing = self._search_l1_cache(vector, threshold=0.95, max_results=1)

        if existing.entries:
            # Update existing pattern in L1
            entry = existing.entries[0]
            logger.info(f"Updating existing L1 pattern: {entry.id}")

            if success:
                entry.update_success(files_touched, latency_ms)

                # Check if should be promoted to L2
                if entry.success_count >= self.promotion_threshold:
                    if not entry.metadata.get('promoted_to_l2'):
                        self._queue_for_promotion(entry)
            else:
                entry.update_failure(meta_prompt)

            # Update in L1
            self._update_l1_entry(entry)
            return str(entry.id)
        else:
            # Create new pattern
            entry = CanonEntry(
                vector=vector,
                ast_json=ast_json,
                ast_hash=ast_hash,
                policy_key=policy_key,
                failure_count=0 if success else 1,
                success_count=1 if success else 0,
                latency_ms=latency_ms,
                project_tag=project_tag,
                metadata={
                    "risk_score": 0,
                    "max_files_touched": files_touched,
                    "pattern_type": pattern_type,
                    "agent_name": agent_name,
                    "validation_status": "validated" if success else "failed",
                    "is_canon_key": False,  # Canon Keys are loaded separately
                    "meta_prompt": meta_prompt,
                    "promoted_to_l2": "false"
                }
            )

            # Store in L1 immediately
            self._store_l1_entry(entry)
            logger.info(f"Created new L1 pattern: {entry.id}")

            # Ingest to L2 using ContinuousIngester
            if self.continuous_ingester and self.qdrant:
                if success:
                    asyncio.create_task(
                        self.continuous_ingester.ingest_success(entry))
                else:
                    # Ingest failure with error trace
                    error_msg = error_trace or meta_prompt or "Unknown error"
                    asyncio.create_task(
                        self.continuous_ingester.ingest_failure(entry, error_msg))

            return str(entry.id)

    def _store_l1_entry(self, entry: CanonEntry):
        """Store a canon entry in L1 cache (Redis)."""
        key = f"canon_l1:{entry.id}"

        # Prepare data for storage
        data = {
            "vector": np.array(entry.vector).astype(np.float32).tobytes(),
            "ast_hash": entry.ast_hash,
            "risk_score": entry.metadata.get("risk_score", 0),
            "failure_count": entry.metadata.get("failure_count", 0),
            "success_count": entry.metadata.get("success_count", 0),
            "max_files_touched": entry.metadata.get("max_files_touched", 0),
            "validation_status": entry.metadata.get("validation_status", "pending"),
            "pattern_type": entry.metadata.get("pattern_type", "unknown"),
            "agent_name": entry.metadata.get("agent_name", "unknown"),
            "created_at": entry.metadata.get("created_at", ""),
            "last_seen": entry.metadata.get("last_seen", ""),
            "promoted_to_l2": entry.metadata.get("promoted_to_l2", "false"),
            "id": str(entry.id)
        }

        # Store in Redis
        self.redis.client.hset(key, mapping=data)

        # Check if we need to evict old entries
        self._evict_l1_if_needed()

    def _update_l1_entry(self, entry: CanonEntry):
        """Update an existing L1 cache entry."""
        key = f"canon_l1:{entry.id}"

        # Update metadata fields
        updates = {
            "risk_score": entry.metadata.get("risk_score", 0),
            "failure_count": entry.metadata.get("failure_count", 0),
            "success_count": entry.metadata.get("success_count", 0),
            "max_files_touched": entry.metadata.get("max_files_touched", 0),
            "validation_status": entry.metadata.get("validation_status", "pending"),
            "last_seen": entry.metadata.get("last_seen", ""),
            "promoted_to_l2": entry.metadata.get("promoted_to_l2", "false")
        }

        self.redis.client.hset(key, mapping=updates)

    def _queue_for_promotion(self, entry: CanonEntry):
        """Queue a pattern for promotion to L2 cache."""
        # Add to promotion queue
        asyncio.create_task(self._promotion_queue.put(entry))
        logger.info(f"Queued pattern {entry.id} for L2 promotion")

    async def _promotion_worker(self):
        """Async worker to promote patterns to L2 cache."""
        logger.info("L2 promotion worker started")

        while True:
            try:
                # Get entry from queue
                entry = await self._promotion_queue.get()

                # Upsert to Qdrant
                if self.qdrant:
                    await self._upsert_to_l2(entry)

                # Mark as promoted in L1
                self._mark_as_promoted(str(entry.id))

            except Exception as e:
logger.error(f"Error in L2 promotion worker: {e}")
                await asyncio.sleep(5)  # Brief pause on error

    async def _upsert_to_l2(self, entry: CanonEntry):
        """Upsert a pattern to L2 cache (Qdrant)."""
        try:
            # Upsert to Qdrant
            self.qdrant.upsert(entry)

            logger.info(f"Upserted pattern {entry.id} to L2")

        except Exception as e:
logger.error(f"Failed to upsert to L2: {e}")

    def _mark_as_promoted(self, entry_id: str):
        """Mark an L1 entry as promoted to L2."""
        key = f"canon_l1:{entry_id}"
        self.redis.client.hset(key, "promoted_to_l2", "true")

    def _evict_l1_if_needed(self):
        """Evict old entries from L1 cache if over capacity."""
        try:
            # Get current size
            size = self.redis.client.dbsize()

            if size > self.redis_max_size:
                # Find oldest entries by last_seen
                oldest = self.redis.client.ft(self.redis_index_name).search(
                    "*",
                    return_fields=["id", "last_seen"],
                    sortby="last_seen",
                    limit=size - self.redis_max_size + 100  # Evict extra for buffer
                )

                # Delete oldest entries
                for doc in oldest.docs:
                    key = f"canon_l1:{doc.id}"
                    self.redis.client.delete(key)

                logger.info(
                    f"Evicted {len(oldest.docs)} old entries from L1 cache")

        except Exception as e:
logger.error(f"Failed to evict from L1: {e}")

    def get_safety_stats(self) -> dict:
        """Get statistics about the hybrid canon safety status."""
        try:
            # L1 Cache (Redis) stats
            l1_total = len(self.redis.client.keys("canon_l1:*"))

            # Get L1 counts by validation status
            l1_validated = self.redis.client.ft(self.redis_index_name).search(
                "@validation_status:{validated}"
            ).total
            l1_failed = self.redis.client.ft(self.redis_index_name).search(
                "@validation_status:{failed}"
            ).total
            l1_blocked = self.redis.client.ft(self.redis_index_name).search(
                "@validation_status:{blocked}"
            ).total

            # L2 Cache (Pinecone) stats
            l2_stats = {"total": 0, "projects": set()}
            # Note: The original code had a self.pinecone check which is not defined in the class.
            # Assuming this was a placeholder or intended for a different cache type.
            # For now, we'll report L2 as disabled if self.qdrant is None.
            l2_enabled = self.qdrant is not None

            return {
                "l1_cache": {
                    "total_patterns": l1_total,
                    "validated": l1_validated,
                    "failed": l1_failed,
                    "blocked": l1_blocked,
                    "safety_ratio": l1_validated / l1_total if l1_total > 0 else 0,
                    "capacity": f"{l1_total}/{self.redis_max_size}"
                },
                "l2_cache": {
                    "total_patterns": l2_stats["total"],
                    "enabled": l2_enabled
                },
                "meta_learning": {
                    "promotion_threshold": self.promotion_threshold,
                    "promotion_queue_size": self._promotion_queue.qsize() if self._promotion_queue else 0
                }
            }
        except Exception as e:
logger.error(f"Failed to get safety stats: {e}")
            return {"error": str(e)}

    def _track_latency(self, latency_ms: int):
        """Track query latency for performance monitoring."""
        self._latency_history.append(latency_ms)

        # Log if latency exceeds threshold
        if latency_ms > self._latency_threshold_ms:
            logger.warning(
                f"Canon check latency exceeded threshold: {latency_ms}ms > {self._latency_threshold_ms}ms")

    def get_latency_stats(self) -> Dict[str, Any]:
        """
        Get latency statistics for performance monitoring.

        Returns:
            Dictionary with latency metrics
        """
        if not self._latency_history:
            return {
                "total_queries": 0,
                "avg_latency_ms": 0,
                "p95_latency_ms": 0,
                "p99_latency_ms": 0,
                "under_10ms_percent": 0,
                "threshold_met": False
            }

        sorted_latencies = sorted(self._latency_history)
        total_queries = len(sorted_latencies)
        avg_latency = sum(sorted_latencies) / total_queries

        # Calculate percentiles
        p95_idx = int(0.95 * total_queries)
        p99_idx = int(0.99 * total_queries)
        p95_latency = sorted_latencies[p95_idx]
        p99_latency = sorted_latencies[p99_idx]

        # Calculate percentage under 10ms
        under_10ms = sum(
            1 for latency in sorted_latencies if latency < self._latency_threshold_ms)
        under_10ms_percent = (under_10ms / total_queries) * 100

        return {
            "total_queries": total_queries,
            "avg_latency_ms": round(avg_latency, 2),
            "p95_latency_ms": p95_latency,
            "p99_latency_ms": p99_latency,
            "under_10ms_percent": round(under_10ms_percent, 2),
            "threshold_met": under_10ms_percent >= 90,  # 90% under 10ms requirement
            "latency_target_ms": self._latency_threshold_ms
        }

    def shutdown(self):
        """Gracefully shutdown the gatekeeper and cleanup resources."""
        logger.info("Shutting down Semantic Gatekeeper...")

        # Log final latency stats
        stats = self.get_latency_stats()
        logger.info(f"Final latency stats: {stats}")

        # Cancel promotion task
        if self._promotion_task:
            self._promotion_task.cancel()

        logger.info("Semantic Gatekeeper shutdown complete")


# Singleton instance for global access
_gatekeeper = None


def get_gatekeeper() -> SemanticGatekeeper:
    """Get the global SemanticGatekeeper instance."""
    global _gatekeeper
    if _gatekeeper is None:
        _gatekeeper = SemanticGatekeeper()
    return _gatekeeper
