"""Post-call reasoning ledger — deterministic governance evidence."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.reasoning.reasoning_control_requirement import (
    AllowedSurface,
    DowngradeDisposition,
    ReceiptState,
    RequirementLevel,
)


@dataclass(frozen=True, slots=True)
class ControlLedgerEntry:
    """Per-control requested → observed binding."""

    control_name: str
    requested: bool
    requirement_level: RequirementLevel
    receipt_state: ReceiptState
    applied_layer: AllowedSurface | None
    proved_reference: str
    gap_notes: str
    downgrade_disposition: DowngradeDisposition
    decisive_reason: str


def _parse_ledger_rows(raw: object) -> tuple[ControlLedgerEntry, ...] | None:
    if not isinstance(raw, list):
        return None
    rows: list[ControlLedgerEntry] = []
    for item in raw:
        if not isinstance(item, dict):
            return None
        try:
            al = item.get("applied_layer")
            rows.append(
                ControlLedgerEntry(
                    control_name=str(item["control_name"]),
                    requested=bool(item["requested"]),
                    requirement_level=RequirementLevel(str(item["requirement_level"])),
                    receipt_state=ReceiptState(str(item["receipt_state"])),
                    applied_layer=AllowedSurface(str(al)) if al is not None else None,
                    proved_reference=str(item.get("proved_reference", "")),
                    gap_notes=str(item.get("gap_notes", "")),
                    downgrade_disposition=DowngradeDisposition(str(item["downgrade_disposition"])),
                    decisive_reason=str(item.get("decisive_reason", "")),
                ),
            )
        except (KeyError, ValueError, TypeError):
            return None
    return tuple(rows)


@dataclass(frozen=True, slots=True)
class ReasoningExecutionReceipt:
    aggregate_warn: bool
    aggregate_review: bool
    aggregate_blocked: bool
    quality_certification_denied: bool
    ledger: tuple[ControlLedgerEntry, ...]

    @classmethod
    def from_primitive(cls, data: Mapping[str, Any]) -> ReasoningExecutionReceipt | None:
        """Parse gateway / trace-embedded receipt; None if shape invalid."""
        try:
            ledger = _parse_ledger_rows(data.get("ledger"))
            if ledger is None:
                return None
            return cls(
                aggregate_warn=bool(data["aggregate_warn"]),
                aggregate_review=bool(data["aggregate_review"]),
                aggregate_blocked=bool(data["aggregate_blocked"]),
                quality_certification_denied=bool(data["quality_certification_denied"]),
                ledger=ledger,
            )
        except (KeyError, TypeError, ValueError):
            return None

    def to_primitive(self) -> dict:
        """JSON-serialize friendly structure for gateway response embedding."""
        return {
            "aggregate_warn": self.aggregate_warn,
            "aggregate_review": self.aggregate_review,
            "aggregate_blocked": self.aggregate_blocked,
            "quality_certification_denied": self.quality_certification_denied,
            "ledger": [
                {
                    "control_name": x.control_name,
                    "requested": x.requested,
                    "requirement_level": x.requirement_level.value,
                    "receipt_state": x.receipt_state.value,
                    "applied_layer": x.applied_layer.value if x.applied_layer else None,
                    "proved_reference": x.proved_reference,
                    "gap_notes": x.gap_notes,
                    "downgrade_disposition": x.downgrade_disposition.value,
                    "decisive_reason": x.decisive_reason,
                }
                for x in self.ledger
            ],
        }


__all__ = ["ControlLedgerEntry", "ReasoningExecutionReceipt"]
