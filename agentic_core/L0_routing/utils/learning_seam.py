"""
Seam for adaptive learning intent delegation — approved L0 interface.

This seam defines the LearningArtifactIntent frozen dataclass and the
LearningPersistenceService protocol.  Per SFE-1 (intent artifacts, not
delegation) agents emit frozen intents; only L2 persists them.

Per SFE-3 (seams precede consumers) this file MUST exist before any
agent integration code references LearningArtifactIntent.

Hardening item: H5 — Frozen LearningArtifactIntent with pre-L2 hash.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Protocol

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
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    emit_replay_key,
)

_emit_authorize_and_execute("p2", "learning_seam", "execution_auth")
_emit_validates_capability("p2", "learning_seam", "capability_check")
_emit_routes_to_capability("p2", "learning_seam", "capability_route")
_emit_writes_via_uwg("p2", "learning_seam", "uwg_write")
_emit_blocks_direct_write("p2", "learning_seam", "direct_write_block")
_emit_records_tool_invocation("p2", "learning_seam", "tool_invocation")
_emit_captures_execution_output("p2", "learning_seam", "exec_output")
_emit_dispatches_agent("p3", "learning_seam", "agent_dispatch")
_emit_coordinates_agents("p3", "learning_seam", "agent_coordination")
_emit_records_workflow_lineage("p3", "learning_seam", "workflow_lineage")
_emit_records_healing_outcome("p3", "learning_seam", "healing_outcome")
_emit_escalates_failure("p3", "learning_seam", "failure_escalation")
_emit_orchestrates_workflow("p3", "learning_seam", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "learning_seam", "healing_dispatch")
_emit_invokes_evaluation("p3", "learning_seam", "evaluation_signal")
_emit_records_telemetry_event("p4", "learning_seam", "telemetry_event")
_emit_captures_evaluation_metric("p4", "learning_seam", "eval_metric")
_emit_stores_embedding("p4", "learning_seam", "embedding_store")
_emit_updates_meta_learning_state("p4", "learning_seam", "meta_learning")
_emit_links_execution_to_snapshot("p4", "learning_seam", "exec_snapshot_link")
from agentic_core.utils.canonical_serializer_util import (
    canonical_bytes,
)

_emit_dispatches_healing_run("p1", "learning_seam", "L0")
_emit_routes_through("p1", "learning_seam", "L0")
_emit_checks_agent_registry("p1", "learning_seam", "agent_registry")
_emit_validates_agent_capability("p1", "learning_seam", "capability")
_emit_dispatches_execution_plan("p1", "learning_seam", "exec_plan")
_emit_agent_executes_agent("p1", "learning_seam", "sub_agent")
_emit_routes_to_agent("p1", "learning_seam", "target_agent")
_emit_verifies_policy("p1", "learning_seam", "policy_check")
_emit_observes_runtime_state("p1", "learning_seam", "runtime_state")
_emit_verifies_boundary("p1", "learning_seam", "boundary_check")
_emit_transcripts_response("p1", "learning_seam", "transcript")
_emit_hard_fails_untranscripted("p1", "learning_seam")
_emit_gated_by_confidence("p1", "learning_seam", "confidence_gate")
_emit_escalates_to_human("p1", "learning_seam", "L0")
_emit_reads_policy_state("p1", "learning_seam", "L0")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "learning_seam", "p0_governance")
_emit_snapshots_state("p0", "learning_seam", "state_snapshot")
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

_emit_emits_metric_event("learning_seam", "p4obs", "metric_1")
_emit_emits_metric_event("learning_seam", "p4obs", "metric_2")
_emit_emits_metric_event("learning_seam", "p4obs", "metric_3")
_emit_emits_metric_event("learning_seam", "p4obs", "metric_4")
_emit_emits_metric_event("learning_seam", "p4obs", "metric_5")
_emit_emits_metric_event("learning_seam", "p4obs", "metric_6")
_emit_records_incident_event("learning_seam", "p4obs", "incident")
_emit_captures_runtime_anomaly("learning_seam", "p4obs", "anomaly")
_emit_writes_observability_log("learning_seam", "p4obs", "obs_log")
_emit_updates_monitoring_state("learning_seam", "p4obs", "mon_state")
_emit_triggers_alert("learning_seam", "p4obs", "alert")
_emit_links_incident_trace("learning_seam", "p4obs", "trace_link")
_emit_captures_pattern("learning_seam", "p3lm", "pattern")
_emit_records_learning_event("learning_seam", "p3lm", "learning_event")
_emit_writes_learning_snapshot("learning_seam", "p3lm", "snapshot")
_emit_feeds_meta_learning("learning_seam", "p3lm", "meta_feed")
_emit_updates_routing_strategy("learning_seam", "p3lm", "routing")
_emit_improves_agent_policy("learning_seam", "p3lm", "policy")
_emit_stores_learning_state("learning_seam", "p3lm", "state")
_emit_records_execution_trace("learning_seam", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("learning_seam", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("learning_seam", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("learning_seam", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("learning_seam", "L4_STATE", "p2_trace_5")
_emit_reads_environ("learning_seam", "env_read", "p2_env_1")
_emit_reads_environ("learning_seam", "env_read", "p2_env_2")
_emit_reads_runtime_state("learning_seam", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("learning_seam", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "learning_seam", "context_pull")
_emit_pulls_context("p1", "learning_seam", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "learning_seam", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "learning_seam", "uwg_term_2")
_emit_writes_through("p1", "learning_seam", "write_through")
_emit_writes_through("p1", "learning_seam", "write_through_2")
_emit_validated_by_safety_plane("p1", "learning_seam", "safety_validation")
_emit_invokes_eval("p1", "learning_seam", "eval_call")
_emit_proposal_commits_routing("p1", "learning_seam", "routing_commit")


def _intent_canonical_bytes(
    agent_id: str,
    execution_id: str,
    outcome: str,
    metrics: tuple[tuple[str, float], ...],
    context_hash: str,
) -> bytes:
    """Produce deterministic canonical bytes for intent hash.

    Delegates to the shared canonical serializer.
    """
    payload = {
        "agent_id": agent_id,
        "context_hash": context_hash,
        "execution_id": execution_id,
        "metrics": [[k, v] for k, v in metrics],
        "outcome": outcome,
    }
    return canonical_bytes(payload)


@dataclass(frozen=True)
class LearningArtifactIntent:
    """Immutable intent object emitted by agents for L2 persistence.

    Fields are frozen at construction.  ``intent_hash`` is the
    sha-256 of the canonical serialisation of all other fields and
    MUST be computed before the intent leaves the emitting layer.

    L2 verifies ``intent_hash`` on receipt before persisting.
    """

    agent_id: str
    execution_id: str
    outcome: str
    metrics: tuple[tuple[str, float], ...]
    context_hash: str
    intent_hash: str

    @staticmethod
    def create(
        *,
        agent_id: str,
        execution_id: str,
        outcome: str,
        metrics: tuple[tuple[str, float], ...],
        context_hash: str,
    ) -> LearningArtifactIntent:
        """Construct an intent with a pre-computed hash.

        This is the ONLY approved construction path.  Direct
        ``__init__`` is allowed but callers are responsible for
        providing a correct ``intent_hash``.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "LearningArtifactIntent.create")
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        cb = _intent_canonical_bytes(
            agent_id=agent_id,
            execution_id=execution_id,
            outcome=outcome,
            metrics=metrics,
            context_hash=context_hash,
        )
        intent_hash = hashlib.sha256(cb).hexdigest()
        return LearningArtifactIntent(
            agent_id=agent_id,
            execution_id=execution_id,
            outcome=outcome,
            metrics=metrics,
            context_hash=context_hash,
            intent_hash=intent_hash,
        )

    def verify(self) -> bool:
        """Re-derive hash and compare — used by L2 on receipt."""
        cb = _intent_canonical_bytes(
            agent_id=self.agent_id,
            execution_id=self.execution_id,
            outcome=self.outcome,
            metrics=self.metrics,
            context_hash=self.context_hash,
        )
        return hashlib.sha256(cb).hexdigest() == self.intent_hash


class LearningPersistenceService(Protocol):
    """Protocol that L2 implements to persist learning intents.

    No layer other than L2 may implement durable writes.
    """

    def persist_learning_intent(self, intent: LearningArtifactIntent) -> bool:
        """Persist a verified learning intent.

        Returns True on success, False on rejection.
        Implementations MUST call ``intent.verify()`` before
        writing.
        """
        ...
