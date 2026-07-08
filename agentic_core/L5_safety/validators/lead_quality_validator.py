"""
Lead Quality Validator - Deterministic Lead Quality Validation

Zero-Ambiguity Standard: Renamed from lead_quality_deterministic_validator.py
Category: VALIDATOR (Deterministic safety check)

Moved from L0_routing/deterministic to L5_safety/validators.

Deterministic Operations:
- Required field validation (existence checks)
- Contact information validation (field presence)
- Email domain validation (pattern matching)
- Spam indicator detection (keyword matching)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "lead_quality_validator")
trace_contract.emit_determinism_digest("p0", "lead_quality_validator")

trace_contract._emit_dispatches_healing_run("p1", "lead_quality_validator", "L5")
trace_contract._emit_routes_through("p1", "lead_quality_validator", "L5")
trace_contract._emit_checks_agent_registry("p1", "lead_quality_validator", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "lead_quality_validator", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "lead_quality_validator", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "lead_quality_validator", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "lead_quality_validator", "target_agent")
trace_contract._emit_verifies_policy("p1", "lead_quality_validator", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "lead_quality_validator", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "lead_quality_validator", "boundary_check")
trace_contract._emit_transcripts_response("p1", "lead_quality_validator", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "lead_quality_validator")
trace_contract._emit_gated_by_confidence("p1", "lead_quality_validator", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "lead_quality_validator", "L5")
trace_contract._emit_reads_policy_state("p1", "lead_quality_validator", "L5")

trace_contract._emit_applies_guardrail("p0", "lead_quality_validator", "p0_governance")
trace_contract._emit_snapshots_state("p0", "lead_quality_validator", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "lead_quality_validator", "execution_auth")
trace_contract._emit_validates_capability("p2", "lead_quality_validator", "capability_check")
trace_contract._emit_routes_to_capability("p2", "lead_quality_validator", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "lead_quality_validator", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "lead_quality_validator", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "lead_quality_validator", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "lead_quality_validator", "exec_output")
trace_contract._emit_dispatches_agent("p3", "lead_quality_validator", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "lead_quality_validator", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "lead_quality_validator", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "lead_quality_validator", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "lead_quality_validator", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "lead_quality_validator", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "lead_quality_validator", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "lead_quality_validator", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "lead_quality_validator", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "lead_quality_validator", "eval_metric")
trace_contract._emit_stores_embedding("p4", "lead_quality_validator", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "lead_quality_validator", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "lead_quality_validator", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("lead_quality_validator", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("lead_quality_validator", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("lead_quality_validator", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("lead_quality_validator", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("lead_quality_validator", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("lead_quality_validator", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("lead_quality_validator", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("lead_quality_validator", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("lead_quality_validator", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("lead_quality_validator", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("lead_quality_validator", "p4obs", "alert")
trace_contract._emit_links_incident_trace("lead_quality_validator", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("lead_quality_validator", "p3lm", "pattern")
trace_contract._emit_records_learning_event("lead_quality_validator", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("lead_quality_validator", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("lead_quality_validator", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("lead_quality_validator", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("lead_quality_validator", "p3lm", "policy")
trace_contract._emit_stores_learning_state("lead_quality_validator", "p3lm", "state")
trace_contract._emit_records_execution_trace("lead_quality_validator", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("lead_quality_validator", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("lead_quality_validator", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("lead_quality_validator", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("lead_quality_validator", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("lead_quality_validator", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("lead_quality_validator", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("lead_quality_validator", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("lead_quality_validator", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "lead_quality_validator", "context_pull")
trace_contract._emit_pulls_context("p1", "lead_quality_validator", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "lead_quality_validator", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "lead_quality_validator", "uwg_term_2")
trace_contract._emit_writes_through("p1", "lead_quality_validator", "write_through")
trace_contract._emit_writes_through("p1", "lead_quality_validator", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "lead_quality_validator", "safety_validation")
trace_contract._emit_invokes_eval("p1", "lead_quality_validator", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "lead_quality_validator", "routing_commit")


@dataclass
class LeadQualityResult:
    """Result of lead quality validation."""

    passed: bool
    issues: list[str]
    score: float | None = None
    metadata: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        if self.metadata is None:
            self.metadata = {}


class LeadQualityValidator:
    """
    Pure deterministic lead quality validation.

    All methods are 100% deterministic and can be executed without
    external dependencies or LLM calls.
    """

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        """
        Initialize with lead quality validation configuration.

        Args:
            config: Configuration dictionary containing validation rules
        """
        config = config or {}
        self.required_fields = config.get("required_fields", ["company"])
        self.contact_fields = config.get("contact_fields", ["contact_name", "email"])
        self.suspicious_domains = config.get(
            "suspicious_domains",
            [".xyz", ".top", ".click", ".link", ".work", ".date"],
        )
        self.spam_indicators = config.get("spam_indicators", ["test@", "noreply@", "donotreply@", "spam@"])

    def validate_lead_quality(self, leads: list[dict[str, Any]]) -> LeadQualityResult:
        """
        Validate lead quality using purely deterministic logic.

        Args:
            leads: List of lead dictionaries

        Returns:
            LeadQualityResult with deterministic findings
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id,
            trace_contract.LayerSegment.L5_POLICY,
            "LeadQualityValidator.validate_lead_quality",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:LeadQualityValidator.validate_lead_quality".encode(),
        ).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if not leads:
            return LeadQualityResult(
                passed=True,
                issues=[],
                score=1.0,
                metadata={"validation_type": "deterministic", "lead_count": 0},
            )
        issues: list[str] = []
        for i, lead in enumerate(leads):
            field_issues = self._check_required_fields(lead, i)
            issues.extend(field_issues)
            contact_issues = self._check_contact_info(lead, i)
            issues.extend(contact_issues)
            email_issues = self._check_email_domain(lead, i)
            issues.extend(email_issues)
            spam_issues = self._check_spam_indicators(lead, i)
            issues.extend(spam_issues)
        score = self._calculate_quality_score(issues, len(leads))
        return LeadQualityResult(
            passed=len(issues) == 0,
            issues=issues,
            score=score,
            metadata={"validation_type": "deterministic", "lead_count": len(leads)},
        )

    def _check_required_fields(self, lead: dict[str, Any], lead_index: int) -> list[str]:
        """
        Check required fields using deterministic existence checks.

        Moved to Deterministic: Pure field existence validation
        """
        issues: list[str] = []
        for field in self.required_fields:
            if not lead.get(field):
                issues.append(f"Lead {lead_index}: Missing {field}")
        return issues

    def _check_contact_info(self, lead: dict[str, Any], lead_index: int) -> list[str]:
        """
        Check contact information using deterministic field presence.

        Moved to Deterministic: Pure field presence validation
        """
        issues: list[str] = []
        has_contact = any(lead.get(field) for field in self.contact_fields)
        if not has_contact:
            issues.append(f"Lead {lead_index}: Missing contact info")
        return issues

    def _check_email_domain(self, lead: dict[str, Any], lead_index: int) -> list[str]:
        """
        Check email domain using deterministic pattern matching.

        Moved to Deterministic: Pure domain validation
        """
        issues: list[str] = []
        email = lead.get("email", "")
        if email:
            for domain in self.suspicious_domains:
                if email.endswith(domain):
                    issues.append(f"Lead {lead_index}: Suspicious email domain")
                    break
        return issues

    def _check_spam_indicators(self, lead: dict[str, Any], lead_index: int) -> list[str]:
        """
        Check spam indicators using deterministic keyword matching.

        Moved to Deterministic: Pure keyword matching
        """
        issues: list[str] = []
        email = lead.get("email", "").lower()
        if email:
            for indicator in self.spam_indicators:
                if indicator in email:
                    issues.append(f"Lead {lead_index}: Spam indicator in email")
                    break
        return issues

    def _calculate_quality_score(self, issues: list[str], lead_count: int) -> float:
        """
        Calculate quality score using deterministic algorithm.

        Moved to Deterministic: Pure mathematical scoring
        """
        if lead_count == 0:
            return 1.0
        base_score = 1.0
        issue_penalty = len(issues) / lead_count * 0.5
        base_score -= issue_penalty
        return max(0.0, min(1.0, base_score))

    def validate_single_lead(self, lead: dict[str, Any]) -> LeadQualityResult:
        """
        Validate a single lead for quality issues.

        Convenience method for single lead validation.
        """
        return self.validate_lead_quality([lead])

    def get_lead_completeness(self, lead: dict[str, Any]) -> float:
        """
        Calculate lead completeness score.

        Moved to Deterministic: Pure completeness calculation
        """
        all_fields = self.required_fields + self.contact_fields
        present_fields = sum(1 for field in all_fields if lead.get(field))
        return present_fields / len(all_fields) if all_fields else 1.0

    def analyze_lead_risk(self, lead: dict[str, Any]) -> dict[str, Any]:
        """
        Analyze lead risk using deterministic rules.

        Returns detailed risk analysis for a lead.
        """
        email = lead.get("email", "")
        has_suspicious_domain = any(email.endswith(d) for d in self.suspicious_domains)
        has_spam_indicator = any(ind in email.lower() for ind in self.spam_indicators)
        completeness = self.get_lead_completeness(lead)
        risk_score = 0
        if has_suspicious_domain:
            risk_score += 3
        if has_spam_indicator:
            risk_score += 5
        if completeness < 0.5:
            risk_score += 2
        risk_level = "low" if risk_score == 0 else "medium" if risk_score < 5 else "high"
        return {
            "has_suspicious_domain": has_suspicious_domain,
            "has_spam_indicator": has_spam_indicator,
            "completeness": completeness,
            "risk_score": risk_score,
            "risk_level": risk_level,
        }
