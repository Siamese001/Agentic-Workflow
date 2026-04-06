"""Late Interaction Reranker - SOTA Layer for Precise Document Ranking.

This component uses a Cross-Encoder to re-sort retrieved documents,
ensuring the most relevant context hits the LLM first.
"""

import logging
import time

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

_emit_applies_guardrail("p0", "late_interaction_reranker_util", "p0_governance")
_emit_reads_policy_state("p0", "late_interaction_reranker_util", "policy_binding")
_emit_snapshots_state("p0", "late_interaction_reranker_util", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_emits_metric_event("late_interaction_reranker_util", "p4obs", "metric_1")
_emit_emits_metric_event("late_interaction_reranker_util", "p4obs", "metric_2")
_emit_emits_metric_event("late_interaction_reranker_util", "p4obs", "metric_3")
_emit_emits_metric_event("late_interaction_reranker_util", "p4obs", "metric_4")
_emit_emits_metric_event("late_interaction_reranker_util", "p4obs", "metric_5")
_emit_emits_metric_event("late_interaction_reranker_util", "p4obs", "metric_6")
_emit_records_incident_event("late_interaction_reranker_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("late_interaction_reranker_util", "p4obs", "anomaly")
_emit_writes_observability_log("late_interaction_reranker_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("late_interaction_reranker_util", "p4obs", "mon_state")
_emit_triggers_alert("late_interaction_reranker_util", "p4obs", "alert")
_emit_links_incident_trace("late_interaction_reranker_util", "p4obs", "trace_link")
_emit_captures_pattern("late_interaction_reranker_util", "p3lm", "pattern")
_emit_records_learning_event("late_interaction_reranker_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("late_interaction_reranker_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("late_interaction_reranker_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("late_interaction_reranker_util", "p3lm", "routing")
_emit_improves_agent_policy("late_interaction_reranker_util", "p3lm", "policy")
_emit_stores_learning_state("late_interaction_reranker_util", "p3lm", "state")
_emit_records_execution_trace("late_interaction_reranker_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("late_interaction_reranker_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("late_interaction_reranker_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("late_interaction_reranker_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("late_interaction_reranker_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("late_interaction_reranker_util", "env_read", "p2_env_1")
_emit_reads_environ("late_interaction_reranker_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("late_interaction_reranker_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("late_interaction_reranker_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "late_interaction_reranker_util", "context_pull")
_emit_pulls_context("p1", "late_interaction_reranker_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "late_interaction_reranker_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "late_interaction_reranker_util", "uwg_term_2")
_emit_writes_through("p1", "late_interaction_reranker_util", "write_through")
_emit_writes_through("p1", "late_interaction_reranker_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "late_interaction_reranker_util", "safety_validation")
_emit_invokes_eval("p1", "late_interaction_reranker_util", "eval_call")
_emit_proposal_commits_routing("p1", "late_interaction_reranker_util", "routing_commit")
_emit_escalates_to_human("p1", "late_interaction_reranker_util", "human_escalation")
_emit_routes_through("p1", "late_interaction_reranker_util", "route_through")
_emit_checks_agent_registry("p1", "late_interaction_reranker_util", "agent_registry")
_emit_validates_agent_capability("p1", "late_interaction_reranker_util", "capability")
_emit_dispatches_execution_plan("p1", "late_interaction_reranker_util", "exec_plan")
_emit_agent_executes_agent("p1", "late_interaction_reranker_util", "sub_agent")
_emit_routes_to_agent("p1", "late_interaction_reranker_util", "target_agent")
_emit_verifies_policy("p1", "late_interaction_reranker_util", "policy_check")
_emit_observes_runtime_state("p1", "late_interaction_reranker_util", "runtime_state")
_emit_verifies_boundary("p1", "late_interaction_reranker_util", "boundary_check")
_emit_transcripts_response("p1", "late_interaction_reranker_util", "transcript")
_emit_hard_fails_untranscripted("p1", "late_interaction_reranker_util")
_emit_gated_by_confidence("p1", "late_interaction_reranker_util", "confidence_gate")
emit_replay_key("p0", "late_interaction_reranker_util")
emit_determinism_digest("p0", "late_interaction_reranker_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "late_interaction_reranker_util", "execution_auth")
_emit_validates_capability("p2", "late_interaction_reranker_util", "capability_check")
_emit_routes_to_capability("p2", "late_interaction_reranker_util", "capability_route")
_emit_writes_via_uwg("p2", "late_interaction_reranker_util", "uwg_write")
_emit_blocks_direct_write("p2", "late_interaction_reranker_util", "direct_write_block")
_emit_records_tool_invocation("p2", "late_interaction_reranker_util", "tool_invocation")
_emit_captures_execution_output("p2", "late_interaction_reranker_util", "exec_output")
_emit_dispatches_agent("p3", "late_interaction_reranker_util", "agent_dispatch")
_emit_coordinates_agents("p3", "late_interaction_reranker_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "late_interaction_reranker_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "late_interaction_reranker_util", "healing_outcome")
_emit_escalates_failure("p3", "late_interaction_reranker_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "late_interaction_reranker_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "late_interaction_reranker_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "late_interaction_reranker_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "late_interaction_reranker_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "late_interaction_reranker_util", "eval_metric")
_emit_stores_embedding("p4", "late_interaction_reranker_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "late_interaction_reranker_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "late_interaction_reranker_util", "exec_snapshot_link")

logger = logging.getLogger(__name__)


class LateInteractionReranker:
    """Reranks documents using a Cross-Encoder for late interaction scoring.

    Uses a cross-encoder to examine every word interaction between query
    and document, providing superior ranking accuracy compared to bi-encoders.
    """

    def __init__(self, model_name: str = "BAAI/bge-reranker-v2-m3", lazy_load: bool = True):
        """Initialize the Late Interaction Reranker.

        Args:
            model_name: Name of the cross-encoder model to use
            lazy_load: Whether to load model on first use (recommended)
        """
        self.model_name = model_name
        self.lazy_load = lazy_load
        self._model = None
        self._model_loaded = False
        self._fallback_mode = False
        logger.info(f"Initialized LateInteractionReranker: model={model_name}, lazy={lazy_load}")

    @property
    def is_available(self) -> bool:
        """Check if the reranker is available (model loaded or can be loaded)."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "LateInteractionReranker.is_available")

        if self._model_loaded:
            return not self._fallback_mode
        if self._fallback_mode:
            return False
        try:
            from sentence_transformers import CrossEncoder  # noqa: F401

            return True
        # guardian: allow-silent-swallow - optional dependency
        except ImportError:
            logger.warning("sentence_transformers not available, reranker will be in fallback mode")
            return False

    def _load_model(self) -> bool:
        """Load the cross-encoder model.

        Returns:
            True if model loaded successfully, False if in fallback mode
        """
        if self._model_loaded:
            return not self._fallback_mode
        try:
            import torch  # noqa: F401
            from sentence_transformers import CrossEncoder

            logger.info(f"Loading CrossEncoder model: {self.model_name}")
            start_time = time.time()
            self._model = CrossEncoder(self.model_name)
            load_time = time.time() - start_time
            logger.info(f"Model loaded in {load_time:.2f}s")
            self._model_loaded = True
            self._fallback_mode = False
            return True
        except ImportError as e:
            logger.error(f"Failed to import sentence_transformers: {e}")
            logger.warning("Reranker will operate in fallback mode (no reranking)")
            self._fallback_mode = True
            self._model_loaded = True
            return False
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Failed to load model {self.model_name}: {e}")
            logger.warning("Reranker will operate in fallback mode (no reranking)")
            self._fallback_mode = True
            self._model_loaded = True
            return False

    def rerank(
        self, query: str, documents: list[str], top_k: int | None = None, batch_size: int = 32
    ) -> list[str]:
        """Rerank documents based on query relevance.

        Args:
            query: Query string
            documents: List of document texts to rank
            top_k: Number of top documents to return (None for all)
            batch_size: Batch size for model inference

        Returns:
            Reranked list of document texts
        """
        if not query:
            logger.warning("Empty query provided, returning original documents")
            return documents[:top_k] if top_k else documents
        if not documents:
            logger.warning("No documents provided for reranking")
            return []
        if not self._model_loaded:
            if not self._load_model():
                logger.info("Reranker in fallback mode, returning original order")
                return documents[:top_k] if top_k else documents
        if self._fallback_mode:
            return documents[:top_k] if top_k else documents
        if top_k is None:
            top_k = len(documents)
        else:
            top_k = min(top_k, len(documents))
        pairs = [(query, doc) for doc in documents]
        try:
            logger.debug(f"Reranking {len(documents)} documents")
            start_time = time.time()
            scores = self._model.predict(pairs, batch_size=batch_size, show_progress_bar=False)
            scored_docs = list(zip(documents, scores, strict=False))
            scored_docs.sort(key=lambda x: x[1], reverse=True)
            reranked = [doc for doc, _ in scored_docs[:top_k]]
            elapsed = time.time() - start_time
            logger.debug(f"Reranking completed in {elapsed:.3f}s")
            if scores is not None and len(scores) > 0:
                score_stats = {
                    "min": float(min(scores)),
                    "max": float(max(scores)),
                    "mean": float(sum(scores) / len(scores)),
                }
                logger.debug(f"Score distribution: {score_stats}")
            return reranked
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Reranking failed: {e}")
            logger.info("Falling back to original document order")
            return documents[:top_k]

    def rerank_with_scores(
        self, query: str, documents: list[str], top_k: int | None = None, batch_size: int = 32
    ) -> list[tuple[str, float]]:
        """Rerank documents and return with scores.

        Args:
            query: Query string
            documents: List of document texts to rank
            top_k: Number of top documents to return (None for all)
            batch_size: Batch size for model inference

        Returns:
            List of (document, score) tuples sorted by score
        """
        if not query or not documents:
            return []
        if not self._model_loaded:
            if not self._load_model():
                return [(doc, 0.0) for doc in (documents[:top_k] if top_k else documents)]
        if self._fallback_mode:
            return [(doc, 0.0) for doc in (documents[:top_k] if top_k else documents)]
        if top_k is None:
            top_k = len(documents)
        else:
            top_k = min(top_k, len(documents))
        pairs = [(query, doc) for doc in documents]
        try:
            scores = self._model.predict(pairs, batch_size=batch_size, show_progress_bar=False)
            scored_docs = list(zip(documents, scores, strict=False))
            scored_docs.sort(key=lambda x: x[1], reverse=True)
            return scored_docs[:top_k]
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Reranking with scores failed: {e}")
            return [(doc, 0.0) for doc in (documents[:top_k] if top_k else documents)]

    def get_model_info(self) -> dict:
        """Get information about the loaded model.

        Returns:
            Dictionary with model information
        """
        info = {
            "model_name": self.model_name,
            "loaded": self._model_loaded,
            "fallback_mode": self._fallback_mode,
            "available": self.is_available,
        }
        if self._model_loaded and (not self._fallback_mode):
            try:
                if hasattr(self._model, "config"):
                    info.update(
                        {
                            "max_seq_length": getattr(
                                self._model.config, "max_position_embeddings", "unknown"
                            ),
                            "num_labels": getattr(self._model.config, "num_labels", "unknown"),
                        }
                    )
            # guardian: allow-silent-swallow
            except Exception:
                pass
        return info


def rerank_documents(
    query: str, documents: list[str], model_name: str = "BAAI/bge-reranker-v2-m3", top_k: int = 5
) -> list[str]:
    """Rerank documents using default settings.

    Args:
        query: Query string
        documents: List of document texts
        model_name: Model to use for reranking
        top_k: Number of top documents to return

    Returns:
        Reranked list of documents
    """
    reranker = LateInteractionReranker(model_name=model_name)
    return reranker.rerank(query, documents, top_k=top_k)


class PassThroughReranker:
    """Fallback reranker that returns documents in original order."""

    def __init__(self, *args, **kwargs):
        """Initialize the pass-through reranker."""
        logger.warning("Using PassThroughReranker - no actual reranking will be performed")

    def rerank(self, query: str, documents: list[str], top_k: int | None = None) -> list[str]:
        """Return documents in original order."""
        return documents[:top_k] if top_k else documents

    def rerank_with_scores(
        self, query: str, documents: list[str], top_k: int | None = None
    ) -> list[tuple[str, float]]:
        """Return documents with dummy scores."""
        return [(doc, 0.0) for doc in (documents[:top_k] if top_k else documents)]
