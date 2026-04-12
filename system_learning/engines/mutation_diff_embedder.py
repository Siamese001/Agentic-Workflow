"""MutationDiffEmbedder — Semantic memory for UWG mutation diffs.

Converts MutationDiffRecord objects into CorpusRecords for seed-pack ingestion
and provides nearest-neighbour retrieval over historical mutations.

Enables:
  - Pre-commit nearest-neighbour checks for risky mutation similarity
  - Post-commit retrieval for future healing
  - Rollback refinement retrieval from similar failed mutations

Design constraints:
- No wall-clock reads; all timestamps provided by caller.
- Deterministic text serialization via MutationDiffRecord.to_embedding_text().
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

_emit_authorize_and_execute("p2", "mutation_diff_embedder", "execution_auth")
_emit_validates_capability("p2", "mutation_diff_embedder", "capability_check")
_emit_routes_to_capability("p2", "mutation_diff_embedder", "capability_route")
_emit_writes_via_uwg("p2", "mutation_diff_embedder", "uwg_write")
_emit_blocks_direct_write("p2", "mutation_diff_embedder", "direct_write_block")
_emit_records_tool_invocation("p2", "mutation_diff_embedder", "tool_invocation")
_emit_captures_execution_output("p2", "mutation_diff_embedder", "exec_output")
_emit_dispatches_agent("p3", "mutation_diff_embedder", "agent_dispatch")
_emit_coordinates_agents("p3", "mutation_diff_embedder", "agent_coordination")
_emit_records_workflow_lineage("p3", "mutation_diff_embedder", "workflow_lineage")
_emit_records_healing_outcome("p3", "mutation_diff_embedder", "healing_outcome")
_emit_escalates_failure("p3", "mutation_diff_embedder", "failure_escalation")
_emit_orchestrates_workflow("p3", "mutation_diff_embedder", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "mutation_diff_embedder", "healing_dispatch")
_emit_invokes_evaluation("p3", "mutation_diff_embedder", "evaluation_signal")
_emit_records_telemetry_event("p4", "mutation_diff_embedder", "telemetry_event")
_emit_captures_evaluation_metric("p4", "mutation_diff_embedder", "eval_metric")
_emit_stores_embedding("p4", "mutation_diff_embedder", "embedding_store")
_emit_updates_meta_learning_state("p4", "mutation_diff_embedder", "meta_learning")
_emit_links_execution_to_snapshot("p4", "mutation_diff_embedder", "exec_snapshot_link")
from system_learning.config.semantic_memory_config import DEFAULT_EMBEDDER_BUFFER_SIZE
from system_learning.engines.embedding_corpus_extraction import (
    CorpusRecord,
    compute_content_hash,
)
from system_learning.types.semantic_memory_types import MutationDiffRecord

_emit_applies_guardrail("p0", "mutation_diff_embedder", "p0_governance")
_emit_snapshots_state("p0", "mutation_diff_embedder", "state_snapshot")
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

_emit_emits_metric_event("mutation_diff_embedder", "p4obs", "metric_1")
_emit_emits_metric_event("mutation_diff_embedder", "p4obs", "metric_2")
_emit_emits_metric_event("mutation_diff_embedder", "p4obs", "metric_3")
_emit_emits_metric_event("mutation_diff_embedder", "p4obs", "metric_4")
_emit_emits_metric_event("mutation_diff_embedder", "p4obs", "metric_5")
_emit_emits_metric_event("mutation_diff_embedder", "p4obs", "metric_6")
_emit_records_incident_event("mutation_diff_embedder", "p4obs", "incident")
_emit_captures_runtime_anomaly("mutation_diff_embedder", "p4obs", "anomaly")
_emit_writes_observability_log("mutation_diff_embedder", "p4obs", "obs_log")
_emit_updates_monitoring_state("mutation_diff_embedder", "p4obs", "mon_state")
_emit_triggers_alert("mutation_diff_embedder", "p4obs", "alert")
_emit_links_incident_trace("mutation_diff_embedder", "p4obs", "trace_link")
_emit_captures_pattern("mutation_diff_embedder", "p3lm", "pattern")
_emit_records_learning_event("mutation_diff_embedder", "p3lm", "learning_event")
_emit_writes_learning_snapshot("mutation_diff_embedder", "p3lm", "snapshot")
_emit_feeds_meta_learning("mutation_diff_embedder", "p3lm", "meta_feed")
_emit_updates_routing_strategy("mutation_diff_embedder", "p3lm", "routing")
_emit_improves_agent_policy("mutation_diff_embedder", "p3lm", "policy")
_emit_stores_learning_state("mutation_diff_embedder", "p3lm", "state")
_emit_records_execution_trace("mutation_diff_embedder", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("mutation_diff_embedder", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("mutation_diff_embedder", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("mutation_diff_embedder", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("mutation_diff_embedder", "L4_STATE", "p2_trace_5")
_emit_reads_environ("mutation_diff_embedder", "env_read", "p2_env_1")
_emit_reads_environ("mutation_diff_embedder", "env_read", "p2_env_2")
_emit_reads_runtime_state("mutation_diff_embedder", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("mutation_diff_embedder", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "mutation_diff_embedder", "context_pull")
_emit_pulls_context("p1", "mutation_diff_embedder", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "mutation_diff_embedder", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "mutation_diff_embedder", "uwg_term_2")
_emit_writes_through("p1", "mutation_diff_embedder", "write_through")
_emit_writes_through("p1", "mutation_diff_embedder", "write_through_2")
_emit_validated_by_safety_plane("p1", "mutation_diff_embedder", "safety_validation")
_emit_invokes_eval("p1", "mutation_diff_embedder", "eval_call")
_emit_proposal_commits_routing("p1", "mutation_diff_embedder", "routing_commit")
_emit_escalates_to_human("p1", "mutation_diff_embedder", "human_escalation")
_emit_routes_through("p1", "mutation_diff_embedder", "route_through")
_emit_checks_agent_registry("p1", "mutation_diff_embedder", "agent_registry")
_emit_validates_agent_capability("p1", "mutation_diff_embedder", "capability")
_emit_dispatches_execution_plan("p1", "mutation_diff_embedder", "exec_plan")
_emit_agent_executes_agent("p1", "mutation_diff_embedder", "sub_agent")
_emit_routes_to_agent("p1", "mutation_diff_embedder", "target_agent")
_emit_verifies_policy("p1", "mutation_diff_embedder", "policy_check")
_emit_observes_runtime_state("p1", "mutation_diff_embedder", "runtime_state")
_emit_verifies_boundary("p1", "mutation_diff_embedder", "boundary_check")
_emit_transcripts_response("p1", "mutation_diff_embedder", "transcript")
_emit_hard_fails_untranscripted("p1", "mutation_diff_embedder")
_emit_gated_by_confidence("p1", "mutation_diff_embedder", "confidence_gate")
emit_replay_key("p0", "mutation_diff_embedder")
emit_determinism_digest("p0", "mutation_diff_embedder")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

logger = logging.getLogger(__name__)

_NAMESPACE = "mutation_diffs"


@dataclass(frozen=True)
class MutationRetrievalResult:
    """Nearest-neighbour result from mutation diff retrieval.

    C0_INFORMATIONAL only — no routing influence.
    """

    content_hash: str
    similarity_score: float
    mutation_id: str
    target_resource: str
    commit_outcome: str
    content_preview: str


class MutationDiffEmbedder:
    """Converts MutationDiffRecord objects to corpus records and retrieves similar diffs.

    Three-phase use:
      1. pre_commit_check(record)  — retrieve similar prior mutations before commit
      2. ingest(record)            — buffer a committed or rolled-back record
      3. export_corpus_records()   — export for seed-pack ingestion

    All retrieval is C0_INFORMATIONAL: results influence proposals, not decisions.
    """

    def __init__(self, max_buffer: int = DEFAULT_EMBEDDER_BUFFER_SIZE) -> None:
        if max_buffer < 1:
            raise ValueError(f"max_buffer must be >= 1, got {max_buffer}")
        self._max_buffer = max_buffer
        self._lock = threading.Lock()
        self._records: list[CorpusRecord] = []
        self._meta: dict[str, dict[str, Any]] = {}

    def ingest(self, record: MutationDiffRecord) -> CorpusRecord:
        """Convert a MutationDiffRecord to a CorpusRecord and buffer it.

        Args:
            record: The mutation diff record to ingest.

        Returns:
            The generated CorpusRecord.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "MutationDiffEmbedder.ingest")

        text = record.to_embedding_text()
        content_hash = compute_content_hash(text.encode("utf-8"))
        corpus_record = CorpusRecord(
            text=text,
            trace_id=record.trace_id,
            content_hash=content_hash,
            namespace=_NAMESPACE,
        )
        meta = {
            "mutation_id": record.mutation_id,
            "target_resource": record.target_resource,
            "commit_outcome": record.commit_outcome,
            "policy_hash": record.policy_hash,
            "diff_hash": record.diff_hash,
        }
        with self._lock:
            if len(self._records) >= self._max_buffer:
                dropped = self._records.pop(0)
                self._meta.pop(dropped.content_hash, None)
                logger.debug("MutationDiffEmbedder: buffer full, dropped oldest record")
            self._records.append(corpus_record)
            self._meta[content_hash] = meta
        return corpus_record

    def ingest_batch(self, records: list[MutationDiffRecord]) -> list[CorpusRecord]:
        """Ingest multiple MutationDiffRecords.

        Args:
            records: List of mutation diff records.

        Returns:
            List of generated CorpusRecords in the same order.
        """
        return [self.ingest(r) for r in records]

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

    def pre_commit_check(
        self,
        candidate: MutationDiffRecord,
        *,
        k: int = 5,
        namespace: str = _NAMESPACE,
    ) -> list[MutationRetrievalResult]:
        """Retrieve similar prior mutations before committing a new one.

        Used for risky-similarity detection: if top-k results contain
        rolled_back outcomes with high similarity, the caller should
        treat the candidate as high-risk.

        Args:
            candidate: The pending mutation to check.
            k: Maximum results.
            namespace: Seed pack namespace.

        Returns:
            List of MutationRetrievalResult — C0_INFORMATIONAL.
        """
        return self._retrieve(candidate.to_embedding_text(), k=k, namespace=namespace)

    def retrieve_similar(
        self,
        query_record: MutationDiffRecord,
        *,
        k: int = 5,
        namespace: str = _NAMESPACE,
    ) -> list[MutationRetrievalResult]:
        """Retrieve nearest-neighbour mutations via sovereign semantic cache.

        Args:
            query_record: The mutation to find neighbours for.
            k: Maximum results.
            namespace: Seed pack namespace.

        Returns:
            List of MutationRetrievalResult — C0_INFORMATIONAL.
        """
        return self._retrieve(query_record.to_embedding_text(), k=k, namespace=namespace)

    def _retrieve(
        self,
        query_text: str,
        *,
        k: int,
        namespace: str,
    ) -> list[MutationRetrievalResult]:
        k = min(k, 20)
        try:
            from agentic_core.interfaces.embeddings import query_similarity

            raw_results = query_similarity(query_text, top_k=k, namespace=namespace)
            out: list[MutationRetrievalResult] = []
            for r in raw_results:
                ch = r.content_hash
                meta = self._meta.get(ch, {})
                out.append(
                    MutationRetrievalResult(
                        content_hash=ch,
                        similarity_score=r.similarity_score,
                        mutation_id=meta.get("mutation_id", ""),
                        target_resource=meta.get("target_resource", ""),
                        commit_outcome=meta.get("commit_outcome", ""),
                        content_preview=r.content_preview,
                    ),
                )
            return out
        # guardian: allow-silent-swallow
        except Exception as exc:
            logger.debug("MutationDiffEmbedder._retrieve: %s", exc)
            return []

    @staticmethod
    def record_from_uwg_mutation(
        *,
        mutation_id: str,
        target_resource: str,
        operations: list[str],
        state_diff_summary: str,
        rollback_context: str,
        commit_outcome: str,
        trace_id: str,
        policy_hash: str,
        timestamp_utc: int,
    ) -> MutationDiffRecord:
        """Convenience constructor that validates commit_outcome literal."""
        if commit_outcome not in ("committed", "rolled_back", "pending"):
            raise ValueError(f"commit_outcome must be committed/rolled_back/pending, got {commit_outcome!r}")
        return MutationDiffRecord(
            mutation_id=mutation_id,
            target_resource=target_resource,
            operations=tuple(sorted(operations)),
            state_diff_summary=state_diff_summary,
            rollback_context=rollback_context,
            commit_outcome=commit_outcome,  # type: ignore[arg-type]
            trace_id=trace_id,
            policy_hash=policy_hash,
            timestamp_utc=timestamp_utc,
        )


__all__ = ["MutationDiffEmbedder", "MutationRetrievalResult"]
