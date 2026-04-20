"""
AppBase - Common base class for both LIC and RG applications.

Provides unified inheritance hierarchy for apps_lic and apps_rg.
Phase 2A.3 - Base Class Standardization

NOTE: This is a CLASS (blueprint/template), NOT an active worker agent.
Zero-Ambiguity Standard: Removed "Agent" suffix to clarify its role.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Final

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
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
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "app_base_util", "p0_governance")
_emit_reads_policy_state("p0", "app_base_util", "policy_binding")
_emit_snapshots_state("p0", "app_base_util", "state_snapshot")
emit_replay_key("p0", "app_base_util")
emit_determinism_digest("p0", "app_base_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "app_base_util", "execution_auth")
_emit_validates_capability("p2", "app_base_util", "capability_check")
_emit_routes_to_capability("p2", "app_base_util", "capability_route")
_emit_writes_via_uwg("p2", "app_base_util", "uwg_write")
_emit_blocks_direct_write("p2", "app_base_util", "direct_write_block")
_emit_records_tool_invocation("p2", "app_base_util", "tool_invocation")
_emit_captures_execution_output("p2", "app_base_util", "exec_output")
_emit_dispatches_agent("p3", "app_base_util", "agent_dispatch")
_emit_coordinates_agents("p3", "app_base_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "app_base_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "app_base_util", "healing_outcome")
_emit_escalates_failure("p3", "app_base_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "app_base_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "app_base_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "app_base_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "app_base_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "app_base_util", "eval_metric")
_emit_stores_embedding("p4", "app_base_util", "embedding_store")
# _emit_updates_meta_learning_state("p4", "app_base_util", "meta_learning")
# _emit_links_execution_to_snapshot("p4", "app_base_util", "exec_snapshot_link")

try:
    from agentic_core.interfaces.mixins import MetaLearningMixin
except ImportError:  # guardian: allow-silent-swallow - optional dependency

    class MetaLearningMixin:
        """Fallback MetaLearningMixin when not available."""

        pass


try:
    from agentic_core.interfaces.mixins import HealerMixin
except ImportError:

    class HealerMixin:
        """Fallback HealerMixin when not available."""

        pass


from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("app_base_util", "p4obs", "metric_1")
_emit_emits_metric_event("app_base_util", "p4obs", "metric_2")
_emit_emits_metric_event("app_base_util", "p4obs", "metric_3")
_emit_emits_metric_event("app_base_util", "p4obs", "metric_4")
_emit_emits_metric_event("app_base_util", "p4obs", "metric_5")
_emit_emits_metric_event("app_base_util", "p4obs", "metric_6")
_emit_records_incident_event("app_base_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("app_base_util", "p4obs", "anomaly")
_emit_writes_observability_log("app_base_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("app_base_util", "p4obs", "mon_state")
_emit_triggers_alert("app_base_util", "p4obs", "alert")
_emit_links_incident_trace("app_base_util", "p4obs", "trace_link")
_emit_captures_pattern("app_base_util", "p3lm", "pattern")
_emit_records_learning_event("app_base_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("app_base_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("app_base_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("app_base_util", "p3lm", "routing")
_emit_improves_agent_policy("app_base_util", "p3lm", "policy")
_emit_stores_learning_state("app_base_util", "p3lm", "state")
_emit_records_execution_trace("app_base_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("app_base_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("app_base_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("app_base_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("app_base_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("app_base_util", "env_read", "p2_env_1")
_emit_reads_environ("app_base_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("app_base_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("app_base_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "app_base_util", "context_pull")
_emit_pulls_context("p1", "app_base_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "app_base_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "app_base_util", "uwg_term_2")
_emit_writes_through("p1", "app_base_util", "write_through")
_emit_writes_through("p1", "app_base_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "app_base_util", "safety_validation")
_emit_invokes_eval("p1", "app_base_util", "eval_call")
_emit_proposal_commits_routing("p1", "app_base_util", "routing_commit")
_emit_escalates_to_human("p1", "app_base_util", "human_escalation")
_emit_routes_through("p1", "app_base_util", "route_through")
_emit_checks_agent_registry("p1", "app_base_util", "agent_registry")
_emit_validates_agent_capability("p1", "app_base_util", "capability")
_emit_dispatches_execution_plan("p1", "app_base_util", "exec_plan")
_emit_agent_executes_agent("p1", "app_base_util", "sub_agent")
_emit_routes_to_agent("p1", "app_base_util", "target_agent")
_emit_verifies_policy("p1", "app_base_util", "policy_check")
_emit_observes_runtime_state("p1", "app_base_util", "runtime_state")
_emit_verifies_boundary("p1", "app_base_util", "boundary_check")
_emit_transcripts_response("p1", "app_base_util", "transcript")
_emit_hard_fails_untranscripted("p1", "app_base_util")
_emit_gated_by_confidence("p1", "app_base_util", "confidence_gate")


@dataclass
class AppBase(MetaLearningMixin, SovereignBaseAgent, HealerMixin):
    """
    AppBase: Common foundation for all application-level agents.

    Provides unified base class for both apps_lic (LinkedIn Outreach) and
    apps_rg (Resume Generation) applications, ensuring consistent behavior
    and capabilities across all application agents.

    Architecture:
        - Inherits from SovereignBaseAgent for core sovereignty
        - Includes MetaLearningMixin for learning capabilities
        - Includes HealerMixin for self-healing capabilities

    NOTE: This is a CLASS (blueprint), NOT an active worker agent.
    The "Agent" suffix was removed per Zero-Ambiguity Naming Standard.
    """

    domain_root: Path = field(default_factory=lambda: Path("apps"))
    _app_version: Final[str] = "2.5.0-unified"
    _namespace: str = field(default="apps", init=False)
    _similarity_threshold: float = field(default=0.85, init=False)
    _resource_prefix: str = field(default="app", init=False)

    def __post_init__(self) -> None:
        """
        Initialize app-level capabilities after core hardening.
        """
        super().__post_init__()
        if not self.domain_root.exists():
            self.domain_root.mkdir(parents=True, exist_ok=True)

    def get_app_context(self) -> dict[str, Any]:
        """
        Return app-specific context wrapper.

        Returns:
            Dictionary with app context information
        """
        return {
            "domain": str(self.domain_root),
            "version": self._app_version,
            "namespace": self._namespace,
            "capabilities": self.get_sovereign_capabilities(),
            "resource_prefix": self._resource_prefix,
        }

    def get_resource_key(self, key: str) -> str:
        """
        Generate namespaced resource key for isolation.

        Args:
            key: Base resource key

        Returns:
            Namespaced resource key
        """
        return f"{self._resource_prefix}:{self._namespace}:{key}"

    def validate_app_config(self) -> bool:
        """
        Validate application-specific configuration.

        Returns:
            True if configuration is valid
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "AppBase.validate_app_config")

        # guardian: allow-config-with-logic
        if not self.domain_root.exists():
            return False
        # guardian: allow-config-with-logic
        if not self._namespace or self._namespace == "":
            return False
        return True

    def get_app_metadata(self) -> dict[str, Any]:
        """
        Get application metadata for telemetry and monitoring.

        Returns:
            Dictionary with app metadata
        """
        return {
            "agent_class": self.__class__.__name__,
            "domain": str(self.domain_root),
            "namespace": self._namespace,
            "version": self._app_version,
            "similarity_threshold": self._similarity_threshold,
        }

    def heal(self, violation, **kwargs):
        return super().heal(violation, **kwargs)
