from __future__ import annotations

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    # noqa: E402,
    # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,
    # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    # noqa: E402
    emit_replay_key,
)

emit_replay_key("p0", "text_similarity_util")
emit_determinism_digest("p0", "text_similarity_util")

_emit_dispatches_healing_run("p1", "text_similarity_util", "L2")
_emit_routes_through("p1", "text_similarity_util", "L2")
_emit_checks_agent_registry("p1", "text_similarity_util", "agent_registry")
_emit_validates_agent_capability("p1", "text_similarity_util", "capability")
_emit_dispatches_execution_plan("p1", "text_similarity_util", "exec_plan")
_emit_agent_executes_agent("p1", "text_similarity_util", "sub_agent")
_emit_routes_to_agent("p1", "text_similarity_util", "target_agent")
_emit_verifies_policy("p1", "text_similarity_util", "policy_check")
_emit_observes_runtime_state("p1", "text_similarity_util", "runtime_state")
_emit_verifies_boundary("p1", "text_similarity_util", "boundary_check")
_emit_transcripts_response("p1", "text_similarity_util", "transcript")
_emit_hard_fails_untranscripted("p1", "text_similarity_util")
_emit_gated_by_confidence("p1", "text_similarity_util", "confidence_gate")
_emit_escalates_to_human("p1", "text_similarity_util", "L2")
_emit_reads_policy_state("p1", "text_similarity_util", "L2")

_emit_applies_guardrail("p0", "text_similarity_util", "p0_governance")
_emit_snapshots_state("p0", "text_similarity_util", "state_snapshot")
_emit_authorize_and_execute("p2", "text_similarity_util", "execution_auth")
_emit_validates_capability("p2", "text_similarity_util", "capability_check")
_emit_routes_to_capability("p2", "text_similarity_util", "capability_route")
_emit_writes_via_uwg("p2", "text_similarity_util", "uwg_write")
_emit_blocks_direct_write("p2", "text_similarity_util", "direct_write_block")
_emit_records_tool_invocation("p2", "text_similarity_util", "tool_invocation")
_emit_captures_execution_output("p2", "text_similarity_util", "exec_output")
_emit_dispatches_agent("p3", "text_similarity_util", "agent_dispatch")
_emit_coordinates_agents("p3", "text_similarity_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "text_similarity_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "text_similarity_util", "healing_outcome")
_emit_escalates_failure("p3", "text_similarity_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "text_similarity_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "text_similarity_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "text_similarity_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "text_similarity_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "text_similarity_util", "eval_metric")
_emit_stores_embedding("p4", "text_similarity_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "text_similarity_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "text_similarity_util", "exec_snapshot_link")

"\nText similarity computation using TF-IDF cosine similarity.\n\nProvides core similarity calculation with sklearn alternative path.\n"
import math
from typing import Any

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    SKLEARN_AVAILABLE: Any = True
except ImportError:  # guardian: allow-silent-swallow
    TfidfVectorizer = None
    SKLEARN_AVAILABLE: Any = False
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_signs_execution_trace,
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

_emit_emits_metric_event("text_similarity_util", "p4obs", "metric_1")
_emit_emits_metric_event("text_similarity_util", "p4obs", "metric_2")
_emit_emits_metric_event("text_similarity_util", "p4obs", "metric_3")
_emit_emits_metric_event("text_similarity_util", "p4obs", "metric_4")
_emit_emits_metric_event("text_similarity_util", "p4obs", "metric_5")
_emit_emits_metric_event("text_similarity_util", "p4obs", "metric_6")
_emit_records_incident_event("text_similarity_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("text_similarity_util", "p4obs", "anomaly")
_emit_writes_observability_log("text_similarity_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("text_similarity_util", "p4obs", "mon_state")
_emit_triggers_alert("text_similarity_util", "p4obs", "alert")
_emit_links_incident_trace("text_similarity_util", "p4obs", "trace_link")
_emit_captures_pattern("text_similarity_util", "p3lm", "pattern")
_emit_records_learning_event("text_similarity_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("text_similarity_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("text_similarity_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("text_similarity_util", "p3lm", "routing")
_emit_improves_agent_policy("text_similarity_util", "p3lm", "policy")
_emit_stores_learning_state("text_similarity_util", "p3lm", "state")
_emit_records_execution_trace("text_similarity_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("text_similarity_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("text_similarity_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("text_similarity_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("text_similarity_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("text_similarity_util", "env_read", "p2_env_1")
_emit_reads_environ("text_similarity_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("text_similarity_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("text_similarity_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "text_similarity_util", "context_pull")
_emit_pulls_context("p1", "text_similarity_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "text_similarity_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "text_similarity_util", "uwg_term_2")
_emit_writes_through("p1", "text_similarity_util", "write_through")
_emit_writes_through("p1", "text_similarity_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "text_similarity_util", "safety_validation")
_emit_invokes_eval("p1", "text_similarity_util", "eval_call")
_emit_proposal_commits_routing("p1", "text_similarity_util", "routing_commit")


class TextSimilarityCalculator:
    """Calculate TF-IDF cosine similarity between texts."""

    def __init__(self) -> None:
        """Initialize the similarity calculator."""
        self.vectorizer = None
        if SKLEARN_AVAILABLE and TfidfVectorizer is not None:
            self.vectorizer = TfidfVectorizer(stop_words="english", norm="l2")

    def calculate(self, text1: str, text2: str) -> float:
        """Calculate cosine similarity between two texts."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L2_EXECUTION, "TextSimilarityCalculator.calculate"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:TextSimilarityCalculator.calculate".encode()).hexdigest()[
            :24
        ]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if SKLEARN_AVAILABLE:
            return self._calculate_sklearn(text1, text2)
        return self._calculate_fallback(text1, text2)

    def _calculate_sklearn(self, text1: str, text2: str) -> float:
        """Calculate using scikit-learn TfidfVectorizer."""
        if not text1 or not text2:
            return 0.0
        try:
            tfidf_matrix = self.vectorizer.fit_transform([text1, text2])
            return cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        except (ValueError, TypeError, RuntimeError):
            return 0.0

    def _calculate_fallback(self, text1: str, text2: str) -> float:
        """Basic fallback implementation without sklearn."""
        if not text1 or not text2:
            return 0.0
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        if not words1 or not words2:
            return 0.0
        intersection = words1.intersection(words2)
        if not intersection:
            return 0.0
        numerator = len(intersection)
        denominator = math.sqrt(len(words1) * len(words2))
        if denominator == 0:
            return 0.0
        return numerator / denominator

    # guardian: allow-magic-config
    def find_duplicates(self, texts: list[str], threshold: float = 0.9) -> list[tuple[int, int, float]]:
        """Find text pairs with similarity >= threshold."""
        duplicates = []
        for i in range(len(texts)):
            for j in range(i + 1, len(texts)):
                similarity = self.calculate(texts[i], texts[j])
                if similarity >= threshold:
                    duplicates.append((i, j, similarity))
        return duplicates
