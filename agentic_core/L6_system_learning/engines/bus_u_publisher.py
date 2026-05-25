"""V7 6D.S4E BUS U Publisher + Alias Activator.

Publishes approved promotion packets to BUS U *for future runs only*. The
activation rule is absolute: updates take effect at next run_start, never
during the current run.

Reference
---------
``docs/reference/06_Shadow_Evaluation_System_Learning/06_Shadow_Evaluation_System_Learning_v7.md``
section 6D S4E "FUTURE-RUN PUBLISH".

KPI surface
-----------
``BUS_U_ACTIVATION_CORRECTNESS`` — must be 1.0 (every publish activates
only at next run_start).
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any

from .rollout_receipt_generator import RolloutReceipt

logger = logging.getLogger(__name__)


class ActivationPolicy(str, Enum):
    """Allowed activation policies. Anything else is rejected."""

    NEXT_RUN_START = "next_run_start"
    NEXT_RUN_START_CANARY = "next_run_start_canary"
    NEXT_RUN_START_DARK = "next_run_start_dark"


_VALID_POLICIES: frozenset[str] = frozenset({p.value for p in ActivationPolicy})


@dataclass(frozen=True)
class FutureRunActivationReceipt:
    """Receipt produced by BUS U publish."""

    publish_id: str
    rollout_receipt_id: str
    target_surface: str
    activation_policy: ActivationPolicy
    canary_scope: str
    activate_at: str  # always "next_run_start"
    ttl_review_date_epoch: float
    timestamp: float


class AliasActivator:
    """Swap version aliases at next run_start.

    This module is *purely* an alias planner: it does not perform live
    activation. The actual atomic swap is performed by the runtime at
    run_start, consuming the activation receipt produced here.
    """

    @staticmethod
    def plan_swap(
        *,
        target_surface: str,
        previous_version_pointer: str,
        new_version_pointer: str,
    ) -> dict[str, str]:
        """Return the alias-swap plan as a deterministic dict."""
        return {
            "target_surface": target_surface,
            "from": previous_version_pointer,
            "to": new_version_pointer,
            "swap_at": "next_run_start",
        }


class BusUPublisher:
    """Publish approved promotions to BUS U.

    Enforces v7 §S4E activation invariants. Any policy that would
    activate during the current run is rejected; the publish counter
    only increments for *correct* activations, so the published KPI
    reflects compliance.
    """

    def __init__(self) -> None:
        self._correct: int = 0
        self._total_attempts: int = 0
        self._activator = AliasActivator()

    def publish(
        self,
        *,
        receipt: RolloutReceipt,
        activation_policy: str = ActivationPolicy.NEXT_RUN_START.value,
        canary_scope: str = "",
        ttl_review_date_epoch: float | None = None,
    ) -> FutureRunActivationReceipt:
        """Publish ``receipt`` to BUS U with the given activation policy.

        Raises ``ValueError`` if the activation policy is not in
        :data:`_VALID_POLICIES` (which would break the future-run-only
        invariant).
        """
        self._total_attempts += 1
        if activation_policy not in _VALID_POLICIES:
            # Do NOT increment _correct — this is the failure case the KPI
            # tracks. The publish itself is rejected.
            raise ValueError(
                f"activation_policy={activation_policy!r} is not "
                f"future-run-only; allowed: {sorted(_VALID_POLICIES)}"
            )
        if not receipt.rollback_handle.verified_reachable:
            raise ValueError(
                "cannot publish: rollback handle not verified reachable"
            )

        ts = time.time()
        ttl = ttl_review_date_epoch if ttl_review_date_epoch is not None else (
            ts + 30.0 * 86400.0
        )
        publish_id = f"pub::{receipt.receipt_id}"
        # Plan the alias swap (executed by runtime at run_start).
        self._activator.plan_swap(
            target_surface=receipt.target_surface,
            previous_version_pointer=receipt.previous_version_pointer,
            new_version_pointer=receipt.new_version_pointer,
        )
        self._correct += 1
        return FutureRunActivationReceipt(
            publish_id=publish_id,
            rollout_receipt_id=receipt.receipt_id,
            target_surface=receipt.target_surface,
            activation_policy=ActivationPolicy(activation_policy),
            canary_scope=canary_scope,
            activate_at="next_run_start",
            ttl_review_date_epoch=ttl,
            timestamp=ts,
        )

    @property
    def counters(self) -> tuple[int, int]:
        """Return ``(correct_activations, total_attempts)``."""
        return (self._correct, self._total_attempts)

    def reset(self) -> None:
        self._correct = 0
        self._total_attempts = 0

    def publish_kpi_sample(self, board: Any) -> None:
        try:
            from .v7_kpi_board import (  # noqa: PLC0415
                V7KPIName,
                V7KPISample,
            )

            ratio = (
                self._correct / self._total_attempts
                if self._total_attempts > 0
                else 0.0
            )
            board.record(V7KPISample(
                name=V7KPIName.BUS_U_ACTIVATION_CORRECTNESS,
                value=ratio,
                timestamp=time.time(),
                source="bus_u_publisher",
                metadata={"correct": self._correct,
                          "total_attempts": self._total_attempts},
            ))
        except (ImportError, AttributeError, RuntimeError, ValueError) as exc:  # guardian: allow-log-and-swallow -- KPI must not break publish
            logger.warning("v7_kpi_bus_u_activation_correctness_failed: %s", exc)


__all__ = [
    "ActivationPolicy",
    "FutureRunActivationReceipt",
    "AliasActivator",
    "BusUPublisher",
]
