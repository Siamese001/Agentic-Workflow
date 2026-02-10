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

from __future__ import annotations

import hashlib
import json
import logging
import time
from dataclasses import dataclass, field
from typing import Any

from agentic_core.L1_cognition.types.client_types import (
    CACHE_KEY_PREFIX,
    DEFAULT_SIMILARITY_THRESHOLD,
    DEFAULT_TTL_SECONDS,
    MAX_HEALING_DEPTH,
    PINECONE_NAMESPACE_PREFIX,
    CacheEntry,
    HealingPattern,
)

Logger = logging.getLogger(__name__)


# Module-level singleton instance
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

    # Configuration
    similarity_threshold: float = DEFAULT_SIMILARITY_THRESHOLD
    default_ttl: int = DEFAULT_TTL_SECONDS
    max_healing_depth: int = MAX_HEALING_DEPTH

    # Domain-specific thresholds (from existing base agents)
    domain_thresholds: dict[str, float] = field(
        default_factory=lambda: {
            "agentic_core": 0.85,
            "apps_lic": 0.92,
            "apps_rg": 0.85,
        },
    )

    # Domain-specific TTLs
    domain_ttls: dict[str, int] = field(
        default_factory=lambda: {
            "agentic_core": 3600,  # 1 hour
            "apps_lic": 7200,  # 2 hours
            "apps_rg": 3600,  # 1 hour
        },
    )

    # State
    _redis_client: Any = field(default=None, init=False)
    _pinecone_client: Any = field(default=None, init=False)
    _pinecone_index: Any = field(default=None, init=False)
    _local_cache: dict[str, CacheEntry] = field(default_factory=dict, init=False)
    _healing_depth_tracker: dict[str, int] = field(default_factory=dict, init=False)

    # Statistics
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
        """Initialize Redis and Pinecone connections."""
        self._initialize_redis()
        self._initialize_pinecone()
        Logger.info("[MetaLearningClient] Initialized with domain isolation")

    @classmethod
    def reset_instance(cls) -> None:
        """[TESTING ONLY] Reset singleton state."""
        global _singleton_instance
        _singleton_instance = None

    def _initialize_redis(self) -> None:
        """Initialize Redis connection with fallback to local cache."""
        try:
            from pathlib import Path

            from agentic_core.L5_safety.validators.RedisSovereignAgent import (
                get_redis_sovereign,
            )

            RedisSovereignAgent = get_redis_sovereign(Path.cwd())
            self._redis_client = RedisSovereignAgent.get_client()
            Logger.info("[MetaLearningClient] Redis connection established")
        except Exception as e:
            Logger.warning(f"[MetaLearningClient] Redis unavailable, using local cache: {e}")
            self._redis_client = None

    def _initialize_pinecone(self) -> None:
        """Initialize Pinecone connection."""
        try:
            from pathlib import Path

            from agentic_core.L5_safety.validators.PineconeSovereignAgent import (
                PineconeSovereignAgent,
            )

            SovereignPineconeStoreAgent = PineconeSovereignAgent(Path.cwd())
            if SovereignPineconeStoreAgent.status == "ONLINE":
                self._pinecone_client = SovereignPineconeStoreAgent.pc
                self._pinecone_index = SovereignPineconeStoreAgent.index
                Logger.info("[MetaLearningClient] Pinecone connection established")
            else:
                Logger.warning(f"[MetaLearningClient] Pinecone status: {SovereignPineconeStoreAgent.status}")
        except Exception as e:
            Logger.warning(f"[MetaLearningClient] Pinecone unavailable: {e}")
            self._pinecone_client = None

    def _get_cache_key(self, key: str, domain: str = "agentic_core") -> str:
        """Generate namespaced cache key."""
        return f"{CACHE_KEY_PREFIX}{domain}:{key}"

    def _validate_input(self, data: Any) -> bool:
        """Validate input to prevent cache poisoning."""
        if data is None:
            return False
        if isinstance(data, str) and len(data) > 100000:  # 100KB limit
            Logger.warning("[MetaLearningClient] Input exceeds size limit")
            return False
        if isinstance(data, dict):
            try:
                json.dumps(data)  # Ensure serializable
            except (TypeError, ValueError):
                Logger.warning("[MetaLearningClient] Input not JSON serializable")
                return False
        return True

    def _generate_error_signature(self, violation: dict[str, Any]) -> str:
        """Generate a hash signature for a violation."""
        signature_data = {
            "type": violation.get("type", "unknown"),
            "path": violation.get("path", ""),
            "message": violation.get("message", "")[:200],  # Truncate for consistency
        }
        signature_str = json.dumps(signature_data, sort_keys=True)
        return hashlib.sha256(signature_str.encode()).hexdigest()[:16]

    # ==================== REDIS CACHING ====================

    def cache_get(self, key: str, domain: str = "agentic_core") -> Any | None:
        """
        Get value from cache (Redis or local fallback).

        Args:
            key: Cache key
            domain: Domain context for namespacing

        Returns:
            Cached value or None if not found/expired
        """
        cache_key = self._get_cache_key(key, domain)

        # Try Redis first
        if self._redis_client:
            try:
                value = self._redis_client.get(cache_key)
                if value:
                    self.stats["cache_hits"] += 1
                    self._update_domain_stats(domain, "cache_hits")
                    return json.loads(value)
            except Exception as e:
                Logger.warning(f"[MetaLearningClient] Redis get failed: {e}")

        # Fallback to local cache
        if cache_key in self._local_cache:
            entry = self._local_cache[cache_key]
            if not entry.is_expired():
                entry.hit_count += 1
                self.stats["cache_hits"] += 1
                self._update_domain_stats(domain, "cache_hits")
                return entry.value
            else:
                del self._local_cache[cache_key]

        self.stats["cache_misses"] += 1
        self._update_domain_stats(domain, "cache_misses")
        return None

    def cache_set(
        self,
        key: str,
        value: Any,
        domain: str = "agentic_core",
        ttl: int | None = None,
    ) -> bool:
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

        # Try Redis first
        if self._redis_client:
            try:
                self._redis_client.setex(
                    cache_key,
                    effective_ttl,
                    json.dumps(value),
                )
                return True
            except Exception as e:
                Logger.warning(f"[MetaLearningClient] Redis set failed: {e}")

        # Fallback to local cache
        self._local_cache[cache_key] = CacheEntry(
            key=cache_key,
            value=value,
            ttl=effective_ttl,
            domain=domain,
        )
        return True

    def cache_delete(self, key: str, domain: str = "agentic_core") -> bool:
        """Delete value from cache."""
        cache_key = self._get_cache_key(key, domain)

        if self._redis_client:
            try:
                self._redis_client.delete(cache_key)
            except Exception as e:
                Logger.warning(f"[MetaLearningClient] Redis delete failed: {e}")

        if cache_key in self._local_cache:
            del self._local_cache[cache_key]

        return True

    # ==================== PINECONE PATTERN RETRIEVAL ====================

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
        pattern_id = f"{domain}:{error_signature}:{int(time.time())}"

        pattern = HealingPattern(
            pattern_id=pattern_id,
            violation_type=violation.get("type", "unknown"),
            error_signature=error_signature,
            healing_strategy=healing_result,
            domain=domain,
            metadata={
                "violation_path": violation.get("path", ""),
                "timestamp": time.time(),
            },
        )

        # Store in Pinecone if available
        if self._pinecone_index:
            try:
                # Generate embedding for the pattern
                embedding = self._generate_embedding(violation)
                if embedding:
                    self._pinecone_index.upsert(
                        vectors=[
                            {
                                "id": pattern_id,
                                "values": embedding,
                                "metadata": pattern.to_dict(),
                            },
                        ],
                        namespace=f"{PINECONE_NAMESPACE_PREFIX}:{domain}",
                    )
                    self.stats["pattern_stores"] += 1
                    self._update_domain_stats(domain, "pattern_stores")
                    Logger.info(f"[MetaLearningClient] Stored pattern: {pattern_id}")
                    return pattern_id
            except Exception as e:
                Logger.warning(f"[MetaLearningClient] Pinecone store failed: {e}")

        # Fallback: store in Redis cache
        cache_key = f"pattern:{error_signature}"
        self.cache_set(cache_key, pattern.to_dict(), domain, ttl=86400)  # 24 hours
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
        if not self._pinecone_index:
            return []

        # Generate embedding for current violation
        try:
            embedding = self._generate_embedding(violation)
            if not embedding:
                return []
        except Exception as e:
            Logger.warning(f"[MetaLearningClient] Failed to generate embedding: {e}")
            return []

        # Use domain-specific threshold if not overridden
        effective_threshold = min_similarity or self.domain_thresholds.get(
            domain,
            DEFAULT_SIMILARITY_THRESHOLD,
        )

        # Query Pinecone with namespace
        namespace = f"{PINECONE_NAMESPACE_PREFIX}_{domain}"

        try:
            results = self._pinecone_index.query(
                vector=embedding,
                top_k=top_k,
                namespace=namespace,
                include_metadata=True,
            )

            patterns = []
            for match in results.matches:
                # Apply similarity threshold guardrail
                if match.score >= effective_threshold:
                    pattern_data = match.metadata
                    pattern_data["embedding"] = match.values if hasattr(match, "values") else None
                    pattern = HealingPattern.from_dict(pattern_data)
                    pattern.similarity_score = match.score
                    patterns.append(pattern)

            self.stats["pattern_retrievals"] += 1
            self._update_domain_stats(domain, "pattern_retrievals")

            Logger.info(
                f"[MetaLearningClient] Retrieved {len(patterns)} patterns for {domain} "
                f"(threshold={effective_threshold:.2f})",
            )

            return patterns

        except Exception as e:
            Logger.error(f"[MetaLearningClient] Pattern retrieval failed: {e}")
            return []

    def _generate_embedding(self, violation: dict[str, Any]) -> list[float] | None:
        """Generate embedding for a violation using the embedding service."""
        try:
            from pathlib import Path

            from agentic_core.L2_execution.reasoning.EmbeddingSovereignAgent import (
                EmbeddingSovereignAgent,
            )

            embedding_agent = EmbeddingSovereignAgent(Path.cwd())
            v_type = violation.get("type", "")
            v_msg = violation.get("message", "")
            v_path = violation.get("path", "")
            text = f"{v_type} {v_msg} {v_path}"
            return embedding_agent.embed_text(text)
        except Exception as e:
            Logger.warning(f"[MetaLearningClient] Embedding generation failed: {e}")
            return None

    # ==================== HEALING CYCLE MANAGEMENT ====================

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

    # ==================== STATISTICS ====================

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


# Singleton accessor
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
