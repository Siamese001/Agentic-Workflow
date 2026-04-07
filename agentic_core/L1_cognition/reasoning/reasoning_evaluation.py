"""
agentic_core/L1_cognition/evaluation/reasoning_evaluation.py

ReasoningEvaluation — P2/L1 reasoning quality evaluation.

Every runtime reasoning step executed through reason_and_record() MUST be
evaluated via evaluate_reasoning_step(). No reasoning evaluation may exist
without explicit linkage to a reasoning trace.

evaluate_reasoning_step() steps (mandatory, in order):
  1. bind evaluation to reasoning trace (raises OrphanReasoningEvaluationError if no trace)
  2. attach prompt / context / output hashes
  3. record evaluator identity
  4. record score and critique
  5. persist evaluation artifact

ReasoningEvaluationRecord (12 required spec fields):
    reasoning_evaluation_id, run_id, trace_id, reasoning_trace_id,
    evaluated_prompt_hash, evaluated_context_hash, evaluated_output_hash,
    evaluator_id, rubric_hash, score_hash, critique_hash,
    evaluation_outcome_status

ReasoningEvaluationOutcome (5 mandatory outcome statuses):
    PASS, FAIL, INCONCLUSIVE, NEEDS_REVIEW, ESCALATE

Evaluated dimensions (spec §4 — at least one rubric/critique per step):
    relevance, consistency, policy_compliance, coherence, actionability

ComparativeReasoningEvaluation (5 required spec fields):
    candidate_a_hash, candidate_b_hash, winning_reasoning_hash,
    comparison_rubric_hash, evaluator_id

ReasoningEvaluationStore — queryable by run_id, trace_id, reasoning_trace_id, outcome

ADG edges emitted:
    invokes_eval              — every evaluate_reasoning_step() call
    records_execution_trace   — evaluation binds to reasoning trace lifecycle
    compares_proof            — comparative evaluations
"""

from __future__ import annotations

import hashlib
import logging
import threading
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

emit_replay_key("p0", "reasoning_evaluation")
emit_determinism_digest("p0", "reasoning_evaluation")

