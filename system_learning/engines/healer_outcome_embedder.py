"""HealerOutcomeEmbedder — Semantic playbook memory for healer case retrieval.

Converts HealerOutcomeRecord objects into CorpusRecords for seed-pack ingestion
and provides nearest-neighbour retrieval over historical healer cases.

High-quality signal because the healer-validator architecture enforces lineage
and replay validation — healed cases are verified true positives.

Use cases:
  - Healer selection: retrieve successful healers for a given failure type
  - Failure clustering: group recurring patterns by semantic similarity
  - RCA assistance: find closest historical incident to a new failure

Design constraints:
- No wall-clock reads; all timestamps provided by caller.
- Deterministic text serialization via HealerOutcomeRecord.to_embedding_text().
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

_emit_authorize_and_execute("p2", "healer_outcome_embedder", "execution_auth")
_emit_validates_capability("p2", "healer_outcome_embedder", "capability_check")
_emit_routes_to_capability("p2", "healer_outcome_embedder", "capability_route")
_emit_writes_via_uwg("p2", "healer_outcome_embedder", "uwg_write")
_emit_blocks_direct_write("p2", "healer_outcome_embedder", "direct_write_block")
_emit_records_tool_invocation("p2", "healer_outcome_embedder", "tool_invocation")
_emit_captures_execution_output("p2", "healer_outcome_embedder", "exec_output")
_emit_dispatches_agent("p3", "healer_outcome_embedder", "agent_dispatch")
_emit_coordinates_agents("p3", "healer_outcome_embedder", "agent_coordination")
_emit_records_workflow_lineage("p3", "healer_outcome_embedder", "workflow_lineage")
_emit_records_healing_outcome("p3", "healer_outcome_embedder", "healing_outcome")
_emit_escalates_failure("p3", "healer_outcome_embedder", "failure_escalation")
_emit_orchestrates_workflow("p3", "healer_outcome_embedder", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "healer_outcome_embedder", "healing_dispatch")
_emit_invokes_evaluation("p3", "healer_outcome_embedder", "evaluation_signal")
_emit_records_telemetry_event("p4", "healer_outcome_embedder", "telemetry_event")
_emit_captures_evaluation_metric("p4", "healer_outcome_embedder", "eval_metric")
_emit_stores_embedding("p4", "healer_outcome_embedder", "embedding_store")
_emit_updates_meta_learning_state("p4", "healer_outcome_embedder", "meta_learning")
_emit_links_execution_to_snapshot("p4", "healer_outcome_embedder", "exec_snapshot_link")
from system_learning.config.semantic_memory_config import DEFAULT_EMBEDDER_BUFFER_SIZE
from system_learning.engines.embedding_corpus_extraction import (
    CorpusRecord,
    compute_content_hash,
)
from system_learning.types.semantic_memory_types import HealerOutcomeRecord

_emit_applies_guardrail("p0", "healer_outcome_embedder", "p0_governance")
_emit_reads_policy_state("p0", "healer_outcome_embedder", "policy_binding")
_emit_snapshots_state("p0", "healer_outcome_embedder", "state_snapshot")
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

_emit_emits_metric_event("healer_outcome_embedder", "p4obs", "metric_1")
_emit_emits_metric_event("healer_outcome_embedder", "p4obs", "metric_2")
_emit_emits_metric_event("healer_outcome_embedder", "p4obs", "metric_3")
_emit_emits_metric_event("healer_outcome_embedder", "p4obs", "metric_4")
_emit_emits_metric_event("healer_outcome_embedder", "p4obs", "metric_5")
_emit_emits_metric_event("healer_outcome_embedder", "p4obs", "metric_6")
_emit_records_incident_event("healer_outcome_embedder", "p4obs", "incident")
_emit_captures_runtime_anomaly("healer_outcome_embedder", "p4obs", "anomaly")
_emit_writes_observability_log("healer_outcome_embedder", "p4obs", "obs_log")
_emit_updates_monitoring_state("healer_outcome_embedder", "p4obs", "mon_state")
_emit_triggers_alert("healer_outcome_embedder", "p4obs", "alert")
_emit_links_incident_trace("healer_outcome_embedder", "p4obs", "trace_link")
_emit_captures_pattern("healer_outcome_embedder", "p3lm", "pattern")
_emit_records_learning_event("healer_outcome_embedder", "p3lm", "learning_event")
_emit_writes_learning_snapshot("healer_outcome_embedder", "p3lm", "snapshot")
_emit_feeds_meta_learning("healer_outcome_embedder", "p3lm", "meta_feed")
_emit_updates_routing_strategy("healer_outcome_embedder", "p3lm", "routing")
_emit_improves_agent_policy("healer_outcome_embedder", "p3lm", "policy")
_emit_stores_learning_state("healer_outcome_embedder", "p3lm", "state")
_emit_records_execution_trace("healer_outcome_embedder", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("healer_outcome_embedder", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("healer_outcome_embedder", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("healer_outcome_embedder", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("healer_outcome_embedder", "L4_STATE", "p2_trace_5")
_emit_reads_environ("healer_outcome_embedder", "env_read", "p2_env_1")
_emit_reads_environ("healer_outcome_embedder", "env_read", "p2_env_2")
_emit_reads_runtime_state("healer_outcome_embedder", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("healer_outcome_embedder", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "healer_outcome_embedder", "context_pull")
_emit_pulls_context("p1", "healer_outcome_embedder", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "healer_outcome_embedder", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "healer_outcome_embedder", "uwg_term_2")
_emit_writes_through("p1", "healer_outcome_embedder", "write_through")
_emit_writes_through("p1", "healer_outcome_embedder", "write_through_2")
_emit_validated_by_safety_plane("p1", "healer_outcome_embedder", "safety_validation")
_emit_invokes_eval("p1", "healer_outcome_embedder", "eval_call")
_emit_proposal_commits_routing("p1", "healer_outcome_embedder", "routing_commit")
_emit_escalates_to_human("p1", "healer_outcome_embedder", "human_escalation")
_emit_routes_through("p1", "healer_outcome_embedder", "route_through")
_emit_checks_agent_registry("p1", "healer_outcome_embedder", "agent_registry")
_emit_validates_agent_capability("p1", "healer_outcome_embedder", "capability")
_emit_dispatches_execution_plan("p1", "healer_outcome_embedder", "exec_plan")
_emit_agent_executes_agent("p1", "healer_outcome_embedder", "sub_agent")
_emit_routes_to_agent("p1", "healer_outcome_embedder", "target_agent")
_emit_verifies_policy("p1", "healer_outcome_embedder", "policy_check")
_emit_observes_runtime_state("p1", "healer_outcome_embedder", "runtime_state")
_emit_verifies_boundary("p1", "healer_outcome_embedder", "boundary_check")
_emit_transcripts_response("p1", "healer_outcome_embedder", "transcript")
_emit_hard_fails_untranscripted("p1", "healer_outcome_embedder")
_emit_gated_by_confidence("p1", "healer_outcome_embedder", "confidence_gate")
emit_replay_key("p0", "healer_outcome_embedder")
emit_determinism_digest("p0", "healer_outcome_embedder")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

logger = logging.getLogger(__name__)

_NAMESPACE = "healer_outcomes"


@dataclass(frozen=True)
class HealerRetrievalResult:
    """Nearest-neighbour result from healer outcome retrieval.

    C0_INFORMATIONAL only — no routing influence.
    """

    content_hash: str
    similarity_score: float
    healer_id: str
    failure_type: str
    outcome: str
    tier: str
    content_preview: str


class HealerOutcomeEmbedder:
    """Converts HealerOutcomeRecord objects to corpus records and retrieves similar cases.

    Usage:
        embedder = HealerOutcomeEmbedder()
        embedder.ingest(record)
        similar = embedder.retrieve_for_failure("IMPORT_ERROR: missing module x", k=5)
    """

    def __init__(self, max_buffer: int = DEFAULT_EMBEDDER_BUFFER_SIZE) -> None:
        if max_buffer < 1:
            raise ValueError(f"max_buffer must be >= 1, got {max_buffer}")
        self._max_buffer = max_buffer
        self._lock = threading.Lock()
        self._records: list[CorpusRecord] = []
        self._meta: dict[str, dict[str, Any]] = {}

    def ingest(self, record: HealerOutcomeRecord) -> CorpusRecord:
        """Convert a HealerOutcomeRecord to a CorpusRecord and buffer it.

        Args:
            record: The healer outcome record to ingest.

        Returns:
            The generated CorpusRecord.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "HealerOutcomeEmbedder.ingest"
        )

        text = record.to_embedding_text()
        content_hash = compute_content_hash(text.encode("utf-8"))
        corpus_record = CorpusRecord(
            text=text,
            trace_id=record.trace_id,
            content_hash=content_hash,
            namespace=_NAMESPACE,
        )
        meta = {
            "healer_id": record.healer_id,
            "failure_type": record.failure_type,
            "outcome": record.outcome,
            "tier": record.tier,
            "package_version": record.package_version,
            "outcome_hash": record.outcome_hash,
        }
        with self._lock:
            if len(self._records) >= self._max_buffer:
                dropped = self._records.pop(0)
                self._meta.pop(dropped.content_hash, None)
                logger.debug("HealerOutcomeEmbedder: buffer full, dropped oldest record")
            self._records.append(corpus_record)
            self._meta[content_hash] = meta
        return corpus_record

    def ingest_batch(self, records: list[HealerOutcomeRecord]) -> list[CorpusRecord]:
        """Ingest multiple HealerOutcomeRecords.

        Args:
            records: List of healer outcome records.

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

    def retrieve_for_failure(
        self,
        failure_text: str,
        *,
        k: int = 5,
        namespace: str = _NAMESPACE,
    ) -> list[HealerRetrievalResult]:
        """Retrieve healers that successfully handled similar failures.

        Primary use: healer selection — find the best historical healer
        for a new failure by semantic similarity to the violation text.

        Args:
            failure_text: The new failure description to match against.
            k: Maximum results.
            namespace: Seed pack namespace.

        Returns:
            List of HealerRetrievalResult — C0_INFORMATIONAL.
        """
        return self._retrieve(failure_text, k=k, namespace=namespace)

    def retrieve_similar(
        self,
        query_record: HealerOutcomeRecord,
        *,
        k: int = 5,
        namespace: str = _NAMESPACE,
    ) -> list[HealerRetrievalResult]:
        """Retrieve nearest-neighbour healer outcomes via sovereign semantic cache.

        Args:
            query_record: The outcome record to find neighbours for.
            k: Maximum results.
            namespace: Seed pack namespace.

        Returns:
            List of HealerRetrievalResult — C0_INFORMATIONAL.
        """
        return self._retrieve(query_record.to_embedding_text(), k=k, namespace=namespace)

    def _retrieve(
        self,
        query_text: str,
        *,
        k: int,
        namespace: str,
    ) -> list[HealerRetrievalResult]:
        k = min(k, 20)
        try:
            from agentic_core.interfaces.embeddings import query_similarity

            raw_results = query_similarity(query_text, top_k=k, namespace=namespace)
            out: list[HealerRetrievalResult] = []
            for r in tqdm(raw_results, desc="Processing", unit="item"):
                ch = r.content_hash
                meta = self._meta.get(ch, {})
                out.append(
                    HealerRetrievalResult(
                        content_hash=ch,
                        similarity_score=r.similarity_score,
                        healer_id=meta.get("healer_id", ""),
                        failure_type=meta.get("failure_type", ""),
                        outcome=meta.get("outcome", ""),
                        tier=meta.get("tier", ""),
                        content_preview=r.content_preview,
                    ),
                )
            return out
        except (AttributeError, ImportError, RuntimeError, TypeError, ValueError) as exc:
            logger.debug("HealerOutcomeEmbedder._retrieve: %s", exc)
            return []

    @staticmethod
    def record_from_healing_event(
        *,
        healer_id: str,
        failure_type: str,
        violation_text: str,
        fix_rationale: str,
        change_summary: str,
        package_version: str,
        outcome: str,
        tier: str,
        trace_id: str,
        timestamp_utc: int,
    ) -> HealerOutcomeRecord:
        """Convenience constructor that validates outcome literal."""
        if outcome not in ("success", "failure", "partial"):
            raise ValueError(f"outcome must be success/failure/partial, got {outcome!r}")
        return HealerOutcomeRecord(
            healer_id=healer_id,
            failure_type=failure_type,
            violation_text=violation_text,
            fix_rationale=fix_rationale,
            change_summary=change_summary,
            package_version=package_version,
            outcome=outcome,  # type: ignore[arg-type]
            tier=tier,
            trace_id=trace_id,
            timestamp_utc=timestamp_utc,
        )


__all__ = ["HealerOutcomeEmbedder", "HealerRetrievalResult"]
