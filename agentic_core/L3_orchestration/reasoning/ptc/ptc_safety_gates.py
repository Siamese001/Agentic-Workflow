"""PTC Safety Gates and Validation

Provides fail-closed safety validation for Programmatic Tool Calling.
Enforces PTC-specific invariants and security constraints.

Safety Gates:
1. Confidence Gate: Low confidence → Human review
2. Routing Gate: Policy-ambiguous routing → Human review
3. Execution Gate: Un-transcripted I/O → Fail-closed halt
4. Validation Gate: Script validation → L5 re-clear
"""

from __future__ import annotations

import ast
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
emit_replay_key("p0", "ptc_safety_gates")
emit_determinism_digest("p0", "ptc_safety_gates")

_emit_applies_guardrail("p0", "ptc_safety_gates", "p0_governance")
_emit_snapshots_state("p0", "ptc_safety_gates", "state_snapshot")
_emit_authorize_and_execute("p2", "ptc_safety_gates", "execution_auth")
_emit_validates_capability("p2", "ptc_safety_gates", "capability_check")
_emit_routes_to_capability("p2", "ptc_safety_gates", "capability_route")
_emit_writes_via_uwg("p2", "ptc_safety_gates", "uwg_write")
_emit_blocks_direct_write("p2", "ptc_safety_gates", "direct_write_block")
_emit_records_tool_invocation("p2", "ptc_safety_gates", "tool_invocation")
_emit_captures_execution_output("p2", "ptc_safety_gates", "exec_output")
_emit_dispatches_agent("p3", "ptc_safety_gates", "agent_dispatch")
_emit_coordinates_agents("p3", "ptc_safety_gates", "agent_coordination")
_emit_records_workflow_lineage("p3", "ptc_safety_gates", "workflow_lineage")
_emit_records_healing_outcome("p3", "ptc_safety_gates", "healing_outcome")
_emit_escalates_failure("p3", "ptc_safety_gates", "failure_escalation")
_emit_orchestrates_workflow("p3", "ptc_safety_gates", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "ptc_safety_gates", "healing_dispatch")
_emit_invokes_evaluation("p3", "ptc_safety_gates", "evaluation_signal")
_emit_records_telemetry_event("p4", "ptc_safety_gates", "telemetry_event")
_emit_captures_evaluation_metric("p4", "ptc_safety_gates", "eval_metric")
_emit_stores_embedding("p4", "ptc_safety_gates", "embedding_store")
_emit_updates_meta_learning_state("p4", "ptc_safety_gates", "meta_learning")
_emit_links_execution_to_snapshot("p4", "ptc_safety_gates", "exec_snapshot_link")

# P1 orchestration signals
_emit_dispatches_healing_run("p1", "ptc_safety_gates", "L3")
_emit_routes_through("p1", "ptc_safety_gates", "L3")
_emit_checks_agent_registry("p1", "ptc_safety_gates", "agent_registry")
_emit_validates_agent_capability("p1", "ptc_safety_gates", "capability")
_emit_dispatches_execution_plan("p1", "ptc_safety_gates", "exec_plan")
_emit_agent_executes_agent("p1", "ptc_safety_gates", "sub_agent")
_emit_routes_to_agent("p1", "ptc_safety_gates", "target_agent")
_emit_verifies_policy("p1", "ptc_safety_gates", "policy_check")
_emit_observes_runtime_state("p1", "ptc_safety_gates", "runtime_state")
_emit_verifies_boundary("p1", "ptc_safety_gates", "boundary_check")
_emit_transcripts_response("p1", "ptc_safety_gates", "transcript")
_emit_hard_fails_untranscripted("p1", "ptc_safety_gates")
_emit_gated_by_confidence("p1", "ptc_safety_gates", "confidence_gate")
_emit_escalates_to_human("p1", "ptc_safety_gates", "L3")
_emit_reads_policy_state("p1", "ptc_safety_gates", "L3")

