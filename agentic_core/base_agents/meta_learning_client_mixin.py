"""
MetaLearningClientMixin - Bridge between SovereignBaseAgent and MetaLearningClient.

[PHASE 2] Meta-Learning Integration

Provides:
- Automatic MetaLearningClient injection into agents
- Healing pattern recall and storage
- Cache-aware healing decision logic
- Domain-specific context handling
- [NEW] Comprehensive guardrails and safety checks

This mixin integrates the Phase 1 MetaLearningClient infrastructure
into the SovereignBaseAgent hierarchy, enabling all agents to:
1. Recall successful healing strategies from Pinecone
2. Cache expensive analysis results in Redis
3. Prevent recursive healing loops via depth tracking
4. [NEW] Operate safely with strict abuse prevention
"""

from __future__ import annotations

import logging
from typing import Any

Logger = logging.getLogger(__name__)


class MetaLearningClientMixin:
    """
    Mixin that provides MetaLearningClient capabilities to agents.

    Enables agents to:
    1. Recall healing patterns from previous successful healings
    2. Cache expensive analysis results to prevent redundant processing
    3. Store successful healing patterns for future use
    4. Track healing depth to prevent infinite loops
    5. [NEW] Operate with comprehensive safety guardrails

    Thread Safety:
        Uses lazy initialization with singleton pattern from MetaLearningClient.

    Domain Isolation:
        Automatically determines domain from agent class name or explicit setting.

    Safety Features:
        - Input validation and sanitization
        - Rate limiting and cache size limits
        - TTL management and expiration
        - Similarity threshold enforcement
        - Graceful degradation on failures
    """

    _ml_client = None  # Lazy-loaded MetaLearningClient singleton
    _ml_embedder = None  # Lazy-loaded HealingMemoryEmbedder singleton
    _ml_cache_manager = None  # Lazy-loaded CacheStrategyManager singleton
    _ml_guardrails = None  # Lazy-loaded guardrails singleton

    def _ensure_ml_client(self) -> None:
        """Ensure MetaLearningClient is initialized (lazy loading)."""
        if MetaLearningClientMixin._ml_client is None:
            try:
                from agentic_core.L1_cognition.meta_learning.meta_learning_client_types import (
                    get_meta_learning_client,
                )

                MetaLearningClientMixin._ml_client = get_meta_learning_client()
                Logger.debug(f"[{self.__class__.__name__}] MetaLearningClient initialized")
            except Exception as e:
                Logger.warning(f"[{self.__class__.__name__}] MetaLearningClient unavailable: {e}")

    def _ensure_ml_embedder(self) -> None:
        """Ensure HealingMemoryEmbedder is initialized (lazy loading)."""
        if MetaLearningClientMixin._ml_embedder is None:
            try:
                from agentic_core.L1_cognition.meta_learning.healing_memory_embedder_types import (
                    get_healing_memory_embedder,
                )

                MetaLearningClientMixin._ml_embedder = get_healing_memory_embedder()
                Logger.debug(f"[{self.__class__.__name__}] HealingMemoryEmbedder initialized")
            except Exception as e:
                Logger.warning(f"[{self.__class__.__name__}] HealingMemoryEmbedder unavailable: {e}")

    def _ensure_ml_cache_manager(self) -> None:
        """Ensure CacheStrategyManager is initialized (lazy loading)."""
        if MetaLearningClientMixin._ml_cache_manager is None:
            try:
                from agentic_core.L1_cognition.meta_learning.cache_strategy_manager_types import (
                    get_cache_strategy_manager,
                )

                MetaLearningClientMixin._ml_cache_manager = get_cache_strategy_manager()
                Logger.debug(f"[{self.__class__.__name__}] CacheStrategyManager initialized")
            except Exception as e:
                Logger.warning(f"[{self.__class__.__name__}] CacheStrategyManager unavailable: {e}")

    def _ensure_ml_guardrails(self) -> None:
        """Ensure guardrails are initialized (lazy loading)."""
        if MetaLearningClientMixin._ml_guardrails is None:
            try:
                from agentic_core.L1_cognition.meta_learning.guardrails import get_guardrails

                MetaLearningClientMixin._ml_guardrails = get_guardrails()
                Logger.debug(f"[{self.__class__.__name__}] Guardrails initialized")
            except Exception as e:
                Logger.warning(f"[{self.__class__.__name__}] Guardrails unavailable: {e}")

    def _get_ml_domain(self) -> str:
        """
        Determine the domain for this agent based on class name or module.

        Returns:
            Domain string: 'agentic_core', 'apps_lic', or 'apps_rg'
        """
        # Check for explicit domain attribute
        if hasattr(self, "_ml_domain"):
            return self._ml_domain

        # Infer from class name
        class_name = self.__class__.__name__
        if "Lic" in class_name or "LIC" in class_name:
            return "apps_lic"
        if "Rg" in class_name or "RG" in class_name:
            return "apps_rg"

        # Infer from module path
        module = self.__class__.__module__
        if "apps_lic" in module:
            return "apps_lic"
        if "apps_rg" in module:
            return "apps_rg"

        return "agentic_core"

    # ==================== HEALING PATTERN RECALL ====================

    def ml_recall_healing_pattern(
        self,
        violation: dict[str, Any],
    ) -> dict[str, Any] | None:
        """
        Recall a successful healing pattern for a similar violation with safety checks.

        Args:
            violation: The violation to find patterns for

        Returns:
            Healing pattern if found above similarity threshold, None otherwise
        """
        self._ensure_ml_client()
        self._ensure_ml_guardrails()

        if MetaLearningClientMixin._ml_client is None:
            return None

        domain = self._get_ml_domain()

        # Sanitize violation data
        if MetaLearningClientMixin._ml_guardrails is not None:
            violation = MetaLearningClientMixin._ml_guardrails.sanitize_violation_data(violation)

        # Check rate limits for pattern operations
        if MetaLearningClientMixin._ml_guardrails is not None:
            if not MetaLearningClientMixin._ml_guardrails.check_rate_limit(domain, "pattern"):
                Logger.warning(f"[{self.__class__.__name__}] Pattern rate limited for domain: {domain}")
                return None

        try:
            patterns = MetaLearningClientMixin._ml_client.retrieve_healing_patterns(
                violation,
                domain,
                top_k=1,
            )

            if patterns:
                pattern = patterns[0]

                # Validate domain isolation
                if MetaLearningClientMixin._ml_guardrails is not None:
                    if not MetaLearningClientMixin._ml_guardrails.validate_domain_isolation(domain, pattern):
                        Logger.warning(f"[{self.__class__.__name__}] Cross-domain pattern rejected")
                        return None

                    # Check similarity threshold
                    similarity = pattern.get("similarity_score", 0.0)
                    min_threshold = MetaLearningClientMixin._ml_guardrails.guardrails.min_similarity_threshold

                    if similarity < min_threshold:
                        Logger.debug(
                            f"[{self.__class__.__name__}] Pattern below similarity threshold: {similarity:.2f} < {min_threshold:.2f}",
                        )
                        return None

                Logger.info(
                    f"[{self.__class__.__name__}] Recalled healing pattern: "
                    f"{pattern.get('violation_type', 'unknown')} (domain={domain}, similarity={pattern.get('similarity_score', 0):.2f})",
                )
                return pattern.get("healing_strategy", pattern)

            return None

        except Exception as e:
            Logger.error(f"[{self.__class__.__name__}] Pattern recall failed: {e}")
            return None

    def ml_store_healing_pattern(
        self,
        violation: dict[str, Any],
        healing_result: dict[str, Any],
    ) -> str | None:
        """
        Store a successful healing pattern for future recall with safety checks.

        Args:
            violation: The violation that was healed
            healing_result: The successful healing result

        Returns:
            Pattern ID if stored successfully, None otherwise
        """
        self._ensure_ml_client()
        self._ensure_ml_guardrails()

        if MetaLearningClientMixin._ml_client is None:
            return None

        # Only store successful healings
        if healing_result.get("status") not in ("fixed", "success"):
            return None

        domain = self._get_ml_domain()

        # Sanitize violation data
        if MetaLearningClientMixin._ml_guardrails is not None:
            violation = MetaLearningClientMixin._ml_guardrails.sanitize_violation_data(violation)

        # Check rate limits for pattern operations
        if MetaLearningClientMixin._ml_guardrails is not None:
            if not MetaLearningClientMixin._ml_guardrails.check_rate_limit(domain, "pattern"):
                Logger.warning(f"[{self.__class__.__name__}] Pattern rate limited for domain: {domain}")
                return None

        try:
            pattern_id = MetaLearningClientMixin._ml_client.store_healing_pattern(
                violation,
                healing_result,
                domain,
            )

            if pattern_id:
                Logger.info(f"[{self.__class__.__name__}] Stored healing pattern: {pattern_id}")

            return pattern_id

        except Exception as e:
            Logger.error(f"[{self.__class__.__name__}] Pattern storage failed: {e}")
            return None

    # ==================== CACHE OPERATIONS ====================

    def ml_cache_get(self, key: str) -> Any | None:
        """
        Get a cached value (e.g., AST analysis result) with safety checks.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        self._ensure_ml_client()
        self._ensure_ml_guardrails()

        if MetaLearningClientMixin._ml_client is None:
            return None

        # Validate cache key
        if MetaLearningClientMixin._ml_guardrails is not None:
            if not MetaLearningClientMixin._ml_guardrails.validate_cache_key(key):
                Logger.warning(f"[{self.__class__.__name__}] Invalid cache key: {key}")
                return None

        domain = self._get_ml_domain()

        # Check rate limits
        if MetaLearningClientMixin._ml_guardrails is not None:
            if not MetaLearningClientMixin._ml_guardrails.check_rate_limit(domain, "request"):
                Logger.warning(f"[{self.__class__.__name__}] Rate limited for domain: {domain}")
                return None

        try:
            return MetaLearningClientMixin._ml_client.cache_get(key, domain)
        except Exception as e:
            Logger.error(f"[{self.__class__.__name__}] Cache get failed: {e}")
            return None

    def ml_cache_set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        """
        Set a cached value (e.g., AST analysis result) with safety checks.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Optional TTL override (uses domain default if not specified)

        Returns:
            True if cached successfully, False otherwise
        """
        self._ensure_ml_client()
        self._ensure_ml_guardrails()

        if MetaLearningClientMixin._ml_client is None:
            return False

        domain = self._get_ml_domain()

        # Validate inputs
        if MetaLearningClientMixin._ml_guardrails is not None:
            if not MetaLearningClientMixin._ml_guardrails.validate_cache_key(key):
                Logger.warning(f"[{self.__class__.__name__}] Invalid cache key: {key}")
                return False

            if not MetaLearningClientMixin._ml_guardrails.validate_cache_value(value):
                Logger.warning(f"[{self.__class__.__name__}] Invalid cache value")
                return False

            if not MetaLearningClientMixin._ml_guardrails.check_cache_size_limit(domain):
                Logger.warning(f"[{self.__class__.__name__}] Cache size limit reached: {domain}")
                return False

            if not MetaLearningClientMixin._ml_guardrails.check_rate_limit(domain, "request"):
                Logger.warning(f"[{self.__class__.__name__}] Rate limited for domain: {domain}")
                return False

            # Validate and normalize TTL
            ttl = MetaLearningClientMixin._ml_guardrails.validate_ttl(ttl)

        try:
            success = MetaLearningClientMixin._ml_client.cache_set(key, value, domain, ttl)

            # Update cache size tracking
            if success and MetaLearningClientMixin._ml_guardrails is not None:
                MetaLearningClientMixin._ml_guardrails.update_cache_size(domain, 1)

            return success
        except Exception as e:
            Logger.error(f"[{self.__class__.__name__}] Cache set failed: {e}")
            return False

    def ml_cache_delete(self, key: str) -> bool:
        """Delete a cached value."""
        self._ensure_ml_client()
        if MetaLearningClientMixin._ml_client is None:
            return False

        domain = self._get_ml_domain()
        return MetaLearningClientMixin._ml_client.cache_delete(key, domain)

    # ==================== HEALING DEPTH TRACKING ====================

    def ml_check_healing_depth(self, violation_id: str) -> bool:
        """
        Check if healing depth limit has been reached for this violation.

        Args:
            violation_id: Unique identifier for the violation

        Returns:
            True if healing can proceed, False if depth limit reached
        """
        self._ensure_ml_guardrails()

        if MetaLearningClientMixin._ml_guardrails is None:
            return True  # Allow healing if guardrails unavailable

        return MetaLearningClientMixin._ml_guardrails.check_healing_depth(
            self.__class__.__name__,
            violation_id,
        )

    def ml_increment_healing_depth(self, violation_id: str) -> int:
        """
        Increment healing depth counter for this violation.

        Args:
            violation_id: Unique identifier for the violation

        Returns:
            Current depth after increment
        """
        self._ensure_ml_guardrails()

        if MetaLearningClientMixin._ml_guardrails is None:
            return 0

        return MetaLearningClientMixin._ml_guardrails.increment_healing_depth(
            self.__class__.__name__,
            violation_id,
        )

    def ml_reset_healing_depth(self, violation_id: str) -> None:
        """
        Reset healing depth counter after successful healing.

        Args:
            violation_id: Unique identifier for the violation
        """
        self._ensure_ml_guardrails()

        if MetaLearningClientMixin._ml_guardrails is None:
            return

        MetaLearningClientMixin._ml_guardrails.reset_healing_depth(self.__class__.__name__, violation_id)

    # ==================== SIGNATURE GENERATION ====================

    def ml_get_violation_signature(self, violation: dict[str, Any]) -> str:
        """
        Generate a hash signature for a violation.

        Args:
            violation: Violation dictionary

        Returns:
            Hash signature string
        """
        self._ensure_ml_embedder()
        if MetaLearningClientMixin._ml_embedder is None:
            # Fallback to simple hash
            import hashlib
            import json

            sig_str = json.dumps(
                {
                    "type": violation.get("type", ""),
                    "path": violation.get("path", ""),
                },
                sort_keys=True,
            )
            return hashlib.sha256(sig_str.encode()).hexdigest()[:16]

        return MetaLearningClientMixin._ml_embedder.get_hash_signature(violation)

    # ==================== STATISTICS ====================

    def ml_get_stats(self) -> dict[str, Any]:
        """Get combined statistics from all meta-learning components."""
        stats = {"domain": self._get_ml_domain()}

        self._ensure_ml_client()
        if MetaLearningClientMixin._ml_client is not None:
            stats["client"] = MetaLearningClientMixin._ml_client.get_stats()

        self._ensure_ml_embedder()
        if MetaLearningClientMixin._ml_embedder is not None:
            stats["embedder"] = MetaLearningClientMixin._ml_embedder.get_stats()

        self._ensure_ml_cache_manager()
        if MetaLearningClientMixin._ml_cache_manager is not None:
            stats["cache_manager"] = MetaLearningClientMixin._ml_cache_manager.get_stats()

        return stats

    # ==================== ENHANCED HEAL METHOD ====================

    def ml_enhanced_heal(
        self,
        violation: dict[str, Any],
        heal_fn: callable,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Enhanced heal method with meta-learning integration.

        This method:
        1. Checks healing depth to prevent infinite loops
        2. Attempts to recall a successful healing pattern
        3. If no pattern found, executes the provided heal function
        4. Stores successful healing patterns for future use

        Args:
            violation: The violation to heal
            heal_fn: The actual healing function to call
            **kwargs: Additional arguments to pass to heal_fn

        Returns:
            Healing result dictionary
        """
        violation_id = violation.get("id", self.ml_get_violation_signature(violation))

        # Step 1: Check healing depth
        if not self.ml_check_healing_depth(violation_id):
            Logger.warning(f"[{self.__class__.__name__}] Healing depth limit reached for {violation_id}")
            return {
                "status": "skipped",
                "reason": "healing_depth_limit_reached",
                "violation_id": violation_id,
            }

        # Step 2: Increment depth
        self.ml_increment_healing_depth(violation_id)

        try:
            # Step 3: Try to recall a successful pattern
            cached_pattern = self.ml_recall_healing_pattern(violation)
            if cached_pattern:
                Logger.info(f"[{self.__class__.__name__}] Using cached healing pattern for {violation_id}")
                # Reset depth on successful recall
                self.ml_reset_healing_depth(violation_id)
                return {
                    **cached_pattern,
                    "source": "meta_learning_cache",
                    "violation_id": violation_id,
                }

            # Step 4: Execute the actual healing
            result = heal_fn(violation, **kwargs)

            # Step 5: Store successful pattern
            if result.get("status") in ("fixed", "success"):
                self.ml_store_healing_pattern(violation, result)
                # Reset depth on successful healing
                self.ml_reset_healing_depth(violation_id)

            return result

        except Exception as e:
            Logger.error(f"[{self.__class__.__name__}] Healing failed: {e}")
            return {
                "status": "error",
                "reason": str(e),
                "violation_id": violation_id,
            }

    @classmethod
    def reset_ml_singletons(cls) -> None:
        """[TESTING ONLY] Reset all meta-learning singletons."""
        cls._ml_client = None
        cls._ml_embedder = None
        cls._ml_cache_manager = None
        cls._ml_guardrails = None
        Logger.info("[MetaLearningClientMixin] All singletons reset")
