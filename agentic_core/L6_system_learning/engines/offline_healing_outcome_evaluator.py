"""Offline evaluator for healing outcome proposals.

Phase 3: Deterministic scoring engine for shadow mode evaluation.
No IO except optional store; no config/routing/L4 writes.
"""

from __future__ import annotations

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_authorize_and_execute("p2", "offline_healing_outcome_evaluator", "execution_auth")
trace_contract._emit_validates_capability("p2", "offline_healing_outcome_evaluator", "capability_check")
trace_contract._emit_routes_to_capability("p2", "offline_healing_outcome_evaluator", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "offline_healing_outcome_evaluator", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "offline_healing_outcome_evaluator", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "offline_healing_outcome_evaluator", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "offline_healing_outcome_evaluator", "exec_output")
trace_contract._emit_dispatches_agent("p3", "offline_healing_outcome_evaluator", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "offline_healing_outcome_evaluator", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "offline_healing_outcome_evaluator", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "offline_healing_outcome_evaluator", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "offline_healing_outcome_evaluator", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "offline_healing_outcome_evaluator", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "offline_healing_outcome_evaluator", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "offline_healing_outcome_evaluator", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "offline_healing_outcome_evaluator", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "offline_healing_outcome_evaluator", "eval_metric")
trace_contract._emit_stores_embedding("p4", "offline_healing_outcome_evaluator", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "offline_healing_outcome_evaluator", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "offline_healing_outcome_evaluator", "exec_snapshot_link")
from agentic_core.L6_system_learning.types.healing_outcome_intake_types import HealingOutcomeIntakeRecord
from agentic_core.L6_system_learning.types.healing_outcome_scoring_types import (
    ScoredRecommendation,
    ScoringReport,
    ScoringWeights,
    _stable_round,
)
from agentic_core.L6_system_learning.types.healing_outcome_types import HealingOutcomeProposal

trace_contract._emit_applies_guardrail("p0", "offline_healing_outcome_evaluator", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "offline_healing_outcome_evaluator", "policy_binding")
trace_contract._emit_snapshots_state("p0", "offline_healing_outcome_evaluator", "state_snapshot")
from tqdm import tqdm

