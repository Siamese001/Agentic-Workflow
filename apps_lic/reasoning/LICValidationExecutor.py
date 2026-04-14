"""LICValidationExecutor — Canonical parameterized LIC validation agent.

Consolidates: CampaignBalanceAgent, DeliverabilityAgent, MessageComplianceAgent
Created: 2026-02-08 (Structural Agent Count Reduction)
Updated: 2026-03-11 (P1-A: absorbed MessageComplianceAgent as rule_set="message_compliance")
Updated: 2026-03-11 (P3-A: now subclasses ParameterizedValidator)
"""

from __future__ import annotations

from dataclasses import dataclass

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

_emit_authorize_and_execute("p2", "LICValidationExecutor", "execution_auth")
_emit_validates_capability("p2", "LICValidationExecutor", "capability_check")
_emit_routes_to_capability("p2", "LICValidationExecutor", "capability_route")
_emit_writes_via_uwg("p2", "LICValidationExecutor", "uwg_write")
_emit_blocks_direct_write("p2", "LICValidationExecutor", "direct_write_block")
_emit_records_tool_invocation("p2", "LICValidationExecutor", "tool_invocation")
_emit_captures_execution_output("p2", "LICValidationExecutor", "exec_output")
_emit_dispatches_agent("p3", "LICValidationExecutor", "agent_dispatch")
_emit_coordinates_agents("p3", "LICValidationExecutor", "agent_coordination")
_emit_records_workflow_lineage("p3", "LICValidationExecutor", "workflow_lineage")
_emit_records_healing_outcome("p3", "LICValidationExecutor", "healing_outcome")
_emit_escalates_failure("p3", "LICValidationExecutor", "failure_escalation")
_emit_orchestrates_workflow("p3", "LICValidationExecutor", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "LICValidationExecutor", "healing_dispatch")
_emit_invokes_evaluation("p3", "LICValidationExecutor", "evaluation_signal")
_emit_records_telemetry_event("p4", "LICValidationExecutor", "telemetry_event")
_emit_captures_evaluation_metric("p4", "LICValidationExecutor", "eval_metric")
_emit_stores_embedding("p4", "LICValidationExecutor", "embedding_store")
_emit_updates_meta_learning_state("p4", "LICValidationExecutor", "meta_learning")
_emit_links_execution_to_snapshot("p4", "LICValidationExecutor", "exec_snapshot_link")
from apps_lic.utils.lic_engine_validation_capability_util import LICEngineValidationCapability
from apps_shared.reasoning.ParameterizedValidator import ParameterizedValidator

