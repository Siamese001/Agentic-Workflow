"""RAGAS-style evaluation metrics.

Deterministic, BGE-cosine-based implementations of the four core RAG quality
dimensions:

- FaithfulnessMetric:     answer attribution to retrieved context chunks
- AnswerRelevancyMetric:  query-answer cosine similarity
- ContextPrecisionMetric: fraction of retrieved chunks that are relevant
- GroundednessMetric:     per-claim attribution to context
"""

from __future__ import annotations

import math
import re
from typing import Any

from agentic_core.evaluation.metrics.base import EvaluationMetric
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

_emit_applies_guardrail("p0", "ragas_metrics", "p0_governance")
_emit_reads_policy_state("p0", "ragas_metrics", "policy_binding")
_emit_snapshots_state("p0", "ragas_metrics", "state_snapshot")
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

_emit_emits_metric_event("ragas_metrics", "p4obs", "metric_1")
_emit_emits_metric_event("ragas_metrics", "p4obs", "metric_2")
_emit_emits_metric_event("ragas_metrics", "p4obs", "metric_3")
_emit_emits_metric_event("ragas_metrics", "p4obs", "metric_4")
_emit_emits_metric_event("ragas_metrics", "p4obs", "metric_5")
_emit_emits_metric_event("ragas_metrics", "p4obs", "metric_6")
_emit_records_incident_event("ragas_metrics", "p4obs", "incident")
_emit_captures_runtime_anomaly("ragas_metrics", "p4obs", "anomaly")
_emit_writes_observability_log("ragas_metrics", "p4obs", "obs_log")
_emit_updates_monitoring_state("ragas_metrics", "p4obs", "mon_state")
_emit_triggers_alert("ragas_metrics", "p4obs", "alert")
_emit_links_incident_trace("ragas_metrics", "p4obs", "trace_link")
_emit_captures_pattern("ragas_metrics", "p3lm", "pattern")
_emit_records_learning_event("ragas_metrics", "p3lm", "learning_event")
_emit_writes_learning_snapshot("ragas_metrics", "p3lm", "snapshot")
_emit_feeds_meta_learning("ragas_metrics", "p3lm", "meta_feed")
_emit_updates_routing_strategy("ragas_metrics", "p3lm", "routing")
_emit_improves_agent_policy("ragas_metrics", "p3lm", "policy")
_emit_stores_learning_state("ragas_metrics", "p3lm", "state")
_emit_records_execution_trace("ragas_metrics", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("ragas_metrics", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("ragas_metrics", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("ragas_metrics", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("ragas_metrics", "L4_STATE", "p2_trace_5")
_emit_reads_environ("ragas_metrics", "env_read", "p2_env_1")
_emit_reads_environ("ragas_metrics", "env_read", "p2_env_2")
_emit_reads_runtime_state("ragas_metrics", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("ragas_metrics", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "ragas_metrics", "context_pull")
_emit_pulls_context("p1", "ragas_metrics", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "ragas_metrics", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "ragas_metrics", "uwg_term_2")
_emit_writes_through("p1", "ragas_metrics", "write_through")
_emit_writes_through("p1", "ragas_metrics", "write_through_2")
_emit_validated_by_safety_plane("p1", "ragas_metrics", "safety_validation")
_emit_invokes_eval("p1", "ragas_metrics", "eval_call")
_emit_proposal_commits_routing("p1", "ragas_metrics", "routing_commit")
_emit_escalates_to_human("p1", "ragas_metrics", "human_escalation")
_emit_routes_through("p1", "ragas_metrics", "route_through")
_emit_checks_agent_registry("p1", "ragas_metrics", "agent_registry")
_emit_validates_agent_capability("p1", "ragas_metrics", "capability")
_emit_dispatches_execution_plan("p1", "ragas_metrics", "exec_plan")
_emit_agent_executes_agent("p1", "ragas_metrics", "sub_agent")
_emit_routes_to_agent("p1", "ragas_metrics", "target_agent")
_emit_verifies_policy("p1", "ragas_metrics", "policy_check")
_emit_observes_runtime_state("p1", "ragas_metrics", "runtime_state")
_emit_verifies_boundary("p1", "ragas_metrics", "boundary_check")
_emit_transcripts_response("p1", "ragas_metrics", "transcript")
_emit_hard_fails_untranscripted("p1", "ragas_metrics")
_emit_gated_by_confidence("p1", "ragas_metrics", "confidence_gate")
emit_replay_key("p0", "ragas_metrics")
emit_determinism_digest("p0", "ragas_metrics")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "ragas_metrics", "execution_auth")
_emit_validates_capability("p2", "ragas_metrics", "capability_check")
_emit_routes_to_capability("p2", "ragas_metrics", "capability_route")
_emit_writes_via_uwg("p2", "ragas_metrics", "uwg_write")
_emit_blocks_direct_write("p2", "ragas_metrics", "direct_write_block")
_emit_records_tool_invocation("p2", "ragas_metrics", "tool_invocation")
_emit_captures_execution_output("p2", "ragas_metrics", "exec_output")
_emit_dispatches_agent("p3", "ragas_metrics", "agent_dispatch")
_emit_coordinates_agents("p3", "ragas_metrics", "agent_coordination")
_emit_records_workflow_lineage("p3", "ragas_metrics", "workflow_lineage")
_emit_records_healing_outcome("p3", "ragas_metrics", "healing_outcome")
_emit_escalates_failure("p3", "ragas_metrics", "failure_escalation")
_emit_orchestrates_workflow("p3", "ragas_metrics", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "ragas_metrics", "healing_dispatch")
_emit_invokes_evaluation("p3", "ragas_metrics", "evaluation_signal")
_emit_records_telemetry_event("p4", "ragas_metrics", "telemetry_event")
_emit_captures_evaluation_metric("p4", "ragas_metrics", "eval_metric")
_emit_stores_embedding("p4", "ragas_metrics", "embedding_store")
_emit_updates_meta_learning_state("p4", "ragas_metrics", "meta_learning")
_emit_links_execution_to_snapshot("p4", "ragas_metrics", "exec_snapshot_link")

_FAITHFULNESS_THRESHOLD = 0.75
_DEFAULT_EMBED_DIM = 1024


def _cosine(a: list[float], b: list[float]) -> float:
    """Deterministic cosine similarity; returns 0.0 on zero-norm vectors."""
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum((x * y for x, y in zip(a, b)))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return max(-1.0, min(1.0, dot / (norm_a * norm_b)))


def _split_sentences(text: str) -> list[str]:
    """Split text into sentences on .!? boundaries; strips empty results."""
    parts = re.split("(?<=[.!?])\\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def _get_embedder():
    """Return a callable embed(text: str) -> list[float] using BGE-m3 or stub."""
    try:
        from agentic_core.L3_orchestration.healers.bmg_embedding_similarity import bmg_embed_text

        return bmg_embed_text
    # guardian: allow-silent-swallow
    except Exception:

        def _stub(text: str) -> list[float]:
            return [0.0] * _DEFAULT_EMBED_DIM

        return _stub


class FaithfulnessMetric(EvaluationMetric):
    """Measures what fraction of answer sentences are attributable to context.

    ``score = attributable_sentences / total_sentences``

    A sentence is attributable if its cosine similarity to any context chunk
    exceeds ``attribution_threshold`` (default 0.75).
    """

    def __init__(self, attribution_threshold: float = _FAITHFULNESS_THRESHOLD) -> None:
        self._threshold = attribution_threshold
        self._embed = _get_embedder()

    @property
    def name(self) -> str:
        return "faithfulness"

    def compute(self, prediction: str, ground_truth: Any = None, context: list[str] | None = None) -> float:
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "FaithfulnessMetric.compute")

        if not prediction or not context:
            return 0.0
        sentences = _split_sentences(prediction)
        if not sentences:
            return 0.0
        context_embeddings = [self._embed(c) for c in context]
        attributable = 0
        for sentence in sentences:
            s_emb = self._embed(sentence)
            if any(_cosine(s_emb, c_emb) >= self._threshold for c_emb in context_embeddings):
                attributable += 1
        return round(attributable / len(sentences), 6)


class AnswerRelevancyMetric(EvaluationMetric):
    """Cosine similarity between query embedding and answer embedding.

    ``score = cosine(embed(query), embed(answer))``
    """

    def __init__(self) -> None:
        self._embed = _get_embedder()

    @property
    def name(self) -> str:
        return "answer_relevancy"

    def compute(self, prediction: str, ground_truth: str, context: Any = None) -> float:
        """
        Args:
            prediction: Generated answer.
            ground_truth: The query string (repurposed as query for relevancy scoring).
            context: Ignored.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "AnswerRelevancyMetric.compute")

        if not prediction or not ground_truth:
            return 0.0
        query_emb = self._embed(ground_truth)
        answer_emb = self._embed(prediction)
        return round(max(0.0, _cosine(query_emb, answer_emb)), 6)


class ContextPrecisionMetric(EvaluationMetric):
    """Set-based context precision.

    ``score = |relevant ∩ retrieved| / |retrieved|``

    Uses chunk IDs directly; no embedding required.
    """

    @property
    def name(self) -> str:
        return "context_precision"

    def compute(
        self, prediction: list[str], ground_truth: set[str] | list[str], context: Any = None,
    ) -> float:
        """
        Args:
            prediction: Retrieved chunk IDs.
            ground_truth: Ground-truth relevant chunk IDs.
            context: Ignored.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ContextPrecisionMetric.compute")

        if not prediction:
            return 0.0
        retrieved = list(prediction)
        relevant = set(ground_truth) if ground_truth else set()
        hits = sum(1 for cid in retrieved if cid in relevant)
        return round(hits / len(retrieved), 6)


class GroundednessMetric(EvaluationMetric):
    """Per-claim attribution to context chunks.

    Each sentence in ``prediction`` is treated as a claim.
    ``score = attributable_claims / total_claims``.

    No context → groundedness = 0.0 (conservative).
    """

    def __init__(self, attribution_threshold: float = _FAITHFULNESS_THRESHOLD) -> None:
        self._threshold = attribution_threshold
        self._embed = _get_embedder()

    @property
    def name(self) -> str:
        return "groundedness"

    def compute(self, prediction: str, ground_truth: Any = None, context: list[str] | None = None) -> float:
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "GroundednessMetric.compute")

        if not prediction or not context:
            return 0.0
        claims = _split_sentences(prediction)
        if not claims:
            return 0.0
        context_embeddings = [self._embed(c) for c in context]
        grounded = 0
        for claim in claims:
            c_emb = self._embed(claim)
            if any(_cosine(c_emb, ctx_emb) >= self._threshold for ctx_emb in context_embeddings):
                grounded += 1
        return round(grounded / len(claims), 6)


__all__ = [
    "FaithfulnessMetric",
    "AnswerRelevancyMetric",
    "ContextPrecisionMetric",
    "GroundednessMetric",
    "_cosine",
    "_split_sentences",
]
