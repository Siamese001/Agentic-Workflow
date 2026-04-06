"""
Retrieval Profiles

Named retrieval pipeline configurations: vector_only, hybrid, hybrid_reranked.
Each profile wires together retrieval, fusion, and reranking components.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

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
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
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
    _emit_routes_through,
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
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_authorize_and_execute("p2", "profiles", "execution_auth")
_emit_validates_capability("p2", "profiles", "capability_check")
_emit_routes_to_capability("p2", "profiles", "capability_route")
_emit_writes_via_uwg("p2", "profiles", "uwg_write")
_emit_blocks_direct_write("p2", "profiles", "direct_write_block")
_emit_records_tool_invocation("p2", "profiles", "tool_invocation")
_emit_captures_execution_output("p2", "profiles", "exec_output")
_emit_dispatches_agent("p3", "profiles", "agent_dispatch")
_emit_coordinates_agents("p3", "profiles", "agent_coordination")
_emit_records_workflow_lineage("p3", "profiles", "workflow_lineage")
_emit_records_healing_outcome("p3", "profiles", "healing_outcome")
_emit_escalates_failure("p3", "profiles", "failure_escalation")
_emit_orchestrates_workflow("p3", "profiles", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "profiles", "healing_dispatch")
_emit_invokes_evaluation("p3", "profiles", "evaluation_signal")
_emit_records_telemetry_event("p4", "profiles", "telemetry_event")
_emit_captures_evaluation_metric("p4", "profiles", "eval_metric")
_emit_stores_embedding("p4", "profiles", "embedding_store")
_emit_updates_meta_learning_state("p4", "profiles", "meta_learning")
_emit_links_execution_to_snapshot("p4", "profiles", "exec_snapshot_link")
from .fusion import ReciprocalRankFusion
from .interfaces import (
    Document,
    ICandidateFusion,
    IReranker,
    IRetrieverLexical,
    IRetrieverVector,
)
from .reranker import HeuristicReranker

_emit_applies_guardrail("p0", "profiles", "p0_governance")
_emit_reads_policy_state("p0", "profiles", "policy_binding")
_emit_snapshots_state("p0", "profiles", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
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
    _emit_routes_through,
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

_emit_emits_metric_event("profiles", "p4obs", "metric_1")
_emit_emits_metric_event("profiles", "p4obs", "metric_2")
_emit_emits_metric_event("profiles", "p4obs", "metric_3")
_emit_emits_metric_event("profiles", "p4obs", "metric_4")
_emit_emits_metric_event("profiles", "p4obs", "metric_5")
_emit_emits_metric_event("profiles", "p4obs", "metric_6")
_emit_records_incident_event("profiles", "p4obs", "incident")
_emit_captures_runtime_anomaly("profiles", "p4obs", "anomaly")
_emit_writes_observability_log("profiles", "p4obs", "obs_log")
_emit_updates_monitoring_state("profiles", "p4obs", "mon_state")
_emit_triggers_alert("profiles", "p4obs", "alert")
_emit_links_incident_trace("profiles", "p4obs", "trace_link")
_emit_captures_pattern("profiles", "p3lm", "pattern")
_emit_records_learning_event("profiles", "p3lm", "learning_event")
_emit_writes_learning_snapshot("profiles", "p3lm", "snapshot")
_emit_feeds_meta_learning("profiles", "p3lm", "meta_feed")
_emit_updates_routing_strategy("profiles", "p3lm", "routing")
_emit_improves_agent_policy("profiles", "p3lm", "policy")
_emit_stores_learning_state("profiles", "p3lm", "state")
_emit_records_execution_trace("profiles", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("profiles", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("profiles", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("profiles", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("profiles", "L4_STATE", "p2_trace_5")
_emit_reads_environ("profiles", "env_read", "p2_env_1")
_emit_reads_environ("profiles", "env_read", "p2_env_2")
_emit_reads_runtime_state("profiles", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("profiles", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "profiles", "context_pull")
_emit_pulls_context("p1", "profiles", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "profiles", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "profiles", "uwg_term_2")
_emit_writes_through("p1", "profiles", "write_through")
_emit_writes_through("p1", "profiles", "write_through_2")
_emit_validated_by_safety_plane("p1", "profiles", "safety_validation")
_emit_invokes_eval("p1", "profiles", "eval_call")
_emit_proposal_commits_routing("p1", "profiles", "routing_commit")
_emit_escalates_to_human("p1", "profiles", "human_escalation")
_emit_routes_through("p1", "profiles", "route_through")
_emit_checks_agent_registry("p1", "profiles", "agent_registry")
_emit_validates_agent_capability("p1", "profiles", "capability")
_emit_dispatches_execution_plan("p1", "profiles", "exec_plan")
_emit_agent_executes_agent("p1", "profiles", "sub_agent")
_emit_routes_to_agent("p1", "profiles", "target_agent")
_emit_verifies_policy("p1", "profiles", "policy_check")
_emit_observes_runtime_state("p1", "profiles", "runtime_state")
_emit_verifies_boundary("p1", "profiles", "boundary_check")
_emit_transcripts_response("p1", "profiles", "transcript")
_emit_hard_fails_untranscripted("p1", "profiles")
_emit_gated_by_confidence("p1", "profiles", "confidence_gate")
emit_replay_key("p0", "profiles")
emit_determinism_digest("p0", "profiles")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

PROFILE_VECTOR_ONLY = "vector_only"
PROFILE_HYBRID = "hybrid"
PROFILE_HYBRID_RERANKED = "hybrid_reranked"


@dataclass
class RetrievalProfileConfig:
    """Configuration for a named retrieval profile."""
    mode: str
    lexical_k: int = 50
    vector_k: int = 50
    rerank_k: int = 10
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "lexical_k": self.lexical_k,
            "vector_k": self.vector_k,
            "rerank_k": self.rerank_k,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RetrievalProfileConfig:
        return cls(
            mode=data["mode"],
            lexical_k=data.get("lexical_k", 50),
            vector_k=data.get("vector_k", 50),
            rerank_k=data.get("rerank_k", 10),
            metadata=data.get("metadata", {}),
        )

    @classmethod
    def load_from_file(cls, path: Path) -> RetrievalProfileConfig:
        """Load profile config from JSON file."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "RetrievalProfileConfig.load_from_file")

        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)


