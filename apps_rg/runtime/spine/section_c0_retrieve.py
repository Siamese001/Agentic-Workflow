"""Section spine C0 retrieve — ``c0_retrieve_apps_rg`` authority (W4).

Product-visible section lanes must not treat raw proof-pool metadata as C0/FEC
authority. This module invokes the spine binding and enforces STOP AS EVIDENCE
GAP when grounding is required and FEC support is weak or retrieval fails.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from agentic_core.runtime.contracts.final_evidence_contract import (
    FinalEvidenceContract,
    STATUS_NOT_APPLICABLE,
    STATUS_UNKNOWN,
    SUPPORT_STATUS_BLOCKED,
    SUPPORT_STATUS_CONFLICTED,
    SUPPORT_STATUS_EMPTY,
    SUPPORT_STATUS_PASS,
    SUPPORT_STATUS_WEAK,
    SUPPORT_STATUS_WEAK_WITH_CAVEATS,
)

from apps_rg.runtime.bindings.c0_binding import (
    APPS_RG_C0_CERT_REF,
    C0_GRAPH_LANE_NA_REF,
    C0EvidenceGapError,
    c0_retrieve_apps_rg,
)
from apps_rg.runtime.spine.front_contracts import (
    SectionFrontSpineBridge,
    fixture_dev_bypass_active,
)

STOP_AS_EVIDENCE_GAP = "STOP_AS_EVIDENCE_GAP"

_GROUNDING_FAIL_STATUSES = frozenset(
    {
        SUPPORT_STATUS_WEAK,
        SUPPORT_STATUS_WEAK_WITH_CAVEATS,
        SUPPORT_STATUS_EMPTY,
        SUPPORT_STATUS_BLOCKED,
        SUPPORT_STATUS_CONFLICTED,
        STATUS_UNKNOWN,
    }
)


class StopAsEvidenceGapError(RuntimeError):
    """C0 preflight blocked or FEC too weak for grounded section work."""

    def __init__(self, message: str, *, support_status: str = "", reason_code: str = "") -> None:
        super().__init__(message)
        self.support_status = support_status
        self.reason_code = reason_code or STOP_AS_EVIDENCE_GAP


@dataclass(frozen=True, slots=True)
class SectionSpineC0RetrieveResult:
    fec: FinalEvidenceContract
    receipt: dict[str, Any]


def section_spine_c0_retrieve_required(front_spine: SectionFrontSpineBridge) -> bool:
    """Whether product section runs must invoke spine ``c0_retrieve_apps_rg``."""
    if fixture_dev_bypass_active() or bool(front_spine.fixture_dev_only_bypass):
        return False
    if not front_spine.product_visible:
        return False
    if os.environ.get("APPS_RG_SECTION_SPINE_C0_SKIP", "").strip().lower() in (
        "1",
        "true",
        "yes",
    ):
        return False
    return True


def grounding_required_for_section(front_spine: SectionFrontSpineBridge) -> bool:
    plan = front_spine.l1_plan
    route = front_spine.route
    if plan is not None and hasattr(plan, "grounding_required"):
        return bool(plan.grounding_required)
    if route is not None and hasattr(route, "grounding_required"):
        return bool(route.grounding_required)
    return True


def assert_no_stop_as_evidence_gap(
    *,
    grounding_required: bool,
    fec: FinalEvidenceContract,
    section_id: str = "",
) -> None:
    """Raise STOP AS EVIDENCE GAP when grounded work has weak FEC support."""
    if not grounding_required:
        return
    status = str(getattr(fec, "support_status", "") or "")
    if status in _GROUNDING_FAIL_STATUSES:
        raise StopAsEvidenceGapError(
            f"{STOP_AS_EVIDENCE_GAP}: section={section_id or '?'} grounding_required "
            f"but FEC support_status={status!r}",
            support_status=status,
        )
    if status == STATUS_NOT_APPLICABLE and not getattr(fec, "support_target_met", False):
        reason = str(getattr(fec, "not_applicable_reason", "") or "")
        raise StopAsEvidenceGapError(
            f"{STOP_AS_EVIDENCE_GAP}: section={section_id or '?'} grounding_required "
            f"but spine C0 returned NOT_APPLICABLE ({reason})",
            support_status=status,
        )


def _fec_evidence_items_payload(fec: FinalEvidenceContract) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for it in fec.evidence_items or ():
        out.append(
            {
                "evidence_id": getattr(it, "evidence_id", "") or getattr(it, "source", ""),
                "source": getattr(it, "source", ""),
                "source_class": getattr(it, "source_type", "") or getattr(it, "source_class", ""),
                "source_type": getattr(it, "source_type", ""),
                "content_digest": getattr(it, "content_digest", ""),
                "allowed_prompt_slot": getattr(it, "allowed_prompt_slot", ""),
            }
        )
    return out


def _build_spine_retrieve_receipt(
    *,
    section_id: str,
    fec: FinalEvidenceContract,
    graph_lane_ref: str,
) -> dict[str, Any]:
    dense_ran = bool(getattr(fec, "dense_search_refs", None))
    sparse_refs = list(getattr(fec, "sparse_search_refs", None) or ())
    return {
        "schema_version": "section_spine_c0_retrieve_receipt_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "section_id": section_id,
        "stop_as_evidence_gap_policy": STOP_AS_EVIDENCE_GAP,
        "spine_binding": "apps_rg.runtime.bindings.c0_binding.c0_retrieve_apps_rg",
        "cert_ref": getattr(fec, "l5_certification_ref", None) or APPS_RG_C0_CERT_REF,
        "support_status": fec.support_status,
        "not_applicable_reason": getattr(fec, "not_applicable_reason", "") or "",
        "final_evidence_digest": getattr(fec, "final_evidence_digest", "") or "",
        "evidence_item_count": len(fec.evidence_items or ()),
        "dense_search_refs": list(getattr(fec, "dense_search_refs", None) or ()),
        "sparse_search_refs": sparse_refs,
        "graph_expansion_refs": list(getattr(fec, "graph_expansion_refs", None) or ()),
        "graph_lane_na_ref": graph_lane_ref,
        "canonical_c0_2_dense_claimed": dense_ran,
        "canonical_c0_3_graph_claimed": graph_lane_ref != C0_GRAPH_LANE_NA_REF,
        "graph_lane_deferred": graph_lane_ref == C0_GRAPH_LANE_NA_REF,
        "proof_pool_shim_skipped": graph_lane_ref == C0_GRAPH_LANE_NA_REF,
    }


def invoke_section_spine_c0_retrieve(
    *,
    front_spine: SectionFrontSpineBridge,
    section_id: str,
    chromadb_path: str | None = None,
    assert_grounding: bool = True,
) -> SectionSpineC0RetrieveResult:
    """Run spine C0 retrieve for a section front-spine bundle.

    ``assert_grounding`` (default ``True``) controls whether the spine-retrieve FEC's
    support is grounding-asserted *here*. For ``evidence_room_producer`` (graph-authority)
    sections the section's OWN evidence-room FEC is the grounding authority and is asserted
    by the caller AFTER ``apply_spine_c03_overlay_to_bridge_doc`` overlays it onto the
    bridge; the spine retrieve is non-authoritative enrichment, so its ``WEAK`` support must
    not prematurely STOP a section whose own FEC rated ``PASS``. Such callers pass
    ``assert_grounding=False`` and re-assert on the merged/overlaid bridge. Direct callers
    keep the default so standalone use stays grounding-safe.
    """
    if front_spine.route is None or front_spine.validated_request is None:
        raise StopAsEvidenceGapError(
            f"{STOP_AS_EVIDENCE_GAP}: missing RouteContract or ValidatedRequest on front spine"
        )

    chroma = chromadb_path
    if chroma is None:
        chroma = os.environ.get("CHROMA_PERSIST_DIR", "").strip() or None

    try:
        fec = c0_retrieve_apps_rg(
            route=front_spine.route,
            validated_request=front_spine.validated_request,
            chromadb_path=chroma,
        )
    except C0EvidenceGapError as exc:
        raise StopAsEvidenceGapError(str(exc), reason_code=STOP_AS_EVIDENCE_GAP) from exc

    if assert_grounding:
        assert_no_stop_as_evidence_gap(
            grounding_required=grounding_required_for_section(front_spine),
            fec=fec,
            section_id=section_id,
        )

    graph_ref = C0_GRAPH_LANE_NA_REF
    if fec.graph_expansion_refs:
        graph_ref = str(fec.graph_expansion_refs[0])

    receipt = _build_spine_retrieve_receipt(
        section_id=section_id,
        fec=fec,
        graph_lane_ref=graph_ref,
    )
    return SectionSpineC0RetrieveResult(fec=fec, receipt=receipt)


def apply_spine_c03_overlay_to_bridge_doc(
    bridge_doc: dict[str, Any],
    *,
    spine: SectionSpineC0RetrieveResult,
) -> dict[str, Any]:
    """Overlay core C0.3 spine graph authority without replacing evidence-room producer_stage."""
    from apps_rg.runtime.spine.spine_c03_authority import (
        overlay_spine_graph_authority_on_bridge,
        spine_graph_refs_live,
    )

    fec = spine.fec
    out = dict(bridge_doc)
    spine_exp = list(getattr(fec, "graph_expansion_refs", None) or ())
    spine_lin = list(out.get("graph_lineage_refs") or [])
    out["spine_c0_retrieve_receipt"] = spine.receipt
    out = overlay_spine_graph_authority_on_bridge(
        out,
        spine_graph_expansion_refs=spine_exp,
        spine_graph_lineage_refs=spine_lin,
    )
    core_live = spine_graph_refs_live(spine_exp)
    out["core_c03_graph_rag_used"] = core_live
    if core_live:
        out["apps_rg_c03_skills_graph_used"] = True
    pa = dict(out.get("pa_proof_authority_metadata") or {})
    pa["core_c03_graph_rag_used"] = core_live
    pa["spine_c0_retrieve_receipt_ref"] = "section_spine_c0_retrieve_receipt.json"
    out["pa_proof_authority_metadata"] = pa
    snap = dict(out.get("final_evidence_contract_snapshot") or {})
    if spine_exp:
        snap["graph_expansion_refs"] = spine_exp
    out["final_evidence_contract_snapshot"] = snap
    return out


def merge_spine_fec_into_bridge_doc(
    bridge_doc: dict[str, Any],
    *,
    spine: SectionSpineC0RetrieveResult,
    pool_allowed_fact_ids: list[str],
) -> dict[str, Any]:
    """Overlay spine FEC authority fields onto a section FEC bridge document."""
    fec = spine.fec
    out = dict(bridge_doc)
    items = _fec_evidence_items_payload(fec)
    if not items and pool_allowed_fact_ids:
        for fid in pool_allowed_fact_ids:
            items.append(
                {
                    "evidence_id": f"evidence:section:{fid}",
                    "source_fact_id": fid,
                    "source_class": out.get("proof_source") or "proof_pool",
                }
            )

    dense_ran = bool(getattr(fec, "dense_search_refs", None))
    support = str(fec.support_status or SUPPORT_STATUS_PASS)
    snap = {
        "request_id": fec.request_id,
        "run_id": fec.run_id,
        "final_evidence_digest": fec.final_evidence_digest,
        "support_status": support,
        "evidence_items": items,
        "dense_search_refs": list(getattr(fec, "dense_search_refs", None) or ()),
        "sparse_search_refs": list(getattr(fec, "sparse_search_refs", None) or ()),
        "graph_expansion_refs": list(getattr(fec, "graph_expansion_refs", None) or ()),
    }

    spine_exp = list(getattr(fec, "graph_expansion_refs", None) or ())
    spine_lin: list[str] = []
    from apps_rg.runtime.spine.spine_c03_authority import overlay_spine_graph_authority_on_bridge

    out.update(
        {
            "support_status": support,
            "evidence_items": items,
            "final_evidence_contract": snap,
            "final_evidence_contract_snapshot": snap,
            "spine_c0_retrieve_receipt": spine.receipt,
            "producer_stage": "spine_c0_retrieve_apps_rg",
            "fec_bridge_mode": out.get("fec_bridge_mode") or "spine_c0_fec_compose",
            "canonical_c0_2_claimed": dense_ran,
            "canonical_c0_3_claimed": bool(
                spine.receipt.get("canonical_c0_3_graph_claimed")
                or (
                    spine.fec.graph_expansion_refs
                    and str(spine.fec.graph_expansion_refs[0]) != C0_GRAPH_LANE_NA_REF
                )
            ),
            "canonical_c0_5_claimed": True,
            "canonical_c0_5_fec": True,
            "fec_shape_only": False,
            "graph_expansion_refs": spine_exp,
            "graph_lane_na_ref": C0_GRAPH_LANE_NA_REF,
            "proof_pool_shim_only": False,
            "binding_kind": "spine_c0_retrieve_apps_rg",
        }
    )
    out = overlay_spine_graph_authority_on_bridge(
        out,
        spine_graph_expansion_refs=spine_exp,
        spine_graph_lineage_refs=spine_lin,
    )
    pa_meta = dict(out.get("pa_proof_authority_metadata") or {})
    pa_meta["fec_shape_only"] = False
    pa_meta["binding_kind"] = "spine_c0_retrieve_apps_rg"
    pa_meta["canonical_c0_path"] = True
    pa_meta["support_status"] = support
    out["pa_proof_authority_metadata"] = pa_meta
    return out


__all__ = [
    "STOP_AS_EVIDENCE_GAP",
    "SectionSpineC0RetrieveResult",
    "StopAsEvidenceGapError",
    "apply_spine_c03_overlay_to_bridge_doc",
    "assert_no_stop_as_evidence_gap",
    "invoke_section_spine_c0_retrieve",
    "merge_spine_fec_into_bridge_doc",
    "grounding_required_for_section",
    "section_spine_c0_retrieve_required",
    "write_spine_c0_retrieve_receipt",
]


def write_spine_c0_retrieve_receipt(artifact_dir: Path, receipt: dict[str, Any]) -> Path:
    """Persist spine C0 retrieve receipt under a section artifact dir."""
    artifact_dir = Path(artifact_dir)
    artifact_dir.mkdir(parents=True, exist_ok=True)
    path = artifact_dir / "section_spine_c0_retrieve_receipt.json"
    path.write_text(
        json.dumps(receipt, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    from apps_rg.runtime.spine.c0_graph_lane_receipt import (
        build_c0_graph_lane_receipt_from_spine_retrieve,
        emit_c0_graph_lane_receipt,
    )

    graph_receipt = build_c0_graph_lane_receipt_from_spine_retrieve(receipt)
    emit_c0_graph_lane_receipt(artifact_dir, graph_receipt)
    return path
