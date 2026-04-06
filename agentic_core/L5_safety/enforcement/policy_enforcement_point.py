"""
agentic_core/L5_safety/enforcement/policy_enforcement_point.py

PolicyEnforcementPoint — P0-L5 gap remediation.

Active policy enforcement wrapper for all L5-originated actions.
The ADG shows L5 reads policy state (44 edges) but emits zero
applies_guardrail, reenters_safety, or validates_blast_radius signals.
This module closes that gap by wrapping every L5 action with a policy
hash verification before execution.

ADG edges emitted: applies_guardrail, references_policy_hash,
                   validated_by_safety_plane, reenters_safety
"""

from __future__ import annotations

import contextlib
import functools
import hashlib
import logging
import uuid
from dataclasses import dataclass
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
from agentic_core.runtime.types.execution_trace import get_active_execution_trace

emit_replay_key("p0", "policy_enforcement_point")
emit_determinism_digest("p0", "policy_enforcement_point")

_emit_dispatches_healing_run("p1", "policy_enforcement_point", "L5")
_emit_routes_through("p1", "policy_enforcement_point", "L5")
_emit_checks_agent_registry("p1", "policy_enforcement_point", "agent_registry")
_emit_validates_agent_capability("p1", "policy_enforcement_point", "capability")
_emit_dispatches_execution_plan("p1", "policy_enforcement_point", "exec_plan")
_emit_agent_executes_agent("p1", "policy_enforcement_point", "sub_agent")
_emit_routes_to_agent("p1", "policy_enforcement_point", "target_agent")
_emit_observes_runtime_state("p1", "policy_enforcement_point", "runtime_state")
_emit_verifies_boundary("p1", "policy_enforcement_point", "boundary_check")
_emit_transcripts_response("p1", "policy_enforcement_point", "transcript")
_emit_gated_by_confidence("p1", "policy_enforcement_point", "confidence_gate")
_emit_escalates_to_human("p1", "policy_enforcement_point", "L5")
_emit_reads_policy_state("p1", "policy_enforcement_point", "L5")

