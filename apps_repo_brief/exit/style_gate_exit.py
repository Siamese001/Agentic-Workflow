"""
P4.4 — StyleGate Exit Hard Gate (AG P4.1 Option A).

This is the persistent-violation gate at Exit (X3). It fires ONLY when
L2.E4 escalated violations that it could not repair inline.

Gate authority:
  - Checks E4 receipt for escalated_slot_ids.
  - For each escalated slot, verifies the slot body does NOT contain
    unresolved evidence stubs ({{KEY}} tokens) or disqualifying patterns.
  - If any disqualifying violation remains → BLOCK_COMMIT (Exit emits X3 FAIL).
  - If no escalations → PASS (X3 not triggered by this gate).

This gate does NOT re-run the full style check — it trusts E4 receipt
for the list of escalated slots and re-validates only those slots.

Plan: .windsurf/plans/apps-repo-brief-plan3-zero-loss-overwrite.md §P4.4
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

_log = logging.getLogger(__name__)

_STUB_PATTERN = re.compile(r"\{\{[^}]+\}\}")


class ExitGateVerdict(str, Enum):
    PASS = "PASS"
    BLOCK = "BLOCK"
    SKIP = "SKIP"


@dataclass
class StyleGateExitResult:
    verdict: ExitGateVerdict
    checked_slot_ids: list[str]
    blocking_slot_ids: list[str]
    blocking_reasons: dict[str, str]
    x3_triggered: bool
    gate_name: str = "style_gate_exit"

    def to_dict(self) -> dict[str, Any]:
        return {
            "gate_name": self.gate_name,
            "verdict": self.verdict.value,
            "checked_slot_ids": self.checked_slot_ids,
            "blocking_slot_ids": self.blocking_slot_ids,
            "blocking_reasons": self.blocking_reasons,
            "x3_triggered": self.x3_triggered,
        }


class StyleGateExitCheck:
    """
    Exit X3 gate for persistent style violations not resolved by L2.E4.

    Usage::

        gate = StyleGateExitCheck()
        result = gate.check(e4_receipt, repaired_slots)
        if result.x3_triggered:
            # emit X3 BLOCK_COMMIT
            ...

    """

    def check(
        self,
        e4_receipt: dict[str, Any],
        repaired_slots: dict[str, str],
    ) -> StyleGateExitResult:
        """
        Check escalated slots from E4 for persistent disqualifying violations.

        Args:
            e4_receipt:     E4Receipt.to_dict() output.
            repaired_slots: dict slot_id → body after E4 repair.

        Returns:
            StyleGateExitResult
        """
        escalated_ids: list[str] = e4_receipt.get("escalated_slot_ids", [])

        if not escalated_ids:
            return StyleGateExitResult(
                verdict=ExitGateVerdict.PASS,
                checked_slot_ids=[],
                blocking_slot_ids=[],
                blocking_reasons={},
                x3_triggered=False,
            )

        blocking: dict[str, str] = {}
        for slot_id in escalated_ids:
            body = repaired_slots.get(slot_id, "")
            reason = self._check_slot(body)
            if reason:
                blocking[slot_id] = reason

        if blocking:
            _log.warning(
                "StyleGateExitCheck: X3 triggered — %d blocking slots: %s",
                len(blocking),
                list(blocking.keys()),
            )
            return StyleGateExitResult(
                verdict=ExitGateVerdict.BLOCK,
                checked_slot_ids=escalated_ids,
                blocking_slot_ids=list(blocking.keys()),
                blocking_reasons=blocking,
                x3_triggered=True,
            )

        return StyleGateExitResult(
            verdict=ExitGateVerdict.PASS,
            checked_slot_ids=escalated_ids,
            blocking_slot_ids=[],
            blocking_reasons={},
            x3_triggered=False,
        )

    @staticmethod
    def _check_slot(body: str) -> str:
        """Return reason string if slot has disqualifying violation, else ''."""
        stubs = _STUB_PATTERN.findall(body)
        if stubs:
            return f"unresolved evidence stubs: {stubs[:3]}"
        return ""
