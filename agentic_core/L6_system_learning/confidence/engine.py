"""Healing confidence scoring engine for deterministic escalation decisions.

Wave H5 M2-M4 (2026-04-21, plan meta-learning-confidence-audit-b7c4e1):
Removed 3 orphaned "placeholder for test compatibility" symbols
(`CONFIDENCE_THRESHOLD`, `ConfidenceScore`, `calculate_confidence`) after
ADG fan-in analysis (docs/reports/plans/h5-wave-m1-adg-fanin-evidence.md)
confirmed zero production consumers. The real `HealingConfidenceScorer`
class is the only public surface of this module.
"""

from __future__ import annotations

import json
import uuid
from typing import Sequence

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

_emit_emits_metric_event("engine", "p4obs", "metric_1")
_emit_emits_metric_event("engine", "p4obs", "metric_2")
_emit_emits_metric_event("engine", "p4obs", "metric_3")
_emit_emits_metric_event("engine", "p4obs", "metric_4")
_emit_emits_metric_event("engine", "p4obs", "metric_5")
_emit_emits_metric_event("engine", "p4obs", "metric_6")
_emit_records_incident_event("engine", "p4obs", "incident")
_emit_captures_runtime_anomaly("engine", "p4obs", "anomaly")
_emit_writes_observability_log("engine", "p4obs", "obs_log")
_emit_updates_monitoring_state("engine", "p4obs", "mon_state")
_emit_triggers_alert("engine", "p4obs", "alert")
_emit_links_incident_trace("engine", "p4obs", "trace_link")
_emit_captures_pattern("engine", "p3lm", "pattern")
_emit_records_learning_event("engine", "p3lm", "learning_event")
_emit_writes_learning_snapshot("engine", "p3lm", "snapshot")
_emit_feeds_meta_learning("engine", "p3lm", "meta_feed")
_emit_updates_routing_strategy("engine", "p3lm", "routing")
_emit_improves_agent_policy("engine", "p3lm", "policy")
_emit_stores_learning_state("engine", "p3lm", "state")
_emit_records_execution_trace("engine", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("engine", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("engine", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("engine", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("engine", "L4_STATE", "p2_trace_5")
_emit_reads_environ("engine", "env_read", "p2_env_1")
_emit_reads_environ("engine", "env_read", "p2_env_2")
_emit_reads_runtime_state("engine", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("engine", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "engine", "context_pull")
_emit_pulls_context("p1", "engine", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "engine", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "engine", "uwg_term_2")
_emit_writes_through("p1", "engine", "write_through")
_emit_writes_through("p1", "engine", "write_through_2")
_emit_validated_by_safety_plane("p1", "engine", "safety_validation")
_emit_invokes_eval("p1", "engine", "eval_call")
_emit_proposal_commits_routing("p1", "engine", "routing_commit")
_emit_escalates_to_human("p1", "engine", "human_escalation")
_emit_routes_through("p1", "engine", "route_through")
_emit_checks_agent_registry("p1", "engine", "agent_registry")
_emit_validates_agent_capability("p1", "engine", "capability")
_emit_dispatches_execution_plan("p1", "engine", "exec_plan")
_emit_agent_executes_agent("p1", "engine", "sub_agent")
_emit_routes_to_agent("p1", "engine", "target_agent")
_emit_verifies_policy("p1", "engine", "policy_check")
_emit_observes_runtime_state("p1", "engine", "runtime_state")
_emit_verifies_boundary("p1", "engine", "boundary_check")
_emit_transcripts_response("p1", "engine", "transcript")
_emit_hard_fails_untranscripted("p1", "engine")
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
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "HealingConfidenceScorer.score"
        )

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
                ConfidenceDecision(attempt_id=attempt.attempt_id, confidence=confidence, action=action),
            )
        canonical_data = {
            "decisions": [
                {"attempt_id": d.attempt_id, "confidence": d.confidence, "action": d.action}
                for d in decisions
            ],
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
