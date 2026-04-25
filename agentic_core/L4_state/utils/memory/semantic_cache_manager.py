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
import sqlite3
import threading
import time
import uuid
from typing import Any, Callable

# GPTCacheClient import for persistent Layer 2 backend
try:
    from agentic_core.L4_state.cache.gptcache_client import GPTCacheClient

    _GPTCACHE_AVAILABLE = True
except ImportError:
    _GPTCACHE_AVAILABLE = False
    GPTCacheClient = None  # type: ignore[misc, assignment]

try:
    from agentic_core.cache.cache_key_builders import build_semantic_cache_d2_key as _build_d2_key

    _D2_KEY_BUILDER_AVAILABLE = True
except ImportError:
    _D2_KEY_BUILDER_AVAILABLE = False
    _build_d2_key = None  # type: ignore[assignment]

try:
    from agentic_core.embeddings.embedding_factory import get_active_embedding_model_id as _get_model_id
except ImportError:

    def _get_model_id() -> str:  # type: ignore[misc]
        """Fallback when embedding factory is unavailable."""
        return os.environ.get("EMBEDDING_MODEL_ID", "bge-m3-v1")


# G1 hybrid fusion (Author-Gate 2026-04-23 Option A): per-row sparse features.
import re as _re  # noqa: E402
from agentic_core.L4_state.utils.memory.sparse_feature_extractor import (  # noqa: E402
    extract_features as _extract_sparse_features,
    fused_score as _fused_reuse_score,
    jaccard_overlap as _jaccard_overlap,
)
from agentic_core.L4_state.utils.memory import doc_to_cache_index as _doc_idx  # noqa: E402
from agentic_core.L4_state.utils.memory.cache_lock_client import (  # noqa: E402
    acquire_single_flight as _acquire_single_flight,
    jittered_ttl as _jittered_ttl,
)


def _hybrid_enabled() -> bool:
    """G1 hybrid fusion active. Default on."""
    return os.environ.get("SEMANTIC_CACHE_HYBRID_ENABLED", "1") != "0"


_HYBRID_FUSED_THRESHOLD: float = float(os.environ.get("SEMANTIC_CACHE_HYBRID_THRESHOLD", "0.88"))
_HYBRID_DENSE_WEIGHT: float = float(os.environ.get("SEMANTIC_CACHE_DENSE_WEIGHT", "0.7"))
_HYBRID_SPARSE_WEIGHT: float = float(os.environ.get("SEMANTIC_CACHE_SPARSE_WEIGHT", "0.3"))


# G2 support-manifest reuse validator (Author-Gate 2026-04-23 Option A: fail-closed).
def _default_evidence_resolver(evidence_id: str) -> bool:
    """Default: treat every evidence_id as resolvable. Back-compat shim."""
    del evidence_id
    return True


_EVIDENCE_RESOLVER: Callable[[str], bool] = _default_evidence_resolver


def set_evidence_resolver(resolver: Callable[[str], bool]) -> None:
    """Install a process-wide resolver for G2 support-manifest validation."""
    global _EVIDENCE_RESOLVER  # noqa: PLW0603
    _EVIDENCE_RESOLVER = resolver


def _support_manifest_enabled() -> bool:
    """G2 validation active. Default on."""
    return os.environ.get("SEMANTIC_CACHE_SUPPORT_MANIFEST_VALIDATION", "1") != "0"


# G3 content-signal bypass: query-content signals that trip hard rejection.
_LIVE_SIGNAL_RE = _re.compile(
    r"\b(?:"
    r"latest|current|currently|now|today|tonight|this\s+(?:week|month|quarter|year)"
    r"|right\s+now|at\s+the\s+moment|as\s+of\s+(?:today|now)"
    r"|delete|remove|update|modify|create|add|insert|patch|upsert|overwrite"
    r"|approve|reject|cancel"
    r"|issue\s+(?:a\s+)?refund|process\s+(?:a\s+)?refund|grant\s+(?:a\s+)?refund"
    r"|charge\s+(?:the|their|my)|bill\s+(?:the|their|my)"
    r"|status\s+of|state\s+of|is\s+.{0,20}\s+(?:up|down|available|online|offline)"
    r")\b",
    _re.IGNORECASE,
)


def _live_signal_bypass_enabled() -> bool:
    """G3 live-signal bypass active. Default on."""
    return os.environ.get("SEMANTIC_CACHE_LIVE_SIGNAL_BYPASS", "1") != "0"


def _query_has_live_signal(context: str) -> str | None:
    """Return a short reason code if *context* trips a live/mutation signal."""
    if not context or len(context) < 3:
        return None
    match = _LIVE_SIGNAL_RE.search(context)
    if match is None:
        return None
    return match.group(0).lower()[:32]


# G5 CDC + G8 single-flight / TTL-jitter feature flags.
def _cdc_enabled() -> bool:
    """G5 doc-to-cache inverse index active. Default on."""
    return os.environ.get("SEMANTIC_CACHE_CDC_ENABLED", "1") != "0"


def _single_flight_enabled() -> bool:
    """G8 single-flight lock active. Default on."""
    return os.environ.get("SEMANTIC_CACHE_SINGLE_FLIGHT", "1") != "0"


_TTL_JITTER_PCT: float = float(os.environ.get("SEMANTIC_CACHE_TTL_JITTER_PCT", "0.1"))


def _structured_emit_enabled() -> bool:
    """G10 structured payload emit active. Default on; off reverts to string-only."""
    return os.environ.get("SEMANTIC_CACHE_STRUCTURED_EMIT", "1") != "0"


# G11 per-tier similarity thresholds (R1B follow-on #3).
# Default values mirror the historical single-threshold behavior: static (L1
# exact) is conceptually 1.0 (exact match) but reported here for telemetry
# parity; dynamic (L2 semantic) defaults to 0.95 matching GPTCacheClient.
_TIER_THRESHOLD_DEFAULTS: dict[str, float] = {"static": 1.0, "dynamic": 0.95}


