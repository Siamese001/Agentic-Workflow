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

from system_learning.enforcement.determinism import deterministic_json
from system_learning.types.optimization_types import OptimizationProposal
from system_learning.types.trace_feature_types import RCACluster

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
        }
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
    "generate_proposals",
]
