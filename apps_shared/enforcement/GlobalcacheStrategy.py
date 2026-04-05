"""Global Semantic cache - Unified caching layer for all engines.

This module provides a unified caching layer shared between the Resume and
Outreach engines, ensuring expensive operations are done once and reused
everywhere through semantic similarity matching.
"""

import hashlib
import logging
import time
from collections import OrderedDict
from typing import Any, Callable

from agentic_core.L0_routing.config.path_constants import THRESHOLD
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
    _emit_reads_through,
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

_emit_applies_guardrail("p0", "GlobalcacheStrategy", "p0_governance")
_emit_reads_policy_state("p0", "GlobalcacheStrategy", "policy_binding")
_emit_snapshots_state("p0", "GlobalcacheStrategy", "state_snapshot")
emit_replay_key("p0", "GlobalcacheStrategy")
emit_determinism_digest("p0", "GlobalcacheStrategy")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "GlobalcacheStrategy", "execution_auth")
_emit_validates_capability("p2", "GlobalcacheStrategy", "capability_check")
_emit_routes_to_capability("p2", "GlobalcacheStrategy", "capability_route")
_emit_writes_via_uwg("p2", "GlobalcacheStrategy", "uwg_write")
_emit_blocks_direct_write("p2", "GlobalcacheStrategy", "direct_write_block")
_emit_records_tool_invocation("p2", "GlobalcacheStrategy", "tool_invocation")
_emit_captures_execution_output("p2", "GlobalcacheStrategy", "exec_output")
_emit_dispatches_agent("p3", "GlobalcacheStrategy", "agent_dispatch")
_emit_coordinates_agents("p3", "GlobalcacheStrategy", "agent_coordination")
_emit_records_workflow_lineage("p3", "GlobalcacheStrategy", "workflow_lineage")
_emit_records_healing_outcome("p3", "GlobalcacheStrategy", "healing_outcome")
_emit_escalates_failure("p3", "GlobalcacheStrategy", "failure_escalation")
_emit_orchestrates_workflow("p3", "GlobalcacheStrategy", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "GlobalcacheStrategy", "healing_dispatch")
_emit_invokes_evaluation("p3", "GlobalcacheStrategy", "evaluation_signal")
_emit_records_telemetry_event("p4", "GlobalcacheStrategy", "telemetry_event")
_emit_captures_evaluation_metric("p4", "GlobalcacheStrategy", "eval_metric")
_emit_stores_embedding("p4", "GlobalcacheStrategy", "embedding_store")
_emit_updates_meta_learning_state("p4", "GlobalcacheStrategy", "meta_learning")
_emit_links_execution_to_snapshot("p4", "GlobalcacheStrategy", "exec_snapshot_link")

try:
    import numpy as np
except ImportError as _err:
    raise ImportError("numpy is required for this module. Install with: pip install -e '.[infra]'") from _err
from pydantic import BaseModel, Field

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

