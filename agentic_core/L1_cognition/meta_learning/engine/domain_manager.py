"""
DomainContextManager - Domain-specific context management for Meta-Learning.

[PHASE 6] Cross-Domain Sharing Implementation

Provides:
- Domain-specific context isolation (agentic_core, apps_lic, apps_rg)
- Cross-domain pattern sharing with configurable policies
- Context inheritance and propagation
- Domain boundary enforcement
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

Logger = logging.getLogger(__name__)


class SharingPolicy(Enum):
    """Policy for cross-domain pattern sharing."""

    NONE = "none"  # No sharing allowed
    READ_ONLY = "read_only"  # Can read from other domains
    BIDIRECTIONAL = "bidirectional"  # Full sharing
    SELECTIVE = "selective"  # Share only specific pattern types


@dataclass
class DomainContext:
    """
    Context for a specific domain.

    Attributes:
        domain: Domain identifier
        parent_domain: Parent domain for inheritance (if any)
        sharing_policy: Policy for cross-domain sharing
        allowed_sources: Domains allowed to share patterns with this domain
        pattern_types_shared: Pattern types allowed for sharing (if selective)
    """

    domain: str
    parent_domain: str | None = None
    sharing_policy: SharingPolicy = SharingPolicy.NONE
    allowed_sources: list[str] = field(default_factory=list)
    pattern_types_shared: list[str] = field(default_factory=list)

    def can_read_from(self, source_domain: str) -> bool:
        """Check if this domain can read patterns from source domain."""
        if self.sharing_policy == SharingPolicy.NONE:
            return False
        if self.sharing_policy == SharingPolicy.BIDIRECTIONAL:
            return True
        if source_domain in self.allowed_sources:
            return True
        if self.parent_domain == source_domain:
            return True
        return False

    def can_share_pattern_type(self, pattern_type: str) -> bool:
        """Check if a pattern type can be shared."""
        if self.sharing_policy == SharingPolicy.NONE:
            return False
        if self.sharing_policy in (SharingPolicy.READ_ONLY, SharingPolicy.BIDIRECTIONAL):
            return True
        if self.sharing_policy == SharingPolicy.SELECTIVE:
            return pattern_type in self.pattern_types_shared
        return False


# Module-level singleton
_domain_context_manager: Any = None


@dataclass
class DomainContextManager:
    """
    Manages domain-specific contexts for Meta-Learning.

    [PHASE 6] Core Implementation

    Features:
    - Domain context registration and lookup
    - Cross-domain pattern sharing with policies
    - Context inheritance from parent domains
    - Domain boundary enforcement
    """

    # Domain contexts
    _contexts: dict[str, DomainContext] = field(default_factory=dict)

    # Cross-domain sharing statistics
    stats: dict[str, Any] = field(
        default_factory=lambda: {
            "cross_domain_reads": 0,
            "cross_domain_writes": 0,
            "sharing_denials": 0,
            "context_lookups": 0,
            "by_domain": {},
        },
    )

    def __post_init__(self) -> None:
        """Initialize default domain contexts."""
        self._initialize_default_contexts()

    def _initialize_default_contexts(self) -> None:
        """Initialize default domain contexts."""
        # agentic_core is the root domain
        self._contexts["agentic_core"] = DomainContext(
            domain="agentic_core",
            parent_domain=None,
            sharing_policy=SharingPolicy.BIDIRECTIONAL,
            allowed_sources=["apps_lic", "apps_rg"],
        )

        # apps_lic inherits from agentic_core, can read from core
        self._contexts["apps_lic"] = DomainContext(
            domain="apps_lic",
            parent_domain="agentic_core",
            sharing_policy=SharingPolicy.SELECTIVE,
            allowed_sources=["agentic_core"],
            pattern_types_shared=["healing_pattern", "compliance_rule"],
        )

        # apps_rg inherits from agentic_core, can read from core
        self._contexts["apps_rg"] = DomainContext(
            domain="apps_rg",
            parent_domain="agentic_core",
            sharing_policy=SharingPolicy.SELECTIVE,
            allowed_sources=["agentic_core"],
            pattern_types_shared=["healing_pattern", "quality_pattern"],
        )

        Logger.info("[DomainContextManager] Default contexts initialized")

    def get_context(self, domain: str) -> DomainContext | None:
        """
        Get context for a domain.

        Args:
            domain: Domain identifier

        Returns:
            DomainContext or None if not found
        """
        self.stats["context_lookups"] += 1
        return self._contexts.get(domain)

    def register_context(self, context: DomainContext) -> None:
        """
        Register a new domain context.

        Args:
            context: DomainContext to register
        """
        self._contexts[context.domain] = context
        self.stats["by_domain"][context.domain] = {
            "reads": 0,
            "writes": 0,
            "denials": 0,
        }
        Logger.info(f"[DomainContextManager] Registered context for {context.domain}")

    def can_share(
        self,
        source_domain: str,
        target_domain: str,
        pattern_type: str | None = None,
    ) -> bool:
        """
        Check if sharing is allowed between domains.

        Args:
            source_domain: Domain providing the pattern
            target_domain: Domain requesting the pattern
            pattern_type: Optional pattern type for selective sharing

        Returns:
            True if sharing is allowed
        """
        # Same domain always allowed
        if source_domain == target_domain:
            return True

        target_context = self.get_context(target_domain)
        if target_context is None:
            self.stats["sharing_denials"] += 1
            return False

        # Check if target can read from source
        if not target_context.can_read_from(source_domain):
            self.stats["sharing_denials"] += 1
            return False

        # Check pattern type if selective
        if pattern_type and not target_context.can_share_pattern_type(pattern_type):
            self.stats["sharing_denials"] += 1
            return False

        return True

    def get_shared_pattern(
        self,
        key: str,
        requesting_domain: str,
        source_domains: list[str] | None = None,
        pattern_type: str | None = None,
    ) -> tuple[Any, str | None]:
        """
        Get a pattern from any allowed domain.

        Args:
            key: Pattern key
            requesting_domain: Domain making the request
            source_domains: Optional list of domains to search
            pattern_type: Optional pattern type for filtering

        Returns:
            Tuple of (pattern_data, source_domain) or (None, None)
        """
        from agentic_core.L1_cognition.meta_learning.meta_learning_client_types import (
            get_meta_learning_client,
        )

        client = get_meta_learning_client()

        # Determine domains to search
        if source_domains is None:
            context = self.get_context(requesting_domain)
            if context:
                source_domains = [requesting_domain] + context.allowed_sources
            else:
                source_domains = [requesting_domain]

        # Search domains in order
        for domain in source_domains:
            if not self.can_share(domain, requesting_domain, pattern_type):
                continue

            value = client.cache_get(key, domain)
            if value is not None:
                self.stats["cross_domain_reads"] += 1
                self._update_domain_stats(domain, "reads")
                return value, domain

        return None, None

    def share_pattern(
        self,
        key: str,
        value: Any,
        source_domain: str,
        target_domains: list[str] | None = None,
        pattern_type: str | None = None,
    ) -> dict[str, bool]:
        """
        Share a pattern to multiple domains.

        Args:
            key: Pattern key
            value: Pattern value
            source_domain: Domain providing the pattern
            target_domains: Domains to share with (None = all allowed)
            pattern_type: Optional pattern type

        Returns:
            Dict mapping domain to success status
        """
        from agentic_core.L1_cognition.meta_learning.meta_learning_client_types import (
            get_meta_learning_client,
        )

        client = get_meta_learning_client()
        results: dict[str, bool] = {}

        # Determine target domains
        if target_domains is None:
            source_context = self.get_context(source_domain)
            if source_context and source_context.sharing_policy == SharingPolicy.BIDIRECTIONAL:
                target_domains = list(self._contexts.keys())
            else:
                target_domains = [source_domain]

        # Share to each allowed domain
        for domain in target_domains:
            if self.can_share(source_domain, domain, pattern_type):
                success = client.cache_set(key, value, domain)
                results[domain] = success
                if success:
                    self.stats["cross_domain_writes"] += 1
                    self._update_domain_stats(domain, "writes")
            else:
                results[domain] = False
                self._update_domain_stats(domain, "denials")

        return results

    def _update_domain_stats(self, domain: str, stat_type: str) -> None:
        """Update domain-specific statistics."""
        if domain not in self.stats["by_domain"]:
            self.stats["by_domain"][domain] = {"reads": 0, "writes": 0, "denials": 0}
        self.stats["by_domain"][domain][stat_type] += 1

    def get_stats(self) -> dict[str, Any]:
        """Get cross-domain sharing statistics."""
        return {
            **self.stats,
            "registered_domains": list(self._contexts.keys()),
        }

    def get_domain_hierarchy(self) -> dict[str, list[str]]:
        """Get domain hierarchy showing parent-child relationships."""
        hierarchy: dict[str, list[str]] = {}
        for domain, context in self._contexts.items():
            parent = context.parent_domain or "root"
            if parent not in hierarchy:
                hierarchy[parent] = []
            hierarchy[parent].append(domain)
        return hierarchy

    @classmethod
    def reset_instance(cls) -> None:
        """[TESTING ONLY] Reset singleton state."""
        global _domain_context_manager
        _domain_context_manager = None


def get_domain_context_manager() -> DomainContextManager:
    """Get or create the DomainContextManager singleton."""
    global _domain_context_manager
    if _domain_context_manager is None:
        _domain_context_manager = DomainContextManager()
    return _domain_context_manager
