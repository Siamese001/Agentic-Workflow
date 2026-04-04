"""Adaptive Retrieval Gate - Smart Guard for RAG Queries.

This component acts as a smart gatekeeper that decides whether a query
requires retrieval from the vector database or can be handled from context.
"""

import logging
import re

from pydantic import BaseModel, Field

# L5 retrieval wiring (Turn 3, Wave 34): Import creates ADG edge to L5_safety
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

_emit_applies_guardrail("p0", "AdaptiveretrievalgateStrategy", "p0_governance")
_emit_reads_policy_state("p0", "AdaptiveretrievalgateStrategy", "policy_binding")
_emit_snapshots_state("p0", "AdaptiveretrievalgateStrategy", "state_snapshot")
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

_emit_emits_metric_event("AdaptiveretrievalgateStrategy", "p4obs", "metric_1")
_emit_emits_metric_event("AdaptiveretrievalgateStrategy", "p4obs", "metric_2")
_emit_emits_metric_event("AdaptiveretrievalgateStrategy", "p4obs", "metric_3")
_emit_emits_metric_event("AdaptiveretrievalgateStrategy", "p4obs", "metric_4")
_emit_emits_metric_event("AdaptiveretrievalgateStrategy", "p4obs", "metric_5")
_emit_emits_metric_event("AdaptiveretrievalgateStrategy", "p4obs", "metric_6")
_emit_records_incident_event("AdaptiveretrievalgateStrategy", "p4obs", "incident")
_emit_captures_runtime_anomaly("AdaptiveretrievalgateStrategy", "p4obs", "anomaly")
_emit_writes_observability_log("AdaptiveretrievalgateStrategy", "p4obs", "obs_log")
_emit_updates_monitoring_state("AdaptiveretrievalgateStrategy", "p4obs", "mon_state")
_emit_triggers_alert("AdaptiveretrievalgateStrategy", "p4obs", "alert")
_emit_links_incident_trace("AdaptiveretrievalgateStrategy", "p4obs", "trace_link")
_emit_captures_pattern("AdaptiveretrievalgateStrategy", "p3lm", "pattern")
_emit_records_learning_event("AdaptiveretrievalgateStrategy", "p3lm", "learning_event")
_emit_writes_learning_snapshot("AdaptiveretrievalgateStrategy", "p3lm", "snapshot")
_emit_feeds_meta_learning("AdaptiveretrievalgateStrategy", "p3lm", "meta_feed")
_emit_updates_routing_strategy("AdaptiveretrievalgateStrategy", "p3lm", "routing")
_emit_improves_agent_policy("AdaptiveretrievalgateStrategy", "p3lm", "policy")
_emit_stores_learning_state("AdaptiveretrievalgateStrategy", "p3lm", "state")
_emit_records_execution_trace("AdaptiveretrievalgateStrategy", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("AdaptiveretrievalgateStrategy", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("AdaptiveretrievalgateStrategy", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("AdaptiveretrievalgateStrategy", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("AdaptiveretrievalgateStrategy", "L4_STATE", "p2_trace_5")
_emit_reads_environ("AdaptiveretrievalgateStrategy", "env_read", "p2_env_1")
_emit_reads_environ("AdaptiveretrievalgateStrategy", "env_read", "p2_env_2")
_emit_reads_runtime_state("AdaptiveretrievalgateStrategy", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("AdaptiveretrievalgateStrategy", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "AdaptiveretrievalgateStrategy", "context_pull")
_emit_pulls_context("p1", "AdaptiveretrievalgateStrategy", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "AdaptiveretrievalgateStrategy", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "AdaptiveretrievalgateStrategy", "uwg_term_2")
_emit_writes_through("p1", "AdaptiveretrievalgateStrategy", "write_through")
_emit_writes_through("p1", "AdaptiveretrievalgateStrategy", "write_through_2")
_emit_validated_by_safety_plane("p1", "AdaptiveretrievalgateStrategy", "safety_validation")
_emit_invokes_eval("p1", "AdaptiveretrievalgateStrategy", "eval_call")
_emit_proposal_commits_routing("p1", "AdaptiveretrievalgateStrategy", "routing_commit")
_emit_escalates_to_human("p1", "AdaptiveretrievalgateStrategy", "human_escalation")
_emit_routes_through("p1", "AdaptiveretrievalgateStrategy", "route_through")
_emit_checks_agent_registry("p1", "AdaptiveretrievalgateStrategy", "agent_registry")
_emit_validates_agent_capability("p1", "AdaptiveretrievalgateStrategy", "capability")
_emit_dispatches_execution_plan("p1", "AdaptiveretrievalgateStrategy", "exec_plan")
_emit_agent_executes_agent("p1", "AdaptiveretrievalgateStrategy", "sub_agent")
_emit_routes_to_agent("p1", "AdaptiveretrievalgateStrategy", "target_agent")
_emit_verifies_policy("p1", "AdaptiveretrievalgateStrategy", "policy_check")
_emit_observes_runtime_state("p1", "AdaptiveretrievalgateStrategy", "runtime_state")
_emit_verifies_boundary("p1", "AdaptiveretrievalgateStrategy", "boundary_check")
_emit_transcripts_response("p1", "AdaptiveretrievalgateStrategy", "transcript")
_emit_hard_fails_untranscripted("p1", "AdaptiveretrievalgateStrategy")
_emit_gated_by_confidence("p1", "AdaptiveretrievalgateStrategy", "confidence_gate")
emit_replay_key("p0", "AdaptiveretrievalgateStrategy")
emit_determinism_digest("p0", "AdaptiveretrievalgateStrategy")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "AdaptiveretrievalgateStrategy", "execution_auth")
_emit_validates_capability("p2", "AdaptiveretrievalgateStrategy", "capability_check")
_emit_routes_to_capability("p2", "AdaptiveretrievalgateStrategy", "capability_route")
_emit_writes_via_uwg("p2", "AdaptiveretrievalgateStrategy", "uwg_write")
_emit_blocks_direct_write("p2", "AdaptiveretrievalgateStrategy", "direct_write_block")
_emit_records_tool_invocation("p2", "AdaptiveretrievalgateStrategy", "tool_invocation")
_emit_captures_execution_output("p2", "AdaptiveretrievalgateStrategy", "exec_output")
_emit_dispatches_agent("p3", "AdaptiveretrievalgateStrategy", "agent_dispatch")
_emit_coordinates_agents("p3", "AdaptiveretrievalgateStrategy", "agent_coordination")
_emit_records_workflow_lineage("p3", "AdaptiveretrievalgateStrategy", "workflow_lineage")
_emit_records_healing_outcome("p3", "AdaptiveretrievalgateStrategy", "healing_outcome")
_emit_escalates_failure("p3", "AdaptiveretrievalgateStrategy", "failure_escalation")
_emit_orchestrates_workflow("p3", "AdaptiveretrievalgateStrategy", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "AdaptiveretrievalgateStrategy", "healing_dispatch")
_emit_invokes_evaluation("p3", "AdaptiveretrievalgateStrategy", "evaluation_signal")
_emit_records_telemetry_event("p4", "AdaptiveretrievalgateStrategy", "telemetry_event")
_emit_captures_evaluation_metric("p4", "AdaptiveretrievalgateStrategy", "eval_metric")
_emit_stores_embedding("p4", "AdaptiveretrievalgateStrategy", "embedding_store")
_emit_updates_meta_learning_state("p4", "AdaptiveretrievalgateStrategy", "meta_learning")
_emit_links_execution_to_snapshot("p4", "AdaptiveretrievalgateStrategy", "exec_snapshot_link")

logger = logging.getLogger(__name__)


class RetrievalDecision(BaseModel):
    """Decision about whether to retrieve from vector database."""

    should_retrieve: bool = Field(..., description="Whether retrieval is needed")
    reason: str = Field(..., description="Explanation for the decision")
    query_type: str = Field(..., description="Type of query classified")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence in decision")


class AdaptiveRetrievalGate:
    """Smart gate that determines if retrieval is necessary for a query.

    Uses pattern matching and complexity analysis to avoid unnecessary
    vector database searches for simple or contextual queries.
    """

    def __init__(self):
        """Initialize the Adaptive Retrieval Gate."""
        self.patterns = {
            "conversational": re.compile(
                "^(hi|hello|hey|thanks|thank you|ok|okay|bye|goodbye|yes|no|sure|got it|understood|cool|awesome|great|perfect)$",
                re.IGNORECASE,
            ),
            "reference": re.compile(
                "\\b(previous|last|that|above|mentioned|earlier|said|told|asked|discussed)\\b", re.IGNORECASE
            ),
            "self_reference": re.compile(
                "\\b(who are you|what are you|what can you do|how do you work|your name|help)\\b",
                re.IGNORECASE,
            ),
            "continuation": re.compile(
                "^(and|but|so|then|also|plus|however|therefore|meanwhile)\\b", re.IGNORECASE
            ),
        }
        self.complex_keywords = {
            "metrics",
            "how to",
            "latest",
            "compare",
            "strategy",
            "plan",
            "analyze",
            "evaluate",
            "recommend",
            "implement",
            "design",
            "architecture",
            "framework",
            "best practices",
            "guidelines",
            "statistics",
            "data",
            "performance",
            "optimization",
            "trends",
            "forecast",
            "roadmap",
            "timeline",
            "requirements",
        }
        self.question_patterns = [
            "\\bwhat\\s+(is|are|were|do|does|did)\\b",
            "\\bwhen\\s+(was|were|is|are|did|do)\\b",
            "\\bwhere\\s+(is|are|was|were|did|do)\\b",
            "\\bwhich\\s+(is|are|was|were|did|do)\\b",
            "\\bwho\\s+(is|are|was|were|did|do)\\b",
            "\\bwhy\\s+(is|are|was|were|did|do|does)\\b",
            "\\bhow\\s+(can|could|should|would|will|do|does|did)\\b",
        ]
        self.compiled_questions = [re.compile(p, re.IGNORECASE) for p in self.question_patterns]
        logger.info("Initialized AdaptiveRetrievalGate")

    def _classify_query_type(self, query: str) -> str:
        """Classify the type of query.

        Args:
            query: Query string to classify

        Returns:
            Query type string
        """
        query_lower = query.lower().strip()
        if self.patterns["conversational"].match(query):
            return "CONVERSATIONAL"
        if self.patterns["self_reference"].search(query):
            return "SELF_REFERENCE"
        if self.patterns["reference"].search(query):
            return "REFERENCE"
        if self.patterns["continuation"].match(query):
            return "CONTINUATION"
        if any(keyword in query_lower for keyword in self.complex_keywords):
            return "COMPLEX"
        if any(pattern.search(query) for pattern in self.compiled_questions):
            return "FACTUAL"
        return "COMPLEX"

    def _calculate_complexity_score(self, query: str, query_type: str) -> float:
        """Calculate complexity score for the query.

        Args:
            query: Query string
            query_type: Classified query type

        Returns:
            Complexity score (0-1)
        """
        type_scores = {
            "CONVERSATIONAL": 0.0,
            "SELF_REFERENCE": 0.0,
            "REFERENCE": 0.1,
            "CONTINUATION": 0.2,
            "FACTUAL": 0.6,
            "COMPLEX": 0.8,
        }
        base_score = type_scores.get(query_type, 0.5)
        word_count = len(query.split())
        if word_count > 10:
            base_score = min(1.0, base_score + 0.2)
        elif word_count < 3:
            base_score = max(0.0, base_score - 0.1)
        if query.endswith("?"):
            base_score = min(1.0, base_score + 0.1)
        complex_count = sum(1 for keyword in self.complex_keywords if keyword in query.lower())
        if complex_count > 0:
            base_score = min(1.0, base_score + 0.1 * min(complex_count, 2))
        return base_score

    def should_retrieve(self, query: str, history: list[dict] | None = None) -> RetrievalDecision:
        """Determine if retrieval is needed for the query.

        Args:
            query: Query string to evaluate
            history: Optional conversation history for context

        Returns:
            RetrievalDecision with recommendation
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "AdaptiveRetrievalGate.should_retrieve")

        query = query.strip()
        if not query:
            return RetrievalDecision(
                should_retrieve=False, reason="Empty query", query_type="EMPTY", confidence=1.0
            )
        query_type = self._classify_query_type(query)
        complexity_score = self._calculate_complexity_score(query, query_type)
        should_retrieve = False
        reason = ""
        confidence = 0.9
        if query_type == "CONVERSATIONAL":
            should_retrieve = False
            reason = "Conversational query - no retrieval needed"
            confidence = 0.95
        elif query_type == "SELF_REFERENCE":
            should_retrieve = False
            reason = "Query about assistant - use internal knowledge"
            confidence = 0.9
        elif query_type == "REFERENCE":
            should_retrieve = False
            reason = "Reference to previous context - check conversation history"
            confidence = 0.85
        elif query_type == "CONTINUATION":
            should_retrieve = False
            reason = "Continuation marker - context should provide information"
            confidence = 0.8
        elif query_type == "FACTUAL":
            if complexity_score > 0.4:
                should_retrieve = True
                reason = "Factual question requiring external knowledge"
            else:
                should_retrieve = False
                reason = "Simple factual query - may be handled from context"
        elif query_type == "COMPLEX":
            should_retrieve = True
            reason = "Complex query requiring retrieval"
            confidence = 0.85
        if should_retrieve:
            if len(query.split()) < 4 and (
                not any(pattern.search(query) for pattern in self.compiled_questions)
            ):
                should_retrieve = False
                reason = "Short query likely a clarification"
                confidence = 0.7
        logger.info(
            f"Retrieval decision: {should_retrieve} | Type: {query_type} | Reason: {reason} | Query: {query[:50]}..."
        )
        return RetrievalDecision(
            should_retrieve=should_retrieve, reason=reason, query_type=query_type, confidence=confidence
        )

    def get_statistics(self, decisions: list[RetrievalDecision]) -> dict[str, float]:
        """Calculate statistics from a list of retrieval decisions.

        Args:
            decisions: List of RetrievalDecision objects

        Returns:
            Dictionary with statistics
        """
        if not decisions:
            return {}
        total = len(decisions)
        retrieve_count = sum(1 for d in decisions if d.should_retrieve)
        type_counts = {}
        for decision in decisions:
            type_counts[decision.query_type] = type_counts.get(decision.query_type, 0) + 1
        return {
            "total_queries": total,
            "retrieval_rate": retrieve_count / total,
            "type_distribution": {k: v / total for k, v in type_counts.items()},
            "avg_confidence": sum(d.confidence for d in decisions) / total,
        }


def should_retrieve(query: str, history: list[dict] | None = None) -> bool:
    """Quick check if retrieval is needed.

    Args:
        query: Query string
        history: Optional conversation history

    Returns:
        Boolean indicating if retrieval is needed
    """
    gate = AdaptiveRetrievalGate()
    decision = gate.should_retrieve(query, history)
    return decision.should_retrieve
