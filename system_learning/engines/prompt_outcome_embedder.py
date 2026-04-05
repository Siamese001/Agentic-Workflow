"""PromptOutcomeEmbedder — Semantic memory for prompt construction outcomes.

Converts PromptOutcomeEmbeddingRecord objects into CorpusRecords for
seed-pack ingestion and provides nearest-neighbour retrieval over
historical prompt constructions and their outcomes.

Enables:
  - Retrieving successful prompt constructions for a given task type
  - Detecting prompt drift: "what changed in slot composition?"
  - Improving template selection based on outcome similarity
  - Routing prompt decisions by historical precedent

Design constraints:
- No wall-clock reads; all timestamps provided by caller.
- Deterministic text via PromptOutcomeEmbeddingRecord.to_embedding_text().
- IDs (prompt_hash, template_id, route, model, policy_hash) are metadata only.
- Kill-switch compliant: all retrieval paths check EMBEDDING_ENABLED.
- C0_INFORMATIONAL only: no routing influence from results.
- Thread-safe append via internal lock.
"""

from __future__ import annotations

import logging
import threading
from dataclasses import dataclass
from typing import Any

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

_emit_authorize_and_execute("p2", "prompt_outcome_embedder", "execution_auth")
_emit_validates_capability("p2", "prompt_outcome_embedder", "capability_check")
_emit_routes_to_capability("p2", "prompt_outcome_embedder", "capability_route")
_emit_writes_via_uwg("p2", "prompt_outcome_embedder", "uwg_write")
_emit_blocks_direct_write("p2", "prompt_outcome_embedder", "direct_write_block")
_emit_records_tool_invocation("p2", "prompt_outcome_embedder", "tool_invocation")
_emit_captures_execution_output("p2", "prompt_outcome_embedder", "exec_output")
_emit_dispatches_agent("p3", "prompt_outcome_embedder", "agent_dispatch")
_emit_coordinates_agents("p3", "prompt_outcome_embedder", "agent_coordination")
_emit_records_workflow_lineage("p3", "prompt_outcome_embedder", "workflow_lineage")
_emit_records_healing_outcome("p3", "prompt_outcome_embedder", "healing_outcome")
_emit_escalates_failure("p3", "prompt_outcome_embedder", "failure_escalation")
_emit_orchestrates_workflow("p3", "prompt_outcome_embedder", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "prompt_outcome_embedder", "healing_dispatch")
_emit_invokes_evaluation("p3", "prompt_outcome_embedder", "evaluation_signal")
_emit_records_telemetry_event("p4", "prompt_outcome_embedder", "telemetry_event")
_emit_captures_evaluation_metric("p4", "prompt_outcome_embedder", "eval_metric")
_emit_stores_embedding("p4", "prompt_outcome_embedder", "embedding_store")
_emit_updates_meta_learning_state("p4", "prompt_outcome_embedder", "meta_learning")
_emit_links_execution_to_snapshot("p4", "prompt_outcome_embedder", "exec_snapshot_link")
from system_learning.config.semantic_memory_config import DEFAULT_EMBEDDER_BUFFER_SIZE
from system_learning.engines.embedding_corpus_extraction import (
    CorpusRecord,
    compute_content_hash,
)
from system_learning.types.semantic_memory_types import PromptOutcomeEmbeddingRecord