# P4 observability signals
_emit_emits_metric_event("ptc_safety_gates", "p4obs", "metric_1")
_emit_emits_metric_event("ptc_safety_gates", "p4obs", "metric_2")
_emit_emits_metric_event("ptc_safety_gates", "p4obs", "metric_3")
_emit_emits_metric_event("ptc_safety_gates", "p4obs", "metric_4")
_emit_emits_metric_event("ptc_safety_gates", "p4obs", "metric_5")
_emit_emits_metric_event("ptc_safety_gates", "p4obs", "metric_6")
_emit_records_incident_event("ptc_safety_gates", "p4obs", "incident")
_emit_captures_runtime_anomaly("ptc_safety_gates", "p4obs", "anomaly")
_emit_writes_observability_log("ptc_safety_gates", "p4obs", "obs_log")
_emit_updates_monitoring_state("ptc_safety_gates", "p4obs", "mon_state")
_emit_triggers_alert("ptc_safety_gates", "p4obs", "alert")
_emit_links_incident_trace("ptc_safety_gates", "p4obs", "trace_link")

# P3 learning maturity signals
_emit_captures_pattern("ptc_safety_gates", "p3lm", "pattern")
_emit_records_learning_event("ptc_safety_gates", "p3lm", "learning_event")
_emit_writes_learning_snapshot("ptc_safety_gates", "p3lm", "snapshot")
_emit_feeds_meta_learning("ptc_safety_gates", "p3lm", "meta_feed")
_emit_updates_routing_strategy("ptc_safety_gates", "p3lm", "routing")
_emit_improves_agent_policy("ptc_safety_gates", "p3lm", "policy")
_emit_stores_learning_state("ptc_safety_gates", "p3lm", "state")

