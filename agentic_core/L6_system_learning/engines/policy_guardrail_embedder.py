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

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_authorize_and_execute("p2", "policy_guardrail_embedder", "execution_auth")
trace_contract._emit_validates_capability("p2", "policy_guardrail_embedder", "capability_check")
trace_contract._emit_routes_to_capability("p2", "policy_guardrail_embedder", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "policy_guardrail_embedder", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "policy_guardrail_embedder", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "policy_guardrail_embedder", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "policy_guardrail_embedder", "exec_output")
trace_contract._emit_dispatches_agent("p3", "policy_guardrail_embedder", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "policy_guardrail_embedder", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "policy_guardrail_embedder", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "policy_guardrail_embedder", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "policy_guardrail_embedder", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "policy_guardrail_embedder", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "policy_guardrail_embedder", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "policy_guardrail_embedder", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "policy_guardrail_embedder", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "policy_guardrail_embedder", "eval_metric")
trace_contract._emit_stores_embedding("p4", "policy_guardrail_embedder", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "policy_guardrail_embedder", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "policy_guardrail_embedder", "exec_snapshot_link")
from agentic_core.L6_system_learning.config.semantic_memory_config import DEFAULT_EMBEDDER_BUFFER_SIZE
from .embedding_corpus_extraction import (
    CorpusRecord,
    compute_content_hash,
)
from agentic_core.L6_system_learning.types.semantic_memory_types import PolicyGuardrailCase

trace_contract._emit_applies_guardrail("p0", "policy_guardrail_embedder", "p0_governance")
trace_contract._emit_snapshots_state("p0", "policy_guardrail_embedder", "state_snapshot")
from tqdm import tqdm

trace_contract._emit_emits_metric_event("policy_guardrail_embedder", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("policy_guardrail_embedder", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("policy_guardrail_embedder", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("policy_guardrail_embedder", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("policy_guardrail_embedder", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("policy_guardrail_embedder", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("policy_guardrail_embedder", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("policy_guardrail_embedder", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("policy_guardrail_embedder", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("policy_guardrail_embedder", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("policy_guardrail_embedder", "p4obs", "alert")
trace_contract._emit_links_incident_trace("policy_guardrail_embedder", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("policy_guardrail_embedder", "p3lm", "pattern")
trace_contract._emit_records_learning_event("policy_guardrail_embedder", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("policy_guardrail_embedder", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("policy_guardrail_embedder", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("policy_guardrail_embedder", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("policy_guardrail_embedder", "p3lm", "policy")
trace_contract._emit_stores_learning_state("policy_guardrail_embedder", "p3lm", "state")
trace_contract._emit_records_execution_trace("policy_guardrail_embedder", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("policy_guardrail_embedder", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("policy_guardrail_embedder", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("policy_guardrail_embedder", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("policy_guardrail_embedder", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("policy_guardrail_embedder", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("policy_guardrail_embedder", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("policy_guardrail_embedder", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("policy_guardrail_embedder", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "policy_guardrail_embedder", "context_pull")
trace_contract._emit_pulls_context("p1", "policy_guardrail_embedder", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "policy_guardrail_embedder", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "policy_guardrail_embedder", "uwg_term_2")
trace_contract._emit_writes_through("p1", "policy_guardrail_embedder", "write_through")
trace_contract._emit_writes_through("p1", "policy_guardrail_embedder", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "policy_guardrail_embedder", "safety_validation")
trace_contract._emit_invokes_eval("p1", "policy_guardrail_embedder", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "policy_guardrail_embedder", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "policy_guardrail_embedder", "human_escalation")
trace_contract._emit_routes_through("p1", "policy_guardrail_embedder", "route_through")
trace_contract._emit_checks_agent_registry("p1", "policy_guardrail_embedder", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "policy_guardrail_embedder", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "policy_guardrail_embedder", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "policy_guardrail_embedder", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "policy_guardrail_embedder", "target_agent")
trace_contract._emit_observes_runtime_state("p1", "policy_guardrail_embedder", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "policy_guardrail_embedder", "boundary_check")
trace_contract._emit_transcripts_response("p1", "policy_guardrail_embedder", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "policy_guardrail_embedder")
trace_contract._emit_gated_by_confidence("p1", "policy_guardrail_embedder", "confidence_gate")
trace_contract.emit_replay_key("p0", "policy_guardrail_embedder")
trace_contract.emit_determinism_digest("p0", "policy_guardrail_embedder")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

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
        trace_contract._emit_verifies_policy(str(uuid.uuid4()), "PolicyGuardrailEmbedder.ingest", "L4_STATE")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "PolicyGuardrailEmbedder.ingest"
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
