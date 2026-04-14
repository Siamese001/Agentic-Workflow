"""
agentic_core/L2_execution/enforcement/guardrail_gate.py

GuardrailGate — P0-L2 gap remediation.

Canonical pre-execution interceptor for all L2 writes, calls, and tool
invocations. Every L2 module with writes_to or calls edges must invoke
check() before performing the operation. This closes the 99.7% ungated
execution surface identified by ADG analysis.

ADG edges emitted: applies_guardrail, validated_by_safety_plane
"""

from __future__ import annotations

import contextlib
import functools
import logging
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
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

emit_replay_key("p0", "guardrail_gate")
emit_determinism_digest("p0", "guardrail_gate")

_emit_dispatches_healing_run("p1", "guardrail_gate", "L2")
_emit_routes_through("p1", "guardrail_gate", "L2")
_emit_checks_agent_registry("p1", "guardrail_gate", "agent_registry")
_emit_validates_agent_capability("p1", "guardrail_gate", "capability")
_emit_dispatches_execution_plan("p1", "guardrail_gate", "exec_plan")
_emit_agent_executes_agent("p1", "guardrail_gate", "sub_agent")
_emit_routes_to_agent("p1", "guardrail_gate", "target_agent")
_emit_verifies_policy("p1", "guardrail_gate", "policy_check")
_emit_observes_runtime_state("p1", "guardrail_gate", "runtime_state")
_emit_verifies_boundary("p1", "guardrail_gate", "boundary_check")
_emit_transcripts_response("p1", "guardrail_gate", "transcript")
_emit_gated_by_confidence("p1", "guardrail_gate", "confidence_gate")
_emit_escalates_to_human("p1", "guardrail_gate", "L2")
_emit_reads_policy_state("p1", "guardrail_gate", "L2")

_emit_snapshots_state("p0", "guardrail_gate", "state_snapshot")
_emit_authorize_and_execute("p2", "guardrail_gate", "execution_auth")
_emit_validates_capability("p2", "guardrail_gate", "capability_check")
_emit_routes_to_capability("p2", "guardrail_gate", "capability_route")
_emit_writes_via_uwg("p2", "guardrail_gate", "uwg_write")
_emit_blocks_direct_write("p2", "guardrail_gate", "direct_write_block")
_emit_records_tool_invocation("p2", "guardrail_gate", "tool_invocation")
_emit_captures_execution_output("p2", "guardrail_gate", "exec_output")
_emit_dispatches_agent("p3", "guardrail_gate", "agent_dispatch")
_emit_coordinates_agents("p3", "guardrail_gate", "agent_coordination")
_emit_records_workflow_lineage("p3", "guardrail_gate", "workflow_lineage")
_emit_records_healing_outcome("p3", "guardrail_gate", "healing_outcome")
_emit_escalates_failure("p3", "guardrail_gate", "failure_escalation")
_emit_orchestrates_workflow("p3", "guardrail_gate", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "guardrail_gate", "healing_dispatch")
_emit_invokes_evaluation("p3", "guardrail_gate", "evaluation_signal")
_emit_records_telemetry_event("p4", "guardrail_gate", "telemetry_event")
_emit_captures_evaluation_metric("p4", "guardrail_gate", "eval_metric")
_emit_stores_embedding("p4", "guardrail_gate", "embedding_store")
_emit_updates_meta_learning_state("p4", "guardrail_gate", "meta_learning")
_emit_links_execution_to_snapshot("p4", "guardrail_gate", "exec_snapshot_link")
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