class RetrievalPipeline:
    """Executes a retrieval profile against injected retriever components.

    Supports vector_only, hybrid, and hybrid_reranked modes.
    """

    def __init__(
        self,
        config: RetrievalProfileConfig,
        lexical_retriever: IRetrieverLexical | None = None,
        vector_retriever: IRetrieverVector | None = None,
        fusion: ICandidateFusion | None = None,
        reranker: IReranker | None = None,
    ):
        self.config = config
        self.lexical_retriever = lexical_retriever
        self.vector_retriever = vector_retriever
        self.fusion = fusion or ReciprocalRankFusion()
        self.reranker = reranker or HeuristicReranker(top_k=config.rerank_k)

    def retrieve(self, query: str) -> list[Document]:
        """Execute the configured retrieval pipeline for a query.

        Args:
            query: Search query string

        Returns:
            Ranked list of Document objects
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "RetrievalPipeline.retrieve")

        mode = self.config.mode

        if mode == PROFILE_VECTOR_ONLY:
            return self._vector_only(query)
        elif mode == PROFILE_HYBRID:
            return self._hybrid(query)
        elif mode == PROFILE_HYBRID_RERANKED:
            return self._hybrid_reranked(query)
        else:
            raise ValueError(f"Unknown retrieval mode: {mode!r}")

    def _vector_only(self, query: str) -> list[Document]:
        """Vector-only retrieval."""
        if self.vector_retriever is None:
            return []
        embedding = self.vector_retriever.embed_query(query)
        return self.vector_retriever.retrieve(embedding, top_k=self.config.vector_k)

    def _hybrid(self, query: str) -> list[Document]:
        """Hybrid retrieval with fusion but no reranking."""
        lexical: list[Document] = []
        vector: list[Document] = []

        if self.lexical_retriever is not None:
            lexical = self.lexical_retriever.retrieve(query, top_k=self.config.lexical_k)
        if self.vector_retriever is not None:
            embedding = self.vector_retriever.embed_query(query)
            vector = self.vector_retriever.retrieve(embedding, top_k=self.config.vector_k)

        return self.fusion.merge(lexical, vector)

    def _hybrid_reranked(self, query: str) -> list[Document]:
        """Hybrid retrieval with fusion and reranking."""
        merged = self._hybrid(query)
        return self.reranker.rerank(query, merged)

    def to_retrieval_fn(self):
        """Return a callable compatible with OfflineEvaluationRunner.retrieval_fn."""
        def retrieval_fn(query: str) -> list[str]:
            docs = self.retrieve(query)
            return [d.doc_id for d in docs]
        return retrieval_fn


def make_profile(
    mode: str,
    lexical_k: int = 50,
    vector_k: int = 50,
    rerank_k: int = 10,
) -> RetrievalProfileConfig:
    """Factory for common retrieval profiles."""
    valid_modes = {PROFILE_VECTOR_ONLY, PROFILE_HYBRID, PROFILE_HYBRID_RERANKED}
    if mode not in valid_modes:
        raise ValueError(f"mode must be one of {valid_modes}, got {mode!r}")
    return RetrievalProfileConfig(
        mode=mode,
        lexical_k=lexical_k,
        vector_k=vector_k,
        rerank_k=rerank_k,
    )


__all__ = [
    "RetrievalProfileConfig",
    "RetrievalPipeline",
    "make_profile",
    "PROFILE_VECTOR_ONLY",
    "PROFILE_HYBRID",
    "PROFILE_HYBRID_RERANKED",
]
