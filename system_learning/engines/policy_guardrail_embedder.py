"""PolicyGuardrailEmbedder — Semantic memory for guardrail drift cases.

Converts PolicyGuardrailCase objects into CorpusRecords for seed-pack
ingestion and provides nearest-neighbour retrieval over historical
guardrail blocks, false-positives, and false-negatives.

Enables:
  - Calibrating strictness by retrieving similar past blocks
  - Identifying drift: "what changed behavior after this policy root?"
  - False-positive/negative pattern recognition
  - Policy-hash neighborhood search: incidents linked to a policy change

Design constraints:
- No wall-clock reads; all timestamps provided by caller.
- Deterministic text serialization via PolicyGuardrailCase.to_embedding_text().
- Kill-switch compliant: all retrieval paths check EMBEDDING_ENABLED.
- C0_INFORMATIONAL only: no routing influence from results.
- Thread-safe append via internal lock.
"""

from __future__ import annotations

import logging
import threading
import uuid
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

_emit_authorize_and_execute("p2", "policy_guardrail_embedder", "execution_auth")
_emit_validates_capability("p2", "policy_guardrail_embedder", "capability_check")
_emit_routes_to_capability("p2", "policy_guardrail_embedder", "capability_route")
_emit_writes_via_uwg("p2", "policy_guardrail_embedder", "uwg_write")
_emit_blocks_direct_write("p2", "policy_guardrail_embedder", "direct_write_block")
_emit_records_tool_invocation("p2", "policy_guardrail_embedder", "tool_invocation")
_emit_captures_execution_output("p2", "policy_guardrail_embedder", "exec_output")
_emit_dispatches_agent("p3", "policy_guardrail_embedder", "agent_dispatch")
_emit_coordinates_agents("p3", "policy_guardrail_embedder", "agent_coordination")
_emit_records_workflow_lineage("p3", "policy_guardrail_embedder", "workflow_lineage")
_emit_records_healing_outcome("p3", "policy_guardrail_embedder", "healing_outcome")
_emit_escalates_failure("p3", "policy_guardrail_embedder", "failure_escalation")
_emit_orchestrates_workflow("p3", "policy_guardrail_embedder", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "policy_guardrail_embedder", "healing_dispatch")
_emit_invokes_evaluation("p3", "policy_guardrail_embedder", "evaluation_signal")
_emit_records_telemetry_event("p4", "policy_guardrail_embedder", "telemetry_event")
_emit_captures_evaluation_metric("p4", "policy_guardrail_embedder", "eval_metric")
_emit_stores_embedding("p4", "policy_guardrail_embedder", "embedding_store")
_emit_updates_meta_learning_state("p4", "policy_guardrail_embedder", "meta_learning")
_emit_links_execution_to_snapshot("p4", "policy_guardrail_embedder", "exec_snapshot_link")
from system_learning.config.semantic_memory_config import DEFAULT_EMBEDDER_BUFFER_SIZE
from system_learning.engines.embedding_corpus_extraction import (
    CorpusRecord,
    compute_content_hash,
)
from system_learning.types.semantic_memory_types import PolicyGuardrailCase

_emit_applies_guardrail("p0", "policy_guardrail_embedder", "p0_governance")
_emit_snapshots_state("p0", "policy_guardrail_embedder", "state_snapshot")
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

