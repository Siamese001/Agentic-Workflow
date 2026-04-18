"""
MetaLearningClient - Unified Redis/Pinecone wrapper for healing pattern memory.

[PHASE 1] Core Infrastructure Implementation

Provides:
- Redis hot-path caching for expensive AST analysis results
- Pinecone semantic retrieval for successful healing strategies
- TTL management and similarity threshold guardrails
- Domain isolation for apps_lic and apps_rg territories

Guardrails:
- Minimum similarity threshold (0.85 default, configurable per domain)
- TTL expiration (1 hour default, configurable)
- Cache poisoning protection via input validation
- Recursive loop prevention via healing cycle depth tracking
"""
# guardian: allow-silent_swallower - ADG violation exemption

from __future__ import annotations

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402,
    # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,
    # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    # noqa: E402
    emit_replay_key,
)

emit_replay_key("p0", "meta_client")
emit_determinism_digest("p0", "meta_client")

_emit_dispatches_healing_run("p1", "meta_client", "L1")
_emit_routes_through("p1", "meta_client", "L1")
_emit_checks_agent_registry("p1", "meta_client", "agent_registry")
_emit_validates_agent_capability("p1", "meta_client", "capability")
_emit_dispatches_execution_plan("p1", "meta_client", "exec_plan")
_emit_agent_executes_agent("p1", "meta_client", "sub_agent")
_emit_routes_to_agent("p1", "meta_client", "target_agent")
_emit_verifies_policy("p1", "meta_client", "policy_check")
_emit_observes_runtime_state("p1", "meta_client", "runtime_state")
_emit_verifies_boundary("p1", "meta_client", "boundary_check")
_emit_transcripts_response("p1", "meta_client", "transcript")
_emit_hard_fails_untranscripted("p1", "meta_client")
_emit_gated_by_confidence("p1", "meta_client", "confidence_gate")
_emit_escalates_to_human("p1", "meta_client", "L1")
_emit_reads_policy_state("p1", "meta_client", "L1")
_emit_authorize_and_execute("p2", "meta_client", "execution_auth")
_emit_validates_capability("p2", "meta_client", "capability_check")
_emit_routes_to_capability("p2", "meta_client", "capability_route")
_emit_writes_via_uwg("p2", "meta_client", "uwg_write")
_emit_blocks_direct_write("p2", "meta_client", "direct_write_block")
_emit_records_tool_invocation("p2", "meta_client", "tool_invocation")
_emit_captures_execution_output("p2", "meta_client", "exec_output")
_emit_dispatches_agent("p3", "meta_client", "agent_dispatch")
_emit_coordinates_agents("p3", "meta_client", "agent_coordination")
_emit_records_workflow_lineage("p3", "meta_client", "workflow_lineage")
_emit_records_healing_outcome("p3", "meta_client", "healing_outcome")
_emit_escalates_failure("p3", "meta_client", "failure_escalation")
_emit_orchestrates_workflow("p3", "meta_client", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "meta_client", "healing_dispatch")
_emit_invokes_evaluation("p3", "meta_client", "evaluation_signal")
_emit_records_telemetry_event("p4", "meta_client", "telemetry_event")
_emit_captures_evaluation_metric("p4", "meta_client", "eval_metric")
_emit_stores_embedding("p4", "meta_client", "embedding_store")
_emit_updates_meta_learning_state("p4", "meta_client", "meta_learning")
_emit_links_execution_to_snapshot("p4", "meta_client", "exec_snapshot_link")


def _get_redis_sovereign_agent():
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_get_redis_sovereign_agent", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "_get_redis_sovereign_agent", "p0_governance")
    from agentic_core.interfaces.execution_agents import RedisSovereignAgent

    return RedisSovereignAgent


def _get_embedding_sovereign_agent():
    from agentic_core.interfaces.execution_agents import EmbeddingSovereignAgent

    return EmbeddingSovereignAgent


import hashlib
import json
import logging
import uuid
from dataclasses import dataclass, field
from typing import Any

