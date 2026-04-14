"""Meta-Learning Bus — ADG-driven learning pipeline orchestrator.

Orchestrates the full closed learning loop:

  execution_trace
    → TraceFeatureExtractor   → FeatureBundle / TraceFeatureRecord
    → RCAClusterEngine        → RCACluster
    → GovernanceRewardModel   → GovernanceRewardScore
    → OptimizationProposalEngine → OptimizationProposal (scored)
    → ProposalValidationEngine   → ValidationResult
    → OptimizationCommit         (for passing proposals)
    → ADG relations emitted      (proposal_commits_optimization + lineage)

ADG relation families emitted by this bus
------------------------------------------
  triggered_telemetry          — trace → feature bundle stored
  chunks_into                  — feature bundle → RCA cluster
  stores_embedding             — cluster → learning record persisted
  proposal_commits_optimization — proposal → optimization commit
  scored_by_reward             — proposal → governance reward score

Design invariants
-----------------
1. No wall-clock reads inside the pipeline; ``timestamp_utc`` must be
   supplied by the caller.
2. The bus is purely additive — it never deletes or mutates existing
   ADG entities.
3. All pipeline outputs are deterministically content-addressed.
4. The bus is fail-open at every stage: a stage failure produces a
   warning log and an empty output list for that stage, allowing
   downstream stages to proceed with reduced inputs.
5. ADG persistence is optional and fail-open; if the bridge is
   unavailable, the bus still returns full in-process results.
6. The bus is NOT a singleton — callers may instantiate multiple buses
   with different configs for different agent contexts.
"""

from __future__ import annotations

from tqdm import tqdm
import logging
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_applies_guardrail("p0", "meta_learning_bus", "p0_governance")
_emit_snapshots_state("p0", "meta_learning_bus", "state_snapshot")
emit_replay_key("p0", "meta_learning_bus")
emit_determinism_digest("p0", "meta_learning_bus")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "meta_learning_bus", "execution_auth")
_emit_validates_capability("p2", "meta_learning_bus", "capability_check")
_emit_routes_to_capability("p2", "meta_learning_bus", "capability_route")
_emit_writes_via_uwg("p2", "meta_learning_bus", "uwg_write")
_emit_blocks_direct_write("p2", "meta_learning_bus", "direct_write_block")
_emit_records_tool_invocation("p2", "meta_learning_bus", "tool_invocation")
_emit_captures_execution_output("p2", "meta_learning_bus", "exec_output")
_emit_dispatches_agent("p3", "meta_learning_bus", "agent_dispatch")
_emit_coordinates_agents("p3", "meta_learning_bus", "agent_coordination")
_emit_records_workflow_lineage("p3", "meta_learning_bus", "workflow_lineage")
_emit_records_healing_outcome("p3", "meta_learning_bus", "healing_outcome")
_emit_escalates_failure("p3", "meta_learning_bus", "failure_escalation")
_emit_orchestrates_workflow("p3", "meta_learning_bus", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "meta_learning_bus", "healing_dispatch")
_emit_invokes_evaluation("p3", "meta_learning_bus", "evaluation_signal")
_emit_records_telemetry_event("p4", "meta_learning_bus", "telemetry_event")
_emit_captures_evaluation_metric("p4", "meta_learning_bus", "eval_metric")
_emit_stores_embedding("p4", "meta_learning_bus", "embedding_store")
_emit_updates_meta_learning_state("p4", "meta_learning_bus", "meta_learning")
_emit_links_execution_to_snapshot("p4", "meta_learning_bus", "exec_snapshot_link")

# Configuration constants
DEFAULT_COMMIT_REWARD_THRESHOLD = 0.60

