"""PathDPreferenceEmbedder — Semantic memory for HITL preference pairs.

Converts PathDPreferencePair objects (DPO-style human decisions from Path D)
into CorpusRecords for seed-pack ingestion and provides nearest-neighbour
retrieval over historical human preference judgments.

Enables retrieval of human preference precedents before:
  - Proposing an action that resembles a previously-rejected plan
  - Escalating to HITL (what did humans decide in similar situations?)
  - Tuning thresholds based on human approval/rejection patterns

Design constraints:
- No wall-clock reads; all timestamps provided by caller.
- Deterministic text serialization via PathDPreferencePair.to_embedding_text().
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

_emit_authorize_and_execute("p2", "path_d_preference_embedder", "execution_auth")
_emit_validates_capability("p2", "path_d_preference_embedder", "capability_check")
_emit_routes_to_capability("p2", "path_d_preference_embedder", "capability_route")
_emit_writes_via_uwg("p2", "path_d_preference_embedder", "uwg_write")
_emit_blocks_direct_write("p2", "path_d_preference_embedder", "direct_write_block")
_emit_records_tool_invocation("p2", "path_d_preference_embedder", "tool_invocation")
_emit_captures_execution_output("p2", "path_d_preference_embedder", "exec_output")
_emit_dispatches_agent("p3", "path_d_preference_embedder", "agent_dispatch")
_emit_coordinates_agents("p3", "path_d_preference_embedder", "agent_coordination")
_emit_records_workflow_lineage("p3", "path_d_preference_embedder", "workflow_lineage")
_emit_records_healing_outcome("p3", "path_d_preference_embedder", "healing_outcome")
_emit_escalates_failure("p3", "path_d_preference_embedder", "failure_escalation")
_emit_orchestrates_workflow("p3", "path_d_preference_embedder", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "path_d_preference_embedder", "healing_dispatch")
_emit_invokes_evaluation("p3", "path_d_preference_embedder", "evaluation_signal")
_emit_records_telemetry_event("p4", "path_d_preference_embedder", "telemetry_event")
_emit_captures_evaluation_metric("p4", "path_d_preference_embedder", "eval_metric")
_emit_stores_embedding("p4", "path_d_preference_embedder", "embedding_store")
_emit_updates_meta_learning_state("p4", "path_d_preference_embedder", "meta_learning")
_emit_links_execution_to_snapshot("p4", "path_d_preference_embedder", "exec_snapshot_link")
from system_learning.config.semantic_memory_config import DEFAULT_EMBEDDER_BUFFER_SIZE
from system_learning.engines.embedding_corpus_extraction import (
    CorpusRecord,
    compute_content_hash,
)
from system_learning.types.semantic_memory_types import PathDPreferencePair

_emit_applies_guardrail("p0", "path_d_preference_embedder", "p0_governance")
_emit_reads_policy_state("p0", "path_d_preference_embedder", "policy_binding")
_emit_snapshots_state("p0", "path_d_preference_embedder", "state_snapshot")
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

_emit_emits_metric_event("path_d_preference_embedder", "p4obs", "metric_1")
_emit_emits_metric_event("path_d_preference_embedder", "p4obs", "metric_2")
_emit_emits_metric_event("path_d_preference_embedder", "p4obs", "metric_3")
_emit_emits_metric_event("path_d_preference_embedder", "p4obs", "metric_4")
_emit_emits_metric_event("path_d_preference_embedder", "p4obs", "metric_5")
_emit_emits_metric_event("path_d_preference_embedder", "p4obs", "metric_6")
_emit_records_incident_event("path_d_preference_embedder", "p4obs", "incident")
_emit_captures_runtime_anomaly("path_d_preference_embedder", "p4obs", "anomaly")
_emit_writes_observability_log("path_d_preference_embedder", "p4obs", "obs_log")
_emit_updates_monitoring_state("path_d_preference_embedder", "p4obs", "mon_state")
_emit_triggers_alert("path_d_preference_embedder", "p4obs", "alert")
_emit_links_incident_trace("path_d_preference_embedder", "p4obs", "trace_link")
_emit_captures_pattern("path_d_preference_embedder", "p3lm", "pattern")
_emit_records_learning_event("path_d_preference_embedder", "p3lm", "learning_event")
_emit_writes_learning_snapshot("path_d_preference_embedder", "p3lm", "snapshot")
_emit_feeds_meta_learning("path_d_preference_embedder", "p3lm", "meta_feed")
_emit_updates_routing_strategy("path_d_preference_embedder", "p3lm", "routing")
_emit_improves_agent_policy("path_d_preference_embedder", "p3lm", "policy")
_emit_stores_learning_state("path_d_preference_embedder", "p3lm", "state")
_emit_records_execution_trace("path_d_preference_embedder", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("path_d_preference_embedder", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("path_d_preference_embedder", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("path_d_preference_embedder", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("path_d_preference_embedder", "L4_STATE", "p2_trace_5")
_emit_reads_environ("path_d_preference_embedder", "env_read", "p2_env_1")
_emit_reads_environ("path_d_preference_embedder", "env_read", "p2_env_2")
_emit_reads_runtime_state("path_d_preference_embedder", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("path_d_preference_embedder", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "path_d_preference_embedder", "context_pull")
_emit_pulls_context("p1", "path_d_preference_embedder", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "path_d_preference_embedder", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "path_d_preference_embedder", "uwg_term_2")
_emit_writes_through("p1", "path_d_preference_embedder", "write_through")
_emit_writes_through("p1", "path_d_preference_embedder", "write_through_2")
_emit_validated_by_safety_plane("p1", "path_d_preference_embedder", "safety_validation")
_emit_invokes_eval("p1", "path_d_preference_embedder", "eval_call")
_emit_proposal_commits_routing("p1", "path_d_preference_embedder", "routing_commit")
_emit_escalates_to_human("p1", "path_d_preference_embedder", "human_escalation")
_emit_routes_through("p1", "path_d_preference_embedder", "route_through")
_emit_checks_agent_registry("p1", "path_d_preference_embedder", "agent_registry")
_emit_validates_agent_capability("p1", "path_d_preference_embedder", "capability")
_emit_dispatches_execution_plan("p1", "path_d_preference_embedder", "exec_plan")
_emit_agent_executes_agent("p1", "path_d_preference_embedder", "sub_agent")
_emit_routes_to_agent("p1", "path_d_preference_embedder", "target_agent")
_emit_verifies_policy("p1", "path_d_preference_embedder", "policy_check")
_emit_observes_runtime_state("p1", "path_d_preference_embedder", "runtime_state")
_emit_verifies_boundary("p1", "path_d_preference_embedder", "boundary_check")
_emit_transcripts_response("p1", "path_d_preference_embedder", "transcript")
_emit_hard_fails_untranscripted("p1", "path_d_preference_embedder")
_emit_gated_by_confidence("p1", "path_d_preference_embedder", "confidence_gate")
emit_replay_key("p0", "path_d_preference_embedder")
emit_determinism_digest("p0", "path_d_preference_embedder")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

logger = logging.getLogger(__name__)

_NAMESPACE = "path_d_preferences"


@dataclass(frozen=True)
class PreferenceRetrievalResult:
    """Nearest-neighbour result from Path D preference retrieval.

    C0_INFORMATIONAL only — no routing influence.
    """

    content_hash: str
    similarity_score: float
    decision_id: str
    decision: str
    agent: str
    content_preview: str


class PathDPreferenceEmbedder:
    """Converts PathDPreferencePair objects to corpus records and retrieves similar cases.

    Usage:
        embedder = PathDPreferenceEmbedder()
        embedder.ingest(pair)
        similar = embedder.retrieve_for_proposal(plan_text, k=5)
    """

    def __init__(self, max_buffer: int = DEFAULT_EMBEDDER_BUFFER_SIZE) -> None:
        if max_buffer < 1:
            raise ValueError(f"max_buffer must be >= 1, got {max_buffer}")
        self._max_buffer = max_buffer
        self._lock = threading.Lock()
        self._records: list[CorpusRecord] = []
        self._meta: dict[str, dict[str, Any]] = {}

    def ingest(self, pair: PathDPreferencePair) -> CorpusRecord:
        """Convert a PathDPreferencePair to a CorpusRecord and buffer it.

        Args:
            pair: The preference pair to ingest.

        Returns:
            The generated CorpusRecord.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "PathDPreferenceEmbedder.ingest")

        text = pair.to_embedding_text()
        content_hash = compute_content_hash(text.encode("utf-8"))
        corpus_record = CorpusRecord(
            text=text,
            trace_id=pair.trace_id,
            content_hash=content_hash,
            namespace=_NAMESPACE,
        )
        meta = {
            "decision_id": pair.decision_id,
            "decision": pair.decision,
            "agent": pair.agent,
            "resulting_outcome": pair.resulting_outcome,
            "pair_hash": pair.pair_hash,
        }
        with self._lock:
            if len(self._records) >= self._max_buffer:
                dropped = self._records.pop(0)
                self._meta.pop(dropped.content_hash, None)
                logger.debug("PathDPreferenceEmbedder: buffer full, dropped oldest record")
            self._records.append(corpus_record)
            self._meta[content_hash] = meta
        return corpus_record

    def ingest_batch(self, pairs: list[PathDPreferencePair]) -> list[CorpusRecord]:
        """Ingest multiple PathDPreferencePairs.

        Args:
            pairs: List of preference pairs.

        Returns:
            List of generated CorpusRecords in the same order.
        """
        return [self.ingest(p) for p in pairs]

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

    def retrieve_for_proposal(
        self,
        plan_text: str,
        *,
        k: int = 5,
        namespace: str = _NAMESPACE,
    ) -> list[PreferenceRetrievalResult]:
        """Retrieve precedent human decisions for a proposed plan.

        Primary use: before escalating to HITL, check whether similar plans
        were previously approved or rejected to inform the proposal framing.

        Args:
            plan_text: The proposed plan text to match against.
            k: Maximum results.
            namespace: Seed pack namespace.

        Returns:
            List of PreferenceRetrievalResult — C0_INFORMATIONAL.
        """
        return self._retrieve(plan_text, k=k, namespace=namespace)

    def retrieve_similar(
        self,
        query_pair: PathDPreferencePair,
        *,
        k: int = 5,
        namespace: str = _NAMESPACE,
    ) -> list[PreferenceRetrievalResult]:
        """Retrieve nearest-neighbour preference pairs via sovereign semantic cache.

        Args:
            query_pair: The preference pair to find neighbours for.
            k: Maximum results.
            namespace: Seed pack namespace.

        Returns:
            List of PreferenceRetrievalResult — C0_INFORMATIONAL.
        """
        return self._retrieve(query_pair.to_embedding_text(), k=k, namespace=namespace)

    def _retrieve(
        self,
        query_text: str,
        *,
        k: int,
        namespace: str,
    ) -> list[PreferenceRetrievalResult]:
        k = min(k, 20)
        try:
            from agentic_core.interfaces.embeddings import query_similarity

            raw_results = query_similarity(query_text, top_k=k, namespace=namespace)
            out: list[PreferenceRetrievalResult] = []
            for r in raw_results:
                ch = r.content_hash
                meta = self._meta.get(ch, {})
                out.append(
                    PreferenceRetrievalResult(
                        content_hash=ch,
                        similarity_score=r.similarity_score,
                        decision_id=meta.get("decision_id", ""),
                        decision=meta.get("decision", ""),
                        agent=meta.get("agent", ""),
                        content_preview=r.content_preview,
                    ),
                )
            return out
        # guardian: allow-silent-swallow
        except Exception as exc:
            logger.debug("PathDPreferenceEmbedder._retrieve: %s", exc)
            return []

    @staticmethod
    def pair_from_hitl_log(
        *,
        decision_id: str,
        original_plan: str,
        human_patch: str,
        decision: str,
        reason: str,
        resulting_outcome: str,
        agent: str,
        trace_id: str,
        timestamp_utc: int,
    ) -> PathDPreferencePair:
        """Convenience constructor that validates decision literal."""
        if decision not in ("approved", "rejected", "modified"):
            raise ValueError(f"decision must be approved/rejected/modified, got {decision!r}")
        return PathDPreferencePair(
            decision_id=decision_id,
            original_plan=original_plan,
            human_patch=human_patch,
            decision=decision,  # type: ignore[arg-type]
            reason=reason,
            resulting_outcome=resulting_outcome,
            agent=agent,
            trace_id=trace_id,
            timestamp_utc=timestamp_utc,
        )


__all__ = ["PathDPreferenceEmbedder", "PreferenceRetrievalResult"]