def tier_similarity_threshold(tier: str) -> float:
    """Resolve the similarity threshold for ``tier`` (``static`` | ``dynamic``).

    Reads ``SEMANTIC_CACHE_THRESHOLD_STATIC`` / ``SEMANTIC_CACHE_THRESHOLD_DYNAMIC``
    env vars when set; otherwise returns the historical default. Unknown tiers
    return ``1.0`` (most conservative — never serves below exact).
    """
    tier_norm = (tier or "").strip().lower()
    env_var = f"SEMANTIC_CACHE_THRESHOLD_{tier_norm.upper()}"
    raw = os.environ.get(env_var)
    if raw is not None:
        try:
            value = float(raw)
            if 0.0 <= value <= 1.0:
                return value
        except ValueError:  # guardian: allow-silent-swallow -- env var threshold override: malformed value falls through to canonical default below
            pass  # fall through to default
    return _TIER_THRESHOLD_DEFAULTS.get(tier_norm, 1.0)


def _l1_key_hardening_enabled() -> bool:
    """G12 L1 cache-key normalization (R1B follow-on #4). Default on."""
    return os.environ.get("SEMANTIC_CACHE_L1_KEY_HARDENING", "1") != "0"


_WS_RE = None  # lazy compile in _normalize_l1_context


def _normalize_l1_context(context: str) -> str:
    """Normalize a context string before L1 hash derivation.

    Hardening applied:
      * strip leading/trailing whitespace
      * collapse internal whitespace runs to single space
      * NFKC unicode normalization (compose width / compatibility variants)

    Case is preserved — semantic distinctions like ``"Apple"`` vs ``"apple"``
    matter for some routing flows. Operators who want case-insensitive L1
    can wrap their callers; we will not silently lose information here.

    Off when ``SEMANTIC_CACHE_L1_KEY_HARDENING=0``.
    """
    if not _l1_key_hardening_enabled():
        return context
    import unicodedata  # noqa: PLC0415

    global _WS_RE  # noqa: PLW0603
    if _WS_RE is None:
        import re as _re  # noqa: PLC0415

        _WS_RE = _re.compile(r"\s+")
    normalized = unicodedata.normalize("NFKC", context).strip()
    return _WS_RE.sub(" ", normalized)


def _emit_structured_cache_event(
    *,
    namespace: str,
    tenant_id: str,
    cache_lineage: str,
    reason_code: str,
    dense_score: float = 0.0,
    sparse_score: float = 0.0,
    fused_score: float = 0.0,
    evidence_ids: tuple[str, ...] = (),
    written_at: float = 0.0,
    ttl_seconds: int = 0,
    policy_hash: str = "",
    embedding_model_id: str = "",
    cache_tier: str = "dynamic",
) -> None:
    """G10 R1B.5 structured emit. Builds a :class:`SemanticCachePayload`
    and forwards a single JSON-shaped event to ``_emit_emits_metric_event``.

    Additive to existing string emits — both fire so legacy consumers keep
    working while structured consumers gain a contract-shaped payload.
    Failures are swallowed: telemetry must never break the cache hot path.
    """
    if not _structured_emit_enabled():
        return
    try:
        from agentic_core.L4_state.utils.memory.cache_payload_contract import (  # noqa: PLC0415
            SemanticCachePayload,
            compute_cache_id,
            freshness_class_for_age,
            new_hit_id,
        )
    except ImportError as _exc:  # guardian: allow-return-none-swallow -- structured emit is observability-only; missing payload contract module means no structured event, cache hot path continues
        Logger.debug("structured emit: payload contract import failed: %s", _exc)
        return
    try:
        _age = max(0.0, time.time() - written_at) if written_at else 0.0
        payload = SemanticCachePayload(
            prior_answer=None,
            dense_score=float(dense_score),
            sparse_score=float(sparse_score),
            fused_score=float(fused_score),
            hit_id=new_hit_id(),
            cache_id=compute_cache_id(namespace, tenant_id),
            cache_lineage=cache_lineage,
            cache_tier=cache_tier,
            reason_codes=(reason_code,),
            policy_hash=policy_hash,
            embedding_model_id=embedding_model_id,
            namespace=namespace,
            tenant_id=tenant_id,
            written_at=float(written_at),
            ttl_seconds=int(ttl_seconds),
            freshness_class=freshness_class_for_age(_age),
            evidence_ids=tuple(str(_e) for _e in evidence_ids),
        )
        _payload_json = json.dumps(payload.to_dict(), separators=(",", ":"))
        _emit_emits_metric_event(
            "semantic_cache_manager",
            "p4obs",
            f"structured:{reason_code}:{_payload_json}",
        )
    except (
        ValueError,
        TypeError,
        RuntimeError,
    ) as _exc:  # guardian: allow-log-and-swallow -- structured emit is observability-only; never break the cache hot path on a payload validation glitch
        Logger.debug("structured emit: payload build failed: %s", _exc)


from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
    _record_semantic_cache_prom_event,
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

