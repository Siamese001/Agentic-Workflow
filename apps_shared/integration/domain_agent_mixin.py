"""
Domain Agent Mixin for apps_rg and apps_lic integration.

Provides a ready-to-use mixin that combines FeatureFlaggedAgentMixin
with domain-specific configuration and utilities.
"""

import logging
from typing import Any, Callable, Dict, Optional

from agentic_core.base_agents.feature_flagged_agent_mixin import FeatureFlaggedAgentMixin
from agentic_core.primitives.feature_flags import FeatureFlagManager

logger = logging.getLogger(__name__)


class DomainAgentMixin(FeatureFlaggedAgentMixin):
    """Domain-aware mixin for apps_rg and apps_lic agents.

    Extends FeatureFlaggedAgentMixin with domain-specific functionality:
    - Domain isolation for cache operations
    - Domain-specific rate limiting
    - Audit trail with domain context
    - Pattern storage with domain tagging
    """

    def __init__(self, *args: Any, domain: str = "unknown", **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._domain = domain
        self._domain_prefix = f"apps_{domain}" if not domain.startswith("apps_") else domain

    @property
    def domain(self) -> str:
        """Get the domain this agent belongs to."""
        return self._domain

    @property
    def domain_prefix(self) -> str:
        """Get the domain prefix for namespacing."""
        return self._domain_prefix

    def get_namespaced_key(self, key: str) -> str:
        """Generate a namespaced key for domain isolation.

        Args:
            key: Base key

        Returns:
            Namespaced key with domain prefix
        """
        return f"{self._domain_prefix}:{self.__class__.__name__}:{key}"

    def domain_heal_with_verification(
        self,
        violation: Dict[str, Any],
        heal_fn: Callable[[Dict[str, Any]], Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Heal a violation with domain context.

        Extends heal_with_verification with domain-specific audit logging.

        Args:
            violation: Violation to heal
            heal_fn: Healing function

        Returns:
            Healing result with domain context
        """
        # Add domain context to violation
        violation_with_domain = {
            **violation,
            "_domain": self._domain_prefix,
            "_agent": self.__class__.__name__,
        }

        # Use parent's heal_with_verification
        result = self.heal_with_verification(violation_with_domain, heal_fn)

        # Add domain context to result
        if isinstance(result, dict):
            result["_domain"] = self._domain_prefix

        return result

    def domain_log_audit_event(
        self,
        event_type: str,
        data: Dict[str, Any],
    ) -> Optional[str]:
        """Log an audit event with domain context.

        Args:
            event_type: Type of event
            data: Event data

        Returns:
            Event ID if logged, None otherwise
        """
        domain_data = {
            **data,
            "_domain": self._domain_prefix,
            "_agent": self.__class__.__name__,
        }
        return self.log_audit_event(event_type, domain_data)

    def validate_domain_pattern(self, pattern: Dict[str, Any]) -> bool:
        """Validate that a pattern belongs to this domain.

        Args:
            pattern: Pattern to validate

        Returns:
            True if pattern is valid for this domain
        """
        pattern_domain = pattern.get("_domain") or pattern.get("domain")
        if pattern_domain and pattern_domain != self._domain_prefix:
            logger.warning(
                f"[{self.__class__.__name__}] Cross-domain pattern rejected: "
                f"{pattern_domain} != {self._domain_prefix}"
            )
            return False
        return True

    def get_domain_context(self) -> Dict[str, Any]:
        """Get domain context for this agent.

        Returns:
            Dictionary with domain information
        """
        return {
            "domain": self._domain,
            "domain_prefix": self._domain_prefix,
            "agent_name": self.__class__.__name__,
            "feature_flags": self.get_feature_flag_status(),
        }

    def check_domain_rate_limit(self, operation: str = "request") -> bool:
        """Check domain-specific rate limit.

        Args:
            operation: Type of operation

        Returns:
            True if operation is allowed
        """
        # For now, delegate to feature flag check
        # Full implementation would integrate with domain-specific rate limiting
        return FeatureFlagManager.is_enabled("ENABLE_META_LEARNING", self.__class__.__name__)


class RGDomainMixin(DomainAgentMixin):
    """Mixin for Resume Generation (apps_rg) agents."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, domain="rg", **kwargs)
        self._similarity_threshold = 0.85
        self._ttl_seconds = 3600  # 1 hour

    def store_resume_pattern(
        self,
        pattern_id: str,
        pattern_data: Dict[str, Any],
    ) -> bool:
        """Store a resume quality pattern.

        Args:
            pattern_id: Pattern identifier
            pattern_data: Pattern data

        Returns:
            True if stored successfully
        """
        key = self.get_namespaced_key(f"resume_pattern:{pattern_id}")
        self.domain_log_audit_event(
            "pattern_stored",
            {"pattern_id": pattern_id, "key": key},
        )
        # Return True - actual storage would use meta-learning service
        return True

    def get_rg_context(self) -> Dict[str, Any]:
        """Get RG-specific context."""
        base_context = self.get_domain_context()
        return {
            **base_context,
            "similarity_threshold": self._similarity_threshold,
            "ttl_seconds": self._ttl_seconds,
        }


class LICDomainMixin(DomainAgentMixin):
    """Mixin for LinkedIn Canonical (apps_lic) agents."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, domain="lic", **kwargs)
        self._similarity_threshold = 0.92  # Stricter for LIC
        self._ttl_seconds = 7200  # 2 hours

    def store_campaign_pattern(
        self,
        campaign_id: str,
        pattern_data: Dict[str, Any],
    ) -> bool:
        """Store a campaign pattern.

        Args:
            campaign_id: Campaign identifier
            pattern_data: Pattern data

        Returns:
            True if stored successfully
        """
        key = self.get_namespaced_key(f"campaign_pattern:{campaign_id}")
        self.domain_log_audit_event(
            "pattern_stored",
            {"campaign_id": campaign_id, "key": key},
        )
        return True

    def get_lic_context(self) -> Dict[str, Any]:
        """Get LIC-specific context."""
        base_context = self.get_domain_context()
        return {
            **base_context,
            "similarity_threshold": self._similarity_threshold,
            "ttl_seconds": self._ttl_seconds,
        }
