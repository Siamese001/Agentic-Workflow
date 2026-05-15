"""L6 shadow package for competencies runtime slice."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class L6ShadowPackage:
    run_id: str
    section_id: str
    l2_output_ref: str
    x1d_judge_refs: list[str]
    x2_gate_refs: list[str]
    x3_disposition_ref: str
    human_label_required: bool
    judge_calibration_status: str
    offline_only: bool
    promotion_allowed: bool
    learning_mutation_performed: bool
    runtime_approval_authority: str
    notes: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_l6_shadow_package(
    *,
    run_id: str,
    l2_output_ref: str,
    x1d_judge_refs: list[str],
    x2_gate_refs: list[str],
    x3_disposition_ref: str,
) -> L6ShadowPackage:
    return L6ShadowPackage(
        run_id=run_id,
        section_id="competencies",
        l2_output_ref=l2_output_ref,
        x1d_judge_refs=x1d_judge_refs,
        x2_gate_refs=x2_gate_refs,
        x3_disposition_ref=x3_disposition_ref,
        human_label_required=True,
        judge_calibration_status="NOT_CALIBRATED",
        offline_only=True,
        promotion_allowed=False,
        learning_mutation_performed=False,
        runtime_approval_authority="NONE",
        notes="L6 shadow-eval only for competencies. No runtime approval or learning mutation.",
    )


__all__ = ["L6ShadowPackage", "build_l6_shadow_package"]
