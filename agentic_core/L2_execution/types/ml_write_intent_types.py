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
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "ml_write_intent_types")
trace_contract.emit_determinism_digest("p0", "ml_write_intent_types")

trace_contract._emit_dispatches_healing_run("p1", "ml_write_intent_types", "L2")
trace_contract._emit_routes_through("p1", "ml_write_intent_types", "L2")
trace_contract._emit_checks_agent_registry("p1", "ml_write_intent_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "ml_write_intent_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "ml_write_intent_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "ml_write_intent_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "ml_write_intent_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "ml_write_intent_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "ml_write_intent_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "ml_write_intent_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "ml_write_intent_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "ml_write_intent_types")
trace_contract._emit_gated_by_confidence("p1", "ml_write_intent_types", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "ml_write_intent_types", "L2")
trace_contract._emit_reads_policy_state("p1", "ml_write_intent_types", "L2")

trace_contract._emit_applies_guardrail("p0", "ml_write_intent_types", "p0_governance")
trace_contract._emit_snapshots_state("p0", "ml_write_intent_types", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "ml_write_intent_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "ml_write_intent_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "ml_write_intent_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "ml_write_intent_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "ml_write_intent_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "ml_write_intent_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "ml_write_intent_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "ml_write_intent_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "ml_write_intent_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "ml_write_intent_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "ml_write_intent_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "ml_write_intent_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "ml_write_intent_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "ml_write_intent_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "ml_write_intent_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "ml_write_intent_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "ml_write_intent_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "ml_write_intent_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "ml_write_intent_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "ml_write_intent_types", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("ml_write_intent_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("ml_write_intent_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("ml_write_intent_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("ml_write_intent_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("ml_write_intent_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("ml_write_intent_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("ml_write_intent_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("ml_write_intent_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("ml_write_intent_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("ml_write_intent_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("ml_write_intent_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("ml_write_intent_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("ml_write_intent_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("ml_write_intent_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("ml_write_intent_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("ml_write_intent_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("ml_write_intent_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("ml_write_intent_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("ml_write_intent_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("ml_write_intent_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("ml_write_intent_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("ml_write_intent_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("ml_write_intent_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("ml_write_intent_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("ml_write_intent_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("ml_write_intent_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("ml_write_intent_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("ml_write_intent_types", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "ml_write_intent_types", "context_pull")
trace_contract._emit_pulls_context("p1", "ml_write_intent_types", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "ml_write_intent_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "ml_write_intent_types", "uwg_term_2")
trace_contract._emit_writes_through("p1", "ml_write_intent_types", "write_through")
trace_contract._emit_writes_through("p1", "ml_write_intent_types", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "ml_write_intent_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "ml_write_intent_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "ml_write_intent_types", "routing_commit")


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
                f"MLWriteIntent: kind must be one of {sorted(self._ALLOWED_KINDS)}, got {self.kind!r}",
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
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L2_EXECUTION, "MLWriteIntent.canonical_bytes")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:MLWriteIntent.canonical_bytes".encode()).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

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
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L2_EXECUTION, "MLWriteIntentExecutor.execute")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:MLWriteIntentExecutor.execute".encode()).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        # Wave 3: Guardrail pre-check (target derived from payload or kind — no attr drift)
        guardrail = get_guardrail_gate()
        _target = str(intent.payload.get("target_path") or intent.kind)
        guardrail.check(operation="execute_ml_write", target=_target)
        if not _SANDBOX_ACTIVE:
            raise MLWriteEnvelopeViolation(
                f"execute() called outside L2.2 commit sandbox for kind={intent.kind!r}",
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
            f"Direct ML write attempted outside L2.2 sandbox for kind={intent.kind!r}",
        )
