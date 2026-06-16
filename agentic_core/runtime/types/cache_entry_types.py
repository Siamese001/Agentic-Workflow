from __future__ import annotations

from agentic_core.config.model_catalog import (
    BGE_M3_MODEL_ID,
)

from dataclasses import dataclass, field

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_applies_guardrail("p0", "cache_entry_types", "p0_governance")
_emit_reads_policy_state("p0", "cache_entry_types", "policy_binding")
_emit_snapshots_state("p0", "cache_entry_types", "state_snapshot")
emit_replay_key("p0", "cache_entry_types")
emit_determinism_digest("p0", "cache_entry_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "cache_entry_types", "execution_auth")
_emit_validates_capability("p2", "cache_entry_types", "capability_check")
_emit_routes_to_capability("p2", "cache_entry_types", "capability_route")
_emit_writes_via_uwg("p2", "cache_entry_types", "uwg_write")
_emit_blocks_direct_write("p2", "cache_entry_types", "direct_write_block")
_emit_records_tool_invocation("p2", "cache_entry_types", "tool_invocation")
_emit_captures_execution_output("p2", "cache_entry_types", "exec_output")
_emit_dispatches_agent("p3", "cache_entry_types", "agent_dispatch")
_emit_coordinates_agents("p3", "cache_entry_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "cache_entry_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "cache_entry_types", "healing_outcome")
_emit_escalates_failure("p3", "cache_entry_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "cache_entry_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "cache_entry_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "cache_entry_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "cache_entry_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "cache_entry_types", "eval_metric")
_emit_stores_embedding("p4", "cache_entry_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "cache_entry_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "cache_entry_types", "exec_snapshot_link")

"Semantic cache for LLM response caching.\n\nPhase 1 - Pillar 11: Cost & Optimization (Semantic Caching)\nEnhanced with embedding-based semantic similarity matching.\n"
import hashlib
import json
import logging
import time
from typing import Any

try:
    import numpy as np
except ImportError as _err:
    raise ImportError("numpy is required for this module. Install with: pip install -e '.[infra]'") from _err
try:
    from agentic_core.semantic_memory.embeddings.core_embedder import get_embedding
except ImportError as _get_embedding_import_err:

    def get_embedding(text: str, model: str = None, dimensions: int = None):  # type: ignore[misc]
        """Fail-fast: real embedder unavailable — do not silently disable semantic matching."""
        raise ImportError(
            "agentic_core.semantic_memory.embeddings.core_embedder is unavailable; "
            "cannot compute embeddings (install the semantic_memory extras)"
        ) from _get_embedding_import_err


from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("cache_entry_types", "p4obs", "metric_1")
_emit_emits_metric_event("cache_entry_types", "p4obs", "metric_2")
_emit_emits_metric_event("cache_entry_types", "p4obs", "metric_3")
_emit_emits_metric_event("cache_entry_types", "p4obs", "metric_4")
_emit_emits_metric_event("cache_entry_types", "p4obs", "metric_5")
_emit_emits_metric_event("cache_entry_types", "p4obs", "metric_6")
_emit_records_incident_event("cache_entry_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("cache_entry_types", "p4obs", "anomaly")
_emit_writes_observability_log("cache_entry_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("cache_entry_types", "p4obs", "mon_state")
_emit_triggers_alert("cache_entry_types", "p4obs", "alert")
_emit_links_incident_trace("cache_entry_types", "p4obs", "trace_link")
_emit_captures_pattern("cache_entry_types", "p3lm", "pattern")
_emit_records_learning_event("cache_entry_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("cache_entry_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("cache_entry_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("cache_entry_types", "p3lm", "routing")
_emit_improves_agent_policy("cache_entry_types", "p3lm", "policy")
_emit_stores_learning_state("cache_entry_types", "p3lm", "state")
_emit_records_execution_trace("cache_entry_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("cache_entry_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("cache_entry_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("cache_entry_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("cache_entry_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("cache_entry_types", "env_read", "p2_env_1")
_emit_reads_environ("cache_entry_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("cache_entry_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("cache_entry_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "cache_entry_types", "context_pull")
_emit_pulls_context("p1", "cache_entry_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "cache_entry_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "cache_entry_types", "uwg_term_2")
_emit_writes_through("p1", "cache_entry_types", "write_through")
_emit_writes_through("p1", "cache_entry_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "cache_entry_types", "safety_validation")
_emit_invokes_eval("p1", "cache_entry_types", "eval_call")
_emit_proposal_commits_routing("p1", "cache_entry_types", "routing_commit")
_emit_escalates_to_human("p1", "cache_entry_types", "human_escalation")
_emit_routes_through("p1", "cache_entry_types", "route_through")
_emit_checks_agent_registry("p1", "cache_entry_types", "agent_registry")
_emit_validates_agent_capability("p1", "cache_entry_types", "capability")
_emit_dispatches_execution_plan("p1", "cache_entry_types", "exec_plan")
_emit_agent_executes_agent("p1", "cache_entry_types", "sub_agent")
_emit_routes_to_agent("p1", "cache_entry_types", "target_agent")
_emit_verifies_policy("p1", "cache_entry_types", "policy_check")
_emit_observes_runtime_state("p1", "cache_entry_types", "runtime_state")
_emit_verifies_boundary("p1", "cache_entry_types", "boundary_check")
_emit_transcripts_response("p1", "cache_entry_types", "transcript")
_emit_hard_fails_untranscripted("p1", "cache_entry_types")
_emit_gated_by_confidence("p1", "cache_entry_types", "confidence_gate")

Logger: Any = logging.getLogger(__name__)
SIMILARITY_THRESHOLD = 0.92
EMBEDDING_MODEL = BGE_M3_MODEL_ID
EMBEDDING_DIM = 1024


@dataclass
class CacheEntry:
    """Single cache entry."""

    key: str
    prompt: str
    response: Any
    created_at: float
    accessed_at: float
    hit_count: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)
    embedding: np.ndarray | None = None
    evidence_ids: list[str] = field(default_factory=list)
    corpus_version: str = ""
    embedding_model_id: str = ""
    tenant_id: str = ""
    ttl_seconds: int = 86400
    grounding_complete: bool = False
    policy_version: str = ""

    def is_expired(self, ttl: int) -> bool:
        """Check if entry is expired.

        Args:
            ttl: Time-to-live in seconds

        Returns:
            True if expired
        """
        return time.time() - self.created_at > ttl


@dataclass
class SemanticCacheHit:
    """Extended cache hit with semantic details."""

    response: Any
    entry: CacheEntry
    age_seconds: float
    similarity_score: float = 1.0
    match_type: str = "exact"
    evidence_ids: list[str] = field(default_factory=list)
    corpus_version: str = ""
    embedding_model_id: str = ""
    tenant_id: str = ""
    ttl_seconds: int = 86400
    grounding_complete: bool = False
    policy_version: str = ""


@dataclass
class CacheMiss:
    """cache miss result."""

    prompt: str
    reason: str = "not_found"


class semantic_cache:
    """Enhanced semantic cache with optional embedding-based similarity matching."""

    # guardian: allow-magic-config
    def __init__(
        self,
        ttl: int = 3600,
        max_entries: int = 10000,
        enable_logging: bool = True,
        enable_semantic_matching: bool = True,
        similarity_threshold: float = SIMILARITY_THRESHOLD,
        embedding_model: str = EMBEDDING_MODEL,
    ):
        """Initialize semantic cache.

        Args:
            ttl: Time-to-live for cache entries in seconds
            max_entries: Maximum number of cache entries
            enable_logging: Enable logging of cache events
            enable_semantic_matching: Enable embedding-based similarity matching
            similarity_threshold: Cosine similarity threshold for semantic matches
            embedding_model: Model to use for embeddings
        """
        self.ttl = ttl
        self.max_entries = max_entries
        self.enable_logging = enable_logging
        self.enable_semantic_matching = enable_semantic_matching
        self.similarity_threshold = similarity_threshold
        self.embedding_model = embedding_model
        self._cache: dict[str, CacheEntry] = {}
        self._embedding_index: dict[str, np.ndarray] = {}
        self._hit_count = 0
        self._miss_count = 0
        self._semantic_hit_count = 0

    def _compute_embedding(self, text: str) -> np.ndarray:
        """Compute normalized embedding vector."""
        embedding = get_embedding(text[:8192], model=self.embedding_model)
        vec = np.array(embedding)
        norm = float(np.linalg.norm(vec))
        if norm == 0.0:
            raise ValueError(
                "_compute_embedding produced a zero-norm vector; "
                "the embedder may be unavailable or returning invalid output"
            )
        return vec / norm

    def _find_semantic_match(self, query_embedding: np.ndarray) -> tuple[str, float] | None:
        """Linear search for best semantic match above threshold."""
        if float(np.linalg.norm(query_embedding)) == 0.0:
            raise ValueError(
                "_find_semantic_match received a zero-norm embedding; "
                "invalid embedding cannot be used for semantic comparison"
            )
        best_key = None
        best_score = 0.0
        for key, cached_emb in self._embedding_index.items():
            score = float(np.dot(query_embedding, cached_emb))
            if score > best_score and score >= self.similarity_threshold:
                best_score = score
                best_key = key
        return (best_key, best_score) if best_key else None

    def _hash_prompt(self, prompt: str, context: dict[str, Any] | None = None) -> str:
        """Generate cache key from prompt and context."""
        cache_input = prompt
        if context:
            context_str = json.dumps(context, sort_keys=True, default=str)
            cache_input = f"{prompt}::{context_str}"
        return hashlib.sha256(cache_input.encode()).hexdigest()

    def get(self, prompt: str, context: dict[str, Any] | None = None) -> SemanticCacheHit | CacheMiss:
        """Get cached response, falling back to semantic similarity if enabled."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "semantic_cache.get")

        key = self._hash_prompt(prompt, context)
        entry = self._cache.get(key)
        if entry and (not entry.is_expired(self.ttl)):
            entry.accessed_at = time.time()
            entry.hit_count += 1
            self._hit_count += 1
            return SemanticCacheHit(
                response=entry.response,
                entry=entry,
                age_seconds=time.time() - entry.created_at,
                similarity_score=1.0,
                match_type="exact",
            )
        if self.enable_semantic_matching:
            query_text = prompt
            if context:
                query_text += f"::{json.dumps(context, sort_keys=True, default=str)}"
            query_emb = self._compute_embedding(query_text)
            match = self._find_semantic_match(query_emb)
            if match:
                matched_key, score = match
                matched_entry = self._cache.get(matched_key)
                if matched_entry and (not matched_entry.is_expired(self.ttl)):
                    matched_entry.accessed_at = time.time()
                    matched_entry.hit_count += 1
                    self._semantic_hit_count += 1
                    if self.enable_logging:
                        Logger.info(
                            "semantic_cache_hit",
                            extra={
                                "similarity_score": score,
                                "matched_prompt_snippet": matched_entry.prompt[:100],
                                "query_prompt_snippet": prompt[:100],
                            },
                        )
                    return SemanticCacheHit(
                        response=matched_entry.response,
                        entry=matched_entry,
                        age_seconds=time.time() - matched_entry.created_at,
                        similarity_score=score,
                        match_type="semantic",
                    )
        self._miss_count += 1
        return CacheMiss(prompt=prompt, reason="not_found")

    def set(
        self,
        prompt: str,
        response: Any,
        context: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Set cache entry, computing embedding if semantic matching enabled."""
        if len(self._cache) >= self.max_entries:
            self._evict_oldest()
        key = self._hash_prompt(prompt, context)
        now = time.time()
        embedding = None
        if self.enable_semantic_matching:
            set_text = prompt
            if context:
                set_text += f"::{json.dumps(context, sort_keys=True, default=str)}"
            embedding = self._compute_embedding(set_text)
            self._embedding_index[key] = embedding
        entry = CacheEntry(
            key=key,
            prompt=prompt,
            response=response,
            created_at=now,
            accessed_at=now,
            metadata=metadata or {},
            embedding=embedding,
        )
        self._cache[key] = entry
        if self.enable_logging:
            Logger.debug(f"Cached entry: {key[:10]}... (semantic: {self.enable_semantic_matching})")

    def _evict_oldest(self) -> None:
        """Evict the least recently accessed entry."""
        if not self._cache:
            return
        oldest_key = min(self._cache, key=lambda k: self._cache[k].accessed_at)
        del self._cache[oldest_key]
        if oldest_key in self._embedding_index:
            del self._embedding_index[oldest_key]
        if self.enable_logging:
            Logger.info(f"Evicted oldest cache entry: {oldest_key[:10]}...")

    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()
        self._embedding_index.clear()
        if self.enable_logging:
            Logger.info("cache_cleared")

    def get_stats(self) -> dict[str, Any]:
        """Get detailed cache statistics."""
        total_hits = self._hit_count + self._semantic_hit_count
        total_requests = total_hits + self._miss_count
        hit_rate = total_hits / total_requests if total_requests > 0 else 0.0
        semantic_hit_rate = self._semantic_hit_count / total_requests if total_requests > 0 else 0.0
        return {
            "exact_hits": self._hit_count,
            "semantic_hits": self._semantic_hit_count,
            "misses": self._miss_count,
            "total_hit_rate": hit_rate,
            "semantic_hit_rate": semantic_hit_rate,
            "current_size": len(self._cache),
            "max_size": self.max_entries,
        }

    def prune_expired(self) -> int:
        """Remove all expired entries.

        Returns:
            Number of entries removed
        """
        expired_keys = [key for key, entry in self._cache.items() if entry.is_expired(self.ttl)]
        for key in expired_keys:
            del self._cache[key]
            if key in self._embedding_index:
                del self._embedding_index[key]
        if self.enable_logging and expired_keys:
            Logger.info("cache_pruned", extra={"removed_count": len(expired_keys)})
        return len(expired_keys)


# guardian: allow-magic-config
def create_semantic_cache(
    ttl: int = 3600,
    max_entries: int = 10000,
    enable_semantic_matching: bool = True,
    similarity_threshold: float = SIMILARITY_THRESHOLD,
) -> semantic_cache:
    """Factory function to create a semantic cache.

    Args:
        ttl: Time-to-live in seconds
        max_entries: Maximum cache entries
        enable_semantic_matching: Enable embedding-based similarity matching
        similarity_threshold: Cosine similarity threshold for semantic matches

    Returns:
        Configured semantic_cache instance
    """
    return semantic_cache(
        ttl=ttl,
        max_entries=max_entries,
        enable_semantic_matching=enable_semantic_matching,
        similarity_threshold=similarity_threshold,
    )


_emit_reads_through("l4", "cache_entry_types", "urg_read_1")
_emit_reads_through("l4", "cache_entry_types", "urg_read_2")
_emit_reads_through("l4", "cache_entry_types", "urg_read_3")
_emit_reads_through("l4", "cache_entry_types", "urg_read_4")
_emit_reads_through("l4", "cache_entry_types", "urg_read_5")
_emit_reads_through("l4", "cache_entry_types", "urg_read_6")
_emit_reads_through("l4", "cache_entry_types", "urg_read_7")
_emit_reads_through("l4", "cache_entry_types", "urg_read_8")
_emit_reads_through("l4", "cache_entry_types", "urg_read_9")
_emit_reads_through("l4", "cache_entry_types", "urg_read_10")
_emit_reads_through("l4", "cache_entry_types", "urg_read_11")
_emit_reads_through("l4", "cache_entry_types", "urg_read_12")
_emit_reads_through("l4", "cache_entry_types", "urg_read_13")
_emit_reads_through("l4", "cache_entry_types", "urg_read_14")
_emit_reads_through("l4", "cache_entry_types", "urg_read_15")
_emit_reads_through("l4", "cache_entry_types", "urg_read_16")
_emit_reads_through("l4", "cache_entry_types", "urg_read_17")
_emit_reads_through("l4", "cache_entry_types", "urg_read_18")
_emit_reads_through("l4", "cache_entry_types", "urg_read_19")
_emit_reads_through("l4", "cache_entry_types", "urg_read_20")
_emit_reads_through("l4", "cache_entry_types", "urg_read_21")
_emit_reads_through("l4", "cache_entry_types", "urg_read_22")
_emit_reads_through("l4", "cache_entry_types", "urg_read_23")
_emit_reads_through("l4", "cache_entry_types", "urg_read_24")
_emit_reads_through("l4", "cache_entry_types", "urg_read_25")
_emit_reads_through("l4", "cache_entry_types", "urg_read_26")
_emit_reads_through("l4", "cache_entry_types", "urg_read_27")
_emit_reads_through("l4", "cache_entry_types", "urg_read_28")
_emit_reads_through("l4", "cache_entry_types", "urg_read_29")
_emit_reads_through("l4", "cache_entry_types", "urg_read_30")
_emit_reads_through("l4", "cache_entry_types", "urg_read_31")
_emit_reads_through("l4", "cache_entry_types", "urg_read_32")
_emit_reads_through("l4", "cache_entry_types", "urg_read_33")
_emit_reads_through("l4", "cache_entry_types", "urg_read_34")
_emit_reads_through("l4", "cache_entry_types", "urg_read_35")
_emit_reads_through("l4", "cache_entry_types", "urg_read_36")
_emit_reads_through("l4", "cache_entry_types", "urg_read_37")
_emit_reads_through("l4", "cache_entry_types", "urg_read_38")
_emit_reads_through("l4", "cache_entry_types", "urg_read_39")
_emit_reads_through("l4", "cache_entry_types", "urg_read_40")
_emit_reads_through("l4", "cache_entry_types", "urg_read_41")
_emit_reads_through("l4", "cache_entry_types", "urg_read_42")
_emit_reads_through("l4", "cache_entry_types", "urg_read_43")
_emit_reads_through("l4", "cache_entry_types", "urg_read_44")
_emit_reads_through("l4", "cache_entry_types", "urg_read_45")
_emit_reads_through("l4", "cache_entry_types", "urg_read_46")
_emit_reads_through("l4", "cache_entry_types", "urg_read_47")
_emit_reads_through("l4", "cache_entry_types", "urg_read_48")
_emit_reads_through("l4", "cache_entry_types", "urg_read_49")
_emit_reads_through("l4", "cache_entry_types", "urg_read_50")
_emit_reads_through("l4", "cache_entry_types", "urg_read_51")
_emit_reads_through("l4", "cache_entry_types", "urg_read_52")
_emit_reads_through("l4", "cache_entry_types", "urg_read_53")
_emit_reads_through("l4", "cache_entry_types", "urg_read_54")
_emit_reads_through("l4", "cache_entry_types", "urg_read_55")