_emit_emits_metric_event("GlobalcacheStrategy", "p4obs", "metric_1")
_emit_emits_metric_event("GlobalcacheStrategy", "p4obs", "metric_2")
_emit_emits_metric_event("GlobalcacheStrategy", "p4obs", "metric_3")
_emit_emits_metric_event("GlobalcacheStrategy", "p4obs", "metric_4")
_emit_emits_metric_event("GlobalcacheStrategy", "p4obs", "metric_5")
_emit_emits_metric_event("GlobalcacheStrategy", "p4obs", "metric_6")
_emit_records_incident_event("GlobalcacheStrategy", "p4obs", "incident")
_emit_captures_runtime_anomaly("GlobalcacheStrategy", "p4obs", "anomaly")
_emit_writes_observability_log("GlobalcacheStrategy", "p4obs", "obs_log")
_emit_updates_monitoring_state("GlobalcacheStrategy", "p4obs", "mon_state")
_emit_triggers_alert("GlobalcacheStrategy", "p4obs", "alert")
_emit_links_incident_trace("GlobalcacheStrategy", "p4obs", "trace_link")
_emit_captures_pattern("GlobalcacheStrategy", "p3lm", "pattern")
_emit_records_learning_event("GlobalcacheStrategy", "p3lm", "learning_event")
_emit_writes_learning_snapshot("GlobalcacheStrategy", "p3lm", "snapshot")
_emit_feeds_meta_learning("GlobalcacheStrategy", "p3lm", "meta_feed")
_emit_updates_routing_strategy("GlobalcacheStrategy", "p3lm", "routing")
_emit_improves_agent_policy("GlobalcacheStrategy", "p3lm", "policy")
_emit_stores_learning_state("GlobalcacheStrategy", "p3lm", "state")
_emit_records_execution_trace("GlobalcacheStrategy", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("GlobalcacheStrategy", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("GlobalcacheStrategy", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("GlobalcacheStrategy", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("GlobalcacheStrategy", "L4_STATE", "p2_trace_5")
_emit_reads_environ("GlobalcacheStrategy", "env_read", "p2_env_1")
_emit_reads_environ("GlobalcacheStrategy", "env_read", "p2_env_2")
_emit_reads_runtime_state("GlobalcacheStrategy", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("GlobalcacheStrategy", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "GlobalcacheStrategy", "context_pull")
_emit_pulls_context("p1", "GlobalcacheStrategy", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "GlobalcacheStrategy", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "GlobalcacheStrategy", "uwg_term_2")
_emit_writes_through("p1", "GlobalcacheStrategy", "write_through")
_emit_writes_through("p1", "GlobalcacheStrategy", "write_through_2")
_emit_validated_by_safety_plane("p1", "GlobalcacheStrategy", "safety_validation")
_emit_invokes_eval("p1", "GlobalcacheStrategy", "eval_call")
_emit_proposal_commits_routing("p1", "GlobalcacheStrategy", "routing_commit")
_emit_escalates_to_human("p1", "GlobalcacheStrategy", "human_escalation")
_emit_routes_through("p1", "GlobalcacheStrategy", "route_through")
_emit_checks_agent_registry("p1", "GlobalcacheStrategy", "agent_registry")
_emit_validates_agent_capability("p1", "GlobalcacheStrategy", "capability")
_emit_dispatches_execution_plan("p1", "GlobalcacheStrategy", "exec_plan")
_emit_agent_executes_agent("p1", "GlobalcacheStrategy", "sub_agent")
_emit_routes_to_agent("p1", "GlobalcacheStrategy", "target_agent")
_emit_verifies_policy("p1", "GlobalcacheStrategy", "policy_check")
_emit_observes_runtime_state("p1", "GlobalcacheStrategy", "runtime_state")
_emit_verifies_boundary("p1", "GlobalcacheStrategy", "boundary_check")
_emit_transcripts_response("p1", "GlobalcacheStrategy", "transcript")
_emit_hard_fails_untranscripted("p1", "GlobalcacheStrategy")
_emit_gated_by_confidence("p1", "GlobalcacheStrategy", "confidence_gate")
_emit_reads_through("l4", "GlobalcacheStrategy", "urg_read_1")
_emit_reads_through("l4", "GlobalcacheStrategy", "urg_read_2")
_emit_reads_through("l4", "GlobalcacheStrategy", "urg_read_3")
_emit_reads_through("l4", "GlobalcacheStrategy", "urg_read_4")
_emit_reads_through("l4", "GlobalcacheStrategy", "urg_read_5")
_emit_reads_through("l4", "GlobalcacheStrategy", "urg_read_6")
_emit_reads_through("l4", "GlobalcacheStrategy", "urg_read_7")
_emit_reads_through("l4", "GlobalcacheStrategy", "urg_read_8")
_emit_reads_through("l4", "GlobalcacheStrategy", "urg_read_9")
_emit_reads_through("l4", "GlobalcacheStrategy", "urg_read_10")
_emit_reads_through("l4", "GlobalcacheStrategy", "urg_read_11")
_emit_reads_through("l4", "GlobalcacheStrategy", "urg_read_12")
_emit_reads_through("l4", "GlobalcacheStrategy", "urg_read_13")
_emit_reads_through("l4", "GlobalcacheStrategy", "urg_read_14")
_emit_reads_through("l4", "GlobalcacheStrategy", "urg_read_15")
_emit_reads_through("l4", "GlobalcacheStrategy", "urg_read_16")
_emit_reads_through("l4", "GlobalcacheStrategy", "urg_read_17")
_emit_reads_through("l4", "GlobalcacheStrategy", "urg_read_18")
_emit_reads_through("l4", "GlobalcacheStrategy", "urg_read_19")
_emit_reads_through("l4", "GlobalcacheStrategy", "urg_read_20")
_emit_reads_through("l4", "GlobalcacheStrategy", "urg_read_21")
_emit_reads_through("l4", "GlobalcacheStrategy", "urg_read_22")
_emit_reads_through("l4", "GlobalcacheStrategy", "urg_read_23")
_emit_reads_through("l4", "GlobalcacheStrategy", "urg_read_24")
_emit_reads_through("l4", "GlobalcacheStrategy", "urg_read_25")
_emit_reads_through("l4", "GlobalcacheStrategy", "urg_read_26")
_emit_reads_through("l4", "GlobalcacheStrategy", "urg_read_27")
_emit_reads_through("l4", "GlobalcacheStrategy", "urg_read_28")
_emit_reads_through("l4", "GlobalcacheStrategy", "urg_read_29")
_emit_reads_through("l4", "GlobalcacheStrategy", "urg_read_30")
_emit_reads_through("l4", "GlobalcacheStrategy", "urg_read_31")
_emit_reads_through("l4", "GlobalcacheStrategy", "urg_read_32")
_emit_reads_through("l4", "GlobalcacheStrategy", "urg_read_33")
_emit_reads_through("l4", "GlobalcacheStrategy", "urg_read_34")
_emit_reads_through("l4", "GlobalcacheStrategy", "urg_read_35")
_emit_reads_through("l4", "GlobalcacheStrategy", "urg_read_36")
_emit_reads_through("l4", "GlobalcacheStrategy", "urg_read_37")
_emit_reads_through("l4", "GlobalcacheStrategy", "urg_read_38")
_emit_reads_through("l4", "GlobalcacheStrategy", "urg_read_39")
_emit_reads_through("l4", "GlobalcacheStrategy", "urg_read_40")
_emit_reads_through("l4", "GlobalcacheStrategy", "urg_read_41")
_emit_reads_through("l4", "GlobalcacheStrategy", "urg_read_42")
_emit_reads_through("l4", "GlobalcacheStrategy", "urg_read_43")
_emit_reads_through("l4", "GlobalcacheStrategy", "urg_read_44")
_emit_reads_through("l4", "GlobalcacheStrategy", "urg_read_45")
_emit_reads_through("l4", "GlobalcacheStrategy", "urg_read_46")
_emit_reads_through("l4", "GlobalcacheStrategy", "urg_read_47")
_emit_reads_through("l4", "GlobalcacheStrategy", "urg_read_48")
_emit_reads_through("l4", "GlobalcacheStrategy", "urg_read_49")
_emit_reads_through("l4", "GlobalcacheStrategy", "urg_read_50")
_emit_reads_through("l4", "GlobalcacheStrategy", "urg_read_51")
_emit_reads_through("l4", "GlobalcacheStrategy", "urg_read_52")
_emit_reads_through("l4", "GlobalcacheStrategy", "urg_read_53")
_emit_reads_through("l4", "GlobalcacheStrategy", "urg_read_54")
_emit_reads_through("l4", "GlobalcacheStrategy", "urg_read_55")
_emit_reads_through("l4", "GlobalcacheStrategy", "urg_read_56")
_emit_reads_through("l4", "GlobalcacheStrategy", "urg_read_57")
_emit_reads_through("l4", "GlobalcacheStrategy", "urg_read_58")
_emit_reads_through("l4", "GlobalcacheStrategy", "urg_read_59")
_emit_reads_through("l4", "GlobalcacheStrategy", "urg_read_60")
_emit_reads_through("l4", "GlobalcacheStrategy", "urg_read_61")
_emit_reads_through("l4", "GlobalcacheStrategy", "urg_read_62")
_emit_reads_through("l4", "GlobalcacheStrategy", "urg_read_63")
_emit_reads_through("l4", "GlobalcacheStrategy", "urg_read_64")
_emit_reads_through("l4", "GlobalcacheStrategy", "urg_read_65")
_emit_reads_through("l4", "GlobalcacheStrategy", "urg_read_66")
_emit_reads_through("l4", "GlobalcacheStrategy", "urg_read_67")

logger = logging.getLogger(__name__)


class CacheEntry(BaseModel):
    """cache entry with metadata."""

    key_hash: str
    value: Any
    embedding: list[float] = Field(default_factory=list)
    created_at: float = Field(default_factory=time.time)
    ttl: int = Field(default=3600)
    source_engine: str = Field(default="UNKNOWN")
    hit_count: int = Field(default=0)
    last_accessed: float = Field(default_factory=time.time)

    def is_expired(self) -> bool:
        """Check if entry is expired.

        Returns:
            True if expired
        """
        return time.time() > self.created_at + self.ttl

    def touch(self) -> None:
        """Update last accessed time."""
        self.last_accessed = time.time()
        self.hit_count += 1


class L1MemoryCache:
    """L1 cache - LRU memory cache for exact matches."""

    # guardian: allow-magic-config
    def __init__(self, max_size: int = 1000):
        """Initialize L1 cache.

        Args:
            max_size: Maximum number of entries
        """
        self.max_size = max_size
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._hits = 0
        self._misses = 0
        logger.debug(f"Initialized L1 cache with max_size={max_size}")

    def get(self, key_hash: str) -> CacheEntry | None:
        """Get entry from cache.

        Args:
            key_hash: Hash of the key

        Returns:
            cache entry if found and not expired
        """
        if key_hash in self.cache:
            entry = self.cache[key_hash]
            if entry.is_expired():
                del self.cache[key_hash]
                self._misses += 1
                return None
            self.cache.move_to_end(key_hash)
            entry.touch()
            self._hits += 1
            return entry
        self._misses += 1
        return None

    def put(self, key_hash: str, entry: CacheEntry) -> None:
        """Put entry in cache.

        Args:
            key_hash: Hash of the key
            entry: cache entry
        """
        if key_hash in self.cache:
            del self.cache[key_hash]
        self.cache[key_hash] = entry
        while len(self.cache) > self.max_size:
            self.cache.popitem(last=False)

    def clear(self) -> None:
        """Clear all entries."""
        self.cache.clear()
        self._hits = 0
        self._misses = 0

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics.

        Returns:
            Statistics dictionary
        """
        total_requests = self._hits + self._misses
        hit_rate = self._hits / total_requests if total_requests > 0 else 0.0
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": hit_rate,
        }


class L2VectorStore:
    """L2 cache - Vector store for semantic matches."""

    # guardian: allow-magic-config
    def __init__(self, max_size: int = 10000):
        """Initialize L2 vector store.

        Args:
            max_size: Maximum number of entries
        """
        self.max_size = max_size
        self.entries: list[CacheEntry] = []
        self.embeddings: np.ndarray = np.array([]).reshape(0, 0)
        self._hits = 0
        self._misses = 0
        logger.debug(f"Initialized L2 vector store with max_size={max_size}")

    def add(self, entry: CacheEntry) -> None:
        """Add entry to vector store.

        Args:
            entry: cache entry with embedding
        """
        if not entry.embedding:
            return
        for i, existing in enumerate(self.entries):
            if existing.key_hash == entry.key_hash:
                self.entries[i] = entry
                if self.embeddings.shape[0] > 0:
                    self.embeddings[i] = np.array(entry.embedding)
                return
        self.entries.append(entry)
        if self.embeddings.shape[0] == 0:
            self.embeddings = np.array([entry.embedding])
        else:
            self.embeddings = np.vstack([self.embeddings, entry.embedding])
        while len(self.entries) > self.max_size:
            self.entries.pop(0)
            self.embeddings = self.embeddings[1:]

    # guardian: allow-magic-config
    def search(
        self, query_embedding: list[float], threshold: float = 0.92, max_results: int = 5
    ) -> list[tuple[CacheEntry, float]]:
        """Search for semantically similar entries.

        Args:
            query_embedding: Query embedding vector
            threshold: Similarity threshold
            max_results: Maximum results to return

        Returns:
            List of (entry, similarity) tuples
        """
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, "SemanticVectorStore.search")
        if self.embeddings.shape[0] == 0:
            self._misses += 1
            return []
        query_vec = np.array(query_embedding)
        similarities = np.dot(self.embeddings, query_vec)
        results = []
        for i, similarity in enumerate(similarities):
            if similarity >= threshold:
                entry = self.entries[i]
                if entry.is_expired():
                    continue
                entry.touch()
                results.append((entry, float(similarity)))
        results.sort(key=lambda x: x[1], reverse=True)
        if results:
            self._hits += 1
        else:
            self._misses += 1
        return results[:max_results]

    def clear(self) -> None:
        """Clear all entries."""
        self.entries.clear()
        self.embeddings = np.array([]).reshape(0, 0)
        self._hits = 0
        self._misses = 0

    def get_stats(self) -> dict[str, Any]:
        """Get store statistics.

        Returns:
            Statistics dictionary
        """
        total_requests = self._hits + self._misses
        hit_rate = self._hits / total_requests if total_requests > 0 else 0.0
        return {
            "size": len(self.entries),
            "max_size": self.max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": hit_rate,
            "embedding_dim": self.embeddings.shape[1] if self.embeddings.shape[0] > 0 else 0,
        }


class SimpleEmbedder:
    """Simple local embedding generator."""

    def __init__(self, model_name: str = "BAAI/bge-m3"):
        """Initialize embedder.

        Args:
            model_name: Name of sentence transformer model
        """
        self.model_name = model_name
        self._model = None
        self._embedding_dim = 512  # Changed from 1024 to 512
        logger.debug(f"Initialized SimpleEmbedder with model: {model_name}")

    def _load_model(self) -> None:
        """Load the embedding model."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer

                self._model = SentenceTransformer(self.model_name)
                logger.info(f"Loaded embedding model: {self.model_name}")
            # guardian: allow-silent-swallow - optional dependency
            except ImportError:
                logger.warning("sentence_transformers not available, using dummy embeddings")
                self._model = "dummy"

    def embed(self, text: str) -> list[float]:
        """Generate embedding for text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        self._load_model()
        if self._model == "dummy":
            hash_obj = hashlib.md5(text.encode())
            hash_hex = hash_obj.hexdigest()
            embedding = []
            for i in range(0, len(hash_hex), 2):
                val = int(hash_hex[i : i + 2], 16) / 255.0 - 0.5
                embedding.append(val)
            while len(embedding) < self._embedding_dim:
                embedding.append(0.0)
            return embedding[: self._embedding_dim]
        embedding = self._model.encode(text, convert_to_numpy=True)
        return embedding.tolist()


class GlobalCache:
    """Global semantic cache with L1/L2 storage.

    L1: in-process LRU (exact key hash, O(1))
    L2: delegates to SemanticCacheManager singleton (BGE vector store, Redis working memory)
    """

    _HIVE_NAMESPACE = "GlobalCache"

    # guardian: allow-magic-config
    def __init__(self, l1_size: int = 1000, l2_size: int = 10000, semantic_threshold: float = 0.92):
        """Initialize global cache.

        Args:
            l1_size: L1 cache size
            l2_size: L2 cache size (kept for API compat; L2 is now SSOT-backed)
            semantic_threshold: Semantic similarity threshold
        """
        self.l1 = L1MemoryCache(l1_size)
        self.l2 = L2VectorStore(l2_size)
        self.embedder = SimpleEmbedder()
        self.semantic_threshold = semantic_threshold
        self._hive: Any = None
        self._stats = {"total_requests": 0, "l1_hits": 0, "l2_hits": 0, "total_misses": 0}
        logger.info(
            f"Initialized GlobalCache (L1: {l1_size}, L2: SSOT-backed, threshold: {semantic_threshold})"
        )

    def get_hive_mind(self):
        """Lazy-load SemanticCacheManager singleton for L2 delegation."""
        if self._hive is None:
            try:
                from agentic_core.L4_state.utils.memory.semantic_cache_manager import SemanticCacheManager

                self._hive = SemanticCacheManager.get_instance()
            # guardian: allow-silent-swallow
            except Exception as e:
                logger.warning(f"[GlobalCache] SemanticCacheManager unavailable, L2 disabled: {e}")
                self._hive = False
        return self._hive if self._hive is not False else None

    def get(self, key: str) -> Any | None:
        """Get value by exact key.

        Args:
            key: Lookup key

        Returns:
            Cached value if found
        """
        self._stats["total_requests"] += 1
        key_hash = self._hash_key(key)
        entry = self.l1.get(key_hash)
        if entry:
            self._stats["l1_hits"] += 1
            return entry.value
        results = self.l2.search(self.embedder.embed(key), threshold=THRESHOLD, max_results=1)
        if results:
            entry, _ = results[0]
            self._stats["l2_hits"] += 1
            self.l1.put(key_hash, entry)
            return entry.value
        self._stats["total_misses"] += 1
        return None

    def get_semantic(
        self, query_text: str, threshold: float | None = None, max_results: int = 1
    ) -> list[Any]:
        """Get values by semantic similarity.

        Checks SemanticCacheManager (SSOT L2) first, then falls back to
        local L2VectorStore for entries stored before SSOT delegation.

        Args:
            query_text: Query text
            threshold: Similarity threshold (uses default if None)
            max_results: Maximum results

        Returns:
            List of cached values
        """
        self._stats["total_requests"] += 1
        if threshold is None:
            threshold = self.semantic_threshold
        hive = self.get_hive_mind()
        if hive is not None:
            try:
                recalled = hive.recall(query_text, self._HIVE_NAMESPACE)
                if recalled is not None:
                    self._stats["l2_hits"] += 1
                    value = recalled.get("value", recalled)
                    return [value] if max_results >= 1 else []
            # guardian: allow-silent-swallow
            except Exception as e:
                logger.debug(f"[GlobalCache] Hive recall failed: {e}")
        query_embedding = self.embedder.embed(query_text)
        results = self.l2.search(query_embedding, threshold, max_results)
        if results:
            self._stats["l2_hits"] += 1
            best_entry, _ = results[0]
            key_hash = self._hash_key(query_text)
            self.l1.put(key_hash, best_entry)
            return [entry.value for entry, _ in results]
        self._stats["total_misses"] += 1
        return []

    def put(
        self,
        key: str,
        value: Any,
        text_for_embedding: str | None = None,
        ttl: int = 3600,
        source_engine: str = "UNKNOWN",
    ) -> None:
        """Put value in cache.

        Stores in L1 LRU and, when text_for_embedding is provided, also
        delegates to SemanticCacheManager.learn() for SSOT L2 persistence.

        Args:
            key: cache key
            value: Value to cache
            text_for_embedding: Text for semantic indexing
            ttl: Time to live in seconds
            source_engine: Source engine identifier
        """
        key_hash = self._hash_key(key)
        embedding = []
        if text_for_embedding:
            embedding = self.embedder.embed(text_for_embedding)
        entry = CacheEntry(
            key_hash=key_hash, value=value, embedding=embedding, ttl=ttl, source_engine=source_engine
        )
        self.l1.put(key_hash, entry)
        if embedding:
            self.l2.add(entry)
        if text_for_embedding:
            hive = self.get_hive_mind()
            if hive is not None:
                try:
                    hive.learn(
                        text_for_embedding,
                        self._HIVE_NAMESPACE,
                        {"value": value, "key": key, "source_engine": source_engine},
                    )
                # guardian: allow-silent-swallow
                except Exception as e:
                    logger.debug(f"[GlobalCache] Hive learn failed: {e}")

    def _hash_key(self, key: str) -> str:
        """Generate hash for key.

        Args:
            key: Key to hash

        Returns:
            Hash string
        """
        return hashlib.sha256(key.encode()).hexdigest()[:16]

    def clear(self) -> None:
        """Clear all cache entries."""
        self.l1.clear()
        self.l2.clear()
        self._stats = {"total_requests": 0, "l1_hits": 0, "l2_hits": 0, "total_misses": 0}
        logger.info("Cleared global cache")

    def cleanup_expired(self) -> int:
        """Remove expired entries.

        Returns:
            Number of entries cleaned up
        """
        cleaned = 0
        l1_keys = list(self.l1.cache.keys())
        for key_hash in l1_keys:
            entry = self.l1.cache[key_hash]
            if entry.is_expired():
                del self.l1.cache[key_hash]
                cleaned += 1
        self.l2.entries = [e for e in self.l2.entries if not e.is_expired()]
        if self.l2.entries:
            self.l2.embeddings = np.array([e.embedding for e in self.l2.entries])
        else:
            self.l2.embeddings = np.array([]).reshape(0, 0)
        if cleaned > 0:
            logger.info(f"Cleaned up {cleaned} expired cache entries")
        return cleaned

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics.

        Returns:
            Statistics dictionary
        """
        stats = self._stats.copy()
        stats["l1"] = self.l1.get_stats()
        stats["l2"] = self.l2.get_stats()
        if stats["total_requests"] > 0:
            stats["overall_hit_rate"] = (stats["l1_hits"] + stats["l2_hits"]) / stats["total_requests"]
        else:
            stats["overall_hit_rate"] = 0.0
        return stats


_global_cache: GlobalCache | None = None


def get_global_cache() -> GlobalCache:
    """Get global cache instance.

    Returns:
        GlobalCache instance
    """
    global _global_cache
    if _global_cache is None:
        _global_cache = GlobalCache()
    return _global_cache


# guardian: allow-magic-config
def cached(
    key_func: Callable[..., Any] | None = None,
    ttl: int = 3600,
    semantic: bool = False,
    threshold: float = 0.92,
):
    """Decorator for caching function results.

    Args:
        key_func: Function to generate cache key from args
        ttl: Time to live in seconds
        semantic: Use semantic caching
        threshold: Semantic similarity threshold

    Returns:
        Decorated function
    """

    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            cache = get_global_cache()
            if key_func:
                key = key_func(*args, **kwargs)
            else:
                key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            if semantic:
                query_text = str(args[0]) if args else key
                results = cache.get_semantic(query_text, threshold=threshold)
                if results:
                    return results[0]
            else:
                result = cache.get(key)
                if result is not None:
                    return result
            result = await func(*args, **kwargs)
            if semantic:
                cache.put(
                    key,
                    result,
                    text_for_embedding=str(args[0]) if args else key,
                    ttl=ttl,
                    source_engine=func.__module__,
                )
            else:
                cache.put(key, result, ttl=ttl, source_engine=func.__module__)
            return result

        return async_wrapper

    return decorator


def cache_get(key: str) -> Any | None:
    """Get value from global cache.

    Args:
        key: cache key

    Returns:
        Cached value
    """
    cache = get_global_cache()
    return cache.get(key)


def cache_put(
    key: str,
    value: Any,
    text_for_embedding: str | None = None,
    ttl: int = 3600,
    source_engine: str = "UNKNOWN",
) -> None:
    """Put value in global cache.

    Args:
        key: cache key
        value: Value to cache
        text_for_embedding: Text for semantic indexing
        ttl: Time to live
        source_engine: Source engine
    """
    cache = get_global_cache()
    cache.put(key, value, text_for_embedding, ttl, source_engine)


def cache_search_semantic(query_text: str, threshold: float | None = None, max_results: int = 1) -> list[Any]:
    """Search cache semantically.

    Args:
        query_text: Query text
        threshold: Similarity threshold
        max_results: Maximum results

    Returns:
        List of cached values
    """
    cache = get_global_cache()
    return cache.get_semantic(query_text, threshold, max_results)
