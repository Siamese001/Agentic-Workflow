from __future__ import annotations

"""
[PHASE 17/20] Semantic cache Manager - The Collective Hive Mind.

[PHASE 3 MIGRATION] Canonical Implementation:
- This is the ONLY SemanticCacheManager in the codebase.
- All other copies (L5/guardrails, L5/cognition) have been deprecated.
- Use semantic_cache_mixin.py for agent-level access.

Located in L4_state as it manages the persistence and state of agentic memory.
Provides O(1) exact recall (Redis) and semantic similarity recall (Pinecone).

Phase 17: Initial implementation with Redis + Pinecone
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
from typing import Any

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

    # Compiled regex patterns for PII detection
    PATTERNS = {
        # Email addresses
        "EMAIL": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", re.IGNORECASE),
        # IPv4 addresses
        "IPV4": re.compile(
            r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}"
            r"(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b",
        ),
        # IPv6 addresses (simplified pattern)
        "IPV6": re.compile(
            r"\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b|"
            r"\b(?:[0-9a-fA-F]{1,4}:){1,7}:\b|"
            r"\b(?:[0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}\b|"
            r"\b::(?:[0-9a-fA-F]{1,4}:){0,5}[0-9a-fA-F]{1,4}\b",
        ),
        # OpenAI API keys (sk-...)
        "OPENAI_KEY": re.compile(r"\bsk-[a-zA-Z0-9]{20,}\b"),
        # Anthropic API keys (sk-ant-...)
        "ANTHROPIC_KEY": re.compile(r"\bsk-ant-[a-zA-Z0-9-]{20,}\b"),
        # Generic API keys (api_key=, apikey=, key=)
        "GENERIC_API_KEY": re.compile(
            r'(?:api[_-]?key|apikey|secret[_-]?key|access[_-]?token)\s*[=:]\s*["\']?([a-zA-Z0-9_-]{20,})["\']?',
            re.IGNORECASE,
        ),
        # AWS Access Key IDs
        "AWS_KEY": re.compile(r"\b(?:AKIA|ABIA|ACCA|ASIA)[A-Z0-9]{16}\b"),
        # Credit card numbers (basic pattern - 13-19 digits with optional separators)
        "CREDIT_CARD": re.compile(r"\b(?:\d{4}[- ]?){3,4}\d{1,4}\b"),
        # US Phone numbers
        "PHONE_US": re.compile(r"\b(?:\+1[- ]?)?(?:\([0-9]{3}\)|[0-9]{3})[- ]?[0-9]{3}[- ]?[0-9]{4}\b"),
        # Social Security Numbers
        "SSN": re.compile(r"\b[0-9]{3}[- ]?[0-9]{2}[- ]?[0-9]{4}\b"),
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
    - Layer 2 (Pinecone): Semantic similarity matching (Long-Term DNA - promoted memories)

    Phase 20: Enforces singleton pattern with thread-safe initialization.
    Phase 20+: Configurable compliance, PII sanitization, trace sampling, memory lifecycle.

    configuration:
        HIVE_MIND_STRICT_MODE: "true" raises on failure, "false" degrades gracefully
        HIVE_MIND_TRACE_SAMPLING_RATE: 0.0 to 1.0 - controls trace capture rate
        HIVE_MIND_PROMOTION_THRESHOLD: 0.0 to 1.0 - minimum feedback score for promotion

    Usage:
        cache = SemanticCacheManager.get_instance()
        result = cache.recall(context, namespace)
    """

    _instance: SemanticCacheManager | None = None
    _instance_lock = threading.RLock()

    # Default configuration
    DEFAULT_STRICT_MODE = True
    DEFAULT_TRACE_SAMPLING_RATE = 1.0
    DEFAULT_PROMOTION_THRESHOLD = 0.8
    DEFAULT_WORKING_MEMORY_TTL = 86400  # 24 hours
    DEFAULT_LONG_TERM_TTL = 86400 * 7  # 7 days

    @classmethod
    def get_instance(cls, api_key: str | None = None) -> SemanticCacheManager:
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
    def _create_instance(cls, api_key: str | None = None) -> SemanticCacheManager:
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
        self.api_key = api_key  # unused; BGE embeddings require no API key
        self.similarity_threshold = 0.98  # Strict threshold for auto-action

        # configuration from environment
        self.strict_mode = os.environ.get("HIVE_MIND_STRICT_MODE", "true").lower() == "true"

        self.trace_sampling_rate = float(
            os.environ.get("HIVE_MIND_TRACE_SAMPLING_RATE", str(self.DEFAULT_TRACE_SAMPLING_RATE)),
        )

        self.promotion_threshold = float(
            os.environ.get("HIVE_MIND_PROMOTION_THRESHOLD", str(self.DEFAULT_PROMOTION_THRESHOLD)),
        )

        # Thread safety lock for operations
        self._lock = threading.RLock()

        # Stateless fallback mode (when infrastructure unavailable in non-strict mode)
        self.stateless_mode = False

        # PII Sanitizer
        self.sanitizer = PII_Sanitizer()

        # Layer 1: Redis (Working Memory - Short-Term)
        self.redis_client = None
        self.redis_enabled = False
        self._init_redis()

        # Layer 2: InMemoryVectorStore (Long-Term Memory - DNA)
        self._vector_store: dict[str, dict] = {}
        self.vector_store_enabled = True
        self._init_vector_store()

        # Statistics
        self.stats = {
            "redis_hits": 0,
            "vector_store_hits": 0,
            "cache_misses": 0,
            "cache_stores": 0,
            "traces_sampled": 0,
            "traces_skipped": 0,
            "promotions": 0,
        }

        # Check infrastructure and apply compliance policy
        infrastructure_available = self.redis_enabled or self.vector_store_enabled

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

        # Log initialization status
        if self.redis_enabled:
            Logger.info("[HiveMind] Connected to Working Memory (Redis)")
        else:
            Logger.warning("[HiveMind] Working Memory (Redis) unavailable")

        Logger.info("[HiveMind] Connected to Long-Term Memory (InMemoryVectorStore+BGE)")

        Logger.info(
            f"[HiveMind] Config: strict_mode={self.strict_mode}, "
            f"sampling_rate={self.trace_sampling_rate}, "
            f"promotion_threshold={self.promotion_threshold}",
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
        except Exception as e:
            Logger.warning(f"[HiveMind] Redis connection failed: {e}")
            return e

    def _init_vector_store(self) -> None:
        """Initialize in-memory vector store for semantic matching (BGE-m3 backend)."""
        self._vector_store = {}
        self.vector_store_enabled = True
        Logger.debug("[HiveMind] In-memory vector store initialized (BGE-m3 backend)")

    def _compute_hash(self, context: str, namespace: str) -> str:
        """Compute SHA256 hash for exact matching."""
        key = f"{namespace}:{context}"
        return hashlib.sha256(key.encode()).hexdigest()

    def _get_embedding(self, text: str) -> list[float] | None:
        """Generate BGE-m3 embedding for semantic matching."""
        try:
            from agentic_core.L2_execution.healers.bmg_embedding_similarity import bmg_embed_text

            return bmg_embed_text(text[:2000])
        except Exception as e:
            Logger.warning(f"[HiveMind] BGE embedding failed: {e}")
            return None

    def recall(
        self,
        context: str,
        namespace: str,
    ) -> dict[str, Any] | None:
        """
        Recall a result based on exact or semantic match.

        Args:
            context: The context string to query
            namespace: The namespace (typically agent class name)

        Returns:
            Cached result dict or None if not found
        """
        # Stateless mode check
        if self.stateless_mode:
            return None

        ctx_hash = self._compute_hash(context, namespace)

        # Layer 1: Exact Match (Redis - O(1))
        if self.redis_enabled:
            try:
                cached = self.redis_client.get(f"memory:{ctx_hash}")
                if cached:
                    Logger.debug(f"[HiveMind] Redis HIT for {namespace}")
                    with self._lock:
                        self.stats["redis_hits"] += 1
                    return json.loads(cached)
            except Exception as e:
                Logger.debug(f"[HiveMind] Redis recall failed: {e}")

        # Layer 2: Semantic Match (InMemoryVectorStore+BGE)
        if self.vector_store_enabled and self._vector_store:
            vector = self._get_embedding(context)
            if vector:
                try:
                    import numpy as np

                    q = np.array(vector, dtype=np.float32)
                    q_norm = q / (np.linalg.norm(q) + 1e-8)
                    best_score, best_payload = 0.0, None
                    for entry in self._vector_store.values():
                        if entry.get("namespace") != namespace:
                            continue
                        v = np.array(entry["vector"], dtype=np.float32)
                        v_norm = v / (np.linalg.norm(v) + 1e-8)
                        score = float(np.dot(q_norm, v_norm))
                        if score > best_score:
                            best_score, best_payload = score, entry.get("payload")
                    if best_payload and best_score >= self.similarity_threshold:
                        Logger.info(f"[HiveMind] VectorStore HIT ({best_score:.2f}) for {namespace}")
                        with self._lock:
                            self.stats["vector_store_hits"] += 1
                        return json.loads(best_payload)
                except Exception as e:
                    Logger.debug(f"[HiveMind] VectorStore recall failed: {e}")

        with self._lock:
            self.stats["cache_misses"] += 1
        return None

    def _should_sample_trace(self) -> bool:
        """
        Determine if this trace should be sampled based on sampling rate.

        Returns:
            True if trace should be captured, False if skipped
        """
        if self.trace_sampling_rate >= 1.0:
            return True
        if self.trace_sampling_rate <= 0.0:
            return False
        return random.random() < self.trace_sampling_rate

    def learn(
        self,
        context: str,
        namespace: str,
        result: dict[str, Any],
        feedback_score: float | None = None,
    ) -> None:
        """
        Teach the Hive Mind a new result (Working Memory).

        Stores in Working Memory (Redis) with 24h TTL.
        Does NOT automatically promote to Long-Term Memory (Pinecone).
        Use promote_to_long_term() with explicit feedback_score for DNA promotion.

        Args:
            context: The context string
            namespace: The namespace (typically agent class name)
            result: The result to store
            feedback_score: Optional feedback score (0.0 to 1.0) for promotion consideration
        """
        # Stateless mode check
        if self.stateless_mode:
            return

        # Trace sampling check
        if not self._should_sample_trace():
            with self._lock:
                self.stats["traces_skipped"] += 1
            return

        with self._lock:
            self.stats["traces_sampled"] += 1

        # Sanitize content before storage
        sanitized_context = self.sanitizer.sanitize(context)

        ctx_hash = self._compute_hash(sanitized_context, namespace)

        # Add metadata to result
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

        # Layer 1: Store in Redis (Working Memory - 24h TTL)
        if self.redis_enabled:
            try:
                self.redis_client.setex(
                    f"memory:{ctx_hash}",
                    self.DEFAULT_WORKING_MEMORY_TTL,  # 24 hours
                    payload_json,
                )
            except Exception as e:
                Logger.debug(f"[HiveMind] Redis learn failed: {e}")

        # NOTE: Pinecone storage is handled by promote_to_long_term()
        # Working memory only stores in Redis for 24h

        with self._lock:
            self.stats["cache_stores"] += 1

    async def learn_async(
        self,
        context: str,
        namespace: str,
        result: dict[str, Any],
        feedback_score: float | None = None,
    ) -> None:
        """
        [PHASE 25] Async version of learn for fire-and-forget pattern.
        """
        # Stateless mode check
        if self.stateless_mode:
            return

        # Trace sampling check
        if not self._should_sample_trace():
            with self._lock:
                self.stats["traces_skipped"] += 1
            return

        with self._lock:
            self.stats["traces_sampled"] += 1

        # Sanitize content before storage
        sanitized_context = self.sanitizer.sanitize(context)

        ctx_hash = self._compute_hash(sanitized_context, namespace)

        # Add metadata to result
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

        # Layer 1: Store in Redis (Working Memory - 24h TTL)
        if self.redis_enabled:
            try:
                await self.redis_client.setex(
                    f"memory:{ctx_hash}",
                    self.DEFAULT_WORKING_MEMORY_TTL,  # 24 hours
                    payload_json,
                )
            except Exception as e:
                Logger.debug(f"[HiveMind] Redis async learn failed: {e}")

        with self._lock:
            self.stats["cache_stores"] += 1

    def promote_to_long_term(
        self,
        context: str,
        namespace: str,
        result: dict[str, Any],
        feedback_score: float,
    ) -> bool:
        """
        Promote a memory to Long-Term DNA storage (Pinecone).

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
        # Validate feedback score
        if feedback_score < self.promotion_threshold:
            Logger.debug(
                f"[HiveMind] Promotion rejected: feedback_score={feedback_score} "
                f"< threshold={self.promotion_threshold}",
            )
            return False

        if not self.vector_store_enabled:
            Logger.warning("[HiveMind] Cannot promote: vector store not available")
            return False

        # Sanitize content
        sanitized_context = self.sanitizer.sanitize(context)
        ctx_hash = self._compute_hash(sanitized_context, namespace)

        # Enrich result with promotion metadata
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

        # Generate embedding
        vector = self._get_embedding(sanitized_context)
        if not vector:
            Logger.warning("[HiveMind] Cannot promote: Embedding generation failed")
            return False

        try:
            self._vector_store[ctx_hash] = {
                "vector": vector,
                "namespace": namespace,
                "payload": payload_json,
                "feedback_score": feedback_score,
            }

            # Also extend Redis TTL for promoted memories
            if self.redis_enabled:
                try:
                    self.redis_client.setex(
                        f"memory:{ctx_hash}",
                        self.DEFAULT_LONG_TERM_TTL,  # 7 days
                        payload_json,
                    )
                except Exception:
                    pass  # Redis extension is optional

            with self._lock:
                self.stats["promotions"] += 1

            Logger.info(
                f"[HiveMind] Memory promoted to DNA: {namespace} (feedback_score={feedback_score:.2f})",
            )
            return True

        except Exception as e:
            Logger.error(f"[HiveMind] Promotion failed: {e}")
            return False

    def update_feedback_score(
        self,
        context: str,
        namespace: str,
        feedback_score: float,
    ) -> bool:
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

        # Try to retrieve existing memory from Redis
        if not self.redis_enabled:
            return False

        try:
            cached = self.redis_client.get(f"memory:{ctx_hash}")
            if not cached:
                return False

            result = json.loads(cached)

            # Update metadata
            if "_metadata" not in result:
                result["_metadata"] = {}

            old_score = result["_metadata"].get("feedback_score", 0.0)
            result["_metadata"]["feedback_score"] = feedback_score
            result["_metadata"]["score_updated"] = time.time()

            # Re-store in Redis
            payload_json = json.dumps(result)
            self.redis_client.setex(
                f"memory:{ctx_hash}",
                self.DEFAULT_WORKING_MEMORY_TTL,
                payload_json,
            )

            Logger.debug(f"[HiveMind] Feedback score updated: {old_score:.2f} -> {feedback_score:.2f}")

            # Auto-promote if threshold exceeded
            if feedback_score >= self.promotion_threshold:
                # Remove _metadata for clean promotion
                clean_result = {k: v for k, v in result.items() if k != "_metadata"}
                return self.promote_to_long_term(context, namespace, clean_result, feedback_score)

            return True

        except Exception as e:
            Logger.warning(f"[HiveMind] Feedback update failed: {e}")
            return False

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
                "sampling_rate_actual": (
                    self.stats["traces_sampled"] / total_traces if total_traces > 0 else 0.0
                ),
                "strict_mode": self.strict_mode,
                "stateless_mode": self.stateless_mode,
            }
