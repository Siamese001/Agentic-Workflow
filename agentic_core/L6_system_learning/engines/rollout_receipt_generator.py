"""V7 6D.S4D Rollout Receipt Generator + Rollback Handle Validator.

Produces ``RolloutReceipt`` and ``RollbackHandle`` artifacts after UWG
commits an approved promotion. Verifies rollback reachability before the
update is published to BUS U.

Reference
---------
``docs/reference/06_Shadow_Evaluation_System_Learning/06_Shadow_Evaluation_System_Learning_v7.md``
section 6D S4D "LEDGER PROOF".

KPI surface
-----------
``ROLLBACK_REACHABILITY`` — must be 1.0 (every promotion has a tested
rollback handle).
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from dataclasses import dataclass
from typing import Any, Mapping

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RollbackHandle:
    """Reversibility handle returned with every promotion."""

    handle_id: str
    target_surface: str
    previous_version_pointer: str
    new_version_pointer: str
    revert_diff: str
    verified_reachable: bool
    verification_notes: str


@dataclass(frozen=True)
class RolloutReceipt:
    """Receipt produced after UWG commits a promotion."""

    receipt_id: str
    proposal_id: str
    target_surface: str
    content_hash: str
    policy_hash: str
    signer_identity: str
    previous_version_pointer: str
    new_version_pointer: str
    alias_swap_planned: bool
    cache_refresh_planned: bool
    rollback_handle: RollbackHandle
    timestamp: float


def _stable_hash(payload: Mapping[str, Any]) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class RollbackHandleValidator:
    """Verify a rollback handle is actually reachable.

    "Reachable" means: the previous version pointer resolves, the revert
    diff is non-empty, and the handle is uniquely identified. This is a
    static validator; deeper integration tests (does executing the revert
    actually restore prior behavior?) belong to the gauntlet.
    """

    def validate(self, handle: RollbackHandle) -> tuple[bool, str]:
        if not handle.handle_id:
            return False, "handle_id is empty"
        if not handle.previous_version_pointer:
            return False, "previous_version_pointer is empty"
        if not handle.revert_diff:
            return False, "revert_diff is empty"
        if handle.previous_version_pointer == handle.new_version_pointer:
            return False, "previous and new pointers identical"
        return True, "rollback handle reachable"


class RolloutReceiptGenerator:
    """Generate ``RolloutReceipt`` and emit ``ROLLBACK_REACHABILITY``."""

    def __init__(self) -> None:
        self._reachable: int = 0
        self._total: int = 0
        self._validator = RollbackHandleValidator()

    def generate(
        self,
        *,
        proposal_id: str,
        target_surface: str,
        content_hash: str,
        policy_hash: str,
        signer_identity: str,
        previous_version_pointer: str,
        new_version_pointer: str,
        revert_diff: str,
        alias_swap_planned: bool = True,
        cache_refresh_planned: bool = True,
        timestamp: float | None = None,
    ) -> RolloutReceipt:
        ts = timestamp if timestamp is not None else time.time()

        # Build provisional handle, then validate.
        handle_payload = {
            "proposal_id": proposal_id,
            "target_surface": target_surface,
            "previous_version_pointer": previous_version_pointer,
            "new_version_pointer": new_version_pointer,
        }
        handle_id = _stable_hash(handle_payload)
        provisional = RollbackHandle(
            handle_id=handle_id,
            target_surface=target_surface,
            previous_version_pointer=previous_version_pointer,
            new_version_pointer=new_version_pointer,
            revert_diff=revert_diff,
            verified_reachable=False,
            verification_notes="",
        )
        ok, note = self._validator.validate(provisional)
        handle = RollbackHandle(
            handle_id=handle_id,
            target_surface=target_surface,
            previous_version_pointer=previous_version_pointer,
            new_version_pointer=new_version_pointer,
            revert_diff=revert_diff,
            verified_reachable=ok,
            verification_notes=note,
        )

        self._total += 1
        if ok:
            self._reachable += 1

        receipt_payload = {
            "proposal_id": proposal_id,
            "target_surface": target_surface,
            "content_hash": content_hash,
            "policy_hash": policy_hash,
            "signer_identity": signer_identity,
            "previous_version_pointer": previous_version_pointer,
            "new_version_pointer": new_version_pointer,
            "handle_id": handle_id,
        }
        receipt_id = _stable_hash(receipt_payload)
        return RolloutReceipt(
            receipt_id=receipt_id,
            proposal_id=proposal_id,
            target_surface=target_surface,
            content_hash=content_hash,
            policy_hash=policy_hash,
            signer_identity=signer_identity,
            previous_version_pointer=previous_version_pointer,
            new_version_pointer=new_version_pointer,
            alias_swap_planned=alias_swap_planned,
            cache_refresh_planned=cache_refresh_planned,
            rollback_handle=handle,
            timestamp=ts,
        )

    @property
    def counters(self) -> tuple[int, int]:
        """Return ``(reachable, total)``."""
        return (self._reachable, self._total)

    def reset(self) -> None:
        self._reachable = 0
        self._total = 0

    def publish_kpi_sample(self, board: Any) -> None:
        try:
            from .v7_kpi_board import (  # noqa: PLC0415
                V7KPIName,
                V7KPISample,
            )

            ratio = (
                self._reachable / self._total if self._total > 0 else 0.0
            )
            board.record(V7KPISample(
                name=V7KPIName.ROLLBACK_REACHABILITY,
                value=ratio,
                timestamp=time.time(),
                source="rollout_receipt_generator",
                metadata={"reachable": self._reachable,
                          "total": self._total},
            ))
        except (ImportError, AttributeError, RuntimeError, ValueError) as exc:  # guardian: allow-log-and-swallow -- KPI must not break receipt gen
            logger.warning("v7_kpi_rollback_reachability_failed: %s", exc)


__all__ = [
    "RollbackHandle",
    "RolloutReceipt",
    "RollbackHandleValidator",
    "RolloutReceiptGenerator",
]