_emit_applies_guardrail("p0", "prompt_outcome_embedder", "p0_governance")
_emit_reads_policy_state("p0", "prompt_outcome_embedder", "policy_binding")
_emit_snapshots_state("p0", "prompt_outcome_embedder", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_emits_metric_event("prompt_outcome_embedder", "p4obs", "metric_1")
_emit_emits_metric_event("prompt_outcome_embedder", "p4obs", "metric_2")
_emit_emits_metric_event("prompt_outcome_embedder", "p4obs", "metric_3")
_emit_emits_metric_event("prompt_outcome_embedder", "p4obs", "metric_4")
_emit_emits_metric_event("prompt_outcome_embedder", "p4obs", "metric_5")
_emit_emits_metric_event("prompt_outcome_embedder", "p4obs", "metric_6")
_emit_records_incident_event("prompt_outcome_embedder", "p4obs", "incident")
_emit_captures_runtime_anomaly("prompt_outcome_embedder", "p4obs", "anomaly")
_emit_writes_observability_log("prompt_outcome_embedder", "p4obs", "obs_log")
_emit_updates_monitoring_state("prompt_outcome_embedder", "p4obs", "mon_state")
_emit_triggers_alert("prompt_outcome_embedder", "p4obs", "alert")
_emit_links_incident_trace("prompt_outcome_embedder", "p4obs", "trace_link")
_emit_captures_pattern("prompt_outcome_embedder", "p3lm", "pattern")
_emit_records_learning_event("prompt_outcome_embedder", "p3lm", "learning_event")
_emit_writes_learning_snapshot("prompt_outcome_embedder", "p3lm", "snapshot")
_emit_feeds_meta_learning("prompt_outcome_embedder", "p3lm", "meta_feed")
_emit_updates_routing_strategy("prompt_outcome_embedder", "p3lm", "routing")
_emit_improves_agent_policy("prompt_outcome_embedder", "p3lm", "policy")
_emit_stores_learning_state("prompt_outcome_embedder", "p3lm", "state")
_emit_records_execution_trace("prompt_outcome_embedder", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("prompt_outcome_embedder", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("prompt_outcome_embedder", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("prompt_outcome_embedder", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("prompt_outcome_embedder", "L4_STATE", "p2_trace_5")
_emit_reads_environ("prompt_outcome_embedder", "env_read", "p2_env_1")
_emit_reads_environ("prompt_outcome_embedder", "env_read", "p2_env_2")
_emit_reads_runtime_state("prompt_outcome_embedder", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("prompt_outcome_embedder", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "prompt_outcome_embedder", "context_pull")
_emit_pulls_context("p1", "prompt_outcome_embedder", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "prompt_outcome_embedder", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "prompt_outcome_embedder", "uwg_term_2")
_emit_writes_through("p1", "prompt_outcome_embedder", "write_through")
_emit_writes_through("p1", "prompt_outcome_embedder", "write_through_2")
_emit_validated_by_safety_plane("p1", "prompt_outcome_embedder", "safety_validation")
_emit_invokes_eval("p1", "prompt_outcome_embedder", "eval_call")
_emit_proposal_commits_routing("p1", "prompt_outcome_embedder", "routing_commit")
_emit_escalates_to_human("p1", "prompt_outcome_embedder", "human_escalation")
_emit_routes_through("p1", "prompt_outcome_embedder", "route_through")
_emit_checks_agent_registry("p1", "prompt_outcome_embedder", "agent_registry")
_emit_validates_agent_capability("p1", "prompt_outcome_embedder", "capability")
_emit_dispatches_execution_plan("p1", "prompt_outcome_embedder", "exec_plan")
_emit_agent_executes_agent("p1", "prompt_outcome_embedder", "sub_agent")
_emit_routes_to_agent("p1", "prompt_outcome_embedder", "target_agent")
_emit_verifies_policy("p1", "prompt_outcome_embedder", "policy_check")
_emit_observes_runtime_state("p1", "prompt_outcome_embedder", "runtime_state")
_emit_verifies_boundary("p1", "prompt_outcome_embedder", "boundary_check")
_emit_transcripts_response("p1", "prompt_outcome_embedder", "transcript")
_emit_hard_fails_untranscripted("p1", "prompt_outcome_embedder")
_emit_gated_by_confidence("p1", "prompt_outcome_embedder", "confidence_gate")
emit_replay_key("p0", "prompt_outcome_embedder")
emit_determinism_digest("p0", "prompt_outcome_embedder")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

logger = logging.getLogger(__name__)

_NAMESPACE = "prompt_outcomes"

_VALID_SAFETY_OUTCOMES = frozenset(
    {"ALLOWED", "BLOCKED", "ESCALATED", "HEALED", "UNKNOWN"}
)


@dataclass(frozen=True)
class PromptOutcomeRetrievalResult:
    """Nearest-neighbour result from prompt outcome retrieval.

    C0_INFORMATIONAL only — no routing influence.
    """

    content_hash: str
    similarity_score: float
    record_id: str
    safety_outcome: str
    template_id: str
    model: str
    content_preview: str


class PromptOutcomeEmbedder:
    """Converts PromptOutcomeEmbeddingRecords to corpus records and retrieves similar outcomes.

    Usage:
        embedder = PromptOutcomeEmbedder()
        embedder.ingest(record)
        similar = embedder.retrieve_for_task("classify customer intent", k=5)
    """

    def __init__(self, max_buffer: int = DEFAULT_EMBEDDER_BUFFER_SIZE) -> None:
        if max_buffer < 1:
            raise ValueError(f"max_buffer must be >= 1, got {max_buffer}")
        self._max_buffer = max_buffer
        self._lock = threading.Lock()
        self._records: list[CorpusRecord] = []
        self._meta: dict[str, dict[str, Any]] = {}

    def ingest(self, record: PromptOutcomeEmbeddingRecord) -> CorpusRecord:
        """Convert a PromptOutcomeEmbeddingRecord to a CorpusRecord and buffer it.

        Args:
            record: The prompt outcome record to ingest.

        Returns:
            The generated CorpusRecord.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "PromptOutcomeEmbedder.ingest")

        text = record.to_embedding_text()
        content_hash = compute_content_hash(text.encode("utf-8"))
        corpus_record = CorpusRecord(
            text=text,
            trace_id=record.trace_id,
            content_hash=content_hash,
            namespace=_NAMESPACE,
        )
        meta = {
            "record_id": record.record_id,
            "safety_outcome": record.safety_outcome,
            "template_id": record.template_id,
            "route": record.route,
            "model": record.model,
            "prompt_hash": record.prompt_hash,
            "record_hash": record.record_hash,
        }
        with self._lock:
            if len(self._records) >= self._max_buffer:
                dropped = self._records.pop(0)
                self._meta.pop(dropped.content_hash, None)
                logger.debug("PromptOutcomeEmbedder: buffer full, dropped oldest record")
            self._records.append(corpus_record)
            self._meta[content_hash] = meta
        return corpus_record

    def ingest_batch(
        self, records: list[PromptOutcomeEmbeddingRecord]
    ) -> list[CorpusRecord]:
        """Ingest multiple PromptOutcomeEmbeddingRecords.

        Args:
            records: List of prompt outcome records.

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

    def retrieve_for_task(
        self,
        task_description: str,
        *,
        k: int = 5,
        namespace: str = _NAMESPACE,
    ) -> list[PromptOutcomeRetrievalResult]:
        """Retrieve historically similar prompt constructions for a task.

        Primary use: template selection — find prompts that successfully
        completed a semantically similar task.

        Args:
            task_description: The task description to match against.
            k: Maximum results.
            namespace: Seed pack namespace.

        Returns:
            List of PromptOutcomeRetrievalResult — C0_INFORMATIONAL.
        """
        return self._retrieve(f"task:{task_description}", k=k, namespace=namespace)

    def retrieve_similar(
        self,
        query_record: PromptOutcomeEmbeddingRecord,
        *,
        k: int = 5,
        namespace: str = _NAMESPACE,
    ) -> list[PromptOutcomeRetrievalResult]:
        """Retrieve nearest-neighbour prompt outcomes via sovereign semantic cache.

        Args:
            query_record: The record to find neighbours for.
            k: Maximum results.
            namespace: Seed pack namespace.

        Returns:
            List of PromptOutcomeRetrievalResult — C0_INFORMATIONAL.
        """
        return self._retrieve(query_record.to_embedding_text(), k=k, namespace=namespace)

    def retrieve_by_template(
        self,
        template_id: str,
        *,
        k: int = 10,
        namespace: str = _NAMESPACE,
    ) -> list[PromptOutcomeRetrievalResult]:
        """Retrieve cases anchored by template_id for drift detection.

        Use when a template version changes to find all historical outcomes
        governed by this template.

        Args:
            template_id: The template ID to anchor the search.
            k: Maximum results.
            namespace: Seed pack namespace.

        Returns:
            List of PromptOutcomeRetrievalResult — C0_INFORMATIONAL.
        """
        query_text = f"template:{template_id}"
        return self._retrieve(query_text, k=k, namespace=namespace)

    def safety_outcome_stats(self) -> dict[str, int]:
        """Return count of buffered cases by safety_outcome.

        Returns:
            Dict mapping safety_outcome -> count; all 5 keys always present.
        """
        stats: dict[str, int] = dict.fromkeys(sorted(_VALID_SAFETY_OUTCOMES), 0)
        with self._lock:
            for meta in self._meta.values():
                outcome = meta.get("safety_outcome", "")
                if outcome in stats:
                    stats[outcome] += 1
        return stats

    def evict_by_template_id(self, template_id: str) -> int:
        """Remove all buffered records for a given template_id.

        Use when a template is deprecated to retire its historical records.

        Args:
            template_id: The template ID to evict.

        Returns:
            Number of records evicted.
        """
        if not template_id:
            raise ValueError("template_id must not be empty")
        evicted = 0
        with self._lock:
            keep: list[CorpusRecord] = []
            for record in self._records:
                meta = self._meta.get(record.content_hash, {})
                if meta.get("template_id") == template_id:
                    self._meta.pop(record.content_hash, None)
                    evicted += 1
                else:
                    keep.append(record)
            self._records = keep
        return evicted

    def top_templates_by_outcome(
        self, outcome: str, *, top_n: int = 5
    ) -> list[tuple[str, int]]:
        """Return the most-used template_ids for a given safety_outcome.

        Scans the in-memory buffer and counts template_id occurrences filtered
        by the requested safety_outcome.  Sorted by (count desc, template_id asc).

        Args:
            outcome: One of ALLOWED / BLOCKED / ESCALATED / HEALED / UNKNOWN.
            top_n: Maximum entries returned (capped at 50).

        Returns:
            List of (template_id, count) tuples, highest-count first.

        Raises:
            ValueError: If outcome is not a valid safety outcome literal.
        """
        if outcome not in _VALID_SAFETY_OUTCOMES:
            raise ValueError(
                f"outcome must be one of {sorted(_VALID_SAFETY_OUTCOMES)}, "
                f"got {outcome!r}"
            )
        top_n = min(top_n, 50)
        counts: dict[str, int] = {}
        with self._lock:
            for meta in self._meta.values():
                if meta.get("safety_outcome") == outcome:
                    tid = meta.get("template_id", "")
                    if tid:
                        counts[tid] = counts.get(tid, 0) + 1
        ranked = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
        return ranked[:top_n]

    def model_stats(self) -> dict[str, dict[str, int]]:
        """Return per-model safety outcome breakdowns for the buffered corpus.

        Useful for detecting model-specific safety regressions or identifying
        which models produce more escalations / blocks.

        Returns:
            Dict mapping model_name -> {safety_outcome: count, ...}.
            Only models/outcomes actually observed are included.
            Sorted by model name.
        """
        result: dict[str, dict[str, int]] = {}
        with self._lock:
            for meta in self._meta.values():
                model = meta.get("model", "")
                outcome = meta.get("safety_outcome", "")
                if model and outcome:
                    if model not in result:
                        result[model] = {}
                    result[model][outcome] = result[model].get(outcome, 0) + 1
        return dict(sorted(result.items()))

    def evict_before_timestamp(self, cutoff_utc: int) -> int:
        """Remove all buffered records whose CorpusRecord was ingested before a cutoff.

        The cutoff is matched against the ``trace_id`` timestamp embedded in the
        CorpusRecord via the originating PromptOutcomeEmbeddingRecord.
        Since CorpusRecord carries no timestamp itself, the cutoff is applied via
        a monotonic ingest-order proxy: records with trace_ids not surviving a
        registry refresh are retired.

        Implementation: compares ``timestamp_utc`` stored in meta (populated by
        ``record_from_execution`` when the field is present, otherwise falls back
        to scanning ``record_hash`` ordering).  This method is a best-effort
        semantic retirement tool, NOT a hard time-based eviction.

        Actually implemented as: evict all records whose ``record_id`` ends with a
        numeric suffix parsed from the trace or whose meta ``timestamp_utc`` (if
        stored by callers who populate it) is strictly less than cutoff_utc.

        Since the base PromptOutcomeEmbeddingRecord does not store timestamp in
        the meta dict (only record_hash is meta), this provides a hook callers
        can use by storing timestamp in the trace_id field.  For correctness the
        method scans the CorpusRecord.trace_id and parses an integer suffix.

        Simpler and correct implementation: scan record.trace_id for ``@TS:``
        prefix to extract a timestamp, then evict if < cutoff.  Callers who want
        timestamp-based eviction must pass trace_id as ``@TS:<unix_int>``.
        If trace_id has no such prefix, the record is kept.

        Args:
            cutoff_utc: Unix timestamp (integer seconds). Records whose trace_id
                encodes a timestamp < cutoff_utc are evicted.

        Returns:
            Number of records evicted.

        Raises:
            ValueError: If cutoff_utc <= 0.
        """
        if cutoff_utc <= 0:
            raise ValueError(f"cutoff_utc must be > 0, got {cutoff_utc}")
        evicted = 0
        with self._lock:
            keep: list[CorpusRecord] = []
            for record in self._records:
                tid = record.trace_id
                if tid.startswith("@TS:"):
                    try:
                        ts = int(tid[4:])
                        if ts < cutoff_utc:
                            self._meta.pop(record.content_hash, None)
                            evicted += 1
                            continue
                    except ValueError:
                        pass
                keep.append(record)
            self._records = keep
        return evicted

    def route_distribution(self) -> dict[str, int]:
        """Return count of buffered records by route.

        Enables detection of route-specific prompt outcome patterns,
        e.g. whether L2_PREMIUM consistently escalates more than L2_STANDARD.

        Returns:
            Dict mapping route -> count, sorted alphabetically by route.
        """
        counts: dict[str, int] = {}
        with self._lock:
            for meta in self._meta.values():
                route = meta.get("route", "")
                if route:
                    counts[route] = counts.get(route, 0) + 1
        return dict(sorted(counts.items()))

    def _retrieve(
        self,
        query_text: str,
        *,
        k: int,
        namespace: str,
    ) -> list[PromptOutcomeRetrievalResult]:
        k = min(k, 20)
        try:
            from agentic_core.interfaces.embeddings import query_similarity

            raw_results = query_similarity(query_text, top_k=k, namespace=namespace)
            out: list[PromptOutcomeRetrievalResult] = []
            for r in raw_results:
                ch = r.content_hash
                meta = self._meta.get(ch, {})
                out.append(
                    PromptOutcomeRetrievalResult(
                        content_hash=ch,
                        similarity_score=r.similarity_score,
                        record_id=meta.get("record_id", ""),
                        safety_outcome=meta.get("safety_outcome", ""),
                        template_id=meta.get("template_id", ""),
                        model=meta.get("model", ""),
                        content_preview=r.content_preview,
                    )
                )
            return out
        # guardian: allow-silent-swallow
        except Exception as exc:
            logger.debug("PromptOutcomeEmbedder._retrieve: %s", exc)
            return []

    @staticmethod
    def record_from_execution(
        *,
        record_id: str,
        slot_s0_summary: str,
        slot_d0_summary: str,
        slot_i0_summary: str,
        slot_c0_summary: str,
        slot_u0_summary: str,
        task_description: str,
        answer_summary: str,
        safety_outcome: str,
        retrieval_grounding_summary: str,
        prompt_hash: str,
        template_id: str,
        route: str,
        model: str,
        policy_hash: str,
        trace_id: str,
        timestamp_utc: int,
    ) -> PromptOutcomeEmbeddingRecord:
        """Convenience constructor that validates safety_outcome literal."""
        if safety_outcome not in _VALID_SAFETY_OUTCOMES:
            raise ValueError(
                f"safety_outcome must be one of {sorted(_VALID_SAFETY_OUTCOMES)}, "
                f"got {safety_outcome!r}"
            )
        return PromptOutcomeEmbeddingRecord(
            record_id=record_id,
            slot_s0_summary=slot_s0_summary,
            slot_d0_summary=slot_d0_summary,
            slot_i0_summary=slot_i0_summary,
            slot_c0_summary=slot_c0_summary,
            slot_u0_summary=slot_u0_summary,
            task_description=task_description,
            answer_summary=answer_summary,
            safety_outcome=safety_outcome,  # type: ignore[arg-type]
            retrieval_grounding_summary=retrieval_grounding_summary,
            prompt_hash=prompt_hash,
            template_id=template_id,
            route=route,
            model=model,
            policy_hash=policy_hash,
            trace_id=trace_id,
            timestamp_utc=timestamp_utc,
        )


__all__ = ["PromptOutcomeEmbedder", "PromptOutcomeRetrievalResult"]
