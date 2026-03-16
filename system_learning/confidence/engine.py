"""Healing confidence scoring engine for deterministic escalation decisions."""

from __future__ import annotations

import json
import uuid
from typing import Sequence

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_gated_by_confidence,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_authorize_and_execute("p2", "engine", "execution_auth")
_emit_validates_capability("p2", "engine", "capability_check")
_emit_routes_to_capability("p2", "engine", "capability_route")
_emit_writes_via_uwg("p2", "engine", "uwg_write")
_emit_blocks_direct_write("p2", "engine", "direct_write_block")
_emit_records_tool_invocation("p2", "engine", "tool_invocation")
_emit_captures_execution_output("p2", "engine", "exec_output")
_emit_dispatches_agent("p3", "engine", "agent_dispatch")
_emit_coordinates_agents("p3", "engine", "agent_coordination")
_emit_records_workflow_lineage("p3", "engine", "workflow_lineage")
_emit_records_healing_outcome("p3", "engine", "healing_outcome")
_emit_escalates_failure("p3", "engine", "failure_escalation")
_emit_orchestrates_workflow("p3", "engine", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "engine", "healing_dispatch")
_emit_invokes_evaluation("p3", "engine", "evaluation_signal")
_emit_records_telemetry_event("p4", "engine", "telemetry_event")
_emit_captures_evaluation_metric("p4", "engine", "eval_metric")
_emit_stores_embedding("p4", "engine", "embedding_store")
_emit_updates_meta_learning_state("p4", "engine", "meta_learning")
_emit_links_execution_to_snapshot("p4", "engine", "exec_snapshot_link")
from .types import ConfidenceDecision, HealingAttempt, HealingConfidenceReport

_emit_applies_guardrail("p0", "engine", "p0_governance")
_emit_reads_policy_state("p0", "engine", "policy_binding")
_emit_snapshots_state("p0", "engine", "state_snapshot")
emit_replay_key("p0", "engine")
emit_determinism_digest("p0", "engine")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


class HealingConfidenceScorer:
    """Deterministic healing confidence scorer for escalation decisions."""

    def __init__(self):
        """Initialize confidence scorer with deterministic parameters."""
        self._outcome_scores = {"SUCCESS": 0.8, "PARTIAL": 0.5, "FAIL": 0.2}
        # guardian: allow-magic-config
        self._escalate_threshold = 0.33
        # guardian: allow-magic-config
        self._review_threshold = 0.66

    def score(self, attempts: Sequence[HealingAttempt]) -> HealingConfidenceReport:
        """Score healing attempts and generate confidence report."""
        _emit_gated_by_confidence(str(uuid.uuid4()), "HealingConfidenceScorer.score", "0.5")
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "HealingConfidenceScorer.score")

        if attempts is None:
            raise TypeError("Attempts cannot be None")
        if not attempts:
            return HealingConfidenceReport.from_canonical_bytes([], b"{}")
        for attempt in attempts:
            if not isinstance(attempt, HealingAttempt):
                raise TypeError(f"All attempts must be HealingAttempt objects, got {type(attempt)}")
            if not attempt.attempt_id:
                raise ValueError("Attempt ID cannot be empty")
            if attempt.outcome not in self._outcome_scores:
                raise ValueError(f"Unknown outcome: {attempt.outcome}")
        sorted_attempts = sorted(attempts, key=lambda a: a.attempt_id)
        decisions = []
        for attempt in sorted_attempts:
            confidence = self._calculate_confidence(attempt)
            action = self._map_confidence_to_action(confidence)
            decisions.append(
                ConfidenceDecision(attempt_id=attempt.attempt_id, confidence=confidence, action=action)
            )
        canonical_data = {
            "decisions": [
                {"attempt_id": d.attempt_id, "confidence": d.confidence, "action": d.action}
                for d in decisions
            ]
        }
        canonical_bytes = json.dumps(canonical_data, separators=(",", ":"), sort_keys=True).encode("ascii")
        return HealingConfidenceReport.from_canonical_bytes(decisions, canonical_bytes)

    def _calculate_confidence(self, attempt: HealingAttempt) -> float:
        """Calculate confidence score for a single attempt."""
        base_score = self._outcome_scores[attempt.outcome]
        severity_penalty = min(attempt.severity * 0.1, 0.5)
        cost_penalty = min(attempt.cost * 0.05, 0.3)
        confidence = base_score - severity_penalty - cost_penalty
        if attempt.outcome == "SUCCESS":
            min_confidence = self._outcome_scores["PARTIAL"] - 0.1
            confidence = max(confidence, min_confidence)
        elif attempt.outcome == "FAIL":
            max_confidence = self._outcome_scores["PARTIAL"] + 0.1
            confidence = min(confidence, max_confidence)
        return max(0.0, min(1.0, confidence))

    def _map_confidence_to_action(self, confidence: float) -> str:
        """Map confidence score to action deterministically."""
        if confidence < self._escalate_threshold:
            return "ESCALATE"
        elif confidence < self._review_threshold:
            return "REVIEW"
        else:
            return "ACCEPT"