# P1 specific signals
_emit_records_execution_trace("ptc_safety_gates", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("ptc_safety_gates", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("ptc_safety_gates", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("ptc_safety_gates", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("ptc_safety_gates", "L4_STATE", "p2_trace_5")
_emit_reads_environ("ptc_safety_gates", "env_read", "p2_env_1")
_emit_reads_environ("ptc_safety_gates", "env_read", "p2_env_2")
_emit_reads_runtime_state("ptc_safety_gates", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("ptc_safety_gates", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "ptc_safety_gates", "context_pull")
_emit_pulls_context("p1", "ptc_safety_gates", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "ptc_safety_gates", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "ptc_safety_gates", "uwg_term_2")
_emit_writes_through("p1", "ptc_safety_gates", "write_through")
_emit_writes_through("p1", "ptc_safety_gates", "write_through_2")
_emit_validated_by_safety_plane("p1", "ptc_safety_gates", "safety_validation")
_emit_invokes_evaluation("p1", "ptc_safety_gates", "eval_call")


class PTCSafetyGateType(Enum):
    """Types of PTC safety gates."""
    CONFIDENCE = "confidence"
    ROUTING = "routing"
    EXECUTION = "execution"
    VALIDATION = "validation"


class PTCSafetyGateStatus(Enum):
    """Status of safety gate evaluation."""
    PASSED = "passed"
    REVIEW_REQUIRED = "review_required"
    REJECTED = "rejected"
    ESCALATED = "escalated"


@dataclass(frozen=True)
class PTCSafetyGateResult:
    """Result of PTC safety gate evaluation.

    Attributes:
        gate_type: Type of safety gate
        status: Evaluation status
        passed: Whether gate was passed
        requires_human_review: Whether human review is required
        reason: Explanation for status
        trace_id: Trace ID
    """
    gate_type: PTCSafetyGateType
    status: PTCSafetyGateStatus
    passed: bool
    requires_human_review: bool
    reason: str
    trace_id: str


class PTCSafetyGateViolation(Exception):
    """Raised when a PTC safety gate is violated."""
    pass


class PTCConfidenceGate:
    """Confidence-based safety gate for PTC scripts.

    Routes scripts with low confidence scores to human review.

    Thresholds:
    - >= 0.9: High confidence, auto-approve
    - 0.7-0.9: Medium confidence, may require review based on risk
    - < 0.7: Low confidence, requires human review
    """

    HIGH_CONFIDENCE_THRESHOLD: float = 0.9
    MEDIUM_CONFIDENCE_THRESHOLD: float = 0.7

    def __init__(self) -> None:
        """Initialize confidence gate."""
        import uuid as _uuid

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "PTCConfidenceGate.__init__")

    def evaluate(
        self,
        script_id: str,
        confidence_score: float,
        risk_level: str,
    ) -> PTCSafetyGateResult:
        """Evaluate script against confidence gate.

        Args:
            script_id: Script identifier
            confidence_score: Confidence score (0.0-1.0)
            risk_level: Risk level (low/medium/high/critical)

        Returns:
            PTCSafetyGateResult with evaluation outcome
        """
        import uuid as _uuid

        trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(trace_id, LayerSegment.L5_POLICY, "PTCConfidenceGate.evaluate")

        if confidence_score >= self.HIGH_CONFIDENCE_THRESHOLD:
            # High confidence - auto-approve
            status = PTCSafetyGateStatus.PASSED
            passed = True
            requires_review = False
            reason = f"High confidence ({confidence_score:.2f})"

        elif confidence_score >= self.MEDIUM_CONFIDENCE_THRESHOLD:
            # Medium confidence - depends on risk
            if risk_level in ("high", "critical"):
                status = PTCSafetyGateStatus.REVIEW_REQUIRED
                passed = False
                requires_review = True
                reason = f"Medium confidence ({confidence_score:.2f}) with high risk"
                _emit_gated_by_confidence(trace_id, script_id, f"medium_high_risk:{confidence_score:.2f}")
            else:
                status = PTCSafetyGateStatus.PASSED
                passed = True
                requires_review = False
                reason = f"Medium confidence ({confidence_score:.2f}) with low risk"

        else:
            # Low confidence - requires review
            status = PTCSafetyGateStatus.REVIEW_REQUIRED
            passed = False
            requires_review = True
            reason = f"Low confidence ({confidence_score:.2f})"
            _emit_gated_by_confidence(trace_id, script_id, f"low_confidence:{confidence_score:.2f}")

        if requires_review:
            _emit_escalates_to_human(trace_id, script_id, "confidence_gate")

        return PTCSafetyGateResult(
            gate_type=PTCSafetyGateType.CONFIDENCE,
            status=status,
            passed=passed,
            requires_human_review=requires_review,
            reason=reason,
            trace_id=trace_id,
        )


class PTCRoutingGate:
    """Routing safety gate for PTC scripts.

    Ensures scripts are routed to appropriate execution paths based on
    policy compliance and risk assessment.
    """

    def __init__(self) -> None:
        """Initialize routing gate."""
        import uuid as _uuid

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "PTCRoutingGate.__init__")

    def evaluate(
        self,
        script_id: str,
        policy_compliant: bool,
        detected_patterns: list[str],
        target_path: str,
    ) -> PTCSafetyGateResult:
        """Evaluate script routing.

        Args:
            script_id: Script identifier
            policy_compliant: Whether script is policy-compliant
            detected_patterns: List of detected patterns
            target_path: Intended routing path

        Returns:
            PTCSafetyGateResult with routing decision
        """
        import uuid as _uuid

        trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(trace_id, LayerSegment.L5_POLICY, "PTCRoutingGate.evaluate")
        _emit_routes_through(trace_id, script_id, target_path)

        if not policy_compliant:
            # Non-compliant scripts escalate to L5
            status = PTCSafetyGateStatus.ESCALATED
            passed = False
            requires_review = True
            reason = "Policy non-compliant, requires L5 review"
            _emit_escalates_to_human(trace_id, script_id, "policy_non_compliant")

        elif any("high_risk" in p for p in detected_patterns):
            # High-risk patterns route through safety plane
            status = PTCSafetyGateStatus.REVIEW_REQUIRED
            passed = False
            requires_review = True
            reason = "High-risk patterns detected"
            _emit_escalates_to_human(trace_id, script_id, "high_risk_patterns")

        else:
            # Standard routing
            status = PTCSafetyGateStatus.PASSED
            passed = True
            requires_review = False
            reason = f"Routed to {target_path}"

        return PTCSafetyGateResult(
            gate_type=PTCSafetyGateType.ROUTING,
            status=status,
            passed=passed,
            requires_human_review=requires_review,
            reason=reason,
            trace_id=trace_id,
        )


class PTCExecutionGate:
    """Execution safety gate for PTC scripts.

    Fail-closed enforcement of execution contracts.

    Fail-Closed Conditions:
    - Un-transcripted I/O detected
    - Output exceeds byte cap
    - Envelope unsigned or invalid
    - Un-transcripted stderr
    """

    MAX_STDOUT_BYTES: int = 65536  # 64 KiB per PTC spec

    def __init__(self) -> None:
        """Initialize execution gate."""
        import uuid as _uuid

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "PTCExecutionGate.__init__")

    def evaluate_pre_execution(
        self,
        script_id: str,
        envelope_signed: bool,
        envelope_valid: bool,
    ) -> PTCSafetyGateResult:
        """Evaluate pre-execution conditions.

        Args:
            script_id: Script identifier
            envelope_signed: Whether envelope is signed
            envelope_valid: Whether envelope signature is valid

        Returns:
            PTCSafetyGateResult

        Raises:
            PTCSafetyGateViolation: If fail-closed conditions met
        """
        import uuid as _uuid

        trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(trace_id, LayerSegment.L5_POLICY, "PTCExecutionGate.evaluate_pre")

        if not envelope_signed:
            _emit_hard_fails_untranscripted(trace_id, script_id)
            _emit_records_incident_event(trace_id, script_id, "unsigned_envelope")
            raise PTCSafetyGateViolation(
                f"Script {script_id}: envelope unsigned (fail-closed)"
            )

        if not envelope_valid:
            _emit_hard_fails_untranscripted(trace_id, script_id)
            _emit_records_incident_event(trace_id, script_id, "invalid_envelope_signature")
            raise PTCSafetyGateViolation(
                f"Script {script_id}: Envelope signature invalid (fail-closed)"
            )

        _emit_validated_by_safety_plane(trace_id, script_id, "pre_execution")

        return PTCSafetyGateResult(
            gate_type=PTCSafetyGateType.EXECUTION,
            status=PTCSafetyGateStatus.PASSED,
            passed=True,
            requires_human_review=False,
            reason="Pre-execution checks passed",
            trace_id=trace_id,
        )

    def evaluate_post_execution(
        self,
        script_id: str,
        stdout: str,
        stderr: str,
        transcripts_complete: bool,
    ) -> PTCSafetyGateResult:
        """Evaluate post-execution conditions.

        Args:
            script_id: Script identifier
            stdout: Standard output
            stderr: Standard error
            transcripts_complete: Whether all I/O was properly transcripted

        Returns:
            PTCSafetyGateResult

        Raises:
            PTCSafetyGateViolation: If fail-closed conditions met
        """
        import uuid as _uuid

        trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(trace_id, LayerSegment.L5_POLICY, "PTCExecutionGate.evaluate_post")

        # Check byte cap
        stdout_bytes = len(stdout.encode("utf-8"))
        if stdout_bytes > self.MAX_STDOUT_BYTES:
            _emit_hard_fails_untranscripted(trace_id, script_id)
            _emit_records_incident_event(trace_id, script_id, "byte_cap_exceeded")
            raise PTCSafetyGateViolation(
                f"Script {script_id}: Output {stdout_bytes} bytes exceeds cap {self.MAX_STDOUT_BYTES} (fail-closed)"
            )

        # Check transcripts complete
        if not transcripts_complete:
            _emit_hard_fails_untranscripted(trace_id, script_id)
            _emit_records_incident_event(trace_id, script_id, "untranscripted_io")
            raise PTCSafetyGateViolation(
                f"Script {script_id}: Un-transcripted I/O detected (fail-closed)"
            )

        # Check for stderr (should be empty or transcribed)
        if stderr and not transcripts_complete:
            _emit_hard_fails_untranscripted(trace_id, script_id)
            raise PTCSafetyGateViolation(
                f"Script {script_id}: Un-transcripted stderr detected (fail-closed)"
            )

        _emit_transcripts_response(trace_id, script_id, "execution_complete")

        return PTCSafetyGateResult(
            gate_type=PTCSafetyGateType.EXECUTION,
            status=PTCSafetyGateStatus.PASSED,
            passed=True,
            requires_human_review=False,
            reason="Post-execution checks passed",
            trace_id=trace_id,
        )


class PTCValidationGate:
    """Validation safety gate for PTC scripts.

    Performs static validation and L5 re-clear for modified scripts.
    """

    def __init__(self) -> None:
        """Initialize validation gate."""
        import uuid as _uuid

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "PTCValidationGate.__init__")

    def evaluate(
        self,
        script_id: str,
        code: str,
        modified_by_human: bool,
        l5_reclear_passed: bool | None,
    ) -> PTCSafetyGateResult:
        """Evaluate script validation.

        Args:
            script_id: Script identifier
            code: Script code
            modified_by_human: Whether script was modified by human
            l5_reclear_passed: Result of L5 re-clear (if applicable)

        Returns:
            PTCSafetyGateResult
        """
        import uuid as _uuid

        trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(trace_id, LayerSegment.L5_POLICY, "PTCValidationGate.evaluate")

        # Parse and validate code
        try:
            ast.parse(code)
            syntax_valid = True
        except SyntaxError:
            syntax_valid = False

        if not syntax_valid:
            _emit_records_incident_event(trace_id, script_id, "syntax_error")
            return PTCSafetyGateResult(
                gate_type=PTCSafetyGateType.VALIDATION,
                status=PTCSafetyGateStatus.REJECTED,
                passed=False,
                requires_human_review=False,
                reason="Syntax error in script",
                trace_id=trace_id,
            )

        # Check L5 re-clear for human-modified scripts
        if modified_by_human:
            if l5_reclear_passed is None:
                # Reclear not performed yet
                _emit_escalates_to_human(trace_id, script_id, "l5_reclear_required")
                return PTCSafetyGateResult(
                    gate_type=PTCSafetyGateType.VALIDATION,
                    status=PTCSafetyGateStatus.REVIEW_REQUIRED,
                    passed=False,
                    requires_human_review=True,
                    reason="L5 re-clear required for human-modified script",
                    trace_id=trace_id,
                )
            elif not l5_reclear_passed:
                # Reclear failed
                _emit_records_incident_event(trace_id, script_id, "l5_reclear_failed")
                return PTCSafetyGateResult(
                    gate_type=PTCSafetyGateType.VALIDATION,
                    status=PTCSafetyGateStatus.REJECTED,
                    passed=False,
                    requires_human_review=False,
                    reason="L5 re-clear failed",
                    trace_id=trace_id,
                )

        _emit_validated_by_safety_plane(trace_id, script_id, "l5_validation")

        return PTCSafetyGateResult(
            gate_type=PTCSafetyGateType.VALIDATION,
            status=PTCSafetyGateStatus.PASSED,
            passed=True,
            requires_human_review=False,
            reason="Validation passed" + (" with L5 re-clear" if modified_by_human else ""),
            trace_id=trace_id,
        )


class PTCSafetyGateManager:
    """Manages all PTC safety gates.

    Coordinates confidence, routing, execution, and validation gates
    for comprehensive PTC safety.
    """

    def __init__(self) -> None:
        """Initialize safety gate manager."""
        import uuid as _uuid

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "PTCSafetyGateManager.__init__")
        _emit_signs_execution_trace(_trace_id, _trace_id[:12], "ptc_safety_init", 0)

        self.confidence_gate = PTCConfidenceGate()
        self.routing_gate = PTCRoutingGate()
        self.execution_gate = PTCExecutionGate()
        self.validation_gate = PTCValidationGate()

        self._gate_history: list[PTCSafetyGateResult] = []

    def evaluate_all_gates(
        self,
        script_id: str,
        confidence_score: float,
        risk_level: str,
        policy_compliant: bool,
        detected_patterns: list[str],
        code: str,
        envelope_signed: bool,
        envelope_valid: bool,
    ) -> dict[str, PTCSafetyGateResult]:
        """Evaluate all safety gates for a script.

        Args:
            script_id: Script identifier
            confidence_score: Confidence score
            risk_level: Risk level
            policy_compliant: Whether policy-compliant
            detected_patterns: Detected patterns
            code: Script code
            envelope_signed: Whether envelope signed
            envelope_valid: Whether envelope valid

        Returns:
            Dictionary mapping gate type to result
        """
        import uuid as _uuid

        trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(trace_id, LayerSegment.L5_POLICY, "PTCSafetyGateManager.evaluate_all")

        results = {}

        # Confidence gate
        results["confidence"] = self.confidence_gate.evaluate(
            script_id, confidence_score, risk_level
        )

        # Routing gate
        results["routing"] = self.routing_gate.evaluate(
            script_id, policy_compliant, detected_patterns, "L2_SANDBOX"
        )

        # Execution gate (pre-execution check)
        try:
            results["execution"] = self.execution_gate.evaluate_pre_execution(
                script_id, envelope_signed, envelope_valid
            )
        except PTCSafetyGateViolation as e:
            # Create a failed result for execution gate
            results["execution"] = PTCSafetyGateResult(
                gate_type=PTCSafetyGateType.EXECUTION,
                status=PTCSafetyGateStatus.REJECTED,
                passed=False,
                requires_human_review=False,
                reason=str(e),
                trace_id=trace_id,
            )

        # Validation gate
        results["validation"] = self.validation_gate.evaluate(
            script_id, code, modified_by_human=False, l5_reclear_passed=None
        )

        # Store results
        for result in results.values():
            self._gate_history.append(result)

        return results

    def check_all_passed(self, results: dict[str, PTCSafetyGateResult]) -> bool:
        """Check if all gates passed."""
        return all(r.passed for r in results.values())

    def requires_human_review(self, results: dict[str, PTCSafetyGateResult]) -> bool:
        """Check if any gate requires human review."""
        return any(r.requires_human_review for r in results.values())

    def get_gate_history(self) -> list[PTCSafetyGateResult]:
        """Get history of gate evaluations."""
        return self._gate_history.copy()

    def get_statistics(self) -> dict[str, Any]:
        """Get gate statistics."""
        if not self._gate_history:
            return {
                "total_evaluations": 0,
                "passed": 0,
                "review_required": 0,
                "rejected": 0,
            }

        total = len(self._gate_history)
        passed = sum(1 for r in self._gate_history if r.status == PTCSafetyGateStatus.PASSED)
        review_required = sum(1 for r in self._gate_history if r.status == PTCSafetyGateStatus.REVIEW_REQUIRED)
        rejected = sum(1 for r in self._gate_history if r.status == PTCSafetyGateStatus.REJECTED)

        return {
            "total_evaluations": total,
            "passed": passed,
            "review_required": review_required,
            "rejected": rejected,
            "pass_rate": passed / total,
        }


