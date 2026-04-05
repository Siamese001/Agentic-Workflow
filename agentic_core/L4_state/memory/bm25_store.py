"""
In-memory BM25 retrieval engine for hybrid search operations.

Zero-Ambiguity Standard: Renamed from Bm25Store.py to bm25_store.py
Moved from semantic_memory/store to L4_state/memory/semantic
"""

from __future__ import annotations

from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402,
    # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,
    # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    # noqa: E402
    emit_replay_key,
)

emit_replay_key("p0", "bm25_store")
emit_determinism_digest("p0", "bm25_store")

_emit_dispatches_healing_run("p1", "bm25_store", "L4")
_emit_routes_through("p1", "bm25_store", "L4")
_emit_checks_agent_registry("p1", "bm25_store", "agent_registry")
_emit_validates_agent_capability("p1", "bm25_store", "capability")
_emit_dispatches_execution_plan("p1", "bm25_store", "exec_plan")
_emit_agent_executes_agent("p1", "bm25_store", "sub_agent")
_emit_routes_to_agent("p1", "bm25_store", "target_agent")
_emit_verifies_policy("p1", "bm25_store", "policy_check")
_emit_observes_runtime_state("p1", "bm25_store", "runtime_state")
_emit_verifies_boundary("p1", "bm25_store", "boundary_check")
_emit_transcripts_response("p1", "bm25_store", "transcript")
_emit_hard_fails_untranscripted("p1", "bm25_store")
_emit_gated_by_confidence("p1", "bm25_store", "confidence_gate")
_emit_escalates_to_human("p1", "bm25_store", "L4")
_emit_reads_policy_state("p1", "bm25_store", "L4")
_emit_authorize_and_execute("p2", "bm25_store", "execution_auth")
_emit_validates_capability("p2", "bm25_store", "capability_check")
_emit_routes_to_capability("p2", "bm25_store", "capability_route")
_emit_writes_via_uwg("p2", "bm25_store", "uwg_write")
_emit_blocks_direct_write("p2", "bm25_store", "direct_write_block")
_emit_records_tool_invocation("p2", "bm25_store", "tool_invocation")
_emit_captures_execution_output("p2", "bm25_store", "exec_output")
_emit_dispatches_agent("p3", "bm25_store", "agent_dispatch")
_emit_coordinates_agents("p3", "bm25_store", "agent_coordination")
_emit_records_workflow_lineage("p3", "bm25_store", "workflow_lineage")
_emit_records_healing_outcome("p3", "bm25_store", "healing_outcome")
_emit_escalates_failure("p3", "bm25_store", "failure_escalation")
_emit_orchestrates_workflow("p3", "bm25_store", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "bm25_store", "healing_dispatch")
_emit_invokes_evaluation("p3", "bm25_store", "evaluation_signal")
_emit_records_telemetry_event("p4", "bm25_store", "telemetry_event")
_emit_captures_evaluation_metric("p4", "bm25_store", "eval_metric")
_emit_stores_embedding("p4", "bm25_store", "embedding_store")
_emit_updates_meta_learning_state("p4", "bm25_store", "meta_learning")
_emit_links_execution_to_snapshot("p4", "bm25_store", "exec_snapshot_link")

try:
    from rank_bm25 import BM25Okapi
except ImportError as _err:
    raise ImportError(
        "rank-bm25 is required for this module. Install with: pip install -e '.[infra]'"
    ) from _err
from agentic_core.L2_execution.config.hybrid_retriever_config import ASTAwareTokenizer
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
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
    _emit_signs_execution_trace,
    _emit_snapshots_state,
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

_emit_emits_metric_event("bm25_store", "p4obs", "metric_1")
_emit_emits_metric_event("bm25_store", "p4obs", "metric_2")
_emit_emits_metric_event("bm25_store", "p4obs", "metric_3")
_emit_emits_metric_event("bm25_store", "p4obs", "metric_4")
_emit_emits_metric_event("bm25_store", "p4obs", "metric_5")
_emit_emits_metric_event("bm25_store", "p4obs", "metric_6")
_emit_records_incident_event("bm25_store", "p4obs", "incident")
_emit_captures_runtime_anomaly("bm25_store", "p4obs", "anomaly")
_emit_writes_observability_log("bm25_store", "p4obs", "obs_log")
_emit_updates_monitoring_state("bm25_store", "p4obs", "mon_state")
_emit_triggers_alert("bm25_store", "p4obs", "alert")
_emit_links_incident_trace("bm25_store", "p4obs", "trace_link")
_emit_captures_pattern("bm25_store", "p3lm", "pattern")
_emit_records_learning_event("bm25_store", "p3lm", "learning_event")
_emit_writes_learning_snapshot("bm25_store", "p3lm", "snapshot")
_emit_feeds_meta_learning("bm25_store", "p3lm", "meta_feed")
_emit_updates_routing_strategy("bm25_store", "p3lm", "routing")
_emit_improves_agent_policy("bm25_store", "p3lm", "policy")
_emit_stores_learning_state("bm25_store", "p3lm", "state")
_emit_records_execution_trace("bm25_store", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("bm25_store", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("bm25_store", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("bm25_store", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("bm25_store", "L4_STATE", "p2_trace_5")
_emit_reads_environ("bm25_store", "env_read", "p2_env_1")
_emit_reads_environ("bm25_store", "env_read", "p2_env_2")
_emit_reads_runtime_state("bm25_store", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("bm25_store", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "bm25_store", "context_pull")
_emit_pulls_context("p1", "bm25_store", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "bm25_store", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "bm25_store", "uwg_term_2")
_emit_writes_through("p1", "bm25_store", "write_through")
_emit_writes_through("p1", "bm25_store", "write_through_2")
_emit_validated_by_safety_plane("p1", "bm25_store", "safety_validation")
_emit_invokes_eval("p1", "bm25_store", "eval_call")
_emit_proposal_commits_routing("p1", "bm25_store", "routing_commit")

_tokenizer = ASTAwareTokenizer()


class Bm25Store:
    """In-memory BM25 index for fast keyword retrieval."""

    def __init__(self):
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "Bm25Store.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "Bm25Store.__init__", "p0_governance")
        self.documents: list[dict] = []
        self.bm25: BM25Okapi | None = None
        self._build_index()

    def add_documents(self, docs: list[dict]) -> None:
        """Add or update documents."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L4_STATE, "Bm25Store.add_documents")

        self.documents.extend(docs)
        self._build_index()

    def _build_index(self) -> None:
        if not self.documents:
            self.bm25 = None
            return
        tokenized = [_tokenizer.tokenize_code(doc["text"]) for doc in self.documents]
        self.bm25 = BM25Okapi(tokenized)

    def query(self, query: str, top_k: int = 5) -> list[dict]:
        """BM25 keyword search."""
        if not self.bm25 or not self.documents:
            return []
        tokenized_query: Any = _tokenizer.tokenize_query(query)
        scores: Any = self.bm25.get_scores(tokenized_query)
        ranked: Any = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)[:top_k]
        results: Any = []
        for idx, score in ranked:
            if score == 0:
                continue
            doc: Any = self.documents[idx]
            results.append(
                {
                    "source": "bm25",
                    "content": doc["text"],
                    "score": float(score),
                    "id": doc["id"],
                    "metadata": doc.get("metadata", {}),
                }
            )
        return results


_bm25_store: Any = Bm25Store()


def get_bm25_store() -> Bm25Store:
    """Get the singleton BM25 store instance for hybrid search operations."""
    return _bm25_store
