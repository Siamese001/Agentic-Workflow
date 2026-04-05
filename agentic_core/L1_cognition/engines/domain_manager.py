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
from typing import Any

from agentic_core.L0_routing.config import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
)
from agentic_core.L1_cognition.types.domain_types import (
    DomainContext,
    SharingPolicy,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

Logger = logging.getLogger(__name__)


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
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(
            str(_uuid.uuid4()), "DomainContextManager._initialize_default_contexts", "state_snapshot"
        )
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(
            str(_uuid.uuid4()), "DomainContextManager._initialize_default_contexts", "p0_governance"
        )
        # agentic_core is the root domain
        self._contexts[AGENTIC_CORE_DIR] = DomainContext(
            domain=AGENTIC_CORE_DIR,
            parent_domain=None,
            sharing_policy=SharingPolicy.BIDIRECTIONAL,
            allowed_sources=[APPS_LIC_DIR, APPS_RG_DIR],
        )

        # apps_lic inherits from agentic_core, can read from core
        self._contexts[APPS_LIC_DIR] = DomainContext(
            domain=APPS_LIC_DIR,
            parent_domain=AGENTIC_CORE_DIR,
            sharing_policy=SharingPolicy.SELECTIVE,
            allowed_sources=[AGENTIC_CORE_DIR],
            pattern_types_shared=["healing_pattern", "compliance_rule"],
        )

        # apps_rg inherits from agentic_core, can read from core
        self._contexts[APPS_RG_DIR] = DomainContext(
            domain=APPS_RG_DIR,
            parent_domain=AGENTIC_CORE_DIR,
            sharing_policy=SharingPolicy.SELECTIVE,
            allowed_sources=[AGENTIC_CORE_DIR],
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
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L1_REASONING, "DomainContextManager.get_context"
        )

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
        from agentic_core.L1_cognition.reasoning.meta_learning_client_types import (
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
        from agentic_core.L1_cognition.reasoning.meta_learning_client_types import (
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
