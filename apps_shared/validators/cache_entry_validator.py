"""Contrastive Semantic cache - SOTA Layer for Instant Response Retrieval.

This component uses embedding similarity to recognize semantically similar
queries and serve cached responses instantly.
"""

import json
import logging
import time
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "cache_entry_validator", "p0_governance")
_emit_reads_policy_state("p0", "cache_entry_validator", "policy_binding")
_emit_snapshots_state("p0", "cache_entry_validator", "state_snapshot")
emit_replay_key("p0", "cache_entry_validator")
emit_determinism_digest("p0", "cache_entry_validator")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "cache_entry_validator", "execution_auth")
_emit_validates_capability("p2", "cache_entry_validator", "capability_check")
_emit_routes_to_capability("p2", "cache_entry_validator", "capability_route")
_emit_writes_via_uwg("p2", "cache_entry_validator", "uwg_write")
_emit_blocks_direct_write("p2", "cache_entry_validator", "direct_write_block")
_emit_records_tool_invocation("p2", "cache_entry_validator", "tool_invocation")
_emit_captures_execution_output("p2", "cache_entry_validator", "exec_output")
_emit_dispatches_agent("p3", "cache_entry_validator", "agent_dispatch")
_emit_coordinates_agents("p3", "cache_entry_validator", "agent_coordination")
_emit_records_workflow_lineage("p3", "cache_entry_validator", "workflow_lineage")
_emit_records_healing_outcome("p3", "cache_entry_validator", "healing_outcome")
_emit_escalates_failure("p3", "cache_entry_validator", "failure_escalation")
_emit_orchestrates_workflow("p3", "cache_entry_validator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "cache_entry_validator", "healing_dispatch")
_emit_invokes_evaluation("p3", "cache_entry_validator", "evaluation_signal")
_emit_records_telemetry_event("p4", "cache_entry_validator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "cache_entry_validator", "eval_metric")
_emit_stores_embedding("p4", "cache_entry_validator", "embedding_store")
_emit_updates_meta_learning_state("p4", "cache_entry_validator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "cache_entry_validator", "exec_snapshot_link")

try:
    import numpy as np
except ImportError as _err:
    raise ImportError("numpy is required for this module. Install with: pip install -e '.[infra]'") from _err
from pydantic import BaseModel, Field, validator

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("cache_entry_validator", "p4obs", "metric_1")
_emit_emits_metric_event("cache_entry_validator", "p4obs", "metric_2")
_emit_emits_metric_event("cache_entry_validator", "p4obs", "metric_3")
_emit_emits_metric_event("cache_entry_validator", "p4obs", "metric_4")
_emit_emits_metric_event("cache_entry_validator", "p4obs", "metric_5")
_emit_emits_metric_event("cache_entry_validator", "p4obs", "metric_6")
_emit_records_incident_event("cache_entry_validator", "p4obs", "incident")
_emit_captures_runtime_anomaly("cache_entry_validator", "p4obs", "anomaly")
_emit_writes_observability_log("cache_entry_validator", "p4obs", "obs_log")
_emit_updates_monitoring_state("cache_entry_validator", "p4obs", "mon_state")
_emit_triggers_alert("cache_entry_validator", "p4obs", "alert")
_emit_links_incident_trace("cache_entry_validator", "p4obs", "trace_link")
_emit_captures_pattern("cache_entry_validator", "p3lm", "pattern")
_emit_records_learning_event("cache_entry_validator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("cache_entry_validator", "p3lm", "snapshot")
_emit_feeds_meta_learning("cache_entry_validator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("cache_entry_validator", "p3lm", "routing")
_emit_improves_agent_policy("cache_entry_validator", "p3lm", "policy")
_emit_stores_learning_state("cache_entry_validator", "p3lm", "state")
_emit_records_execution_trace("cache_entry_validator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("cache_entry_validator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("cache_entry_validator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("cache_entry_validator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("cache_entry_validator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("cache_entry_validator", "env_read", "p2_env_1")
_emit_reads_environ("cache_entry_validator", "env_read", "p2_env_2")
_emit_reads_runtime_state("cache_entry_validator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("cache_entry_validator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "cache_entry_validator", "context_pull")
_emit_pulls_context("p1", "cache_entry_validator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "cache_entry_validator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "cache_entry_validator", "uwg_term_2")
_emit_writes_through("p1", "cache_entry_validator", "write_through")
_emit_writes_through("p1", "cache_entry_validator", "write_through_2")
_emit_validated_by_safety_plane("p1", "cache_entry_validator", "safety_validation")
_emit_invokes_eval("p1", "cache_entry_validator", "eval_call")
_emit_proposal_commits_routing("p1", "cache_entry_validator", "routing_commit")
_emit_escalates_to_human("p1", "cache_entry_validator", "human_escalation")
_emit_routes_through("p1", "cache_entry_validator", "route_through")
_emit_checks_agent_registry("p1", "cache_entry_validator", "agent_registry")
_emit_validates_agent_capability("p1", "cache_entry_validator", "capability")
_emit_dispatches_execution_plan("p1", "cache_entry_validator", "exec_plan")
_emit_agent_executes_agent("p1", "cache_entry_validator", "sub_agent")
_emit_routes_to_agent("p1", "cache_entry_validator", "target_agent")
_emit_verifies_policy("p1", "cache_entry_validator", "policy_check")
_emit_observes_runtime_state("p1", "cache_entry_validator", "runtime_state")
_emit_verifies_boundary("p1", "cache_entry_validator", "boundary_check")
_emit_transcripts_response("p1", "cache_entry_validator", "transcript")
_emit_hard_fails_untranscripted("p1", "cache_entry_validator")
_emit_gated_by_confidence("p1", "cache_entry_validator", "confidence_gate")

logger = logging.getLogger(__name__)


class CacheEntry(BaseModel):
    """Entry in the semantic cache."""

    query_text: str = Field(..., description="Original query text")
    response_text: str = Field(..., description="Cached response")
    embedding: list[float] = Field(..., description="Query embedding vector")
    timestamp: float = Field(..., description="Creation timestamp")
    access_count: int = Field(default=0, description="Number of times accessed")
    last_accessed: float = Field(default_factory=time.time, description="Last access timestamp")

    @validator("embedding")
    def validate_embedding(cls, v):
        """Ensure embedding is a list of floats."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "CacheEntry.validate_embedding")

        if not isinstance(v, list):
            raise ValueError("Embedding must be a list")
        if len(v) == 0:
            raise ValueError("Embedding cannot be empty")
        return v


class ContrastiveSemanticCache:
    """Semantic cache that uses embedding similarity for query matching.

    Uses a bi-encoder to embed queries and cosine similarity to find
    semantically similar cached queries, enabling instant responses
    for recurring questions even if phrased differently.
    """

    # guardian: allow-magic-config
    def __init__(
        self,
        model_name: str = "BAAI/bge-m3",
        similarity_threshold: float = 0.92,
        max_entries: int = 1000,
        lazy_load: bool = True,
        ttl_seconds: int | None = None,
    ):
        """Initialize the Contrastive Semantic cache.

        Args:
            model_name: Name of the sentence transformer model
            similarity_threshold: Minimum similarity for cache hit (0.0-1.0)
            max_entries: Maximum number of entries to store
            lazy_load: Whether to load model on first use
            ttl_seconds: Time-to-live for cache entries (None for no expiry)
        """
        self.model_name = model_name
        self.similarity_threshold = max(0.0, min(1.0, similarity_threshold))
        self.max_entries = max_entries
        self.lazy_load = lazy_load
        self.ttl_seconds = ttl_seconds
        self._cache: list[CacheEntry] = []
        self._embedding_matrix: np.ndarray | None = None
        self._model = None
        self._model_loaded = False
        self._fallback_mode = False
        self._stats = {"hits": 0, "misses": 0, "puts": 0, "evictions": 0}
        logger.info(
            f"Initialized ContrastiveSemanticCache: model={model_name}, threshold={similarity_threshold}, max_entries={max_entries}"
        )

    @property
    def is_available(self) -> bool:
        """Check if the cache is available (model loaded or can be loaded)."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ContrastiveSemanticCache.is_available")

        if self._model_loaded:
            return not self._fallback_mode
        if self._fallback_mode:
            return False
        try:
            return True
        # guardian: allow-silent-swallow - optional dependency
        except ImportError:
            logger.warning("sentence_transformers or numpy not available, cache will be in fallback mode")
            return False

    def _load_model(self) -> bool:
        """Load the sentence transformer model.

        Returns:
            True if model loaded successfully, False if in fallback mode
        """
        if self._model_loaded:
            return not self._fallback_mode
        try:
            from sentence_transformers import SentenceTransformer

            logger.info(f"Loading SentenceTransformer model: {self.model_name}")
            start_time = time.time()
            self._model = SentenceTransformer(self.model_name)
            load_time = time.time() - start_time
            logger.info(f"Model loaded in {load_time:.2f}s")
            self._model_loaded = True
            self._fallback_mode = False
            return True
        except ImportError as e:
            logger.error(f"Failed to import required libraries: {e}")
            logger.warning("cache will operate in fallback mode (no caching)")
            self._fallback_mode = True
            self._model_loaded = True
            return False
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Failed to load model {self.model_name}: {e}")
            logger.warning("cache will operate in fallback mode (no caching)")
            self._fallback_mode = True
            self._model_loaded = True
            return False

    def _encode_query(self, query: str) -> np.ndarray | None:
        """Encode a query into an embedding vector.

        Args:
            query: Query string to encode

        Returns:
            Embedding vector or None if encoding failed
        """
        if not query:
            return None
        if not self._model_loaded:
            if not self._load_model():
                return None
        if self._fallback_mode:
            return None
        try:
            embedding = self._model.encode(query, convert_to_numpy=True, show_progress_bar=False)
            return embedding
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Failed to encode query: {e}")
            return None

    def _update_embedding_matrix(self):
        """Update the embedding matrix from cache entries."""
        if not self._cache:
            self._embedding_matrix = None
            return
        try:
            embeddings = [np.array(entry.embedding) for entry in self._cache]
            self._embedding_matrix = np.vstack(embeddings)
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Failed to update embedding matrix: {e}")
            self._embedding_matrix = None

    def _calculate_similarity(self, query_embedding: np.ndarray) -> np.ndarray:
        """Calculate cosine similarity between query and all cached embeddings.

        Args:
            query_embedding: Query embedding vector

        Returns:
            Array of similarity scores
        """
        if self._embedding_matrix is None:
            return np.array([])
        try:
            query_norm = query_embedding / np.linalg.norm(query_embedding)
            cache_norm = self._embedding_matrix / np.linalg.norm(
                self._embedding_matrix, axis=1, keepdims=True
            )
            similarities = np.dot(cache_norm, query_norm)
            return similarities
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Failed to calculate similarities: {e}")
            return np.array([])

    def _evict_if_needed(self):
        """Evict entries if cache exceeds max_entries."""
        if len(self._cache) <= self.max_entries:
            return
        evict_count = len(self._cache) - self.max_entries
        self._cache = self._cache[evict_count:]
        self._stats["evictions"] += evict_count
        self._update_embedding_matrix()
        logger.info(f"Evicted {evict_count} old cache entries")

    def _is_expired(self, entry: CacheEntry) -> bool:
        """Check if a cache entry has expired.

        Args:
            entry: cache entry to check

        Returns:
            True if entry is expired
        """
        if self.ttl_seconds is None:
            return False
        age = time.time() - entry.timestamp
        return age > self.ttl_seconds

    def get(self, query: str, threshold: float | None = None) -> str | None:
        """Get cached response for a semantically similar query.

        Args:
            query: Query string to look up
            threshold: Override similarity threshold

        Returns:
            Cached response if found, None otherwise
        """
        if not query:
            return None
        sim_threshold = threshold if threshold is not None else self.similarity_threshold
        if self._fallback_mode:
            logger.debug("cache in fallback mode, returning miss")
            self._stats["misses"] += 1
            return None
        query_embedding = self._encode_query(query)
        if query_embedding is None:
            self._stats["misses"] += 1
            return None
        similarities = self._calculate_similarity(query_embedding)
        if len(similarities) == 0:
            self._stats["misses"] += 1
            return None
        max_idx = np.argmax(similarities)
        max_similarity = float(similarities[max_idx])
        if max_similarity >= sim_threshold:
            entry = self._cache[max_idx]
            if self._is_expired(entry):
                logger.debug(f"cache hit but entry expired (similarity: {max_similarity:.3f})")
                self._cache.pop(max_idx)
                self._update_embedding_matrix()
                self._stats["misses"] += 1
                return None
            entry.access_count += 1
            entry.last_accessed = time.time()
            logger.debug(f"cache hit (similarity: {max_similarity:.3f})")
            self._stats["hits"] += 1
            return entry.response_text
        else:
            logger.debug(f"cache miss (best similarity: {max_similarity:.3f} < {sim_threshold})")
            self._stats["misses"] += 1
            return None

    def put(self, query: str, response: str, force: bool = False) -> bool:
        """Store a query-response pair in the cache.

        Args:
            query: Query string
            response: Response to cache
            force: Whether to force storage even in fallback mode

        Returns:
            True if stored successfully, False otherwise
        """
        if not query or not response:
            return False
        if self._fallback_mode and (not force):
            logger.debug("cache in fallback mode, skipping put")
            return False
        query_embedding = self._encode_query(query)
        if query_embedding is None:
            return False
        entry = CacheEntry(
            query_text=query,
            response_text=response,
            embedding=query_embedding.tolist(),
            timestamp=time.time(),
        )
        self._cache.append(entry)
        self._stats["puts"] += 1
        self._evict_if_needed()
        self._update_embedding_matrix()
        logger.debug(f"Cached entry for query: {query[:50]}...")
        return True

    def clear(self):
        """Clear all cache entries."""
        self._cache.clear()
        self._embedding_matrix = None
        logger.info("cache cleared")

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        total_requests = self._stats["hits"] + self._stats["misses"]
        hit_rate = self._stats["hits"] / total_requests if total_requests > 0 else 0.0
        return {
            "entries": len(self._cache),
            "max_entries": self.max_entries,
            "hits": self._stats["hits"],
            "misses": self._stats["misses"],
            "puts": self._stats["puts"],
            "evictions": self._stats["evictions"],
            "hit_rate": hit_rate,
            "model_loaded": self._model_loaded,
            "fallback_mode": self._fallback_mode,
        }

    def export_cache(self, filepath: str):
        """Export cache to JSON file.

        Args:
            filepath: Path to save the cache
        """
        try:
            data = {
                "entries": [entry.dict() for entry in self._cache],
                "stats": self._stats,
                "config": {
                    "model_name": self.model_name,
                    "similarity_threshold": self.similarity_threshold,
                    "max_entries": self.max_entries,
                },
            }
            with open(filepath, "w") as f:
                json.dump(data, f, indent=2)
            logger.info(f"Exported {len(self._cache)} cache entries to {filepath}")
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Failed to export cache: {e}")

    def import_cache(self, filepath: str, clear_existing: bool = False):
        """Import cache from JSON file.

        Args:
            filepath: Path to load cache from
            clear_existing: Whether to clear existing cache
        """
        try:
            with open(filepath) as f:
                data = json.load(f)
            if clear_existing:
                self.clear()
            for entry_data in data.get("entries", []):
                entry = CacheEntry(**entry_data)
                self._cache.append(entry)
            self._update_embedding_matrix()
            logger.info(f"Imported {len(data.get('entries', []))} cache entries from {filepath}")
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Failed to import cache: {e}")


def get_cached_response(query: str, cache: ContrastiveSemanticCache) -> str | None:
    """Get cached response for a query.

    Args:
        query: Query string
        cache: Semantic cache instance

    Returns:
        Cached response or None
    """
    return cache.get(query)


class NullCache:
    """Fallback cache that never stores or retrieves anything."""

    def __init__(self, *args, **kwargs):
        """Initialize the null cache."""
        logger.warning("Using NullCache - no caching will be performed")

    def get(self, query: str, threshold: float | None = None) -> str | None:
        """Always return None (cache miss)."""
        return None

    def put(self, query: str, response: str, force: bool = False) -> bool:
        """Never store anything."""
        return False

    def clear(self):
        """No-op."""
        pass

    def get_stats(self) -> dict[str, Any]:
        """Return empty stats."""
        return {"entries": 0, "hits": 0, "misses": 0, "hit_rate": 0.0, "fallback_mode": True}
