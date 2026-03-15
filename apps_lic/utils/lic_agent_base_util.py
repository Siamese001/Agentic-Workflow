"""
apps_lic/shared/core/agent_base.py - Linked-In Canonical Sovereign Bridge

PHASE 3 META-LEARNING (Feb 2026):
- MetaLearningClientMixin activation for LIC domain
- Domain-specific healing pattern memory (similarity_threshold=THRESHOLD)
- Campaign pattern learning and compliance rule memory

PHASE 1.1 GUARDRAILS INTEGRATION (Feb 2026):
- MetaLearningGuardrails integration for security and safety
- Cache poisoning protection, healing depth tracking
- Domain isolation enforcement, rate limiting

PHASE 2.1 META-LEARNING CLIENT (Feb 2026):
- Full MetaLearningClient integration for Redis/Pinecone
- Pattern storage and retrieval with semantic search
- Healing pattern memory with domain isolation
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Final

from apps_shared.utils.AppBase import AppBase

from agentic_core.interfaces.meta_learning import HealingPattern, MetaLearningGuardrails, get_guardrails
from agentic_core.interfaces.meta_learning import SovereignMetaLearningClient as MetaLearningClient
from agentic_core.interfaces.meta_learning import get_sovereign_meta_client as get_meta_learning_client
from agentic_core.L0_routing.config import APPS_LIC_DIR
from agentic_core.L0_routing.config.path_constants import APPS_LIC_DIR

Logger = logging.getLogger(__name__)
try:
    from agentic_core.interfaces.mixins import MetaLearningMixin
except ImportError:

    class MetaLearningMixin:
        pass


try:
    from agentic_core.interfaces.mixins import HealerMixin
except ImportError:

    class HealerMixin:
        pass


try:
    from agentic_core.mixins.semantic_cache_mixin import SemanticCacheMixin
except ImportError:

    class SemanticCacheMixin:
        pass


try:
    from agentic_core.mixins.embedding_mixin import EmbeddingMixin
except ImportError:

    class EmbeddingMixin:
        pass
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace


@dataclass
class LICAgentBase(SemanticCacheMixin, EmbeddingMixin, MetaLearningMixin, AppBase, HealerMixin):
    """
    LICAgentBase: Sovereign Foundation for 'Linked-In Canonical' (LIC).

    Inherits from AppBase for unified app-level capabilities.

    PHASE 1.1 GUARDRAILS:
    - Integrated MetaLearningGuardrails for security
    - Cache poisoning protection via input validation
    - Healing depth tracking to prevent infinite loops
    - Domain isolation enforcement for apps_lic
    - Higher similarity threshold (0.92) for stricter LIC compliance
    """

    domain_root: Path = field(default_factory=lambda: Path(APPS_LIC_DIR))
    _lic_version: Final[str] = "2.5.0-hardened"
    _namespace: str = field(default=APPS_LIC_DIR, init=False)
    _similarity_threshold: float = field(default=0.92, init=False)
    _resource_prefix: str = field(default="lic", init=False)
    _ml_domain: str = field(default=APPS_LIC_DIR, init=False)
    _guardrails: MetaLearningGuardrails = field(default=None, init=False)
    _lic_ttl: int = field(default=7200, init=False)
    _meta_client: MetaLearningClient = field(default=None, init=False)

    def __post_init__(self) -> None:
        """
        Initialize LIC capabilities after Core hardening.
        """
        super().__post_init__()
        if not self.domain_root.exists():
            self.domain_root.mkdir(parents=True, exist_ok=True)
        self._initialize_guardrails()
        self._initialize_meta_client()
        Logger.debug(
            f"[{self.__class__.__name__}] LIC Meta-Learning activated with guardrails and MetaLearningClient"
        )

    def _initialize_guardrails(self) -> None:
        """Initialize guardrails with LIC-specific configuration (stricter thresholds)."""
        self._guardrails = get_guardrails()
        self._guardrails.guardrails.default_similarity_threshold = self._similarity_threshold
        self._guardrails.guardrails.default_ttl = self._lic_ttl
        Logger.debug(
            f"[{self.__class__.__name__}] Guardrails initialized (threshold={self._similarity_threshold})"
        )

    def _initialize_meta_client(self) -> None:
        """Initialize MetaLearningClient with LIC-specific configuration."""
        self._meta_client = get_meta_learning_client()
        Logger.debug(f"[{self.__class__.__name__}] MetaLearningClient initialized")

    def store_healing_pattern(self, violation: dict[str, Any], healing_result: dict[str, Any]) -> str | None:
        """
        Store a successful healing pattern for future recall.

        Args:
            violation: The violation that was healed
            healing_result: The successful healing result

        Returns:
            Pattern ID if stored successfully, None otherwise
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "LICAgentBase.store_healing_pattern")

        if self._meta_client is None:
            self._initialize_meta_client()
        if not self.validate_domain_pattern({"domain": APPS_LIC_DIR, **violation}):
            return None
        return self._meta_client.store_healing_pattern(violation, healing_result, domain=APPS_LIC_DIR)

    def retrieve_healing_patterns(self, violation: dict[str, Any], top_k: int = 3) -> list[HealingPattern]:
        """
        Retrieve similar healing patterns for a violation.

        Args:
            violation: Current violation to find patterns for
            top_k: Maximum number of patterns to retrieve

        Returns:
            List of similar healing patterns
        """
        if self._meta_client is None:
            self._initialize_meta_client()
        return self._meta_client.retrieve_healing_patterns(
            violation, domain=APPS_LIC_DIR, top_k=top_k, min_similarity=self._similarity_threshold
        )

    def ml_check_healing_depth(self, violation_id: str) -> bool:
        """
        Check healing depth using MetaLearningClient.

        Args:
            violation_id: Unique violation identifier

        Returns:
            True if healing can proceed, False if depth limit reached
        """
        if self._meta_client is None:
            self._initialize_meta_client()
        return self._meta_client.check_healing_depth(self.__class__.__name__, violation_id)

    def ml_increment_healing_depth(self, violation_id: str) -> int:
        """
        Increment healing depth using MetaLearningClient.

        Args:
            violation_id: Unique violation identifier

        Returns:
            Current depth after increment
        """
        if self._meta_client is None:
            self._initialize_meta_client()
        return self._meta_client.increment_healing_depth(self.__class__.__name__, violation_id)

    def ml_reset_healing_depth(self, violation_id: str) -> None:
        """
        Reset healing depth after successful healing.

        Args:
            violation_id: Unique violation identifier
        """
        if self._meta_client is None:
            self._initialize_meta_client()
        self._meta_client.reset_healing_depth(self.__class__.__name__, violation_id)

    def get_meta_learning_stats(self) -> dict[str, Any]:
        """
        Get meta-learning statistics for monitoring.

        Returns:
            Dictionary with meta-learning statistics
        """
        if self._meta_client is None:
            self._initialize_meta_client()
        return self._meta_client.get_stats()

    def get_lic_context(self) -> dict[str, Any]:
        return {
            "domain": "apps_lic",
            "version": self._lic_version,
            "capabilities": self.get_sovereign_capabilities(),
            "meta_learning_domain": self._ml_domain,
        }

    def cache_pattern_with_metadata(
        self, pattern_type: str, pattern_id: str, pattern_data: dict[str, Any], success_count: int = 0
    ) -> bool:
        """
        Cache a pattern with full metadata for enhanced learning.

        Args:
            pattern_type: Type of pattern (campaign, compliance, etc.)
            pattern_id: Unique pattern identifier
            pattern_data: Pattern data
            success_count: Number of successful applications

        Returns:
            True if cached successfully
        """
        import time

        if not self.check_and_enforce_rate_limit("pattern"):
            return False
        if not self.check_cache_capacity():
            return False
        enhanced_data = {
            **pattern_data,
            "_metadata": {
                "pattern_type": pattern_type,
                "domain": "apps_lic",
                "created_at": time.time(),
                "success_count": success_count,
                "similarity_threshold": self._similarity_threshold,
            },
        }
        success, namespaced_key = self.isolate_cache_operation(
            "set", f"{pattern_type}:{pattern_id}", enhanced_data
        )
        if not success:
            return False
        try:
            result = self.ml_cache_set(namespaced_key, enhanced_data)
            if result:
                self.update_cache_metrics(1)
            return result
        except Exception as e:
            Logger.error(f"[{self.__class__.__name__}] Enhanced cache failed: {e}")
            return False

    def retrieve_pattern_with_metadata(self, pattern_type: str, pattern_id: str) -> dict[str, Any] | None:
        """
        Retrieve a pattern with its metadata.

        Args:
            pattern_type: Type of pattern
            pattern_id: Pattern identifier

        Returns:
            Pattern data with metadata or None
        """
        if not self.check_and_enforce_rate_limit("request"):
            return None
        namespaced_key = self.get_namespaced_cache_key(f"{pattern_type}:{pattern_id}")
        try:
            return self.ml_cache_get(namespaced_key)
        except Exception as e:
            Logger.error(f"[{self.__class__.__name__}] Pattern retrieval failed: {e}")
            return None

    def increment_pattern_success(self, pattern_type: str, pattern_id: str) -> bool:
        """
        Increment success count for a pattern (learning signal).

        Args:
            pattern_type: Type of pattern
            pattern_id: Pattern identifier

        Returns:
            True if updated successfully
        """
        pattern = self.retrieve_pattern_with_metadata(pattern_type, pattern_id)
        if pattern is None:
            return False
        metadata = pattern.get("_metadata", {})
        metadata["success_count"] = metadata.get("success_count", 0) + 1
        pattern["_metadata"] = metadata
        return self.cache_pattern_with_metadata(pattern_type, pattern_id, pattern, metadata["success_count"])

    def ml_cache_campaign_pattern(self, campaign_id: str, pattern_data: dict[str, Any]) -> bool:
        """
        Cache a successful campaign pattern for future recall.

        Args:
            campaign_id: Unique campaign identifier
            pattern_data: Campaign pattern data (templates, timing, etc.)

        Returns:
            True if cached successfully
        """
        cache_key = f"campaign_pattern:{campaign_id}"
        return self.ml_cache_set(cache_key, pattern_data)

    def ml_recall_campaign_pattern(self, campaign_id: str) -> dict[str, Any] | None:
        """
        Recall a cached campaign pattern.

        Args:
            campaign_id: Unique campaign identifier

        Returns:
            Cached pattern data or None
        """
        cache_key = f"campaign_pattern:{campaign_id}"
        return self.ml_cache_get(cache_key)

    def ml_cache_compliance_rule(self, rule_id: str, rule_data: dict[str, Any]) -> bool:
        """
        Cache a compliance rule resolution for future reference.

        Args:
            rule_id: Unique rule identifier
            rule_data: Rule resolution data

        Returns:
            True if cached successfully
        """
        cache_key = f"compliance_rule:{rule_id}"
        return self.ml_cache_set(cache_key, rule_data)

    def ml_recall_compliance_rule(self, rule_id: str) -> dict[str, Any] | None:
        """
        Recall a cached compliance rule resolution.

        Args:
            rule_id: Unique rule identifier

        Returns:
            Cached rule data or None
        """
        cache_key = f"compliance_rule:{rule_id}"
        return self.ml_cache_get(cache_key)

    def get_namespaced_cache_key(self, key: str) -> str:
        """
        Generate a namespaced cache key for LIC domain isolation.

        Args:
            key: Base cache key

        Returns:
            Namespaced key with apps_lic prefix
        """
        return f"apps_lic:{self._resource_prefix}:{key}"

    def validate_domain_pattern(self, pattern: dict[str, Any]) -> bool:
        """
        Validate that a pattern belongs to the LIC domain.

        Args:
            pattern: Pattern to validate

        Returns:
            True if pattern is valid for LIC domain
        """
        domain_value = pattern.get("domain") or pattern.get("_domain")
        if domain_value:
            if domain_value != APPS_LIC_DIR:
                Logger.warning(f"[{self.__class__.__name__}] Rejected cross-domain pattern: {domain_value}")
                return False
        return True

    def isolate_cache_operation(self, operation: str, key: str, value: Any = None) -> tuple[bool, Any]:
        """
        Perform a cache operation with domain isolation.

        Args:
            operation: 'get', 'set', or 'delete'
            key: Cache key (will be namespaced)
            value: Value for set operations

        Returns:
            Tuple of (success, result)
        """
        namespaced_key = self.get_namespaced_cache_key(key)
        if not self.guardrails_validate_cache_key(namespaced_key):
            return (False, None)
        if operation == "set" and value is not None:
            if not self.guardrails_validate_cache_value(value):
                return (False, None)
            if isinstance(value, dict):
                value["_domain"] = APPS_LIC_DIR
                value["_namespace"] = self._namespace
        return (True, namespaced_key)

    def check_and_enforce_rate_limit(self, operation: str = "request") -> bool:
        """
        Check and enforce rate limits for cache operations.

        Args:
            operation: Type of operation ('request' or 'pattern')

        Returns:
            True if operation is allowed, False if rate limited
        """
        if self._guardrails is None:
            self._initialize_guardrails()
        allowed = self._guardrails.check_rate_limit(APPS_LIC_DIR, operation)
        if not allowed:
            Logger.warning(f"[{self.__class__.__name__}] Rate limit exceeded for {operation}")
        return allowed

    def check_cache_capacity(self) -> bool:
        """
        Check if cache has capacity for new entries.

        Returns:
            True if cache can accept new entries, False if at capacity
        """
        if self._guardrails is None:
            self._initialize_guardrails()
        return self._guardrails.check_cache_size_limit(APPS_LIC_DIR)

    def update_cache_metrics(self, delta: int = 1) -> None:
        """
        Update cache size metrics after cache operations.

        Args:
            delta: Change in cache size (+1 for add, -1 for remove)
        """
        if self._guardrails is None:
            self._initialize_guardrails()
        self._guardrails.update_cache_size(APPS_LIC_DIR, delta)

    def safe_cache_set(self, key: str, value: Any, validate_rate: bool = True) -> bool:
        """
        Safely set a cache value with rate limiting and size checks.

        Args:
            key: Cache key
            value: Value to cache
            validate_rate: Whether to check rate limits

        Returns:
            True if cached successfully, False otherwise
        """
        if validate_rate and (not self.check_and_enforce_rate_limit("request")):
            return False
        if not self.check_cache_capacity():
            Logger.warning(f"[{self.__class__.__name__}] Cache at capacity")
            return False
        success, namespaced_key = self.isolate_cache_operation("set", key, value)
        if not success:
            return False
        try:
            result = self.ml_cache_set(namespaced_key, value)
            if result:
                self.update_cache_metrics(1)
            return result
        except Exception as e:
            Logger.error(f"[{self.__class__.__name__}] Cache set failed: {e}")
            return False

    def safe_cache_get(self, key: str, validate_rate: bool = True) -> Any:
        """
        Safely get a cache value with rate limiting.

        Args:
            key: Cache key
            validate_rate: Whether to check rate limits

        Returns:
            Cached value or None
        """
        if validate_rate and (not self.check_and_enforce_rate_limit("request")):
            return None
        namespaced_key = self.get_namespaced_cache_key(key)
        try:
            return self.ml_cache_get(namespaced_key)
        except Exception as e:
            Logger.error(f"[{self.__class__.__name__}] Cache get failed: {e}")
            return None

    def get_cache_health(self) -> dict[str, Any]:
        """
        Get cache health metrics for monitoring.

        Returns:
            Dictionary with cache health information
        """
        if self._guardrails is None:
            self._initialize_guardrails()
        stats = self._guardrails.get_stats()
        return {
            "domain": "apps_lic",
            "cache_size": stats.get("cache_sizes", {}).get("apps_lic", 0),
            "request_rate": stats.get("request_rates", {}).get("apps_lic", 0),
            "pattern_rate": stats.get("pattern_rates", {}).get("apps_lic", 0),
            "active_healing_cycles": len(stats.get("depth_trackers", {}).get(self.__class__.__name__, {})),
            "healthy": True,
        }

    def guardrails_validate_cache_key(self, key: str) -> bool:
        """
        Validate cache key to prevent injection attacks.

        Args:
            key: Cache key to validate

        Returns:
            True if key is safe, False otherwise
        """
        if self._guardrails is None:
            self._initialize_guardrails()
        return self._guardrails.validate_cache_key(key)

    def guardrails_validate_cache_value(self, value: Any) -> bool:
        """
        Validate cache value to prevent memory exhaustion.

        Args:
            value: Cache value to validate

        Returns:
            True if value is safe, False otherwise
        """
        if self._guardrails is None:
            self._initialize_guardrails()
        return self._guardrails.validate_cache_value(value)

    def guardrails_check_healing_depth(self, violation_id: str) -> bool:
        """
        Check if healing depth limit is reached for this agent.

        Args:
            violation_id: Unique identifier for the violation

        Returns:
            True if healing can proceed, False if depth limit reached
        """
        if self._guardrails is None:
            self._initialize_guardrails()
        return self._guardrails.check_healing_depth(self.__class__.__name__, violation_id)

    def guardrails_increment_healing_depth(self, violation_id: str) -> int:
        """
        Increment healing depth counter.

        Args:
            violation_id: Unique identifier for the violation

        Returns:
            Current depth after increment
        """
        if self._guardrails is None:
            self._initialize_guardrails()
        return self._guardrails.increment_healing_depth(self.__class__.__name__, violation_id)

    def guardrails_reset_healing_depth(self, violation_id: str) -> None:
        """
        Reset healing depth counter after successful healing.

        Args:
            violation_id: Unique identifier for the violation
        """
        if self._guardrails is None:
            self._initialize_guardrails()
        self._guardrails.reset_healing_depth(self.__class__.__name__, violation_id)

    def guardrails_validate_domain_isolation(self, pattern: dict[str, Any]) -> bool:
        """
        Validate domain isolation to prevent cross-domain contamination.

        Args:
            pattern: Pattern to validate

        Returns:
            True if pattern is valid for apps_lic domain, False otherwise
        """
        if self._guardrails is None:
            self._initialize_guardrails()
        return self._guardrails.validate_domain_isolation(APPS_LIC_DIR, pattern)

    def guardrails_sanitize_violation(self, violation: dict[str, Any]) -> dict[str, Any]:
        """
        Sanitize violation data to prevent cache poisoning.

        Args:
            violation: Raw violation data

        Returns:
            Sanitized violation data
        """
        if self._guardrails is None:
            self._initialize_guardrails()
        return self._guardrails.sanitize_violation_data(violation)

    def guardrails_check_rate_limit(self, operation: str = "request") -> bool:
        """
        Check rate limits for operations.

        Args:
            operation: Type of operation (request, pattern)

        Returns:
            True if operation allowed, False if rate limited
        """
        if self._guardrails is None:
            self._initialize_guardrails()
        return self._guardrails.check_rate_limit(APPS_LIC_DIR, operation)

    def guardrails_get_stats(self) -> dict[str, Any]:
        """Get guardrails statistics for monitoring."""
        if self._guardrails is None:
            self._initialize_guardrails()
        return self._guardrails.get_stats()