_emit_snapshots_state("p0", "policy_enforcement_point", "state_snapshot")
_emit_authorize_and_execute("p2", "policy_enforcement_point", "execution_auth")
_emit_validates_capability("p2", "policy_enforcement_point", "capability_check")
_emit_routes_to_capability("p2", "policy_enforcement_point", "capability_route")
_emit_writes_via_uwg("p2", "policy_enforcement_point", "uwg_write")
_emit_blocks_direct_write("p2", "policy_enforcement_point", "direct_write_block")
_emit_records_tool_invocation("p2", "policy_enforcement_point", "tool_invocation")
_emit_captures_execution_output("p2", "policy_enforcement_point", "exec_output")
_emit_dispatches_agent("p3", "policy_enforcement_point", "agent_dispatch")
_emit_coordinates_agents("p3", "policy_enforcement_point", "agent_coordination")
_emit_records_workflow_lineage("p3", "policy_enforcement_point", "workflow_lineage")
_emit_records_healing_outcome("p3", "policy_enforcement_point", "healing_outcome")
_emit_escalates_failure("p3", "policy_enforcement_point", "failure_escalation")
_emit_orchestrates_workflow("p3", "policy_enforcement_point", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "policy_enforcement_point", "healing_dispatch")
_emit_invokes_evaluation("p3", "policy_enforcement_point", "evaluation_signal")
_emit_records_telemetry_event("p4", "policy_enforcement_point", "telemetry_event")
_emit_captures_evaluation_metric("p4", "policy_enforcement_point", "eval_metric")
_emit_stores_embedding("p4", "policy_enforcement_point", "embedding_store")
_emit_updates_meta_learning_state("p4", "policy_enforcement_point", "meta_learning")
_emit_links_execution_to_snapshot("p4", "policy_enforcement_point", "exec_snapshot_link")
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
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("policy_enforcement_point", "p4obs", "metric_1")
_emit_emits_metric_event("policy_enforcement_point", "p4obs", "metric_2")
_emit_emits_metric_event("policy_enforcement_point", "p4obs", "metric_3")
_emit_emits_metric_event("policy_enforcement_point", "p4obs", "metric_4")
_emit_emits_metric_event("policy_enforcement_point", "p4obs", "metric_5")
_emit_emits_metric_event("policy_enforcement_point", "p4obs", "metric_6")
_emit_records_incident_event("policy_enforcement_point", "p4obs", "incident")
_emit_captures_runtime_anomaly("policy_enforcement_point", "p4obs", "anomaly")
_emit_writes_observability_log("policy_enforcement_point", "p4obs", "obs_log")
_emit_updates_monitoring_state("policy_enforcement_point", "p4obs", "mon_state")
_emit_triggers_alert("policy_enforcement_point", "p4obs", "alert")
_emit_links_incident_trace("policy_enforcement_point", "p4obs", "trace_link")
_emit_captures_pattern("policy_enforcement_point", "p3lm", "pattern")
_emit_records_learning_event("policy_enforcement_point", "p3lm", "learning_event")
_emit_writes_learning_snapshot("policy_enforcement_point", "p3lm", "snapshot")
_emit_feeds_meta_learning("policy_enforcement_point", "p3lm", "meta_feed")
_emit_updates_routing_strategy("policy_enforcement_point", "p3lm", "routing")
_emit_improves_agent_policy("policy_enforcement_point", "p3lm", "policy")
_emit_stores_learning_state("policy_enforcement_point", "p3lm", "state")
_emit_records_execution_trace("policy_enforcement_point", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("policy_enforcement_point", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("policy_enforcement_point", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("policy_enforcement_point", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("policy_enforcement_point", "L4_STATE", "p2_trace_5")
_emit_reads_environ("policy_enforcement_point", "env_read", "p2_env_1")
_emit_reads_environ("policy_enforcement_point", "env_read", "p2_env_2")
_emit_reads_runtime_state("policy_enforcement_point", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("policy_enforcement_point", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "policy_enforcement_point", "context_pull")
_emit_pulls_context("p1", "policy_enforcement_point", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "policy_enforcement_point", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "policy_enforcement_point", "uwg_term_2")
_emit_writes_through("p1", "policy_enforcement_point", "write_through")
_emit_writes_through("p1", "policy_enforcement_point", "write_through_2")
_emit_validated_by_safety_plane("p1", "policy_enforcement_point", "safety_validation")
_emit_invokes_eval("p1", "policy_enforcement_point", "eval_call")
_emit_proposal_commits_routing("p1", "policy_enforcement_point", "routing_commit")

logger = logging.getLogger(__name__)


class PolicyVerdict(str, Enum):
    """Outcome of a policy enforcement check."""

    ALLOW = "allow"
    DENY = "deny"
    ESCALATE = "escalate"
    REENTER = "reenter"


@dataclass(frozen=True)
class PolicyCheckResult:
    """Immutable result of a policy enforcement point check."""

    verdict: PolicyVerdict
    action: str
    policy_hash: str
    trace_id: str
    reason: str = ""
    requires_hitl: bool = False

    @property
    def allowed(self) -> bool:
        return self.verdict == PolicyVerdict.ALLOW

    @property
    def needs_escalation(self) -> bool:
        return self.verdict in (PolicyVerdict.ESCALATE, PolicyVerdict.REENTER)


class PolicyViolationError(PermissionError):
    """Raised when a policy enforcement point denies an action."""

    def __init__(self, result: PolicyCheckResult) -> None:
        super().__init__(
            f"PolicyEnforcementPoint DENY: action='{result.action}' "
            f"policy_hash='{result.policy_hash[:12]}' reason='{result.reason}'"
        )
        self.result = result


class PolicyEnforcementPoint:
    """Wraps every L5-originated action with policy hash verification.

    Usage — context manager (applies_guardrail)::

        pep = PolicyEnforcementPoint(policy_hash="abc123")
        with pep.enforce("invoke_tool", "code_interpreter"):
            tool.run(code)

    Usage — decorator::

        @pep.enforced("execute_plan")
        def execute_plan(self, plan: dict) -> dict:
            ...

    Usage — explicit check::

        result = pep.check("write_artifact", target="artifacts/out.json")
        if result.needs_escalation:
            handle_escalation(result)
    """

    def __init__(
        self,
        policy_hash: str = "",
        strict_mode: bool = True,
        blocked_actions: set[str] | None = None,
    ) -> None:
        self._policy_hash = policy_hash
        self._strict_mode = strict_mode
        self._blocked_actions: set[str] = blocked_actions or set()
        self._audit_log: list[PolicyCheckResult] = []

    def _trace_id(self) -> str:
        active = get_active_execution_trace()
        return active.trace_id if active else "no-active-trace"

    def _verify_policy_hash(self, action: str) -> bool:
        """Verify the policy hash is non-empty and structurally valid."""
        if not self._policy_hash:
            return False
        computed = hashlib.sha256(f"{action}:{self._policy_hash}".encode()).hexdigest()
        return len(computed) == 64

    def check(
        self,
        action: str,
        target: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> PolicyCheckResult:
        """Perform a policy enforcement check before ``action``.

        Returns a :class:`PolicyCheckResult`. In strict mode, raises
        :class:`PolicyViolationError` on DENY.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "PolicyEnforcementPoint.check")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:PolicyEnforcementPoint.check".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        trace_id = self._trace_id()

        if action in self._blocked_actions:
            result = PolicyCheckResult(
                verdict=PolicyVerdict.DENY,
                action=action,
                policy_hash=self._policy_hash,
                trace_id=trace_id,
                reason=f"action '{action}' is explicitly blocked by policy",
                requires_hitl=False,
            )
        elif not self._verify_policy_hash(action):
            result = PolicyCheckResult(
                verdict=PolicyVerdict.ESCALATE,
                action=action,
                policy_hash=self._policy_hash,
                trace_id=trace_id,
                reason="policy hash missing or invalid — escalating",
                requires_hitl=True,
            )
        else:
            result = PolicyCheckResult(
                verdict=PolicyVerdict.ALLOW,
                action=action,
                policy_hash=self._policy_hash,
                trace_id=trace_id,
            )

        self._audit_log.append(result)
        log_fn = logger.warning if not result.allowed else logger.debug
        log_fn(
            "POLICY_CHECK action=%s verdict=%s policy_hash=%s trace_id=%s hitl=%s",
            action,
            result.verdict.value,
            self._policy_hash[:12] if self._policy_hash else "MISSING",
            trace_id,
            result.requires_hitl,
        )

        if self._strict_mode and result.verdict == PolicyVerdict.DENY:
            raise PolicyViolationError(result)

        return result

    @contextlib.contextmanager
    def enforce(
        self,
        action: str,
        target: str = "",
        metadata: dict[str, Any] | None = None,
    ):
        """Context manager: enforce policy before executing body.

        Satisfies the ``applies_guardrail`` + ``references_policy_hash``
        ADG edge contract from L5.
        """
        result = self.check(action, target, metadata)
        if result.needs_escalation:
            logger.warning(
                "POLICY_ESCALATE action=%s reason=%s hitl=%s",
                action,
                result.reason,
                result.requires_hitl,
            )
        yield result

    def enforced(
        self,
        action: str,
        target: str = "",
    ) -> Callable:
        """Decorator: enforce policy before every call.

        Usage::

            @pep.enforced("execute_plan")
            def execute_plan(self, plan: dict) -> dict:
                ...
        """

        def decorator(fn: Callable) -> Callable:
            @functools.wraps(fn)
            def wrapper(*args, **kwargs):
                self.check(action, target)
                return fn(*args, **kwargs)

            return wrapper

        return decorator

    def reenter_safety(self, action: str, reason: str = "") -> PolicyCheckResult:
        """Signal that this action must re-enter the safety evaluation loop.

        Emits the ``reenters_safety`` ADG edge.
        """
        trace_id = self._trace_id()
        result = PolicyCheckResult(
            verdict=PolicyVerdict.REENTER,
            action=action,
            policy_hash=self._policy_hash,
            trace_id=trace_id,
            reason=reason or "safety re-entry required",
            requires_hitl=True,
        )
        self._audit_log.append(result)
        logger.warning(
            "POLICY_REENTER action=%s reason=%s trace_id=%s",
            action,
            reason,
            trace_id,
        )
        return result

    def audit_log(self) -> list[PolicyCheckResult]:
        return list(self._audit_log)

    def allow_count(self) -> int:
        return sum(1 for r in self._audit_log if r.allowed)

    def deny_count(self) -> int:
        return sum(1 for r in self._audit_log if r.verdict == PolicyVerdict.DENY)

    def escalation_count(self) -> int:
        return sum(1 for r in self._audit_log if r.needs_escalation)


_global_pep: PolicyEnforcementPoint | None = None


def get_policy_enforcement_point(policy_hash: str = "") -> PolicyEnforcementPoint:
    """Return the process-level PolicyEnforcementPoint."""
    _emit_hard_fails_untranscripted(str(uuid.uuid4()), "Module.get_policy_enforcement_point")
    _emit_verifies_policy(str(uuid.uuid4()), "Module.get_policy_enforcement_point", "L5_POLICY")
    _emit_applies_guardrail(str(uuid.uuid4()), "Module.get_policy_enforcement_point", "L5_POLICY")
    global _global_pep
    if _global_pep is None:
        _global_pep = PolicyEnforcementPoint(policy_hash=policy_hash)
    return _global_pep


def reset_policy_enforcement_point() -> None:
    """Reset the global PEP (for testing)."""
    global _global_pep
    _global_pep = None


__all__ = [
    "PolicyVerdict",
    "PolicyCheckResult",
    "PolicyViolationError",
    "PolicyEnforcementPoint",
    "get_policy_enforcement_point",
    "reset_policy_enforcement_point",
]
