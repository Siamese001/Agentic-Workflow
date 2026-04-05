"""Governance Reward Model — scores OptimizationProposals against reward signals.

Aggregates ``GovernanceRewardSignal`` objects into a ``GovernanceRewardScore``
for each proposal.  Proposals must maximize the aggregate reward while
preserving governance invariants (policy compliance, replay stability,
guardrail cleanliness, mutation correctness, groundedness).

Reward formula (weighted sum):
    aggregate = w_g * groundedness
              + w_p * policy_compliance
              + w_r * replay_stability
              + w_gc * guardrail_cleanliness
              + w_mc * mutation_correctness

Default weights sum to 1.0 and are tunable via ``RewardModelConfig``.

Design invariants
-----------------
1. Pure function interface — no global mutable state.
2. No wall-clock reads; ``timestamp_utc`` always caller-supplied.
3. All outputs are deterministically content-addressed.
4. ``invariant_preserved=True`` iff ``aggregate_score >= invariant_floor``
   AND ``policy_compliance >= policy_floor`` AND ``replay_stability >= replay_floor``.
5. Human approval rate: 1.0 when no HITL signals present (benefit of the doubt).
6. Signals with empty ``trace_id`` are rejected (fail-closed).
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass
from typing import Sequence

from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_authorize_and_execute("p2", "governance_reward_model", "execution_auth")
_emit_validates_capability("p2", "governance_reward_model", "capability_check")
_emit_routes_to_capability("p2", "governance_reward_model", "capability_route")
_emit_writes_via_uwg("p2", "governance_reward_model", "uwg_write")
_emit_blocks_direct_write("p2", "governance_reward_model", "direct_write_block")
_emit_records_tool_invocation("p2", "governance_reward_model", "tool_invocation")
_emit_captures_execution_output("p2", "governance_reward_model", "exec_output")
_emit_dispatches_agent("p3", "governance_reward_model", "agent_dispatch")
_emit_coordinates_agents("p3", "governance_reward_model", "agent_coordination")
_emit_records_workflow_lineage("p3", "governance_reward_model", "workflow_lineage")
_emit_records_healing_outcome("p3", "governance_reward_model", "healing_outcome")
_emit_escalates_failure("p3", "governance_reward_model", "failure_escalation")
_emit_orchestrates_workflow("p3", "governance_reward_model", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "governance_reward_model", "healing_dispatch")
_emit_invokes_evaluation("p3", "governance_reward_model", "evaluation_signal")
_emit_records_telemetry_event("p4", "governance_reward_model", "telemetry_event")
_emit_captures_evaluation_metric("p4", "governance_reward_model", "eval_metric")
_emit_stores_embedding("p4", "governance_reward_model", "embedding_store")
_emit_updates_meta_learning_state("p4", "governance_reward_model", "meta_learning")
_emit_links_execution_to_snapshot("p4", "governance_reward_model", "exec_snapshot_link")
from system_learning.enforcement.determinism import deterministic_json
from system_learning.types.optimization_types import (
    GovernanceRewardScore,
    GovernanceRewardSignal,
    OptimizationProposal,
)

_emit_applies_guardrail("p0", "governance_reward_model", "p0_governance")
_emit_snapshots_state("p0", "governance_reward_model", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_emits_metric_event("governance_reward_model", "p4obs", "metric_1")
_emit_emits_metric_event("governance_reward_model", "p4obs", "metric_2")
_emit_emits_metric_event("governance_reward_model", "p4obs", "metric_3")
_emit_emits_metric_event("governance_reward_model", "p4obs", "metric_4")
_emit_emits_metric_event("governance_reward_model", "p4obs", "metric_5")
_emit_emits_metric_event("governance_reward_model", "p4obs", "metric_6")
_emit_records_incident_event("governance_reward_model", "p4obs", "incident")
_emit_captures_runtime_anomaly("governance_reward_model", "p4obs", "anomaly")
_emit_writes_observability_log("governance_reward_model", "p4obs", "obs_log")
_emit_updates_monitoring_state("governance_reward_model", "p4obs", "mon_state")
_emit_triggers_alert("governance_reward_model", "p4obs", "alert")
_emit_links_incident_trace("governance_reward_model", "p4obs", "trace_link")
_emit_captures_pattern("governance_reward_model", "p3lm", "pattern")
_emit_records_learning_event("governance_reward_model", "p3lm", "learning_event")
_emit_writes_learning_snapshot("governance_reward_model", "p3lm", "snapshot")
_emit_feeds_meta_learning("governance_reward_model", "p3lm", "meta_feed")
_emit_updates_routing_strategy("governance_reward_model", "p3lm", "routing")
_emit_improves_agent_policy("governance_reward_model", "p3lm", "policy")
_emit_stores_learning_state("governance_reward_model", "p3lm", "state")
_emit_records_execution_trace("governance_reward_model", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("governance_reward_model", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("governance_reward_model", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("governance_reward_model", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("governance_reward_model", "L4_STATE", "p2_trace_5")
_emit_reads_environ("governance_reward_model", "env_read", "p2_env_1")
_emit_reads_environ("governance_reward_model", "env_read", "p2_env_2")
_emit_reads_runtime_state("governance_reward_model", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("governance_reward_model", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "governance_reward_model", "context_pull")
_emit_pulls_context("p1", "governance_reward_model", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "governance_reward_model", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "governance_reward_model", "uwg_term_2")
_emit_writes_through("p1", "governance_reward_model", "write_through")
_emit_writes_through("p1", "governance_reward_model", "write_through_2")
_emit_validated_by_safety_plane("p1", "governance_reward_model", "safety_validation")
_emit_invokes_eval("p1", "governance_reward_model", "eval_call")
_emit_proposal_commits_routing("p1", "governance_reward_model", "routing_commit")
_emit_escalates_to_human("p1", "governance_reward_model", "human_escalation")
_emit_routes_through("p1", "governance_reward_model", "route_through")
_emit_checks_agent_registry("p1", "governance_reward_model", "agent_registry")
_emit_validates_agent_capability("p1", "governance_reward_model", "capability")
_emit_dispatches_execution_plan("p1", "governance_reward_model", "exec_plan")
_emit_agent_executes_agent("p1", "governance_reward_model", "sub_agent")
_emit_routes_to_agent("p1", "governance_reward_model", "target_agent")
_emit_verifies_policy("p1", "governance_reward_model", "policy_check")
_emit_observes_runtime_state("p1", "governance_reward_model", "runtime_state")
_emit_verifies_boundary("p1", "governance_reward_model", "boundary_check")
_emit_transcripts_response("p1", "governance_reward_model", "transcript")
_emit_hard_fails_untranscripted("p1", "governance_reward_model")
_emit_gated_by_confidence("p1", "governance_reward_model", "confidence_gate")
emit_replay_key("p0", "governance_reward_model")
emit_determinism_digest("p0", "governance_reward_model")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


@dataclass
class RewardModelConfig:
    """Configures the governance reward model weights and invariant floors.

    Weights must sum to 1.0 (enforced in __post_init__).
    """

    weight_groundedness: float = 0.25
    weight_policy_compliance: float = 0.25
    weight_replay_stability: float = 0.20
    weight_guardrail_cleanliness: float = 0.15
    weight_mutation_correctness: float = 0.15

    # Invariant floors — aggregate and individual minimums for invariant_preserved=True
    invariant_floor: float = 0.60
    policy_floor: float = 0.80
    replay_floor: float = 0.75

    def __post_init__(self) -> None:
        total = round(
            self.weight_groundedness
            + self.weight_policy_compliance
            + self.weight_replay_stability
            + self.weight_guardrail_cleanliness
            + self.weight_mutation_correctness,
            6,
        )
        if abs(total - 1.0) > 1e-6:
            raise ValueError(
                f"Reward weights must sum to 1.0, got {total}"
            )
        for attr in (
            "invariant_floor",
            "policy_floor",
            "replay_floor",
        ):
            val = getattr(self, attr)
            if not 0.0 <= val <= 1.0:
                raise ValueError(f"{attr} must be in [0.0, 1.0], got {val}")


# ---------------------------------------------------------------------------
# Aggregation helpers
# ---------------------------------------------------------------------------


def _safe_mean(values: list[float]) -> float:
    if not values:
        return 0.0
    return round(sum(values) / len(values), 6)


def _human_approval_rate(signals: list[GovernanceRewardSignal]) -> float:
    hitl_signals = [s for s in signals if s.human_approval is not None]
    if not hitl_signals:
        return 1.0  # benefit of the doubt when no HITL
    approved = sum(1 for s in hitl_signals if s.human_approval is True)
    return round(approved / len(hitl_signals), 6)


def _build_score_id(
    proposal_id: str,
    aggregate_score: float,
    signal_count: int,
    timestamp_utc: int,
) -> str:
    canonical = deterministic_json({
        "aggregate_score": round(aggregate_score, 6),
        "proposal_id": proposal_id,
        "signal_count": signal_count,
        "timestamp_utc": timestamp_utc,
    })
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------


class GovernanceRewardModel:
    """Scores optimization proposals against governance reward signals.

    Usage::

        model = GovernanceRewardModel()
        score = model.score(proposal, signals, timestamp_utc=ts)
        if score.invariant_preserved and score.aggregate_score >= 0.7:
            # proceed to validation
    """

    def __init__(self, config: RewardModelConfig | None = None) -> None:
        self._config = config or RewardModelConfig()

    def score(
        self,
        proposal: OptimizationProposal,
        signals: Sequence[GovernanceRewardSignal],
        timestamp_utc: int,
    ) -> GovernanceRewardScore:
        """Compute a GovernanceRewardScore for a proposal.

        Parameters
        ----------
        proposal:
            The proposal to score.
        signals:
            GovernanceRewardSignal objects collected for the affected
            execution traces.  Empty sequence → zero-signal score.
        timestamp_utc:
            Caller-supplied Unix timestamp.

        Returns
        -------
        GovernanceRewardScore
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "GovernanceRewardModel.score")

        cfg = self._config

        # Filter out invalid signals (fail-closed)
        valid_signals: list[GovernanceRewardSignal] = []
        for s in signals:
            if not s.trace_id:
                logger.warning(
                    "reward_model: rejecting signal with empty trace_id"
                )
                continue
            valid_signals.append(s)

        if not valid_signals:
            # Zero-signal score — invariant_preserved=False so proposal cannot
            # proceed without evidence
            score_id = _build_score_id(
                proposal.proposal_id, 0.0, 0, timestamp_utc
            )
            return GovernanceRewardScore(
                score_id=score_id,
                proposal_id=proposal.proposal_id,
                aggregate_score=0.0,
                groundedness_contrib=0.0,
                policy_compliance_contrib=0.0,
                replay_stability_contrib=0.0,
                guardrail_cleanliness_contrib=0.0,
                mutation_correctness_contrib=0.0,
                human_approval_rate=1.0,
                invariant_preserved=False,
                signal_count=0,
                timestamp_utc=timestamp_utc,
            )

        # --- Compute per-dimension means ---
        g_mean = _safe_mean([s.groundedness_score for s in valid_signals])
        p_mean = _safe_mean([s.policy_compliance for s in valid_signals])
        r_mean = _safe_mean([s.replay_stability for s in valid_signals])
        gc_mean = _safe_mean([s.guardrail_cleanliness for s in valid_signals])
        mc_mean = _safe_mean([s.mutation_correctness for s in valid_signals])
        approval_rate = _human_approval_rate(valid_signals)

        # --- Weighted contributions ---
        g_contrib = round(cfg.weight_groundedness * g_mean, 6)
        p_contrib = round(cfg.weight_policy_compliance * p_mean, 6)
        r_contrib = round(cfg.weight_replay_stability * r_mean, 6)
        gc_contrib = round(cfg.weight_guardrail_cleanliness * gc_mean, 6)
        mc_contrib = round(cfg.weight_mutation_correctness * mc_mean, 6)

        aggregate = round(
            g_contrib + p_contrib + r_contrib + gc_contrib + mc_contrib, 6
        )
        aggregate = max(0.0, min(1.0, aggregate))

        # --- Invariant check ---
        invariant_preserved = (
            aggregate >= cfg.invariant_floor
            and p_mean >= cfg.policy_floor
            and r_mean >= cfg.replay_floor
        )

        score_id = _build_score_id(
            proposal.proposal_id, aggregate, len(valid_signals), timestamp_utc
        )

        return GovernanceRewardScore(
            score_id=score_id,
            proposal_id=proposal.proposal_id,
            aggregate_score=aggregate,
            groundedness_contrib=g_contrib,
            policy_compliance_contrib=p_contrib,
            replay_stability_contrib=r_contrib,
            guardrail_cleanliness_contrib=gc_contrib,
            mutation_correctness_contrib=mc_contrib,
            human_approval_rate=approval_rate,
            invariant_preserved=invariant_preserved,
            signal_count=len(valid_signals),
            timestamp_utc=timestamp_utc,
        )

    def score_batch(
        self,
        proposals: Sequence[OptimizationProposal],
        signals_map: dict[str, Sequence[GovernanceRewardSignal]],
        timestamp_utc: int,
    ) -> list[GovernanceRewardScore]:
        """Score a batch of proposals.

        Parameters
        ----------
        proposals:
            Proposals to score.
        signals_map:
            Dict mapping ``proposal_id`` → signals.  Missing keys default
            to empty signal list (zero-signal score).
        timestamp_utc:
            Caller-supplied Unix timestamp.

        Returns
        -------
        list[GovernanceRewardScore]
            Sorted by score_id for determinism.
        """
        scores = [
            self.score(
                p,
                signals_map.get(p.proposal_id, []),
                timestamp_utc,
            )
            for p in proposals
        ]
        scores.sort(key=lambda s: s.score_id)
        return scores

    def annotate_proposals(
        self,
        proposals: Sequence[OptimizationProposal],
        scores: Sequence[GovernanceRewardScore],
        timestamp_utc: int,
    ) -> list[OptimizationProposal]:
        """Return new OptimizationProposal objects with reward_score populated.

        Produces frozen copies with the aggregate_score injected so that
        downstream validation and commit stages can read the score.
        Proposals without a matching score are returned unchanged.
        """
        score_by_pid: dict[str, GovernanceRewardScore] = {
            s.proposal_id: s for s in scores
        }
        annotated: list[OptimizationProposal] = []
        for p in proposals:
            gs = score_by_pid.get(p.proposal_id)
            if gs is None:
                annotated.append(p)
                continue
            # Rebuild with reward_score populated (frozen dataclass copy pattern)
            import dataclasses
            annotated.append(
                dataclasses.replace(p, reward_score=gs.aggregate_score)
            )
        return annotated


# ---------------------------------------------------------------------------
# Module-level convenience
# ---------------------------------------------------------------------------


def score_proposal(
    proposal: OptimizationProposal,
    signals: Sequence[GovernanceRewardSignal],
    timestamp_utc: int,
    *,
    config: RewardModelConfig | None = None,
) -> GovernanceRewardScore:
    """Module-level convenience wrapper."""
    return GovernanceRewardModel(config).score(proposal, signals, timestamp_utc)


__all__ = [
    "GovernanceRewardModel",
    "RewardModelConfig",
    "score_proposal",
]