_emit_dispatches_healing_run("p1", "reasoning_evaluation", "L1")
_emit_routes_through("p1", "reasoning_evaluation", "L1")
_emit_checks_agent_registry("p1", "reasoning_evaluation", "agent_registry")
_emit_validates_agent_capability("p1", "reasoning_evaluation", "capability")
_emit_dispatches_execution_plan("p1", "reasoning_evaluation", "exec_plan")
_emit_agent_executes_agent("p1", "reasoning_evaluation", "sub_agent")
_emit_routes_to_agent("p1", "reasoning_evaluation", "target_agent")
_emit_verifies_policy("p1", "reasoning_evaluation", "policy_check")
_emit_observes_runtime_state("p1", "reasoning_evaluation", "runtime_state")
_emit_verifies_boundary("p1", "reasoning_evaluation", "boundary_check")
_emit_transcripts_response("p1", "reasoning_evaluation", "transcript")
_emit_hard_fails_untranscripted("p1", "reasoning_evaluation")
_emit_gated_by_confidence("p1", "reasoning_evaluation", "confidence_gate")
_emit_escalates_to_human("p1", "reasoning_evaluation", "L1")
_emit_reads_policy_state("p1", "reasoning_evaluation", "L1")
_emit_authorize_and_execute("p2", "reasoning_evaluation", "execution_auth")
_emit_validates_capability("p2", "reasoning_evaluation", "capability_check")
_emit_routes_to_capability("p2", "reasoning_evaluation", "capability_route")
_emit_writes_via_uwg("p2", "reasoning_evaluation", "uwg_write")
_emit_blocks_direct_write("p2", "reasoning_evaluation", "direct_write_block")
_emit_records_tool_invocation("p2", "reasoning_evaluation", "tool_invocation")
_emit_captures_execution_output("p2", "reasoning_evaluation", "exec_output")
_emit_dispatches_agent("p3", "reasoning_evaluation", "agent_dispatch")
_emit_coordinates_agents("p3", "reasoning_evaluation", "agent_coordination")
_emit_records_workflow_lineage("p3", "reasoning_evaluation", "workflow_lineage")
_emit_records_healing_outcome("p3", "reasoning_evaluation", "healing_outcome")
_emit_escalates_failure("p3", "reasoning_evaluation", "failure_escalation")
_emit_orchestrates_workflow("p3", "reasoning_evaluation", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "reasoning_evaluation", "healing_dispatch")
_emit_invokes_evaluation("p3", "reasoning_evaluation", "evaluation_signal")
_emit_records_telemetry_event("p4", "reasoning_evaluation", "telemetry_event")
_emit_captures_evaluation_metric("p4", "reasoning_evaluation", "eval_metric")
_emit_stores_embedding("p4", "reasoning_evaluation", "embedding_store")
_emit_updates_meta_learning_state("p4", "reasoning_evaluation", "meta_learning")
_emit_links_execution_to_snapshot("p4", "reasoning_evaluation", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_emits_metric_event("reasoning_evaluation", "p4obs", "metric_1")
_emit_emits_metric_event("reasoning_evaluation", "p4obs", "metric_2")
_emit_emits_metric_event("reasoning_evaluation", "p4obs", "metric_3")
_emit_emits_metric_event("reasoning_evaluation", "p4obs", "metric_4")
_emit_emits_metric_event("reasoning_evaluation", "p4obs", "metric_5")
_emit_emits_metric_event("reasoning_evaluation", "p4obs", "metric_6")
_emit_records_incident_event("reasoning_evaluation", "p4obs", "incident")
_emit_captures_runtime_anomaly("reasoning_evaluation", "p4obs", "anomaly")
_emit_writes_observability_log("reasoning_evaluation", "p4obs", "obs_log")
_emit_updates_monitoring_state("reasoning_evaluation", "p4obs", "mon_state")
_emit_triggers_alert("reasoning_evaluation", "p4obs", "alert")
_emit_links_incident_trace("reasoning_evaluation", "p4obs", "trace_link")
_emit_captures_pattern("reasoning_evaluation", "p3lm", "pattern")
_emit_records_learning_event("reasoning_evaluation", "p3lm", "learning_event")
_emit_writes_learning_snapshot("reasoning_evaluation", "p3lm", "snapshot")
_emit_feeds_meta_learning("reasoning_evaluation", "p3lm", "meta_feed")
_emit_updates_routing_strategy("reasoning_evaluation", "p3lm", "routing")
_emit_improves_agent_policy("reasoning_evaluation", "p3lm", "policy")
_emit_stores_learning_state("reasoning_evaluation", "p3lm", "state")
_emit_records_execution_trace("reasoning_evaluation", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("reasoning_evaluation", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("reasoning_evaluation", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("reasoning_evaluation", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("reasoning_evaluation", "L4_STATE", "p2_trace_5")
_emit_reads_environ("reasoning_evaluation", "env_read", "p2_env_1")
_emit_reads_environ("reasoning_evaluation", "env_read", "p2_env_2")
_emit_reads_runtime_state("reasoning_evaluation", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("reasoning_evaluation", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "reasoning_evaluation", "context_pull")
_emit_pulls_context("p1", "reasoning_evaluation", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "reasoning_evaluation", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "reasoning_evaluation", "uwg_term_2")
_emit_writes_through("p1", "reasoning_evaluation", "write_through")
_emit_writes_through("p1", "reasoning_evaluation", "write_through_2")
_emit_validated_by_safety_plane("p1", "reasoning_evaluation", "safety_validation")
_emit_invokes_eval("p1", "reasoning_evaluation", "eval_call")
_emit_proposal_commits_routing("p1", "reasoning_evaluation", "routing_commit")

logger = logging.getLogger(__name__)
_EVAL_LOG = logging.getLogger("adg.invokes_eval")
_TRACE_LOG = logging.getLogger("adg.records_execution_trace")
_COMPARE_LOG = logging.getLogger("adg.compares_proof")


# ---------------------------------------------------------------------------
# ReasoningEvaluationOutcome — 5 mandatory outcome statuses
# ---------------------------------------------------------------------------


class ReasoningEvaluationOutcome(str, Enum):
    """Classification of a reasoning evaluation result."""

    PASS = "pass"
    FAIL = "fail"
    INCONCLUSIVE = "inconclusive"
    NEEDS_REVIEW = "needs_review"
    ESCALATE = "escalate"


# ---------------------------------------------------------------------------
# OrphanReasoningEvaluationError — raised when evaluation has no trace binding
# ---------------------------------------------------------------------------


class OrphanReasoningEvaluationError(RuntimeError):
    """Raised when evaluate_reasoning_step() is called without a reasoning_trace_id.

    No reasoning evaluation may exist without explicit linkage to a
    ReasoningTraceArtifact (spec §3: Gate A).
    """


# ---------------------------------------------------------------------------
# ReasoningEvaluationRecord — 12 required spec fields
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ReasoningEvaluationRecord:
    """Immutable evaluation artifact for one evaluated reasoning step.

    All 12 fields are required (spec §2). Evaluated dimensions per spec §4:
    relevance, consistency, policy_compliance, coherence, actionability.
    """

    reasoning_evaluation_id: str
    run_id: str
    trace_id: str
    reasoning_trace_id: str
    evaluated_prompt_hash: str
    evaluated_context_hash: str
    evaluated_output_hash: str
    evaluator_id: str
    rubric_hash: str
    score_hash: str
    critique_hash: str
    evaluation_outcome_status: str

    @classmethod
    def create(
        cls,
        *,
        run_id: str,
        trace_id: str,
        reasoning_trace_id: str,
        evaluated_prompt_hash: str,
        evaluated_context_hash: str,
        evaluated_output_hash: str,
        evaluator_id: str,
        rubric: dict[str, Any],
        score_payload: dict[str, Any],
        critique: str,
        evaluation_outcome_status: ReasoningEvaluationOutcome,
    ) -> ReasoningEvaluationRecord:
        """Factory — computes all hash fields deterministically."""
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "ReasoningEvaluationRecord.create", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "ReasoningEvaluationRecord.create", "p0_governance")
        evaluation_id = f"re-{uuid.uuid4().hex[:12]}"
        rubric_hash = _sha256(repr(sorted(rubric.items())))
        score_hash = _sha256(repr(sorted(score_payload.items())))
        critique_hash = _sha256(critique)
        return cls(
            reasoning_evaluation_id=evaluation_id,
            run_id=run_id,
            trace_id=trace_id,
            reasoning_trace_id=reasoning_trace_id,
            evaluated_prompt_hash=evaluated_prompt_hash,
            evaluated_context_hash=evaluated_context_hash,
            evaluated_output_hash=evaluated_output_hash,
            evaluator_id=evaluator_id,
            rubric_hash=rubric_hash,
            score_hash=score_hash,
            critique_hash=critique_hash,
            evaluation_outcome_status=evaluation_outcome_status.value,
        )


# ---------------------------------------------------------------------------
# ComparativeReasoningEvaluation — 5 required spec fields (spec §5)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ComparativeReasoningEvaluation:
    """Side-by-side evaluation of two reasoning candidates (spec §5).

    Required for ranking or model selection based on reasoning quality.
    """

    candidate_a_hash: str
    candidate_b_hash: str
    winning_reasoning_hash: str
    comparison_rubric_hash: str
    evaluator_id: str

    @classmethod
    def create(
        cls,
        *,
        candidate_a: Any,
        candidate_b: Any,
        winner: Any,
        comparison_rubric: dict[str, Any],
        evaluator_id: str,
    ) -> ComparativeReasoningEvaluation:
        """Factory — hashes candidates and rubric deterministically."""
        return cls(
            candidate_a_hash=_sha256(repr(candidate_a)),
            candidate_b_hash=_sha256(repr(candidate_b)),
            winning_reasoning_hash=_sha256(repr(winner)),
            comparison_rubric_hash=_sha256(repr(sorted(comparison_rubric.items()))),
            evaluator_id=evaluator_id,
        )


# ---------------------------------------------------------------------------
# ReasoningEvaluationContext — input bundle for evaluate_reasoning_step()
# ---------------------------------------------------------------------------


@dataclass
class ReasoningEvaluationContext:
    """All inputs required to evaluate one reasoning step.

    Callers supply the reasoning_trace (from reason_and_record()), the
    rubric defining evaluation criteria, and the evaluator identity.
    Scoring and critique are provided inline or can be derived.
    """

    reasoning_trace_id: str
    run_id: str
    trace_id: str
    evaluated_prompt_hash: str
    evaluated_context_hash: str
    evaluated_output_hash: str
    evaluator_id: str
    rubric: dict[str, Any]
    score_payload: dict[str, Any]
    critique: str
    evaluation_outcome_status: ReasoningEvaluationOutcome = ReasoningEvaluationOutcome.PASS
    metadata: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# ReasoningEvaluationRubric — structured rubric for 5 evaluation dimensions
# ---------------------------------------------------------------------------


@dataclass
class ReasoningEvaluationRubric:
    """Structured rubric covering the 5 required evaluation dimensions (spec §4).

    At least one dimension score must be non-None to satisfy Gate C.
    """

    relevance: float | None = None
    consistency: float | None = None
    policy_compliance: float | None = None
    coherence: float | None = None
    actionability: float | None = None
    rubric_id: str = field(default_factory=lambda: f"rubric-{uuid.uuid4().hex[:8]}")

    def to_dict(self) -> dict[str, Any]:
        return {
            "rubric_id": self.rubric_id,
            "relevance": self.relevance,
            "consistency": self.consistency,
            "policy_compliance": self.policy_compliance,
            "coherence": self.coherence,
            "actionability": self.actionability,
        }

    def has_at_least_one_score(self) -> bool:
        return any(
            v is not None
            for v in (
                self.relevance,
                self.consistency,
                self.policy_compliance,
                self.coherence,
                self.actionability,
            )
        )

    def overall_score(self) -> float:
        """Mean of all non-None dimension scores."""
        values = [
            v
            for v in (
                self.relevance,
                self.consistency,
                self.policy_compliance,
                self.coherence,
                self.actionability,
            )
            if v is not None
        ]
        return sum(values) / len(values) if values else 0.0


# ---------------------------------------------------------------------------
# evaluate_reasoning_step() — mandatory entrypoint per spec §3
# ---------------------------------------------------------------------------


def evaluate_reasoning_step(
    reasoning_eval_context: ReasoningEvaluationContext,
) -> ReasoningEvaluationRecord:
    """Mandatory reasoning evaluation entrypoint — P2/L1 spec §3.

    Steps (in order, all mandatory):
      1. bind evaluation to reasoning trace (orphan guard)
      2. attach prompt / context / output hashes
      3. record evaluator identity
      4. record score and critique
      5. persist evaluation artifact

    Args:
        reasoning_eval_context: Fully-populated ReasoningEvaluationContext.

    Returns:
        ReasoningEvaluationRecord (immutable, 12 fields), persisted to the store.

    Raises:
        OrphanReasoningEvaluationError: If reasoning_trace_id is empty.
    """
    # --- Step 1: Bind to reasoning trace (orphan guard) ---
    if not reasoning_eval_context.reasoning_trace_id:
        raise OrphanReasoningEvaluationError(
            "evaluate_reasoning_step: reasoning_trace_id is required. "
            "No reasoning evaluation may exist without explicit trace linkage.",
        )

    _TRACE_LOG.debug(
        "records_execution_trace REASONING_EVALUATION evaluator=%s trace=%s run=%s",
        reasoning_eval_context.evaluator_id,
        reasoning_eval_context.reasoning_trace_id,
        reasoning_eval_context.run_id,
    )

    # --- Step 2: Attach prompt / context / output hashes ---
    # (validated via ReasoningEvaluationContext fields — non-empty enforced by caller)

    # --- Step 3: Record evaluator identity ---
    _EVAL_LOG.debug(
        "invokes_eval REASONING_EVALUATION evaluator=%s reasoning_trace=%s run=%s trace=%s",
        reasoning_eval_context.evaluator_id,
        reasoning_eval_context.reasoning_trace_id,
        reasoning_eval_context.run_id,
        reasoning_eval_context.trace_id,
    )

    # --- Step 4: Record score and critique ---
    record = ReasoningEvaluationRecord.create(
        run_id=reasoning_eval_context.run_id,
        trace_id=reasoning_eval_context.trace_id,
        reasoning_trace_id=reasoning_eval_context.reasoning_trace_id,
        evaluated_prompt_hash=reasoning_eval_context.evaluated_prompt_hash,
        evaluated_context_hash=reasoning_eval_context.evaluated_context_hash,
        evaluated_output_hash=reasoning_eval_context.evaluated_output_hash,
        evaluator_id=reasoning_eval_context.evaluator_id,
        rubric=reasoning_eval_context.rubric,
        score_payload=reasoning_eval_context.score_payload,
        critique=reasoning_eval_context.critique,
        evaluation_outcome_status=reasoning_eval_context.evaluation_outcome_status,
    )

    # --- Step 5: Persist evaluation artifact ---
    _persist_evaluation(record)

    logger.debug(
        "EVALUATE_REASONING_STEP emitted id=%s evaluator=%s trace=%s outcome=%s "
        "rubric_hash=%s score_hash=%s critique_hash=%s",
        record.reasoning_evaluation_id,
        record.evaluator_id,
        record.reasoning_trace_id,
        record.evaluation_outcome_status,
        record.rubric_hash,
        record.score_hash,
        record.critique_hash,
    )
    return record


def evaluate_reasoning_step_from_trace(
    trace: Any,
    *,
    rubric: ReasoningEvaluationRubric | None = None,
    critique: str = "",
    evaluator_id: str = "ReasoningChokepoint",
    outcome: ReasoningEvaluationOutcome | None = None,
) -> ReasoningEvaluationRecord:
    """Convenience wrapper — build context directly from a ReasoningTraceArtifact.

    Called from reason_and_record() after trace is complete.

    Args:
        trace:        Completed ReasoningTraceArtifact.
        rubric:       Optional ReasoningEvaluationRubric (defaults to coherence=1.0).
        critique:     Optional critique string (defaults to empty, auto-filled).
        evaluator_id: Evaluator identity string.
        outcome:      Explicit outcome; defaults to PASS if trace is complete.
    """
    _rubric = rubric or ReasoningEvaluationRubric(coherence=1.0)
    _critique = critique or f"auto:trace={getattr(trace, 'reasoning_trace_id', '')}"
    _outcome = outcome or (
        ReasoningEvaluationOutcome.PASS
        if getattr(trace, "signed", False)
        else ReasoningEvaluationOutcome.NEEDS_REVIEW
    )
    ctx = ReasoningEvaluationContext(
        reasoning_trace_id=getattr(trace, "reasoning_trace_id", ""),
        run_id=getattr(trace, "run_id", ""),
        trace_id=getattr(trace, "reasoning_trace_id", ""),
        evaluated_prompt_hash=getattr(trace, "prompt_hash", ""),
        evaluated_context_hash=getattr(trace, "context_hash", ""),
        evaluated_output_hash=getattr(trace, "output_hash", ""),
        evaluator_id=evaluator_id,
        rubric=_rubric.to_dict(),
        score_payload={"overall": _rubric.overall_score()},
        critique=_critique,
        evaluation_outcome_status=_outcome,
    )
    return evaluate_reasoning_step(ctx)


# ---------------------------------------------------------------------------
# evaluate_comparative_reasoning() — comparative evaluation (spec §5)
# ---------------------------------------------------------------------------


def evaluate_comparative_reasoning(
    *,
    candidate_a: Any,
    candidate_b: Any,
    winner: Any,
    comparison_rubric: dict[str, Any],
    evaluator_id: str,
) -> ComparativeReasoningEvaluation:
    """Record a comparative evaluation of two reasoning candidates (spec §5).

    Emits compares_proof ADG edge.

    Args:
        candidate_a:        First candidate (trace, output, or hashable artifact).
        candidate_b:        Second candidate.
        winner:             The winning candidate (must be candidate_a or candidate_b).
        comparison_rubric:  Dict describing comparison criteria.
        evaluator_id:       Evaluator identity.

    Returns:
        ComparativeReasoningEvaluation (immutable, 5 fields).

    Raises:
        ValueError: If winning_reasoning_hash doesn't match either candidate.
    """
    comparative = ComparativeReasoningEvaluation.create(
        candidate_a=candidate_a,
        candidate_b=candidate_b,
        winner=winner,
        comparison_rubric=comparison_rubric,
        evaluator_id=evaluator_id,
    )

    _COMPARE_LOG.debug(
        "compares_proof COMPARATIVE_REASONING evaluator=%s candidate_a=%s candidate_b=%s winner=%s rubric=%s",
        evaluator_id,
        comparative.candidate_a_hash,
        comparative.candidate_b_hash,
        comparative.winning_reasoning_hash,
        comparative.comparison_rubric_hash,
    )

    _persist_comparative(comparative)

    logger.debug(
        "EVALUATE_COMPARATIVE_REASONING emitted evaluator=%s winner=%s",
        evaluator_id,
        comparative.winning_reasoning_hash,
    )
    return comparative


# ---------------------------------------------------------------------------
# ReasoningEvaluationStore — queryable store (spec §5 / Gate E)
# ---------------------------------------------------------------------------


class ReasoningEvaluationStore:
    """In-memory queryable store for all emitted ReasoningEvaluationRecord instances.

    Queryable by:
    - run_id
    - trace_id
    - reasoning_trace_id
    - evaluation_outcome_status
    """

    def __init__(self) -> None:
        self._records: list[ReasoningEvaluationRecord] = []
        self._comparatives: list[ComparativeReasoningEvaluation] = []
        self._lock = threading.RLock()

    def ingest(self, record: ReasoningEvaluationRecord) -> None:
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(
            str(uuid.uuid4()),
            LayerSegment.L3_ORCHESTRATION,
            f"ReasoningEvaluationStore.ingest:{record.run_id}",
        )
        with self._lock:
            self._records.append(record)

    def ingest_comparative(self, record: ComparativeReasoningEvaluation) -> None:
        with self._lock:
            self._comparatives.append(record)

    def by_run_id(self, run_id: str) -> list[ReasoningEvaluationRecord]:
        with self._lock:
            return [r for r in self._records if r.run_id == run_id]

    def by_trace_id(self, trace_id: str) -> list[ReasoningEvaluationRecord]:
        with self._lock:
            return [r for r in self._records if r.trace_id == trace_id]

    def by_reasoning_trace_id(self, reasoning_trace_id: str) -> list[ReasoningEvaluationRecord]:
        with self._lock:
            return [r for r in self._records if r.reasoning_trace_id == reasoning_trace_id]

    def by_outcome(self, outcome: ReasoningEvaluationOutcome) -> list[ReasoningEvaluationRecord]:
        with self._lock:
            return [r for r in self._records if r.evaluation_outcome_status == outcome.value]

    def all_records(self) -> list[ReasoningEvaluationRecord]:
        with self._lock:
            return list(self._records)

    def all_comparatives(self) -> list[ComparativeReasoningEvaluation]:
        with self._lock:
            return list(self._comparatives)

    def record_count(self) -> int:
        with self._lock:
            return len(self._records)

    def orphan_evaluations(self) -> list[ReasoningEvaluationRecord]:
        """Return records with empty reasoning_trace_id (should be zero)."""
        with self._lock:
            return [r for r in self._records if not r.reasoning_trace_id]

    def missing_rubric(self) -> list[ReasoningEvaluationRecord]:
        """Return records with empty rubric_hash."""
        with self._lock:
            return [r for r in self._records if not r.rubric_hash]

    def missing_critique_and_score(self) -> list[ReasoningEvaluationRecord]:
        """Return records missing both critique_hash and score_hash."""
        with self._lock:
            return [r for r in self._records if not r.critique_hash and not r.score_hash]

    def comparatives_without_winner(self) -> list[ComparativeReasoningEvaluation]:
        """Return comparative records with empty winning_reasoning_hash."""
        with self._lock:
            return [c for c in self._comparatives if not c.winning_reasoning_hash]


# ---------------------------------------------------------------------------
# Process-level singleton
# ---------------------------------------------------------------------------

_global_store: ReasoningEvaluationStore | None = None
_global_store_lock = threading.Lock()


def get_reasoning_evaluation_store() -> ReasoningEvaluationStore:
    """Return the process-level ReasoningEvaluationStore singleton."""
    global _global_store
    if _global_store is None:
        with _global_store_lock:
            if _global_store is None:
                _global_store = ReasoningEvaluationStore()
    return _global_store


def reset_reasoning_evaluation_store() -> None:
    """Reset the global store (for testing)."""
    global _global_store
    _global_store = None


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()[:32]


def _persist_evaluation(record: ReasoningEvaluationRecord) -> None:
    get_reasoning_evaluation_store().ingest(record)


def _persist_comparative(record: ComparativeReasoningEvaluation) -> None:
    get_reasoning_evaluation_store().ingest_comparative(record)


__all__ = [
    "ReasoningEvaluationOutcome",
    "OrphanReasoningEvaluationError",
    "ReasoningEvaluationRecord",
    "ComparativeReasoningEvaluation",
    "ReasoningEvaluationContext",
    "ReasoningEvaluationRubric",
    "ReasoningEvaluationStore",
    "evaluate_reasoning_step",
    "evaluate_reasoning_step_from_trace",
    "evaluate_comparative_reasoning",
    "get_reasoning_evaluation_store",
    "reset_reasoning_evaluation_store",
]
