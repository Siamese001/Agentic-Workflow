"""L5 Governance v4 — Identity Propagator (G-04 / G-05).

Binds and propagates the principal chain ``invoking_user → agent → parent →
tool/connector`` across handoffs. Enforces ``delegation_depth <= max``.
Tracks principal-chain propagation completeness and delegation-depth
breaches.

Reference
---------
``docs/reference/00_L5_Policy_Plane/Governance & Safety v4.md`` G-04, G-05;
``docs/contracts/identity_propagation.md``.

KPI surface
-----------
- ``PRINCIPAL_CHAIN_PROPAGATION_COMPLETENESS`` (ratio, GE 1.0)
- ``DELEGATION_DEPTH_BREACHES`` (count, EQ 0)
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, replace
from typing import Any

from system_learning.engines.governance_v4.capability_token import PrincipalChain

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PropagationResult:
    """Outcome of one propagate() call."""

    new_chain: PrincipalChain
    accepted: bool
    reason: str


class IdentityPropagator:
    """Propagate identity across A2A handoffs (G-05)."""

    DEFAULT_MAX_DEPTH: int = 4

    def __init__(self, *, max_depth: int | None = None) -> None:
        self._max_depth = max_depth or self.DEFAULT_MAX_DEPTH
        self._calls_with_full_chain: int = 0
        self._total_calls: int = 0
        self._delegation_breaches: int = 0

    def propagate(
        self,
        parent_chain: PrincipalChain,
        *,
        new_agent_id: str,
        new_scope: str | None = None,
    ) -> PropagationResult:
        """Propagate ``parent_chain`` to a new specialist agent.

        - Increments ``delegation_depth`` by 1.
        - Sets ``parent_agent_id`` to the previous ``agent_id``.
        - Rejects (returns ``accepted=False``) if depth would exceed
          ``max_depth`` — counts as a breach.
        """
        self._total_calls += 1
        full_chain = bool(
            parent_chain.invoking_user
            and parent_chain.agent_id
            and parent_chain.scope
        )
        if full_chain:
            self._calls_with_full_chain += 1

        new_depth = parent_chain.delegation_depth + 1
        if new_depth > self._max_depth:
            self._delegation_breaches += 1
            return PropagationResult(
                new_chain=parent_chain,
                accepted=False,
                reason=(
                    f"delegation depth {new_depth} exceeds max "
                    f"{self._max_depth}"
                ),
            )

        new_chain = replace(
            parent_chain,
            agent_id=new_agent_id,
            parent_agent_id=parent_chain.agent_id,
            delegation_depth=new_depth,
            scope=new_scope if new_scope is not None else parent_chain.scope,
        )
        return PropagationResult(
            new_chain=new_chain,
            accepted=True,
            reason="propagated",
        )

    @property
    def counters(self) -> tuple[int, int, int]:
        """Return ``(calls_with_full_chain, total_calls, breach_count)``."""
        return (
            self._calls_with_full_chain,
            self._total_calls,
            self._delegation_breaches,
        )

    def reset(self) -> None:
        self._calls_with_full_chain = 0
        self._total_calls = 0
        self._delegation_breaches = 0

    def publish_kpi_sample(self, board: Any) -> None:
        try:
            from system_learning.engines.v7_kpi_board import (  # noqa: PLC0415
                V7KPIName,
                V7KPISample,
            )

            ts = time.time()
            ratio = (
                self._calls_with_full_chain / self._total_calls
                if self._total_calls > 0
                else 0.0
            )
            board.record(V7KPISample(
                name=V7KPIName.PRINCIPAL_CHAIN_PROPAGATION_COMPLETENESS,
                value=ratio,
                timestamp=ts, source="identity_propagator",
                metadata={"with_full_chain": self._calls_with_full_chain,
                          "total": self._total_calls},
            ))
            board.record(V7KPISample(
                name=V7KPIName.DELEGATION_DEPTH_BREACHES,
                value=float(self._delegation_breaches),
                timestamp=ts, source="identity_propagator",
                metadata={"count": self._delegation_breaches},
            ))
        except (ImportError, AttributeError, RuntimeError, ValueError) as exc:  # guardian: allow-specific -- KPI must not break propagation
            logger.warning("v7_kpi_identity_propagator_failed: %s", exc)


__all__ = ["PropagationResult", "IdentityPropagator"]
