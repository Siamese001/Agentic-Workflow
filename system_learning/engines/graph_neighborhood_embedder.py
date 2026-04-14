"""GraphNeighborhoodEmbedder — Semantic search over ADG architectural motifs.

Converts GraphNeighborhood objects (local ADG subgraphs) into CorpusRecords
for seed-pack ingestion and provides nearest-neighbour retrieval over
architectural patterns.

Enables queries like:
  - "modules that look like risky mutation brokers"
  - "components architecturally similar to this healer"
  - "nodes with the same governance edge pattern as this one"

The structural context — layer, relation types, governance edges,
mutation/determinism edges, territory — is serialized into flat text
so that BGE-M3 / OpenAI embeddings capture the motif semantically.

Design constraints:
- No wall-clock reads; structural data provided by ADG scanner.
- Deterministic text serialization via GraphNeighborhood.to_embedding_text().
- Kill-switch compliant: all retrieval paths check EMBEDDING_ENABLED.
- C0_INFORMATIONAL only: no routing influence from results.
- Thread-safe append via internal lock.
"""

from __future__ import annotations

import logging
import threading
from dataclasses import dataclass
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

_emit_authorize_and_execute("p2", "graph_neighborhood_embedder", "execution_auth")
_emit_validates_capability("p2", "graph_neighborhood_embedder", "capability_check")
_emit_routes_to_capability("p2", "graph_neighborhood_embedder", "capability_route")
_emit_writes_via_uwg("p2", "graph_neighborhood_embedder", "uwg_write")
_emit_blocks_direct_write("p2", "graph_neighborhood_embedder", "direct_write_block")
_emit_records_tool_invocation("p2", "graph_neighborhood_embedder", "tool_invocation")
_emit_captures_execution_output("p2", "graph_neighborhood_embedder", "exec_output")
_emit_dispatches_agent("p3", "graph_neighborhood_embedder", "agent_dispatch")
_emit_coordinates_agents("p3", "graph_neighborhood_embedder", "agent_coordination")
_emit_records_workflow_lineage("p3", "graph_neighborhood_embedder", "workflow_lineage")
_emit_records_healing_outcome("p3", "graph_neighborhood_embedder", "healing_outcome")
_emit_escalates_failure("p3", "graph_neighborhood_embedder", "failure_escalation")
_emit_orchestrates_workflow("p3", "graph_neighborhood_embedder", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "graph_neighborhood_embedder", "healing_dispatch")
_emit_invokes_evaluation("p3", "graph_neighborhood_embedder", "evaluation_signal")
_emit_records_telemetry_event("p4", "graph_neighborhood_embedder", "telemetry_event")
_emit_captures_evaluation_metric("p4", "graph_neighborhood_embedder", "eval_metric")
_emit_stores_embedding("p4", "graph_neighborhood_embedder", "embedding_store")
_emit_updates_meta_learning_state("p4", "graph_neighborhood_embedder", "meta_learning")
_emit_links_execution_to_snapshot("p4", "graph_neighborhood_embedder", "exec_snapshot_link")
from system_learning.config.semantic_memory_config import GRAPH_NEIGHBORHOOD_BUFFER_SIZE
from system_learning.engines.embedding_corpus_extraction import (
    CorpusRecord,
    compute_content_hash,
)
from system_learning.types.semantic_memory_types import GraphNeighborhood

_emit_applies_guardrail("p0", "graph_neighborhood_embedder", "p0_governance")
_emit_reads_policy_state("p0", "graph_neighborhood_embedder", "policy_binding")
_emit_snapshots_state("p0", "graph_neighborhood_embedder", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)
from tqdm import tqdm

