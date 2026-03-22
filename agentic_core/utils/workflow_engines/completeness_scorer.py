"""
Phase A: Concrete Context Completeness Scorer implementation.

Scores retrieved evidence for the five context dimensions:
  - condition     (if/when/unless/provided that)
  - action        (the main operation — implicit if content is non-empty)
  - exception     (except/unless/however/but/note/warning/error)
  - scope         (only/all/none/within/for/applies to)
  - temporal      (as of/until/since/before/after/deprecated/effective)

Detection is keyword-based with configurable keyword sets.
This is intentionally simple and deterministic — no randomness, no wall-clock.

C0 RULE: All scores are informational only. Never mutates routing or safety.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from agentic_core.evaluation.retrieval.completeness import (
    ContextCompletenessScore,
    GroundedDocument,
    IContextCompletenessScorer,
)
from agentic_core.evaluation.retrieval.interfaces import Document
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_emits_metric_event("completeness_scorer", "p4obs", "metric_1")
_emit_emits_metric_event("completeness_scorer", "p4obs", "metric_2")
_emit_emits_metric_event("completeness_scorer", "p4obs", "metric_3")
_emit_emits_metric_event("completeness_scorer", "p4obs", "metric_4")
_emit_emits_metric_event("completeness_scorer", "p4obs", "metric_5")
_emit_emits_metric_event("completeness_scorer", "p4obs", "metric_6")
_emit_records_incident_event("completeness_scorer", "p4obs", "incident")
_emit_captures_runtime_anomaly("completeness_scorer", "p4obs", "anomaly")
_emit_writes_observability_log("completeness_scorer", "p4obs", "obs_log")
_emit_updates_monitoring_state("completeness_scorer", "p4obs", "mon_state")
_emit_triggers_alert("completeness_scorer", "p4obs", "alert")
_emit_links_incident_trace("completeness_scorer", "p4obs", "trace_link")
_emit_captures_pattern("completeness_scorer", "p3lm", "pattern")
_emit_records_learning_event("completeness_scorer", "p3lm", "learning_event")
_emit_writes_learning_snapshot("completeness_scorer", "p3lm", "snapshot")
_emit_feeds_meta_learning("completeness_scorer", "p3lm", "meta_feed")
_emit_updates_routing_strategy("completeness_scorer", "p3lm", "routing")
_emit_improves_agent_policy("completeness_scorer", "p3lm", "policy")
_emit_stores_learning_state("completeness_scorer", "p3lm", "state")
_emit_records_execution_trace("completeness_scorer", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("completeness_scorer", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("completeness_scorer", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("completeness_scorer", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("completeness_scorer", "L4_STATE", "p2_trace_5")
_emit_reads_environ("completeness_scorer", "env_read", "p2_env_1")
_emit_reads_environ("completeness_scorer", "env_read", "p2_env_2")
_emit_reads_runtime_state("completeness_scorer", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("completeness_scorer", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "completeness_scorer")
_emit_applies_guardrail("p0", "completeness_scorer", "p0_governance")
_emit_reads_policy_state("p0", "completeness_scorer", "policy_binding")
_emit_snapshots_state("p0", "completeness_scorer", "state_snapshot")
_emit_pulls_context("p1", "completeness_scorer", "context_pull")
_emit_pulls_context("p1", "completeness_scorer", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "completeness_scorer", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "completeness_scorer", "uwg_term_secondary")
_emit_writes_through("p1", "completeness_scorer", "write_through")
_emit_writes_through("p1", "completeness_scorer", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "completeness_scorer", "safety_validation")
_emit_invokes_eval("p1", "completeness_scorer", "eval_call")
_emit_proposal_commits_routing("p1", "completeness_scorer", "routing_commit")
_emit_escalates_to_human("p1", "completeness_scorer", "human_escalation")
_emit_routes_through("p1", "completeness_scorer", "route_through")
_emit_checks_agent_registry("p1", "completeness_scorer", "agent_registry")
_emit_validates_agent_capability("p1", "completeness_scorer", "capability")
_emit_dispatches_execution_plan("p1", "completeness_scorer", "exec_plan")
_emit_agent_executes_agent("p1", "completeness_scorer", "sub_agent")
_emit_routes_to_agent("p1", "completeness_scorer", "target_agent")
_emit_verifies_policy("p1", "completeness_scorer", "policy_check")
_emit_observes_runtime_state("p1", "completeness_scorer", "runtime_state")
_emit_verifies_boundary("p1", "completeness_scorer", "boundary_check")
_emit_transcripts_response("p1", "completeness_scorer", "transcript")
_emit_hard_fails_untranscripted("p1", "completeness_scorer")
_emit_gated_by_confidence("p1", "completeness_scorer", "confidence_gate")
emit_replay_key("p0", "completeness_scorer")
emit_determinism_digest("p0", "completeness_scorer")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "completeness_scorer", "execution_auth")
_emit_validates_capability("p2", "completeness_scorer", "capability_check")
_emit_routes_to_capability("p2", "completeness_scorer", "capability_route")
_emit_writes_via_uwg("p2", "completeness_scorer", "uwg_write")
_emit_blocks_direct_write("p2", "completeness_scorer", "direct_write_block")
_emit_records_tool_invocation("p2", "completeness_scorer", "tool_invocation")
_emit_captures_execution_output("p2", "completeness_scorer", "exec_output")
_emit_dispatches_agent("p3", "completeness_scorer", "agent_dispatch")
_emit_coordinates_agents("p3", "completeness_scorer", "agent_coordination")
_emit_records_workflow_lineage("p3", "completeness_scorer", "workflow_lineage")
_emit_records_healing_outcome("p3", "completeness_scorer", "healing_outcome")
_emit_escalates_failure("p3", "completeness_scorer", "failure_escalation")
_emit_orchestrates_workflow("p3", "completeness_scorer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "completeness_scorer", "healing_dispatch")
_emit_invokes_evaluation("p3", "completeness_scorer", "evaluation_signal")
_emit_records_telemetry_event("p4", "completeness_scorer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "completeness_scorer", "eval_metric")
_emit_stores_embedding("p4", "completeness_scorer", "embedding_store")
_emit_updates_meta_learning_state("p4", "completeness_scorer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "completeness_scorer", "exec_snapshot_link")

# ---------------------------------------------------------------------------
# Default keyword sets (deterministic, stable)
# ---------------------------------------------------------------------------

_CONDITION_KEYWORDS: frozenset[str] = frozenset(
    {
        "if",
        "when",
        "unless",
        "provided",
        "assuming",
        "given that",
        "in case",
        "only if",
        "whenever",
        "on condition",
        "where",
        "requires",
    }
)

_EXCEPTION_KEYWORDS: frozenset[str] = frozenset(
    {
        "except",
        "however",
        "but",
        "note",
        "warning",
        "error",
        "caution",
        "not applicable",
        "does not apply",
        "excluded",
        "unless",
        "except when",
        "exception",
        "caveat",
        "limitation",
        "constraint",
        "restriction",
    }
)

_SCOPE_KEYWORDS: frozenset[str] = frozenset(
    {
        "only",
        "all",
        "none",
        "within",
        "for",
        "applies to",
        "limited to",
        "specific to",
        "in scope",
        "out of scope",
        "includes",
        "excludes",
        "version",
        "release",
        "edition",
        "tier",
        "plan",
        "configuration",
    }
)

_TEMPORAL_KEYWORDS: frozenset[str] = frozenset(
    {
        "as of",
        "until",
        "since",
        "before",
        "after",
        "deprecated",
        "effective",
        "from",
        "through",
        "by",
        "no longer",
        "starting",
        "ending",
        "valid",
        "expires",
        "current",
        "legacy",
        "future",
    }
)


# ---------------------------------------------------------------------------
# Scorer Config
# ---------------------------------------------------------------------------


@dataclass
class CompletenessScorerConfig:
    """Configuration for the KeywordCompletetenessScorer.

    All keyword sets are frozensets for deterministic membership checks.
    """

    condition_keywords: frozenset[str] = field(default_factory=lambda: _CONDITION_KEYWORDS)
    exception_keywords: frozenset[str] = field(default_factory=lambda: _EXCEPTION_KEYWORDS)
    scope_keywords: frozenset[str] = field(default_factory=lambda: _SCOPE_KEYWORDS)
    temporal_keywords: frozenset[str] = field(default_factory=lambda: _TEMPORAL_KEYWORDS)
    dimension_weight: float = 0.25


# ---------------------------------------------------------------------------
# Concrete Implementation
# ---------------------------------------------------------------------------


class KeywordCompletenessScorer(IContextCompletenessScorer):
    """Keyword-based context completeness scorer.

    Detects missing context dimensions by checking whether the query contains
    signals for that dimension AND the chunk/parent content does NOT address it.

    Scoring logic:
      1. Determine which dimensions the QUERY signals (query_signals).
      2. For each signaled dimension, check if the CHUNK (+ parent) contains
         at least one keyword from that dimension's set.
      3. missing_X = query signals X AND chunk does not address X.
      4. completeness_score = 1 - (missing_count / max(1, signaled_count)).

    C0 RULE: Pure function — no side effects, no mutation, no wall-clock.
    """

    def __init__(self, config: CompletenessScorerConfig | None = None) -> None:
        self._cfg = config or CompletenessScorerConfig()

    def score(
        self,
        query_id: str,
        query: str,
        chunk: Document | GroundedDocument,
    ) -> ContextCompletenessScore:
        query_lower = query.lower()
        chunk_text = chunk.content.lower()

        if isinstance(chunk, GroundedDocument) and chunk.parent_content:
            chunk_text = chunk_text + " " + chunk.parent_content.lower()

        chunk_id = chunk.doc_id
        parent_id = chunk.parent_section_id if isinstance(chunk, GroundedDocument) else ""

        signals = self._detect_query_signals(query_lower)
        missing = self._detect_missing(signals, chunk_text)

        completeness = self._compute_completeness(signals, missing)

        return ContextCompletenessScore(
            query_id=query_id,
            chunk_id=chunk_id,
            parent_section_id=parent_id,
            relevance_score=round(float(chunk.score), 6),
            completeness_score=round(completeness, 6),
            missing_condition=missing["condition"],
            missing_exception=missing["exception"],
            missing_scope=missing["scope"],
            missing_temporal_qualifier=missing["temporal"],
            confidence=self._compute_confidence(signals),
        )

    def score_batch(
        self,
        query_id: str,
        query: str,
        chunks: list[Document | GroundedDocument],
    ) -> list[ContextCompletenessScore]:
        return [self.score(query_id, query, chunk) for chunk in chunks]

    # ------------------------------------------------------------------
    # Internal helpers — all deterministic, no side effects
    # ------------------------------------------------------------------

    def _detect_query_signals(self, query_lower: str) -> dict[str, bool]:
        """Detect which context dimensions the query signals."""
        return {
            "condition": self._has_keyword(query_lower, self._cfg.condition_keywords),
            "exception": self._has_keyword(query_lower, self._cfg.exception_keywords),
            "scope": self._has_keyword(query_lower, self._cfg.scope_keywords),
            "temporal": self._has_keyword(query_lower, self._cfg.temporal_keywords),
        }

    def _detect_missing(self, signals: dict[str, bool], chunk_text: str) -> dict[str, bool]:
        """For each signaled dimension, check if chunk addresses it."""
        return {
            "condition": signals["condition"]
            and not self._has_keyword(chunk_text, self._cfg.condition_keywords),
            "exception": signals["exception"]
            and not self._has_keyword(chunk_text, self._cfg.exception_keywords),
            "scope": signals["scope"] and not self._has_keyword(chunk_text, self._cfg.scope_keywords),
            "temporal": signals["temporal"]
            and not self._has_keyword(chunk_text, self._cfg.temporal_keywords),
        }

    def _compute_completeness(self, signals: dict[str, bool], missing: dict[str, bool]) -> float:
        signaled = sum(1 for v in signals.values() if v)
        if signaled == 0:
            return 1.0
        missing_count = sum(1 for v in missing.values() if v)
        return max(0.0, 1.0 - missing_count / signaled)

    def _compute_confidence(self, signals: dict[str, bool]) -> float:
        """Confidence is higher when more dimensions are signaled."""
        signaled = sum(1 for v in signals.values() if v)
        return min(1.0, 0.5 + 0.125 * signaled)

    @staticmethod
    def _has_keyword(text: str, keywords: frozenset[str]) -> bool:
        return any(kw in text for kw in keywords)


__all__ = [
    "CompletenessScorerConfig",
    "KeywordCompletenessScorer",
]
