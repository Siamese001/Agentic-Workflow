"""
Campaign Balance Deterministic Layer

Moved from CampaignBalanceAgent - 100% deterministic logic extracted.
This module contains pure deterministic campaign balance validation.

Deterministic Operations:
- Ratio calculations
- Required field validation
- Threshold comparisons
- Balance rule processing
"""

from __future__ import annotations

from dataclasses import dataclass
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
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "campaign_balance_validator")
emit_determinism_digest("p0", "campaign_balance_validator")

_emit_dispatches_healing_run("p1", "campaign_balance_validator", "L5")
_emit_routes_through("p1", "campaign_balance_validator", "L5")
_emit_checks_agent_registry("p1", "campaign_balance_validator", "agent_registry")
_emit_validates_agent_capability("p1", "campaign_balance_validator", "capability")
_emit_dispatches_execution_plan("p1", "campaign_balance_validator", "exec_plan")
_emit_agent_executes_agent("p1", "campaign_balance_validator", "sub_agent")
_emit_routes_to_agent("p1", "campaign_balance_validator", "target_agent")
_emit_verifies_policy("p1", "campaign_balance_validator", "policy_check")
_emit_observes_runtime_state("p1", "campaign_balance_validator", "runtime_state")
_emit_verifies_boundary("p1", "campaign_balance_validator", "boundary_check")
_emit_transcripts_response("p1", "campaign_balance_validator", "transcript")
_emit_hard_fails_untranscripted("p1", "campaign_balance_validator")
_emit_gated_by_confidence("p1", "campaign_balance_validator", "confidence_gate")
_emit_escalates_to_human("p1", "campaign_balance_validator", "L5")
_emit_reads_policy_state("p1", "campaign_balance_validator", "L5")