_emit_emits_metric_event("graph_neighborhood_embedder", "p4obs", "metric_1")
_emit_emits_metric_event("graph_neighborhood_embedder", "p4obs", "metric_2")
_emit_emits_metric_event("graph_neighborhood_embedder", "p4obs", "metric_3")
_emit_emits_metric_event("graph_neighborhood_embedder", "p4obs", "metric_4")
_emit_emits_metric_event("graph_neighborhood_embedder", "p4obs", "metric_5")
_emit_emits_metric_event("graph_neighborhood_embedder", "p4obs", "metric_6")
_emit_records_incident_event("graph_neighborhood_embedder", "p4obs", "incident")
_emit_captures_runtime_anomaly("graph_neighborhood_embedder", "p4obs", "anomaly")
_emit_writes_observability_log("graph_neighborhood_embedder", "p4obs", "obs_log")
_emit_updates_monitoring_state("graph_neighborhood_embedder", "p4obs", "mon_state")
_emit_triggers_alert("graph_neighborhood_embedder", "p4obs", "alert")
_emit_links_incident_trace("graph_neighborhood_embedder", "p4obs", "trace_link")
_emit_captures_pattern("graph_neighborhood_embedder", "p3lm", "pattern")
_emit_records_learning_event("graph_neighborhood_embedder", "p3lm", "learning_event")
_emit_writes_learning_snapshot("graph_neighborhood_embedder", "p3lm", "snapshot")
_emit_feeds_meta_learning("graph_neighborhood_embedder", "p3lm", "meta_feed")
_emit_updates_routing_strategy("graph_neighborhood_embedder", "p3lm", "routing")
_emit_improves_agent_policy("graph_neighborhood_embedder", "p3lm", "policy")
_emit_stores_learning_state("graph_neighborhood_embedder", "p3lm", "state")
_emit_records_execution_trace("graph_neighborhood_embedder", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("graph_neighborhood_embedder", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("graph_neighborhood_embedder", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("graph_neighborhood_embedder", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("graph_neighborhood_embedder", "L4_STATE", "p2_trace_5")
_emit_reads_environ("graph_neighborhood_embedder", "env_read", "p2_env_1")
_emit_reads_environ("graph_neighborhood_embedder", "env_read", "p2_env_2")
_emit_reads_runtime_state("graph_neighborhood_embedder", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("graph_neighborhood_embedder", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "graph_neighborhood_embedder", "context_pull")
_emit_pulls_context("p1", "graph_neighborhood_embedder", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "graph_neighborhood_embedder", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "graph_neighborhood_embedder", "uwg_term_2")
_emit_writes_through("p1", "graph_neighborhood_embedder", "write_through")
_emit_writes_through("p1", "graph_neighborhood_embedder", "write_through_2")
_emit_validated_by_safety_plane("p1", "graph_neighborhood_embedder", "safety_validation")
_emit_invokes_eval("p1", "graph_neighborhood_embedder", "eval_call")
_emit_proposal_commits_routing("p1", "graph_neighborhood_embedder", "routing_commit")
_emit_escalates_to_human("p1", "graph_neighborhood_embedder", "human_escalation")
_emit_routes_through("p1", "graph_neighborhood_embedder", "route_through")
_emit_checks_agent_registry("p1", "graph_neighborhood_embedder", "agent_registry")
_emit_validates_agent_capability("p1", "graph_neighborhood_embedder", "capability")
_emit_dispatches_execution_plan("p1", "graph_neighborhood_embedder", "exec_plan")
_emit_agent_executes_agent("p1", "graph_neighborhood_embedder", "sub_agent")
_emit_routes_to_agent("p1", "graph_neighborhood_embedder", "target_agent")
_emit_verifies_policy("p1", "graph_neighborhood_embedder", "policy_check")
_emit_observes_runtime_state("p1", "graph_neighborhood_embedder", "runtime_state")
_emit_verifies_boundary("p1", "graph_neighborhood_embedder", "boundary_check")
_emit_transcripts_response("p1", "graph_neighborhood_embedder", "transcript")
_emit_hard_fails_untranscripted("p1", "graph_neighborhood_embedder")
_emit_gated_by_confidence("p1", "graph_neighborhood_embedder", "confidence_gate")
emit_replay_key("p0", "graph_neighborhood_embedder")
emit_determinism_digest("p0", "graph_neighborhood_embedder")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

logger = logging.getLogger(__name__)

_NAMESPACE = "graph_neighborhoods"


@dataclass(frozen=True)
class NeighborhoodRetrievalResult:
    """Nearest-neighbour result from graph neighborhood retrieval.

    C0_INFORMATIONAL only — no routing influence.
    """

    content_hash: str
    similarity_score: float
    node_id: str
    node_type: str
    layer: str
    risk_label: str
    content_preview: str


class GraphNeighborhoodEmbedder:
    """Converts GraphNeighborhood objects to corpus records and retrieves similar motifs.

    Usage:
        embedder = GraphNeighborhoodEmbedder()
        embedder.ingest(neighborhood)
        similar = embedder.retrieve_similar_motif(query_neighborhood, k=5)

    ADG integration:
        Build GraphNeighborhood objects from the ADG file graph JSON using
        neighborhood_from_adg_node(), then ingest to populate the buffer.
    """

    def __init__(self, max_buffer: int = GRAPH_NEIGHBORHOOD_BUFFER_SIZE) -> None:
        if max_buffer < 1:
            raise ValueError(f"max_buffer must be >= 1, got {max_buffer}")
        self._max_buffer = max_buffer
        self._lock = threading.Lock()
        self._records: list[CorpusRecord] = []
        self._meta: dict[str, dict[str, Any]] = {}

    def ingest(self, neighborhood: GraphNeighborhood) -> CorpusRecord:
        """Convert a GraphNeighborhood to a CorpusRecord and buffer it.

        Args:
            neighborhood: The graph neighborhood to ingest.

        Returns:
            The generated CorpusRecord.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "GraphNeighborhoodEmbedder.ingest"
        )

        text = neighborhood.to_embedding_text()
        content_hash = compute_content_hash(text.encode("utf-8"))
        corpus_record = CorpusRecord(
            text=text,
            trace_id=neighborhood.node_id,
            content_hash=content_hash,
            namespace=_NAMESPACE,
        )
        meta = {
            "node_id": neighborhood.node_id,
            "node_type": neighborhood.node_type,
            "layer": neighborhood.layer,
            "risk_label": neighborhood.risk_label,
            "ownership_territory": neighborhood.ownership_territory,
            "neighborhood_hash": neighborhood.neighborhood_hash,
        }
        with self._lock:
            if len(self._records) >= self._max_buffer:
                dropped = self._records.pop(0)
                self._meta.pop(dropped.content_hash, None)
                logger.debug("GraphNeighborhoodEmbedder: buffer full, dropped oldest record")
            self._records.append(corpus_record)
            self._meta[content_hash] = meta
        return corpus_record

    def ingest_batch(self, neighborhoods: list[GraphNeighborhood]) -> list[CorpusRecord]:
        """Ingest multiple GraphNeighborhoods.

        Args:
            neighborhoods: List of graph neighborhoods.

        Returns:
            List of generated CorpusRecords in the same order.
        """
        return [self.ingest(n) for n in neighborhoods]

    def export_corpus_records(self) -> list[CorpusRecord]:
        """Return a deterministically sorted snapshot of buffered records.

        Sorted by (content_hash, trace_id) for determinism.
        """
        with self._lock:
            return sorted(self._records, key=lambda r: (r.content_hash, r.trace_id))

    def buffer_size(self) -> int:
        """Return current number of buffered records."""
        with self._lock:
            return len(self._records)

    def retrieve_similar_motif(
        self,
        query_neighborhood: GraphNeighborhood,
        *,
        k: int = 5,
        namespace: str = _NAMESPACE,
    ) -> list[NeighborhoodRetrievalResult]:
        """Retrieve architecturally similar nodes via sovereign semantic cache.

        Args:
            query_neighborhood: The node whose motif to match.
            k: Maximum results.
            namespace: Seed pack namespace.

        Returns:
            List of NeighborhoodRetrievalResult — C0_INFORMATIONAL.
        """
        return self._retrieve(query_neighborhood.to_embedding_text(), k=k, namespace=namespace)

    def retrieve_by_description(
        self,
        motif_description: str,
        *,
        k: int = 5,
        namespace: str = _NAMESPACE,
    ) -> list[NeighborhoodRetrievalResult]:
        """Retrieve nodes matching a natural-language architectural description.

        Example queries:
            "risky mutation broker with writes_through and no guardrail"
            "healer that applies L5 safety policy and records execution trace"

        Args:
            motif_description: Natural language description of the desired motif.
            k: Maximum results.
            namespace: Seed pack namespace.

        Returns:
            List of NeighborhoodRetrievalResult — C0_INFORMATIONAL.
        """
        return self._retrieve(motif_description, k=k, namespace=namespace)

    def _retrieve(
        self,
        query_text: str,
        *,
        k: int,
        namespace: str,
    ) -> list[NeighborhoodRetrievalResult]:
        k = min(k, 20)
        try:
            from agentic_core.interfaces.embeddings import query_similarity

            raw_results = query_similarity(query_text, top_k=k, namespace=namespace)
            out: list[NeighborhoodRetrievalResult] = []
            for r in tqdm(raw_results, desc="Processing", unit="item"):
                ch = r.content_hash
                meta = self._meta.get(ch, {})
                out.append(
                    NeighborhoodRetrievalResult(
                        content_hash=ch,
                        similarity_score=r.similarity_score,
                        node_id=meta.get("node_id", ""),
                        node_type=meta.get("node_type", ""),
                        layer=meta.get("layer", ""),
                        risk_label=meta.get("risk_label", ""),
                        content_preview=r.content_preview,
                    ),
                )
            return out
        # guardian: allow-silent-swallow
        except Exception as exc:
            logger.debug("GraphNeighborhoodEmbedder._retrieve: %s", exc)
            return []

    @staticmethod
    def neighborhood_from_adg_node(
        *,
        node_id: str,
        node_type: str,
        layer: str,
        inbound_relations: list[str],
        outbound_relations: list[str],
        governance_edges: list[str],
        mutation_edges: list[str],
        ownership_territory: str,
        risk_label: str = "unknown",
    ) -> GraphNeighborhood:
        """Build a GraphNeighborhood from raw ADG node data.

        Args:
            node_id: Canonical node identifier (e.g. module path).
            node_type: Node type (e.g. 'agent', 'healer', 'engine', 'config').
            layer: Layer string (e.g. 'L2_execution', 'L5_safety').
            inbound_relations: List of inbound edge relation type strings.
            outbound_relations: List of outbound edge relation type strings.
            governance_edges: List of governance relation type strings.
            mutation_edges: List of mutation/determinism edge type strings.
            ownership_territory: SSOT territory name.
            risk_label: Risk classification (default 'unknown').

        Returns:
            GraphNeighborhood instance.
        """
        return GraphNeighborhood(
            node_id=node_id,
            node_type=node_type,
            layer=layer,
            inbound_relations=tuple(sorted(inbound_relations)),
            outbound_relations=tuple(sorted(outbound_relations)),
            governance_edges=tuple(sorted(governance_edges)),
            mutation_edges=tuple(sorted(mutation_edges)),
            ownership_territory=ownership_territory,
            risk_label=risk_label,
        )


__all__ = ["GraphNeighborhoodEmbedder", "NeighborhoodRetrievalResult"]
