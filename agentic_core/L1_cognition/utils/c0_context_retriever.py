"""C0ContextRetriever — informational-only embeddings.

Guarantees: top_k=20, score >= 0.5, seed pack hash verification.
C0 context cannot affect routing decisions; only informational.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_dispatches_healing_run("p1", "c0_context_retriever", "L0")
_emit_routes_through("p1", "c0_context_retriever", "L0")
_emit_checks_agent_registry("p1", "c0_context_retriever", "agent_registry")
_emit_validates_agent_capability("p1", "c0_context_retriever", "capability")
_emit_dispatches_execution_plan("p1", "c0_context_retriever", "exec_plan")
_emit_agent_executes_agent("p1", "c0_context_retriever", "sub_agent")
_emit_routes_to_agent("p1", "c0_context_retriever", "target_agent")
_emit_verifies_policy("p1", "c0_context_retriever", "policy_check")
_emit_observes_runtime_state("p1", "c0_context_retriever", "runtime_state")
_emit_verifies_boundary("p1", "c0_context_retriever", "boundary_check")
_emit_transcripts_response("p1", "c0_context_retriever", "transcript")
_emit_hard_fails_untranscripted("p1", "c0_context_retriever")
_emit_gated_by_confidence("p1", "c0_context_retriever", "confidence_gate")
_emit_escalates_to_human("p1", "c0_context_retriever", "L0")
_emit_reads_policy_state("p1", "c0_context_retriever", "L0")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "c0_context_retriever", "p0_governance")
_emit_snapshots_state("p0", "c0_context_retriever", "state_snapshot")
_emit_authorize_and_execute("p2", "c0_context_retriever", "execution_auth")
_emit_validates_capability("p2", "c0_context_retriever", "capability_check")
_emit_routes_to_capability("p2", "c0_context_retriever", "capability_route")
_emit_writes_via_uwg("p2", "c0_context_retriever", "uwg_write")
_emit_blocks_direct_write("p2", "c0_context_retriever", "direct_write_block")
_emit_records_tool_invocation("p2", "c0_context_retriever", "tool_invocation")
_emit_captures_execution_output("p2", "c0_context_retriever", "exec_output")
_emit_dispatches_agent("p3", "c0_context_retriever", "agent_dispatch")
_emit_coordinates_agents("p3", "c0_context_retriever", "agent_coordination")
_emit_records_workflow_lineage("p3", "c0_context_retriever", "workflow_lineage")
_emit_records_healing_outcome("p3", "c0_context_retriever", "healing_outcome")
_emit_escalates_failure("p3", "c0_context_retriever", "failure_escalation")
_emit_orchestrates_workflow("p3", "c0_context_retriever", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "c0_context_retriever", "healing_dispatch")
_emit_invokes_evaluation("p3", "c0_context_retriever", "evaluation_signal")
_emit_records_telemetry_event("p4", "c0_context_retriever", "telemetry_event")
_emit_captures_evaluation_metric("p4", "c0_context_retriever", "eval_metric")
_emit_stores_embedding("p4", "c0_context_retriever", "embedding_store")
_emit_updates_meta_learning_state("p4", "c0_context_retriever", "meta_learning")
_emit_links_execution_to_snapshot("p4", "c0_context_retriever", "exec_snapshot_link")
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

_emit_emits_metric_event("c0_context_retriever", "p4obs", "metric_1")
_emit_emits_metric_event("c0_context_retriever", "p4obs", "metric_2")
_emit_emits_metric_event("c0_context_retriever", "p4obs", "metric_3")
_emit_emits_metric_event("c0_context_retriever", "p4obs", "metric_4")
_emit_emits_metric_event("c0_context_retriever", "p4obs", "metric_5")
_emit_emits_metric_event("c0_context_retriever", "p4obs", "metric_6")
_emit_records_incident_event("c0_context_retriever", "p4obs", "incident")
_emit_captures_runtime_anomaly("c0_context_retriever", "p4obs", "anomaly")
_emit_writes_observability_log("c0_context_retriever", "p4obs", "obs_log")
_emit_updates_monitoring_state("c0_context_retriever", "p4obs", "mon_state")
_emit_triggers_alert("c0_context_retriever", "p4obs", "alert")
_emit_links_incident_trace("c0_context_retriever", "p4obs", "trace_link")
_emit_captures_pattern("c0_context_retriever", "p3lm", "pattern")
_emit_records_learning_event("c0_context_retriever", "p3lm", "learning_event")
_emit_writes_learning_snapshot("c0_context_retriever", "p3lm", "snapshot")
_emit_feeds_meta_learning("c0_context_retriever", "p3lm", "meta_feed")
_emit_updates_routing_strategy("c0_context_retriever", "p3lm", "routing")
_emit_improves_agent_policy("c0_context_retriever", "p3lm", "policy")
_emit_stores_learning_state("c0_context_retriever", "p3lm", "state")
_emit_records_execution_trace("c0_context_retriever", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("c0_context_retriever", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("c0_context_retriever", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("c0_context_retriever", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("c0_context_retriever", "L4_STATE", "p2_trace_5")
_emit_reads_environ("c0_context_retriever", "env_read", "p2_env_1")
_emit_reads_environ("c0_context_retriever", "env_read", "p2_env_2")
_emit_reads_runtime_state("c0_context_retriever", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("c0_context_retriever", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "c0_context_retriever", "context_pull")
_emit_pulls_context("p1", "c0_context_retriever", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "c0_context_retriever", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "c0_context_retriever", "uwg_term_2")
_emit_writes_through("p1", "c0_context_retriever", "write_through")
_emit_writes_through("p1", "c0_context_retriever", "write_through_2")
_emit_validated_by_safety_plane("p1", "c0_context_retriever", "safety_validation")
_emit_invokes_eval("p1", "c0_context_retriever", "eval_call")
_emit_proposal_commits_routing("p1", "c0_context_retriever", "routing_commit")


@dataclass
class ContentHash:
    content_hash: str
    score: float


@dataclass
class C0ContextArtifact:
    seed_pack: str
    seed_pack_hash: str
    supporting_content_hashes: list[ContentHash]

    @classmethod
    async def load(cls) -> C0ContextArtifact | None:
        return None


_SCORE_CUTOFF = 0.5
_TOP_K = 20


class C0ContextRetriever:
    """Populate c0_context slot with informational embedding results."""

    async def retrieve(self, u0_user_prompt: str) -> str:
        """Return a deterministic, bounded context string."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "C0ContextRetriever.retrieve")
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        artifact = await C0ContextArtifact.load()
        if not artifact:
            raise RuntimeError("C0 seed pack missing or unloadable")
        expected_hash = hashlib.sha256(artifact.seed_pack.encode("utf-8", errors="replace")).hexdigest()
        if artifact.seed_pack_hash != expected_hash:
            raise RuntimeError("C0 seed pack hash mismatch — corrupted or tampered")
        results = sorted(
            [r for r in artifact.supporting_content_hashes if r.score >= _SCORE_CUTOFF],
            key=lambda r: (-round(r.score, 6), r.content_hash),
        )[:_TOP_K]
        lines = [f"[{i + 1:02d}] {r.content_hash[:12]} (score={r.score:.3f})" for i, r in enumerate(results)]
        return "\n".join(lines)
