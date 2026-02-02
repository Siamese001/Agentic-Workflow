"""
apps_lic/shared/core/agent_base.py - Linked-In Canonical Sovereign Bridge

PHASE 3 META-LEARNING (Feb 2026):
- MetaLearningClientMixin activation for LIC domain
- Domain-specific healing pattern memory (similarity_threshold=0.92)
- Campaign pattern learning and compliance rule memory

PHASE 1.1 GUARDRAILS INTEGRATION (Feb 2026):
- MetaLearningGuardrails integration for security and safety
- Cache poisoning protection, healing depth tracking
- Domain isolation enforcement, rate limiting
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Final

# CORE SOCKETING: Align with Phase 2A Unified Base Class
from agentic_core.base_agents.AppBaseAgent import AppBaseAgent

# PHASE 1.1: Guardrails Integration
from agentic_core.L1_cognition.meta_learning.guardrails import (
    MetaLearningGuardrails,
    get_guardrails,
)

Logger = logging.getLogger(__name__)

# Import mixins with fallbacks
try:
    from agentic_core.L1_cognition.thought_engine.meta_learning_mixin import (
        MetaLearningMixin,
    )
except ImportError:

    class MetaLearningMixin:
        pass


try:
    from agentic_core.L5_safety.validators.healing_mixin import HealerMixin
except ImportError:

    class HealerMixin:
        pass


@dataclass
class LICAgentBase(MetaLearningMixin, AppBaseAgent, HealerMixin):
    """
    LICAgentBase: Sovereign Foundation for 'Linked-In Canonical' (LIC).

    Inherits from AppBaseAgent for unified app-level capabilities.

    PHASE 1.1 GUARDRAILS:
    - Integrated MetaLearningGuardrails for security
    - Cache poisoning protection via input validation
    - Healing depth tracking to prevent infinite loops
    - Domain isolation enforcement for apps_lic
    - Higher similarity threshold (0.92) for stricter LIC compliance
    """

    # Domain-specific LIC configuration
    domain_root: Path = field(default_factory=lambda: Path("apps_lic"))
    _lic_version: Final[str] = "2.5.0-hardened"

    # [PHASE 25] Infrastructure Config (STRICTER)
    _namespace: str = field(default="apps_lic", init=False)
    _similarity_threshold: float = field(default=0.92, init=False)
    _resource_prefix: str = field(default="lic", init=False)

    # [PHASE 3] Meta-Learning Domain Override
    _ml_domain: str = field(default="apps_lic", init=False)

    # [PHASE 1.1] Guardrails Integration
    _guardrails: MetaLearningGuardrails = field(default=None, init=False)
    _lic_ttl: int = field(default=7200, init=False)  # 2 hours for LIC domain (longer campaigns)

    def __post_init__(self) -> None:
        """
        Initialize LIC capabilities after Core hardening.
        """
        # CRITICAL: Trigger Core Security Validation
        super().__post_init__()

        # LIC Domain Integrity Check
        if not self.domain_root.exists():
            self.domain_root.mkdir(parents=True, exist_ok=True)

        # [PHASE 1.1] Initialize Guardrails with LIC-specific configuration
        self._initialize_guardrails()

        Logger.debug(f"[{self.__class__.__name__}] LIC Meta-Learning activated with guardrails")

    def _initialize_guardrails(self) -> None:
        """Initialize guardrails with LIC-specific configuration (stricter thresholds)."""
        self._guardrails = get_guardrails()
        # Configure LIC-specific thresholds (stricter than RG)
        self._guardrails.guardrails.default_similarity_threshold = self._similarity_threshold
        self._guardrails.guardrails.default_ttl = self._lic_ttl
        Logger.debug(
            f"[{self.__class__.__name__}] Guardrails initialized "
            f"(threshold={self._similarity_threshold})"
        )

    def get_lic_context(self) -> dict[str, Any]:
        return {
            "domain": "apps_lic",
            "version": self._lic_version,
            "capabilities": self.get_sovereign_capabilities(),
            "meta_learning_domain": self._ml_domain,
        }

    # ==================== LIC-SPECIFIC META-LEARNING ====================

    def ml_cache_campaign_pattern(
        self,
        campaign_id: str,
        pattern_data: dict[str, Any],
    ) -> bool:
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

    def ml_cache_compliance_rule(
        self,
        rule_id: str,
        rule_data: dict[str, Any],
    ) -> bool:
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

    # ==================== PHASE 1.2: DOMAIN ISOLATION ====================

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
        # Check domain field if present (both "domain" and "_domain" metadata)
        domain_value = pattern.get("domain") or pattern.get("_domain")
        if domain_value:
            if domain_value != "apps_lic":
                Logger.warning(
                    f"[{self.__class__.__name__}] Rejected cross-domain pattern: {domain_value}"
                )
                return False
        return True

    def isolate_cache_operation(
        self,
        operation: str,
        key: str,
        value: Any = None,
    ) -> tuple[bool, Any]:
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

        # Validate key
        if not self.guardrails_validate_cache_key(namespaced_key):
            return (False, None)

        # For set operations, validate value
        if operation == "set" and value is not None:
            if not self.guardrails_validate_cache_value(value):
                return (False, None)

            # Add domain metadata
            if isinstance(value, dict):
                value["_domain"] = "apps_lic"
                value["_namespace"] = self._namespace

        return (True, namespaced_key)

    # ==================== PHASE 1.1: GUARDRAILS METHODS ====================

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
        return self._guardrails.validate_domain_isolation("apps_lic", pattern)

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
        return self._guardrails.check_rate_limit("apps_lic", operation)

    def guardrails_get_stats(self) -> dict[str, Any]:
        """Get guardrails statistics for monitoring."""
        if self._guardrails is None:
            self._initialize_guardrails()
        return self._guardrails.get_stats()
