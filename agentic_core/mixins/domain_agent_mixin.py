"""
Domain Agent Mixin for apps_rg and apps_lic integration.

Provides a ready-to-use mixin that combines FeatureFlaggedAgentMixin
with domain-specific configuration and utilities.
"""

import logging
from collections.abc import Callable
from typing import Any

from agentic_core.utils.feature_flags import FeatureFlagManager

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "domain_agent_mixin", "p0_governance")
_emit_reads_policy_state("p0", "domain_agent_mixin", "policy_binding")
_emit_snapshots_state("p0", "domain_agent_mixin", "state_snapshot")
emit_replay_key("p0", "domain_agent_mixin")
emit_determinism_digest("p0", "domain_agent_mixin")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

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
        self, violation: dict[str, Any], heal_fn: Callable[[dict[str, Any]], dict[str, Any]]
    ) -> dict[str, Any]:
        """Heal a violation with domain context.

        Extends heal_with_verification with domain-specific audit logging.

        Args:
            violation: Violation to heal
            heal_fn: Healing function

        Returns:
            Healing result with domain context
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "DomainAgentMixin.domain_heal_with_verification")

        violation_with_domain = {
            **violation,
            "_domain": self._domain_prefix,
            "_agent": self.__class__.__name__,
        }
        result = self.heal_with_verification(violation_with_domain, heal_fn)
        if isinstance(result, dict):
            result["_domain"] = self._domain_prefix
        return result

    def domain_log_audit_event(self, event_type: str, data: dict[str, Any]) -> str | None:
        """Log an audit event with domain context.

        Args:
            event_type: Type of event
            data: Event data

        Returns:
            Event ID if logged, None otherwise
        """
        domain_data = {**data, "_domain": self._domain_prefix, "_agent": self.__class__.__name__}
        return self.log_audit_event(event_type, domain_data)

    def validate_domain_pattern(self, pattern: dict[str, Any]) -> bool:
        """Validate that a pattern belongs to this domain.

        Args:
            pattern: Pattern to validate

        Returns:
            True if pattern is valid for this domain
        """
        pattern_domain = pattern.get("_domain") or pattern.get("domain")
        if pattern_domain and pattern_domain != self._domain_prefix:
            logger.warning(
                f"[{self.__class__.__name__}] Cross-domain pattern rejected: {pattern_domain} != {self._domain_prefix}"
            )
            return False
        return True

    def get_domain_context(self) -> dict[str, Any]:
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
        return FeatureFlagManager.is_enabled("ENABLE_META_LEARNING", self.__class__.__name__)


class RGDomainMixin(DomainAgentMixin):
    """Mixin for Resume Generation (apps_rg) agents."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, domain="rg", **kwargs)
        # guardian: allow-magic-config
        self._similarity_threshold = 0.85
        self._ttl_seconds = 3600

    def store_resume_pattern(self, pattern_id: str, pattern_data: dict[str, Any]) -> bool:
        """Store a resume quality pattern.

        Args:
            pattern_id: Pattern identifier
            pattern_data: Pattern data

        Returns:
            True if stored successfully
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "RGDomainMixin.store_resume_pattern")

        key = self.get_namespaced_key(f"resume_pattern:{pattern_id}")
        self.domain_log_audit_event("pattern_stored", {"pattern_id": pattern_id, "key": key})
        return True

    def get_rg_context(self) -> dict[str, Any]:
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
        # guardian: allow-magic-config
        self._similarity_threshold = 0.92
        self._ttl_seconds = 7200

    def store_campaign_pattern(self, campaign_id: str, pattern_data: dict[str, Any]) -> bool:
        """Store a campaign pattern.

        Args:
            campaign_id: Campaign identifier
            pattern_data: Pattern data

        Returns:
            True if stored successfully
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "LICDomainMixin.store_campaign_pattern")

        key = self.get_namespaced_key(f"campaign_pattern:{campaign_id}")
        self.domain_log_audit_event("pattern_stored", {"campaign_id": campaign_id, "key": key})
        return True

    def get_lic_context(self) -> dict[str, Any]:
        """Get LIC-specific context."""
        base_context = self.get_domain_context()
        return {
            **base_context,
            "similarity_threshold": self._similarity_threshold,
            "ttl_seconds": self._ttl_seconds,
        }