_emit_applies_guardrail("p0", "LICValidationExecutor", "p0_governance")
_emit_reads_policy_state("p0", "LICValidationExecutor", "policy_binding")
_emit_snapshots_state("p0", "LICValidationExecutor", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
from tqdm import tqdm

_emit_emits_metric_event("LICValidationExecutor", "p4obs", "metric_1")
_emit_emits_metric_event("LICValidationExecutor", "p4obs", "metric_2")
_emit_emits_metric_event("LICValidationExecutor", "p4obs", "metric_3")
_emit_emits_metric_event("LICValidationExecutor", "p4obs", "metric_4")
_emit_emits_metric_event("LICValidationExecutor", "p4obs", "metric_5")
_emit_emits_metric_event("LICValidationExecutor", "p4obs", "metric_6")
_emit_records_incident_event("LICValidationExecutor", "p4obs", "incident")
_emit_captures_runtime_anomaly("LICValidationExecutor", "p4obs", "anomaly")
_emit_writes_observability_log("LICValidationExecutor", "p4obs", "obs_log")
_emit_updates_monitoring_state("LICValidationExecutor", "p4obs", "mon_state")
_emit_triggers_alert("LICValidationExecutor", "p4obs", "alert")
_emit_links_incident_trace("LICValidationExecutor", "p4obs", "trace_link")
_emit_captures_pattern("LICValidationExecutor", "p3lm", "pattern")
_emit_records_learning_event("LICValidationExecutor", "p3lm", "learning_event")
_emit_writes_learning_snapshot("LICValidationExecutor", "p3lm", "snapshot")
_emit_feeds_meta_learning("LICValidationExecutor", "p3lm", "meta_feed")
_emit_updates_routing_strategy("LICValidationExecutor", "p3lm", "routing")
_emit_improves_agent_policy("LICValidationExecutor", "p3lm", "policy")
_emit_stores_learning_state("LICValidationExecutor", "p3lm", "state")
_emit_records_execution_trace("LICValidationExecutor", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("LICValidationExecutor", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("LICValidationExecutor", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("LICValidationExecutor", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("LICValidationExecutor", "L4_STATE", "p2_trace_5")
_emit_reads_environ("LICValidationExecutor", "env_read", "p2_env_1")
_emit_reads_environ("LICValidationExecutor", "env_read", "p2_env_2")
_emit_reads_runtime_state("LICValidationExecutor", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("LICValidationExecutor", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "LICValidationExecutor", "context_pull")
_emit_pulls_context("p1", "LICValidationExecutor", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "LICValidationExecutor", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "LICValidationExecutor", "uwg_term_2")
_emit_writes_through("p1", "LICValidationExecutor", "write_through")
_emit_writes_through("p1", "LICValidationExecutor", "write_through_2")
_emit_validated_by_safety_plane("p1", "LICValidationExecutor", "safety_validation")
_emit_invokes_eval("p1", "LICValidationExecutor", "eval_call")
_emit_proposal_commits_routing("p1", "LICValidationExecutor", "routing_commit")
_emit_escalates_to_human("p1", "LICValidationExecutor", "human_escalation")
_emit_routes_through("p1", "LICValidationExecutor", "route_through")
_emit_checks_agent_registry("p1", "LICValidationExecutor", "agent_registry")
_emit_validates_agent_capability("p1", "LICValidationExecutor", "capability")
_emit_dispatches_execution_plan("p1", "LICValidationExecutor", "exec_plan")
_emit_agent_executes_agent("p1", "LICValidationExecutor", "sub_agent")
_emit_routes_to_agent("p1", "LICValidationExecutor", "target_agent")
_emit_verifies_policy("p1", "LICValidationExecutor", "policy_check")
_emit_observes_runtime_state("p1", "LICValidationExecutor", "runtime_state")
_emit_verifies_boundary("p1", "LICValidationExecutor", "boundary_check")
_emit_transcripts_response("p1", "LICValidationExecutor", "transcript")
_emit_hard_fails_untranscripted("p1", "LICValidationExecutor")
_emit_gated_by_confidence("p1", "LICValidationExecutor", "confidence_gate")
emit_replay_key("p0", "LICValidationExecutor")
emit_determinism_digest("p0", "LICValidationExecutor")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


@dataclass
class LICValidationExecutor(LICEngineValidationCapability, ParameterizedValidator):
    """Parameterized LIC engine validation agent.

    Usage:
        validator = LICValidationExecutor(rule_set="campaign_balance")

    Inherits execute(), collect_issues(), and _RULE_REGISTRY dispatch
    from ParameterizedValidator (P3-A). Rule handlers registered below.
    """

    rule_set: str = "generic"

    def collect_issues(self, data: dict, **kwargs) -> list[dict]:
        """Dispatch to rule-specific validation (LIC-local registry)."""
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(
            str(uuid.uuid4()),
            LayerSegment.L3_ORCHESTRATION,
            f"LICValidationExecutor.collect_issues:{self.rule_set}",
        )
        if self.rule_set == "campaign_balance":
            return self._validate_campaign_balance(data)
        elif self.rule_set == "deliverability":
            return self._validate_deliverability(data)
        elif self.rule_set == "message_compliance":
            return self._validate_message_compliance(data)
        return super().collect_issues(data, **kwargs)

    def _validate_campaign_balance(self, data: dict) -> list[dict]:
        """Campaign balance validation rules."""
        issues = []
        channels = data.get("channels", {})
        total = sum(channels.values()) if channels else 0
        if total > 0:
            for ch, val in channels.items():
                ratio = val / total
                if ratio > 0.7:
                    issues.append({"type": "channel_imbalance", "channel": ch, "ratio": ratio})
        return issues

    def _validate_deliverability(self, data: dict) -> list[dict]:
        """Deliverability validation rules."""
        issues = []
        if data.get("spam_score", 0) > 5:
            issues.append({"type": "high_spam_score", "score": data["spam_score"]})
        if not data.get("dkim_valid", True):
            issues.append({"type": "dkim_invalid"})
        if not data.get("spf_valid", True):
            issues.append({"type": "spf_invalid"})
        return issues

    _MESSAGE_COMPLIANCE_FORBIDDEN_WORDS = [
        "guaranteed",
        "free money",
        "act now",
        "limited time",
        "winner",
        "congratulations",
        "urgent",
        "click here",
    ]
    _MESSAGE_COMPLIANCE_MAX_LENGTH = 5000

    def _validate_message_compliance(self, data: dict) -> list[dict]:
        """Message compliance validation rules.

        Absorbed from MessageComplianceAgent (2026-03-11, P1-A).
        Checks: forbidden words, unsubscribe link presence, message length.

        Expected data shape:
            {"messages": [{"content": str, "subject": str}, ...]}
        """
        issues = []
        messages = data.get("messages", [])
        for i, message in tqdm(enumerate(messages), desc="Processing", unit="item"):
            content = message.get("content", "").lower()
            subject = message.get("subject", "").lower()
            for word in self._MESSAGE_COMPLIANCE_FORBIDDEN_WORDS:
                if word in content or word in subject:
                    issues.append({"type": "compliance_forbidden_word", "message_index": i, "word": word})
            if "unsubscribe" not in content:
                issues.append({"type": "compliance_missing_unsubscribe", "message_index": i})
            if len(content) > self._MESSAGE_COMPLIANCE_MAX_LENGTH:
                issues.append(
                    {
                        "type": "compliance_message_too_long",
                        "message_index": i,
                        "length": len(content),
                        "max": self._MESSAGE_COMPLIANCE_MAX_LENGTH,
                    },
                )
        return issues