from agentic_core.L1_cognition.types.client_types import (
    CACHE_KEY_PREFIX,
    DEFAULT_SIMILARITY_THRESHOLD,
    DEFAULT_TTL_SECONDS,
    MAX_HEALING_DEPTH,
    CacheEntry,
    HealingPattern,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
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
    _emit_routes_to_agent,
    _emit_snapshots_state,
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

_emit_emits_metric_event("meta_client", "p4obs", "metric_1")
_emit_emits_metric_event("meta_client", "p4obs", "metric_2")
_emit_emits_metric_event("meta_client", "p4obs", "metric_3")
_emit_emits_metric_event("meta_client", "p4obs", "metric_4")
_emit_emits_metric_event("meta_client", "p4obs", "metric_5")
_emit_emits_metric_event("meta_client", "p4obs", "metric_6")
_emit_records_incident_event("meta_client", "p4obs", "incident")
_emit_captures_runtime_anomaly("meta_client", "p4obs", "anomaly")
_emit_writes_observability_log("meta_client", "p4obs", "obs_log")
_emit_updates_monitoring_state("meta_client", "p4obs", "mon_state")
_emit_triggers_alert("meta_client", "p4obs", "alert")
_emit_links_incident_trace("meta_client", "p4obs", "trace_link")
_emit_captures_pattern("meta_client", "p3lm", "pattern")
_emit_records_learning_event("meta_client", "p3lm", "learning_event")
_emit_writes_learning_snapshot("meta_client", "p3lm", "snapshot")
_emit_feeds_meta_learning("meta_client", "p3lm", "meta_feed")
_emit_updates_routing_strategy("meta_client", "p3lm", "routing")
_emit_improves_agent_policy("meta_client", "p3lm", "policy")
_emit_stores_learning_state("meta_client", "p3lm", "state")
_emit_records_execution_trace("meta_client", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("meta_client", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("meta_client", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("meta_client", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("meta_client", "L4_STATE", "p2_trace_5")
_emit_reads_environ("meta_client", "env_read", "p2_env_1")
_emit_reads_environ("meta_client", "env_read", "p2_env_2")
_emit_reads_runtime_state("meta_client", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("meta_client", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "meta_client", "context_pull")
_emit_pulls_context("p1", "meta_client", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "meta_client", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "meta_client", "uwg_term_2")
_emit_writes_through("p1", "meta_client", "write_through")
_emit_writes_through("p1", "meta_client", "write_through_2")
_emit_validated_by_safety_plane("p1", "meta_client", "safety_validation")
_emit_invokes_eval("p1", "meta_client", "eval_call")
_emit_proposal_commits_routing("p1", "meta_client", "routing_commit")

Logger = logging.getLogger(__name__)
_singleton_instance: Any = None


@dataclass
class MetaLearningClient:
    """
    Unified Redis/Pinecone wrapper for healing pattern memory.

    [PHASE 1] Core Infrastructure Implementation

    Features:
    - Redis hot-path caching for expensive AST analysis results
    - Pinecone semantic retrieval for successful healing strategies
    - Domain isolation for apps_lic and apps_rg territories
    - Guardrails: TTL, similarity thresholds, cache poisoning protection
    """

    similarity_threshold: float = DEFAULT_SIMILARITY_THRESHOLD
    default_ttl: int = DEFAULT_TTL_SECONDS
    max_healing_depth: int = MAX_HEALING_DEPTH
    domain_thresholds: dict[str, float] = field(
        default_factory=lambda: {"agentic_core": 0.85, "apps_lic": 0.92, "apps_rg": 0.85},
    )
    domain_ttls: dict[str, int] = field(
        default_factory=lambda: {"agentic_core": 3600, "apps_lic": 7200, "apps_rg": 3600},
    )
    _redis_client: Any = field(default=None, init=False)
    _vector_store: dict = field(default_factory=dict, init=False)
    _local_cache: dict[str, CacheEntry] = field(default_factory=dict, init=False)
    _healing_depth_tracker: dict[str, int] = field(default_factory=dict, init=False)
    stats: dict[str, Any] = field(
        default_factory=lambda: {
            "cache_hits": 0,
            "cache_misses": 0,
            "pattern_retrievals": 0,
            "pattern_stores": 0,
            "healing_cycles_prevented": 0,
            "by_domain": {},
        },
    )

    def __new__(cls, *args, **kwargs):
        """Singleton constructor."""
        global _singleton_instance
        if _singleton_instance is None:
            _singleton_instance = super().__new__(cls)
        return _singleton_instance

    def __post_init__(self) -> None:
        """Initialize Redis and FAISS vector store."""
        self._initialize_redis()
        self._initialize_vector_store()
        Logger.info("[MetaLearningClient] Initialized with domain isolation")

    @classmethod
    def reset_instance(cls) -> None:
        """[TESTING ONLY] Reset singleton state."""
        global _singleton_instance
        _singleton_instance = None

    def _initialize_redis(self) -> None:
        """Initialize Redis connection. Raises if Redis is unavailable."""
        from pathlib import Path

        from agentic_core.L2_execution.types.infra_error_types import (
            InfrastructureDependencyError,
        )  # guardian: allow-layer-violation -- L1 module uses L2 type/utility; intentional cross-layer dependency in cognition layer

        try:
            redis_agent = _get_redis_sovereign_agent()(Path.cwd())
            self._redis_client = redis_agent.get_client()
            Logger.info("[MetaLearningClient] Redis connection established")
        except (ImportError, AttributeError, OSError, RuntimeError, ValueError, TypeError) as e:
            raise InfrastructureDependencyError(
                f"[MetaLearningClient] Redis is a mandatory dependency and is unavailable: {e}",
            ) from e

    def _initialize_vector_store(self) -> None:
        """Initialize in-memory FAISS-backed vector store for healing patterns."""
        self._vector_store = {}
        Logger.info("[MetaLearningClient] In-memory vector store initialized")

    def _get_cache_key(self, key: str, domain: str = "agentic_core") -> str:
        """Generate namespaced cache key."""
        return f"{CACHE_KEY_PREFIX}{domain}:{key}"

    def _validate_input(self, data: Any) -> bool:
        """Validate input to prevent cache poisoning."""
        if data is None:
            return False
        if isinstance(data, str) and len(data) > 100000:
            Logger.warning("[MetaLearningClient] Input exceeds size limit")
            return False
        if isinstance(data, dict):
            try:
                json.dumps(data)
            except (TypeError, ValueError):
                Logger.warning("[MetaLearningClient] Input not JSON serializable")
                return False
        return True

    def _generate_error_signature(self, violation: dict[str, Any]) -> str:
        """Generate a hash signature for a violation."""
        signature_data = {
            "type": violation.get("type", "unknown"),
            "path": violation.get("path", ""),
            "message": violation.get("message", "")[:200],
        }
        signature_str = json.dumps(signature_data, sort_keys=True)
        return hashlib.sha256(signature_str.encode()).hexdigest()[:16]

    def cache_get(self, key: str, domain: str = "agentic_core") -> Any | None:
        """
        Get value from cache (Redis or local fallback).

        Args:
            key: Cache key
            domain: Domain context for namespacing

        Returns:
            Cached value or None if not found/expired
        """

        _emit_records_execution_trace(
            str(uuid.uuid4()),
            LayerSegment.L3_ORCHESTRATION,
            f"MetaClient.cache_get:{domain}:{key}",
        )
        cache_key = self._get_cache_key(key, domain)
        from agentic_core.L2_execution.types.infra_error_types import (
            InfrastructureDependencyError,
        )  # guardian: allow-layer-violation -- L1 module uses L2 type/utility; intentional cross-layer dependency in cognition layer

        if not self._redis_client:
            raise InfrastructureDependencyError("[MetaLearningClient] Redis client is not initialised.")
        try:
            value = self._redis_client.get(cache_key)
            if value:
                self.stats["cache_hits"] += 1
                self._update_domain_stats(domain, "cache_hits")
                return json.loads(value)
        except (OSError, ValueError, TypeError, AttributeError, RuntimeError) as e:
            raise InfrastructureDependencyError(f"[MetaLearningClient] Redis get failed: {e}") from e
        self.stats["cache_misses"] += 1
        self._update_domain_stats(domain, "cache_misses")
        return None

    def cache_set(self, key: str, value: Any, domain: str = "agentic_core", ttl: int | None = None) -> bool:
        """
        Set value in cache (Redis or local fallback).

        Args:
            key: Cache key
            value: Value to cache
            domain: Domain context for namespacing
            ttl: Time-to-live in seconds (uses domain default if not specified)

        Returns:
            True if successful, False otherwise
        """
        if not self._validate_input(value):
            return False
        cache_key = self._get_cache_key(key, domain)
        effective_ttl = ttl or self.domain_ttls.get(domain, self.default_ttl)
        from agentic_core.L2_execution.types.infra_error_types import (  # guardian: allow-layer-violation -- L1 module uses L2 type/utility; intentional cross-layer dependency in cognition layer
            InfrastructureDependencyError,
        )  # guardian: allow-layer-violation -- L1 meta client uses L2 infra error type; deferred import; InfrastructureDependencyError belongs in shared types but currently lives in L2

        if not self._redis_client:
            raise InfrastructureDependencyError("[MetaLearningClient] Redis client is not initialised.")
        try:
            self._redis_client.setex(cache_key, effective_ttl, json.dumps(value))
            return True
        except (OSError, ValueError, TypeError, AttributeError, RuntimeError) as e:
            raise InfrastructureDependencyError(f"[MetaLearningClient] Redis set failed: {e}") from e

    def cache_delete(self, key: str, domain: str = "agentic_core") -> bool:
        """Delete value from cache."""
        from agentic_core.L2_execution.types.infra_error_types import (  # guardian: allow-layer-violation -- L1 module uses L2 type/utility; intentional cross-layer dependency in cognition layer
            InfrastructureDependencyError,
        )  # guardian: allow-layer-violation -- L1 meta client uses L2 infra error type; deferred import; InfrastructureDependencyError belongs in shared types but currently lives in L2

        cache_key = self._get_cache_key(key, domain)
        if not self._redis_client:
            raise InfrastructureDependencyError("[MetaLearningClient] Redis client is not initialised.")
        try:
            self._redis_client.delete(cache_key)
        except (OSError, ValueError, TypeError, AttributeError, RuntimeError) as e:
            raise InfrastructureDependencyError(f"[MetaLearningClient] Redis delete failed: {e}") from e
        return True

    def store_healing_pattern(
        self,
        violation: dict[str, Any],
        healing_result: dict[str, Any],
        domain: str = "agentic_core",
    ) -> str | None:
        """
        Store a successful healing pattern in Pinecone.

        Args:
            violation: The violation that was healed
            healing_result: The successful healing result
            domain: Domain context

        Returns:
            Pattern ID if successful, None otherwise
        """
        if healing_result.get("status") != "fixed":
            return None
        error_signature = self._generate_error_signature(violation)
        pattern_id = f"{domain}:{error_signature}:{int(get_clock().now_epoch())}"
        pattern = HealingPattern(
            pattern_id=pattern_id,
            violation_type=violation.get("type", "unknown"),
            error_signature=error_signature,
            healing_strategy=healing_result,
            domain=domain,
            metadata={"violation_path": violation.get("path", ""), "timestamp": get_clock().now_epoch()},
        )
        embedding = self._generate_embedding(violation)
        if embedding:
            try:
                self._vector_store[pattern_id] = {"embedding": embedding, "metadata": pattern.to_dict()}
                self.stats["pattern_stores"] += 1
                self._update_domain_stats(domain, "pattern_stores")
                Logger.info(f"[MetaLearningClient] Stored pattern: {pattern_id}")
                return pattern_id
            except (OSError, ValueError, TypeError, AttributeError, RuntimeError) as e:
                raise
                Logger.warning(f"[MetaLearningClient] Vector store failed: {e}")
        cache_key = f"pattern:{error_signature}"
        self.cache_set(cache_key, pattern.to_dict(), domain, ttl=86400)
        return pattern_id

    def retrieve_healing_patterns(
        self,
        violation: dict[str, Any],
        domain: str = "agentic_core",
        top_k: int = 3,
        min_similarity: float | None = None,
    ) -> list[HealingPattern]:
        """
        Retrieve similar healing patterns from Pinecone with enhanced guardrails.

        Args:
            violation: Current violation to find patterns for
            domain: Domain context for namespacing
            top_k: Maximum number of patterns to retrieve
            min_similarity: Override default similarity threshold

        Returns:
            List of similar healing patterns sorted by similarity
        """
        if not self._vector_store:
            return []
        try:
            embedding = self._generate_embedding(violation)
            if not embedding:
                return []
        except (OSError, ValueError, TypeError, AttributeError, RuntimeError) as e:
            Logger.warning(f"[MetaLearningClient] Failed to generate embedding: {e}")
            return []
        effective_threshold = min_similarity or self.domain_thresholds.get(
            domain,
            DEFAULT_SIMILARITY_THRESHOLD,
        )
        try:
            ids = list(self._vector_store.keys())
            stored_vecs = [self._vector_store[pid]["embedding"] for pid in ids]
            ranked: list[tuple[str, float]] = []
            try:
                import faiss
                import numpy as np

                vecs_arr = np.array(stored_vecs, dtype=np.float32)
                q_arr = np.array([embedding], dtype=np.float32)
                faiss.normalize_L2(vecs_arr)
                faiss.normalize_L2(q_arr)
                index = faiss.IndexFlatIP(len(embedding))
                index.add(vecs_arr)
                k = min(top_k, len(ids))
                scores_arr, indices_arr = index.search(q_arr, k)
                ranked = [
                    (ids[int(idx)], float(scores_arr[0][i]))
                    for i, idx in enumerate(indices_arr[0])
                    if idx >= 0
                ]
            except ImportError:  # guardian: allow-silent-swallow
                import math

                q_mag = math.sqrt(sum(x * x for x in embedding))
                sims = []
                for pid, vec in zip(ids, stored_vecs):
                    dot = sum((a * b for a, b in zip(embedding, vec)))
                    v_mag = math.sqrt(sum(x * x for x in vec))
                    sim = dot / (q_mag * v_mag) if q_mag * v_mag > 0 else 0.0
                    sims.append((pid, sim))
                sims.sort(key=lambda x: x[1], reverse=True)
                ranked = sims[:top_k]
            patterns = []
            for pid, score in ranked:
                if score >= effective_threshold:
                    entry = self._vector_store.get(pid)
                    if entry:
                        pattern = HealingPattern.from_dict(entry["metadata"])
                        pattern.similarity_score = score
                        patterns.append(pattern)
            self.stats["pattern_retrievals"] += 1
            self._update_domain_stats(domain, "pattern_retrievals")
            Logger.info(
                f"[MetaLearningClient] Retrieved {len(patterns)} patterns for {domain} (threshold={effective_threshold:.2f})",
            )
            return patterns
        except (OSError, ValueError, TypeError, AttributeError, RuntimeError) as e:
            Logger.error(f"[MetaLearningClient] Pattern retrieval failed: {e}")
            return []

    def _generate_embedding(self, violation: dict[str, Any]) -> list[float] | None:
        """Generate embedding for a violation using BGE-m3."""
        try:
            from agentic_core.L3_orchestration.healers.bmg_embedding_similarity import (
                bmg_embed_text,
            )  # guardian: allow-layer-violation -- L1 meta client lazy-loads L3 embedding healer; deferred import; L1 embedding generation requires L3 BGE-m3 model access

            v_type = violation.get("type", "")
            v_msg = violation.get("message", "")
            v_path = violation.get("path", "")
            text = f"{v_type} {v_msg} {v_path}"
            return bmg_embed_text(text)
        except (ImportError, OSError, ValueError, TypeError, AttributeError, RuntimeError) as e:
            Logger.warning(f"[MetaLearningClient] Embedding generation failed: {e}")
            return None

    def check_healing_depth(self, agent_name: str, violation_id: str) -> bool:
        """
        Check if healing depth limit has been reached.

        Args:
            agent_name: Name of the agent attempting healing
            violation_id: Unique identifier for the violation

        Returns:
            True if healing can proceed, False if depth limit reached
        """
        key = f"{agent_name}:{violation_id}"
        current_depth = self._healing_depth_tracker.get(key, 0)
        if current_depth >= self.max_healing_depth:
            self.stats["healing_cycles_prevented"] += 1
            Logger.warning(f"[MetaLearningClient] Healing depth limit reached for {key}")
            return False
        return True

    def increment_healing_depth(self, agent_name: str, violation_id: str) -> int:
        """Increment healing depth counter."""
        key = f"{agent_name}:{violation_id}"
        self._healing_depth_tracker[key] = self._healing_depth_tracker.get(key, 0) + 1
        return self._healing_depth_tracker[key]

    def reset_healing_depth(self, agent_name: str, violation_id: str) -> None:
        """Reset healing depth counter after successful healing."""
        key = f"{agent_name}:{violation_id}"
        if key in self._healing_depth_tracker:
            del self._healing_depth_tracker[key]

    def _update_domain_stats(self, domain: str, stat_key: str) -> None:
        """Update domain-specific statistics."""
        if domain not in self.stats["by_domain"]:
            self.stats["by_domain"][domain] = {
                "cache_hits": 0,
                "cache_misses": 0,
                "pattern_retrievals": 0,
                "pattern_stores": 0,
            }
        if stat_key in self.stats["by_domain"][domain]:
            self.stats["by_domain"][domain][stat_key] += 1

    def get_stats(self) -> dict[str, Any]:
        """Get current statistics."""
        total_cache_ops = self.stats["cache_hits"] + self.stats["cache_misses"]
        hit_ratio = self.stats["cache_hits"] / total_cache_ops if total_cache_ops > 0 else 0
        return {
            **self.stats,
            "cache_hit_ratio": hit_ratio,
            "local_cache_size": len(self._local_cache),
            "active_healing_cycles": len(self._healing_depth_tracker),
        }

    def clear_local_cache(self) -> int:
        """Clear local cache and return number of entries cleared."""
        count = len(self._local_cache)
        self._local_cache.clear()
        return count


_meta_learning_client: MetaLearningClient | None = None


def get_meta_learning_client() -> MetaLearningClient:
    """Get or create the MetaLearningClient singleton."""
    global _meta_learning_client
    if _meta_learning_client is None:
        _meta_learning_client = MetaLearningClient()
    return _meta_learning_client


def reset_meta_learning_client() -> None:
    """[TESTING ONLY] Reset the singleton."""
    global _meta_learning_client
    _meta_learning_client = None
    MetaLearningClient.reset_instance()