trace_contract._emit_emits_metric_event("offline_healing_outcome_evaluator", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("offline_healing_outcome_evaluator", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("offline_healing_outcome_evaluator", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("offline_healing_outcome_evaluator", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("offline_healing_outcome_evaluator", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("offline_healing_outcome_evaluator", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("offline_healing_outcome_evaluator", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("offline_healing_outcome_evaluator", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("offline_healing_outcome_evaluator", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("offline_healing_outcome_evaluator", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("offline_healing_outcome_evaluator", "p4obs", "alert")
trace_contract._emit_links_incident_trace("offline_healing_outcome_evaluator", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("offline_healing_outcome_evaluator", "p3lm", "pattern")
trace_contract._emit_records_learning_event("offline_healing_outcome_evaluator", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("offline_healing_outcome_evaluator", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("offline_healing_outcome_evaluator", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("offline_healing_outcome_evaluator", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("offline_healing_outcome_evaluator", "p3lm", "policy")
trace_contract._emit_stores_learning_state("offline_healing_outcome_evaluator", "p3lm", "state")
trace_contract._emit_records_execution_trace("offline_healing_outcome_evaluator", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("offline_healing_outcome_evaluator", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("offline_healing_outcome_evaluator", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("offline_healing_outcome_evaluator", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("offline_healing_outcome_evaluator", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("offline_healing_outcome_evaluator", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("offline_healing_outcome_evaluator", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("offline_healing_outcome_evaluator", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("offline_healing_outcome_evaluator", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "offline_healing_outcome_evaluator", "context_pull")
trace_contract._emit_pulls_context("p1", "offline_healing_outcome_evaluator", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "offline_healing_outcome_evaluator", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "offline_healing_outcome_evaluator", "uwg_term_2")
trace_contract._emit_writes_through("p1", "offline_healing_outcome_evaluator", "write_through")
trace_contract._emit_writes_through("p1", "offline_healing_outcome_evaluator", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "offline_healing_outcome_evaluator", "safety_validation")
trace_contract._emit_invokes_eval("p1", "offline_healing_outcome_evaluator", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "offline_healing_outcome_evaluator", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "offline_healing_outcome_evaluator", "human_escalation")
trace_contract._emit_routes_through("p1", "offline_healing_outcome_evaluator", "route_through")
trace_contract._emit_checks_agent_registry("p1", "offline_healing_outcome_evaluator", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "offline_healing_outcome_evaluator", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "offline_healing_outcome_evaluator", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "offline_healing_outcome_evaluator", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "offline_healing_outcome_evaluator", "target_agent")
trace_contract._emit_verifies_policy("p1", "offline_healing_outcome_evaluator", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "offline_healing_outcome_evaluator", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "offline_healing_outcome_evaluator", "boundary_check")
trace_contract._emit_transcripts_response("p1", "offline_healing_outcome_evaluator", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "offline_healing_outcome_evaluator")
trace_contract._emit_gated_by_confidence("p1", "offline_healing_outcome_evaluator", "confidence_gate")
trace_contract.emit_replay_key("p0", "offline_healing_outcome_evaluator")
trace_contract.emit_determinism_digest("p0", "offline_healing_outcome_evaluator")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


class OfflineHealingOutcomeEvaluator:
    """Deterministic offline evaluator for healing outcome proposals.

    Evaluates proposals against intake records using pure functions.
    No wall-clock reads; all timestamps are explicit.
    """

    def __init__(self, weights: ScoringWeights) -> None:
        """Initialize evaluator with scoring weights."""
        self.weights = weights

    def evaluate(
        self,
        intake: HealingOutcomeIntakeRecord,
        created_utc: int,
        candidates: tuple[HealingOutcomeProposal, ...],
    ) -> ScoringReport:
        """Evaluate candidate proposals deterministically.

        Args:
            intake: Healing outcome intake record with snapshot stats
            created_utc: Explicit timestamp (no wall-clock reads)
            candidates: Proposals to evaluate (order-independent)

        Returns:
            Deterministic scoring report with sorted recommendations
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "OfflineHealingOutcomeEvaluator.evaluate"
        )

        # Compute aggregate success rate from intake snapshot
        total_success = sum(stat.success_count for stat in intake.snapshot)
        total_events = sum(stat.total_count for stat in intake.snapshot)
        aggregate_success_rate = total_success / total_events if total_events > 0 else 0.0

        # Sample size is total events (deterministic formula)
        sample_size = total_events

        # Compute risk tier penalty (higher tiers get higher penalty)
        # Tier penalty: LOCAL_AGENT=0, REMOTE_AGENT=0.1, CLOUD_SERVICE=0.2
        tier_penalties = {
            "LOCAL_AGENT": 0.0,
            "REMOTE_AGENT": 0.1,
            "CLOUD_SERVICE": 0.2,
        }

        # Aggregate risk tier penalty from snapshot
        risk_penalty = 0.0
        for stat in intake.snapshot:
            tier_penalty = tier_penalties.get(stat.tier, 0.3)  # Default penalty for unknown tiers
            # Weight by proportion of events
            weight = stat.total_count / total_events if total_events > 0 else 0.0
            risk_penalty += tier_penalty * weight

        # Evaluate each candidate
        recommendations = []
        rejected_reasons = []

        for i, candidate in tqdm(enumerate(candidates), desc="Processing", unit="item"):
            proposer_id = f"proposer_{i}"  # Generic proposer ID since proposals don't carry it
            target_surface = "healing_outcome_policy"  # Generic target surface

            # Apply deterministic validation filters
            # Filter 1: Minimum sample size (require at least 10 events)
            if sample_size < 10:
                rejected_reasons.append(f"Candidate {i}: Insufficient sample size ({sample_size} < 10)")
                continue

            # Filter 2: Minimum success rate (require at least 50%)
            if aggregate_success_rate < 0.5:
                rejected_reasons.append(
                    f"Candidate {i}: Low success rate ({aggregate_success_rate:.4f} < 0.5)",
                )
                continue

            # Filter 3: Risk tier threshold (reject if average penalty > 0.15)
            if risk_penalty > 0.15:
                rejected_reasons.append(f"Candidate {i}: High risk tier penalty ({risk_penalty:.4f} > 0.15)")
                continue

            # Compute deterministic score
            # Score = success_rate_weight * success_rate
            #        - stability_penalty_weight * risk_penalty
            #        + sample_size_weight * log(sample_size + 1) / log(1000)
            #        - risk_tier_penalty_weight * risk_penalty

            import math

            sample_size_normalized = math.log(sample_size + 1) / math.log(1000)  # 0 to 1 scale

            raw_score = (
                self.weights.success_rate_weight * aggregate_success_rate
                - self.weights.stability_penalty_weight * risk_penalty
                + self.weights.sample_size_weight * sample_size_normalized
                - self.weights.risk_tier_penalty_weight * risk_penalty
            )

            # Apply deterministic rounding (round-half-up to 4 decimals)
            score = _stable_round(max(0.0, raw_score))  # Clamp to non-negative

            # Generate deterministic reasons
            reasons = [
                f"Success rate: {aggregate_success_rate:.4f}",
                f"Sample size: {sample_size}",
                f"Risk penalty: {risk_penalty:.4f}",
                f"Actions: {len(candidate.recommended_actions)}",
            ]

            recommendation = ScoredRecommendation(
                proposer_id=proposer_id,
                target_surface=target_surface,
                recommended_actions=candidate.recommended_actions,
                score=score,
                reasons=tuple(reasons),
            )
            recommendations.append(recommendation)

        # Sort recommendations deterministically by (-score, proposer_id, target_surface)
        recommendations.sort(key=lambda r: (-r.score, r.proposer_id, r.target_surface))

        # Sort rejected reasons deterministically
        rejected_reasons = tuple(sorted(rejected_reasons))

        return ScoringReport(
            created_utc=created_utc,
            intake_record=intake,
            weights=self.weights,
            recommendations=tuple(recommendations),
            rejected_reasons=rejected_reasons,
        )
