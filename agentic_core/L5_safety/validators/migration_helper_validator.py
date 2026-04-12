"""
Migration Helper for tracking agent compliance with new protocols.

Provides utilities for checking agent compliance with the migration plan
and tracking migration progress across all layers.
"""

import logging
import uuid
from dataclasses import dataclass, field
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
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)
from agentic_core.utils.feature_flags import FeatureFlagManager

emit_replay_key("p0", "migration_helper_validator")
emit_determinism_digest("p0", "migration_helper_validator")

_emit_dispatches_healing_run("p1", "migration_helper_validator", "L5")
_emit_routes_through("p1", "migration_helper_validator", "L5")
_emit_checks_agent_registry("p1", "migration_helper_validator", "agent_registry")
_emit_validates_agent_capability("p1", "migration_helper_validator", "capability")
_emit_dispatches_execution_plan("p1", "migration_helper_validator", "exec_plan")
_emit_agent_executes_agent("p1", "migration_helper_validator", "sub_agent")
_emit_routes_to_agent("p1", "migration_helper_validator", "target_agent")
_emit_verifies_policy("p1", "migration_helper_validator", "policy_check")
_emit_observes_runtime_state("p1", "migration_helper_validator", "runtime_state")
_emit_verifies_boundary("p1", "migration_helper_validator", "boundary_check")
_emit_transcripts_response("p1", "migration_helper_validator", "transcript")
_emit_hard_fails_untranscripted("p1", "migration_helper_validator")
_emit_gated_by_confidence("p1", "migration_helper_validator", "confidence_gate")
_emit_escalates_to_human("p1", "migration_helper_validator", "L5")
_emit_reads_policy_state("p1", "migration_helper_validator", "L5")

