"""L5 Out-of-Band Promotion Receipt (`calibration_assurance_planes.md`) — G11 closure.

Binds the 3 out-of-band planes (Calibration / Assurance / Audit-Forensic) to
the v5 plane via a typed promotion-receipt contract. Cross-checks against
``out_of_band_invariants.assert_no_current_run_mutation`` so a promoted
``policy_version_next`` never alters in-flight certified runs.

Doctrine: ``docs/reference/00A_L5_Governance_Safety/calibration_assurance_planes.md``
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from agentic_core.L5_safety.v5.types import PromotionPlane


def _sorted_strings(values: tuple[str, ...]) -> list[str]:
    return sorted(values)


@dataclass(frozen=True)
class PromotionReceipt:
    """Receipt for a candidate ``policy_version_next`` from an out-of-band plane.

    Per the V4 invariant, this NEVER alters the current run. UWG owns the
    actual durable promotion; this receipt is the L5-plane evidence that the
    candidate satisfies the promotion gate's regression / rollback / owner
    requirements.
    """

    receipt_id: str
    plane: PromotionPlane
    candidate_policy_version: str
    current_policy_version: str
    regression_pack_ref: str
    rollback_plan_ref: str
    owner_approval_ref: str
    uwg_admission_ref: str  # filled by UWG when committed; empty until then
    veto: bool = False
    veto_reason: str = ""
    proposed_changes: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.receipt_id:
            raise ValueError("PromotionReceipt: receipt_id required")
        if self.candidate_policy_version == self.current_policy_version:
            raise ValueError(
                "PromotionReceipt: candidate_policy_version must differ from "
                "current_policy_version (promotion is a version-change event)",
            )
        if self.veto and not self.veto_reason:
            raise ValueError("PromotionReceipt: veto=True requires veto_reason")
        if not self.veto and not self.regression_pack_ref:
            raise ValueError(
                "PromotionReceipt: non-veto promotion requires regression_pack_ref "
                "(`evaluation-promotion-gate.md` — promotion gate)",
            )

    @property
    def admitted(self) -> bool:
        return bool(self.uwg_admission_ref) and not self.veto

    def to_dict(self) -> dict[str, Any]:
        return {
            "admitted": self.admitted,
            "candidate_policy_version": self.candidate_policy_version,
            "current_policy_version": self.current_policy_version,
            "owner_approval_ref": self.owner_approval_ref,
            "plane": self.plane.value,
            "proposed_changes": _sorted_strings(self.proposed_changes),
            "receipt_id": self.receipt_id,
            "regression_pack_ref": self.regression_pack_ref,
            "rollback_plan_ref": self.rollback_plan_ref,
            "uwg_admission_ref": self.uwg_admission_ref,
            "veto": self.veto,
            "veto_reason": self.veto_reason,
        }


__all__ = ["PromotionReceipt"]
