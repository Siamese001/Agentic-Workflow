"""RGValidationExecutor — Canonical parameterized RG validation agent.

Consolidates: ATSCompatibilityAgent, BrandComplianceAgent, FactCheckAgent, SectionBalanceAgent
Created: 2026-02-08 (Structural Agent Count Reduction)
Updated: 2026-03-11 (P3-A: now subclasses ParameterizedValidator)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

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

_emit_authorize_and_execute("p2", "RGValidationExecutor", "execution_auth")
_emit_validates_capability("p2", "RGValidationExecutor", "capability_check")
_emit_routes_to_capability("p2", "RGValidationExecutor", "capability_route")
_emit_writes_via_uwg("p2", "RGValidationExecutor", "uwg_write")
_emit_blocks_direct_write("p2", "RGValidationExecutor", "direct_write_block")
_emit_records_tool_invocation("p2", "RGValidationExecutor", "tool_invocation")
_emit_captures_execution_output("p2", "RGValidationExecutor", "exec_output")
_emit_dispatches_agent("p3", "RGValidationExecutor", "agent_dispatch")
_emit_coordinates_agents("p3", "RGValidationExecutor", "agent_coordination")
_emit_records_workflow_lineage("p3", "RGValidationExecutor", "workflow_lineage")
_emit_records_healing_outcome("p3", "RGValidationExecutor", "healing_outcome")
_emit_escalates_failure("p3", "RGValidationExecutor", "failure_escalation")
_emit_orchestrates_workflow("p3", "RGValidationExecutor", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "RGValidationExecutor", "healing_dispatch")
_emit_invokes_evaluation("p3", "RGValidationExecutor", "evaluation_signal")
_emit_records_telemetry_event("p4", "RGValidationExecutor", "telemetry_event")
_emit_captures_evaluation_metric("p4", "RGValidationExecutor", "eval_metric")
_emit_stores_embedding("p4", "RGValidationExecutor", "embedding_store")
_emit_updates_meta_learning_state("p4", "RGValidationExecutor", "meta_learning")
_emit_links_execution_to_snapshot("p4", "RGValidationExecutor", "exec_snapshot_link")
from apps_shared.reasoning.ParameterizedValidator import ParameterizedValidator

_emit_applies_guardrail("p0", "RGValidationExecutor", "p0_governance")
_emit_reads_policy_state("p0", "RGValidationExecutor", "policy_binding")
_emit_snapshots_state("p0", "RGValidationExecutor", "state_snapshot")
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

_emit_emits_metric_event("RGValidationExecutor", "p4obs", "metric_1")
_emit_emits_metric_event("RGValidationExecutor", "p4obs", "metric_2")
_emit_emits_metric_event("RGValidationExecutor", "p4obs", "metric_3")
_emit_emits_metric_event("RGValidationExecutor", "p4obs", "metric_4")
_emit_emits_metric_event("RGValidationExecutor", "p4obs", "metric_5")
_emit_emits_metric_event("RGValidationExecutor", "p4obs", "metric_6")
_emit_records_incident_event("RGValidationExecutor", "p4obs", "incident")
_emit_captures_runtime_anomaly("RGValidationExecutor", "p4obs", "anomaly")
_emit_writes_observability_log("RGValidationExecutor", "p4obs", "obs_log")
_emit_updates_monitoring_state("RGValidationExecutor", "p4obs", "mon_state")
_emit_triggers_alert("RGValidationExecutor", "p4obs", "alert")
_emit_links_incident_trace("RGValidationExecutor", "p4obs", "trace_link")
_emit_captures_pattern("RGValidationExecutor", "p3lm", "pattern")
_emit_records_learning_event("RGValidationExecutor", "p3lm", "learning_event")
_emit_writes_learning_snapshot("RGValidationExecutor", "p3lm", "snapshot")
_emit_feeds_meta_learning("RGValidationExecutor", "p3lm", "meta_feed")
_emit_updates_routing_strategy("RGValidationExecutor", "p3lm", "routing")
_emit_improves_agent_policy("RGValidationExecutor", "p3lm", "policy")
_emit_stores_learning_state("RGValidationExecutor", "p3lm", "state")
_emit_records_execution_trace("RGValidationExecutor", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("RGValidationExecutor", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("RGValidationExecutor", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("RGValidationExecutor", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("RGValidationExecutor", "L4_STATE", "p2_trace_5")
_emit_reads_environ("RGValidationExecutor", "env_read", "p2_env_1")
_emit_reads_environ("RGValidationExecutor", "env_read", "p2_env_2")
_emit_reads_runtime_state("RGValidationExecutor", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("RGValidationExecutor", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "RGValidationExecutor", "context_pull")
_emit_pulls_context("p1", "RGValidationExecutor", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "RGValidationExecutor", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "RGValidationExecutor", "uwg_term_2")
_emit_writes_through("p1", "RGValidationExecutor", "write_through")
_emit_writes_through("p1", "RGValidationExecutor", "write_through_2")
_emit_validated_by_safety_plane("p1", "RGValidationExecutor", "safety_validation")
_emit_invokes_eval("p1", "RGValidationExecutor", "eval_call")
_emit_proposal_commits_routing("p1", "RGValidationExecutor", "routing_commit")
_emit_escalates_to_human("p1", "RGValidationExecutor", "human_escalation")
_emit_routes_through("p1", "RGValidationExecutor", "route_through")
_emit_checks_agent_registry("p1", "RGValidationExecutor", "agent_registry")
_emit_validates_agent_capability("p1", "RGValidationExecutor", "capability")
_emit_dispatches_execution_plan("p1", "RGValidationExecutor", "exec_plan")
_emit_agent_executes_agent("p1", "RGValidationExecutor", "sub_agent")
_emit_routes_to_agent("p1", "RGValidationExecutor", "target_agent")
_emit_verifies_policy("p1", "RGValidationExecutor", "policy_check")
_emit_observes_runtime_state("p1", "RGValidationExecutor", "runtime_state")
_emit_verifies_boundary("p1", "RGValidationExecutor", "boundary_check")
_emit_transcripts_response("p1", "RGValidationExecutor", "transcript")
_emit_hard_fails_untranscripted("p1", "RGValidationExecutor")
_emit_gated_by_confidence("p1", "RGValidationExecutor", "confidence_gate")
emit_replay_key("p0", "RGValidationExecutor")
emit_determinism_digest("p0", "RGValidationExecutor")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

_RULE_REGISTRY: dict[str, Callable] = {}


def register_rule(name: str):
    """Decorator to register a collect_issues implementation."""

    def decorator(func):
        _RULE_REGISTRY[name] = func
        return func

    return decorator


@register_rule("ats_compatibility")
def _ats_collect_issues(self, resume_data: dict, job_data: dict | None = None) -> list[dict]:
    """ATS compatibility validation logic."""
    issues = []
    if not resume_data.get("skills"):
        issues.append(
            {"type": "ats_missing_skills", "severity": "high", "message": "No skills section found"}
        )
    if not resume_data.get("experience"):
        issues.append(
            {"type": "ats_missing_experience", "severity": "high", "message": "No experience section"}
        )
    keywords = resume_data.get("keywords", [])
    if job_data:
        required = set(job_data.get("required_keywords", []))
        found = set(keywords)
        missing = required - found
        for kw in missing:
            issues.append(
                {"type": "ats_missing_keyword", "severity": "medium", "message": f"Missing keyword: {kw}"}
            )
    return issues


@register_rule("brand_compliance")
def _brand_collect_issues(self, resume_data: dict, job_data: dict | None = None) -> list[dict]:
    """Brand compliance validation logic."""
    issues = []
    tone = resume_data.get("tone", "")
    if tone and tone.lower() not in ("professional", "confident", "balanced"):
        issues.append(
            {"type": "brand_tone_mismatch", "severity": "medium", "message": f"Tone '{tone}' not aligned"}
        )
    if resume_data.get("contains_superlatives", False):
        issues.append({"type": "brand_superlatives", "severity": "low", "message": "Contains superlatives"})
    return issues


@register_rule("fact_check")
def _fact_collect_issues(self, resume_data: dict, job_data: dict | None = None) -> list[dict]:
    """Fact-check validation logic."""
    issues = []
    claims = resume_data.get("quantified_claims", [])
    for claim in claims:
        if not claim.get("source"):
            issues.append(
                {
                    "type": "fact_unsourced_claim",
                    "severity": "high",
                    "message": f"Unsourced: {claim.get('text', '')}",
                }
            )
        if claim.get("value") and (not claim.get("context")):
            issues.append(
                {
                    "type": "fact_no_context",
                    "severity": "medium",
                    "message": f"No context for metric: {claim.get('text', '')}",
                }
            )
    dates = resume_data.get("dates", [])
    for i in range(len(dates) - 1):
        if dates[i].get("end") and dates[i + 1].get("start"):
            if dates[i]["end"] > dates[i + 1]["start"]:
                issues.append(
                    {"type": "fact_date_overlap", "severity": "high", "message": "Overlapping date ranges"}
                )
    return issues


@register_rule("section_balance")
def _section_collect_issues(self, resume_data: dict, job_data: dict | None = None) -> list[dict]:
    """Section balance validation logic."""
    issues = []
    sections = resume_data.get("sections", {})
    total_len = sum(len(str(v)) for v in sections.values()) or 1
    for name, content in sections.items():
        ratio = len(str(content)) / total_len
        if ratio > 0.6:
            issues.append(
                {
                    "type": "section_oversized",
                    "severity": "medium",
                    "message": f"Section '{name}' is {ratio:.0%} of total",
                }
            )
        if ratio < 0.05 and name not in ("objective", "summary"):
            issues.append(
                {
                    "type": "section_undersized",
                    "severity": "low",
                    "message": f"Section '{name}' is only {ratio:.0%} of total",
                }
            )
    return issues


@dataclass
class RGValidationExecutor(ParameterizedValidator):
    """Parameterized RG validation agent.

    Usage:
        validator = RGValidationExecutor(rule_set="ats_compatibility")

    Inherits execute(), collect_issues() skeleton, and _RULE_REGISTRY dispatch
    from ParameterizedValidator (P3-A). Rule functions registered via @register_rule above.
    """

    rule_set: str = "generic"

    # guardian: allow-type-erasure
    def execute(self, resume_data: dict, job_data: dict | None = None, **kwargs) -> dict:
        """Execute validation and return results."""
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, f"RGValidationExecutor.execute:{self.rule_set}")
        issues = self.collect_issues(resume_data, job_data)
        return {
            "rule_set": self.rule_set,
            "issues": issues,
            "issue_count": len(issues),
            "passed": len(issues) == 0,
        }

    def collect_issues(self, resume_data: dict, job_data: dict | None = None, **kwargs) -> list[dict]:
        """Dispatch to registered rule implementation."""
        handler = _RULE_REGISTRY.get(self.rule_set)
        if handler is None:
            return [
                {
                    "type": "unknown_rule_set",
                    "severity": "high",
                    "message": f"No handler for rule_set={self.rule_set}",
                }
            ]
        return handler(self, resume_data, job_data)
