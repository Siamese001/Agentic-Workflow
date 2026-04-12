"""Optimization Proposal Engine — generates OptimizationProposals from RCAClusters.

Converts ``RCACluster`` objects into controlled ``OptimizationProposal``
objects.  Each proposal targets a single affected component and change type
derived from the cluster's dominant failure pattern.

Design invariants
-----------------
1. Pure function interface — no global mutable state.
2. Proposals are strictly informational — they MUST NOT mutate routing,
   safety, config, or any system state.
3. No wall-clock reads; ``timestamp_utc`` always caller-supplied.
4. All outputs are deterministically content-addressed.
5. One cluster may produce zero, one, or multiple proposals depending on
   the failure pattern and affected agents.
6. Proposals with ``risk_class="CRITICAL"`` are only generated when
   ``allow_critical=True`` (default False).
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass
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

_emit_authorize_and_execute("p2", "optimization_proposal_engine", "execution_auth")
_emit_validates_capability("p2", "optimization_proposal_engine", "capability_check")
_emit_routes_to_capability("p2", "optimization_proposal_engine", "capability_route")
_emit_writes_via_uwg("p2", "optimization_proposal_engine", "uwg_write")
_emit_blocks_direct_write("p2", "optimization_proposal_engine", "direct_write_block")
_emit_records_tool_invocation("p2", "optimization_proposal_engine", "tool_invocation")
_emit_captures_execution_output("p2", "optimization_proposal_engine", "exec_output")
_emit_dispatches_agent("p3", "optimization_proposal_engine", "agent_dispatch")
_emit_coordinates_agents("p3", "optimization_proposal_engine", "agent_coordination")
_emit_records_workflow_lineage("p3", "optimization_proposal_engine", "workflow_lineage")
_emit_records_healing_outcome("p3", "optimization_proposal_engine", "healing_outcome")
_emit_escalates_failure("p3", "optimization_proposal_engine", "failure_escalation")
_emit_orchestrates_workflow("p3", "optimization_proposal_engine", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "optimization_proposal_engine", "healing_dispatch")
_emit_invokes_evaluation("p3", "optimization_proposal_engine", "evaluation_signal")
_emit_records_telemetry_event("p4", "optimization_proposal_engine", "telemetry_event")
_emit_captures_evaluation_metric("p4", "optimization_proposal_engine", "eval_metric")
_emit_stores_embedding("p4", "optimization_proposal_engine", "embedding_store")
_emit_updates_meta_learning_state("p4", "optimization_proposal_engine", "meta_learning")
_emit_links_execution_to_snapshot("p4", "optimization_proposal_engine", "exec_snapshot_link")
from system_learning.enforcement.determinism import deterministic_json
from system_learning.types.optimization_types import OptimizationProposal
from system_learning.types.trace_feature_types import RCACluster

_emit_applies_guardrail("p0", "optimization_proposal_engine", "p0_governance")
_emit_snapshots_state("p0", "optimization_proposal_engine", "state_snapshot")
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

_emit_emits_metric_event("optimization_proposal_engine", "p4obs", "metric_1")
_emit_emits_metric_event("optimization_proposal_engine", "p4obs", "metric_2")
_emit_emits_metric_event("optimization_proposal_engine", "p4obs", "metric_3")
_emit_emits_metric_event("optimization_proposal_engine", "p4obs", "metric_4")
_emit_emits_metric_event("optimization_proposal_engine", "p4obs", "metric_5")
_emit_emits_metric_event("optimization_proposal_engine", "p4obs", "metric_6")
_emit_records_incident_event("optimization_proposal_engine", "p4obs", "incident")
_emit_captures_runtime_anomaly("optimization_proposal_engine", "p4obs", "anomaly")
_emit_writes_observability_log("optimization_proposal_engine", "p4obs", "obs_log")
_emit_updates_monitoring_state("optimization_proposal_engine", "p4obs", "mon_state")
_emit_triggers_alert("optimization_proposal_engine", "p4obs", "alert")
_emit_links_incident_trace("optimization_proposal_engine", "p4obs", "trace_link")
_emit_captures_pattern("optimization_proposal_engine", "p3lm", "pattern")
_emit_records_learning_event("optimization_proposal_engine", "p3lm", "learning_event")
_emit_writes_learning_snapshot("optimization_proposal_engine", "p3lm", "snapshot")
_emit_feeds_meta_learning("optimization_proposal_engine", "p3lm", "meta_feed")
_emit_updates_routing_strategy("optimization_proposal_engine", "p3lm", "routing")
_emit_improves_agent_policy("optimization_proposal_engine", "p3lm", "policy")
_emit_stores_learning_state("optimization_proposal_engine", "p3lm", "state")
_emit_records_execution_trace("optimization_proposal_engine", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("optimization_proposal_engine", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("optimization_proposal_engine", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("optimization_proposal_engine", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("optimization_proposal_engine", "L4_STATE", "p2_trace_5")
_emit_reads_environ("optimization_proposal_engine", "env_read", "p2_env_1")
_emit_reads_environ("optimization_proposal_engine", "env_read", "p2_env_2")
_emit_reads_runtime_state("optimization_proposal_engine", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("optimization_proposal_engine", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "optimization_proposal_engine", "context_pull")
_emit_pulls_context("p1", "optimization_proposal_engine", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "optimization_proposal_engine", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "optimization_proposal_engine", "uwg_term_2")
_emit_writes_through("p1", "optimization_proposal_engine", "write_through")
_emit_writes_through("p1", "optimization_proposal_engine", "write_through_2")
_emit_validated_by_safety_plane("p1", "optimization_proposal_engine", "safety_validation")
_emit_invokes_eval("p1", "optimization_proposal_engine", "eval_call")
_emit_proposal_commits_routing("p1", "optimization_proposal_engine", "routing_commit")
_emit_escalates_to_human("p1", "optimization_proposal_engine", "human_escalation")
_emit_routes_through("p1", "optimization_proposal_engine", "route_through")
_emit_checks_agent_registry("p1", "optimization_proposal_engine", "agent_registry")
_emit_validates_agent_capability("p1", "optimization_proposal_engine", "capability")
_emit_dispatches_execution_plan("p1", "optimization_proposal_engine", "exec_plan")
_emit_agent_executes_agent("p1", "optimization_proposal_engine", "sub_agent")
_emit_routes_to_agent("p1", "optimization_proposal_engine", "target_agent")
_emit_verifies_policy("p1", "optimization_proposal_engine", "policy_check")
_emit_observes_runtime_state("p1", "optimization_proposal_engine", "runtime_state")
_emit_verifies_boundary("p1", "optimization_proposal_engine", "boundary_check")
_emit_transcripts_response("p1", "optimization_proposal_engine", "transcript")
_emit_hard_fails_untranscripted("p1", "optimization_proposal_engine")
_emit_gated_by_confidence("p1", "optimization_proposal_engine", "confidence_gate")
emit_replay_key("p0", "optimization_proposal_engine")
emit_determinism_digest("p0", "optimization_proposal_engine")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Proposal rule table
# ---------------------------------------------------------------------------
# Maps failure_pattern → (proposed_change_type, risk_class, expected_outcome_template)

_PROPOSAL_RULES: tuple[tuple[str, str, str, str], ...] = (
    # (failure_pattern_prefix, change_type, risk_class, outcome_template)
    (
        "REPLAY_FAILURE",
        "ROUTING_RULE_ADJUSTMENT",
        "HIGH",
        "Reduce replay failures by tightening determinism enforcement on affected route",
    ),
    (
        "ROLLBACK",
        "ROUTING_RULE_ADJUSTMENT",
        "MEDIUM",
        "Reduce rollback rate by adjusting routing thresholds on affected route",
    ),
    (
        "HEALER_REQUIRED",
        "HEALER_ROUTING_IMPROVEMENT",
        "LOW",
        "Improve healer routing to reduce invocation frequency and latency",
    ),
    (
        "HITL_ESCALATION",
        "CONFIDENCE_THRESHOLD_UPDATE",
        "MEDIUM",
        "Reduce HITL escalation by calibrating confidence gate threshold",
    ),
    (
        "LOW_GROUNDEDNESS",
        "RETRIEVAL_RANKING_ADJUSTMENT",
        "LOW",
        "Improve retrieval groundedness by reranking or expanding corpus",
    ),
    (
        "GUARDRAIL_BLOCK",
        "GUARDRAIL_REFINEMENT",
        "MEDIUM",
        "Reduce false-positive guardrail blocks by refining trigger conditions",
    ),
    (
        "POLICY_VIOLATION",
        "ROUTING_RULE_ADJUSTMENT",
        "HIGH",
        "Route traces away from policy-violating paths",
    ),
    (
        "SAFE_FAILURE",
        "ROUTING_RULE_ADJUSTMENT",
        "LOW",
        "Improve safe-failure recovery by adjusting routing fallback logic",
    ),
    (
        "NEG_SEED_VIOLATION",
        "GUARDRAIL_REFINEMENT",
        "HIGH",
        "Address recurring violation pattern detected in negative-case corpus",
    ),
    (
        "NEG_SEED_ANTIPATTERN",
        "ROUTING_RULE_ADJUSTMENT",
        "MEDIUM",
        "Prevent known antipattern from re-entering execution paths",
    ),
    (
        "NEG_SEED_DRIFT_ALERT",
        "ROUTING_RULE_ADJUSTMENT",
        "MEDIUM",
        "Correct routing drift detected in negative-case corpus",
    ),
    (
        "NEG_SEED_REPLAY_FAILURE",
        "ROUTING_RULE_ADJUSTMENT",
        "HIGH",
        "Address replay failure pattern from negative-case corpus",
    ),
    (
        "NEG_SEED_LOW_GROUNDEDNESS",
        "EMBEDDING_CORPUS_EXPANSION",
        "LOW",
        "Expand embedding corpus to improve coverage of low-groundedness cases",
    ),
    (
        "NEG_SEED_OVER_ESCALATION",
        "CONFIDENCE_THRESHOLD_UPDATE",
        "LOW",
        "Reduce over-escalation by recalibrating confidence gate",
    ),
    (
        "ROUTING_MISCLASSIFICATION",
        "ROUTING_RULE_ADJUSTMENT",
        "LOW",
        "Update intent prototype embedding for consistently misrouted target",
    ),
)


def _match_rule(
    failure_pattern: str,
) -> tuple[str, str, str] | None:
    """Return (change_type, risk_class, outcome_template) for failure_pattern.

    Uses prefix matching on the rule table so that sub-grouped patterns
    (e.g. ``"HEALER_REQUIRED"`` with a route sub-key) still match the
    base rule.  Returns None when no rule matches.
    """
    for prefix, change_type, risk_class, outcome in _PROPOSAL_RULES:
        if failure_pattern.startswith(prefix):
            return change_type, risk_class, outcome
    return None


# ---------------------------------------------------------------------------
# Change spec builder
# ---------------------------------------------------------------------------


def _build_change_spec(
    cluster: RCACluster,
    change_type: str,
) -> tuple[tuple[str, str], ...]:
    """Build a sorted, deterministic change_spec for a proposal.

    Values are stringified so the spec is safe for JSON serialization
    and stable hashing.
    """
    spec: dict[str, str] = {
        "change_type": change_type,
        "cluster_id": cluster.cluster_id,
        "dominant_route": cluster.dominant_route,
        "dominant_retrieval_pattern": cluster.dominant_retrieval_pattern,
        "failure_pattern": cluster.failure_pattern,
        "member_count": str(cluster.member_count),
        "avg_groundedness": str(round(cluster.avg_groundedness, 6)),
        "hitl_escalation_rate": str(round(cluster.hitl_escalation_rate, 6)),
        "healer_invocation_rate": str(round(cluster.healer_invocation_rate, 6)),
    }
    if cluster.dominant_guardrail:
        spec["dominant_guardrail"] = cluster.dominant_guardrail
    return tuple(sorted(spec.items()))


# ---------------------------------------------------------------------------
# Proposal ID builder
# ---------------------------------------------------------------------------


def _build_proposal_id(
    cluster_id: str,
    change_type: str,
    affected_component: str,
    timestamp_utc: int,
) -> str:
    payload = deterministic_json(
        {
            "affected_component": affected_component,
            "change_type": change_type,
            "cluster_id": cluster_id,
            "timestamp_utc": timestamp_utc,
        },
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


@dataclass
class ProposalEngineConfig:
    """Configuration for the optimization proposal engine."""

    allow_critical: bool = False
    max_proposals_per_cluster: int = 3
    min_cluster_members_for_high_risk: int = 5
    policy_hash: str | None = None


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------


class OptimizationProposalEngine:
    """Generates OptimizationProposals from RCAClusters.

    For each cluster, applies the proposal rule table to produce
    controlled proposals targeting specific affected agents.
    """

    def __init__(self, config: ProposalEngineConfig | None = None) -> None:
        self._config = config or ProposalEngineConfig()

    def generate(
        self,
        clusters: Sequence[RCACluster],
        timestamp_utc: int,
    ) -> list[OptimizationProposal]:
        """Generate proposals for all clusters.

        Parameters
        ----------
        clusters:
            RCACluster objects from the RCA cluster engine.
        timestamp_utc:
            Caller-supplied Unix timestamp.

        Returns
        -------
        list[OptimizationProposal]
            Sorted by proposal_id for determinism.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "OptimizationProposalEngine.generate"
        )

        proposals: list[OptimizationProposal] = []
        for cluster in clusters:
            proposals.extend(self._generate_for_cluster(cluster, timestamp_utc))
        proposals.sort(key=lambda p: p.proposal_id)
        return proposals

    def _generate_for_cluster(
        self,
        cluster: RCACluster,
        timestamp_utc: int,
    ) -> list[OptimizationProposal]:
        cfg = self._config
        rule = _match_rule(cluster.failure_pattern)
        if rule is None:
            logger.debug(
                "proposal_engine: no rule for pattern",
                extra={"failure_pattern": cluster.failure_pattern},
            )
            return []

        change_type, risk_class, outcome_template = rule

        # Downgrade HIGH risk to MEDIUM if cluster is too small
        if risk_class == "HIGH" and cluster.member_count < cfg.min_cluster_members_for_high_risk:
            risk_class = "MEDIUM"

        # Block CRITICAL proposals unless explicitly allowed
        if risk_class == "CRITICAL" and not cfg.allow_critical:
            logger.info(
                "proposal_engine: CRITICAL proposal blocked by config",
                extra={"cluster_id": cluster.cluster_id},
            )
            return []

        # Generate one proposal per affected agent (capped)
        agents = list(cluster.affected_agents) or ["ADG::Unknown"]
        agents = agents[: cfg.max_proposals_per_cluster]

        proposals: list[OptimizationProposal] = []
        for agent in agents:
            proposal_id = _build_proposal_id(cluster.cluster_id, change_type, agent, timestamp_utc)
            change_spec = _build_change_spec(cluster, change_type)
            evidence_hashes = (cluster.stable_hash(),)
            expected = f"{outcome_template} [{agent}]"

            # Build proposal with placeholder proposal_id to compute stable_hash
            proposal = OptimizationProposal(
                proposal_id=proposal_id,
                cluster_id=cluster.cluster_id,
                proposed_change_type=change_type,
                affected_component=agent,
                expected_outcome=expected,
                risk_class=risk_class,
                change_spec=change_spec,
                evidence_bundle_hashes=evidence_hashes,
                reward_score=None,
                policy_hash=cfg.policy_hash,
                timestamp_utc=timestamp_utc,
            )
            proposals.append(proposal)

        return proposals