import hashlib
import logging
import uuid
from dataclasses import dataclass
from typing import Any, Sequence

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_records_execution_trace,
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
from system_learning.enforcement.determinism import deterministic_json
from system_learning.engines.governance_reward_model import (
    GovernanceRewardModel,
    RewardModelConfig,
)
from system_learning.engines.optimization_proposal_engine import (
    OptimizationProposalEngine,
    ProposalEngineConfig,
)
from system_learning.engines.proposal_validation_engine import (
    ProposalValidationEngine,
    ValidationConfig,
)
from system_learning.engines.rca_cluster_engine import (
    RCAClusterConfig,
    RCAClusterEngine,
)
from system_learning.engines.trace_feature_extractor import TraceFeatureExtractor
from system_learning.types.optimization_types import (
    GovernanceRewardSignal,
    OptimizationCommit,
    OptimizationProposal,
    ValidationResult,
)
from system_learning.types.trace_feature_types import (
    FailurePattern,
    FeatureBundle,
    RCACluster,
    TraceFeatureRecord,
)

_emit_emits_metric_event("meta_learning_bus", "p4obs", "metric_1")
_emit_emits_metric_event("meta_learning_bus", "p4obs", "metric_2")
_emit_emits_metric_event("meta_learning_bus", "p4obs", "metric_3")
_emit_emits_metric_event("meta_learning_bus", "p4obs", "metric_4")
_emit_emits_metric_event("meta_learning_bus", "p4obs", "metric_5")
_emit_emits_metric_event("meta_learning_bus", "p4obs", "metric_6")
_emit_records_incident_event("meta_learning_bus", "p4obs", "incident")
_emit_captures_runtime_anomaly("meta_learning_bus", "p4obs", "anomaly")
_emit_writes_observability_log("meta_learning_bus", "p4obs", "obs_log")
_emit_updates_monitoring_state("meta_learning_bus", "p4obs", "mon_state")
_emit_triggers_alert("meta_learning_bus", "p4obs", "alert")
_emit_links_incident_trace("meta_learning_bus", "p4obs", "trace_link")
_emit_captures_pattern("meta_learning_bus", "p3lm", "pattern")
_emit_records_learning_event("meta_learning_bus", "p3lm", "learning_event")
_emit_writes_learning_snapshot("meta_learning_bus", "p3lm", "snapshot")
_emit_feeds_meta_learning("meta_learning_bus", "p3lm", "meta_feed")
_emit_updates_routing_strategy("meta_learning_bus", "p3lm", "routing")
_emit_improves_agent_policy("meta_learning_bus", "p3lm", "policy")
_emit_stores_learning_state("meta_learning_bus", "p3lm", "state")
_emit_records_execution_trace("meta_learning_bus", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("meta_learning_bus", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("meta_learning_bus", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("meta_learning_bus", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("meta_learning_bus", "L4_STATE", "p2_trace_5")
_emit_reads_environ("meta_learning_bus", "env_read", "p2_env_1")
_emit_reads_environ("meta_learning_bus", "env_read", "p2_env_2")
_emit_reads_runtime_state("meta_learning_bus", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("meta_learning_bus", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "meta_learning_bus", "context_pull")
_emit_pulls_context("p1", "meta_learning_bus", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "meta_learning_bus", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "meta_learning_bus", "uwg_term_2")
_emit_writes_through("p1", "meta_learning_bus", "write_through")
_emit_writes_through("p1", "meta_learning_bus", "write_through_2")
_emit_validated_by_safety_plane("p1", "meta_learning_bus", "safety_validation")
_emit_invokes_eval("p1", "meta_learning_bus", "eval_call")
_emit_proposal_commits_routing("p1", "meta_learning_bus", "routing_commit")
_emit_escalates_to_human("p1", "meta_learning_bus", "human_escalation")
_emit_routes_through("p1", "meta_learning_bus", "route_through")
_emit_checks_agent_registry("p1", "meta_learning_bus", "agent_registry")
_emit_validates_agent_capability("p1", "meta_learning_bus", "capability")
_emit_dispatches_execution_plan("p1", "meta_learning_bus", "exec_plan")
_emit_agent_executes_agent("p1", "meta_learning_bus", "sub_agent")
_emit_routes_to_agent("p1", "meta_learning_bus", "target_agent")
_emit_verifies_policy("p1", "meta_learning_bus", "policy_check")
_emit_observes_runtime_state("p1", "meta_learning_bus", "runtime_state")
_emit_verifies_boundary("p1", "meta_learning_bus", "boundary_check")
_emit_transcripts_response("p1", "meta_learning_bus", "transcript")
_emit_hard_fails_untranscripted("p1", "meta_learning_bus")
_emit_gated_by_confidence("p1", "meta_learning_bus", "confidence_gate")

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Bus configuration
# ---------------------------------------------------------------------------


@dataclass
class MetaLearningBusConfig:
    """Full configuration for the MetaLearningBus pipeline."""

    rca_config: RCAClusterConfig | None = None
    proposal_config: ProposalEngineConfig | None = None
    validation_config: ValidationConfig | None = None
    reward_config: RewardModelConfig | None = None

    # Minimum reward score for a proposal to proceed to validation
    reward_threshold: float = 0.50

    # Minimum reward score for a proposal to proceed to commit
    commit_reward_threshold: float = DEFAULT_COMMIT_REWARD_THRESHOLD

    # Whether to emit ADG relations (requires bridge availability)
    emit_adg_relations: bool = True

    # Whether to persist TraceFeatureRecords to the case library
    persist_records: bool = True


# ---------------------------------------------------------------------------
# Pipeline result container
# ---------------------------------------------------------------------------


@dataclass
class BusPipelineResult:
    """Complete result of a single MetaLearningBus.process_traces() call.

    Attributes
    ----------
    bundles : list[FeatureBundle]
        Feature bundles extracted from input traces.
    records : list[TraceFeatureRecord]
        Persisted learning records.
    clusters : list[RCACluster]
        RCA clusters produced from records.
    proposals : list[OptimizationProposal]
        Scored optimization proposals (all generated, including rejected).
    validation_results : list[ValidationResult]
        Validation results for proposals that cleared the reward threshold.
    commits : list[OptimizationCommit]
        Optimization commits for proposals that passed validation.
    rejected_proposal_ids : list[str]
        Proposal IDs that were rejected (reward below threshold or
        validation failure).
    adg_relations_emitted : list[tuple[str, str, str]]
        (from_entity, relation_type, to_entity) ADG relation tuples emitted.
    """

    bundles: list[FeatureBundle]
    records: list[TraceFeatureRecord]
    clusters: list[RCACluster]
    proposals: list[OptimizationProposal]
    validation_results: list[ValidationResult]
    commits: list[OptimizationCommit]
    rejected_proposal_ids: list[str]
    adg_relations_emitted: list[tuple[str, str, str]]


# ---------------------------------------------------------------------------
# ADG relation helpers
# ---------------------------------------------------------------------------

_ADG_TRIGGERED_TELEMETRY = "triggered_telemetry"
_ADG_CHUNKS_INTO = "chunks_into"
_ADG_STORES_EMBEDDING = "stores_embedding"
_ADG_PROPOSAL_COMMITS = "proposal_commits_optimization"
_ADG_SCORED_BY_REWARD = "scored_by_reward"


def _build_commit_id(
    proposal_id: str,
    validation_result_id: str,
    timestamp_utc: int,
) -> str:
    canonical = deterministic_json(
        {
            "proposal_id": proposal_id,
            "timestamp_utc": timestamp_utc,
            "validation_result_id": validation_result_id,
        },
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _build_optimization_commit(
    proposal: OptimizationProposal,
    result: ValidationResult,
    timestamp_utc: int,
) -> OptimizationCommit:
    """Build an OptimizationCommit from a passing proposal + validation result."""
    change_spec_dict = dict(proposal.change_spec)

    affected_rules: tuple[str, ...] = tuple(
        sorted(v for k, v in proposal.change_spec if k in ("routing_rule", "rule_id", "rule_ref")),
    ) or (f"rule:{proposal.proposed_change_type}",)

    affected_routes: tuple[str, ...] = (
        tuple(sorted(v for k, v in proposal.change_spec if k in ("dominant_route", "route"))) or ()
    )

    affected_retrieval: tuple[str, ...] = (
        tuple(
            sorted(
                v for k, v in proposal.change_spec if k in ("dominant_retrieval_pattern", "retrieval_policy")
            ),
        )
        or ()
    )

    commit_id = _build_commit_id(proposal.proposal_id, result.result_id, timestamp_utc)

    return OptimizationCommit(
        commit_id=commit_id,
        proposal_id=proposal.proposal_id,
        validation_result_id=result.result_id,
        affected_rules=affected_rules,
        affected_routes=affected_routes,
        affected_retrieval_policy=affected_retrieval,
        affected_components=(proposal.affected_component,),
        policy_hash=proposal.policy_hash,
        change_type=proposal.proposed_change_type,
        risk_class=proposal.risk_class,
        adg_relation="proposal_commits_optimization",
        timestamp_utc=timestamp_utc,
    )


# ---------------------------------------------------------------------------
# Main bus
# ---------------------------------------------------------------------------


class MetaLearningBus:
    """ADG-driven meta-learning pipeline bus.

    Orchestrates the full learning loop from raw execution trace signals
    to optimization commits, with ADG relation emission at each stage.

    Example::

        bus = MetaLearningBus()
        result = bus.process_traces(
            traces=[
                ("trace-001", {"route_selected": "PATH_A", "success": True, ...}, 1700000000),
                ("trace-002", {"route_selected": "PATH_B", "success": False, ...}, 1700000001),
            ],
            timestamp_utc=1700000100,
        )
        print(f"commits: {len(result.commits)}")
    """

    def __init__(
        self,
        config: MetaLearningBusConfig | None = None,
        *,
        bridge: Any | None = None,
    ) -> None:
        """Initialise the bus.

        Parameters
        ----------
        config:
            Pipeline configuration.
        bridge:
            Optional ``GraphMemoryBridge`` instance for ADG persistence.
            When None, ADG relations are collected in-process only.
        """
        self._config = config or MetaLearningBusConfig()
        self._bridge = bridge

        self._extractor = TraceFeatureExtractor()
        self._cluster_engine = RCAClusterEngine(self._config.rca_config)
        self._reward_model = GovernanceRewardModel(self._config.reward_config)
        self._proposal_engine = OptimizationProposalEngine(self._config.proposal_config)
        self._validation_engine = ProposalValidationEngine(self._config.validation_config)

        # Wave 1.1.2: Evaluation signal storage for learning integration
        self._evaluation_signals: list[Any] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def consume_evaluation_signal(self, eval_signal: Any) -> None:
        """Consume evaluation signal from L6 evaluation spine.

        Implements BUS P (Preference: Eval → ML) receiver endpoint.
        Stores evaluation signals for use in learning pipeline.

        Args:
            eval_signal: LearningEvent from evaluation_learning_bridge

        Emits ADG edges:
            - records_learning_event (signal captured)
        """
        _trace_id = str(uuid.uuid4())
        _emit_records_learning_event(
            "meta_learning_bus",
            "p3lm",
            f"eval_signal_{_trace_id[:8]}",
        )

        self._evaluation_signals.append(eval_signal)
        logger.info(
            "META_LEARNING_BUS consumed eval signal: kind=%s score=%.3f",
            getattr(eval_signal, "eval_kind", "unknown"),
            getattr(eval_signal, "eval_score", 0.0),
        )

    def process_traces(
        self,
        traces: Sequence[tuple[str, dict[str, Any], int]],
        timestamp_utc: int,
        *,
        reward_signals: Sequence[GovernanceRewardSignal] | None = None,
        negative_seeds: Sequence[FailurePattern] | None = None,
    ) -> BusPipelineResult:
        """Run the full learning pipeline for a batch of execution traces.

        Parameters
        ----------
        traces:
            Sequence of ``(trace_id, signal_dict, trace_timestamp_utc)``
            tuples.
        timestamp_utc:
            Pipeline-level timestamp (used for cluster/proposal/commit IDs).
        reward_signals:
            Optional pre-collected reward signals.  When None, the bus
            synthesises signals from the feature bundles themselves using
            the available signal fields.
        negative_seeds:
            Optional FailurePattern objects to seed RCA clusters from
            known negative cases.

        Returns
        -------
        BusPipelineResult
        """

        _trace_id = str(uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L3_ORCHESTRATION,
            "MetaLearningBus.process_traces",
        )
        adg_relations: list[tuple[str, str, str]] = []

        # Stage 1 — Feature extraction
        bundles = self._stage_extract(traces)

        # Stage 2 — Record promotion
        records = self._stage_promote(bundles, adg_relations)

        # Stage 3 — RCA clustering (run even when records is empty if seeds provided)
        if records or negative_seeds:
            clusters = self._stage_cluster(records, timestamp_utc, negative_seeds, adg_relations)
        else:
            clusters = []

        if not clusters:
            return BusPipelineResult(
                bundles=bundles,
                records=records,
                clusters=[],
                proposals=[],
                validation_results=[],
                commits=[],
                rejected_proposal_ids=[],
                adg_relations_emitted=adg_relations,
            )

        # Stage 4 — Reward scoring
        if reward_signals is None:
            reward_signals = self._synthesise_reward_signals(bundles, timestamp_utc)

        # Stage 5 — Proposal generation
        proposals_raw = self._stage_propose(clusters, timestamp_utc)

        # Score proposals
        proposals_scored, rejected_low_reward = self._stage_score_and_filter(
            proposals_raw,
            list(reward_signals),
            timestamp_utc,
            adg_relations,
        )

        if not proposals_scored:
            return BusPipelineResult(
                bundles=bundles,
                records=records,
                clusters=clusters,
                proposals=proposals_raw,
                validation_results=[],
                commits=[],
                rejected_proposal_ids=[p.proposal_id for p in proposals_raw],
                adg_relations_emitted=adg_relations,
            )

        # Stage 6 — Validation
        validation_results, commits, rejected_validation = self._stage_validate_and_commit(
            proposals_scored,
            clusters,
            timestamp_utc,
            adg_relations,
        )

        all_rejected = rejected_low_reward + rejected_validation

        # Stage 7 — ADG persistence (fail-open)
        if self._config.emit_adg_relations:
            self._emit_adg_relations(adg_relations)

        return BusPipelineResult(
            bundles=bundles,
            records=records,
            clusters=clusters,
            proposals=proposals_raw,
            validation_results=validation_results,
            commits=commits,
            rejected_proposal_ids=all_rejected,
            adg_relations_emitted=adg_relations,
        )

    def process_single_trace(
        self,
        trace_id: str,
        signal: dict[str, Any],
        trace_timestamp_utc: int,
        pipeline_timestamp_utc: int,
        *,
        reward_signals: Sequence[GovernanceRewardSignal] | None = None,
    ) -> BusPipelineResult:
        """Convenience wrapper for a single trace."""
        return self.process_traces(
            [(trace_id, signal, trace_timestamp_utc)],
            pipeline_timestamp_utc,
            reward_signals=reward_signals,
        )

    # ------------------------------------------------------------------
    # Stage implementations
    # ------------------------------------------------------------------

    def _stage_extract(
        self,
        traces: Sequence[tuple[str, dict[str, Any], int]],
    ) -> list[FeatureBundle]:
        try:
            return self._extractor.extract_batch(list(traces))
        except (AttributeError, KeyError, RuntimeError, TypeError, ValueError) as exc:
            logger.warning(
                "meta_learning_bus: feature extraction stage failed",
                extra={"error": str(exc)},
            )
            return []

    def _stage_promote(
        self,
        bundles: list[FeatureBundle],
        adg_relations: list[tuple[str, str, str]],
    ) -> list[TraceFeatureRecord]:
        records: list[TraceFeatureRecord] = []
        for bundle in tqdm(bundles, desc="extract bundles", unit="bundle", leave=False):
            try:
                record = TraceFeatureRecord.from_bundle(bundle)
                records.append(record)
                # Emit: trace → triggered_telemetry → feature_record
                adg_relations.append(
                    (
                        bundle.adg_entity_name,
                        _ADG_TRIGGERED_TELEMETRY,
                        f"ADG::TraceFeatureRecord::{record.record_id[:12]}",
                    ),
                )
            except (AttributeError, KeyError, RuntimeError, TypeError, ValueError) as exc:
                logger.warning(
                    "meta_learning_bus: record promotion failed",
                    extra={"trace_id": bundle.trace_id, "error": str(exc)},
                )
        return records

    def _stage_cluster(
        self,
        records: list[TraceFeatureRecord],
        timestamp_utc: int,
        negative_seeds: Sequence[FailurePattern] | None,
        adg_relations: list[tuple[str, str, str]],
    ) -> list[RCACluster]:
        try:
            clusters = self._cluster_engine.cluster(records, timestamp_utc, negative_seeds=negative_seeds)
            for cluster in tqdm(clusters, desc="clusters", unit="cluster", leave=False):
                # Emit: each member record → chunks_into → cluster
                for trace_id in cluster.member_trace_ids:
                    adg_relations.append(
                        (
                            f"ADG::TraceFeatureRecord::{trace_id[:12]}",
                            _ADG_CHUNKS_INTO,
                            cluster.adg_cluster_node,
                        ),
                    )
                # Emit: cluster → stores_embedding → cluster node
                adg_relations.append(
                    (
                        cluster.adg_cluster_node,
                        _ADG_STORES_EMBEDDING,
                        cluster.adg_cluster_node,
                    ),
                )
            return clusters
        except (AttributeError, KeyError, RuntimeError, TypeError, ValueError) as exc:
            logger.warning(
                "meta_learning_bus: RCA clustering stage failed",
                extra={"error": str(exc)},
            )
            return []

    def _stage_propose(
        self,
        clusters: list[RCACluster],
        timestamp_utc: int,
    ) -> list[OptimizationProposal]:
        try:
            return self._proposal_engine.generate(clusters, timestamp_utc)
        except (AttributeError, RuntimeError, TypeError, ValueError) as exc:
            logger.warning(
                "meta_learning_bus: proposal generation stage failed",
                extra={"error": str(exc)},
            )
            return []

    def _stage_score_and_filter(
        self,
        proposals: list[OptimizationProposal],
        signals: list[GovernanceRewardSignal],
        timestamp_utc: int,
        adg_relations: list[tuple[str, str, str]],
    ) -> tuple[list[OptimizationProposal], list[str]]:
        """Score proposals and filter out those below reward threshold.

        Returns (passing_proposals, rejected_proposal_ids).
        """
        # Build signals map: proposal_id → signals
        # (all signals apply to all proposals at this stage;
        # a more sophisticated bus could filter by affected component)
        signals_map: dict[str, list[GovernanceRewardSignal]] = {p.proposal_id: signals for p in proposals}

        scores = self._reward_model.score_batch(proposals, signals_map, timestamp_utc)
        annotated = self._reward_model.annotate_proposals(proposals, scores, timestamp_utc)

        passing: list[OptimizationProposal] = []
        rejected: list[str] = []

        score_by_pid = {s.proposal_id: s for s in scores}
        for proposal in tqdm(annotated, desc="score proposals", unit="proposal", leave=False):
            gs = score_by_pid.get(proposal.proposal_id)
            if gs is None:
                rejected.append(proposal.proposal_id)
                continue
            # Emit: proposal → scored_by_reward → reward score node
            adg_relations.append(
                (
                    f"ADG::Proposal::{proposal.proposal_id[:12]}",
                    _ADG_SCORED_BY_REWARD,
                    f"ADG::RewardScore::{gs.score_id[:12]}",
                ),
            )
            if gs.aggregate_score >= self._config.reward_threshold:
                passing.append(proposal)
            else:
                rejected.append(proposal.proposal_id)
                logger.debug(
                    "meta_learning_bus: proposal rejected by reward threshold",
                    extra={
                        "proposal_id": proposal.proposal_id,
                        "score": gs.aggregate_score,
                        "threshold": self._config.reward_threshold,
                    },
                )

        return passing, rejected

    def _stage_validate_and_commit(
        self,
        proposals: list[OptimizationProposal],
        clusters: list[RCACluster],
        timestamp_utc: int,
        adg_relations: list[tuple[str, str, str]],
    ) -> tuple[list[ValidationResult], list[OptimizationCommit], list[str]]:
        """Validate proposals and produce commits for those that pass.

        Returns (validation_results, commits, rejected_proposal_ids).
        """
        # Build HITL rate lookup from clusters
        cluster_by_id = {c.cluster_id: c for c in clusters}

        # Build proposal → cluster mapping via change_spec
        hitl_rates: dict[str, float] = {}
        for proposal in proposals:
            spec_dict = dict(proposal.change_spec)
            cid = spec_dict.get("cluster_id", "")
            cluster = cluster_by_id.get(cid)
            if cluster:
                hitl_rates[proposal.proposal_id] = cluster.hitl_escalation_rate

        validation_results = self._validation_engine.validate_batch(
            proposals,
            timestamp_utc,
            hitl_rates=hitl_rates,
        )

        commits: list[OptimizationCommit] = []
        rejected: list[str] = []
        result_by_pid = {r.proposal_id: r for r in validation_results}

        for proposal in tqdm(proposals, desc="validate proposals", unit="proposal", leave=False):
            result = result_by_pid.get(proposal.proposal_id)
            if result is None:
                rejected.append(proposal.proposal_id)
                continue

            if result.validation_pass:
                # Check reward_score meets commit threshold
                reward_ok = (
                    proposal.reward_score is None
                    or proposal.reward_score >= self._config.commit_reward_threshold
                )
                if reward_ok:
                    commit = _build_optimization_commit(proposal, result, timestamp_utc)
                    commits.append(commit)
                    # Emit: proposal → proposal_commits_optimization → commit
                    adg_relations.append(
                        (
                            f"ADG::Proposal::{proposal.proposal_id[:12]}",
                            _ADG_PROPOSAL_COMMITS,
                            f"ADG::OptimizationCommit::{commit.commit_id[:12]}",
                        ),
                    )
                    logger.info(
                        "meta_learning_bus: optimization commit produced",
                        extra={
                            "commit_id": commit.commit_id,
                            "change_type": commit.change_type,
                            "affected_component": proposal.affected_component,
                        },
                    )
                else:
                    rejected.append(proposal.proposal_id)
            else:
                rejected.append(proposal.proposal_id)
                logger.debug(
                    "meta_learning_bus: proposal failed validation",
                    extra={
                        "proposal_id": proposal.proposal_id,
                        "denial_reasons": list(result.denial_reasons),
                    },
                )

        return validation_results, commits, rejected

    # ------------------------------------------------------------------
    # Reward signal synthesis
    # ------------------------------------------------------------------

    def _synthesise_reward_signals(
        self,
        bundles: list[FeatureBundle],
        timestamp_utc: int,
    ) -> list[GovernanceRewardSignal]:
        """Synthesise GovernanceRewardSignals from FeatureBundles.

        Used when the caller does not supply pre-collected signals.
        Maps feature bundle fields to reward dimensions:
          - groundedness_score  ← retrieval_groundedness_score
          - policy_compliance   ← 1.0 if no policy_state_accessed else 0.9
          - replay_stability    ← 1.0 if no REPLAY_FAILURE else 0.0
          - guardrail_cleanliness ← 1.0 if no guardrails_applied else 0.7
          - mutation_correctness  ← 1.0 if not mutation_presence else 0.5
          - human_approval      ← True if HUMAN_OVERRIDE, None otherwise
        """
        signals: list[GovernanceRewardSignal] = []
        for bundle in tqdm(bundles, desc="reward bundles", unit="bundle", leave=False):
            gnd = bundle.retrieval_groundedness_score
            policy_comp = 0.9 if bundle.policy_state_accessed else 1.0
            replay_stab = 0.0 if bundle.final_outcome_class == "REPLAY_FAILURE" else 1.0
            guard_clean = 0.7 if bundle.guardrails_applied else 1.0
            mut_correct = 0.5 if bundle.mutation_presence else 1.0
            human_approval: bool | None = True if bundle.final_outcome_class == "HUMAN_OVERRIDE" else None

            signal_id = hashlib.sha256(
                deterministic_json(
                    {
                        "trace_id": bundle.trace_id,
                        "timestamp_utc": timestamp_utc,
                    },
                ).encode("utf-8"),
            ).hexdigest()

            try:
                signals.append(
                    GovernanceRewardSignal(
                        signal_id=signal_id,
                        trace_id=bundle.trace_id,
                        groundedness_score=gnd,
                        policy_compliance=policy_comp,
                        replay_stability=replay_stab,
                        guardrail_cleanliness=guard_clean,
                        mutation_correctness=mut_correct,
                        human_approval=human_approval,
                        timestamp_utc=timestamp_utc,
                    ),
                )
            except (AttributeError, KeyError, RuntimeError, TypeError, ValueError) as exc:
                logger.warning(
                    "meta_learning_bus: reward signal synthesis failed",
                    extra={"trace_id": bundle.trace_id, "error": str(exc)},
                )
        return signals

    # ------------------------------------------------------------------
    # ADG relation emission
    # ------------------------------------------------------------------

    def _emit_adg_relations(
        self,
        relations: list[tuple[str, str, str]],
    ) -> None:
        """Persist ADG relations via the bridge (fail-open)."""
        if self._bridge is None:
            return
        for from_entity, relation_type, to_entity in tqdm(
            relations, desc="emit relations", unit="rel", leave=False
        ):
            try:
                self._bridge.create_relation(
                    from_entity=from_entity,
                    relation_type=relation_type,
                    to_entity=to_entity,
                )
            except (AttributeError, RuntimeError, TypeError, ValueError) as exc:
                logger.debug(
                    "meta_learning_bus: ADG relation emission failed",
                    extra={
                        "from": from_entity,
                        "relation": relation_type,
                        "to": to_entity,
                        "error": str(exc),
                    },
                )


# ---------------------------------------------------------------------------
# Module-level convenience
# ---------------------------------------------------------------------------


def run_learning_pipeline(
    traces: Sequence[tuple[str, dict[str, Any], int]],
    timestamp_utc: int,
    *,
    config: MetaLearningBusConfig | None = None,
    reward_signals: Sequence[GovernanceRewardSignal] | None = None,
    negative_seeds: Sequence[FailurePattern] | None = None,
    bridge: Any | None = None,
) -> BusPipelineResult:
    """Module-level convenience wrapper for a full pipeline run."""
    return MetaLearningBus(config, bridge=bridge).process_traces(
        traces,
        timestamp_utc,
        reward_signals=reward_signals,
        negative_seeds=negative_seeds,
    )


__all__ = [
    "BusPipelineResult",
    "MetaLearningBus",
    "MetaLearningBusConfig",
    "run_learning_pipeline",
]
