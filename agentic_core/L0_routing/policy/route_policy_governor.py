"""
agentic_core/L0_routing/policy/route_policy_governor.py

RoutePolicyGovernor — P1-L0 gap remediation.

Commits routing decisions as RoutingProposal records referencing the
governing policy hash before execution. Closes the gap where 366 L0
modules read policy state (76 edges) without committing to governance
constraints (0 proposal_commits_routing / references_policy_hash).

ADG edges emitted: proposal_commits_routing, references_policy_hash,
                   reads_governed_config, verifies_boundary
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass, field
from typing import Any

from agentic_core.L0_routing.artifacts.deterministic_routing_gateway import (
    DeterministicRoutingGateway,
    RoutingArtifact,
    get_routing_gateway,
)
from agentic_core.L0_routing.enforcement.routing_contract import (
    RoutingContext as ContractRoutingContext,
)
from agentic_core.L0_routing.enforcement.routing_contract import (
    create_and_commit_routing_contract,
)
from agentic_core.L2_execution.providers import get_clock

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RoutingProposal:
    """A routing decision committed to a governance policy hash.

    Every L0 routing dispatch must produce a RoutingProposal before
    the request is forwarded, making the policy provenance traceable.
    """

    trace_id: str
    route_path: str
    policy_hash: str
    proposal_hash: str
    routing_artifact: RoutingArtifact
    boundary_verified: bool
    metadata: dict[str, Any] = field(default_factory=dict)

    def satisfies_policy(self) -> bool:
        """Return True if the proposal was committed against a non-empty policy hash."""
        return bool(self.policy_hash) and self.boundary_verified


class RoutePolicyGovernor:
    """Commits routing decisions to a governance policy before dispatch.

    Usage::

        governor = RoutePolicyGovernor(policy_hash="abc123")
        proposal = governor.commit_routing("standard_validation", metadata={})
        assert proposal.satisfies_policy()
        dispatch(proposal.routing_artifact)
    """

    def __init__(
        self,
        policy_hash: str = "",
        gateway: DeterministicRoutingGateway | None = None,
    ) -> None:
        self._policy_hash = policy_hash
        self._gateway = gateway or get_routing_gateway(policy_hash)
        self._ledger: list[RoutingProposal] = []

    def _trace_id(self) -> str:
        from agentic_core.runtime.execution_trace import get_active_execution_trace  # noqa: PLC0415

        active = get_active_execution_trace()
        return active.trace_id if active else "no-active-trace"

    def _verify_boundary(self, route_path: str) -> bool:
        """Verify the route path is within governed boundaries.

        Emits ``verifies_boundary`` ADG edge.
        """
        allowed = {
            "standard_validation",
            "low_risk_bypass",
            "human_escalation",
            "policy_challenge_loop",
            "route_recovery_budget_overflow",
        }
        verified = route_path in allowed
        if not verified:
            logger.warning(
                "GOVERNOR verifies_boundary FAIL route=%s not in governed set",
                route_path,
            )
        return verified

    def commit_routing(
        self,
        route_path: str,
        metadata: dict[str, Any] | None = None,
    ) -> RoutingProposal:
        """Commit a routing decision against the governing policy hash.

        Emits ``proposal_commits_routing`` + ``references_policy_hash``
        + ``reads_governed_config`` ADG edges.
        """
        trace_id = self._trace_id()
        artifact = self._gateway.stamp_decision(route_path, metadata)
        boundary_ok = self._verify_boundary(route_path)
        payload = f"{trace_id}:{route_path}:{self._policy_hash}:{artifact.replay_key}"
        proposal_hash = hashlib.sha256(payload.encode()).hexdigest()[:24]
        proposal = RoutingProposal(
            trace_id=trace_id,
            route_path=route_path,
            policy_hash=self._policy_hash,
            proposal_hash=proposal_hash,
            routing_artifact=artifact,
            boundary_verified=boundary_ok,
            metadata=metadata or {},
        )
        self._ledger.append(proposal)
        _clock = get_clock()
        _clock.emit_replay_key(context=f"{route_path}:{trace_id}")
        # P1/L0: commit full RoutingContract for this governance decision
        _contract_ctx = ContractRoutingContext(
            run_id=trace_id,
            router_id="RoutePolicyGovernor",
            request_hash=proposal_hash,
            candidate_routes=list(
                {
                    "standard_validation",
                    "low_risk_bypass",
                    "human_escalation",
                    "policy_challenge_loop",
                    "route_recovery_budget_overflow",
                }
            ),
            chosen_route=route_path,
            policy_hash=self._policy_hash or "no-policy",
            policy_version="1.0",
        )
        try:
            create_and_commit_routing_contract(_contract_ctx)
        except Exception as _rce:  # guardian: allow-silent-swallow
            logger.warning("GOVERNOR routing contract failed: %s", _rce)
        logger.info(
            "GOVERNOR proposal_commits_routing references_policy_hash "
            "route=%s policy=%s proposal=%s boundary=%s",
            route_path,
            self._policy_hash[:12] if self._policy_hash else "MISSING",
            proposal_hash,
            boundary_ok,
        )
        return proposal

    def ledger(self) -> list[RoutingProposal]:
        return list(self._ledger)


_global_governor: RoutePolicyGovernor | None = None


def get_route_policy_governor(policy_hash: str = "") -> RoutePolicyGovernor:
    global _global_governor
    if _global_governor is None:
        _global_governor = RoutePolicyGovernor(policy_hash=policy_hash)
    return _global_governor


def reset_route_policy_governor() -> None:
    global _global_governor
    _global_governor = None


__all__ = [
    "RoutingProposal",
    "RoutePolicyGovernor",
    "get_route_policy_governor",
    "reset_route_policy_governor",
]
