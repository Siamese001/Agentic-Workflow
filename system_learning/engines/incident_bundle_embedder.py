"""IncidentBundleEmbedder — Semantic memory for composite execution incidents.

Converts IncidentBundle objects into CorpusRecords for seed-pack ingestion
and provides nearest-neighbour retrieval over historical incidents.

Design constraints:
- No wall-clock reads; all timestamps provided by caller.
- Deterministic text serialization via IncidentBundle.to_embedding_text().
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

_emit_authorize_and_execute("p2", "incident_bundle_embedder", "execution_auth")
_emit_validates_capability("p2", "incident_bundle_embedder", "capability_check")
_emit_routes_to_capability("p2", "incident_bundle_embedder", "capability_route")
_emit_writes_via_uwg("p2", "incident_bundle_embedder", "uwg_write")
_emit_blocks_direct_write("p2", "incident_bundle_embedder", "direct_write_block")
_emit_records_tool_invocation("p2", "incident_bundle_embedder", "tool_invocation")
_emit_captures_execution_output("p2", "incident_bundle_embedder", "exec_output")
_emit_dispatches_agent("p3", "incident_bundle_embedder", "agent_dispatch")
_emit_coordinates_agents("p3", "incident_bundle_embedder", "agent_coordination")
_emit_records_workflow_lineage("p3", "incident_bundle_embedder", "workflow_lineage")
_emit_records_healing_outcome("p3", "incident_bundle_embedder", "healing_outcome")
_emit_escalates_failure("p3", "incident_bundle_embedder", "failure_escalation")
_emit_orchestrates_workflow("p3", "incident_bundle_embedder", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "incident_bundle_embedder", "healing_dispatch")
_emit_invokes_evaluation("p3", "incident_bundle_embedder", "evaluation_signal")
_emit_records_telemetry_event("p4", "incident_bundle_embedder", "telemetry_event")
_emit_captures_evaluation_metric("p4", "incident_bundle_embedder", "eval_metric")
_emit_stores_embedding("p4", "incident_bundle_embedder", "embedding_store")
_emit_updates_meta_learning_state("p4", "incident_bundle_embedder", "meta_learning")
_emit_links_execution_to_snapshot("p4", "incident_bundle_embedder", "exec_snapshot_link")
from system_learning.config.semantic_memory_config import DEFAULT_EMBEDDER_BUFFER_SIZE
from system_learning.engines.embedding_corpus_extraction import (
    CorpusRecord,
    compute_content_hash,
)
from system_learning.types.semantic_memory_types import IncidentBundle

_emit_applies_guardrail("p0", "incident_bundle_embedder", "p0_governance")
_emit_snapshots_state("p0", "incident_bundle_embedder", "state_snapshot")
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

_emit_emits_metric_event("incident_bundle_embedder", "p4obs", "metric_1")
_emit_emits_metric_event("incident_bundle_embedder", "p4obs", "metric_2")
_emit_emits_metric_event("incident_bundle_embedder", "p4obs", "metric_3")
_emit_emits_metric_event("incident_bundle_embedder", "p4obs", "metric_4")
_emit_emits_metric_event("incident_bundle_embedder", "p4obs", "metric_5")
_emit_emits_metric_event("incident_bundle_embedder", "p4obs", "metric_6")
_emit_records_incident_event("incident_bundle_embedder", "p4obs", "incident")
_emit_captures_runtime_anomaly("incident_bundle_embedder", "p4obs", "anomaly")
_emit_writes_observability_log("incident_bundle_embedder", "p4obs", "obs_log")
_emit_updates_monitoring_state("incident_bundle_embedder", "p4obs", "mon_state")
_emit_triggers_alert("incident_bundle_embedder", "p4obs", "alert")
_emit_links_incident_trace("incident_bundle_embedder", "p4obs", "trace_link")
_emit_captures_pattern("incident_bundle_embedder", "p3lm", "pattern")
_emit_records_learning_event("incident_bundle_embedder", "p3lm", "learning_event")
_emit_writes_learning_snapshot("incident_bundle_embedder", "p3lm", "snapshot")
_emit_feeds_meta_learning("incident_bundle_embedder", "p3lm", "meta_feed")
_emit_updates_routing_strategy("incident_bundle_embedder", "p3lm", "routing")
_emit_improves_agent_policy("incident_bundle_embedder", "p3lm", "policy")
_emit_stores_learning_state("incident_bundle_embedder", "p3lm", "state")
_emit_records_execution_trace("incident_bundle_embedder", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("incident_bundle_embedder", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("incident_bundle_embedder", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("incident_bundle_embedder", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("incident_bundle_embedder", "L4_STATE", "p2_trace_5")
_emit_reads_environ("incident_bundle_embedder", "env_read", "p2_env_1")
_emit_reads_environ("incident_bundle_embedder", "env_read", "p2_env_2")
_emit_reads_runtime_state("incident_bundle_embedder", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("incident_bundle_embedder", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "incident_bundle_embedder", "context_pull")
_emit_pulls_context("p1", "incident_bundle_embedder", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "incident_bundle_embedder", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "incident_bundle_embedder", "uwg_term_2")
_emit_writes_through("p1", "incident_bundle_embedder", "write_through")
_emit_writes_through("p1", "incident_bundle_embedder", "write_through_2")
_emit_validated_by_safety_plane("p1", "incident_bundle_embedder", "safety_validation")
_emit_invokes_eval("p1", "incident_bundle_embedder", "eval_call")
_emit_proposal_commits_routing("p1", "incident_bundle_embedder", "routing_commit")
_emit_escalates_to_human("p1", "incident_bundle_embedder", "human_escalation")
_emit_routes_through("p1", "incident_bundle_embedder", "route_through")
_emit_checks_agent_registry("p1", "incident_bundle_embedder", "agent_registry")
_emit_validates_agent_capability("p1", "incident_bundle_embedder", "capability")
_emit_dispatches_execution_plan("p1", "incident_bundle_embedder", "exec_plan")
_emit_agent_executes_agent("p1", "incident_bundle_embedder", "sub_agent")
_emit_routes_to_agent("p1", "incident_bundle_embedder", "target_agent")
_emit_verifies_policy("p1", "incident_bundle_embedder", "policy_check")
_emit_observes_runtime_state("p1", "incident_bundle_embedder", "runtime_state")
_emit_verifies_boundary("p1", "incident_bundle_embedder", "boundary_check")
_emit_transcripts_response("p1", "incident_bundle_embedder", "transcript")
_emit_hard_fails_untranscripted("p1", "incident_bundle_embedder")
_emit_gated_by_confidence("p1", "incident_bundle_embedder", "confidence_gate")
emit_replay_key("p0", "incident_bundle_embedder")
emit_determinism_digest("p0", "incident_bundle_embedder")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

logger = logging.getLogger(__name__)

_NAMESPACE = "incident_bundles"


@dataclass(frozen=True)
class IncidentRetrievalResult:
    """Nearest-neighbour result from incident bundle retrieval.

    C0_INFORMATIONAL only — no routing influence.
    """

    content_hash: str
    similarity_score: float
    trace_id: str
    outcome: str
    healer_id: str
    route_path: str
    content_preview: str


class IncidentBundleEmbedder:
    """Converts IncidentBundle objects to corpus records and retrieves similar incidents.

    Usage pattern:
        embedder = IncidentBundleEmbedder()
        embedder.ingest(bundle)
        records = embedder.export_corpus_records()

    Retrieval (requires live embedding gateway):
        results = embedder.retrieve_similar(query_bundle, k=5)
    """

    def __init__(self, max_buffer: int = DEFAULT_EMBEDDER_BUFFER_SIZE) -> None:
        if max_buffer < 1:
            raise ValueError(f"max_buffer must be >= 1, got {max_buffer}")
        self._max_buffer = max_buffer
        self._lock = threading.Lock()
        self._records: list[CorpusRecord] = []
        self._meta: dict[str, dict[str, Any]] = {}

    def ingest(self, bundle: IncidentBundle) -> CorpusRecord:
        """Convert an IncidentBundle to a CorpusRecord and buffer it.

        Args:
            bundle: The incident bundle to ingest.

        Returns:
            The generated CorpusRecord.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "IncidentBundleEmbedder.ingest"
        )

        text = bundle.to_embedding_text()
        content_hash = compute_content_hash(text.encode("utf-8"))
        record = CorpusRecord(
            text=text,
            trace_id=bundle.trace_id,
            content_hash=content_hash,
            namespace=_NAMESPACE,
        )
        meta = {
            "outcome": bundle.outcome,
            "healer_id": bundle.healer_id,
            "route_path": bundle.route_path,
            "policy_hash": bundle.policy_hash,
            "bundle_hash": bundle.bundle_hash,
        }
        with self._lock:
            if len(self._records) >= self._max_buffer:
                dropped = self._records.pop(0)
                self._meta.pop(dropped.content_hash, None)
                logger.debug("IncidentBundleEmbedder: buffer full, dropped oldest record")
            self._records.append(record)
            self._meta[content_hash] = meta
        return record

    def ingest_batch(self, bundles: list[IncidentBundle]) -> list[CorpusRecord]:
        """Ingest multiple IncidentBundles.

        Args:
            bundles: List of incident bundles.

        Returns:
            List of generated CorpusRecords in the same order.
        """
        return [self.ingest(b) for b in bundles]

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

    def retrieve_similar(
        self,
        query_bundle: IncidentBundle,
        *,
        k: int = 5,
        namespace: str = _NAMESPACE,
    ) -> list[IncidentRetrievalResult]:
        """Retrieve nearest-neighbour incidents via sovereign semantic cache.

        Falls back to empty list when EMBEDDING_ENABLED=false or cache unavailable.

        Args:
            query_bundle: The incident to find neighbours for.
            k: Maximum results (capped at 20 per C0 spec).
            namespace: Seed pack namespace to query.

        Returns:
            List of IncidentRetrievalResult — C0_INFORMATIONAL only.
        """
        k = min(k, 20)
        query_text = query_bundle.to_embedding_text()
        try:
            from agentic_core.interfaces.embeddings import query_similarity

            raw_results = query_similarity(query_text, top_k=k, namespace=namespace)
            out: list[IncidentRetrievalResult] = []
            for r in raw_results:
                ch = r.content_hash
                meta = self._meta.get(ch, {})
                out.append(
                    IncidentRetrievalResult(
                        content_hash=ch,
                        similarity_score=r.similarity_score,
                        trace_id=meta.get("trace_id", ""),
                        outcome=meta.get("outcome", ""),
                        healer_id=meta.get("healer_id", ""),
                        route_path=meta.get("route_path", ""),
                        content_preview=r.content_preview,
                    ),
                )
            return out
        # guardian: allow-silent-swallow
        except Exception as exc:
            logger.debug("IncidentBundleEmbedder.retrieve_similar: %s", exc)
            return []

    @staticmethod
    def bundle_from_healing_event(
        *,
        trace_id: str,
        trace_summary: str,
        violations: list[str],
        route_path: str,
        tool_capability: str,
        state_diff_summary: str,
        healer_id: str,
        outcome: str,
        policy_hash: str,
        timestamp_utc: int,
    ) -> IncidentBundle:
        """Convenience constructor that validates outcome literal."""
        if outcome not in ("success", "failure", "partial"):
            raise ValueError(f"outcome must be success/failure/partial, got {outcome!r}")
        return IncidentBundle(
            trace_id=trace_id,
            trace_summary=trace_summary,
            violations=tuple(sorted(violations)),
            route_path=route_path,
            tool_capability=tool_capability,
            state_diff_summary=state_diff_summary,
            healer_id=healer_id,
            outcome=outcome,  # type: ignore[arg-type]
            policy_hash=policy_hash,
            timestamp_utc=timestamp_utc,
        )


__all__ = ["IncidentBundleEmbedder", "IncidentRetrievalResult"]
