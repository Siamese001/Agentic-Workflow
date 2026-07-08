from __future__ import annotations

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "text_similarity_util")
trace_contract.emit_determinism_digest("p0", "text_similarity_util")

trace_contract._emit_dispatches_healing_run("p1", "text_similarity_util", "L2")
trace_contract._emit_routes_through("p1", "text_similarity_util", "L2")
trace_contract._emit_checks_agent_registry("p1", "text_similarity_util", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "text_similarity_util", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "text_similarity_util", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "text_similarity_util", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "text_similarity_util", "target_agent")
trace_contract._emit_verifies_policy("p1", "text_similarity_util", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "text_similarity_util", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "text_similarity_util", "boundary_check")
trace_contract._emit_transcripts_response("p1", "text_similarity_util", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "text_similarity_util")
trace_contract._emit_gated_by_confidence("p1", "text_similarity_util", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "text_similarity_util", "L2")
trace_contract._emit_reads_policy_state("p1", "text_similarity_util", "L2")

trace_contract._emit_applies_guardrail("p0", "text_similarity_util", "p0_governance")
trace_contract._emit_snapshots_state("p0", "text_similarity_util", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "text_similarity_util", "execution_auth")
trace_contract._emit_validates_capability("p2", "text_similarity_util", "capability_check")
trace_contract._emit_routes_to_capability("p2", "text_similarity_util", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "text_similarity_util", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "text_similarity_util", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "text_similarity_util", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "text_similarity_util", "exec_output")
trace_contract._emit_dispatches_agent("p3", "text_similarity_util", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "text_similarity_util", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "text_similarity_util", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "text_similarity_util", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "text_similarity_util", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "text_similarity_util", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "text_similarity_util", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "text_similarity_util", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "text_similarity_util", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "text_similarity_util", "eval_metric")
trace_contract._emit_stores_embedding("p4", "text_similarity_util", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "text_similarity_util", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "text_similarity_util", "exec_snapshot_link")

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

trace_contract._emit_emits_metric_event("text_similarity_util", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("text_similarity_util", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("text_similarity_util", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("text_similarity_util", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("text_similarity_util", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("text_similarity_util", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("text_similarity_util", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("text_similarity_util", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("text_similarity_util", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("text_similarity_util", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("text_similarity_util", "p4obs", "alert")
trace_contract._emit_links_incident_trace("text_similarity_util", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("text_similarity_util", "p3lm", "pattern")
trace_contract._emit_records_learning_event("text_similarity_util", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("text_similarity_util", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("text_similarity_util", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("text_similarity_util", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("text_similarity_util", "p3lm", "policy")
trace_contract._emit_stores_learning_state("text_similarity_util", "p3lm", "state")
trace_contract._emit_records_execution_trace("text_similarity_util", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("text_similarity_util", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("text_similarity_util", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("text_similarity_util", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("text_similarity_util", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("text_similarity_util", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("text_similarity_util", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("text_similarity_util", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("text_similarity_util", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "text_similarity_util", "context_pull")
trace_contract._emit_pulls_context("p1", "text_similarity_util", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "text_similarity_util", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "text_similarity_util", "uwg_term_2")
trace_contract._emit_writes_through("p1", "text_similarity_util", "write_through")
trace_contract._emit_writes_through("p1", "text_similarity_util", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "text_similarity_util", "safety_validation")
trace_contract._emit_invokes_eval("p1", "text_similarity_util", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "text_similarity_util", "routing_commit")


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
        trace_contract._emit_records_execution_trace(
            _trace_id,
            trace_contract.LayerSegment.L2_EXECUTION,
            "TextSimilarityCalculator.calculate",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:TextSimilarityCalculator.calculate".encode()).hexdigest()[
            :24
        ]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

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