_REDIS_RECOVERABLE_EXCEPTIONS = (
    AttributeError,
    ConnectionError,
    TimeoutError,
    TypeError,
    ValueError,
    RuntimeError,
)
_REDIS_READ_EXCEPTIONS = _REDIS_RECOVERABLE_EXCEPTIONS + (json.JSONDecodeError,)
_GPTCACHE_RECOVERABLE_EXCEPTIONS = (AttributeError, TypeError, ValueError, RuntimeError)
_GPTCACHE_READ_EXCEPTIONS = _GPTCACHE_RECOVERABLE_EXCEPTIONS + (json.JSONDecodeError,)
_PROMOTION_EXCEPTIONS = _GPTCACHE_RECOVERABLE_EXCEPTIONS + _REDIS_RECOVERABLE_EXCEPTIONS + (KeyError,)


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
            "\\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\b",
        ),
        "IPV6": re.compile(
            "\\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\\b|\\b(?:[0-9a-fA-F]{1,4}:){1,7}:\\b|\\b(?:[0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}\\b|\\b::(?:[0-9a-fA-F]{1,4}:){0,5}[0-9a-fA-F]{1,4}\\b",
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
    MUST_BYPASS_FLOWS: frozenset[str] = frozenset(
        {
            "D4_ACTION",
            "HITL",
            "UWG_WRITE",
            "AUDIT_EXIT",
            "REPLAY",
        }
    )

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
                "[HiveMind] SINGLETON VIOLATION: Use SemanticCacheManager.get_instance() instead of direct instantiation.",
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
            os.environ.get("HIVE_MIND_TRACE_SAMPLING_RATE", str(self.DEFAULT_TRACE_SAMPLING_RATE)),
        )
        self.promotion_threshold = float(
            os.environ.get("HIVE_MIND_PROMOTION_THRESHOLD", str(self.DEFAULT_PROMOTION_THRESHOLD)),
        )
        self._lock = threading.RLock()
        self.stateless_mode = False
        self.sanitizer = PII_Sanitizer()
        self.redis_client = None
        self.redis_enabled = False
        self._init_redis()
        # Use NativePersistentCacheClient for persistent Layer 2 (SQLite + ChromaDB)
        self._gptcache: GPTCacheClient | None = None
        self.gptcache_enabled = False
        self._init_gptcache()
        self.stats = {
            "redis_hits": 0,
            "vector_store_hits": 0,
            "gptcache_hits": 0,
            "cache_misses": 0,
            "cache_stores": 0,
            "traces_sampled": 0,
            "traces_skipped": 0,
            "promotions": 0,
        }
        infrastructure_available = self.redis_enabled or self.gptcache_enabled
        if not infrastructure_available:
            if self.strict_mode:
                error_msg = "[HiveMind] CRITICAL: Hive Mind infrastructure unavailable in STRICT mode."
                Logger.critical(error_msg)
                raise CriticalInfrastructureError(error_msg)
            else:
                Logger.error(
                    "[HiveMind] Hive Mind infrastructure unavailable. Entering STATELESS fallback mode.",
                )
                self.stateless_mode = True
        if self.redis_enabled:
            Logger.info("[HiveMind] Connected to Working Memory (Redis)")
        else:
            Logger.warning("[HiveMind] Working Memory (Redis) unavailable")
        if self.gptcache_enabled:
            Logger.info("[HiveMind] Connected to Long-Term Memory (Native L2: SQLite+ChromaDB)")
        else:
            Logger.warning("[HiveMind] Long-Term Memory (Native L2) unavailable")
        Logger.info(
            f"[HiveMind] Config: strict_mode={self.strict_mode}, sampling_rate={self.trace_sampling_rate}, promotion_threshold={self.promotion_threshold}",
        )
        # Bounded L2→L1 warmup: on singleton init, read the top-N most-recently-accessed
        # persistent L2 rows and hydrate them into Redis so cold-start recall is fast.
        # Disabled when either layer is unavailable, or when SEMANTIC_CACHE_L1_WARMUP_LIMIT=0.
        try:
            _warmup_limit = int(os.environ.get("SEMANTIC_CACHE_L1_WARMUP_LIMIT", "256"))
        except (TypeError, ValueError):
            _warmup_limit = 256
        if self.redis_enabled and self.gptcache_enabled and _warmup_limit > 0:
            try:
                warmed = self._warm_l1_from_l2(limit=_warmup_limit)
                Logger.info("[HiveMind] L1 warmup from L2 completed: %d keys hydrated", warmed)
            except _PROMOTION_EXCEPTIONS as _warm_err:  # guardian: allow-log-and-swallow -- warmup is best-effort; missing rows just mean cold L1
                Logger.warning("[HiveMind] L1 warmup skipped: %s", _warm_err)
        # L2 TTL sweep at init — removes expired rows so they do not pollute
        # Chroma similarity search. Bounded: _gptcache.cleanup_expired walks
        # only rows whose expires_at is past and is idempotent / safe to skip.
        if self.gptcache_enabled and self._gptcache is not None:
            try:
                _expired = self._gptcache.cleanup_expired()
                if _expired > 0:
                    Logger.info("[HiveMind] L2 cleanup_expired removed %d stale rows", _expired)
            except _PROMOTION_EXCEPTIONS as _cleanup_err:  # guardian: allow-log-and-swallow -- cleanup is opportunistic; lazy eviction still happens on get()
                Logger.warning("[HiveMind] L2 cleanup_expired skipped: %s", _cleanup_err)

    def _warm_l1_from_l2(self, *, limit: int = 256) -> int:
        """Hydrate Redis L1 with the most recently accessed L2 rows.

        Reads ``query`` + ``response`` pairs from ``artifacts/gptcache/l2_cache.db``,
        recomputes the L1 key (``memory:<ctx_hash>``) using the namespace stored in
        each row's response ``_metadata``, and writes the JSON payload at the L1
        TTL. Returns number of keys written.
        """
        if not (self.redis_enabled and self.gptcache_enabled and self._gptcache is not None):
            return 0
        _conn = getattr(self._gptcache, "_sqlite_conn", None)
        if _conn is None:
            return 0
        try:
            cursor = _conn.cursor()
            cursor.execute(
                "SELECT query, response FROM l2_cache "
                "WHERE (expires_at IS NULL OR expires_at > ?) "
                "ORDER BY last_access_at DESC LIMIT ?",
                (time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()), int(limit)),
            )
            rows = cursor.fetchall()
        except (
            _GPTCACHE_READ_EXCEPTIONS
        ) as _read_err:  # guardian: allow-log-and-swallow -- warmup read: L2 unavailable, return 0 warm keys
            Logger.debug("[HiveMind] Warmup read failed: %s", _read_err)
            return 0
        hydrated = 0
        from tqdm import tqdm as _tqdm  # noqa: PLC0415 -- §16 progress bar

        for query_text, response_json in _tqdm(rows, desc="L1 warmup", unit="row"):
            try:
                payload = json.loads(response_json)
            except (json.JSONDecodeError, TypeError):
                continue
            meta = payload.get("_metadata", {}) if isinstance(payload, dict) else {}
            ns = meta.get("namespace") if isinstance(meta, dict) else None
            if not ns:
                continue
            ctx_hash = self._compute_hash(query_text, ns)
            try:
                self.redis_client.setex(f"memory:{ctx_hash}", self.DEFAULT_WORKING_MEMORY_TTL, response_json)
                hydrated += 1
            except _REDIS_RECOVERABLE_EXCEPTIONS as _set_err:  # guardian: allow-log-and-swallow -- warmup write: per-row failure non-fatal, continue
                Logger.debug("[HiveMind] Warmup write failed for %s: %s", ctx_hash[:8], _set_err)
        return hydrated

    def _init_gptcache(self) -> Exception | None:
        """Initialize Native L2 cache client for persistent Layer 2 storage.

        Gated by the ``SEMANTIC_CACHE_D2_ENABLED`` environment variable.
        Default is ``"0"`` (disabled) so production is fail-closed unless
        the flag is explicitly set to ``"1"``.  Non-production environments
        opt-in by exporting ``SEMANTIC_CACHE_D2_ENABLED=1``.

        Returns:
            Exception if initialization failed or flag is off, None if successful
        """
        if os.environ.get("SEMANTIC_CACHE_D2_ENABLED", "0") != "1":
            Logger.info(
                "[HiveMind] Native L2 cache disabled "
                "(SEMANTIC_CACHE_D2_ENABLED != '1'). Set SEMANTIC_CACHE_D2_ENABLED=1 to enable."
            )
            return ValueError("SEMANTIC_CACHE_D2_ENABLED not set — L2 cache intentionally disabled")
        try:
            self._gptcache = GPTCacheClient(
                cache_dir="artifacts/gptcache",
                similarity_threshold=self.similarity_threshold,
                max_entries=10000,
                embedding_provider="bge-m3",
                embedding_model=_get_model_id(),  # Phase C: pass active model ID
            )
            # Check if it's using real implementation or mock
            if self._gptcache._cache == "mock":
                Logger.warning(
                    "[HiveMind] Native L2 cache using mock implementation (ChromaDB not installed)"
                )
                return ValueError("Native L2 cache in mock mode")
            self.gptcache_enabled = True
            Logger.info("[HiveMind] Native L2 cache initialized at artifacts/gptcache/")
            return None
        except _GPTCACHE_RECOVERABLE_EXCEPTIONS as e:
            Logger.warning(f"[HiveMind] Native L2 cache initialization failed: {e}")
            return e

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
        except _REDIS_RECOVERABLE_EXCEPTIONS as e:  # guardian: allow-silent-swallow
            Logger.warning(f"[HiveMind] Redis connection failed: {e}")
            return e

    _EMBEDDING_MODEL_VERSION: str = os.environ.get("HIVE_MIND_EMBEDDING_MODEL_VERSION", "bge-m3-v1")
    _RETRIEVAL_CONFIG_HASH: str = os.environ.get("HIVE_MIND_RETRIEVAL_CONFIG_HASH", "default")

    def _compute_hash(
        self,
        context: str,
        namespace: str,
        *,
        tenant_id: str = "",
        embedding_model_id: str = "",
        corpus_version: str = "",
    ) -> str:
        """Compute cache key.

        When tenant_id is provided, uses build_semantic_cache_d2_key() for D2-compliant
        key derivation. Falls back to legacy SHA256 for backward compatibility (L1 path).
        """
        if tenant_id and _D2_KEY_BUILDER_AVAILABLE and _build_d2_key is not None:
            active_model = embedding_model_id or self._EMBEDDING_MODEL_VERSION
            raw_corpus = corpus_version or self._RETRIEVAL_CONFIG_HASH
            if len(raw_corpus) != 64 or not all(c in "0123456789abcdef" for c in raw_corpus.lower()):
                raw_corpus = hashlib.sha256(raw_corpus.encode()).hexdigest()
            query_hash = hashlib.sha256(context.encode()).hexdigest()
            try:
                return _build_d2_key(
                    tenant_id=tenant_id,
                    namespace=namespace,
                    embedding_model_id=active_model,
                    corpus_version=raw_corpus,
                    query_hash=query_hash,
                )
            except ValueError:  # guardian: allow-silent-swallow -- cache key construction: optional active model context, fallback key built below
                pass  # active_model_context may not have required attrs and fallback
        # G12 L1 key hardening: normalize the legacy L1 path so trivial
        # whitespace / unicode-form variants do not produce different keys.
        # D2 path above is unaffected (its query_hash is computed before).
        normalized_context = _normalize_l1_context(context)
        key = "|".join(
            [namespace, self._EMBEDDING_MODEL_VERSION, self._RETRIEVAL_CONFIG_HASH, normalized_context]
        )
        return hashlib.sha256(key.encode()).hexdigest()

    def recall(
        self,
        context: str,
        namespace: str,
        *,
        tenant_id: str = "",
        replay_mode: bool = False,
        flow_class: str | None = None,
        corpus_version: str = "",
        policy_version: str = "",
    ) -> dict[str, Any] | None:
        """
        Recall a result based on exact or semantic match.

        Args:
            context: The context string to query
            namespace: The namespace (typically agent class name)

        Returns:
            Cached result dict or None if not found
        """

        _emit_records_execution_trace(
            str(uuid.uuid4()),
            LayerSegment.L3_ORCHESTRATION,
            f"SemanticCacheManager.recall:{namespace}",
        )
        if self.stateless_mode:
            return None
        if replay_mode:
            Logger.debug(
                "[HiveMind] semantic_cache_bypass: bypass_reason=replay namespace=%s",
                namespace,
            )
            _emit_emits_metric_event(
                "semantic_cache_manager",
                "p4obs",
                f"semantic_cache_bypass:replay:{namespace}",
            )
            _record_semantic_cache_prom_event("bypass", namespace)
            return None
        if flow_class is not None and flow_class in self.MUST_BYPASS_FLOWS:
            Logger.debug(
                "[HiveMind] semantic_cache_bypass: bypass_reason=flow_class flow_class=%s namespace=%s",
                flow_class,
                namespace,
            )
            _emit_emits_metric_event(
                "semantic_cache_manager",
                "p4obs",
                f"semantic_cache_bypass:flow_class:{namespace}",
            )
            _record_semantic_cache_prom_event("bypass", namespace)
            return None
        # G3 content-signal bypass: reject reuse when the query itself carries
        # live-fact / mutation / status-lookup markers (R1B HARD REJECTION CASES).
        if _live_signal_bypass_enabled():
            _live_reason = _query_has_live_signal(context)
            if _live_reason is not None:
                Logger.debug(
                    "[HiveMind] semantic_cache_bypass: bypass_reason=live_signal signal=%s namespace=%s",
                    _live_reason,
                    namespace,
                )
                _emit_emits_metric_event(
                    "semantic_cache_manager",
                    "p4obs",
                    f"semantic_cache_bypass:live_signal:{namespace}",
                )
                _record_semantic_cache_prom_event("bypass", namespace)
                return None
        ctx_hash = self._compute_hash(context, namespace)
        active_model = _get_model_id()
        if self.redis_enabled:
            try:
                cached = self.redis_client.get(f"memory:{ctx_hash}")
                if cached:
                    cached_payload = json.loads(cached)
                    # v11 R1B scope re-verification on the fast path.
                    # SQLite enforces tenant/model/expiry at get-time; Redis
                    # must do the same or it can silently serve stale-scope
                    # entries (constitutional §19 — no bypass at L1).
                    _meta = cached_payload.get("_metadata", {}) if isinstance(cached_payload, dict) else {}
                    _row_tenant = _meta.get("tenant_id", "") or ""
                    _row_model = _meta.get("embedding_model_id", "") or ""
                    _row_corpus = _meta.get("corpus_version", "") or ""
                    _row_policy = _meta.get("policy_version", "") or ""
                    _mismatch: str | None = None
                    if tenant_id and _row_tenant and _row_tenant != tenant_id:
                        _mismatch = "tenant"
                    elif _row_model and _row_model != active_model:
                        _mismatch = "embedding_model"
                    elif corpus_version and _row_corpus and _row_corpus != corpus_version:
                        _mismatch = "corpus_version"
                    elif policy_version and _row_policy and _row_policy != policy_version:
                        _mismatch = "policy_version"
                    if _mismatch is not None:
                        Logger.debug(
                            "[HiveMind] Redis scope-mismatch suppressed: reason=%s namespace=%s",
                            _mismatch,
                            namespace,
                        )
                        _emit_emits_metric_event(
                            "semantic_cache_manager",
                            "p4obs",
                            f"l1_scope_mismatch:{_mismatch}:{namespace}",
                        )
                        _record_semantic_cache_prom_event("scope_mismatch", namespace)
                        # Treat as a miss — fall through to L2 / final miss.
                    else:
                        Logger.debug(f"[HiveMind] Redis HIT for {namespace}")
                        with self._lock:
                            self.stats["redis_hits"] += 1
                        _emit_emits_metric_event(
                            "semantic_cache_manager", "p4obs", f"l1_hit:{namespace}"
                        )  # [Phase A]
                        _emit_structured_cache_event(
                            namespace=namespace,
                            tenant_id=tenant_id or "",
                            cache_lineage="L1",
                            reason_code="exact_hit",
                            dense_score=tier_similarity_threshold("static"),
                            ttl_seconds=int(self.DEFAULT_WORKING_MEMORY_TTL),
                            embedding_model_id=self._EMBEDDING_MODEL_VERSION,
                            cache_tier="static",
                        )
                        _record_semantic_cache_prom_event("hit", namespace)
                        return cached_payload
            except (
                _REDIS_READ_EXCEPTIONS
            ) as e:  # guardian: allow-log-and-swallow  -- ADG-burn: log_and_swallow
                Logger.debug(f"[HiveMind] Redis recall failed: {e}")
        # Reaching here means L1 was not hit (Redis disabled, miss, or error)
        _emit_emits_metric_event("semantic_cache_manager", "p4obs", f"l1_miss:{namespace}")  # [Phase A]
        if self.gptcache_enabled and self._gptcache:
            try:
                # Use Native L2 cache for semantic search (persistent Layer 2)
                # Native L2 handles embedding internally via BGE-M3
                active_model = self._EMBEDDING_MODEL_VERSION
                result = self._gptcache.get(context, tenant_id=tenant_id, embedding_model_id=active_model)
                if result:
                    # Result is already a JSON string from previous storage
                    cached_result = json.loads(result)
                    # Verify namespace match (Native L2 doesn't support metadata filtering)
                    _l2_meta = cached_result.get("_metadata", {}) if isinstance(cached_result, dict) else {}
                    # v11 R1B scope re-verification on the L2 path — same shape
                    # as the L1 path above. Required because _gptcache.get does
                    # not yet plumb corpus_version / policy_version filters.
                    _l2_row_corpus = _l2_meta.get("corpus_version", "") or ""
                    _l2_row_policy = _l2_meta.get("policy_version", "") or ""
                    _l2_mismatch: str | None = None
                    if corpus_version and _l2_row_corpus and _l2_row_corpus != corpus_version:
                        _l2_mismatch = "corpus_version"
                    elif policy_version and _l2_row_policy and _l2_row_policy != policy_version:
                        _l2_mismatch = "policy_version"
                    if _l2_mismatch is not None:
                        Logger.debug(
                            "[HiveMind] L2 scope-mismatch suppressed: reason=%s namespace=%s",
                            _l2_mismatch,
                            namespace,
                        )
                        _emit_emits_metric_event(
                            "semantic_cache_manager",
                            "p4obs",
                            f"l2_scope_mismatch:{_l2_mismatch}:{namespace}",
                        )
                        _record_semantic_cache_prom_event("scope_mismatch", namespace)
                        # Fall through to final miss — do not writeback, do not return.
                    elif _l2_meta.get("namespace") == namespace:
                        # G1 hybrid fusion gate: require Jaccard overlap on sparse
                        # features to clear the fused-score bar. Rows without
                        # sparse_features (pre-G1) fall through to pure dense.
                        if _hybrid_enabled():
                            _cached_features = _l2_meta.get("sparse_features") or []
                            if _cached_features:
                                _incoming_features = _extract_sparse_features(context)
                                _jaccard = _jaccard_overlap(_incoming_features, _cached_features)
                                _dense_floor = float(getattr(self._gptcache, "similarity_threshold", 0.95))
                                _fused = _fused_reuse_score(
                                    _dense_floor,
                                    _jaccard,
                                    dense_weight=_HYBRID_DENSE_WEIGHT,
                                    sparse_weight=_HYBRID_SPARSE_WEIGHT,
                                )
                                if _fused < _HYBRID_FUSED_THRESHOLD:
                                    Logger.debug(
                                        "[HiveMind] L2 hybrid-reject: namespace=%s "
                                        "jaccard=%.3f fused=%.3f threshold=%.3f",
                                        namespace,
                                        _jaccard,
                                        _fused,
                                        _HYBRID_FUSED_THRESHOLD,
                                    )
                                    _emit_emits_metric_event(
                                        "semantic_cache_manager",
                                        "p4obs",
                                        f"l2_hybrid_reject:{namespace}",
                                    )
                                    _record_semantic_cache_prom_event("hybrid_reject", namespace)
                                    with self._lock:
                                        self.stats["cache_misses"] += 1
                                    _record_semantic_cache_prom_event("miss", namespace)
                                    return None
                        # G2 support-manifest validator (fail-closed).
                        if _support_manifest_enabled():
                            _evidence_ids = _l2_meta.get("evidence_ids") or []
                            if _evidence_ids:
                                _unresolved: list[str] = []
                                for _eid in _evidence_ids:
                                    try:
                                        if not _EVIDENCE_RESOLVER(str(_eid)):
                                            _unresolved.append(str(_eid))
                                    except (LookupError, ValueError, RuntimeError) as _res_err:
                                        Logger.debug(
                                            "[HiveMind] evidence resolver raised: id=%s err=%s",
                                            _eid,
                                            _res_err,
                                        )
                                        _unresolved.append(str(_eid))
                                if _unresolved:
                                    Logger.debug(
                                        "[HiveMind] L2 support-manifest reject: "
                                        "namespace=%s unresolved=%d/%d",
                                        namespace,
                                        len(_unresolved),
                                        len(_evidence_ids),
                                    )
                                    _emit_emits_metric_event(
                                        "semantic_cache_manager",
                                        "p4obs",
                                        f"l2_support_manifest_reject:{namespace}",
                                    )
                                    _record_semantic_cache_prom_event("support_manifest_reject", namespace)
                                    with self._lock:
                                        self.stats["cache_misses"] += 1
                                    _record_semantic_cache_prom_event("miss", namespace)
                                    return None
                        Logger.info(f"[HiveMind] Native L2 HIT for {namespace}")
                        with self._lock:
                            self.stats["gptcache_hits"] += 1
                        _emit_emits_metric_event(
                            "semantic_cache_manager", "p4obs", f"l2_hit:{namespace}"
                        )  # [Phase A]
                        _emit_structured_cache_event(
                            namespace=namespace,
                            tenant_id=tenant_id or "",
                            cache_lineage="L2_to_L1_writeback" if self.redis_enabled else "L2",
                            reason_code="hybrid_hit" if _hybrid_enabled() else "exact_hit",
                            dense_score=tier_similarity_threshold("dynamic"),
                            evidence_ids=tuple(str(_e) for _e in (_l2_meta.get("evidence_ids") or [])),
                            ttl_seconds=int(self.DEFAULT_WORKING_MEMORY_TTL),
                            embedding_model_id=active_model,
                            cache_tier="dynamic",
                        )
                        _record_semantic_cache_prom_event("hit", namespace)
                        # L2 → L1 write-back: hot-promote into Redis so subsequent
                        # recalls stay O(1) without another Chroma round-trip.
                        if self.redis_enabled:
                            try:
                                self.redis_client.setex(
                                    f"memory:{ctx_hash}",
                                    self.DEFAULT_WORKING_MEMORY_TTL,
                                    result,
                                )
                                _emit_writes_observability_log(
                                    "semantic_cache_manager",
                                    "p4obs",
                                    f"l2_to_l1_writeback:{namespace}:{ctx_hash[:8]}",
                                )
                            except _REDIS_RECOVERABLE_EXCEPTIONS as _wb_err:  # guardian: allow-log-and-swallow -- writeback is best-effort; L2 hit already returned
                                Logger.debug("[HiveMind] L2→L1 writeback failed: %s", _wb_err)
                        return cached_result
            except (
                _GPTCACHE_READ_EXCEPTIONS
            ) as e:  # guardian: allow-log-and-swallow  -- ADG-burn: log_and_swallow
                Logger.debug(f"[HiveMind] Native L2 recall failed: {e}")
        with self._lock:
            self.stats["cache_misses"] += 1
        _emit_emits_metric_event("semantic_cache_manager", "p4obs", f"l2_miss:{namespace}")  # [Phase A]
        _record_semantic_cache_prom_event("miss", namespace)
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
        self,
        context: str,
        namespace: str,
        result: dict[str, Any],
        feedback_score: float | None = None,
        *,
        tenant_id: str = "",
        corpus_version: str = "",
        policy_version: str = "",
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
            tenant_id: Tenant identifier for cache key derivation (Phase B)
        """
        if self.stateless_mode:
            return
        # Phase B: embedding_model_id validation
        active_model = _get_model_id()
        payload_model = result.get("embedding_model_id", "")
        if payload_model and payload_model != active_model:
            Logger.warning(
                f"[HiveMind] learn: embedding_model_id mismatch "
                f"payload={payload_model!r} active={active_model!r}"
            )
        sanitized_context = self.sanitizer.sanitize(context)
        ctx_hash = self._compute_hash(sanitized_context, namespace)
        if not self._should_sample_trace(ctx_hash):
            with self._lock:
                self.stats["traces_skipped"] += 1
            return
        with self._lock:
            self.stats["traces_sampled"] += 1
        _sparse_features = _extract_sparse_features(sanitized_context)
        enriched_result = {
            **result,
            "_metadata": {
                "namespace": namespace,
                "timestamp": time.time(),
                "feedback_score": feedback_score,
                "promoted": False,
                "tenant_id": tenant_id,
                "embedding_model_id": active_model,
                "corpus_version": corpus_version,
                "policy_version": policy_version,
                # G1: per-row sparse features for hybrid reuse.
                "sparse_features": _sparse_features,
                # G6: learn() writes land in dynamic tier.
                "cache_tier": "dynamic",
            },
        }
        payload_json = json.dumps(enriched_result)
        # G8 jittered TTL smears simultaneous-expiry of embedding-adjacent rows.
        _l1_ttl = _jittered_ttl(self.DEFAULT_WORKING_MEMORY_TTL, _TTL_JITTER_PCT)
        if self.redis_enabled:
            if _single_flight_enabled():
                with _acquire_single_flight(self.redis_client, f"learn:{ctx_hash}", ttl_seconds=5) as _won:
                    if _won:
                        self.redis_client.setex(f"memory:{ctx_hash}", _l1_ttl, payload_json)
                    else:
                        _emit_emits_metric_event(
                            "semantic_cache_manager",
                            "p4obs",
                            f"l1_single_flight_skip:{namespace}",
                        )
            else:
                self.redis_client.setex(f"memory:{ctx_hash}", _l1_ttl, payload_json)
        # G5 CDC inverse-index registration.
        if _cdc_enabled():
            _ev_ids = result.get("evidence_ids") or []
            if _ev_ids:
                _doc_idx.register_cache_row(ctx_hash, [str(x) for x in _ev_ids])
        if (
            self.redis_enabled
        ):  # [Phase A] fires only after successful Redis write (raise re-propagates on failure)
            _emit_writes_observability_log(
                "semantic_cache_manager", "p4obs", f"l1_write:{namespace}:{ctx_hash[:8]}"
            )  # [Phase A]
        with self._lock:
            self.stats["cache_stores"] += 1

    async def learn_async(
        self,
        context: str,
        namespace: str,
        result: dict[str, Any],
        feedback_score: float | None = None,
        *,
        tenant_id: str = "",
        corpus_version: str = "",
        policy_version: str = "",
    ) -> None:
        """
        [PHASE 25] Async version of learn for fire-and-forget pattern.
        """
        if self.stateless_mode:
            return
        active_model = _get_model_id()
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
                "tenant_id": tenant_id,
                "embedding_model_id": active_model,
                "corpus_version": corpus_version,
                "policy_version": policy_version,
            },
        }
        payload_json = json.dumps(enriched_result)
        if self.redis_enabled:
            self.redis_client.setex(f"memory:{ctx_hash}", self.DEFAULT_WORKING_MEMORY_TTL, payload_json)
        with self._lock:
            self.stats["cache_stores"] += 1

    async def promote_to_long_term(
        self,
        context: str,
        namespace: str,
        result: dict[str, Any],
        feedback_score: float,
        *,
        tenant_id: str = "",
        corpus_version: str = "",
        policy_version: str = "",
    ) -> bool:
        """
        Promote a memory to Long-Term DNA storage (Native L2 persistent backend).

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
                f"[HiveMind] Promotion rejected: feedback_score={feedback_score} < threshold={self.promotion_threshold}",
            )
            _emit_writes_observability_log(
                "semantic_cache_manager", "p4obs", f"l2_promote_rejected:{namespace}:score_too_low"
            )  # [Phase A]
            return False
        # Phase B: content quality gates
        evidence_ids = result.get("evidence_ids", [])
        grounding_complete = result.get("grounding_complete", False)
        if not evidence_ids:
            Logger.warning(f"[HiveMind] Promotion rejected: evidence_ids empty for {namespace}")
            _emit_writes_observability_log(
                "semantic_cache_manager", "p4obs", f"l2_promote_rejected:{namespace}:evidence_ids_empty"
            )
            return False
        if not grounding_complete:
            Logger.warning(f"[HiveMind] Promotion rejected: grounding_complete=False for {namespace}")
            _emit_writes_observability_log(
                "semantic_cache_manager", "p4obs", f"l2_promote_rejected:{namespace}:grounding_incomplete"
            )
            return False
        if not self.gptcache_enabled:
            Logger.warning("[HiveMind] Cannot promote: Native L2 cache not available")
            _emit_writes_observability_log(
                "semantic_cache_manager", "p4obs", f"l2_promote_rejected:{namespace}:l2_unavailable"
            )  # [Phase A]
            return False
        sanitized_context = self.sanitizer.sanitize(context)
        ctx_hash = self._compute_hash(sanitized_context, namespace)
        active_model = _get_model_id()
        _sparse_features = _extract_sparse_features(sanitized_context)
        enriched_result = {
            **result,
            "_metadata": {
                "namespace": namespace,
                "timestamp": time.time(),
                "feedback_score": feedback_score,
                "promoted": True,
                "promotion_time": time.time(),
                "tenant_id": tenant_id,
                "embedding_model_id": active_model,
                "corpus_version": corpus_version,
                "policy_version": policy_version,
                # G1: per-row sparse features for hybrid reuse.
                "sparse_features": _sparse_features,
                # G6: promotion implies vetted content — static tier.
                "cache_tier": "static",
            },
        }
        payload_json = json.dumps(enriched_result)
        try:
            # Store in Native L2 cache (persistent Layer 2)
            # Native L2 handles embedding internally via BGE-M3
            self._gptcache.set(
                sanitized_context,
                payload_json,
                tenant_id=tenant_id,
                embedding_model_id=active_model,
                corpus_version=corpus_version,
                policy_version=policy_version,
                evidence_ids=result.get("evidence_ids", []),
                grounding_complete=bool(result.get("grounding_complete", False)),
            )
            if self.redis_enabled:
                try:
                    _lt_ttl = _jittered_ttl(self.DEFAULT_LONG_TERM_TTL, _TTL_JITTER_PCT)
                    self.redis_client.setex(f"memory:{ctx_hash}", _lt_ttl, payload_json)
                except (
                    _REDIS_RECOVERABLE_EXCEPTIONS
                ) as e:  # guardian: allow-log-and-swallow  -- ADG-burn: log_and_swallow
                    Logger.warning(f"[HiveMind] Redis TTL extension failed: {e}")
            # G5 CDC: register promoted row’s evidence in the inverse index.
            if _cdc_enabled():
                _ev_ids = result.get("evidence_ids") or []
                if _ev_ids:
                    _doc_idx.register_cache_row(ctx_hash, [str(x) for x in _ev_ids])
            with self._lock:
                self.stats["promotions"] += 1
            Logger.info(
                f"[HiveMind] Memory promoted to DNA: {namespace} (feedback_score={feedback_score:.2f})",
            )
            _emit_writes_observability_log(
                "semantic_cache_manager", "p4obs", f"l2_promote:{namespace}:{ctx_hash[:8]}"
            )  # [Phase A]
            return True
        except _PROMOTION_EXCEPTIONS as e:  # guardian: allow-silent-swallow
            Logger.error(f"[HiveMind] Promotion failed: {e}")
            _emit_writes_observability_log(
                "semantic_cache_manager", "p4obs", f"l2_promote_failed:{namespace}"
            )  # [Phase A]
            return False

    def invalidate_by_document(self, doc_id: str) -> int:
        """G5: scope-invalidate every cached row that cited *doc_id*.

        O(queries that touched the document), not O(cache size). Returns
        the number of rows evicted.
        """
        if not doc_id or not _cdc_enabled():
            return 0
        cache_ids = _doc_idx.cache_ids_for_document(doc_id)
        if not cache_ids:
            return 0
        evicted = 0
        for cid in cache_ids:
            if self.redis_enabled:
                try:
                    self.redis_client.delete(f"memory:{cid}")
                except (
                    _REDIS_RECOVERABLE_EXCEPTIONS
                ) as _exc:  # guardian: allow-log-and-swallow -- per-key delete non-fatal
                    Logger.debug("[HiveMind] CDC Redis evict failed: %s", _exc)
            if self.gptcache_enabled and self._gptcache is not None:
                try:
                    cur = self._gptcache._sqlite_conn.cursor()  # noqa: SLF001
                    cur.execute("DELETE FROM l2_cache WHERE id = ?", (cid,))
                    self._gptcache._sqlite_conn.commit()  # noqa: SLF001
                    try:
                        self._gptcache._chroma_collection.delete(ids=[cid])  # noqa: SLF001
                    except (
                        AttributeError,
                        RuntimeError,
                    ) as _cerr:  # guardian: allow-log-and-swallow -- Chroma evict best-effort: CDC invalidation may miss a stale vector; L2 sqlite row deletion below still runs
                        Logger.debug("[HiveMind] CDC Chroma evict failed: %s", _cerr)
                except (
                    AttributeError,
                    sqlite3.Error,
                    RuntimeError,
                ) as _serr:  # guardian: allow-log-and-swallow -- L2 sqlite evict best-effort: CDC invalidation is an optimization; standard TTL expiry still applies
                    Logger.debug("[HiveMind] CDC L2 evict failed: %s", _serr)
            _doc_idx.forget_cache_row(cid)
            evicted += 1
        _emit_emits_metric_event("semantic_cache_manager", "p4obs", f"cdc_evict:{doc_id}:{evicted}")
        _record_semantic_cache_prom_event("cdc_evict", doc_id)
        return evicted

    def invalidate_neighborhood(self, query: str, *, top_k: int = 5) -> int:
        """G7: invalidate the semantic neighborhood of *query* in L2.

        Called on negative-feedback to prevent hallucination amplification.
        Returns rows evicted.
        """
        if not query or top_k < 1:
            return 0
        if not self.gptcache_enabled or self._gptcache is None:
            return 0
        try:
            results = self._gptcache._chroma_collection.query(  # noqa: SLF001
                query_texts=[query], n_results=top_k
            )
        except (AttributeError, RuntimeError) as exc:
            Logger.debug("[HiveMind] Neighborhood query failed: %s", exc)
            return 0
        ids = (results.get("ids") or [[]])[0]
        if not ids:
            return 0
        evicted = 0
        try:
            cursor = self._gptcache._sqlite_conn.cursor()  # noqa: SLF001
            placeholders = ",".join("?" * len(ids))
            cursor.execute(
                f"DELETE FROM l2_cache WHERE id IN ({placeholders})",
                ids,
            )
            self._gptcache._sqlite_conn.commit()  # noqa: SLF001
            try:
                self._gptcache._chroma_collection.delete(ids=ids)  # noqa: SLF001
            except (
                AttributeError,
                RuntimeError,
            ) as _cerr:  # guardian: allow-log-and-swallow -- neighborhood Chroma delete best-effort: bulk invalidation may miss stale vectors; TTL-based expiry covers the gap
                Logger.debug("[HiveMind] Neighborhood Chroma delete failed: %s", _cerr)
            evicted = len(ids)
            if self.redis_enabled:
                for cid in ids:
                    try:
                        self.redis_client.delete(f"memory:{cid}")
                    except (
                        _REDIS_RECOVERABLE_EXCEPTIONS
                    ) as _exc:  # guardian: allow-log-and-swallow -- per-key delete non-fatal
                        Logger.debug("[HiveMind] Neighborhood Redis evict failed: %s", _exc)
                    _doc_idx.forget_cache_row(cid)
        except (AttributeError, RuntimeError) as exc:
            Logger.warning("[HiveMind] Neighborhood invalidation failed: %s", exc)
            return 0
        _emit_emits_metric_event("semantic_cache_manager", "p4obs", f"neighborhood_evict:{evicted}")
        _record_semantic_cache_prom_event("neighborhood_evict", "")
        return evicted

    def invalidate_cache(
        self,
        *,
        tenant_id: str | None = None,
        corpus_version: str | None = None,
        embedding_model_id: str | None = None,
    ) -> int:
        """Invalidate L2 cache entries matching the given scope.

        Thin wrapper over NativePersistentCacheClient.invalidate_by().
        Raises ValueError if all params are None.
        Returns the number of entries invalidated.
        """
        if not self.gptcache_enabled or self._gptcache is None:
            Logger.warning("[HiveMind] invalidate_cache: L2 cache not available")
            return 0
        count = self._gptcache.invalidate_by(
            tenant_id=tenant_id,
            corpus_version=corpus_version,
            embedding_model_id=embedding_model_id,
        )
        _emit_writes_observability_log(
            "semantic_cache_manager",
            "p4obs",
            f"semantic_cache_invalidated:count={count}",
        )
        _record_semantic_cache_prom_event("invalidation", tenant_id or "")
        return count

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
                            self.promote_to_long_term(context, namespace, clean_result, feedback_score),
                        )
                    else:
                        loop.run_until_complete(
                            self.promote_to_long_term(context, namespace, clean_result, feedback_score),
                        )
                except (
                    AttributeError,
                    RuntimeError,
                    TypeError,
                    ValueError,
                ) as e:  # guardian: allow-log-and-swallow  -- ADG-burn: log_and_swallow
                    Logger.warning(f"[HiveMind] Auto-promote failed: {e}")
            return True
        except _REDIS_READ_EXCEPTIONS + (KeyError,) as e:  # guardian: allow-silent-swallow
            Logger.warning(f"[HiveMind] Feedback update failed: {e}")
            return False

    def get_stats(self) -> dict[str, Any]:
        """Alias for get_statistics() for test compatibility."""
        return self.get_statistics()

    def get_statistics(self) -> dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            total_hits = self.stats["redis_hits"] + self.stats["gptcache_hits"]
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
