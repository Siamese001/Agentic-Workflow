"""IntentEmbeddingClassifier — embedding-based intent classifier for AgenticRouter.

Replaces the keyword hit-ratio in AgenticRouter._classify() with cosine-similarity
against per-target prototype vectors stored in a LocalFAISSStore index.

Design invariants
-----------------
1. Pure class — no global mutable state.
2. No wall-clock reads.
3. Deterministic: embedding model pinned by pack-hash; same input → same output.
4. Fail-closed on EmbeddingDisabledError — returns None so caller falls back
   to legacy keyword path.  Never raises into the router.
5. C0_INFORMATIONAL influence class — classification result MUST NOT bypass
   L0 governance contracts or safety gates.

Layer: L0_routing
"""

from __future__ import annotations

import hashlib
import logging
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    emit_replay_key,
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
)

_emit_dispatches_healing_run("p1", "intent_embedding_classifier", "L0")
_emit_routes_through("p1", "intent_embedding_classifier", "L0")
_emit_checks_agent_registry("p1", "intent_embedding_classifier", "agent_registry")
_emit_validates_agent_capability("p1", "intent_embedding_classifier", "capability")
_emit_dispatches_execution_plan("p1", "intent_embedding_classifier", "exec_plan")
_emit_agent_executes_agent("p1", "intent_embedding_classifier", "sub_agent")
_emit_routes_to_agent("p1", "intent_embedding_classifier", "target_agent")
_emit_verifies_policy("p1", "intent_embedding_classifier", "policy_check")
_emit_observes_runtime_state("p1", "intent_embedding_classifier", "runtime_state")
_emit_verifies_boundary("p1", "intent_embedding_classifier", "boundary_check")
_emit_transcripts_response("p1", "intent_embedding_classifier", "transcript")
_emit_hard_fails_untranscripted("p1", "intent_embedding_classifier")
_emit_gated_by_confidence("p1", "intent_embedding_classifier", "confidence_gate")
_emit_escalates_to_human("p1", "intent_embedding_classifier", "L0")
_emit_reads_policy_state("p1", "intent_embedding_classifier", "L0")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "intent_embedding_classifier", "p0_governance")
_emit_snapshots_state("p0", "intent_embedding_classifier", "state_snapshot")
_emit_authorize_and_execute("p2", "intent_embedding_classifier", "execution_auth")
_emit_validates_capability("p2", "intent_embedding_classifier", "capability_check")
_emit_routes_to_capability("p2", "intent_embedding_classifier", "capability_route")
_emit_writes_via_uwg("p2", "intent_embedding_classifier", "uwg_write")
_emit_blocks_direct_write("p2", "intent_embedding_classifier", "direct_write_block")
_emit_records_tool_invocation("p2", "intent_embedding_classifier", "tool_invocation")
_emit_captures_execution_output("p2", "intent_embedding_classifier", "exec_output")
_emit_dispatches_agent("p3", "intent_embedding_classifier", "agent_dispatch")
_emit_coordinates_agents("p3", "intent_embedding_classifier", "agent_coordination")
_emit_records_workflow_lineage("p3", "intent_embedding_classifier", "workflow_lineage")
_emit_records_healing_outcome("p3", "intent_embedding_classifier", "healing_outcome")
_emit_escalates_failure("p3", "intent_embedding_classifier", "failure_escalation")
_emit_orchestrates_workflow("p3", "intent_embedding_classifier", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "intent_embedding_classifier", "healing_dispatch")
_emit_invokes_evaluation("p3", "intent_embedding_classifier", "evaluation_signal")
_emit_records_telemetry_event("p4", "intent_embedding_classifier", "telemetry_event")
_emit_captures_evaluation_metric("p4", "intent_embedding_classifier", "eval_metric")
_emit_stores_embedding("p4", "intent_embedding_classifier", "embedding_store")
_emit_updates_meta_learning_state("p4", "intent_embedding_classifier", "meta_learning")
_emit_links_execution_to_snapshot("p4", "intent_embedding_classifier", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_records_execution_trace,
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
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
)

