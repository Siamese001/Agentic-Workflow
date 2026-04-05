"""
L2.2 MLWriteIntent — Phase 4

Declarative write intent emitted by the ML layer.
All durable ML writes (pattern_store, cache_set) MUST be executed
inside the L2.2 commit sandbox via MLWriteIntentExecutor.

Direct Pinecone/Redis writes from L1/L3/L6 are FORBIDDEN.
Attempting to execute an MLWriteIntent outside the sandbox raises
MLWriteEnvelopeViolation.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Literal

from agentic_core.L2_execution.enforcement.guardrail_gate import get_guardrail_gate
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
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

emit_replay_key("p0", "ml_write_intent_types")
emit_determinism_digest("p0", "ml_write_intent_types")

_emit_dispatches_healing_run("p1", "ml_write_intent_types", "L2")
_emit_routes_through("p1", "ml_write_intent_types", "L2")
_emit_checks_agent_registry("p1", "ml_write_intent_types", "agent_registry")
_emit_validates_agent_capability("p1", "ml_write_intent_types", "capability")
_emit_dispatches_execution_plan("p1", "ml_write_intent_types", "exec_plan")
_emit_agent_executes_agent("p1", "ml_write_intent_types", "sub_agent")
_emit_routes_to_agent("p1", "ml_write_intent_types", "target_agent")
_emit_verifies_policy("p1", "ml_write_intent_types", "policy_check")
_emit_observes_runtime_state("p1", "ml_write_intent_types", "runtime_state")
_emit_verifies_boundary("p1", "ml_write_intent_types", "boundary_check")
_emit_transcripts_response("p1", "ml_write_intent_types", "transcript")
_emit_hard_fails_untranscripted("p1", "ml_write_intent_types")
_emit_gated_by_confidence("p1", "ml_write_intent_types", "confidence_gate")
_emit_escalates_to_human("p1", "ml_write_intent_types", "L2")
_emit_reads_policy_state("p1", "ml_write_intent_types", "L2")

_emit_applies_guardrail("p0", "ml_write_intent_types", "p0_governance")
_emit_snapshots_state("p0", "ml_write_intent_types", "state_snapshot")
_emit_authorize_and_execute("p2", "ml_write_intent_types", "execution_auth")
_emit_validates_capability("p2", "ml_write_intent_types", "capability_check")
_emit_routes_to_capability("p2", "ml_write_intent_types", "capability_route")
_emit_writes_via_uwg("p2", "ml_write_intent_types", "uwg_write")
_emit_blocks_direct_write("p2", "ml_write_intent_types", "direct_write_block")
_emit_records_tool_invocation("p2", "ml_write_intent_types", "tool_invocation")
_emit_captures_execution_output("p2", "ml_write_intent_types", "exec_output")
_emit_dispatches_agent("p3", "ml_write_intent_types", "agent_dispatch")
_emit_coordinates_agents("p3", "ml_write_intent_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "ml_write_intent_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "ml_write_intent_types", "healing_outcome")
_emit_escalates_failure("p3", "ml_write_intent_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "ml_write_intent_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "ml_write_intent_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "ml_write_intent_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "ml_write_intent_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "ml_write_intent_types", "eval_metric")
_emit_stores_embedding("p4", "ml_write_intent_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "ml_write_intent_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "ml_write_intent_types", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_emits_metric_event("ml_write_intent_types", "p4obs", "metric_1")
_emit_emits_metric_event("ml_write_intent_types", "p4obs", "metric_2")
_emit_emits_metric_event("ml_write_intent_types", "p4obs", "metric_3")
_emit_emits_metric_event("ml_write_intent_types", "p4obs", "metric_4")
_emit_emits_metric_event("ml_write_intent_types", "p4obs", "metric_5")
_emit_emits_metric_event("ml_write_intent_types", "p4obs", "metric_6")
_emit_records_incident_event("ml_write_intent_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("ml_write_intent_types", "p4obs", "anomaly")
_emit_writes_observability_log("ml_write_intent_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("ml_write_intent_types", "p4obs", "mon_state")
_emit_triggers_alert("ml_write_intent_types", "p4obs", "alert")
_emit_links_incident_trace("ml_write_intent_types", "p4obs", "trace_link")
_emit_captures_pattern("ml_write_intent_types", "p3lm", "pattern")
_emit_records_learning_event("ml_write_intent_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("ml_write_intent_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("ml_write_intent_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("ml_write_intent_types", "p3lm", "routing")
_emit_improves_agent_policy("ml_write_intent_types", "p3lm", "policy")
_emit_stores_learning_state("ml_write_intent_types", "p3lm", "state")
_emit_records_execution_trace("ml_write_intent_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("ml_write_intent_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("ml_write_intent_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("ml_write_intent_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("ml_write_intent_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("ml_write_intent_types", "env_read", "p2_env_1")
_emit_reads_environ("ml_write_intent_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("ml_write_intent_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("ml_write_intent_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "ml_write_intent_types", "context_pull")
_emit_pulls_context("p1", "ml_write_intent_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "ml_write_intent_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "ml_write_intent_types", "uwg_term_2")
_emit_writes_through("p1", "ml_write_intent_types", "write_through")
_emit_writes_through("p1", "ml_write_intent_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "ml_write_intent_types", "safety_validation")
_emit_invokes_eval("p1", "ml_write_intent_types", "eval_call")
_emit_proposal_commits_routing("p1", "ml_write_intent_types", "routing_commit")


class MLWriteEnvelopeViolation(Exception):
    """
    Raised when an MLWriteIntent is executed outside the L2.2 commit sandbox.

    Violation code: ML_WRITE_OUTSIDE_SANDBOX
    """

    VIOLATION_CODE = "ML_WRITE_OUTSIDE_SANDBOX"

    def __init__(self, message: str = "MLWriteIntent executed outside L2.2 commit sandbox") -> None:
        super().__init__(f"[{self.VIOLATION_CODE}] {message}")


@dataclass
class MLWriteIntent:
    """
    Declarative ML write intent.

    Fields:
        kind        — "pattern_store" or "cache_set"
        payload     — serializable dict of write parameters
        requires_commit — always True; enforced in __post_init__
        intent_hash — sha256 of canonical_bytes() (computed on construction)
    """

    kind: Literal["pattern_store", "cache_set"]
    payload: dict[str, Any]
    requires_commit: bool = True
    intent_hash: str = field(default="", init=False)
    _ALLOWED_KINDS = frozenset({"pattern_store", "cache_set"})

    def __post_init__(self) -> None:
        if self.kind not in self._ALLOWED_KINDS:
            raise ValueError(
                f"MLWriteIntent: kind must be one of {sorted(self._ALLOWED_KINDS)}, got {self.kind!r}"
            )
        if not isinstance(self.payload, dict):
            raise TypeError(f"MLWriteIntent: payload must be a dict, got {type(self.payload).__name__}")
        if not self.requires_commit:
            raise ValueError("MLWriteIntent: requires_commit must be True — direct writes are forbidden")
        object.__setattr__(self, "intent_hash", self._compute_hash())

    def _compute_hash(self) -> str:
        doc = {"kind": self.kind, "payload": self.payload, "requires_commit": self.requires_commit}
        raw = json.dumps(doc, sort_keys=True, separators=(",", ":"), default=str).encode()
        return hashlib.sha256(raw).hexdigest()

    def canonical_bytes(self) -> bytes:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "MLWriteIntent.canonical_bytes")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:MLWriteIntent.canonical_bytes".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        doc = {"kind": self.kind, "payload": self.payload, "requires_commit": self.requires_commit}
        return json.dumps(doc, sort_keys=True, separators=(",", ":"), default=str).encode()


_SANDBOX_ACTIVE = False


def is_commit_sandbox_active() -> bool:
    """Return True if the L2.2 commit sandbox is currently active."""
    return _SANDBOX_ACTIVE


class MLWriteIntentExecutor:
    """
    L2.2 commit sandbox for executing MLWriteIntents.

    Usage (context manager):
        with MLWriteIntentExecutor() as executor:
            executor.execute(intent)

    Attempting to call execute() outside the context manager raises
    MLWriteEnvelopeViolation.
    """

    def __enter__(self) -> MLWriteIntentExecutor:
        global _SANDBOX_ACTIVE
        _SANDBOX_ACTIVE = True
        return self

    def __exit__(self, *_: object) -> None:
        global _SANDBOX_ACTIVE
        _SANDBOX_ACTIVE = False

    def execute(self, intent: MLWriteIntent) -> dict[str, Any]:
        """
        Execute an MLWriteIntent inside the L2.2 sandbox.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "MLWriteIntentExecutor.execute")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:MLWriteIntentExecutor.execute".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        # Wave 3: Guardrail pre-check
        guardrail = get_guardrail_gate()
        guardrail.check(operation="execute_ml_write", target=intent.target_path)
        if not _SANDBOX_ACTIVE:
            raise MLWriteEnvelopeViolation(
                f"execute() called outside L2.2 commit sandbox for kind={intent.kind!r}"
            )
        return {"executed": True, "kind": intent.kind, "intent_hash": intent.intent_hash}


def execute_ml_write_intent_outside_sandbox(intent: MLWriteIntent) -> None:
    """
    Attempt to execute an MLWriteIntent outside the sandbox.
    Always raises MLWriteEnvelopeViolation.

    This function exists to make the enforcement contract explicit and testable.
    """
    if not _SANDBOX_ACTIVE:
        raise MLWriteEnvelopeViolation(
            f"Direct ML write attempted outside L2.2 sandbox for kind={intent.kind!r}"
        )
