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
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace


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
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "RuntimeSafetyReport.guardrail_pass_rate")

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
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "RuntimeSafetyObserver.guardrail_check")

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
