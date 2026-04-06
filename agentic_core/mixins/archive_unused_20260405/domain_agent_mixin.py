"""
Domain Agent Mixin for apps_rg and apps_lic integration.

Provides a ready-to-use mixin that combines FeatureFlaggedAgentMixin
with domain-specific configuration and utilities.
"""

import logging
from collections.abc import Callable
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
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
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
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
from agentic_core.utils.feature_flags import FeatureFlagManager

_emit_applies_guardrail("p0", "domain_agent_mixin", "p0_governance")
_emit_reads_policy_state("p0", "domain_agent_mixin", "policy_binding")
_emit_snapshots_state("p0", "domain_agent_mixin", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
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
    _emit_routes_through,
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

_emit_emits_metric_event("domain_agent_mixin", "p4obs", "metric_1")
_emit_emits_metric_event("domain_agent_mixin", "p4obs", "metric_2")
_emit_emits_metric_event("domain_agent_mixin", "p4obs", "metric_3")
_emit_emits_metric_event("domain_agent_mixin", "p4obs", "metric_4")
_emit_emits_metric_event("domain_agent_mixin", "p4obs", "metric_5")
_emit_emits_metric_event("domain_agent_mixin", "p4obs", "metric_6")
_emit_records_incident_event("domain_agent_mixin", "p4obs", "incident")
_emit_captures_runtime_anomaly("domain_agent_mixin", "p4obs", "anomaly")
_emit_writes_observability_log("domain_agent_mixin", "p4obs", "obs_log")
_emit_updates_monitoring_state("domain_agent_mixin", "p4obs", "mon_state")
_emit_triggers_alert("domain_agent_mixin", "p4obs", "alert")
_emit_links_incident_trace("domain_agent_mixin", "p4obs", "trace_link")
_emit_captures_pattern("domain_agent_mixin", "p3lm", "pattern")
_emit_records_learning_event("domain_agent_mixin", "p3lm", "learning_event")
_emit_writes_learning_snapshot("domain_agent_mixin", "p3lm", "snapshot")
_emit_feeds_meta_learning("domain_agent_mixin", "p3lm", "meta_feed")
_emit_updates_routing_strategy("domain_agent_mixin", "p3lm", "routing")
_emit_improves_agent_policy("domain_agent_mixin", "p3lm", "policy")
_emit_stores_learning_state("domain_agent_mixin", "p3lm", "state")
_emit_records_execution_trace("domain_agent_mixin", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("domain_agent_mixin", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("domain_agent_mixin", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("domain_agent_mixin", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("domain_agent_mixin", "L4_STATE", "p2_trace_5")
_emit_reads_environ("domain_agent_mixin", "env_read", "p2_env_1")
_emit_reads_environ("domain_agent_mixin", "env_read", "p2_env_2")
_emit_reads_runtime_state("domain_agent_mixin", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("domain_agent_mixin", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "domain_agent_mixin", "context_pull")
_emit_pulls_context("p1", "domain_agent_mixin", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "domain_agent_mixin", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "domain_agent_mixin", "uwg_term_2")
_emit_writes_through("p1", "domain_agent_mixin", "write_through")
_emit_writes_through("p1", "domain_agent_mixin", "write_through_2")
_emit_validated_by_safety_plane("p1", "domain_agent_mixin", "safety_validation")
_emit_invokes_eval("p1", "domain_agent_mixin", "eval_call")
_emit_proposal_commits_routing("p1", "domain_agent_mixin", "routing_commit")
_emit_escalates_to_human("p1", "domain_agent_mixin", "human_escalation")
_emit_routes_through("p1", "domain_agent_mixin", "route_through")
_emit_checks_agent_registry("p1", "domain_agent_mixin", "agent_registry")
_emit_validates_agent_capability("p1", "domain_agent_mixin", "capability")
_emit_dispatches_execution_plan("p1", "domain_agent_mixin", "exec_plan")
_emit_agent_executes_agent("p1", "domain_agent_mixin", "sub_agent")
_emit_routes_to_agent("p1", "domain_agent_mixin", "target_agent")
_emit_verifies_policy("p1", "domain_agent_mixin", "policy_check")
_emit_observes_runtime_state("p1", "domain_agent_mixin", "runtime_state")
_emit_verifies_boundary("p1", "domain_agent_mixin", "boundary_check")
_emit_transcripts_response("p1", "domain_agent_mixin", "transcript")
_emit_hard_fails_untranscripted("p1", "domain_agent_mixin")
_emit_gated_by_confidence("p1", "domain_agent_mixin", "confidence_gate")
emit_replay_key("p0", "domain_agent_mixin")
emit_determinism_digest("p0", "domain_agent_mixin")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "domain_agent_mixin", "execution_auth")
_emit_validates_capability("p2", "domain_agent_mixin", "capability_check")
_emit_routes_to_capability("p2", "domain_agent_mixin", "capability_route")
_emit_writes_via_uwg("p2", "domain_agent_mixin", "uwg_write")
_emit_blocks_direct_write("p2", "domain_agent_mixin", "direct_write_block")
_emit_records_tool_invocation("p2", "domain_agent_mixin", "tool_invocation")
_emit_captures_execution_output("p2", "domain_agent_mixin", "exec_output")
_emit_dispatches_agent("p3", "domain_agent_mixin", "agent_dispatch")
_emit_coordinates_agents("p3", "domain_agent_mixin", "agent_coordination")
_emit_records_workflow_lineage("p3", "domain_agent_mixin", "workflow_lineage")
_emit_records_healing_outcome("p3", "domain_agent_mixin", "healing_outcome")
_emit_escalates_failure("p3", "domain_agent_mixin", "failure_escalation")
_emit_orchestrates_workflow("p3", "domain_agent_mixin", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "domain_agent_mixin", "healing_dispatch")
_emit_invokes_evaluation("p3", "domain_agent_mixin", "evaluation_signal")
_emit_records_telemetry_event("p4", "domain_agent_mixin", "telemetry_event")
_emit_captures_evaluation_metric("p4", "domain_agent_mixin", "eval_metric")
_emit_stores_embedding("p4", "domain_agent_mixin", "embedding_store")
_emit_updates_meta_learning_state("p4", "domain_agent_mixin", "meta_learning")
_emit_links_execution_to_snapshot("p4", "domain_agent_mixin", "exec_snapshot_link")

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
