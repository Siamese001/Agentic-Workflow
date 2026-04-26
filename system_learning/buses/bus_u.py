"""BUS_U — UWG-gated promotion bus.

DEFAULT-DENY publish. Every promotion / mutation proposal MUST carry a
valid :class:`UWGReceipt` referencing a sealed completed-run artifact.
Without a receipt, ``publish`` raises :class:`UWGGateError`.

Per the v34 process map and ADR-023, BUS_U is the ONLY route through
which evaluation-derived behavior changes may reach future runs. L6 may
recommend, but only UWG may authorize.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from system_learning.buses._base import BaseBus, BusPublishError


class UWGGateError(BusPublishError):
    """Raised when BUS_U.publish is called without a valid UWG receipt."""


@dataclass(frozen=True)
class UWGReceipt:
    """Proof that a UWG approver authorized a promotion."""

    receipt_id: str
    sealed_run_id: str
    """The completed-run sealed artifact the receipt references. MUST be
    a real, sealed run; the bus does not chase the link, but downstream
    consumers MUST verify it before consuming the promotion record."""
    approver_id: str
    approved_at_unix: float
    policy_snapshot: str = ""
    rationale: str = ""

    def is_valid(self) -> bool:
        return bool(
            self.receipt_id
            and self.sealed_run_id
            and self.approver_id
            and self.approved_at_unix > 0
        )


@dataclass(frozen=True)
class PromotionRecord:
    """One UWG-gated promotion proposal."""

    run_id: str
    sealed_at_unix: float
    proposal_id: str
    target_layer: str  # "L0" | "L1" | "L2" | "L4" | ...
    target_artifact: str  # e.g. "v15_route_selector.threshold"
    delta: Mapping[str, Any]
    uwg_receipt: UWGReceipt | None = None
    attributes: Mapping[str, Any] = field(default_factory=dict)


class BusU(BaseBus[PromotionRecord]):
    """UWG-gated promotion bus. DEFAULT-DENY publish."""

    def __init__(self) -> None:
        super().__init__(name="BUS_U")

    def publish(self, record: PromotionRecord) -> None:
        """Reject unless the record carries a valid UWG receipt AND
        passes the future-run-only gate."""
        self._gate_future_run_only(record)
        if record.uwg_receipt is None:
            self._reject(record, "missing_uwg_receipt")
            raise UWGGateError(
                "BUS_U: missing uwg_receipt — promotions REQUIRE a UWG "
                "approver receipt referencing a sealed run."
            )
        if not record.uwg_receipt.is_valid():
            self._reject(record, "invalid_uwg_receipt")
            raise UWGGateError(
                "BUS_U: uwg_receipt is malformed (missing receipt_id, "
                "sealed_run_id, approver_id, or approved_at_unix)."
            )
        if record.uwg_receipt.sealed_run_id != record.run_id:
            self._reject(record, "receipt_run_id_mismatch")
            raise UWGGateError(
                f"BUS_U: uwg_receipt.sealed_run_id="
                f"{record.uwg_receipt.sealed_run_id!r} does not match "
                f"record.run_id={record.run_id!r}."
            )
        self.records.append(record)


__all__ = ["BusU", "PromotionRecord", "UWGGateError", "UWGReceipt"]
