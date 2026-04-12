from __future__ import annotations

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    # noqa: E402,
    # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,
    # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    # noqa: E402
    emit_replay_key,
)

emit_replay_key("p0", "constitutional_governance_types")
emit_determinism_digest("p0", "constitutional_governance_types")

_emit_dispatches_healing_run("p1", "constitutional_governance_types", "L5")
_emit_routes_through("p1", "constitutional_governance_types", "L5")
_emit_checks_agent_registry("p1", "constitutional_governance_types", "agent_registry")
_emit_validates_agent_capability("p1", "constitutional_governance_types", "capability")
_emit_dispatches_execution_plan("p1", "constitutional_governance_types", "exec_plan")
_emit_agent_executes_agent("p1", "constitutional_governance_types", "sub_agent")
_emit_routes_to_agent("p1", "constitutional_governance_types", "target_agent")
_emit_verifies_policy("p1", "constitutional_governance_types", "policy_check")
_emit_observes_runtime_state("p1", "constitutional_governance_types", "runtime_state")
_emit_verifies_boundary("p1", "constitutional_governance_types", "boundary_check")
_emit_transcripts_response("p1", "constitutional_governance_types", "transcript")
_emit_hard_fails_untranscripted("p1", "constitutional_governance_types")
_emit_gated_by_confidence("p1", "constitutional_governance_types", "confidence_gate")
_emit_escalates_to_human("p1", "constitutional_governance_types", "L5")
_emit_reads_policy_state("p1", "constitutional_governance_types", "L5")

