"""Executive-summary targeting ingress: bounded briefing before U0/C0 proof pool."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from apps_rg.runtime.targeting_context_authority import sha256_hex64


@dataclass(frozen=True)
class TargetingIngressResult:
    """Single bounded targeting view for U0 spine, proof pool, and lane."""

    jd_text: str
    briefing_text_bounded: str
    briefing_signal_packet: dict[str, Any]
    briefing_original_chars: int
    role_family_key: str
    briefing_selection_receipt: dict[str, Any] | None
    ingress_digest: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def prepare_executive_summary_targeting_ingress(
    *,
    jd_text: str,
    briefing_raw: str,
    target_role: str = "",
    target_title: str = "",
    repo_root: Path | None = None,
) -> TargetingIngressResult:
    """
    Select + cap briefing before proof-pool / U0 front spine.

    Role-family inference may read the full briefing for taxonomy signals only;
    all downstream consumers receive ``briefing_text_bounded``.
    """
    from apps_rg.fact_inventory.track_weighted_graph_expansion import infer_projection_role_family_key
    from apps_rg.runtime.sections.executive_summary_briefing import (
        prepare_briefing_for_executive_summary,
    )

    jd_eff = str(jd_text or "").strip()
    raw = str(briefing_raw or "")
    role = str(target_role or target_title or "").strip()
    role_family_key = infer_projection_role_family_key(
        target_role=role,
        jd_text=jd_eff,
        briefing_text=raw,
    )
    bounded, receipt = prepare_briefing_for_executive_summary(
        raw,
        role_family_key=role_family_key,
    )
    signal_packet = dict(receipt.get("briefing_signal_packet") or {})
    selection_receipt: dict[str, Any] | None
    if receipt.get("fail_closed"):
        selection_receipt = dict(receipt)
    elif int(receipt.get("briefing_excluded_chars") or 0) == 0 and int(
        receipt.get("briefing_original_chars") or 0
    ) == len(raw):
        selection_receipt = None
    else:
        selection_receipt = dict(receipt)
        selection_receipt["ingress_stage"] = "pre_proof_pool_u0_aligned"
        selection_receipt["role_family_key"] = role_family_key

    ingress_digest = sha256_hex64(f"{jd_eff}\n---\n{bounded}")
    return TargetingIngressResult(
        jd_text=jd_eff,
        briefing_text_bounded=bounded,
        briefing_signal_packet=signal_packet,
        briefing_original_chars=len(raw),
        role_family_key=role_family_key,
        briefing_selection_receipt=selection_receipt,
        ingress_digest=ingress_digest,
    )


__all__ = [
    "TargetingIngressResult",
    "prepare_executive_summary_targeting_ingress",
]