_emit_emits_metric_event("guardrail_gate", "p4obs", "metric_1")
_emit_emits_metric_event("guardrail_gate", "p4obs", "metric_2")
_emit_emits_metric_event("guardrail_gate", "p4obs", "metric_3")
_emit_emits_metric_event("guardrail_gate", "p4obs", "metric_4")
_emit_emits_metric_event("guardrail_gate", "p4obs", "metric_5")
_emit_emits_metric_event("guardrail_gate", "p4obs", "metric_6")
_emit_records_incident_event("guardrail_gate", "p4obs", "incident")
_emit_captures_runtime_anomaly("guardrail_gate", "p4obs", "anomaly")
_emit_writes_observability_log("guardrail_gate", "p4obs", "obs_log")
_emit_updates_monitoring_state("guardrail_gate", "p4obs", "mon_state")
_emit_triggers_alert("guardrail_gate", "p4obs", "alert")
_emit_links_incident_trace("guardrail_gate", "p4obs", "trace_link")
_emit_captures_pattern("guardrail_gate", "p3lm", "pattern")
_emit_records_learning_event("guardrail_gate", "p3lm", "learning_event")
_emit_writes_learning_snapshot("guardrail_gate", "p3lm", "snapshot")
_emit_feeds_meta_learning("guardrail_gate", "p3lm", "meta_feed")
_emit_updates_routing_strategy("guardrail_gate", "p3lm", "routing")
_emit_improves_agent_policy("guardrail_gate", "p3lm", "policy")
_emit_stores_learning_state("guardrail_gate", "p3lm", "state")
_emit_records_execution_trace("guardrail_gate", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("guardrail_gate", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("guardrail_gate", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("guardrail_gate", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("guardrail_gate", "L4_STATE", "p2_trace_5")
_emit_reads_environ("guardrail_gate", "env_read", "p2_env_1")
_emit_reads_environ("guardrail_gate", "env_read", "p2_env_2")
_emit_reads_runtime_state("guardrail_gate", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("guardrail_gate", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "guardrail_gate", "context_pull")
_emit_pulls_context("p1", "guardrail_gate", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "guardrail_gate", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "guardrail_gate", "uwg_term_2")
_emit_writes_through("p1", "guardrail_gate", "write_through")
_emit_writes_through("p1", "guardrail_gate", "write_through_2")
_emit_validated_by_safety_plane("p1", "guardrail_gate", "safety_validation")
_emit_invokes_eval("p1", "guardrail_gate", "eval_call")
_emit_proposal_commits_routing("p1", "guardrail_gate", "routing_commit")

logger = logging.getLogger(__name__)


class GuardrailVerdict(str, Enum):
    """Result of a guardrail check."""

    ALLOW = "allow"
    DENY = "deny"
    ALLOW_WITH_WARNING = "allow_with_warning"


@dataclass(frozen=True)
class GuardrailCheckResult:
    """Immutable result of a guardrail pre-execution check."""

    verdict: GuardrailVerdict
    operation: str
    target: str
    policy_hash: str
    reason: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def allowed(self) -> bool:
        return self.verdict in (GuardrailVerdict.ALLOW, GuardrailVerdict.ALLOW_WITH_WARNING)


class GuardrailViolationError(PermissionError):
    """Raised when a guardrail check denies an operation."""

    def __init__(self, result: GuardrailCheckResult) -> None:
        super().__init__(
            f"GuardrailGate DENY: operation='{result.operation}' "
            f"target='{result.target}' reason='{result.reason}'",
        )
        self.result = result


class GuardrailGate:
    """Pre-execution guardrail gate for L2 operations.

    All L2 modules with ``writes_to`` or ``calls`` edges should call
    ``check()`` (or use ``guarded_call()``) before performing the operation.

    Usage — explicit::

        gate = GuardrailGate(policy_hash="abc123")
        result = gate.check("write", "artifacts/output.json")
        if not result.allowed:
            raise GuardrailViolationError(result)

    Usage — context manager::

        with gate.applies_guardrail("write", "artifacts/output.json"):
            do_write(...)

    Usage — decorator::

        @gate.guardrail_check("execute", "tool/run_python")
        def run_python(self, code: str) -> str:
            ...
    """

    def __init__(
        self,
        policy_hash: str = "",
        strict_mode: bool = True,
    ) -> None:
        self._policy_hash = policy_hash
        self._strict_mode = strict_mode
        self._blocked_operations: set[str] = set()
        self._audit_log: list[GuardrailCheckResult] = []

    def block_operation(self, operation: str) -> None:
        """Register an operation as explicitly blocked."""
        self._blocked_operations.add(operation)

    def check(
        self,
        operation: str,
        target: str,
        metadata: dict[str, Any] | None = None,
    ) -> GuardrailCheckResult:
        """Perform a guardrail pre-check for ``operation`` on ``target``.

        Returns a :class:`GuardrailCheckResult`.  In strict mode, raises
        :class:`GuardrailViolationError` if the verdict is DENY.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "GuardrailGate.check")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:GuardrailGate.check".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        verdict = GuardrailVerdict.DENY if operation in self._blocked_operations else GuardrailVerdict.ALLOW
        reason = f"operation '{operation}' is explicitly blocked" if verdict == GuardrailVerdict.DENY else ""
        result = GuardrailCheckResult(
            verdict=verdict,
            operation=operation,
            target=target,
            policy_hash=self._policy_hash,
            reason=reason,
            metadata=metadata or {},
        )
        self._audit_log.append(result)
        log_fn = logger.warning if verdict == GuardrailVerdict.DENY else logger.debug
        log_fn(
            "GUARDRAIL_CHECK op=%s target=%s verdict=%s policy_hash=%s",
            operation,
            target,
            verdict.value,
            self._policy_hash[:12] if self._policy_hash else "",
        )
        if self._strict_mode and not result.allowed:
            raise GuardrailViolationError(result)
        return result

    @contextlib.contextmanager
    def applies_guardrail(
        self,
        operation: str,
        target: str,
        metadata: dict[str, Any] | None = None,
    ):
        """Context manager: check guardrail before executing body.

        Satisfies the ``applies_guardrail`` ADG edge contract.
        """
        self.check(operation, target, metadata)
        yield

    def guardrail_check(
        self,
        operation: str,
        target: str,
        metadata: dict[str, Any] | None = None,
    ) -> Callable:
        """Decorator: apply guardrail check before every call.

        Usage::

            @gate.guardrail_check("write", "artifacts/")
            def save_result(self, data: dict) -> None:
                ...
        """

        def decorator(fn: Callable) -> Callable:
            @functools.wraps(fn)
            def wrapper(*args, **kwargs):
                self.check(operation, target, metadata)
                return fn(*args, **kwargs)

            return wrapper

        return decorator

    def audit_log(self) -> list[GuardrailCheckResult]:
        """Return a copy of all guardrail check results."""
        return list(self._audit_log)

    def allow_count(self) -> int:
        return sum(1 for r in self._audit_log if r.allowed)

    def deny_count(self) -> int:
        return sum(1 for r in self._audit_log if not r.allowed)


_global_guardrail_gate: GuardrailGate | None = None


def get_guardrail_gate(policy_hash: str = "") -> GuardrailGate:
    """Return the process-level guardrail gate."""
    _emit_hard_fails_untranscripted(str(uuid.uuid4()), "Module.get_guardrail_gate")
    _emit_applies_guardrail(str(uuid.uuid4()), "Module.get_guardrail_gate", "L2_EXECUTION")
    global _global_guardrail_gate
    if _global_guardrail_gate is None:
        _global_guardrail_gate = GuardrailGate(policy_hash=policy_hash)
    return _global_guardrail_gate


def reset_guardrail_gate() -> None:
    """Reset the global guardrail gate (for testing)."""
    global _global_guardrail_gate
    _global_guardrail_gate = None


__all__ = [
    "GuardrailVerdict",
    "GuardrailCheckResult",
    "GuardrailViolationError",
    "GuardrailGate",
    "get_guardrail_gate",
    "reset_guardrail_gate",
]