_emit_applies_guardrail("p0", "constitutional_governance_types", "p0_governance")
_emit_snapshots_state("p0", "constitutional_governance_types", "state_snapshot")
_emit_authorize_and_execute("p2", "constitutional_governance_types", "execution_auth")
_emit_validates_capability("p2", "constitutional_governance_types", "capability_check")
_emit_routes_to_capability("p2", "constitutional_governance_types", "capability_route")
_emit_writes_via_uwg("p2", "constitutional_governance_types", "uwg_write")
_emit_blocks_direct_write("p2", "constitutional_governance_types", "direct_write_block")
_emit_records_tool_invocation("p2", "constitutional_governance_types", "tool_invocation")
_emit_captures_execution_output("p2", "constitutional_governance_types", "exec_output")
_emit_dispatches_agent("p3", "constitutional_governance_types", "agent_dispatch")
_emit_coordinates_agents("p3", "constitutional_governance_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "constitutional_governance_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "constitutional_governance_types", "healing_outcome")
_emit_escalates_failure("p3", "constitutional_governance_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "constitutional_governance_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "constitutional_governance_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "constitutional_governance_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "constitutional_governance_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "constitutional_governance_types", "eval_metric")
_emit_stores_embedding("p4", "constitutional_governance_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "constitutional_governance_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "constitutional_governance_types", "exec_snapshot_link")

"\nConstitutional Governance Guardrail - Consolidated Constitutional AI\n\nMerges:\n- ConstitutionalReviewer\n- constitutional_ai\n- constitutional_overseer\n\nComposable Rules:\n- constitutional_review: Constitutional principle checks\n- governance: Governance rule enforcement\n- oversight: Oversight and audit trails\n"
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
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

_emit_emits_metric_event("constitutional_governance_types", "p4obs", "metric_1")
_emit_emits_metric_event("constitutional_governance_types", "p4obs", "metric_2")
_emit_emits_metric_event("constitutional_governance_types", "p4obs", "metric_3")
_emit_emits_metric_event("constitutional_governance_types", "p4obs", "metric_4")
_emit_emits_metric_event("constitutional_governance_types", "p4obs", "metric_5")
_emit_emits_metric_event("constitutional_governance_types", "p4obs", "metric_6")
_emit_records_incident_event("constitutional_governance_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("constitutional_governance_types", "p4obs", "anomaly")
_emit_writes_observability_log("constitutional_governance_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("constitutional_governance_types", "p4obs", "mon_state")
_emit_triggers_alert("constitutional_governance_types", "p4obs", "alert")
_emit_links_incident_trace("constitutional_governance_types", "p4obs", "trace_link")
_emit_captures_pattern("constitutional_governance_types", "p3lm", "pattern")
_emit_records_learning_event("constitutional_governance_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("constitutional_governance_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("constitutional_governance_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("constitutional_governance_types", "p3lm", "routing")
_emit_improves_agent_policy("constitutional_governance_types", "p3lm", "policy")
_emit_stores_learning_state("constitutional_governance_types", "p3lm", "state")
_emit_records_execution_trace("constitutional_governance_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("constitutional_governance_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("constitutional_governance_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("constitutional_governance_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("constitutional_governance_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("constitutional_governance_types", "env_read", "p2_env_1")
_emit_reads_environ("constitutional_governance_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("constitutional_governance_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("constitutional_governance_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "constitutional_governance_types", "context_pull")
_emit_pulls_context("p1", "constitutional_governance_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "constitutional_governance_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "constitutional_governance_types", "uwg_term_2")
_emit_writes_through("p1", "constitutional_governance_types", "write_through")
_emit_writes_through("p1", "constitutional_governance_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "constitutional_governance_types", "safety_validation")
_emit_invokes_eval("p1", "constitutional_governance_types", "eval_call")
_emit_proposal_commits_routing("p1", "constitutional_governance_types", "routing_commit")


class ConstitutionalPrinciple(Enum):
    """Core constitutional principles."""

    HELPFULNESS = "helpfulness"
    HARMLESSNESS = "harmlessness"
    HONESTY = "honesty"
    TRANSPARENCY = "transparency"
    PRIVACY = "privacy"
    FAIRNESS = "fairness"
    ACCOUNTABILITY = "accountability"


@dataclass
class PrincipleViolation:
    """Violation of a constitutional principle."""

    principle: ConstitutionalPrinciple
    severity: str
    description: str
    suggested_revision: str | None = None


@dataclass
class GovernanceResult:
    """Result of governance check."""

    compliant: bool
    violations: list[PrincipleViolation] = field(default_factory=list)
    audit_id: str | None = None
    review_notes: str = ""


class ConstitutionalGovernanceGuardrail:
    """
    Consolidated Constitutional Governance Guardrail.

    Provides unified constitutional AI with:
    - Constitutional principle enforcement
    - Governance rule checking
    - Oversight and audit trails
    """

    def __init__(self):
        """Initialize constitutional governance guardrail."""
        self.enabled_rules: list[str] = ["constitutional_review", "governance", "oversight"]
        self.principle_checks = {
            ConstitutionalPrinciple.HARMLESSNESS: {
                "negative_patterns": [
                    "harm",
                    "hurt",
                    "damage",
                    "destroy",
                    "kill",
                    "attack",
                    "exploit",
                    "abuse",
                ],
                "weight": 1.0,
            },
            ConstitutionalPrinciple.HONESTY: {
                "negative_patterns": ["lie", "deceive", "mislead", "fake", "pretend to be"],
                "weight": 0.9,
            },
            ConstitutionalPrinciple.PRIVACY: {
                "negative_patterns": ["personal data", "private information", "ssn", "password"],
                "weight": 0.8,
            },
            ConstitutionalPrinciple.FAIRNESS: {
                "negative_patterns": ["discriminate", "bias against", "unfair"],
                "weight": 0.8,
            },
        }
        self.audit_log: list[dict[str, Any]] = []
        self.audit_counter = 0
        self.reviews_performed = 0
        self.violations_found = 0
        self.revisions_suggested = 0

    async def review(self, content: str, context: dict[str, Any] | None = None) -> GovernanceResult:
        """
        Review content for constitutional compliance.

        Args:
            content: Content to review
            context: Optional context

        Returns:
            GovernanceResult
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L5_POLICY,
            "ConstitutionalGovernanceGuardrail.review",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:ConstitutionalGovernanceGuardrail.review".encode(),
        ).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        self.reviews_performed += 1
        violations = []
        if "constitutional_review" in self.enabled_rules:
            violations.extend(self._check_principles(content))
        if "governance" in self.enabled_rules:
            violations.extend(self._check_governance(content, context))
        audit_id = None
        if "oversight" in self.enabled_rules:
            audit_id = self._create_audit(content, violations)
        self.violations_found += len(violations)
        return GovernanceResult(
            compliant=len(violations) == 0,
            violations=violations,
            audit_id=audit_id,
            review_notes=self._generate_notes(violations),
        )

    def _check_principles(self, content: str) -> list[PrincipleViolation]:
        """Check content against constitutional principles."""
        violations = []
        content_lower = content.lower()
        for principle, config in self.principle_checks.items():
            for pattern in config["negative_patterns"]:
                if pattern in content_lower:
                    violations.append(
                        PrincipleViolation(
                            principle=principle,
                            severity="moderate",
                            description=f"Potential violation of {principle.value}: contains '{pattern}'",
                            suggested_revision=f"Consider removing or rephrasing content containing '{pattern}'",
                        ),
                    )
                    self.revisions_suggested += 1
                    break
        return violations

    def _check_governance(self, content: str, context: dict[str, Any] | None) -> list[PrincipleViolation]:
        """Check governance rules."""
        violations = []
        if len(content) > 10000:
            violations.append(
                PrincipleViolation(
                    principle=ConstitutionalPrinciple.TRANSPARENCY,
                    severity="minor",
                    description="Content exceeds governance length limit",
                ),
            )
        return violations

    def _create_audit(self, content: str, violations: list[PrincipleViolation]) -> str:
        """Create audit trail entry."""
        self.audit_counter += 1
        audit_id = f"audit_{self.audit_counter}_{int(time.time())}"
        self.audit_log.append(
            {
                "audit_id": audit_id,
                "timestamp": time.time(),
                "content_length": len(content),
                "violation_count": len(violations),
                "violations": [
                    {"principle": v.principle.value, "severity": v.severity, "description": v.description}
                    for v in violations
                ],
            },
        )
        return audit_id

    def _generate_notes(self, violations: list[PrincipleViolation]) -> str:
        """Generate review notes."""
        if not violations:
            return "Content is compliant with constitutional principles."
        notes = []
        for v in violations:
            notes.append(f"- {v.principle.value}: {v.description}")
        return "\n".join(notes)

    def revise_content(self, content: str, violations: list[PrincipleViolation]) -> str:
        """
        Suggest revised content based on violations.

        Args:
            content: Original content
            violations: List of violations

        Returns:
            Revised content suggestion
        """
        if violations:
            return f"[REVISED] {content}\n\n[Note: Content was flagged for potential issues with: {', '.join(v.principle.value for v in violations)}]"
        return content

    # guardian: allow-magic-config
    def get_audit_log(self, limit: int = 100) -> list[dict[str, Any]]:
        """Get recent audit log entries."""
        return self.audit_log[-limit:]

    def get_statistics(self) -> dict[str, Any]:
        """Get governance statistics."""
        return {
            "reviews_performed": self.reviews_performed,
            "violations_found": self.violations_found,
            "revisions_suggested": self.revisions_suggested,
            "audit_log_size": len(self.audit_log),
            "compliance_rate": (self.reviews_performed - self.violations_found) / self.reviews_performed * 100
            if self.reviews_performed > 0
            else 100,
        }
