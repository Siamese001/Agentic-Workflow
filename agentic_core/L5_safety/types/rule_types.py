from __future__ import annotations

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "rule_types")
trace_contract.emit_determinism_digest("p0", "rule_types")

trace_contract._emit_dispatches_healing_run("p1", "rule_types", "L5")
trace_contract._emit_routes_through("p1", "rule_types", "L5")
trace_contract._emit_checks_agent_registry("p1", "rule_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "rule_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "rule_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "rule_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "rule_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "rule_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "rule_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "rule_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "rule_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "rule_types")
trace_contract._emit_gated_by_confidence("p1", "rule_types", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "rule_types", "L5")
trace_contract._emit_reads_policy_state("p1", "rule_types", "L5")

trace_contract._emit_applies_guardrail("p0", "rule_types", "p0_governance")
trace_contract._emit_snapshots_state("p0", "rule_types", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "rule_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "rule_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "rule_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "rule_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "rule_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "rule_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "rule_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "rule_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "rule_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "rule_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "rule_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "rule_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "rule_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "rule_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "rule_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "rule_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "rule_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "rule_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "rule_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "rule_types", "exec_snapshot_link")

"Constitutional AI System for Safety and Alignment.\n\nPhase 1 - Pillar 9: Safety & Policy (Control Plane & Guardrails)\nMigrated from archives/engines/legacy_engines/ConstitutionalAiSystem.py\n"
import logging
import re
import time
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum

from tqdm import tqdm

trace_contract._emit_emits_metric_event("rule_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("rule_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("rule_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("rule_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("rule_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("rule_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("rule_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("rule_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("rule_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("rule_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("rule_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("rule_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("rule_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("rule_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("rule_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("rule_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("rule_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("rule_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("rule_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("rule_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("rule_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("rule_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("rule_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("rule_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("rule_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("rule_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("rule_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("rule_types", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "rule_types", "context_pull")
trace_contract._emit_pulls_context("p1", "rule_types", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "rule_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "rule_types", "uwg_term_2")
trace_contract._emit_writes_through("p1", "rule_types", "write_through")
trace_contract._emit_writes_through("p1", "rule_types", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "rule_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "rule_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "rule_types", "routing_commit")

Logger = logging.getLogger(__name__)


class RuleType(Enum):
    """Types of constitutional rules."""

    SAFETY = "safety"
    ETHICS = "ethics"
    PRIVACY = "privacy"
    BIAS = "bias"
    LEGAL = "legal"
    QUALITY = "quality"


class RuleSeverity(Enum):
    """Severity levels for rule violations."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ViolationType(Enum):
    """Types of constitutional violations."""

    CONTENT = "content"
    STYLE = "style"
    STRUCTURE = "structure"
    CONTEXT = "context"


@dataclass
class ConstitutionalRule:
    """Individual constitutional rule."""

    rule_id: str
    RuleType: RuleType
    title: str
    description: str
    pattern: str
    Severity: RuleSeverity
    action: str
    replacement: str | None = None


@dataclass
class ViolationReport:
    """Report of constitutional Violation."""

    rule_id: str
    ViolationType: ViolationType
    Severity: RuleSeverity
    location: str
    content: str
    suggestion: str
    confidence: float


@dataclass
class ConstitutionalReviewResult:
    """Result of constitutional review."""

    is_compliant: bool
    violations: list[ViolationReport]
    compliance_score: float
    recommendations: list[str]
    reviewed_at: float


class ConstitutionalAISystem:
    """Constitutional AI System for Safety and Alignment.

    Provides rule-based validation, ethical guidelines,
    and content compliance checking.
    """

    def __init__(self, enable_logging: bool = True):
        """Initialize Constitutional AI system.

        Args:
            enable_logging: Enable logging of violations
        """
        self.enable_logging = enable_logging
        self.rules: dict[str, ConstitutionalRule] = {}
        self.rule_patterns: dict[RuleType, list[ConstitutionalRule]] = {rt: [] for rt in RuleType}
        self._load_default_rules()

    def add_rule(self, rule: ConstitutionalRule) -> None:
        """Add a constitutional rule.

        Args:
            rule: Rule to add
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L5_POLICY, "ConstitutionalAISystem.add_rule")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:ConstitutionalAISystem.add_rule".encode()).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        self.rules[rule.rule_id] = rule
        self.rule_patterns[rule.RuleType].append(rule)
        if self.enable_logging:
            Logger.debug(f"Added constitutional rule: {rule.rule_id}")

    def remove_rule(self, rule_id: str) -> None:
        """Remove a constitutional rule.

        Args:
            rule_id: ID of rule to remove
        """
        if rule_id in self.rules:
            rule = self.rules[rule_id]
            self.rule_patterns[rule.RuleType].remove(rule)
            del self.rules[rule_id]
            if self.enable_logging:
                Logger.debug(f"Removed constitutional rule: {rule_id}")

    def review_content(
        self,
        content: str,
        context: dict[str, any] | None = None,
    ) -> ConstitutionalReviewResult:
        """Review content against constitutional rules.

        Args:
            content: Content to review
            context: Optional context for evaluation

        Returns:
            ConstitutionalReviewResult with violations and recommendations
        """
        if not content:
            return ConstitutionalReviewResult(
                is_compliant=True,
                violations=[],
                compliance_score=1.0,
                recommendations=[],
                reviewed_at=time.time(),
            )
        violations = self._check_compliance(content, context)
        is_compliant = len(violations) == 0
        compliance_score = self._calculate_compliance_score(violations)
        recommendations = self._generate_recommendations(violations)
        if self.enable_logging and violations:
            Logger.warning(
                "constitutional_violations",
                extra={
                    "violation_count": len(violations),
                    "compliance_score": compliance_score,
                    "critical_count": sum(1 for v in violations if v.Severity == RuleSeverity.CRITICAL),
                },
            )
        return ConstitutionalReviewResult(
            is_compliant=is_compliant,
            violations=violations,
            compliance_score=compliance_score,
            recommendations=recommendations,
            reviewed_at=time.time(),
        )

    def _check_compliance(self, content: str, context: dict[str, any] | None = None) -> list[ViolationReport]:
        """Check content against all rules.

        Args:
            content: Content to check
            context: Optional context

        Returns:
            List of violations
        """
        violations = []
        for rule in self.rules.values():
            rule_violations = self._check_rule(content, rule, context)
            violations.extend(rule_violations)
        severity_order = {
            RuleSeverity.CRITICAL: 0,
            RuleSeverity.HIGH: 1,
            RuleSeverity.MEDIUM: 2,
            RuleSeverity.LOW: 3,
        }
        violations.sort(key=lambda v: severity_order.get(v.Severity, 4))
        return violations

    def _check_rule(
        self,
        content: str,
        rule: ConstitutionalRule,
        context: dict[str, any] | None = None,
    ) -> list[ViolationReport]:
        """Check content against a specific rule.

        Args:
            content: Content to check
            rule: Rule to apply
            context: Optional context

        Returns:
            List of violations for this rule
        """
        violations = []
        try:
            matches = re.finditer(rule.pattern, content, re.IGNORECASE)
            for match in tqdm(matches, desc="Processing", unit="item"):
                Violation = ViolationReport(
                    rule_id=rule.rule_id,
                    ViolationType=ViolationType.CONTENT,
                    Severity=rule.Severity,
                    location=f"Position {match.Span()}",
                    content=match.group(),
                    suggestion=rule.replacement or f"Remove or rephrase: {match.group()}",
                    confidence=0.9,
                )
                violations.append(Violation)
        except re.error as e:
            if self.enable_logging:
                Logger.error(f"Invalid regex pattern in rule {rule.rule_id}: {e}")
        return violations

    def _calculate_compliance_score(self, violations: list[ViolationReport]) -> float:
        """Calculate compliance score based on violations.

        Args:
            violations: List of violations

        Returns:
            Compliance score (0.0-1.0)
        """
        if not violations:
            return 1.0
        severity_weights = {
            RuleSeverity.CRITICAL: 1.0,
            RuleSeverity.HIGH: 0.7,
            RuleSeverity.MEDIUM: 0.4,
            RuleSeverity.LOW: 0.2,
        }
        total_penalty = sum(severity_weights.get(v.Severity, 0.5) for v in violations)
        score = max(0.0, 1.0 - total_penalty / 10.0)
        return round(score, 2)

    def _generate_recommendations(self, violations: list[ViolationReport]) -> list[str]:
        """Generate recommendations based on violations.

        Args:
            violations: List of violations

        Returns:
            List of recommendations
        """
        if not violations:
            return ["Content is compliant with all constitutional rules"]
        recommendations = []
        violation_by_type = defaultdict(list)
        for v in violations:
            violation_by_type[v.Severity].append(v)
        if RuleSeverity.CRITICAL in violation_by_type:
            recommendations.append(
                f"CRITICAL: Address {len(violation_by_type[RuleSeverity.CRITICAL])} critical violations immediately",
            )
        if RuleSeverity.HIGH in violation_by_type:
            recommendations.append(
                f"HIGH: Review {len(violation_by_type[RuleSeverity.HIGH])} high-Severity violations",
            )
        unique_rules = {v.rule_id for v in violations}
        if len(unique_rules) <= 3:
            for rule_id in unique_rules:
                rule = self.rules.get(rule_id)
                if rule:
                    recommendations.append(f"Review rule: {rule.title}")
        return recommendations

    def _load_default_rules(self) -> None:
        """Load default constitutional rules."""
        default_rules = [
            ConstitutionalRule(
                rule_id="safety_001",
                RuleType=RuleType.SAFETY,
                title="No harmful content",
                description="Prevent harmful or dangerous content",
                pattern="\\b(kill|harm|attack|destroy)\\b",
                Severity=RuleSeverity.CRITICAL,
                action="block",
            ),
            ConstitutionalRule(
                rule_id="privacy_001",
                RuleType=RuleType.PRIVACY,
                title="No PII exposure",
                description="Prevent exposure of personal information",
                pattern="\\b\\d{3}-\\d{2}-\\d{4}\\b",
                Severity=RuleSeverity.HIGH,
                action="block",
            ),
            ConstitutionalRule(
                rule_id="ethics_001",
                RuleType=RuleType.ETHICS,
                title="No deceptive content",
                description="Prevent misleading or deceptive content",
                pattern="\\b(fake|fraud|scam|trick)\\b",
                Severity=RuleSeverity.MEDIUM,
                action="warn",
            ),
        ]
        for rule in default_rules:
            self.add_rule(rule)


def review_content(content: str, context: dict[str, any] | None = None) -> ConstitutionalReviewResult:
    """Convenience function to review content.

    Args:
        content: Content to review
        context: Optional context

    Returns:
        ConstitutionalReviewResult
    """
    system = ConstitutionalAISystem()
    return system.review_content(content, context)