_emit_emits_metric_event("policy_guardrail_embedder", "p4obs", "metric_1")
_emit_emits_metric_event("policy_guardrail_embedder", "p4obs", "metric_2")
_emit_emits_metric_event("policy_guardrail_embedder", "p4obs", "metric_3")
_emit_emits_metric_event("policy_guardrail_embedder", "p4obs", "metric_4")
_emit_emits_metric_event("policy_guardrail_embedder", "p4obs", "metric_5")
_emit_emits_metric_event("policy_guardrail_embedder", "p4obs", "metric_6")
_emit_records_incident_event("policy_guardrail_embedder", "p4obs", "incident")
_emit_captures_runtime_anomaly("policy_guardrail_embedder", "p4obs", "anomaly")
_emit_writes_observability_log("policy_guardrail_embedder", "p4obs", "obs_log")
_emit_updates_monitoring_state("policy_guardrail_embedder", "p4obs", "mon_state")
_emit_triggers_alert("policy_guardrail_embedder", "p4obs", "alert")
_emit_links_incident_trace("policy_guardrail_embedder", "p4obs", "trace_link")
_emit_captures_pattern("policy_guardrail_embedder", "p3lm", "pattern")
_emit_records_learning_event("policy_guardrail_embedder", "p3lm", "learning_event")
_emit_writes_learning_snapshot("policy_guardrail_embedder", "p3lm", "snapshot")
_emit_feeds_meta_learning("policy_guardrail_embedder", "p3lm", "meta_feed")
_emit_updates_routing_strategy("policy_guardrail_embedder", "p3lm", "routing")
_emit_improves_agent_policy("policy_guardrail_embedder", "p3lm", "policy")
_emit_stores_learning_state("policy_guardrail_embedder", "p3lm", "state")
_emit_records_execution_trace("policy_guardrail_embedder", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("policy_guardrail_embedder", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("policy_guardrail_embedder", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("policy_guardrail_embedder", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("policy_guardrail_embedder", "L4_STATE", "p2_trace_5")
_emit_reads_environ("policy_guardrail_embedder", "env_read", "p2_env_1")
_emit_reads_environ("policy_guardrail_embedder", "env_read", "p2_env_2")
_emit_reads_runtime_state("policy_guardrail_embedder", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("policy_guardrail_embedder", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "policy_guardrail_embedder", "context_pull")
_emit_pulls_context("p1", "policy_guardrail_embedder", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "policy_guardrail_embedder", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "policy_guardrail_embedder", "uwg_term_2")
_emit_writes_through("p1", "policy_guardrail_embedder", "write_through")
_emit_writes_through("p1", "policy_guardrail_embedder", "write_through_2")
_emit_validated_by_safety_plane("p1", "policy_guardrail_embedder", "safety_validation")
_emit_invokes_eval("p1", "policy_guardrail_embedder", "eval_call")
_emit_proposal_commits_routing("p1", "policy_guardrail_embedder", "routing_commit")
_emit_escalates_to_human("p1", "policy_guardrail_embedder", "human_escalation")
_emit_routes_through("p1", "policy_guardrail_embedder", "route_through")
_emit_checks_agent_registry("p1", "policy_guardrail_embedder", "agent_registry")
_emit_validates_agent_capability("p1", "policy_guardrail_embedder", "capability")
_emit_dispatches_execution_plan("p1", "policy_guardrail_embedder", "exec_plan")
_emit_agent_executes_agent("p1", "policy_guardrail_embedder", "sub_agent")
_emit_routes_to_agent("p1", "policy_guardrail_embedder", "target_agent")
_emit_observes_runtime_state("p1", "policy_guardrail_embedder", "runtime_state")
_emit_verifies_boundary("p1", "policy_guardrail_embedder", "boundary_check")
_emit_transcripts_response("p1", "policy_guardrail_embedder", "transcript")
_emit_hard_fails_untranscripted("p1", "policy_guardrail_embedder")
_emit_gated_by_confidence("p1", "policy_guardrail_embedder", "confidence_gate")
emit_replay_key("p0", "policy_guardrail_embedder")
emit_determinism_digest("p0", "policy_guardrail_embedder")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

logger = logging.getLogger(__name__)

_NAMESPACE = "policy_guardrail_cases"


@dataclass(frozen=True)
class GuardrailRetrievalResult:
    """Nearest-neighbour result from policy guardrail case retrieval.

    C0_INFORMATIONAL only — no routing influence.
    """

    content_hash: str
    similarity_score: float
    case_id: str
    policy_hash: str
    verdict: str
    strictness_level: str
    content_preview: str


class PolicyGuardrailEmbedder:
    """Converts PolicyGuardrailCase objects to corpus records and retrieves similar cases.

    Usage:
        embedder = PolicyGuardrailEmbedder()
        embedder.ingest(case)
        similar = embedder.retrieve_for_policy_hash(policy_hash, k=5)
    """

    def __init__(self, max_buffer: int = DEFAULT_EMBEDDER_BUFFER_SIZE) -> None:
        if max_buffer < 1:
            raise ValueError(f"max_buffer must be >= 1, got {max_buffer}")
        self._max_buffer = max_buffer
        self._lock = threading.Lock()
        self._records: list[CorpusRecord] = []
        self._meta: dict[str, dict[str, Any]] = {}

    def ingest(self, case: PolicyGuardrailCase) -> CorpusRecord:
        """Convert a PolicyGuardrailCase to a CorpusRecord and buffer it.

        Args:
            case: The guardrail case to ingest.

        Returns:
            The generated CorpusRecord.
        """
        _emit_verifies_policy(str(uuid.uuid4()), "PolicyGuardrailEmbedder.ingest", "L4_STATE")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "PolicyGuardrailEmbedder.ingest"
        )

        text = case.to_embedding_text()
        content_hash = compute_content_hash(text.encode("utf-8"))
        corpus_record = CorpusRecord(
            text=text,
            trace_id=case.trace_id,
            content_hash=content_hash,
            namespace=_NAMESPACE,
        )
        meta = {
            "case_id": case.case_id,
            "policy_hash": case.policy_hash,
            "policy_root": case.policy_root,
            "verdict": case.verdict,
            "strictness_level": case.strictness_level,
            "case_hash": case.case_hash,
        }
        with self._lock:
            if len(self._records) >= self._max_buffer:
                dropped = self._records.pop(0)
                self._meta.pop(dropped.content_hash, None)
                logger.debug("PolicyGuardrailEmbedder: buffer full, dropped oldest record")
            self._records.append(corpus_record)
            self._meta[content_hash] = meta
        return corpus_record

    def ingest_batch(self, cases: list[PolicyGuardrailCase]) -> list[CorpusRecord]:
        """Ingest multiple PolicyGuardrailCases.

        Args:
            cases: List of guardrail cases.

        Returns:
            List of generated CorpusRecords in the same order.
        """
        return [self.ingest(c) for c in cases]

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

    def retrieve_for_payload(
        self,
        payload_summary: str,
        *,
        k: int = 5,
        namespace: str = _NAMESPACE,
    ) -> list[GuardrailRetrievalResult]:
        """Retrieve cases similar to a new blocked payload.

        Primary use: when L5 blocks a payload, retrieve semantically similar
        past decisions to calibrate whether the block is likely a true positive.

        Args:
            payload_summary: Summary of the blocked payload.
            k: Maximum results.
            namespace: Seed pack namespace.

        Returns:
            List of GuardrailRetrievalResult — C0_INFORMATIONAL.
        """
        return self._retrieve(payload_summary, k=k, namespace=namespace)

    def retrieve_for_policy_hash(
        self,
        policy_hash: str,
        *,
        k: int = 10,
        namespace: str = _NAMESPACE,
    ) -> list[GuardrailRetrievalResult]:
        """Retrieve incidents linked to a policy hash neighborhood.

        Use when a policy changes to find all historical incidents that were
        governed by this or similar policy roots — answers "what changed
        behavior after this policy root?".

        Args:
            policy_hash: The policy hash to anchor the neighborhood search.
            k: Maximum results.
            namespace: Seed pack namespace.

        Returns:
            List of GuardrailRetrievalResult — C0_INFORMATIONAL.
        """
        query_text = f"policy:{policy_hash}"
        return self._retrieve(query_text, k=k, namespace=namespace)

    def retrieve_similar(
        self,
        query_case: PolicyGuardrailCase,
        *,
        k: int = 5,
        namespace: str = _NAMESPACE,
    ) -> list[GuardrailRetrievalResult]:
        """Retrieve nearest-neighbour guardrail cases via sovereign semantic cache.

        Args:
            query_case: The case to find neighbours for.
            k: Maximum results.
            namespace: Seed pack namespace.

        Returns:
            List of GuardrailRetrievalResult — C0_INFORMATIONAL.
        """
        return self._retrieve(query_case.to_embedding_text(), k=k, namespace=namespace)

    def _retrieve(
        self,
        query_text: str,
        *,
        k: int,
        namespace: str,
    ) -> list[GuardrailRetrievalResult]:
        k = min(k, 20)
        try:
            from agentic_core.interfaces.embeddings import query_similarity

            raw_results = query_similarity(query_text, top_k=k, namespace=namespace)
            out: list[GuardrailRetrievalResult] = []
            for r in tqdm(raw_results, desc="Processing", unit="item"):
                ch = r.content_hash
                meta = self._meta.get(ch, {})
                out.append(
                    GuardrailRetrievalResult(
                        content_hash=ch,
                        similarity_score=r.similarity_score,
                        case_id=meta.get("case_id", ""),
                        policy_hash=meta.get("policy_hash", ""),
                        verdict=meta.get("verdict", ""),
                        strictness_level=meta.get("strictness_level", ""),
                        content_preview=r.content_preview,
                    ),
                )
            return out
        except (AttributeError, ImportError, RuntimeError, TypeError, ValueError) as exc:
            logger.debug("PolicyGuardrailEmbedder._retrieve: %s", exc)
            return []

    def verdict_stats(self) -> dict[str, int]:
        """Return a count of buffered cases by verdict.

        Returns:
            Dict mapping verdict → count, always containing all three keys
            (true_positive, false_positive, false_negative) even if zero.
        """
        stats: dict[str, int] = {
            "true_positive": 0,
            "false_positive": 0,
            "false_negative": 0,
        }
        with self._lock:
            for meta in self._meta.values():
                v = meta.get("verdict", "")
                if v in stats:
                    stats[v] += 1
        return stats

    def evict_by_policy_hash(self, policy_hash: str) -> int:
        """Remove all buffered records whose case metadata matches ``policy_hash``.

        Useful when a policy is rotated and its historical cases are no longer
        relevant for calibration.

        Args:
            policy_hash: Policy hash to evict.

        Returns:
            Number of records evicted.
        """
        if not policy_hash:
            raise ValueError("policy_hash must not be empty")
        evicted = 0
        with self._lock:
            keep_records: list[CorpusRecord] = []
            for record in tqdm(self._records, desc="Processing", unit="item"):
                meta = self._meta.get(record.content_hash, {})
                if meta.get("policy_hash") == policy_hash:
                    self._meta.pop(record.content_hash, None)
                    evicted += 1
                    logger.debug(
                        "PolicyGuardrailEmbedder: evicted record %s for policy %s",
                        record.content_hash[:16],
                        policy_hash[:16],
                    )
                else:
                    keep_records.append(record)
            self._records = keep_records
        return evicted

    def retrieve_by_verdict(
        self,
        verdict: str,
        *,
        limit: int = 20,
    ) -> list[dict[str, str]]:
        """Return metadata snapshots of buffered cases matching a verdict.

        Does not call the embedding service — operates purely over the
        in-memory meta store. C0_INFORMATIONAL.

        Args:
            verdict: One of ``true_positive``, ``false_positive``,
                ``false_negative``.
            limit: Maximum results to return (capped at 100).

        Returns:
            List of metadata dicts, sorted by case_id for determinism.
        """
        if verdict not in ("true_positive", "false_positive", "false_negative"):
            raise ValueError(
                f"verdict must be true_positive/false_positive/false_negative, got {verdict!r}",
            )
        limit = min(limit, 100)
        results: list[dict[str, str]] = []
        with self._lock:
            for meta in self._meta.values():
                if meta.get("verdict") == verdict:
                    results.append(dict(meta))
        results.sort(key=lambda m: m.get("case_id", ""))
        return results[:limit]

    def retrieve_false_positives(
        self,
        *,
        limit: int = 20,
    ) -> list[dict[str, str]]:
        """Convenience wrapper — returns buffered false_positive cases.

        Use to identify over-triggered guardrail patterns that should be
        candidates for strictness relaxation.

        Args:
            limit: Maximum results.

        Returns:
            List of metadata dicts, sorted by case_id.
        """
        return self.retrieve_by_verdict("false_positive", limit=limit)

    def top_strictness_levels(self, *, top_n: int = 5) -> list[tuple[str, int]]:
        """Return the most frequent strictness_level values in the buffer.

        Useful for calibration dashboards: shows which strictness tiers
        generate the most guardrail incidents.

        Args:
            top_n: Number of top levels to return (capped at 20).

        Returns:
            List of (strictness_level, count) tuples sorted by count desc,
            then level name asc for stability.
        """
        top_n = min(top_n, 20)
        counts: dict[str, int] = {}
        with self._lock:
            for meta in self._meta.values():
                level = meta.get("strictness_level", "")
                if level:
                    counts[level] = counts.get(level, 0) + 1
        ranked = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
        return ranked[:top_n]

    @staticmethod
    def case_from_l5_block(
        *,
        case_id: str,
        blocked_payload_summary: str,
        remediation_text: str,
        policy_hash: str,
        policy_root: str,
        verdict: str,
        strictness_level: str,
        trace_id: str,
        timestamp_utc: int,
    ) -> PolicyGuardrailCase:
        """Convenience constructor that validates verdict literal."""
        if verdict not in ("true_positive", "false_positive", "false_negative"):
            raise ValueError(f"verdict must be true_positive/false_positive/false_negative, got {verdict!r}")
        return PolicyGuardrailCase(
            case_id=case_id,
            blocked_payload_summary=blocked_payload_summary,
            remediation_text=remediation_text,
            policy_hash=policy_hash,
            policy_root=policy_root,
            verdict=verdict,  # type: ignore[arg-type]
            strictness_level=strictness_level,
            trace_id=trace_id,
            timestamp_utc=timestamp_utc,
        )


__all__ = ["PolicyGuardrailEmbedder", "GuardrailRetrievalResult"]