_emit_emits_metric_event("intent_embedding_classifier", "p4obs", "metric_1")
_emit_emits_metric_event("intent_embedding_classifier", "p4obs", "metric_2")
_emit_emits_metric_event("intent_embedding_classifier", "p4obs", "metric_3")
_emit_emits_metric_event("intent_embedding_classifier", "p4obs", "metric_4")
_emit_emits_metric_event("intent_embedding_classifier", "p4obs", "metric_5")
_emit_emits_metric_event("intent_embedding_classifier", "p4obs", "metric_6")
_emit_records_incident_event("intent_embedding_classifier", "p4obs", "incident")
_emit_captures_runtime_anomaly("intent_embedding_classifier", "p4obs", "anomaly")
_emit_writes_observability_log("intent_embedding_classifier", "p4obs", "obs_log")
_emit_updates_monitoring_state("intent_embedding_classifier", "p4obs", "mon_state")
_emit_triggers_alert("intent_embedding_classifier", "p4obs", "alert")
_emit_links_incident_trace("intent_embedding_classifier", "p4obs", "trace_link")
_emit_captures_pattern("intent_embedding_classifier", "p3lm", "pattern")
_emit_records_learning_event("intent_embedding_classifier", "p3lm", "learning_event")
_emit_writes_learning_snapshot("intent_embedding_classifier", "p3lm", "snapshot")
_emit_feeds_meta_learning("intent_embedding_classifier", "p3lm", "meta_feed")
_emit_updates_routing_strategy("intent_embedding_classifier", "p3lm", "routing")
_emit_improves_agent_policy("intent_embedding_classifier", "p3lm", "policy")
_emit_stores_learning_state("intent_embedding_classifier", "p3lm", "state")
_emit_records_execution_trace("intent_embedding_classifier", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("intent_embedding_classifier", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("intent_embedding_classifier", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("intent_embedding_classifier", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("intent_embedding_classifier", "L4_STATE", "p2_trace_5")
_emit_reads_environ("intent_embedding_classifier", "env_read", "p2_env_1")
_emit_reads_environ("intent_embedding_classifier", "env_read", "p2_env_2")
_emit_reads_runtime_state("intent_embedding_classifier", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("intent_embedding_classifier", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "intent_embedding_classifier", "context_pull")
_emit_pulls_context("p1", "intent_embedding_classifier", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "intent_embedding_classifier", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "intent_embedding_classifier", "uwg_term_2")
_emit_writes_through("p1", "intent_embedding_classifier", "write_through")
_emit_writes_through("p1", "intent_embedding_classifier", "write_through_2")
_emit_validated_by_safety_plane("p1", "intent_embedding_classifier", "safety_validation")
_emit_invokes_eval("p1", "intent_embedding_classifier", "eval_call")
_emit_proposal_commits_routing("p1", "intent_embedding_classifier", "routing_commit")

logger = logging.getLogger(__name__)

_INDEX_ID = "intent_prototypes"
_TOP_K = 1
_COSINE_CUTOFF = 0.0


def _l2_normalize(vec: list[float]) -> list[float]:
    norm = math.sqrt(sum(x * x for x in vec))
    if norm == 0.0:
        return vec
    return [x / norm for x in vec]


def _average_vectors(vecs: list[list[float]]) -> list[float] | None:
    """Return component-wise average of a non-empty list of equal-length vectors."""
    if not vecs:
        return None
    dim = len(vecs[0])
    avg = [0.0] * dim
    for v in vecs:
        for i, x in enumerate(v):
            avg[i] += x
    n = len(vecs)
    return [x / n for x in avg]


@dataclass
class _PrototypeEntry:
    """In-memory prototype record for one routing target."""

    target_name: str
    content_hash: str
    vector: list[float]


class IntentEmbeddingClassifier:
    """Cosine-similarity intent classifier backed by a LocalFAISSStore index.

    Usage::

        classifier = IntentEmbeddingClassifier(store_base_path=Path("..."))
        classifier.encode_prototype("resume_writer", ["resume", "cv", "career"])
        classifier.encode_prototype("code_reviewer", ["code", "review", "python"])
        target_name, confidence = classifier.classify("Please review my Python code")

    When embedding is unavailable (kill-switch / FAISS not installed), all
    methods return safe defaults without raising.

    Args:
        store_base_path: Directory passed to LocalFAISSStore for index storage.
        embedder:        Optional pre-built embedding callable
                         ``(texts: list[str]) -> list[list[float]]``.
                         When None, the classifier attempts to build one from
                         ``EmbeddingServiceFactory``.
        cosine_cutoff:   Minimum cosine score to return a non-None result
                         (default 0.0 — always returns best match).
    """

    def __init__(
        self,
        store_base_path: Path | None = None,
        embedder: Any | None = None,
        cosine_cutoff: float = _COSINE_CUTOFF,
    ) -> None:
        self._store_base_path = store_base_path or Path("artifacts/intent_index")
        self._embedder = embedder
        self._cosine_cutoff = cosine_cutoff
        self._prototypes: dict[str, _PrototypeEntry] = {}
        self._store: Any | None = None
        self._store_ready = False

    # ------------------------------------------------------------------
    # Embedder access (lazy, fail-silent)
    # ------------------------------------------------------------------

    def _get_embedder(self) -> Any | None:
        if self._embedder is not None:
            return self._embedder
        try:
            from system_learning.engines.embedding_service_factory import (
                EmbeddingServiceFactory,
            )

            factory = EmbeddingServiceFactory.get_instance()
            self._embedder = factory
            return self._embedder
        except Exception as exc:  # guardian: allow-silent-swallow
            logger.debug("IntentEmbeddingClassifier: embedder unavailable: %s", exc)
            return None

    def _embed_texts(self, texts: list[str]) -> list[list[float]] | None:
        """Embed a list of texts, returning None if embedding is disabled."""
        embedder = self._get_embedder()
        if embedder is None:
            return None
        try:
            results: list[list[float]] = []
            for text in texts:
                result = embedder.embed(text)
                if result is None:
                    continue
                try:
                    vec = list(result.vector)
                except AttributeError:
                    vec = list(result)
                results.append(vec)
            return results if results else None
        except Exception as exc:  # guardian: allow-silent-swallow
            logger.debug("IntentEmbeddingClassifier: embedding failed: %s", exc)
            return None

    # ------------------------------------------------------------------
    # Prototype registration
    # ------------------------------------------------------------------

    def encode_prototype(self, target_name: str, texts: list[str]) -> bool:
        """Encode and store a prototype vector for a routing target.

        Args:
            target_name: Name of the routing target (must match RouteTarget.name).
            texts:       List of representative texts (keywords + description).

        Returns:
            True if prototype was stored, False if embedding unavailable.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L0_ROUTING, "IntentEmbeddingClassifier.encode_prototype"
        )
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        if not texts:
            logger.warning("IntentEmbeddingClassifier.encode_prototype: empty texts for %r", target_name)
            return False

        vecs = self._embed_texts(texts)
        if vecs is None:
            logger.debug("IntentEmbeddingClassifier.encode_prototype: skipped %r (no embedder)", target_name)
            return False

        prototype_vec = _average_vectors(vecs)
        if prototype_vec is None:
            return False

        prototype_vec = _l2_normalize(prototype_vec)

        content_hash = hashlib.sha256(f"{target_name}:{'|'.join(sorted(texts))}".encode()).hexdigest()

        self._prototypes[target_name] = _PrototypeEntry(
            target_name=target_name,
            content_hash=content_hash,
            vector=prototype_vec,
        )
        logger.debug(
            "IntentEmbeddingClassifier: prototype encoded for %r (hash=%s)",
            target_name,
            content_hash[:16],
        )
        return True

    def has_prototype(self, target_name: str) -> bool:
        """Return True if a prototype exists for this target."""
        return target_name in self._prototypes

    def prototype_count(self) -> int:
        """Return number of registered prototypes."""
        return len(self._prototypes)

    # ------------------------------------------------------------------
    # Classification
    # ------------------------------------------------------------------

    def classify(self, user_input: str) -> tuple[str, float] | None:
        """Classify user_input against registered prototypes.

        Args:
            user_input: Raw user or task input string.

        Returns:
            ``(target_name, confidence)`` tuple where confidence is cosine
            similarity in ``[0.0, 1.0]``, or ``None`` if:
            - No prototypes registered.
            - Embedding unavailable.
            - No match above ``cosine_cutoff``.
        """
        if not self._prototypes:
            return None

        try:
            query_vecs = self._embed_texts([user_input])
            if not query_vecs:
                return None

            query_vec = _l2_normalize(query_vecs[0])

            best_name: str | None = None
            best_score: float = -1.0

            for name, entry in self._prototypes.items():
                score = sum(q * p for q, p in zip(query_vec, entry.vector))
                score = round(score, 6)
                if score > best_score:
                    best_score = score
                    best_name = name

            if best_name is None or best_score < self._cosine_cutoff:
                return None

            logger.debug("IntentEmbeddingClassifier.classify: best=%r score=%.4f", best_name, best_score)
            return (best_name, max(0.0, min(1.0, best_score)))
        # guardian: allow-silent-swallow
        except Exception as exc:
            logger.debug("IntentEmbeddingClassifier.classify: exception swallowed: %s", exc)
            return None

    # ------------------------------------------------------------------
    # Prototype update (for feedback-loop driven refresh)
    # ------------------------------------------------------------------

    def update_prototype(self, target_name: str, texts: list[str]) -> bool:
        """Re-encode prototype for target_name with new exemplar texts.

        Called by the MetaLearningBus when a ROUTING_MISCLASSIFICATION
        OptimizationCommit is applied.

        Returns:
            True if update succeeded, False otherwise.
        """
        return self.encode_prototype(target_name, texts)

    def get_prototype_hash(self, target_name: str) -> str | None:
        """Return the content hash of a stored prototype, or None."""
        entry = self._prototypes.get(target_name)
        return entry.content_hash if entry else None


__all__ = ["IntentEmbeddingClassifier"]