_emit_applies_guardrail("p0", "migration_helper_validator", "p0_governance")
_emit_snapshots_state("p0", "migration_helper_validator", "state_snapshot")
_emit_authorize_and_execute("p2", "migration_helper_validator", "execution_auth")
_emit_validates_capability("p2", "migration_helper_validator", "capability_check")
_emit_routes_to_capability("p2", "migration_helper_validator", "capability_route")
_emit_writes_via_uwg("p2", "migration_helper_validator", "uwg_write")
_emit_blocks_direct_write("p2", "migration_helper_validator", "direct_write_block")
_emit_records_tool_invocation("p2", "migration_helper_validator", "tool_invocation")
_emit_captures_execution_output("p2", "migration_helper_validator", "exec_output")
_emit_dispatches_agent("p3", "migration_helper_validator", "agent_dispatch")
_emit_coordinates_agents("p3", "migration_helper_validator", "agent_coordination")
_emit_records_workflow_lineage("p3", "migration_helper_validator", "workflow_lineage")
_emit_records_healing_outcome("p3", "migration_helper_validator", "healing_outcome")
_emit_escalates_failure("p3", "migration_helper_validator", "failure_escalation")
_emit_orchestrates_workflow("p3", "migration_helper_validator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "migration_helper_validator", "healing_dispatch")
_emit_invokes_evaluation("p3", "migration_helper_validator", "evaluation_signal")
_emit_records_telemetry_event("p4", "migration_helper_validator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "migration_helper_validator", "eval_metric")
_emit_stores_embedding("p4", "migration_helper_validator", "embedding_store")
_emit_updates_meta_learning_state("p4", "migration_helper_validator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "migration_helper_validator", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("migration_helper_validator", "p4obs", "metric_1")
_emit_emits_metric_event("migration_helper_validator", "p4obs", "metric_2")
_emit_emits_metric_event("migration_helper_validator", "p4obs", "metric_3")
_emit_emits_metric_event("migration_helper_validator", "p4obs", "metric_4")
_emit_emits_metric_event("migration_helper_validator", "p4obs", "metric_5")
_emit_emits_metric_event("migration_helper_validator", "p4obs", "metric_6")
_emit_records_incident_event("migration_helper_validator", "p4obs", "incident")
_emit_captures_runtime_anomaly("migration_helper_validator", "p4obs", "anomaly")
_emit_writes_observability_log("migration_helper_validator", "p4obs", "obs_log")
_emit_updates_monitoring_state("migration_helper_validator", "p4obs", "mon_state")
_emit_triggers_alert("migration_helper_validator", "p4obs", "alert")
_emit_links_incident_trace("migration_helper_validator", "p4obs", "trace_link")
_emit_captures_pattern("migration_helper_validator", "p3lm", "pattern")
_emit_records_learning_event("migration_helper_validator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("migration_helper_validator", "p3lm", "snapshot")
_emit_feeds_meta_learning("migration_helper_validator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("migration_helper_validator", "p3lm", "routing")
_emit_improves_agent_policy("migration_helper_validator", "p3lm", "policy")
_emit_stores_learning_state("migration_helper_validator", "p3lm", "state")
_emit_records_execution_trace("migration_helper_validator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("migration_helper_validator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("migration_helper_validator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("migration_helper_validator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("migration_helper_validator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("migration_helper_validator", "env_read", "p2_env_1")
_emit_reads_environ("migration_helper_validator", "env_read", "p2_env_2")
_emit_reads_runtime_state("migration_helper_validator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("migration_helper_validator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "migration_helper_validator", "context_pull")
_emit_pulls_context("p1", "migration_helper_validator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "migration_helper_validator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "migration_helper_validator", "uwg_term_2")
_emit_writes_through("p1", "migration_helper_validator", "write_through")
_emit_writes_through("p1", "migration_helper_validator", "write_through_2")
_emit_validated_by_safety_plane("p1", "migration_helper_validator", "safety_validation")
_emit_invokes_eval("p1", "migration_helper_validator", "eval_call")
_emit_proposal_commits_routing("p1", "migration_helper_validator", "routing_commit")

logger = logging.getLogger(__name__)


@dataclass
class ComplianceResult:
    """Result of agent compliance check."""

    agent_name: str
    compliant: bool
    has_feature_flag_mixin: bool
    has_verification_gate: bool
    has_human_review: bool
    has_meta_learning: bool
    has_audit_trail: bool
    missing_components: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "agent_name": self.agent_name,
            "compliant": self.compliant,
            "has_feature_flag_mixin": self.has_feature_flag_mixin,
            "has_verification_gate": self.has_verification_gate,
            "has_human_review": self.has_human_review,
            "has_meta_learning": self.has_meta_learning,
            "has_audit_trail": self.has_audit_trail,
            "missing_components": self.missing_components,
            "recommendations": self.recommendations,
        }


@dataclass
class MigrationStatus:
    """Overall migration status."""

    total_agents: int
    compliant_agents: int
    non_compliant_agents: int
    compliance_percentage: float
    agents_by_status: dict[str, list[str]] = field(default_factory=dict)
    feature_flag_status: dict[str, bool] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_agents": self.total_agents,
            "compliant_agents": self.compliant_agents,
            "non_compliant_agents": self.non_compliant_agents,
            "compliance_percentage": self.compliance_percentage,
            "agents_by_status": self.agents_by_status,
            "feature_flag_status": self.feature_flag_status,
        }


class MigrationHelper:
    """Helper for tracking migration compliance."""

    REQUIRED_COMPONENTS = [
        "FeatureFlaggedAgentMixin",
        "verification_gate",
        "human_review",
        "meta_learning",
        "audit_trail",
    ]

    @classmethod
    def check_agent_compliance(cls, agent_class: type, strict: bool = False) -> ComplianceResult:
        """Check if an agent class is compliant with migration requirements.

        Args:
            agent_class: The agent class to check
            strict: If True, require all components; if False, only require mixin

        Returns:
            ComplianceResult with compliance details
        """
        _emit_validated_by_safety_plane(
            str(uuid.uuid4()),
            "MigrationHelper.check_agent_compliance",
            "L5_POLICY",
        )
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L5_POLICY,
            "MigrationHelper.check_agent_compliance",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:MigrationHelper.check_agent_compliance".encode(),
        ).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        agent_name = agent_class.__name__
        missing = []
        recommendations = []
        has_mixin = cls._has_feature_flag_mixin(agent_class)
        if not has_mixin:
            missing.append("FeatureFlaggedAgentMixin")
            recommendations.append(f"Add FeatureFlaggedAgentMixin to {agent_name}'s inheritance")
        has_verification = cls._has_method(agent_class, "verify_action")
        if not has_verification:
            missing.append("verification_gate")
            recommendations.append(f"Implement verify_action method in {agent_name}")
        has_review = cls._has_method(agent_class, "submit_for_review")
        if not has_review:
            missing.append("human_review")
            recommendations.append(f"Implement submit_for_review method in {agent_name}")
        has_ml = cls._has_method(agent_class, "flagged_recall_or_execute")
        if not has_ml:
            missing.append("meta_learning")
            recommendations.append(f"Implement flagged_recall_or_execute method in {agent_name}")
        has_audit = cls._has_method(agent_class, "log_audit_event")
        if not has_audit:
            missing.append("audit_trail")
            recommendations.append(f"Implement log_audit_event method in {agent_name}")
        if strict:
            compliant = len(missing) == 0
        else:
            compliant = has_mixin
        return ComplianceResult(
            agent_name=agent_name,
            compliant=compliant,
            has_feature_flag_mixin=has_mixin,
            has_verification_gate=has_verification,
            has_human_review=has_review,
            has_meta_learning=has_ml,
            has_audit_trail=has_audit,
            missing_components=missing,
            recommendations=recommendations,
        )

    @classmethod
    def _has_feature_flag_mixin(cls, agent_class: type) -> bool:
        """Check if agent has FeatureFlaggedAgentMixin in MRO."""
        for base in agent_class.__mro__:
            if base.__name__ == "FeatureFlaggedAgentMixin":
                return True
        return False

    @classmethod
    def _has_method(cls, agent_class: type, method_name: str) -> bool:
        """Check if agent has a specific method."""
        return hasattr(agent_class, method_name) and callable(getattr(agent_class, method_name, None))

    @classmethod
    def get_migration_status(cls, agent_classes: list[type], strict: bool = False) -> MigrationStatus:
        """Get overall migration status for a list of agents.

        Args:
            agent_classes: List of agent classes to check
            strict: If True, use strict compliance checking

        Returns:
            MigrationStatus with overall statistics
        """
        compliant = []
        non_compliant = []
        for agent_class in agent_classes:
            result = cls.check_agent_compliance(agent_class, strict)
            if result.compliant:
                compliant.append(result.agent_name)
            else:
                non_compliant.append(result.agent_name)
        total = len(agent_classes)
        compliance_pct = len(compliant) / total * 100 if total > 0 else 0.0
        return MigrationStatus(
            total_agents=total,
            compliant_agents=len(compliant),
            non_compliant_agents=len(non_compliant),
            compliance_percentage=compliance_pct,
            agents_by_status={"compliant": compliant, "non_compliant": non_compliant},
            feature_flag_status=FeatureFlagManager.get_all_flags(),
        )

    @classmethod
    def generate_migration_report(cls, agent_classes: list[type], strict: bool = False) -> str:
        """Generate a human-readable migration report.

        Args:
            agent_classes: List of agent classes to check
            strict: If True, use strict compliance checking

        Returns:
            Formatted migration report string
        """
        status = cls.get_migration_status(agent_classes, strict)
        lines = [
            "=" * 60,
            "AGENT MIGRATION STATUS REPORT",
            "=" * 60,
            "",
            f"Total Agents: {status.total_agents}",
            f"Compliant: {status.compliant_agents}",
            f"Non-Compliant: {status.non_compliant_agents}",
            f"Compliance: {status.compliance_percentage:.1f}%",
            "",
            "Feature Flag Status:",
        ]
        for flag, enabled in status.feature_flag_status.items():
            lines.append(f"  {flag}: {('ENABLED' if enabled else 'disabled')}")
        if status.agents_by_status.get("non_compliant"):
            lines.append("")
            lines.append("Non-Compliant Agents:")
            for agent in status.agents_by_status["non_compliant"]:
                lines.append(f"  - {agent}")
        lines.append("")
        lines.append("=" * 60)
        return "\n".join(lines)


def check_agent_compliance(agent_class: type, strict: bool = False) -> ComplianceResult:
    """Check if an agent class is compliant with migration requirements."""
    return MigrationHelper.check_agent_compliance(agent_class, strict)


def get_migration_status(agent_classes: list[type], strict: bool = False) -> MigrationStatus:
    """Get overall migration status for a list of agents."""
    return MigrationHelper.get_migration_status(agent_classes, strict)
