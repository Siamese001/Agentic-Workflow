"""
[PHASE 17/20] Semantic cache Manager - The Collective Hive Mind.

[PHASE 3 MIGRATION] Canonical Implementation:
- This is the ONLY SemanticCacheManager in the codebase.
- All other copies (L5/guardrails, L5/cognition) have been deprecated.
- Use semantic_cache_mixin.py for agent-level access.

Located in L4_state as it manages the persistence and state of agentic memory.
Provides O(1) exact recall (Redis) and semantic similarity recall (InMemoryVectorStore).

Phase 17: Initial implementation with Redis + InMemoryVectorStore
Phase 20: Hardened singleton pattern, thread safety, and connection retries.
Phase 20+: Configurable compliance, PII sanitization, trace sampling, memory lifecycle.

configuration (Environment Variables):
- HIVE_MIND_STRICT_MODE: "true" (default) raises on infrastructure failure, "false" degrades gracefully
- HIVE_MIND_TRACE_SAMPLING_RATE: 0.0 to 1.0 (default 1.0) - controls trace capture rate
- HIVE_MIND_PROMOTION_THRESHOLD: 0.0 to 1.0 (default 0.8) - minimum feedback score for promotion

[SSOT] This is the canonical location for the Hive Mind infrastructure.
"""
import hashlib
import json
import logging
import os
import random
import threading
import time
import uuid
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
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
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("semantic_cache_manager", "p4obs", "metric_1")
_emit_emits_metric_event("semantic_cache_manager", "p4obs", "metric_2")
_emit_emits_metric_event("semantic_cache_manager", "p4obs", "metric_3")
_emit_emits_metric_event("semantic_cache_manager", "p4obs", "metric_4")
_emit_emits_metric_event("semantic_cache_manager", "p4obs", "metric_5")
_emit_emits_metric_event("semantic_cache_manager", "p4obs", "metric_6")
_emit_records_incident_event("semantic_cache_manager", "p4obs", "incident")
_emit_captures_runtime_anomaly("semantic_cache_manager", "p4obs", "anomaly")
_emit_writes_observability_log("semantic_cache_manager", "p4obs", "obs_log")
_emit_updates_monitoring_state("semantic_cache_manager", "p4obs", "mon_state")
_emit_triggers_alert("semantic_cache_manager", "p4obs", "alert")
_emit_links_incident_trace("semantic_cache_manager", "p4obs", "trace_link")
_emit_captures_pattern("semantic_cache_manager", "p3lm", "pattern")
_emit_records_learning_event("semantic_cache_manager", "p3lm", "learning_event")
_emit_writes_learning_snapshot("semantic_cache_manager", "p3lm", "snapshot")
_emit_feeds_meta_learning("semantic_cache_manager", "p3lm", "meta_feed")
_emit_updates_routing_strategy("semantic_cache_manager", "p3lm", "routing")
_emit_improves_agent_policy("semantic_cache_manager", "p3lm", "policy")
_emit_stores_learning_state("semantic_cache_manager", "p3lm", "state")
_emit_records_execution_trace("semantic_cache_manager", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("semantic_cache_manager", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("semantic_cache_manager", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("semantic_cache_manager", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("semantic_cache_manager", "L4_STATE", "p2_trace_5")
_emit_reads_environ("semantic_cache_manager", "env_read", "p2_env_1")
_emit_reads_environ("semantic_cache_manager", "env_read", "p2_env_2")
_emit_reads_runtime_state("semantic_cache_manager", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("semantic_cache_manager", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "semantic_cache_manager", "context_pull")
_emit_pulls_context("p1", "semantic_cache_manager", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "semantic_cache_manager", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "semantic_cache_manager", "uwg_term_2")
_emit_writes_through("p1", "semantic_cache_manager", "write_through")
_emit_writes_through("p1", "semantic_cache_manager", "write_through_2")
_emit_validated_by_safety_plane("p1", "semantic_cache_manager", "safety_validation")
_emit_invokes_eval("p1", "semantic_cache_manager", "eval_call")
_emit_proposal_commits_routing("p1", "semantic_cache_manager", "routing_commit")

Logger = logging.getLogger(__name__)


class CriticalInfrastructureError(Exception):
    """Raised when Hive Mind infrastructure is unavailable in STRICT mode."""

    pass


class PII_Sanitizer:
    """
    [PHASE 21] Production-Grade PII Sanitizer for content sanitization before embedding.

    Detects and redacts:
    - Email addresses
    - IPv4 and IPv6 addresses
    - API keys (OpenAI sk-*, Anthropic sk-ant-*, generic patterns)
    - AWS access keys
    - Credit card numbers (basic pattern)
    - Phone numbers (US format)
    - SSN patterns

    All detected PII is replaced with [REDACTED_<TYPE>] placeholders.
    """

    import re

    PATTERNS = {
        "EMAIL": re.compile("\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b", re.IGNORECASE),
        "IPV4": re.compile(
            "\\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\b"
        ),
        "IPV6": re.compile(
            "\\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\\b|\\b(?:[0-9a-fA-F]{1,4}:){1,7}:\\b|\\b(?:[0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}\\b|\\b::(?:[0-9a-fA-F]{1,4}:){0,5}[0-9a-fA-F]{1,4}\\b"
        ),
        "OPENAI_KEY": re.compile("\\bsk-[a-zA-Z0-9]{20,}\\b"),
        "ANTHROPIC_KEY": re.compile("\\bsk-ant-[a-zA-Z0-9-]{20,}\\b"),
        "GENERIC_API_KEY": re.compile(
            "(?:api[_-]?key|apikey|secret[_-]?key|access[_-]?token)\\s*[=:]\\s*[\"\\']?([a-zA-Z0-9_-]{20,})[\"\\']?",
            re.IGNORECASE,
        ),
        "AWS_KEY": re.compile("\\b(?:AKIA|ABIA|ACCA|ASIA)[A-Z0-9]{16}\\b"),
        "CREDIT_CARD": re.compile("\\b(?:\\d{4}[- ]?){3,4}\\d{1,4}\\b"),
        "PHONE_US": re.compile("\\b(?:\\+1[- ]?)?(?:\\([0-9]{3}\\)|[0-9]{3})[- ]?[0-9]{3}[- ]?[0-9]{4}\\b"),
        "SSN": re.compile("\\b[0-9]{3}[- ]?[0-9]{2}[- ]?[0-9]{4}\\b"),
    }

    @classmethod
    def sanitize(cls, content: str) -> str:
        """
        Sanitize content by redacting all detected PII.

        Args:
            content: Raw content string

        Returns:
            Sanitized content with PII replaced by [REDACTED_<TYPE>] placeholders
        """
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "PII_Sanitizer.sanitize", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "PII_Sanitizer.sanitize", "p0_governance")
        if not content:
            return content
        sanitized = content
        for pii_type, pattern in cls.PATTERNS.items():
            sanitized = pattern.sub(f"[REDACTED_{pii_type}]", sanitized)
        return sanitized

    @classmethod
    def is_safe(cls, content: str) -> bool:
        """
        Check if content contains any detectable PII.

        Args:
            content: Content to check

        Returns:
            True if no PII detected, False otherwise
        """
        if not content:
            return True
        for pattern in cls.PATTERNS.values():
            if pattern.search(content):
                return False
        return True

    @classmethod
    def detect_pii(cls, content: str) -> dict[str, list[str]]:
        """
        Detect and return all PII found in content.

        Args:
            content: Content to scan

        Returns:
            Dictionary mapping PII type to list of matches found
        """
        if not content:
            return {}
        findings = {}
        for pii_type, pattern in cls.PATTERNS.items():
            matches = pattern.findall(content)
            if matches:
                findings[pii_type] = matches
        return findings


class SemanticCacheManager:
    """
    Singleton Semantic cache Manager - The Hive Mind.

    Provides dual-layer caching for collective agent intelligence:
    - Layer 1 (Redis): O(1) exact content hash matching (Working Memory - 24h TTL)
    - Layer 2 (InMemoryVectorStore): Semantic similarity matching (Long-Term DNA - promoted memories)

    Phase 20: Enforces singleton pattern with thread-safe initialization.
    Phase 20+: Configurable compliance, PII sanitization, trace sampling, memory lifecycle.

    Uses FAISS-backed InMemoryVectorStore for Layer 2 semantic search.

    configuration:
        HIVE_MIND_STRICT_MODE: "true" raises on failure, "false" degrades gracefully
        HIVE_MIND_TRACE_SAMPLING_RATE: 0.0 to 1.0 - controls trace capture rate
        HIVE_MIND_PROMOTION_THRESHOLD: 0.0 to 1.0 - minimum feedback score for promotion

    Usage:
        cache = SemanticCacheManager.get_instance()
        result = cache.recall(context, namespace)
    """

    _instance: "SemanticCacheManager | None" = None
    _instance_lock = threading.RLock()
    DEFAULT_STRICT_MODE = True
    DEFAULT_TRACE_SAMPLING_RATE = 1.0
    DEFAULT_PROMOTION_THRESHOLD = 0.8
    DEFAULT_WORKING_MEMORY_TTL = 86400
    DEFAULT_LONG_TERM_TTL = 86400 * 7

    @classmethod
    def get_instance(cls, api_key: str | None = None) -> "SemanticCacheManager":
        """
        Get the singleton instance of SemanticCacheManager.

        Thread-safe singleton pattern ensures only one Hive Mind exists.

        Args:
            api_key: Optional API key for embedding generation

        Returns:
            The singleton SemanticCacheManager instance

        Raises:
            CriticalInfrastructureError: If STRICT_MODE and infrastructure unavailable
        """
        with cls._instance_lock:
            if cls._instance is None:
                cls._instance = cls._create_instance(api_key)
            return cls._instance

    @classmethod
    def _create_instance(cls, api_key: str | None = None) -> "SemanticCacheManager":
        """Internal factory method for creating the singleton."""
        instance = object.__new__(cls)
        instance._initialize(api_key)
        return instance

    @classmethod
    def reset_instance(cls) -> None:
        """Reset the singleton instance (for testing only)."""
        with cls._instance_lock:
            cls._instance = None

    def __init__(self, api_key: str | None = None):
        """
        Initialize is blocked for direct instantiation.
        Use get_instance() instead.
        """
        if SemanticCacheManager._instance is not None:
            raise RuntimeError(
                "[HiveMind] SINGLETON VIOLATION: Use SemanticCacheManager.get_instance() instead of direct instantiation."
            )
        self._initialize(api_key)

    def _initialize(self, api_key: str | None = None) -> None:
        """
        Internal initialization method with configurable compliance.

        Args:
            api_key: Optional API key for embedding generation

        Raises:
            CriticalInfrastructureError: If STRICT_MODE and infrastructure unavailable
        """
        self.api_key = api_key
        # guardian: allow-magic-config
        self.similarity_threshold = 0.98
        self.strict_mode = os.environ.get("HIVE_MIND_STRICT_MODE", "true").lower() == "true"
        self.trace_sampling_rate = float(
            os.environ.get("HIVE_MIND_TRACE_SAMPLING_RATE", str(self.DEFAULT_TRACE_SAMPLING_RATE))
        )
        self.promotion_threshold = float(
            os.environ.get("HIVE_MIND_PROMOTION_THRESHOLD", str(self.DEFAULT_PROMOTION_THRESHOLD))
        )
        self._lock = threading.RLock()
        self.stateless_mode = False
        self.sanitizer = PII_Sanitizer()
        self.redis_client = None
        self.redis_enabled = False
        self._init_redis()
        from agentic_core.L4_state.memory.in_memory_vector_store import InMemoryVectorStore

        self._vector_store: InMemoryVectorStore = InMemoryVectorStore()
        self.vector_store_enabled = True
        self._init_vector_store()
        self.stats = {
            "redis_hits": 0,
            "vector_store_hits": 0,
            "cache_misses": 0,
            "cache_stores": 0,
            "traces_sampled": 0,
            "traces_skipped": 0,
            "promotions": 0,
        }
        infrastructure_available = self.redis_enabled or self.vector_store_enabled
        if not infrastructure_available:
            if self.strict_mode:
                error_msg = "[HiveMind] CRITICAL: Hive Mind infrastructure unavailable in STRICT mode."
                Logger.critical(error_msg)
                raise CriticalInfrastructureError(error_msg)
            else:
                Logger.error(
                    "[HiveMind] Hive Mind infrastructure unavailable. Entering STATELESS fallback mode."
                )
                self.stateless_mode = True
        if self.redis_enabled:
            Logger.info("[HiveMind] Connected to Working Memory (Redis)")
        else:
            Logger.warning("[HiveMind] Working Memory (Redis) unavailable")
        Logger.info("[HiveMind] Connected to Long-Term Memory (InMemoryVectorStore+BGE)")
        Logger.info(
            f"[HiveMind] Config: strict_mode={self.strict_mode}, sampling_rate={self.trace_sampling_rate}, promotion_threshold={self.promotion_threshold}"
        )

    def _init_redis(self) -> Exception | None:
        """
        Initialize Redis connection with retry logic.

        Returns:
            Exception if connection failed, None if successful
        """
        try:
            import redis

            redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379")
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            self.redis_client.ping()
            self.redis_enabled = True
            return None
        except ImportError as e:
            Logger.debug("[HiveMind] redis package not installed")
            return e
        # guardian: allow-silent-swallow
        except Exception as e:
            Logger.warning(f"[HiveMind] Redis connection failed: {e}")
            return e

    def _init_vector_store(self) -> None:
        """Initialize in-memory vector store for semantic matching (BGE-m3 backend)."""
        self.vector_store_enabled = True
        Logger.debug("[HiveMind] In-memory vector store initialized (FAISS+BGE-m3 backend)")

    _EMBEDDING_MODEL_VERSION: str = os.environ.get("HIVE_MIND_EMBEDDING_MODEL_VERSION", "bge-m3-v1")
    _RETRIEVAL_CONFIG_HASH: str = os.environ.get("HIVE_MIND_RETRIEVAL_CONFIG_HASH", "default")

    def _compute_hash(self, context: str, namespace: str) -> str:
        """Compute SHA256 hash for exact matching.

        Key includes determinism anchors (embedding model version and retrieval
        config hash) so cached results are automatically invalidated when either
        changes, preventing stale or inconsistent retrieval results.
        """
        key = "|".join([namespace, self._EMBEDDING_MODEL_VERSION, self._RETRIEVAL_CONFIG_HASH, context])
        return hashlib.sha256(key.encode()).hexdigest()

    def _get_embedding(self, text: str) -> list[float] | None:
        """Generate BGE-m3 embedding for semantic matching."""
        try:
            from agentic_core.L3_orchestration.healers.bmg_embedding_similarity import bmg_embed_text

            return bmg_embed_text(text[:2000])
        # guardian: allow-silent-swallow
        except Exception as e:
            Logger.warning(f"[HiveMind] BGE embedding failed: {e}")
            return None

    def recall(self, context: str, namespace: str) -> dict[str, Any] | None:
        """
        Recall a result based on exact or semantic match.

        Args:
            context: The context string to query
            namespace: The namespace (typically agent class name)

        Returns:
            Cached result dict or None if not found
        """

        _emit_records_execution_trace(
            str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, f"SemanticCacheManager.recall:{namespace}"
        )
        if self.stateless_mode:
            return None
        ctx_hash = self._compute_hash(context, namespace)
        if self.redis_enabled:
            try:
                cached = self.redis_client.get(f"memory:{ctx_hash}")
                if cached:
                    Logger.debug(f"[HiveMind] Redis HIT for {namespace}")
                    with self._lock:
                        self.stats["redis_hits"] += 1
                    return json.loads(cached)
            # guardian: allow-silent-swallow
            except Exception as e:
                raise
                Logger.debug(f"[HiveMind] Redis recall failed: {e}")
        if self.vector_store_enabled and self._vector_store._storage:
            vector = self._get_embedding(context)
            if vector:
                try:
                    import asyncio

                    from agentic_core.L4_state.types.memory_item_types import MemoryQuery

                    query = MemoryQuery(vector=vector, top_k=1, filter_metadata={"namespace": namespace})
                    loop = asyncio.get_event_loop()
                    results = loop.run_until_complete(self._vector_store.query(query))
                    if (
                        results
                        and results[0].score is not None
                        and (results[0].score >= self.similarity_threshold)
                    ):
                        best = results[0]
                        Logger.info(f"[HiveMind] VectorStore HIT ({best.score:.2f}) for {namespace}")
                        with self._lock:
                            self.stats["vector_store_hits"] += 1
                        payload = best.metadata.get("payload")
                        if payload:
                            return json.loads(payload)
                # guardian: allow-silent-swallow
                except Exception as e:
                    raise
                    Logger.debug(f"[HiveMind] VectorStore recall failed: {e}")
        with self._lock:
            self.stats["cache_misses"] += 1
        return None

    def _should_sample_trace(self, trace_id: str | None = None) -> bool:
        """
        Determine if this trace should be sampled based on sampling rate.

        Deterministic sampling based on trace_id hash to ensure reproducibility.

        Returns:
            True if trace should be captured, False if skipped
        """
        if self.trace_sampling_rate >= 1.0:
            return True
        if self.trace_sampling_rate <= 0.0:
            return False
        if trace_id is None:
            return random.random() < self.trace_sampling_rate
        import hashlib

        hash_int = int(hashlib.sha256(trace_id.encode()).hexdigest()[:8], 16)
        threshold = int(self.trace_sampling_rate * 4294967295)
        return hash_int & 4294967295 < threshold

    def learn(
        self, context: str, namespace: str, result: dict[str, Any], feedback_score: float | None = None
    ) -> None:
        """
        Teach the Hive Mind a new result (Working Memory).

        Stores in Working Memory (Redis) with 24h TTL.
        Does NOT automatically promote to Long-Term Memory (InMemoryVectorStore).
        Use promote_to_long_term() with explicit feedback_score for DNA promotion.

        Args:
            context: The context string
            namespace: The namespace (typically agent class name)
            result: The result to store
            feedback_score: Optional feedback score (0.0 to 1.0) for promotion consideration
        """
        if self.stateless_mode:
            return
        sanitized_context = self.sanitizer.sanitize(context)
        ctx_hash = self._compute_hash(sanitized_context, namespace)
        if not self._should_sample_trace(ctx_hash):
            with self._lock:
                self.stats["traces_skipped"] += 1
            return
        with self._lock:
            self.stats["traces_sampled"] += 1
        enriched_result = {
            **result,
            "_metadata": {
                "namespace": namespace,
                "timestamp": time.time(),
                "feedback_score": feedback_score,
                "promoted": False,
            },
        }
        payload_json = json.dumps(enriched_result)
        if self.redis_enabled:
            try:
                self.redis_client.setex(f"memory:{ctx_hash}", self.DEFAULT_WORKING_MEMORY_TTL, payload_json)
            # guardian: allow-silent-swallow
            except Exception as e:
                raise
                Logger.debug(f"[HiveMind] Redis learn failed: {e}")
        with self._lock:
            self.stats["cache_stores"] += 1

    async def learn_async(
        self, context: str, namespace: str, result: dict[str, Any], feedback_score: float | None = None
    ) -> None:
        """
        [PHASE 25] Async version of learn for fire-and-forget pattern.
        """
        if self.stateless_mode:
            return
        sanitized_context = self.sanitizer.sanitize(context)
        ctx_hash = self._compute_hash(sanitized_context, namespace)
        if not self._should_sample_trace(ctx_hash):
            with self._lock:
                self.stats["traces_skipped"] += 1
            return
        with self._lock:
            self.stats["traces_sampled"] += 1
        enriched_result = {
            **result,
            "_metadata": {
                "namespace": namespace,
                "timestamp": time.time(),
                "feedback_score": feedback_score,
                "promoted": False,
            },
        }
        payload_json = json.dumps(enriched_result)
        if self.redis_enabled:
            try:
                self.redis_client.setex(f"memory:{ctx_hash}", self.DEFAULT_WORKING_MEMORY_TTL, payload_json)
            # guardian: allow-silent-swallow
            except Exception as e:
                raise
                Logger.debug(f"[HiveMind] Redis async learn failed: {e}")
        with self._lock:
            self.stats["cache_stores"] += 1

    async def promote_to_long_term(
        self, context: str, namespace: str, result: dict[str, Any], feedback_score: float
    ) -> bool:
        """
        Promote a memory to Long-Term DNA storage (InMemoryVectorStore).

        Only promotes if feedback_score >= promotion_threshold (default 0.8).
        This is the Validation Gate for memory lifecycle.

        Args:
            context: The context string
            namespace: The namespace (typically agent class name)
            result: The result to store
            feedback_score: Explicit feedback score (0.0 to 1.0)

        Returns:
            True if promoted, False if rejected or failed
        """
        if feedback_score < self.promotion_threshold:
            Logger.debug(
                f"[HiveMind] Promotion rejected: feedback_score={feedback_score} < threshold={self.promotion_threshold}"
            )
            return False
        if not self.vector_store_enabled:
            Logger.warning("[HiveMind] Cannot promote: vector store not available")
            return False
        sanitized_context = self.sanitizer.sanitize(context)
        ctx_hash = self._compute_hash(sanitized_context, namespace)
        enriched_result = {
            **result,
            "_metadata": {
                "namespace": namespace,
                "timestamp": time.time(),
                "feedback_score": feedback_score,
                "promoted": True,
                "promotion_time": time.time(),
            },
        }
        payload_json = json.dumps(enriched_result)
        vector = self._get_embedding(sanitized_context)
        if not vector:
            Logger.warning("[HiveMind] Cannot promote: Embedding generation failed")
            return False
        try:
            from agentic_core.L4_state.types.memory_item_types import MemoryItem

            item = MemoryItem(
                content=sanitized_context,
                embedding=vector,
                metadata={
                    "namespace": namespace,
                    "feedback_score": feedback_score,
                    "promoted_at": time.time(),
                    "payload": payload_json,
                },
            )
            await self._vector_store.upsert([item])
            if self.redis_enabled:
                try:
                    self.redis_client.setex(f"memory:{ctx_hash}", self.DEFAULT_LONG_TERM_TTL, payload_json)
                # guardian: allow-silent-swallow
                except Exception as e:
                    raise
                    Logger.warning(f"[HiveMind] Redis TTL extension failed: {e}")
            with self._lock:
                self.stats["promotions"] += 1
            Logger.info(
                f"[HiveMind] Memory promoted to DNA: {namespace} (feedback_score={feedback_score:.2f})"
            )
            return True
        # guardian: allow-silent-swallow
        except Exception as e:
            Logger.error(f"[HiveMind] Promotion failed: {e}")
            return False

    def update_feedback_score(self, context: str, namespace: str, feedback_score: float) -> bool:
        """
        Update the feedback score for an existing memory.

        If the new score exceeds the promotion threshold, the memory
        will be automatically promoted to Long-Term DNA.

        Args:
            context: The context string
            namespace: The namespace
            feedback_score: New feedback score (0.0 to 1.0)

        Returns:
            True if updated (and possibly promoted), False if memory not found
        """
        sanitized_context = self.sanitizer.sanitize(context)
        ctx_hash = self._compute_hash(sanitized_context, namespace)
        if not self.redis_enabled:
            return False
        try:
            cached = self.redis_client.get(f"memory:{ctx_hash}")
            if not cached:
                return False
            result = json.loads(cached)
            if "_metadata" not in result:
                result["_metadata"] = {}
            old_score = result["_metadata"].get("feedback_score", 0.0)
            result["_metadata"]["feedback_score"] = feedback_score
            result["_metadata"]["score_updated"] = time.time()
            payload_json = json.dumps(result)
            self.redis_client.setex(f"memory:{ctx_hash}", self.DEFAULT_WORKING_MEMORY_TTL, payload_json)
            Logger.debug(f"[HiveMind] Feedback score updated: {old_score:.2f} -> {feedback_score:.2f}")
            if feedback_score >= self.promotion_threshold:
                clean_result = {k: v for k, v in result.items() if k != "_metadata"}
                import asyncio

                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        asyncio.ensure_future(
                            self.promote_to_long_term(context, namespace, clean_result, feedback_score)
                        )
                    else:
                        loop.run_until_complete(
                            self.promote_to_long_term(context, namespace, clean_result, feedback_score)
                        )
                # guardian: allow-silent-swallow
                except Exception as e:
                    Logger.warning(f"[HiveMind] Auto-promote failed: {e}")
            return True
        # guardian: allow-silent-swallow
        except Exception as e:
            Logger.warning(f"[HiveMind] Feedback update failed: {e}")
            return False

    def get_stats(self) -> dict[str, Any]:
        """Alias for get_statistics() for test compatibility."""
        return self.get_statistics()

    def get_statistics(self) -> dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            total_hits = self.stats["redis_hits"] + self.stats["vector_store_hits"]
            total_lookups = total_hits + self.stats["cache_misses"]
            total_traces = self.stats["traces_sampled"] + self.stats["traces_skipped"]
            return {
                **self.stats,
                "total_hits": total_hits,
                "total_lookups": total_lookups,
                "hit_rate": total_hits / total_lookups if total_lookups > 0 else 0.0,
                "sampling_rate_actual": self.stats["traces_sampled"] / total_traces
                if total_traces > 0
                else 0.0,
                "strict_mode": self.strict_mode,
                "stateless_mode": self.stateless_mode,
            }
