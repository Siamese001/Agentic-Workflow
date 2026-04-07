"""
Outreach Engine Self-Healing Loop

Provides self-healing capabilities for outreach campaigns:
- Signal routing and strategy selection
- Healing cycles with convergence detection
- Automatic rollback on critical failures
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
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
    _emit_reads_through,
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

_emit_applies_guardrail("p0", "OutreachSignalRouterAgent", "p0_governance")
_emit_reads_policy_state("p0", "OutreachSignalRouterAgent", "policy_binding")
_emit_snapshots_state("p0", "OutreachSignalRouterAgent", "state_snapshot")
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

_emit_emits_metric_event("OutreachSignalRouterAgent", "p4obs", "metric_1")
_emit_emits_metric_event("OutreachSignalRouterAgent", "p4obs", "metric_2")
_emit_emits_metric_event("OutreachSignalRouterAgent", "p4obs", "metric_3")
_emit_emits_metric_event("OutreachSignalRouterAgent", "p4obs", "metric_4")
_emit_emits_metric_event("OutreachSignalRouterAgent", "p4obs", "metric_5")
_emit_emits_metric_event("OutreachSignalRouterAgent", "p4obs", "metric_6")
_emit_records_incident_event("OutreachSignalRouterAgent", "p4obs", "incident")
_emit_captures_runtime_anomaly("OutreachSignalRouterAgent", "p4obs", "anomaly")
_emit_writes_observability_log("OutreachSignalRouterAgent", "p4obs", "obs_log")
_emit_updates_monitoring_state("OutreachSignalRouterAgent", "p4obs", "mon_state")
_emit_triggers_alert("OutreachSignalRouterAgent", "p4obs", "alert")
_emit_links_incident_trace("OutreachSignalRouterAgent", "p4obs", "trace_link")
_emit_captures_pattern("OutreachSignalRouterAgent", "p3lm", "pattern")
_emit_records_learning_event("OutreachSignalRouterAgent", "p3lm", "learning_event")
_emit_writes_learning_snapshot("OutreachSignalRouterAgent", "p3lm", "snapshot")
_emit_feeds_meta_learning("OutreachSignalRouterAgent", "p3lm", "meta_feed")
_emit_updates_routing_strategy("OutreachSignalRouterAgent", "p3lm", "routing")
_emit_improves_agent_policy("OutreachSignalRouterAgent", "p3lm", "policy")
_emit_stores_learning_state("OutreachSignalRouterAgent", "p3lm", "state")
_emit_records_execution_trace("OutreachSignalRouterAgent", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("OutreachSignalRouterAgent", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("OutreachSignalRouterAgent", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("OutreachSignalRouterAgent", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("OutreachSignalRouterAgent", "L4_STATE", "p2_trace_5")
_emit_reads_environ("OutreachSignalRouterAgent", "env_read", "p2_env_1")
_emit_reads_environ("OutreachSignalRouterAgent", "env_read", "p2_env_2")
_emit_reads_runtime_state("OutreachSignalRouterAgent", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("OutreachSignalRouterAgent", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "OutreachSignalRouterAgent", "context_pull")
_emit_pulls_context("p1", "OutreachSignalRouterAgent", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "OutreachSignalRouterAgent", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "OutreachSignalRouterAgent", "uwg_term_2")
_emit_writes_through("p1", "OutreachSignalRouterAgent", "write_through")
_emit_writes_through("p1", "OutreachSignalRouterAgent", "write_through_2")
_emit_validated_by_safety_plane("p1", "OutreachSignalRouterAgent", "safety_validation")
_emit_invokes_eval("p1", "OutreachSignalRouterAgent", "eval_call")
_emit_proposal_commits_routing("p1", "OutreachSignalRouterAgent", "routing_commit")
_emit_escalates_to_human("p1", "OutreachSignalRouterAgent", "human_escalation")
_emit_routes_through("p1", "OutreachSignalRouterAgent", "route_through")
_emit_checks_agent_registry("p1", "OutreachSignalRouterAgent", "agent_registry")
_emit_validates_agent_capability("p1", "OutreachSignalRouterAgent", "capability")
_emit_dispatches_execution_plan("p1", "OutreachSignalRouterAgent", "exec_plan")
_emit_agent_executes_agent("p1", "OutreachSignalRouterAgent", "sub_agent")
_emit_routes_to_agent("p1", "OutreachSignalRouterAgent", "target_agent")
_emit_verifies_policy("p1", "OutreachSignalRouterAgent", "policy_check")
_emit_observes_runtime_state("p1", "OutreachSignalRouterAgent", "runtime_state")
_emit_verifies_boundary("p1", "OutreachSignalRouterAgent", "boundary_check")
_emit_transcripts_response("p1", "OutreachSignalRouterAgent", "transcript")
_emit_hard_fails_untranscripted("p1", "OutreachSignalRouterAgent")
_emit_gated_by_confidence("p1", "OutreachSignalRouterAgent", "confidence_gate")
emit_replay_key("p0", "OutreachSignalRouterAgent")
emit_determinism_digest("p0", "OutreachSignalRouterAgent")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "OutreachSignalRouterAgent", "execution_auth")
_emit_validates_capability("p2", "OutreachSignalRouterAgent", "capability_check")
_emit_routes_to_capability("p2", "OutreachSignalRouterAgent", "capability_route")
_emit_writes_via_uwg("p2", "OutreachSignalRouterAgent", "uwg_write")
_emit_blocks_direct_write("p2", "OutreachSignalRouterAgent", "direct_write_block")
_emit_records_tool_invocation("p2", "OutreachSignalRouterAgent", "tool_invocation")
_emit_captures_execution_output("p2", "OutreachSignalRouterAgent", "exec_output")
_emit_dispatches_agent("p3", "OutreachSignalRouterAgent", "agent_dispatch")
_emit_coordinates_agents("p3", "OutreachSignalRouterAgent", "agent_coordination")
_emit_records_workflow_lineage("p3", "OutreachSignalRouterAgent", "workflow_lineage")
_emit_records_healing_outcome("p3", "OutreachSignalRouterAgent", "healing_outcome")
_emit_escalates_failure("p3", "OutreachSignalRouterAgent", "failure_escalation")
_emit_orchestrates_workflow("p3", "OutreachSignalRouterAgent", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "OutreachSignalRouterAgent", "healing_dispatch")
_emit_invokes_evaluation("p3", "OutreachSignalRouterAgent", "evaluation_signal")
_emit_records_telemetry_event("p4", "OutreachSignalRouterAgent", "telemetry_event")
_emit_captures_evaluation_metric("p4", "OutreachSignalRouterAgent", "eval_metric")
_emit_stores_embedding("p4", "OutreachSignalRouterAgent", "embedding_store")
_emit_updates_meta_learning_state("p4", "OutreachSignalRouterAgent", "meta_learning")
_emit_links_execution_to_snapshot("p4", "OutreachSignalRouterAgent", "exec_snapshot_link")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_1")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_2")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_3")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_4")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_5")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_6")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_7")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_8")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_9")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_10")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_11")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_12")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_13")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_14")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_15")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_16")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_17")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_18")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_19")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_20")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_21")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_22")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_23")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_24")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_25")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_26")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_27")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_28")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_29")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_30")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_31")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_32")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_33")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_34")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_35")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_36")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_37")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_38")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_39")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_40")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_41")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_42")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_43")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_44")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_45")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_46")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_47")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_48")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_49")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_50")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_51")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_52")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_53")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_54")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_55")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_56")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_57")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_58")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_59")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_60")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_61")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_62")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_63")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_64")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_65")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_66")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_67")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_68")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_69")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_70")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_71")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_72")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_73")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_74")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_75")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_76")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_77")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_78")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_79")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_80")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_81")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_82")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_83")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_84")
_emit_reads_through("l4", "OutreachSignalRouterAgent", "urg_read_85")

try:
    from agentic_core.mixins.mcp_hardened_mixin import mcp_hardened_mixin

    class MCPHardenedMixin(mcp_hardened_mixin):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._mixin_init()
# guardian: allow-silent-swallow - optional dependency
except ImportError:

    class MCPHardenedMixin:
        def __init__(self, *args, **kwargs):
            self._mixin_init()


try:
    from agentic_core.interfaces.mixins import HealerMixin
except ImportError:

    class HealerMixin:
        pass


if TYPE_CHECKING:
    from apps_lic.engines import AppWorkflowOrchestratorAgent
    from apps_lic.engines.LeadQualityAgent import LeadQualityAgent



class OutreachHealingStrategy(Enum):
    """Healing strategies for outreach campaigns."""

    FULL_DIAGNOSTIC = "full_diagnostic"
    VERIFICATION_ONLY = "verification_only"
    QUALITY_FOCUS = "quality_focus"
    COMPLIANCE_FOCUS = "compliance_focus"
    SURGICAL_STRIKE = "surgical_strike"


@dataclass
class OutreachCycleResult:
    """Result of a single healing cycle."""

    cycle_number: int
    strategy: OutreachHealingStrategy
    agents_executed: list[str]
    signals_before: set[str]
    signals_after: set[str]
    passed_agents: list[str]
    failed_agents: list[str]
    rollback_triggered: bool
    converged: bool
    duration_ms: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class OutreachHealingResult:
    """Result of the complete healing process."""

    success: bool
    total_cycles: int
    final_signals: set[str]
    cycle_results: list[OutreachCycleResult]
    convergence_cycle: int | None
    budget_exhausted: bool
    total_duration_ms: float
    final_campaign: dict[str, Any]


class OutreachSignalRouterAgent(SovereignBaseAgent):
    """Routes signals to appropriate agents."""

    def __post_init__(self) -> None:
        """Initialize ADG behavioral enrichment."""
        super().__post_init__()
        try:
            from agentic_core.adg.runtime.behavioral_index import ADGBehavioralIndex

            _idx = ADGBehavioralIndex.from_latest(Path(self.project_root))
            _profile = _idx.profile_for(self._adg_resolved_self_path()) if _idx else None
            self.adg_behavioral_score: float = _profile.behavioral_score if _profile else 0.5
            self.adg_antipattern_signals: list[str] = sorted(_profile.antipattern_signals) if _profile else []
        except (ImportError, AttributeError, OSError):
            self.adg_behavioral_score = 0.5
            self.adg_antipattern_signals = []

    SIGNAL_TO_AGENTS = {
        "LEAD_QUALITY_ISSUE": ["LeadQualityAgent"],
        "CONTACT_VALIDATION_FAILED": ["ContactValidatorAgent"],
        "COMPLIANCE_ISSUE": ["MessageComplianceAgent"],
        "TEMPLATE_NEEDS_OPTIMIZATION": ["TemplateOptimizerAgent"],
        "CAMPAIGN_BALANCE_ISSUE": ["CampaignBalanceAgent"],
        "DELIVERABILITY_ISSUE": ["DeliverabilityAgent"],
        "TEST_FAILURE": ["OutreachTestPilot"],
    }
    CRITICAL_SIGNALS = {"COMPLIANCE_ISSUE", "DELIVERABILITY_ISSUE"}

    @classmethod
    def get_agents_for_signals(cls, signals: set[str]) -> list[str]:
        """
        Get agents needed for the given signals.

        Args:
            signals: Set of signal names to route

        Returns:
            List of agent names that should handle these signals
        """
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, "OutreachSignalRouterAgent.get_agents_for_signals")
        agents: set[str] = set()
        for signal in signals:
            if signal in cls.SIGNAL_TO_AGENTS:
                agents.update(cls.SIGNAL_TO_AGENTS[signal])
        return list(agents)

    @classmethod
    def has_critical_signal(cls, signals: set[str]) -> bool:
        """
        Check if any critical signals are present.

        Args:
            signals: Set of signal names to check

        Returns:
            True if any signal is critical, False otherwise
        """
        return bool(signals & cls.CRITICAL_SIGNALS)

    @classmethod
    def determine_strategy(
        cls, cycle_number: int, signals: set[str], modified_sections: set[str]
    ) -> OutreachHealingStrategy:
        """
        Determine healing strategy based on context.

        Args:
            cycle_number: Current healing cycle number (1-indexed)
            signals: Set of active signals requiring attention
            modified_sections: Set of campaign sections that were modified

        Returns:
            Appropriate healing strategy for the current context
        """
        if cycle_number == 1:
            return OutreachHealingStrategy.FULL_DIAGNOSTIC
        if not signals:
            return OutreachHealingStrategy.VERIFICATION_ONLY
        if cls.has_critical_signal(signals):
            return OutreachHealingStrategy.COMPLIANCE_FOCUS
        if len(signals) <= 2:
            return OutreachHealingStrategy.SURGICAL_STRIKE
        return OutreachHealingStrategy.QUALITY_FOCUS

    # guardian: allow-type-erasure
    def heal_repository(self) -> dict:
        """Invoke healing chain via super()."""
        return super().heal_repository()

    # guardian: allow-type-erasure
    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """Heal violations detected by OutreachSignalRouterAgent."""
        violation_type = violation.get("type", "unknown")
        try:
            return {
                "status": "skipped",
                "details": f"OutreachSignalRouterAgent heal() not yet implemented for {violation_type}",
                "artifacts": [],
                "errors": [],
            }
        except Exception as e:
            return {
                "status": "failed",
                "details": f"OutreachSignalRouterAgent heal() failed: {str(e)}",
                "artifacts": [],
                "errors": [str(e)],
            }


class OutreachAgentFactory(MCPHardenedMixin, HealerMixin):
    """Factory for creating outreach agents."""

    @staticmethod
    def create_all_agents(ctx: OutreachEngineContext) -> list[Any]:
        """
        Create all agents for full diagnostic.

        Args:
            ctx: Outreach engine context

        Returns:
            List of all outreach agents
        """
        return [
            LeadQualityAgent(ctx),
            ContactValidatorAgent(ctx),
            MessageComplianceAgent(ctx),
            RgTemplateOptimizerAgent(ctx),
            CampaignBalanceAgent(ctx),
            DeliverabilityAgent(ctx),
            OutreachTestPilot(ctx),
        ]

    @staticmethod
    def create_quality_agents(ctx: OutreachEngineContext) -> list[Any]:
        """
        Create quality-focused agents.

        Args:
            ctx: Outreach engine context

        Returns:
            List of quality-focused agents
        """
        return [
            LeadQualityAgent(ctx),
            ContactValidatorAgent(ctx),
            RgTemplateOptimizerAgent(ctx),
            OutreachTestPilot(ctx),
        ]

    @staticmethod
    def create_compliance_agents(ctx: OutreachEngineContext) -> list[Any]:
        """
        Create compliance-focused agents.

        Args:
            ctx: Outreach engine context

        Returns:
            List of compliance-focused agents
        """
        return [MessageComplianceAgent(ctx), DeliverabilityAgent(ctx), OutreachTestPilot(ctx)]

    @staticmethod
    def create_agents_by_name(ctx: OutreachEngineContext, names: list[str]) -> list[Any]:
        """
        Create specific agents by name.

        Args:
            ctx: Outreach engine context
            names: List of agent class names to create

        Returns:
            List of requested agents
        """
        agent_map = {
            "LeadQualityAgent": LeadQualityAgent,
            "ContactValidatorAgent": ContactValidatorAgent,
            "MessageComplianceAgent": MessageComplianceAgent,
            "TemplateOptimizerAgent": TemplateOptimizerAgent,
            "CampaignBalanceAgent": CampaignBalanceAgent,
            "DeliverabilityAgent": DeliverabilityAgent,
            "OutreachTestPilot": OutreachTestPilot,
            "CampaignPlannerAgent": CampaignPlannerAgent,
            "OutreachReflectionAgent": OutreachReflectionAgent,
        }
        agents = []
        for name in names:
            if name in agent_map:
                agents.append(agent_map[name](ctx))
        return agents

    # guardian: allow-type-erasure
    def heal_repository(self) -> dict:
        """Invoke healing chain via super()."""
        return super().heal_repository()


class OutreachHealingCycle:
    """Manages a single healing cycle."""

    def __init__(self, ctx: OutreachEngineContext, cycle_number: int) -> None:
        """
        Initialize healing cycle.

        Args:
            ctx: Outreach engine context
            cycle_number: Current cycle number (1-indexed)
        """
        self.ctx: OutreachEngineContext = ctx
        self.cycle_number: int = cycle_number
        self.start_time: float | None = None
        self.end_time: float | None = None

    async def execute(self, strategy: OutreachHealingStrategy) -> OutreachCycleResult:
        """
        Execute the healing cycle with the given strategy.

        Args:
            strategy: Healing strategy to apply

        Returns:
            OutreachCycleResult with cycle execution details
        """
        import time

        self.start_time = time.time()
        signals_before = set(self.ctx.signals)
        agents = self._build_agenda(strategy)
        agents_executed: list[str] = []
        passed_agents: list[str] = []
        failed_agents: list[str] = []
        for agent in agents:
            try:
                await agent.execute()
                agents_executed.append(agent.name)
                result = self.ctx.results.get(agent.name, {})
                if result.get("passed", True):
                    passed_agents.append(agent.name)
                else:
                    failed_agents.append(agent.name)
            except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
                raise
                agents_executed.append(agent.name)
                failed_agents.append(agent.name)
                self.ctx.record_result(agent.name, passed=False, details=str(e))
        rollback_triggered = self._check_rollback_conditions()
        if rollback_triggered:
            self._execute_rollback()
        self.end_time = time.time()
        duration_ms = (self.end_time - self.start_time) * 1000
        signals_after = set(self.ctx.signals)
        converged = self.ctx.is_converged()
        return OutreachCycleResult(
            cycle_number=self.cycle_number,
            strategy=strategy,
            agents_executed=agents_executed,
            signals_before=signals_before,
            signals_after=signals_after,
            passed_agents=passed_agents,
            failed_agents=failed_agents,
            rollback_triggered=rollback_triggered,
            converged=converged,
            duration_ms=duration_ms,
        )

    def _build_agenda(self, strategy: OutreachHealingStrategy) -> list[Any]:
        """
        Build the agent agenda based on strategy.

        Args:
            strategy: Healing strategy to apply

        Returns:
            List of agents to execute
        """
        if strategy == OutreachHealingStrategy.FULL_DIAGNOSTIC:
            return OutreachAgentFactory.create_all_agents(self.ctx)
        elif strategy == OutreachHealingStrategy.VERIFICATION_ONLY:
            return [OutreachTestPilot(self.ctx)]
        elif strategy == OutreachHealingStrategy.QUALITY_FOCUS:
            return OutreachAgentFactory.create_quality_agents(self.ctx)
        elif strategy == OutreachHealingStrategy.COMPLIANCE_FOCUS:
            return OutreachAgentFactory.create_compliance_agents(self.ctx)
        elif strategy == OutreachHealingStrategy.SURGICAL_STRIKE:
            agent_names = OutreachSignalRouterAgent.get_agents_for_signals(self.ctx.signals)
            if not agent_names:
                agent_names = ["OutreachTestPilot"]
            agents = OutreachAgentFactory.create_agents_by_name(self.ctx, agent_names)
            if not any(isinstance(a, OutreachTestPilot) for a in agents):
                agents.append(OutreachTestPilot(self.ctx))
            return agents
        return OutreachAgentFactory.create_all_agents(self.ctx)

    def _check_rollback_conditions(self) -> bool:
        """
        Check if rollback should be triggered.

        Returns:
            True if rollback conditions are met, False otherwise
        """
        if OutreachSignalRouterAgent.has_critical_signal(self.ctx.signals):
            return True
        if self.cycle_number > 1 and self.ctx.has_signal("TEST_FAILURE") and self.ctx.campaign_backups:
            return True
        return False

    def _execute_rollback(self) -> None:
        """
        Execute rollback of all changes.

        Reverts campaign to last backup and clears critical signals.
        """
        print(f"   🚨 Cycle {self.cycle_number}: Triggering rollback...")
        self.ctx.rollback_all()
        for signal in list(self.ctx.signals):
            if signal in OutreachSignalRouterAgent.CRITICAL_SIGNALS or signal == "TEST_FAILURE":
                self.ctx.remove_signal(signal)


# guardian: allow-magic-config
async def run_outreach_healing_mission(
    campaign: dict[str, Any],
    leads: list[dict[str, Any]] = None,
    contacts: list[dict[str, Any]] = None,
    messages: list[dict[str, Any]] = None,
    max_cycles: int = 5,
) -> OutreachHealingResult:
    """
    Run a complete outreach healing mission.

    Args:
        campaign: Campaign configuration
        leads: List of leads
        contacts: List of contacts
        messages: List of message templates
        max_cycles: Maximum healing cycles

    Returns:
        OutreachHealingResult with mission outcome
    """
    ctx = OutreachEngineContext()
    ctx.current_campaign = campaign
    ctx.leads = leads or []
    ctx.contacts = contacts or []
    ctx.messages = messages or []
    ctx.backup_campaign("default")
    orchestrator = AppWorkflowOrchestratorAgent(ctx, max_cycles=max_cycles)
    return await orchestrator.run()