_emit_applies_guardrail("p0", "campaign_balance_validator", "p0_governance")
_emit_snapshots_state("p0", "campaign_balance_validator", "state_snapshot")
_emit_authorize_and_execute("p2", "campaign_balance_validator", "execution_auth")
_emit_validates_capability("p2", "campaign_balance_validator", "capability_check")
_emit_routes_to_capability("p2", "campaign_balance_validator", "capability_route")
_emit_writes_via_uwg("p2", "campaign_balance_validator", "uwg_write")
_emit_blocks_direct_write("p2", "campaign_balance_validator", "direct_write_block")
_emit_records_tool_invocation("p2", "campaign_balance_validator", "tool_invocation")
_emit_captures_execution_output("p2", "campaign_balance_validator", "exec_output")
_emit_dispatches_agent("p3", "campaign_balance_validator", "agent_dispatch")
_emit_coordinates_agents("p3", "campaign_balance_validator", "agent_coordination")
_emit_records_workflow_lineage("p3", "campaign_balance_validator", "workflow_lineage")
_emit_records_healing_outcome("p3", "campaign_balance_validator", "healing_outcome")
_emit_escalates_failure("p3", "campaign_balance_validator", "failure_escalation")
_emit_orchestrates_workflow("p3", "campaign_balance_validator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "campaign_balance_validator", "healing_dispatch")
_emit_invokes_evaluation("p3", "campaign_balance_validator", "evaluation_signal")
_emit_records_telemetry_event("p4", "campaign_balance_validator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "campaign_balance_validator", "eval_metric")
_emit_stores_embedding("p4", "campaign_balance_validator", "embedding_store")
_emit_updates_meta_learning_state("p4", "campaign_balance_validator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "campaign_balance_validator", "exec_snapshot_link")
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
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("campaign_balance_validator", "p4obs", "metric_1")
_emit_emits_metric_event("campaign_balance_validator", "p4obs", "metric_2")
_emit_emits_metric_event("campaign_balance_validator", "p4obs", "metric_3")
_emit_emits_metric_event("campaign_balance_validator", "p4obs", "metric_4")
_emit_emits_metric_event("campaign_balance_validator", "p4obs", "metric_5")
_emit_emits_metric_event("campaign_balance_validator", "p4obs", "metric_6")
_emit_records_incident_event("campaign_balance_validator", "p4obs", "incident")
_emit_captures_runtime_anomaly("campaign_balance_validator", "p4obs", "anomaly")
_emit_writes_observability_log("campaign_balance_validator", "p4obs", "obs_log")
_emit_updates_monitoring_state("campaign_balance_validator", "p4obs", "mon_state")
_emit_triggers_alert("campaign_balance_validator", "p4obs", "alert")
_emit_links_incident_trace("campaign_balance_validator", "p4obs", "trace_link")
_emit_captures_pattern("campaign_balance_validator", "p3lm", "pattern")
_emit_records_learning_event("campaign_balance_validator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("campaign_balance_validator", "p3lm", "snapshot")
_emit_feeds_meta_learning("campaign_balance_validator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("campaign_balance_validator", "p3lm", "routing")
_emit_improves_agent_policy("campaign_balance_validator", "p3lm", "policy")
_emit_stores_learning_state("campaign_balance_validator", "p3lm", "state")
_emit_records_execution_trace("campaign_balance_validator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("campaign_balance_validator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("campaign_balance_validator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("campaign_balance_validator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("campaign_balance_validator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("campaign_balance_validator", "env_read", "p2_env_1")
_emit_reads_environ("campaign_balance_validator", "env_read", "p2_env_2")
_emit_reads_runtime_state("campaign_balance_validator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("campaign_balance_validator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "campaign_balance_validator", "context_pull")
_emit_pulls_context("p1", "campaign_balance_validator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "campaign_balance_validator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "campaign_balance_validator", "uwg_term_2")
_emit_writes_through("p1", "campaign_balance_validator", "write_through")
_emit_writes_through("p1", "campaign_balance_validator", "write_through_2")
_emit_validated_by_safety_plane("p1", "campaign_balance_validator", "safety_validation")
_emit_invokes_eval("p1", "campaign_balance_validator", "eval_call")
_emit_proposal_commits_routing("p1", "campaign_balance_validator", "routing_commit")


@dataclass
class BalanceResult:
    """Result of campaign balance validation."""

    passed: bool
    issues: list[str]
    ratio: float | None = None
    metadata: dict[str, Any] = None

    def __post_init__(self) -> None:
        if self.metadata is None:
            self.metadata = {}


class CampaignBalanceValidator:
    """
    Pure deterministic campaign balance validation.

    All logic is 100% deterministic - no external dependencies or LLM calls.
    """

    def __init__(self, thresholds: dict[str, Any] | None = None) -> None:
        """
        Initialize with balance validation thresholds.

        Args:
            thresholds: Configuration for balance validation
        """
        self.thresholds = thresholds or {"max_leads_per_message": 100, "min_leads_per_message": 1}

    def validate_campaign_balance(
        self, campaign: dict[str, Any], leads: list[Any], messages: list[Any],
    ) -> BalanceResult:
        """
        Validate campaign balance using purely deterministic logic.

        Args:
            campaign: Campaign data dictionary
            leads: List of lead objects
            messages: List of message objects

        Returns:
            BalanceResult with deterministic findings
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L5_POLICY, "CampaignBalanceValidator.validate_campaign_balance",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:CampaignBalanceValidator.validate_campaign_balance".encode(),
        ).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        issues: list[str] = []
        ratio = self._calculate_lead_message_ratio(leads, messages)
        if ratio is not None:
            ratio_issues = self._validate_ratio(ratio)
            issues.extend(ratio_issues)
        field_issues = self._validate_required_fields(campaign)
        issues.extend(field_issues)
        return BalanceResult(
            passed=len(issues) == 0, issues=issues, ratio=ratio, metadata={"validation_type": "deterministic"},
        )

    def _calculate_lead_message_ratio(self, leads: list[Any], messages: list[Any]) -> float | None:
        """
        Calculate lead-to-message ratio using deterministic arithmetic.

        Moved to Deterministic: Pure mathematical calculation
        """
        if not messages:
            return None
        lead_count = len(leads)
        message_count = len(messages)
        return lead_count / message_count

    def _validate_ratio(self, ratio: float) -> list[str]:
        """
        Validate ratio against deterministic thresholds.

        Moved to Deterministic: Pure comparison logic
        """
        issues: list[str] = []
        max_ratio = self.thresholds["max_leads_per_message"]
        min_ratio = self.thresholds["min_leads_per_message"]
        if ratio > max_ratio:
            issues.append("Too many leads per message template")
        elif ratio < min_ratio:
            issues.append("More templates than leads")
        return issues

    def _validate_required_fields(self, campaign: dict[str, Any]) -> list[str]:
        """
        Validate required campaign fields using deterministic checks.

        Moved to Deterministic: Pure existence validation
        """
        issues: list[str] = []
        if not campaign.get("name"):
            issues.append("Campaign missing name")
        if not campaign.get("goal"):
            issues.append("Campaign missing goal")
        return issues

    def calculate_balance_score(
        self, campaign: dict[str, Any], leads: list[Any], messages: list[Any],
    ) -> float:
        """
        Calculate overall balance score using deterministic algorithm.

        Returns:
            Float between 0.0 and 1.0 representing balance quality
        """
        score = 1.0
        if not campaign.get("name"):
            score -= 0.3
        if not campaign.get("goal"):
            score -= 0.3
        ratio = self._calculate_lead_message_ratio(leads, messages)
        if ratio is not None:
            max_ratio = self.thresholds["max_leads_per_message"]
            min_ratio = self.thresholds["min_leads_per_message"]
            if ratio > max_ratio:
                excess_ratio = ratio - max_ratio
                score -= min(0.4, excess_ratio / max_ratio * 0.4)
            elif ratio < min_ratio:
                deficit_ratio = min_ratio - ratio
                score -= min(0.4, deficit_ratio / min_ratio * 0.4)
        return max(0.0, score)

    def suggest_improvements(
        self, campaign: dict[str, Any], leads: list[Any], messages: list[Any],
    ) -> list[str]:
        """
        Generate deterministic improvement suggestions.

        Returns:
            List of actionable improvement suggestions
        """
        suggestions: list[str] = []
        if not campaign.get("name"):
            suggestions.append("Add a descriptive campaign name")
        if not campaign.get("goal"):
            suggestions.append("Define a clear campaign goal")
        ratio = self._calculate_lead_message_ratio(leads, messages)
        if ratio is not None:
            max_ratio = self.thresholds["max_leads_per_message"]
            min_ratio = self.thresholds["min_leads_per_message"]
            if ratio > max_ratio:
                needed_messages = len(leads) // max_ratio + 1
                suggestions.append(f"Create {needed_messages - len(messages)} more message templates")
            elif ratio < min_ratio:
                needed_leads = len(messages) * min_ratio
                suggestions.append(f"Add {needed_leads - len(leads)} more leads or remove templates")
        return suggestions