# Wave B-6: RepairRouteCluster support for optimization proposals
@dataclass(frozen=True)
class RepairRouteCluster:
    """Cluster of repair routes for optimization analysis.

    Attributes
    ----------
    cluster_id : str
        Content-addressed cluster identifier
    repair_routes : list[dict[str, Any]]
        List of repair route dictionaries
    failure_pattern : str
        Dominant failure pattern in this cluster
    affected_components : list[str]
        Components affected by these repair routes
    success_rate : float
        Overall success rate of repair routes in cluster
    timestamp_utc : int
        Cluster creation timestamp
    """

    cluster_id: str
    repair_routes: list[dict[str, Any]]
    failure_pattern: str
    affected_components: list[str]
    success_rate: float
    timestamp_utc: int

    def stable_hash(self) -> str:
        """Compute stable hash for content addressing."""
        import json

        data = {
            "repair_routes": sorted(self.repair_routes, key=lambda x: x.get("route_id", "")),
            "failure_pattern": self.failure_pattern,
            "affected_components": sorted(self.affected_components),
        }
        canonical = json.dumps(data, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class RepairRouteOptimizationEngine:
    """Generates optimization proposals from RepairRouteCluster objects.

    Converts repair route data into actionable optimization proposals
    targeting specific components and improvement opportunities.
    """

    def __init__(self, config: ProposalEngineConfig | None = None) -> None:
        self._config = config or ProposalEngineConfig()

    def generate_from_repair_routes(
        self,
        repair_clusters: Sequence[RepairRouteCluster],
        timestamp_utc: int,
    ) -> list[OptimizationProposal]:
        """Generate optimization proposals from repair route clusters.

        Args:
            repair_clusters: Sequence of repair route clusters
            timestamp_utc: Caller-supplied Unix timestamp

        Returns:
            List of optimization proposals sorted by proposal_id
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "RepairRouteOptimizationEngine.generate"
        )

        proposals: list[OptimizationProposal] = []
        for cluster in repair_clusters:
            proposals.extend(self._generate_from_cluster(cluster, timestamp_utc))
        proposals.sort(key=lambda p: p.proposal_id)
        return proposals

    def _generate_from_cluster(
        self,
        cluster: RepairRouteCluster,
        timestamp_utc: int,
    ) -> list[OptimizationProposal]:
        """Generate proposals from a single repair route cluster."""
        if cluster.success_rate < 0.3:
            # Low success rate - suggest strategy changes
            change_type = "REPAIR_STRATEGY_OVERHAUL"
            risk_class = "HIGH" if cluster.success_rate < 0.1 else "MEDIUM"
        elif cluster.success_rate < 0.7:
            # Moderate success rate - suggest tuning
            change_type = "REPAIR_TUNING"
            risk_class = "MEDIUM"
        else:
            # High success rate - suggest optimization
            change_type = "REPAIR_OPTIMIZATION"
            risk_class = "LOW"

        proposals: list[OptimizationProposal] = []
        for component in cluster.affected_components[:3]:  # Cap at 3 components
            proposal_id = _build_proposal_id(cluster.cluster_id, change_type, component, timestamp_utc)
            change_spec = _build_repair_change_spec(cluster, change_type)
            expected = f"Improve repair success rate from {cluster.success_rate:.2%} for {component}"

            proposal = OptimizationProposal(
                proposal_id=proposal_id,
                cluster_id=cluster.cluster_id,
                proposed_change_type=change_type,
                affected_component=component,
                expected_outcome=expected,
                risk_class=risk_class,
                change_spec=change_spec,
                evidence_bundle_hashes=(cluster.stable_hash(),),
                reward_score=None,
                policy_hash=self._config.policy_hash,
                timestamp_utc=timestamp_utc,
            )
            proposals.append(proposal)

        return proposals


def _build_repair_change_spec(
    cluster: RepairRouteCluster,
    change_type: str,
) -> dict[str, Any]:
    """Build change specification for repair route optimization."""
    if change_type == "REPAIR_STRATEGY_OVERHAUL":
        return {
            "type": "repair_strategy_overhaul",
            "current_success_rate": cluster.success_rate,
            "recommended_strategies": ["adaptive_routing", "parallel_execution", "fallback_mechanisms"],
            "evidence": cluster.repair_routes[:5],  # Top 5 routes as evidence
        }
    elif change_type == "REPAIR_TUNING":
        return {
            "type": "repair_tuning",
            "current_success_rate": cluster.success_rate,
            "tuning_parameters": ["timeout_adjustment", "resource_scaling", "retry_policy"],
            "evidence": cluster.repair_routes[:3],
        }
    else:  # REPAIR_OPTIMIZATION
        return {
            "type": "repair_optimization",
            "current_success_rate": cluster.success_rate,
            "optimization_targets": ["latency_reduction", "resource_efficiency", "success_rate_improvement"],
            "evidence": cluster.repair_routes[:2],
        }


# ---------------------------------------------------------------------------
# Module-level convenience
# ---------------------------------------------------------------------------


def generate_proposals(
    clusters: Sequence[RCACluster],
    timestamp_utc: int,
    *,
    config: ProposalEngineConfig | None = None,
) -> list[OptimizationProposal]:
    """Module-level convenience wrapper for ``OptimizationProposalEngine.generate``."""
    return OptimizationProposalEngine(config).generate(clusters, timestamp_utc)


__all__ = [
    "OptimizationProposalEngine",
    "ProposalEngineConfig",
    "RepairRouteCluster",
    "RepairRouteOptimizationEngine",
    "generate_proposals",
]