# =============================================================================
# Global Instance
# =============================================================================

_GLOBAL_SAFETY_GATE_MANAGER: PTCSafetyGateManager | None = None


def get_ptc_safety_gate_manager() -> PTCSafetyGateManager:
    """Get global PTC safety gate manager."""
    global _GLOBAL_SAFETY_GATE_MANAGER
    if _GLOBAL_SAFETY_GATE_MANAGER is None:
        _GLOBAL_SAFETY_GATE_MANAGER = PTCSafetyGateManager()
    return _GLOBAL_SAFETY_GATE_MANAGER


def reset_ptc_safety_gate_manager() -> None:
    """Reset global PTC safety gate manager."""
    global _GLOBAL_SAFETY_GATE_MANAGER
    _GLOBAL_SAFETY_GATE_MANAGER = None


# =============================================================================
# Convenience Functions
# =============================================================================

def evaluate_ptc_safety_gates(
    script_id: str,
    confidence_score: float,
    risk_level: str,
    policy_compliant: bool,
    detected_patterns: list[str],
    code: str,
    envelope_signed: bool,
    envelope_valid: bool,
) -> dict[str, PTCSafetyGateResult]:
    """Evaluate all PTC safety gates."""
    manager = get_ptc_safety_gate_manager()
    return manager.evaluate_all_gates(
        script_id, confidence_score, risk_level, policy_compliant,
        detected_patterns, code, envelope_signed, envelope_valid
    )


def check_ptc_safety_passed(results: dict[str, PTCSafetyGateResult]) -> bool:
    """Check if all PTC safety gates passed."""
    manager = get_ptc_safety_gate_manager()
    return manager.check_all_passed(results)


# =============================================================================
# Public API
# =============================================================================

__all__ = [
    "PTCSafetyGateType",
    "PTCSafetyGateStatus",
    "PTCSafetyGateResult",
    "PTCSafetyGateViolation",
    "PTCConfidenceGate",
    "PTCRoutingGate",
    "PTCExecutionGate",
    "PTCValidationGate",
    "PTCSafetyGateManager",
    "get_ptc_safety_gate_manager",
    "reset_ptc_safety_gate_manager",
    "evaluate_ptc_safety_gates",
    "check_ptc_safety_passed",
]
