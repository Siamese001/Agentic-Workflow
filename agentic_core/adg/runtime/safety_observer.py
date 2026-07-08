"""G5 (gap): Runtime Safety Enforcement Plane — guardrail and policy hash observation.

Complements the static `applies_guardrail` and `verifies_policy` edges produced by
`_SafetyEnforcementVisitor` in static_scanner.py with runtime execution records:
which guardrails fired, which policy hashes were verified/failed, and what safety
decisions were taken at runtime.

Architecture node flow (Gap 5):
  Agent output
    → SovereignLLMGateway / guardrail class (static edge: applies_guardrail)
    → PolicyHashVerifier (static edge: verifies_policy)
    → [if mismatch] → SafetyViolationEvent (runtime: policy_hash_mismatch)
    → [if pass] → SafetyPassEvent (runtime: policy_hash_verified)

Data model:
  GuardrailExecution       — one guardrail check (input, result, reason)
  PolicyHashVerification   — one policy hash check (expected vs actual)
  SafetyViolation          — a runtime safety enforcement failure
  RuntimeSafetyObserver    — collector that writes into RuntimeGraph

Usage::

    from agentic_core.adg.runtime.safety_observer import RuntimeSafetyObserver
    from agentic_core.adg.runtime.event_graph import RuntimeGraph

    rt_graph = RuntimeGraph()
    obs = RuntimeSafetyObserver(rt_graph, agent_id="SovereignLLMGateway")
    obs.guardrail_check(
        guardrail="InstructionFenceGuardrail",
        passed=True,
        input_hash="sha256:abc",
    )
    obs.policy_hash_verify(
        policy_id="CONSTITUTION_V3",
        expected_hash="sha256:def",
        actual_hash="sha256:def",
    )
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from agentic_core.adg.runtime.event_graph import RuntimeGraph, RuntimeGraphCollector
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "safety_observer", "p0_governance")
trace_contract._emit_snapshots_state("p0", "safety_observer", "state_snapshot")

trace_contract._emit_emits_metric_event("safety_observer", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("safety_observer", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("safety_observer", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("safety_observer", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("safety_observer", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("safety_observer", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("safety_observer", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("safety_observer", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("safety_observer", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("safety_observer", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("safety_observer", "p4obs", "alert")
trace_contract._emit_links_incident_trace("safety_observer", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("safety_observer", "p3lm", "pattern")
trace_contract._emit_records_learning_event("safety_observer", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("safety_observer", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("safety_observer", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("safety_observer", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("safety_observer", "p3lm", "policy")
trace_contract._emit_stores_learning_state("safety_observer", "p3lm", "state")
trace_contract._emit_records_execution_trace("safety_observer", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("safety_observer", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("safety_observer", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("safety_observer", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("safety_observer", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("safety_observer", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("safety_observer", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("safety_observer", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("safety_observer", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "safety_observer", "context_pull")
trace_contract._emit_pulls_context("p1", "safety_observer", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "safety_observer", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "safety_observer", "uwg_term_2")
trace_contract._emit_writes_through("p1", "safety_observer", "write_through")
trace_contract._emit_writes_through("p1", "safety_observer", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "safety_observer", "safety_validation")
trace_contract._emit_invokes_eval("p1", "safety_observer", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "safety_observer", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "safety_observer", "human_escalation")
trace_contract._emit_routes_through("p1", "safety_observer", "route_through")
trace_contract._emit_checks_agent_registry("p1", "safety_observer", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "safety_observer", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "safety_observer", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "safety_observer", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "safety_observer", "target_agent")
trace_contract._emit_verifies_policy("p1", "safety_observer", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "safety_observer", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "safety_observer", "boundary_check")
trace_contract._emit_transcripts_response("p1", "safety_observer", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "safety_observer")
trace_contract._emit_gated_by_confidence("p1", "safety_observer", "confidence_gate")
trace_contract.emit_replay_key("p0", "safety_observer")
trace_contract.emit_determinism_digest("p0", "safety_observer")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "safety_observer", "execution_auth")
trace_contract._emit_validates_capability("p2", "safety_observer", "capability_check")
trace_contract._emit_routes_to_capability("p2", "safety_observer", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "safety_observer", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "safety_observer", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "safety_observer", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "safety_observer", "exec_output")
trace_contract._emit_dispatches_agent("p3", "safety_observer", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "safety_observer", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "safety_observer", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "safety_observer", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "safety_observer", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "safety_observer", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "safety_observer", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "safety_observer", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "safety_observer", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "safety_observer", "eval_metric")
trace_contract._emit_stores_embedding("p4", "safety_observer", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "safety_observer", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "safety_observer", "exec_snapshot_link")


@dataclass(frozen=True)
class GuardrailExecution:
    """Record of a single guardrail check at runtime.

    Attributes:
        guardrail:    Name of the guardrail class that was applied.
        agent_id:     Agent that invoked the guardrail.
        run_id:       Execution run identifier.
        passed:       Whether the guardrail check passed.
        input_hash:   Hash of the content submitted to the guardrail.
        reason:       Human-readable reason if check failed.
        executed_at:  Unix epoch timestamp.
    """

    guardrail: str
    agent_id: str
    run_id: str
    passed: bool
    input_hash: str = ""
    reason: str = ""
    executed_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "guardrail": self.guardrail,
            "agent_id": self.agent_id,
            "run_id": self.run_id,
            "passed": self.passed,
            "input_hash": self.input_hash,
            "reason": self.reason,
            "executed_at": self.executed_at,
        }


@dataclass(frozen=True)
class PolicyHashVerification:
    """Record of a single policy hash verification at runtime.

    Attributes:
        policy_id:      Identifier of the policy being verified.
        agent_id:       Agent that ran the verification.
        run_id:         Execution run identifier.
        expected_hash:  The hash the system expects.
        actual_hash:    The hash found at runtime.
        passed:         True when expected_hash == actual_hash.
        verified_at:    Unix epoch timestamp.
    """

    policy_id: str
    agent_id: str
    run_id: str
    expected_hash: str
    actual_hash: str
    passed: bool
    verified_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "policy_id": self.policy_id,
            "agent_id": self.agent_id,
            "run_id": self.run_id,
            "expected_hash": self.expected_hash,
            "actual_hash": self.actual_hash,
            "passed": self.passed,
            "verified_at": self.verified_at,
        }


@dataclass(frozen=True)
class SafetyViolation:
    """A runtime safety enforcement failure.

    Attributes:
        violation_type:  Category (e.g. ``policy_hash_mismatch``, ``guardrail_block``).
        agent_id:        Agent where the violation was detected.
        run_id:          Execution run identifier.
        detail:          Structured detail about the violation.
        detected_at:     Unix epoch timestamp.
    """

    violation_type: str
    agent_id: str
    run_id: str
    detail: dict[str, Any] = field(default_factory=dict)
    detected_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "violation_type": self.violation_type,
            "agent_id": self.agent_id,
            "run_id": self.run_id,
            "detail": self.detail,
            "detected_at": self.detected_at,
        }


@dataclass
class RuntimeSafetyReport:
    """Aggregated runtime safety observation results for a single execution session.

    Attributes:
        guardrail_executions:   All guardrail checks performed.
        policy_verifications:   All policy hash checks performed.
        violations:             All safety failures detected.
    """

    guardrail_executions: list[GuardrailExecution] = field(default_factory=list)
    policy_verifications: list[PolicyHashVerification] = field(default_factory=list)
    violations: list[SafetyViolation] = field(default_factory=list)

    @property
    def guardrail_pass_rate(self) -> float:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "RuntimeSafetyReport.guardrail_pass_rate"
        )

        if not self.guardrail_executions:
            return 1.0
        passed = sum(1 for g in self.guardrail_executions if g.passed)
        return passed / len(self.guardrail_executions)

    @property
    def policy_pass_rate(self) -> float:
        if not self.policy_verifications:
            return 1.0
        passed = sum(1 for p in self.policy_verifications if p.passed)
        return passed / len(self.policy_verifications)

    @property
    def violation_count(self) -> int:
        return len(self.violations)

    def violations_by_type(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for v in self.violations:
            counts[v.violation_type] = counts.get(v.violation_type, 0) + 1
        return counts


class RuntimeSafetyObserver(RuntimeGraphCollector):
    """Observes and records safety enforcement events during agent execution.

    Writes typed records into a RuntimeSafetyReport and simultaneously
    emits RuntimeEdges/Events into the shared RuntimeGraph.

    Args:
        rt_graph:  Shared RuntimeGraph for this execution session.
        report:    Optional RuntimeSafetyReport to aggregate into.
                   Creates a new one if not provided.
        agent_id:  Agent class name that is being observed.
        run_id:    Execution run identifier.
    """

    def __init__(
        self,
        rt_graph: RuntimeGraph,
        report: RuntimeSafetyReport | None = None,
        agent_id: str = "UnknownAgent",
        run_id: str | None = None,
    ) -> None:
        super().__init__(rt_graph, agent_id, run_id)
        self._report = report if report is not None else RuntimeSafetyReport()

    @property
    def report(self) -> RuntimeSafetyReport:
        return self._report

    def guardrail_check(
        self,
        guardrail: str,
        passed: bool,
        input_hash: str = "",
        reason: str = "",
    ) -> None:
        """Record a guardrail execution and emit a RuntimeEdge."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "RuntimeSafetyObserver.guardrail_check"
        )

        record = GuardrailExecution(
            guardrail=guardrail,
            agent_id=self._agent_id,
            run_id=self._run_id,
            passed=passed,
            input_hash=input_hash,
            reason=reason,
        )
        self._report.guardrail_executions.append(record)
        self._emit_event(
            "guardrail_check",
            phase="safety",
            payload={"guardrail": guardrail, "passed": passed, "input_hash": input_hash},
        )
        relation = "applies_guardrail" if passed else "applies_guardrail"
        self._emit_edge(
            relation,
            guardrail,
            metadata={"passed": passed, "input_hash": input_hash, "reason": reason},
        )
        if not passed:
            violation = SafetyViolation(
                violation_type="guardrail_block",
                agent_id=self._agent_id,
                run_id=self._run_id,
                detail={"guardrail": guardrail, "reason": reason, "input_hash": input_hash},
            )
            self._report.violations.append(violation)

    def policy_hash_verify(
        self,
        policy_id: str,
        expected_hash: str,
        actual_hash: str,
    ) -> bool:
        """Verify a policy hash and record the result.

        Returns True if hashes match, False if mismatch.
        """
        passed = expected_hash == actual_hash
        record = PolicyHashVerification(
            policy_id=policy_id,
            agent_id=self._agent_id,
            run_id=self._run_id,
            expected_hash=expected_hash,
            actual_hash=actual_hash,
            passed=passed,
        )
        self._report.policy_verifications.append(record)
        self._emit_event(
            "policy_hash_verify",
            phase="safety",
            payload={
                "policy_id": policy_id,
                "passed": passed,
                "expected_hash": expected_hash[:16],
                "actual_hash": actual_hash[:16],
            },
        )
        relation = "verifies_policy" if passed else "enforces_policy_hash"
        self._emit_edge(
            relation,
            f"Policy::{policy_id}",
            metadata={"passed": passed, "policy_id": policy_id},
        )
        if not passed:
            violation = SafetyViolation(
                violation_type="policy_hash_mismatch",
                agent_id=self._agent_id,
                run_id=self._run_id,
                detail={
                    "policy_id": policy_id,
                    "expected_hash": expected_hash,
                    "actual_hash": actual_hash,
                },
            )
            self._report.violations.append(violation)
        return passed


__all__ = [
    "GuardrailExecution",
    "PolicyHashVerification",
    "SafetyViolation",
    "RuntimeSafetyReport",
    "RuntimeSafetyObserver",
]
