"""
apps_rg/shared/core/agent_base.py - Resume Generation Sovereign Bridge

PHASE 3 META-LEARNING (Feb 2026):
- MetaLearningClientMixin activation for RG domain
- Domain-specific healing pattern memory (similarity_threshold=0.85)
- Resume quality pattern learning and ATS compatibility memory
- Redis/Pinecone integration for content optimization

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


@dataclass
class RGAgentBase(AppBaseAgent):
    """
    RGAgentBase: The Sovereign Foundation for all 'Resume Generation' Agents.

    Inherits from AppBaseAgent for unified app-level capabilities.

    PHASE 1.1 GUARDRAILS:
    - Integrated MetaLearningGuardrails for security
    - Cache poisoning protection via input validation
    - Healing depth tracking to prevent infinite loops
    - Domain isolation enforcement for apps_rg
    """

    # Domain-specific RG configuration
    domain_root: Path = field(default_factory=lambda: Path("apps_rg"))
    _rg_version: Final[str] = "2.5.0"

    # [PHASE 25] Infrastructure Config
    _namespace: str = field(default="apps_rg", init=False)
    _similarity_threshold: float = field(default=0.85, init=False)
    _resource_prefix: str = field(default="rg", init=False)

    # [PHASE 1.1] Guardrails Integration
    _guardrails: MetaLearningGuardrails = field(default=None, init=False)
    _rg_ttl: int = field(default=3600, init=False)  # 1 hour for RG domain

    def __post_init__(self) -> None:
        """
        Initialize RG-specific capabilities after Core hardening.
        """
        # CRITICAL: Trigger Core Security Validation via AppBaseAgent
        super().__post_init__()

        # RG Domain Validation
        if not self.domain_root.exists():
            # Create if missing to ensure domain integrity
            self.domain_root.mkdir(parents=True, exist_ok=True)

        # [PHASE 1.1] Initialize Guardrails with RG-specific configuration
        self._initialize_guardrails()

        Logger.debug(f"[{self.__class__.__name__}] RG Meta-Learning activated with guardrails")

    def _initialize_guardrails(self) -> None:
        """Initialize guardrails with RG-specific configuration."""
        self._guardrails = get_guardrails()
        # Configure RG-specific thresholds
        self._guardrails.guardrails.default_similarity_threshold = self._similarity_threshold
        self._guardrails.guardrails.default_ttl = self._rg_ttl
        Logger.debug(
            f"[{self.__class__.__name__}] Guardrails initialized "
            f"(threshold={self._similarity_threshold})"
        )

    def get_rg_context(self) -> dict[str, Any]:
        """Return RG-specific context wrapper."""
        return {
            "domain": "apps_rg",
            "version": self._rg_version,
            "capabilities": self.get_sovereign_capabilities(),
            "meta_learning_domain": self._ml_domain,
        }

    # ==================== RG-SPECIFIC META-LEARNING ====================

    def ml_cache_resume_quality_pattern(
        self,
        pattern_id: str,
        pattern_data: dict[str, Any],
    ) -> bool:
        """
        Cache a successful resume quality pattern for future recall.

        Args:
            pattern_id: Unique pattern identifier
            pattern_data: Quality pattern data (structure, content, etc.)

        Returns:
            True if cached successfully
        """
        cache_key = f"resume_quality:{pattern_id}"
        return self.ml_cache_set(cache_key, pattern_data)

    def ml_recall_resume_quality_pattern(self, pattern_id: str) -> dict[str, Any] | None:
        """
        Recall a cached resume quality pattern.

        Args:
            pattern_id: Unique pattern identifier

        Returns:
            Cached pattern data or None
        """
        cache_key = f"resume_quality:{pattern_id}"
        return self.ml_cache_get(cache_key)

    def ml_cache_ats_compatibility(
        self,
        ats_system: str,
        compatibility_data: dict[str, Any],
    ) -> bool:
        """
        Cache ATS compatibility requirements for future reference.

        Args:
            ats_system: ATS system identifier
            compatibility_data: Compatibility requirements and fixes

        Returns:
            True if cached successfully
        """
        cache_key = f"ats_compat:{ats_system}"
        return self.ml_cache_set(cache_key, compatibility_data)

    def ml_recall_ats_compatibility(self, ats_system: str) -> dict[str, Any] | None:
        """
        Recall cached ATS compatibility requirements.

        Args:
            ats_system: ATS system identifier

        Returns:
            Cached compatibility data or None
        """
        cache_key = f"ats_compat:{ats_system}"
        return self.ml_cache_get(cache_key)

    def ml_cache_section_balance(
        self,
        job_type: str,
        balance_data: dict[str, Any],
    ) -> bool:
        """
        Cache optimal section balance for a job type.

        Args:
            job_type: Job type identifier
            balance_data: Section balance recommendations

        Returns:
            True if cached successfully
        """
        cache_key = f"section_balance:{job_type}"
        return self.ml_cache_set(cache_key, balance_data)

    def ml_recall_section_balance(self, job_type: str) -> dict[str, Any] | None:
        """
        Recall cached section balance recommendations.

        Args:
            job_type: Job type identifier

        Returns:
            Cached balance data or None
        """
        cache_key = f"section_balance:{job_type}"
        return self.ml_cache_get(cache_key)

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
            True if pattern is valid for apps_rg domain, False otherwise
        """
        if self._guardrails is None:
            self._initialize_guardrails()
        return self._guardrails.validate_domain_isolation("apps_rg", pattern)

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
        return self._guardrails.check_rate_limit("apps_rg", operation)

    def guardrails_get_stats(self) -> dict[str, Any]:
        """Get guardrails statistics for monitoring."""
        if self._guardrails is None:
            self._initialize_guardrails()
        return self._guardrails.get_stats()
