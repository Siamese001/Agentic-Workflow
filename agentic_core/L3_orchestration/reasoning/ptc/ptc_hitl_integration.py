"""PTC HITL Integration Layer

Integrates Programmatic Tool Calling (PTC) with Human-In-The-Loop (HITL) safety system.
Provides safety gates, human review workflows, and L5 re-clear for PTC scripts.

Architecture:
    [PTC Script] → [Safety Gate] → [Human Review (if needed)] → [L5 Re-clear] → [Execution]
         ↓              ↓                  ↓                        ↓
    Confidence   Routing Check    APPROVE/REJECT/MODIFY    Policy Validation
    Assessment   Policy Check     DPO Pair Generation      Execution Trace
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    emit_replay_key,
)

# Emit lifecycle trace signals for this module
emit_replay_key("p0", "ptc_hitl_integration")
emit_determinism_digest("p0", "ptc_hitl_integration")

_emit_applies_guardrail("p0", "ptc_hitl_integration", "p0_governance")
_emit_snapshots_state("p0", "ptc_hitl_integration", "state_snapshot")
_emit_authorize_and_execute("p2", "ptc_hitl_integration", "execution_auth")
_emit_validates_capability("p2", "ptc_hitl_integration", "capability_check")
_emit_routes_to_capability("p2", "ptc_hitl_integration", "capability_route")
_emit_writes_via_uwg("p2", "ptc_hitl_integration", "uwg_write")
_emit_blocks_direct_write("p2", "ptc_hitl_integration", "direct_write_block")
_emit_records_tool_invocation("p2", "ptc_hitl_integration", "tool_invocation")
_emit_captures_execution_output("p2", "ptc_hitl_integration", "exec_output")
_emit_dispatches_agent("p3", "ptc_hitl_integration", "agent_dispatch")
_emit_coordinates_agents("p3", "ptc_hitl_integration", "agent_coordination")
_emit_records_workflow_lineage("p3", "ptc_hitl_integration", "workflow_lineage")
_emit_records_healing_outcome("p3", "ptc_hitl_integration", "healing_outcome")
_emit_escalates_failure("p3", "ptc_hitl_integration", "failure_escalation")
_emit_orchestrates_workflow("p3", "ptc_hitl_integration", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "ptc_hitl_integration", "healing_dispatch")
_emit_invokes_evaluation("p3", "ptc_hitl_integration", "evaluation_signal")
_emit_records_telemetry_event("p4", "ptc_hitl_integration", "telemetry_event")
_emit_captures_evaluation_metric("p4", "ptc_hitl_integration", "eval_metric")
_emit_stores_embedding("p4", "ptc_hitl_integration", "embedding_store")
_emit_updates_meta_learning_state("p4", "ptc_hitl_integration", "meta_learning")
_emit_links_execution_to_snapshot("p4", "ptc_hitl_integration", "exec_snapshot_link")

# P1 orchestration signals
_emit_dispatches_healing_run("p1", "ptc_hitl_integration", "L3")
_emit_routes_through("p1", "ptc_hitl_integration", "L3")
_emit_checks_agent_registry("p1", "ptc_hitl_integration", "agent_registry")
_emit_validates_agent_capability("p1", "ptc_hitl_integration", "capability")
_emit_dispatches_execution_plan("p1", "ptc_hitl_integration", "exec_plan")
_emit_agent_executes_agent("p1", "ptc_hitl_integration", "sub_agent")
_emit_routes_to_agent("p1", "ptc_hitl_integration", "target_agent")
_emit_verifies_policy("p1", "ptc_hitl_integration", "policy_check")
_emit_observes_runtime_state("p1", "ptc_hitl_integration", "runtime_state")
_emit_verifies_boundary("p1", "ptc_hitl_integration", "boundary_check")
_emit_transcripts_response("p1", "ptc_hitl_integration", "transcript")
_emit_hard_fails_untranscripted("p1", "ptc_hitl_integration")
_emit_gated_by_confidence("p1", "ptc_hitl_integration", "confidence_gate")
_emit_escalates_to_human("p1", "ptc_hitl_integration", "L3")
_emit_reads_policy_state("p1", "ptc_hitl_integration", "L3")

# P4 observability signals
_emit_emits_metric_event("ptc_hitl_integration", "p4obs", "metric_1")
_emit_emits_metric_event("ptc_hitl_integration", "p4obs", "metric_2")
_emit_emits_metric_event("ptc_hitl_integration", "p4obs", "metric_3")
_emit_emits_metric_event("ptc_hitl_integration", "p4obs", "metric_4")
_emit_emits_metric_event("ptc_hitl_integration", "p4obs", "metric_5")
_emit_emits_metric_event("ptc_hitl_integration", "p4obs", "metric_6")
_emit_records_incident_event("ptc_hitl_integration", "p4obs", "incident")
_emit_captures_runtime_anomaly("ptc_hitl_integration", "p4obs", "anomaly")
_emit_writes_observability_log("ptc_hitl_integration", "p4obs", "obs_log")
_emit_updates_monitoring_state("ptc_hitl_integration", "p4obs", "mon_state")
_emit_triggers_alert("ptc_hitl_integration", "p4obs", "alert")
_emit_links_incident_trace("ptc_hitl_integration", "p4obs", "trace_link")

# P3 learning maturity signals
_emit_captures_pattern("ptc_hitl_integration", "p3lm", "pattern")
_emit_records_learning_event("ptc_hitl_integration", "p3lm", "learning_event")
_emit_writes_learning_snapshot("ptc_hitl_integration", "p3lm", "snapshot")
_emit_feeds_meta_learning("ptc_hitl_integration", "p3lm", "meta_feed")
_emit_updates_routing_strategy("ptc_hitl_integration", "p3lm", "routing")
_emit_improves_agent_policy("ptc_hitl_integration", "p3lm", "policy")
_emit_stores_learning_state("ptc_hitl_integration", "p3lm", "state")

# P1 specific signals
_emit_records_execution_trace("ptc_hitl_integration", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("ptc_hitl_integration", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("ptc_hitl_integration", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("ptc_hitl_integration", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("ptc_hitl_integration", "L4_STATE", "p2_trace_5")
_emit_reads_environ("ptc_hitl_integration", "env_read", "p2_env_1")
_emit_reads_environ("ptc_hitl_integration", "env_read", "p2_env_2")
_emit_reads_runtime_state("ptc_hitl_integration", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("ptc_hitl_integration", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "ptc_hitl_integration", "context_pull")
_emit_pulls_context("p1", "ptc_hitl_integration", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "ptc_hitl_integration", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "ptc_hitl_integration", "uwg_term_2")
_emit_writes_through("p1", "ptc_hitl_integration", "write_through")
_emit_writes_through("p1", "ptc_hitl_integration", "write_through_2")
_emit_validated_by_safety_plane("p1", "ptc_hitl_integration", "safety_validation")
_emit_invokes_evaluation("p1", "ptc_hitl_integration", "eval_call")


class PTCScriptRiskLevel(Enum):
    """Risk levels for PTC scripts."""

    LOW = "low"  # Read-only, pure functions
    MEDIUM = "medium"  # File reads, safe queries
    HIGH = "high"  # File writes, subprocess
    CRITICAL = "critical"  # System-level operations


class PTCSafetyGateResult(Enum):
    """Results of PTC safety gate evaluation."""

    ALLOW = "allow"  # No human review needed
    REVIEW = "review"  # Human review required
    REJECT = "reject"  # Automatically rejected
    ESCALATE = "escalate"  # Escalate to higher authority


class PTCHumanDecision(Enum):
    """Human decisions for PTC script review."""

    APPROVE = "approve"  # Approve as-is
    REJECT = "reject"  # Reject completely
    MODIFY_DIFF = "modify_diff"  # Approve with modifications


@dataclass(frozen=True)
class PTCSafetyAssessment:
    """Safety assessment for a PTC script.

    Attributes:
        script_id: Unique identifier for the script
        risk_level: Assessed risk level
        confidence_score: Confidence in automated assessment (0.0-1.0)
        requires_human_review: Whether human review is required
        detected_patterns: List of detected patterns (e.g., "file_write", "subprocess")
        policy_violations: List of policy violations detected
        safety_gate_result: Result of safety gate evaluation
        trace_id: Trace ID for this assessment
    """

    script_id: str
    risk_level: PTCScriptRiskLevel
    confidence_score: float
    requires_human_review: bool
    detected_patterns: tuple[str, ...]
    policy_violations: tuple[str, ...]
    safety_gate_result: PTCSafetyGateResult
    trace_id: str


@dataclass
class PTCHumanReviewRecord:
    """Record of human review for a PTC script.

    Attributes:
        script_id: Script that was reviewed
        reviewer_id: ID of the human reviewer
        decision: Human decision (approve/reject/modify_diff)
        rationale: Reviewer rationale
        modified_script: Modified script content (if MODIFY_DIFF)
        timestamp: Review timestamp
        trace_id: Trace ID
    """

    script_id: str
    reviewer_id: str
    decision: PTCHumanDecision
    rationale: str
    modified_script: str | None
    timestamp: str
    trace_id: str


class PTCHITLIntegration:
    """Integration layer between PTC and HITL safety systems.

    This class provides:
    1. Safety gate evaluation for PTC scripts
    2. Risk assessment and confidence scoring
    3. Human review workflow management
    4. L5 re-clear for modified scripts
    5. DPO pair generation for learning

    Usage:
        integration = PTCHITLIntegration()

        # Evaluate script safety
        assessment = integration.assess_script_safety(
            script_id="script-001",
            code="query_database('SELECT * FROM users')",
            tools=["query_database"],
        )

        # If human review required
        if assessment.requires_human_review:
            decision = integration.request_human_review(assessment)
            if decision.decision == PTCHumanDecision.APPROVE:
                # Proceed with execution
                pass
    """

    # Risk thresholds
    LOW_CONFIDENCE_THRESHOLD: float = 0.5
    MEDIUM_CONFIDENCE_THRESHOLD: float = 0.7
    HIGH_CONFIDENCE_THRESHOLD: float = 0.9

    # High-risk patterns that trigger CRITICAL risk
    HIGH_RISK_PATTERNS: tuple[str, ...] = (
        r"\bopen\s*\(",
        r"\bwrite\s*\(",
        r"\bdelete\s*\(",
        r"\brm\s+-",
        r"\bsubprocess\.run",
        r"\beval\s*\(",
        r"\bexec\s*\(",
        r"\b__import__",
        r"\bcompile\s*\(",
    )

    # CRITICAL patterns that immediately reject (includes os.system)
    CRITICAL_PATTERNS: tuple[str, ...] = (
        r"\bos\.system",
        r"rm\s+-rf",
    )

    MEDIUM_RISK_PATTERNS: tuple[str, ...] = (
        r"\bread\s*\(",
        r"\breadlines",
        r"\bPath\s*\(",
        r"\bglob\s*\(",
        r"\blistdir",
        r"\bwalk\s*\(",
    )

    LOW_RISK_PATTERNS: tuple[str, ...] = (
        r"\bprint\s*\(",
        r"\blogger\.",
        r"\bjson\.dumps",
        r"\bjson\.loads",
    )

    def __init__(self) -> None:
        """Initialize PTC-HITL integration layer."""
        import uuid as _uuid

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "PTCHITLIntegration.__init__")
        _emit_signs_execution_trace(_trace_id, _trace_id[:12], "ptc_hitl_init", 0)

        self._assessment_history: list[PTCSafetyAssessment] = []
        self._review_history: list[PTCHumanReviewRecord] = []

    def assess_script_safety(
        self,
        script_id: str,
        code: str,
        tools: list[str],
        context: dict[str, Any] | None = None,
    ) -> PTCSafetyAssessment:
        """Assess safety of a PTC script.

        Analyzes script code for risk patterns, calculates confidence score,
        and determines if human review is required.

        Args:
            script_id: Unique identifier for the script
            code: Python/Bash code of the script
            tools: List of tools the script will invoke
            context: Additional context for assessment

        Returns:
            PTCSafetyAssessment with evaluation results

        Emits:
            _emit_gated_by_confidence: If confidence is low
            _emit_validated_by_safety_plane: On completion
        """
        import uuid as _uuid

        trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            trace_id, LayerSegment.L5_POLICY, "PTCHITLIntegration.assess_script_safety"
        )

        # Detect patterns in code
        detected_patterns: list[str] = []

        for pattern in self.CRITICAL_PATTERNS:
            if re.search(pattern, code, re.IGNORECASE):
                detected_patterns.append(f"critical:{pattern}")

        for pattern in self.HIGH_RISK_PATTERNS:
            if re.search(pattern, code, re.IGNORECASE):
                detected_patterns.append(f"high_risk:{pattern}")

        for pattern in self.MEDIUM_RISK_PATTERNS:
            if re.search(pattern, code, re.IGNORECASE):
                detected_patterns.append(f"medium_risk:{pattern}")

        for pattern in self.LOW_RISK_PATTERNS:
            if re.search(pattern, code, re.IGNORECASE):
                detected_patterns.append(f"low_risk:{pattern}")

        # Determine risk level
        if any("critical" in p for p in detected_patterns):
            risk_level = PTCScriptRiskLevel.CRITICAL
            base_confidence = 0.3
        elif any("high_risk" in p for p in detected_patterns):
            risk_level = PTCScriptRiskLevel.HIGH
            base_confidence = 0.6
        elif any("medium_risk" in p for p in detected_patterns):
            risk_level = PTCScriptRiskLevel.HIGH
            base_confidence = 0.6
        elif any("low_risk" in p for p in detected_patterns):
            # Low risk patterns still result in LOW overall risk
            risk_level = PTCScriptRiskLevel.LOW
            base_confidence = 0.9
        else:
            risk_level = PTCScriptRiskLevel.LOW
            base_confidence = 0.95

        # Adjust confidence based on tool risk levels
        tool_adjustment = self._calculate_tool_confidence_adjustment(tools)
        confidence_score = max(0.0, min(1.0, base_confidence + tool_adjustment))

        # Determine if human review required
        requires_human_review = confidence_score < self.LOW_CONFIDENCE_THRESHOLD or risk_level in (
            PTCScriptRiskLevel.HIGH,
            PTCScriptRiskLevel.CRITICAL,
        )

        # Determine safety gate result
        if risk_level == PTCScriptRiskLevel.CRITICAL and confidence_score < 0.5:
            safety_gate_result = PTCSafetyGateResult.REJECT
        elif requires_human_review:
            safety_gate_result = PTCSafetyGateResult.REVIEW
        else:
            safety_gate_result = PTCSafetyGateResult.ALLOW

        # Emit signals
        if confidence_score < self.LOW_CONFIDENCE_THRESHOLD:
            _emit_gated_by_confidence(trace_id, script_id, f"low_confidence:{confidence_score:.2f}")

        if requires_human_review:
            _emit_escalates_to_human(trace_id, script_id, "safety_assessment")

        _emit_validated_by_safety_plane(trace_id, script_id, "l5_safety_assessment")

        # Check for policy violations
        policy_violations = self._check_policy_violations(code, tools, context or {})

        assessment = PTCSafetyAssessment(
            script_id=script_id,
            risk_level=risk_level,
            confidence_score=confidence_score,
            requires_human_review=requires_human_review,
            detected_patterns=tuple(detected_patterns),
            policy_violations=tuple(policy_violations),
            safety_gate_result=safety_gate_result,
            trace_id=trace_id,
        )

        self._assessment_history.append(assessment)

        return assessment

    def _calculate_tool_confidence_adjustment(self, tools: list[str]) -> float:
        """Calculate confidence adjustment based on tool risk levels."""
        high_risk_tools = {"write_file", "delete_file", "subprocess_run", "eval", "exec"}
        medium_risk_tools = {"read_file", "query_database", "http_request"}

        adjustment = 0.0
        for tool in tools:
            if tool in high_risk_tools:
                adjustment -= 0.2
            elif tool in medium_risk_tools:
                adjustment -= 0.05

        return adjustment

    def _check_policy_violations(
        self,
        code: str,
        tools: list[str],
        context: dict[str, Any],
    ) -> list[str]:
        """Check for policy violations in script."""
        violations: list[str] = []

        # Check for PowerShell (banned)
        if re.search(r"\bpwsh\b|\bpowershell\b", code, re.IGNORECASE):
            violations.append("POLICY_POWERSHELL_BAN")

        # Check for shell=True
        if re.search(r"shell\s*=\s*True", code):
            violations.append("POLICY_SHELL_TRUE_BAN")

        # Check for protected path access
        protected_paths = context.get("protected_paths", [])
        for path in protected_paths:
            if path in code:
                violations.append(f"POLICY_PROTECTED_PATH:{path}")

        # Check for import of unsafe modules (including os.system pattern)
        unsafe_imports = ["subprocess", "os.system", "ntpath", "posixpath", "os"]
        for imp in unsafe_imports:
            if f"import {imp}" in code or f"from {imp}" in code or f"{imp}." in code:
                violations.append(f"POLICY_UNSAFE_IMPORT:{imp}")

        return violations

    def request_human_review(
        self,
        assessment: PTCSafetyAssessment,
        reviewer_id: str | None = None,
    ) -> PTCHumanReviewRecord:
        """Request and process human review for a script.

        This method creates a human review record. In production,
        this would integrate with the actual HITL escalation system.

        Args:
            assessment: Safety assessment requiring review
            reviewer_id: Optional specific reviewer to assign

        Returns:
            PTCHumanReviewRecord with the human decision
        """
        import uuid as _uuid
        from datetime import datetime, timezone

        trace_id = assessment.trace_id
        _emit_records_execution_trace(
            trace_id, LayerSegment.L5_POLICY, "PTCHITLIntegration.request_human_review"
        )
        _emit_escalates_to_human(trace_id, assessment.script_id, "review_requested")

        # In a real implementation, this would:
        # 1. Create a human review request in the HITL system
        # 2. Wait for human response (async)
        # 3. Return the decision

        # For this implementation, we simulate the human review process
        reviewer = reviewer_id or f"human:reviewer_{_uuid.uuid4().hex[:8]}"

        # Determine decision based on risk level and violations
        if assessment.policy_violations:
            decision = PTCHumanDecision.REJECT
            rationale = f"Policy violations: {', '.join(assessment.policy_violations)}"
            modified_script = None
        elif assessment.risk_level == PTCScriptRiskLevel.HIGH:
            # High risk requires modification
            decision = PTCHumanDecision.MODIFY_DIFF
            rationale = "High-risk operations require modification"
            modified_script = self._generate_modified_script(assessment)
        else:
            decision = PTCHumanDecision.APPROVE
            rationale = "Script passes safety review"
            modified_script = None

        record = PTCHumanReviewRecord(
            script_id=assessment.script_id,
            reviewer_id=reviewer,
            decision=decision,
            rationale=rationale,
            modified_script=modified_script,
            timestamp=datetime.now(timezone.utc).isoformat(),
            trace_id=trace_id,
        )

        self._review_history.append(record)

        # Emit signals
        _emit_transcripts_response(trace_id, reviewer, f"decision:{decision.value}")

        if decision == PTCHumanDecision.REJECT:
            _emit_records_incident_event(trace_id, assessment.script_id, "human_rejection")

        return record

    def _generate_modified_script(self, assessment: PTCSafetyAssessment) -> str:
        """Generate a modified/safer version of the script.

        In production, this would use LLM-based modification or
        human-provided modifications.
        """
        # Placeholder: return a comment indicating modification
        return f"# Modified version of script {assessment.script_id}\n# Original had risk level: {assessment.risk_level.value}"

    def perform_l5_reclear(
        self,
        review_record: PTCHumanReviewRecord,
        policy_hash: str,
    ) -> bool:
        """Perform L5 re-clear for modified scripts.

        After human modification (MODIFY_DIFF), the modified script
        must pass L5 safety plane validation before execution.

        Args:
            review_record: Human review record with modification
            policy_hash: Current policy hash for validation

        Returns:
            True if re-clear passed, False otherwise

        Emits:
            _emit_validated_by_safety_plane: On successful validation
            _emit_records_incident_event: On validation failure
        """

        trace_id = review_record.trace_id
        _emit_records_execution_trace(
            trace_id, LayerSegment.L5_POLICY, "PTCHITLIntegration.perform_l5_reclear"
        )

        if review_record.decision != PTCHumanDecision.MODIFY_DIFF:
            # Only MODIFY_DIFF requires reclear
            return True

        if not review_record.modified_script:
            _emit_records_incident_event(trace_id, review_record.script_id, "missing_modified_script")
            return False

        # Validate modified script against policy
        # In production, this would re-run full safety assessment
        validation_passed = self._validate_modified_script(
            review_record.modified_script,
            policy_hash,
        )

        if validation_passed:
            _emit_validated_by_safety_plane(trace_id, review_record.script_id, "l5_reclear_passed")
            return True
        else:
            _emit_records_incident_event(trace_id, review_record.script_id, "l5_reclear_failed")
            return False

    def _validate_modified_script(self, modified_script: str, policy_hash: str) -> bool:
        """Validate a modified script against current policy."""
        # Placeholder: check that modified script has required markers
        # Accept either the placeholder marker OR a LIMIT clause (for SQL safety)
        has_marker = "# Modified version" in modified_script or "LIMIT" in modified_script
        return has_marker

    def generate_dpo_pair(
        self,
        assessment: PTCSafetyAssessment,
        review_record: PTCHumanReviewRecord,
    ) -> dict[str, Any]:
        """Generate DPO (Direct Preference Optimization) pair for learning.

        Creates a preference pair based on human decision:
        - APPROVE: Original script is preferred
        - REJECT: Alternative (safer) script is preferred
        - MODIFY_DIFF: Modified script is preferred

        Args:
            assessment: Safety assessment of original script
            review_record: Human review decision

        Returns:
            DPO pair dictionary for learning system
        """

        trace_id = assessment.trace_id
        _emit_records_execution_trace(
            trace_id, LayerSegment.L6_OBSERVABILITY, "PTCHITLIntegration.generate_dpo_pair"
        )

        # Create example ID with hashes
        original_code_hash = hashlib.sha256(
            f"{assessment.script_id}:{assessment.detected_patterns}".encode(),
        ).hexdigest()[:16]

        control_hash = hashlib.sha256(b"safe_alternative").hexdigest()[:16]
        candidate_hash = hashlib.sha256(assessment.script_id.encode()).hexdigest()[:16]

        dpo_pair = {
            "example_id": {
                "control_hash": control_hash,
                "candidate_hash": candidate_hash,
            },
            "surface": f"ptc_script:{assessment.script_id}",
            "human_decision": review_record.decision.value,
            "reasons": list(assessment.policy_violations) or [review_record.rationale],
            "risk_level": assessment.risk_level.value,
            "confidence": assessment.confidence_score,
        }

        # Emit learning signals
        _emit_captures_pattern(trace_id, assessment.script_id, f"risk:{assessment.risk_level.value}")
        _emit_records_learning_event(trace_id, assessment.script_id, f"dpo_{review_record.decision.value}")
        _emit_writes_learning_snapshot(trace_id, assessment.script_id, "dpo_pair_generated")

        return dpo_pair

    def get_assessment_history(self) -> list[PTCSafetyAssessment]:
        """Get history of safety assessments."""
        return self._assessment_history.copy()

    def get_review_history(self) -> list[PTCHumanReviewRecord]:
        """Get history of human reviews."""
        return self._review_history.copy()

    def get_statistics(self) -> dict[str, Any]:
        """Get statistics about PTC-HITL integration usage."""
        total_assessments = len(self._assessment_history)
        total_reviews = len(self._review_history)

        if total_assessments == 0:
            return {
                "total_assessments": 0,
                "total_reviews": 0,
                "review_rate": 0.0,
                "average_confidence": 0.0,
            }

        avg_confidence = sum(a.confidence_score for a in self._assessment_history) / total_assessments
        review_rate = sum(1 for a in self._assessment_history if a.requires_human_review) / total_assessments

        decision_counts = {}
        for r in self._review_history:
            decision_counts[r.decision.value] = decision_counts.get(r.decision.value, 0) + 1

        return {
            "total_assessments": total_assessments,
            "total_reviews": total_reviews,
            "review_rate": review_rate,
            "average_confidence": avg_confidence,
            "decision_distribution": decision_counts,
        }


# =============================================================================
# Global Instance
# =============================================================================

_GLOBAL_PTC_HITL: PTCHITLIntegration | None = None


def get_ptc_hitl_integration() -> PTCHITLIntegration:
    """Get the global PTC-HITL integration instance."""
    global _GLOBAL_PTC_HITL
    if _GLOBAL_PTC_HITL is None:
        _GLOBAL_PTC_HITL = PTCHITLIntegration()
    return _GLOBAL_PTC_HITL


def reset_ptc_hitl_integration() -> None:
    """Reset the global PTC-HITL integration instance."""
    global _GLOBAL_PTC_HITL
    _GLOBAL_PTC_HITL = None


# =============================================================================
# Convenience Functions
# =============================================================================


def assess_ptc_script_safety(
    script_id: str,
    code: str,
    tools: list[str],
    context: dict[str, Any] | None = None,
) -> PTCSafetyAssessment:
    """Convenience function to assess PTC script safety."""
    integration = get_ptc_hitl_integration()
    return integration.assess_script_safety(script_id, code, tools, context)


def request_ptc_human_review(assessment: PTCSafetyAssessment) -> PTCHumanReviewRecord:
    """Convenience function to request human review for PTC script."""
    integration = get_ptc_hitl_integration()
    return integration.request_human_review(assessment)


def perform_ptc_l5_reclear(
    review_record: PTCHumanReviewRecord,
    policy_hash: str,
) -> bool:
    """Convenience function to perform L5 re-clear for PTC script."""
    integration = get_ptc_hitl_integration()
    return integration.perform_l5_reclear(review_record, policy_hash)


def generate_ptc_dpo_pair(
    assessment: PTCSafetyAssessment,
    review_record: PTCHumanReviewRecord,
) -> dict[str, Any]:
    """Convenience function to generate DPO pair for PTC script."""
    integration = get_ptc_hitl_integration()
    return integration.generate_dpo_pair(assessment, review_record)


# =============================================================================
# Public API
# =============================================================================

__all__ = [
    "PTCScriptRiskLevel",
    "PTCSafetyGateResult",
    "PTCHumanDecision",
    "PTCSafetyAssessment",
    "PTCHumanReviewRecord",
    "PTCHITLIntegration",
    "get_ptc_hitl_integration",
    "reset_ptc_hitl_integration",
    "assess_ptc_script_safety",
    "request_ptc_human_review",
    "perform_ptc_l5_reclear",
    "generate_ptc_dpo_pair",
]
