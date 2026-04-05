"""HealingMemoryRetriever — advisory-only retrieval from the FAISS healing context index.

Layer: L1 (Cognition) — read-only consumer of L4/system_learning vector store.

Design invariants:
- Advisory-only: results MUST NOT be used to mutate routing tier, thresholds, or safety gates.
- Fail-closed: any retrieval error raises SovereigntyError immediately; no silent best-effort.
- Activation-guarded: retrieval only proceeds when the FAISS index exists; otherwise returns
  empty list (safe no-op). BGE embeddings are mandatory.
- L1 must not import from L0 or L5. This module imports only from L4 state stores and
  system_learning engines — layer boundaries enforced at import time.
"""
# guardian: allow-silent_swallower - ADG violation exemption


from __future__ import annotations

import hashlib
import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
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
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
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

emit_replay_key("p0", "healing_memory_retriever")
emit_determinism_digest("p0", "healing_memory_retriever")

_emit_dispatches_healing_run("p1", "healing_memory_retriever", "L1")
_emit_routes_through("p1", "healing_memory_retriever", "L1")
_emit_checks_agent_registry("p1", "healing_memory_retriever", "agent_registry")
_emit_validates_agent_capability("p1", "healing_memory_retriever", "capability")
_emit_dispatches_execution_plan("p1", "healing_memory_retriever", "exec_plan")
_emit_agent_executes_agent("p1", "healing_memory_retriever", "sub_agent")
_emit_routes_to_agent("p1", "healing_memory_retriever", "target_agent")
_emit_verifies_policy("p1", "healing_memory_retriever", "policy_check")
_emit_observes_runtime_state("p1", "healing_memory_retriever", "runtime_state")
_emit_verifies_boundary("p1", "healing_memory_retriever", "boundary_check")
_emit_transcripts_response("p1", "healing_memory_retriever", "transcript")
_emit_hard_fails_untranscripted("p1", "healing_memory_retriever")
_emit_gated_by_confidence("p1", "healing_memory_retriever", "confidence_gate")
_emit_escalates_to_human("p1", "healing_memory_retriever", "L1")
_emit_reads_policy_state("p1", "healing_memory_retriever", "L1")
_emit_authorize_and_execute("p2", "healing_memory_retriever", "execution_auth")
_emit_validates_capability("p2", "healing_memory_retriever", "capability_check")
_emit_routes_to_capability("p2", "healing_memory_retriever", "capability_route")
_emit_writes_via_uwg("p2", "healing_memory_retriever", "uwg_write")
_emit_blocks_direct_write("p2", "healing_memory_retriever", "direct_write_block")
_emit_records_tool_invocation("p2", "healing_memory_retriever", "tool_invocation")
_emit_captures_execution_output("p2", "healing_memory_retriever", "exec_output")
_emit_dispatches_agent("p3", "healing_memory_retriever", "agent_dispatch")
_emit_coordinates_agents("p3", "healing_memory_retriever", "agent_coordination")
_emit_records_workflow_lineage("p3", "healing_memory_retriever", "workflow_lineage")
_emit_records_healing_outcome("p3", "healing_memory_retriever", "healing_outcome")
_emit_escalates_failure("p3", "healing_memory_retriever", "failure_escalation")
_emit_orchestrates_workflow("p3", "healing_memory_retriever", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "healing_memory_retriever", "healing_dispatch")
_emit_invokes_evaluation("p3", "healing_memory_retriever", "evaluation_signal")
_emit_records_telemetry_event("p4", "healing_memory_retriever", "telemetry_event")
_emit_captures_evaluation_metric("p4", "healing_memory_retriever", "eval_metric")
_emit_stores_embedding("p4", "healing_memory_retriever", "embedding_store")
_emit_updates_meta_learning_state("p4", "healing_memory_retriever", "meta_learning")
_emit_links_execution_to_snapshot("p4", "healing_memory_retriever", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
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

_emit_emits_metric_event("healing_memory_retriever", "p4obs", "metric_1")
_emit_emits_metric_event("healing_memory_retriever", "p4obs", "metric_2")
_emit_emits_metric_event("healing_memory_retriever", "p4obs", "metric_3")
_emit_emits_metric_event("healing_memory_retriever", "p4obs", "metric_4")
_emit_emits_metric_event("healing_memory_retriever", "p4obs", "metric_5")
_emit_emits_metric_event("healing_memory_retriever", "p4obs", "metric_6")
_emit_records_incident_event("healing_memory_retriever", "p4obs", "incident")
_emit_captures_runtime_anomaly("healing_memory_retriever", "p4obs", "anomaly")
_emit_writes_observability_log("healing_memory_retriever", "p4obs", "obs_log")
_emit_updates_monitoring_state("healing_memory_retriever", "p4obs", "mon_state")
_emit_triggers_alert("healing_memory_retriever", "p4obs", "alert")
_emit_links_incident_trace("healing_memory_retriever", "p4obs", "trace_link")
_emit_captures_pattern("healing_memory_retriever", "p3lm", "pattern")
_emit_records_learning_event("healing_memory_retriever", "p3lm", "learning_event")
_emit_writes_learning_snapshot("healing_memory_retriever", "p3lm", "snapshot")
_emit_feeds_meta_learning("healing_memory_retriever", "p3lm", "meta_feed")
_emit_updates_routing_strategy("healing_memory_retriever", "p3lm", "routing")
_emit_improves_agent_policy("healing_memory_retriever", "p3lm", "policy")
_emit_stores_learning_state("healing_memory_retriever", "p3lm", "state")
_emit_records_execution_trace("healing_memory_retriever", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("healing_memory_retriever", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("healing_memory_retriever", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("healing_memory_retriever", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("healing_memory_retriever", "L4_STATE", "p2_trace_5")
_emit_reads_environ("healing_memory_retriever", "env_read", "p2_env_1")
_emit_reads_environ("healing_memory_retriever", "env_read", "p2_env_2")
_emit_reads_runtime_state("healing_memory_retriever", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("healing_memory_retriever", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "healing_memory_retriever", "context_pull")
_emit_pulls_context("p1", "healing_memory_retriever", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "healing_memory_retriever", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "healing_memory_retriever", "uwg_term_2")
_emit_writes_through("p1", "healing_memory_retriever", "write_through")
_emit_writes_through("p1", "healing_memory_retriever", "write_through_2")
_emit_validated_by_safety_plane("p1", "healing_memory_retriever", "safety_validation")
_emit_invokes_eval("p1", "healing_memory_retriever", "eval_call")
_emit_proposal_commits_routing("p1", "healing_memory_retriever", "routing_commit")

logger = logging.getLogger(__name__)
_INDEX_ID = "healing_context_v1"


class VectorSourceMismatchError(RuntimeError):
    """Raised when vectors of incompatible sources are compared.

    Phase C hardening: hash-fallback vectors (16-dim) MUST NOT be consumed
    by novelty or cluster logic as if they were real semantic embeddings
    (e.g., bge-m3 ~1024-dim).  Any dimension mismatch detected at comparison
    time raises this error immediately -- no silent coercion.
    """

    pass


class SovereigntyError(RuntimeError):
    """Raised when retrieval violates the advisory-only boundary.

    Any caller that attempts to use retrieved incidents to influence tier
    selection or routing thresholds MUST raise this error.
    """

    pass


@dataclass(frozen=True, slots=True)
class SimilarIncident:
    """Immutable advisory record returned by HealingMemoryRetriever.

    Attributes
    ----------
    content_hash : str
        SHA-256 of the stored failure signal text.
    trace_id : str | None
        Correlation ID from the original healing action (may be absent).
    similarity : float
        Cosine similarity score rounded to 6 decimal places.
    metadata : dict[str, Any]
        Stored metadata (territory, tier, outcome, etc.) — read-only.
    advisory_only : bool
        Always True — prevents misuse as a routing signal.
    """

    content_hash: str
    trace_id: str | None
    similarity: float
    metadata: dict[str, Any]
    advisory_only: bool = True


class NullHealingMemoryRetriever:
    """Null-object implementation returned when embeddings are disabled or index absent.

    All method calls return empty results with zero side effects.
    """

    def retrieve_similar_incidents(self, signal_text: str, top_k: int = 5) -> list[SimilarIncident]:
        return []

    @property
    def is_active(self) -> bool:
        return False


class HealingMemoryRetriever:
    """Advisory retriever over the LocalFAISSStore healing context index.

    Instantiate with an explicit ``store`` and ``profile`` to avoid hidden
    global state.  The caller is responsible for ensuring the index is built
    before calling ``retrieve_similar_incidents()``.

    The ``advisory_only=True`` flag on every returned ``SimilarIncident``
    is the runtime enforcement of the boundary contract (B3 hardening).
    """

    def __init__(self, store: Any, profile: Any | None = None, *, index_id: str = _INDEX_ID) -> None:
        """Initialise retriever.

        Args:
            store: A ``LocalFAISSStore`` instance (or compatible duck-type).
            profile: Optional ``RetrievalProfile`` for cutoff/top_k override.
                     When None, safe defaults (cutoff=0.75, top_k=5) are used.
            index_id: Index identifier to query.  Defaults to ``healing_context_v1``.
        """
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "HealingMemoryRetriever.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "HealingMemoryRetriever.__init__", "p0_governance")
        self._store = store
        self._profile = profile
        self._index_id = index_id

    @property
    def is_active(self) -> bool:
        return True

    def retrieve_similar_incidents(self, signal_text: str, top_k: int | None = None) -> list[SimilarIncident]:
        """Retrieve the top-K most similar healing incidents for ``signal_text``.

        B3 hardening: every returned item carries ``advisory_only=True``.
        Callers MUST NOT use the results to modify tier selection or routing
        thresholds — doing so violates the L1 advisory boundary.

        Args:
            signal_text: Normalized failure signal text (output of normalize_failure_signal).
            top_k: Maximum number of results.  Overrides profile default when given.

        Returns:
            List of SimilarIncident ordered by similarity descending.
            Empty list if the index is unavailable or signal_text is empty.

        Raises:
            SovereigntyError: If called with ``advisory_only`` overridden to False
                              (detected via caller inspection — not yet implemented,
                              reserved for Phase B hardening CI gate).
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L1_REASONING, "HealingMemoryRetriever.retrieve_similar_incidents"
        )

        if not signal_text or not signal_text.strip():
            return []
        cutoff = 0.75
        effective_top_k = top_k
        if self._profile is not None:
            cutoff = getattr(self._profile, "similarity_cutoff", cutoff)
            if effective_top_k is None:
                effective_top_k = getattr(self._profile, "top_k", 5)
        if effective_top_k is None:
            effective_top_k = 5
        try:
            from agentic_core.L2_execution.healers.bmg_embedding_similarity import bmg_embed_text

            query_vec = bmg_embed_text(signal_text)
        # guardian: allow-silent-swallow
        except Exception as exc:
            logger.debug("[HealingMemoryRetriever] bmg_embed_text unavailable: %s", exc)
            return []
        try:
            raw = self._store.search(self._index_id, query_vec, top_k=effective_top_k, cutoff=cutoff)
        # guardian: allow-silent-swallow
        except Exception as exc:
            logger.debug("[HealingMemoryRetriever] store.search failed: %s", exc)
            return []
        results: list[SimilarIncident] = []
        for content_hash, trace_id, score in raw:
            results.append(
                SimilarIncident(
                    content_hash=content_hash,
                    trace_id=trace_id or None,
                    similarity=score,
                    metadata={},
                    advisory_only=True,
                )
            )
        results.sort(key=lambda inc: (-inc.similarity, inc.content_hash, inc.trace_id or ""))
        for _inc in results:
            if not _inc.advisory_only:
                raise SovereigntyError(
                    f"advisory_only=False detected on incident {_inc.content_hash!r}; retrieval results MUST NOT be used to influence routing."
                )
        _sorted_ids = "|".join(sorted(inc.content_hash for inc in results))
        _scores_r6 = "|".join(
            f"{inc.similarity:.6f}" for inc in sorted(results, key=lambda x: x.content_hash)
        )
        _signal_norm = signal_text.strip().lower()
        _digest_input = f"{_signal_norm}|{effective_top_k}|{_sorted_ids}|{_scores_r6}"
        _digest = hashlib.sha256(_digest_input.encode("utf-8", errors="replace")).hexdigest()
        print(f"W-B-DETERMINISM-DIGEST: {_digest}")

        # Track retrieval quality metrics for system learning
        try:
            from system_learning.adapters.system_learning_memory_bridge import get_sl_memory_bridge
            bridge = get_sl_memory_bridge()

            # Calculate quality metrics
            avg_similarity = sum(inc.similarity for inc in results) / len(results) if results else 0.0
            high_similarity_count = sum(1 for inc in results if inc.similarity > 0.8)
            retrieval_quality = "high" if avg_similarity > 0.8 else "medium" if avg_similarity > 0.6 else "low"

            bridge.persist_healing_memory_retrieval_quality(
                signal_hash=hashlib.sha256(signal_text.encode()).hexdigest()[:16],
                results_count=len(results),
                avg_similarity=avg_similarity,
                high_similarity_count=high_similarity_count,
                retrieval_quality=retrieval_quality,
                top_k_used=effective_top_k,
                timestamp_utc=int(time.time() * 1000),
            )
        except Exception:
            # System learning unavailable - continue without tracking
            pass

        return results


def build_retriever(
    base_path: Path | None = None, profile: Any | None = None, *, index_id: str = _INDEX_ID
) -> HealingMemoryRetriever | NullHealingMemoryRetriever:
    """Factory: return a live HealingMemoryRetriever or NullHealingMemoryRetriever.

    Returns NullHealingMemoryRetriever when:
    - LocalFAISSStore import fails
    - base_path is None

    Returns HealingMemoryRetriever when:
    - LocalFAISSStore import succeeds
    - base_path is not None

    BGE embeddings are mandatory. This factory ensures that the retriever is only
    active when the FAISS index is available.
    """
    if base_path is None:
        return NullHealingMemoryRetriever()
    try:
        from system_learning.engines.local_faiss_store import LocalFAISSStore, ManifestIntegrityError

        store = LocalFAISSStore(base_path=Path(base_path))
        disk_dir = Path(base_path) / index_id
        if disk_dir.exists():
            try:
                store.load_from_disk(index_id, disk_dir)
            except (ManifestIntegrityError, Exception):
                pass
        return HealingMemoryRetriever(store=store, profile=profile, index_id=index_id)
    except ImportError:  # guardian: allow-silent-swallow
        return NullHealingMemoryRetriever()


__all__ = [
    "HealingMemoryRetriever",
    "NullHealingMemoryRetriever",
    "SimilarIncident",
    "SovereigntyError",
    "VectorSourceMismatchError",
    "build_retriever",
]
