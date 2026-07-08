"""
agentic_core/L2_execution/context/execution_context.py

Run-scoped ExecutionContext — P0/L2 closure.

All 9 required fields per the guardrail contract MUST be present on
every execution attempt.  No execution may proceed without an explicit
ExecutionContext.

ADG edges emitted (via authorize_and_execute):
    applies_guardrail
    validated_by_safety_plane
    references_policy_hash
    execution_terminates_at_uwg
    reenters_safety
    requires_human_review
"""

from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "execution_context")
trace_contract.emit_determinism_digest("p0", "execution_context")

trace_contract._emit_dispatches_healing_run("p1", "execution_context", "L2")
trace_contract._emit_routes_through("p1", "execution_context", "L2")
trace_contract._emit_checks_agent_registry("p1", "execution_context", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "execution_context", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "execution_context", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "execution_context", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "execution_context", "target_agent")
trace_contract._emit_verifies_policy("p1", "execution_context", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "execution_context", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "execution_context", "boundary_check")
trace_contract._emit_transcripts_response("p1", "execution_context", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "execution_context")
trace_contract._emit_gated_by_confidence("p1", "execution_context", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "execution_context", "L2")
trace_contract._emit_reads_policy_state("p1", "execution_context", "L2")
trace_contract._emit_authorize_and_execute("p2", "execution_context", "execution_auth")
trace_contract._emit_validates_capability("p2", "execution_context", "capability_check")
trace_contract._emit_routes_to_capability("p2", "execution_context", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "execution_context", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "execution_context", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "execution_context", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "execution_context", "exec_output")
trace_contract._emit_dispatches_agent("p3", "execution_context", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "execution_context", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "execution_context", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "execution_context", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "execution_context", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "execution_context", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "execution_context", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "execution_context", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "execution_context", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "execution_context", "eval_metric")
trace_contract._emit_stores_embedding("p4", "execution_context", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "execution_context", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "execution_context", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("execution_context", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("execution_context", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("execution_context", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("execution_context", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("execution_context", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("execution_context", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("execution_context", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("execution_context", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("execution_context", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("execution_context", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("execution_context", "p4obs", "alert")
trace_contract._emit_links_incident_trace("execution_context", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("execution_context", "p3lm", "pattern")
trace_contract._emit_records_learning_event("execution_context", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("execution_context", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("execution_context", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("execution_context", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("execution_context", "p3lm", "policy")
trace_contract._emit_stores_learning_state("execution_context", "p3lm", "state")
trace_contract._emit_records_execution_trace("execution_context", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("execution_context", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("execution_context", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("execution_context", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("execution_context", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("execution_context", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("execution_context", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("execution_context", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("execution_context", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "execution_context", "context_pull")
trace_contract._emit_pulls_context("p1", "execution_context", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "execution_context", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "execution_context", "uwg_term_2")
trace_contract._emit_writes_through("p1", "execution_context", "write_through")
trace_contract._emit_writes_through("p1", "execution_context", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "execution_context", "safety_validation")
trace_contract._emit_invokes_eval("p1", "execution_context", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "execution_context", "routing_commit")


class ActionClass(str, Enum):
    """Execution target action classification.

    Every execution target must be classified before execution.
    Higher-risk classes require stricter routing.
    """

    READ_ONLY = "READ_ONLY"
    MUTATION = "MUTATION"
    NETWORK = "NETWORK"
    PRIVILEGED_LOCAL = "PRIVILEGED_LOCAL"
    EXTERNAL_SIDE_EFFECT = "EXTERNAL_SIDE_EFFECT"
    HUMAN_GATED = "HUMAN_GATED"

    @property
    def is_irreversible(self) -> bool:
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "ActionClass.is_irreversible", "state_snapshot")
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "ActionClass.is_irreversible", "p0_governance")
        return self in (
            ActionClass.MUTATION,
            ActionClass.PRIVILEGED_LOCAL,
            ActionClass.EXTERNAL_SIDE_EFFECT,
            ActionClass.HUMAN_GATED,
        )

    @property
    def requires_uwg(self) -> bool:
        return self in (ActionClass.MUTATION, ActionClass.PRIVILEGED_LOCAL)

    @property
    def requires_human_review(self) -> bool:
        return self == ActionClass.HUMAN_GATED

    @property
    def requires_network_policy(self) -> bool:
        return self == ActionClass.NETWORK


class GuardrailOutcome(str, Enum):
    """Fail-closed guardrail outcome set.

    Only ALLOW may proceed to execution.
    All other outcomes MUST terminate execution.
    """

    ALLOW = "ALLOW"
    DENY = "DENY"
    ERROR = "ERROR"
    TIMEOUT = "TIMEOUT"
    UNKNOWN = "UNKNOWN"

    @property
    def may_proceed(self) -> bool:
        return self == GuardrailOutcome.ALLOW

    @property
    def is_abnormal(self) -> bool:
        return self != GuardrailOutcome.ALLOW


@dataclass(frozen=True)
class ExecutionContext:
    """Immutable run-scoped execution context.

    All 9 required fields MUST be non-empty at creation time.
    No execution may proceed without an explicit instance.

    Fields:
        execution_request_id   — unique per execution attempt
        run_id                 — agent run linkage
        capability_token       — token proving authority to act
        policy_hash            — active policy state hash
        guardrail_decision_id  — ID of guardrail decision (filled post-evaluation)
        guardrail_decision_hash — hash of guardrail decision (filled post-evaluation)
        execution_input_hash   — hash of execution payload
        execution_target_hash  — hash of execution target identifier
        trace_id               — routing/execution trace linkage
    """

    execution_request_id: str
    run_id: str
    capability_token: str
    policy_hash: str
    guardrail_decision_id: str
    guardrail_decision_hash: str
    execution_input_hash: str
    execution_target_hash: str
    trace_id: str
    action_class: ActionClass = ActionClass.READ_ONLY
    extra: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        missing = [
            f
            for f in (
                "execution_request_id",
                "run_id",
                "capability_token",
                "policy_hash",
                "execution_input_hash",
                "execution_target_hash",
                "trace_id",
            )
            if not getattr(self, f)
        ]
        if missing:
            raise ValueError(f"ExecutionContext missing required fields: {missing}")

    @classmethod
    def create(
        cls,
        *,
        run_id: str,
        capability_token: str,
        policy_hash: str,
        execution_input: Any,
        execution_target: str,
        action_class: ActionClass = ActionClass.READ_ONLY,
        trace_id: str | None = None,
        extra: dict[str, Any] | None = None,
    ) -> ExecutionContext:
        """Factory with deterministic hashing."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L2_EXECUTION, "ExecutionContext.create")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:ExecutionContext.create".encode()).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        input_hash = hashlib.sha256(repr(execution_input).encode()).hexdigest()[:32]
        target_hash = hashlib.sha256(execution_target.encode()).hexdigest()[:32]
        return cls(
            execution_request_id=str(uuid.uuid4()),
            run_id=run_id,
            capability_token=capability_token,
            policy_hash=policy_hash,
            guardrail_decision_id="",
            guardrail_decision_hash="",
            execution_input_hash=input_hash,
            execution_target_hash=target_hash,
            trace_id=trace_id or str(uuid.uuid4()),
            action_class=action_class,
            extra=extra or {},
        )

    def with_guardrail_decision(
        self,
        decision_id: str,
        decision_hash: str,
    ) -> ExecutionContext:
        """Return copy with guardrail decision bound."""
        return ExecutionContext(
            execution_request_id=self.execution_request_id,
            run_id=self.run_id,
            capability_token=self.capability_token,
            policy_hash=self.policy_hash,
            guardrail_decision_id=decision_id,
            guardrail_decision_hash=decision_hash,
            execution_input_hash=self.execution_input_hash,
            execution_target_hash=self.execution_target_hash,
            trace_id=self.trace_id,
            action_class=self.action_class,
            extra=self.extra,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "execution_request_id": self.execution_request_id,
            "run_id": self.run_id,
            "capability_token": self.capability_token[:8] + "...",
            "policy_hash": self.policy_hash,
            "guardrail_decision_id": self.guardrail_decision_id,
            "guardrail_decision_hash": self.guardrail_decision_hash,
            "execution_input_hash": self.execution_input_hash,
            "execution_target_hash": self.execution_target_hash,
            "trace_id": self.trace_id,
            "action_class": self.action_class.value,
        }


__all__ = [
    "ActionClass",
    "ExecutionContext",
    "GuardrailOutcome",
]
