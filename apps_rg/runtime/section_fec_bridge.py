"""One-spine C0/FEC bridge — RouteContract + proof_pool → section PA (Wave 4).

Product-visible section PA must consume ``final_evidence_contract_bridge.json`` (apps_rg
``section_fec_bridge`` mode) or a canonical spine ``FinalEvidenceContract``. Raw
``proof_pool_metadata`` is not an authority surface for PA in product-visible runs.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from apps_rg.runtime.proof_pool_resolver import SectionProofPool
from apps_rg.runtime.section_front_spine_bridge import (
    SectionFrontSpineBridge,
    fixture_dev_bypass_active,
)
from apps_rg.runtime.section_spine_terminology import (
    CANONICAL_SPINE_CHAIN,
    section_lane_spine_classification,
)

FEC_BRIDGE_ARTIFACT = "final_evidence_contract_bridge.json"
FEC_BRIDGE_RECEIPT = "c0_fec_bridge_receipt.json"
FEC_BRIDGE_MODE_SECTION = "section_fec_bridge"

OBSERVED_CHAIN_WITH_FEC_BRIDGE: tuple[str, ...] = (
    "CLI",
    "canonical_dispatch.section_branch",
    "section_front_spine_bridge",
    "U0",
    "L1",
    "L0",
    "proof_pool_resolver",
    "section_fec_bridge",
    "section_c03_graph_binding",
    "section_PA",
    "section_L2",
    "section_X2",
    "section_X1D",
    "section_X3",
    "section_L6_shadow",
)

_PA_AUTHORITY_KEYS: tuple[str, ...] = (
    "proof_pool_type",
    "proof_source",
    "claim_evidence_source_type",
    "augmented_skills_graph_present",
    "graph_ref",
    "graph_version",
    "graph_digest",
    "skills_source_authority_status",
    "legacy_skills_ledger_ref",
    "broad_skills_ledger_ref",
    "binding_kind",
    "fec_shape_only",
    "c03_graphrag_bound_status",
    "support_status",
    "graph_lineage_refs",
    "graph_expansion_refs",
    "fec_bridge_mode",
    "route_contract_ref",
    "proof_pool_ref",
    "proof_pool_digest",
)


class SectionFecBridgePreconditionError(RuntimeError):
    """Raised when product-visible PA runs without FEC bridge or canonical FEC."""


@dataclass(frozen=True, slots=True)
class SectionFecBridge:
    """FEC bridge bundle between proof_pool resolution and section PA."""

    section_id: str
    bridge_doc: dict[str, Any]
    product_visible: bool = True
    fixture_dev_only_bypass: bool = False
    non_product_certified: bool = False


def fec_bridge_kill_switch_enabled() -> bool:
    return os.environ.get("APPS_RG_SECTION_FEC_BRIDGE_KILL_SWITCH", "1").strip() not in (
        "0",
        "false",
        "no",
    )


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _extract_support_status(pp_meta: dict[str, Any]) -> str:
    c03 = pp_meta.get("c03_graphrag_bound")
    if isinstance(c03, dict):
        st = str(c03.get("support_status") or "").strip()
        if st:
            return st
    st = str(pp_meta.get("support_status") or "").strip()
    return st or "SUPPORTED"


def _build_pa_proof_authority_metadata(
    pp_meta: dict[str, Any],
    *,
    pool: SectionProofPool,
    route_contract_ref: str,
) -> dict[str, Any]:
    out: dict[str, Any] = {
        "fec_bridge_mode": FEC_BRIDGE_MODE_SECTION,
        "route_contract_ref": route_contract_ref,
        "proof_pool_ref": pool.proof_pool_ref,
        "proof_pool_digest": pool.proof_pool_digest,
        "proof_source": pool.proof_source,
    }
    for key in _PA_AUTHORITY_KEYS:
        if key in pp_meta and key not in out:
            out[key] = pp_meta[key]
    c03 = pp_meta.get("c03_graphrag_bound")
    if isinstance(c03, dict):
        for key in ("graph_lineage_refs", "graph_expansion_refs", "binding_kind", "fec_shape_only"):
            if key in c03 and key not in out:
                out[key] = c03[key]
    native_pa = pp_meta.get("c03_pa_metadata")
    if isinstance(native_pa, dict):
        for key, val in native_pa.items():
            out[key] = val
        if "c03_graphrag_bound_status" not in out:
            if isinstance(c03, dict):
                out["c03_graphrag_bound_status"] = c03.get("c03_graphrag_bound_status")
            else:
                out["c03_graphrag_bound_status"] = pp_meta.get("native_c03_status")
    return out


def build_section_fec_bridge(
    *,
    section_id: str,
    front_spine: SectionFrontSpineBridge,
    pool: SectionProofPool,
    route_contract_ref: str = "route_contract.json",
    proof_pool_ref: str | None = None,
) -> SectionFecBridge:
    """Build apps_rg-local FEC bridge (section_fec_bridge, not canonical C0.5)."""
    if front_spine is None or front_spine.route is None:
        raise SectionFecBridgePreconditionError(
            "section FEC bridge requires RouteContract from section front spine"
        )
    pp_meta = dict(pool.proof_pool_metadata or {})
    c03 = pp_meta.get("c03_graphrag_bound")
    fec_snap: dict[str, Any] = {}
    evidence_items: list[dict[str, Any]] = []
    graph_lineage_refs: list[str] = []
    graph_expansion_refs: list[str] = []

    if isinstance(c03, dict):
        snap = c03.get("final_evidence_contract_snapshot")
        if isinstance(snap, dict):
            fec_snap = dict(snap)
            evidence_items = list(snap.get("evidence_items") or [])
        graph_lineage_refs = list(c03.get("graph_lineage_refs") or fec_snap.get("graph_lineage_refs") or [])
        graph_expansion_refs = list(c03.get("graph_expansion_refs") or fec_snap.get("graph_expansion_refs") or [])

    if not evidence_items:
        for fid in pool.allowed_fact_ids_ordered:
            evidence_items.append(
                {
                    "evidence_id": f"evidence:section:{fid}",
                    "source_fact_id": fid,
                    "source_class": pool.proof_source,
                    "proof_pool_ref": pool.proof_pool_ref,
                }
            )

    support_status = _extract_support_status(pp_meta)
    pa_meta = _build_pa_proof_authority_metadata(
        pp_meta, pool=pool, route_contract_ref=route_contract_ref
    )
    ts = _utc_now()
    bridge_doc: dict[str, Any] = {
        "schema_version": "section_fec_bridge_v1",
        "generated_at_utc": ts,
        "bridge_type": "FinalEvidenceContractBridge",
        "contract_type": "FinalEvidenceContractBridge",
        "fec_bridge_mode": FEC_BRIDGE_MODE_SECTION,
        "producer_stage": "section_fec_bridge",
        "consumer_stage": "section_PA",
        "section_id": section_id,
        "route_contract_ref": route_contract_ref,
        "validated_request_ref": "validated_request.json",
        "l1_plan_contract_ref": "l1_plan_contract.json",
        "proof_pool_ref": proof_pool_ref or pool.proof_pool_ref,
        "proof_pool_digest": pool.proof_pool_digest,
        "source_fact_ids": list(pool.allowed_fact_ids_ordered),
        "evidence_items": evidence_items,
        "citation_lineage_refs": graph_lineage_refs + graph_expansion_refs,
        "graph_lineage_refs": graph_lineage_refs,
        "graph_expansion_refs": graph_expansion_refs,
        "srfs_ref": pool.srfs_ref if pool.srfs_present else "",
        "support_status": support_status,
        "canonical_c0_2_claimed": False,
        "canonical_c0_3_claimed": False,
        "canonical_c0_5_claimed": False,
        "canonical_c0_5_fec": False,
        "fec_shape_only": True,
        "section_c03_graph_binding": isinstance(c03, dict),
        "binding_kind": str(
            pp_meta.get("binding_kind")
            or (c03.get("binding_kind") if isinstance(c03, dict) else "")
            or ("section_c03_graph_binding" if isinstance(c03, dict) else "")
        ),
        "final_evidence_contract": fec_snap,
        "proof_pool_type": pp_meta.get("proof_pool_type"),
        "proof_source": pool.proof_source,
        "pa_proof_authority_metadata": pa_meta,
        "raw_proof_pool_direct_to_pa": False,
        "product_certification": "NOT_CLAIMED",
        "explicit_non_claims": [
            "not canonical C0.2 dense retrieval unless spine Chroma dense path ran",
            "not canonical C0.3 governed graph traverse unless spine traverse ran",
            "not canonical C0.5 FinalEvidenceContract unless spine C0 emitted FEC",
        ],
    }
    fixture_dev = bool(front_spine.fixture_dev_only_bypass or fixture_dev_bypass_active())
    return SectionFecBridge(
        section_id=section_id,
        bridge_doc=bridge_doc,
        product_visible=front_spine.product_visible,
        fixture_dev_only_bypass=fixture_dev,
        non_product_certified=bool(front_spine.non_product_certified or fixture_dev),
    )


def build_section_fec_bridge_receipt(bridge: SectionFecBridge) -> dict[str, Any]:
    doc = bridge.bridge_doc
    spine = section_lane_spine_classification()
    route_ok = bool(str(doc.get("route_contract_ref") or "").strip())
    precond_pass = route_ok and bool(doc.get("source_fact_ids"))
    fixture_dev = bool(bridge.fixture_dev_only_bypass or fixture_dev_bypass_active())
    return {
        "schema_version": "c0_fec_bridge_receipt_v1",
        "generated_at_utc": _utc_now(),
        "plan_slug": "one-canonical-spine",
        "wave": 4,
        "section_id": bridge.section_id,
        "product_visible": bridge.product_visible,
        "fixture_dev_only": fixture_dev,
        "non_product_certified": bridge.non_product_certified,
        "product_certification": "NOT_CLAIMED",
        "fec_bridge_mode": FEC_BRIDGE_MODE_SECTION,
        "fec_bridge_status": "PASS" if precond_pass else "FAIL",
        "precondition_status": "PASS" if precond_pass else "FAIL",
        "final_evidence_contract_bridge_ref": FEC_BRIDGE_ARTIFACT,
        "route_contract_ref": doc.get("route_contract_ref"),
        "proof_pool_ref": doc.get("proof_pool_ref"),
        "proof_pool_digest": doc.get("proof_pool_digest"),
        "support_status": doc.get("support_status"),
        "canonical_c0_2_claimed": False,
        "canonical_c0_3_claimed": False,
        "canonical_c0_5_claimed": False,
        "pa_entry_allowed": precond_pass,
        "raw_proof_pool_direct_to_pa": False,
        "fec_bridge_kill_switch_enabled": fec_bridge_kill_switch_enabled(),
        "observed_chain": list(OBSERVED_CHAIN_WITH_FEC_BRIDGE),
        "canonical_spine_target": list(CANONICAL_SPINE_CHAIN),
        "downstream_classification": spine,
        "explicit_non_claims": list(doc.get("explicit_non_claims") or []),
    }


def emit_section_fec_bridge_artifacts(
    artifact_dir: Path,
    bridge: SectionFecBridge,
) -> dict[str, Path]:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    paths: dict[str, Path] = {}
    p_bridge = artifact_dir / FEC_BRIDGE_ARTIFACT
    p_bridge.write_text(
        json.dumps(bridge.bridge_doc, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    paths["final_evidence_contract_bridge"] = p_bridge
    receipt = build_section_fec_bridge_receipt(bridge)
    p_receipt = artifact_dir / FEC_BRIDGE_RECEIPT
    p_receipt.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    paths["c0_fec_bridge_receipt"] = p_receipt
    fec_inner = bridge.bridge_doc.get("final_evidence_contract")
    if isinstance(fec_inner, dict) and fec_inner:
        p_legacy = artifact_dir / "final_evidence_contract_snapshot.json"
        p_legacy.write_text(json.dumps(fec_inner, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        paths["final_evidence_contract_snapshot"] = p_legacy
    return paths


def assert_section_pa_fec_preconditions(
    runtime_payload: dict[str, Any],
    *,
    product_visible: bool | None = None,
    fixture_dev_only_bypass: bool = False,
    non_product_certified: bool = False,
) -> None:
    """Fail closed before section PA compile in product-visible mode."""
    if fixture_dev_only_bypass or fixture_dev_bypass_active():
        return
    if non_product_certified:
        return
    pv = product_visible if product_visible is not None else bool(
        runtime_payload.get("product_visible", True)
    )
    if not pv:
        return
    if not fec_bridge_kill_switch_enabled():
        return

    bridge = runtime_payload.get("section_fec_bridge")
    canonical_ref = str(runtime_payload.get("canonical_final_evidence_contract_ref") or "").strip()
    if not bridge and not canonical_ref:
        raise SectionFecBridgePreconditionError(
            "product-visible section PA requires section_fec_bridge or canonical FinalEvidenceContract"
        )
    if runtime_payload.get("raw_proof_pool_direct_to_pa") is True:
        raise SectionFecBridgePreconditionError(
            "raw_proof_pool_direct_to_pa is forbidden for product-visible section PA"
        )
    if isinstance(bridge, dict):
        mode = str(bridge.get("fec_bridge_mode") or "")
        if mode and mode != FEC_BRIDGE_MODE_SECTION:
            raise SectionFecBridgePreconditionError(
                f"unsupported fec_bridge_mode for product-visible PA: {mode!r}"
            )
        if not str(bridge.get("route_contract_ref") or "").strip():
            raise SectionFecBridgePreconditionError(
                "section FEC bridge missing route_contract_ref"
            )


def resolve_pa_proof_authority_for_compile(
    runtime_payload: dict[str, Any],
) -> tuple[dict[str, Any], bool]:
    """Return (metadata_for_PA, consumed_via_fec_bridge)."""
    assert_section_pa_fec_preconditions(runtime_payload)
    if fixture_dev_bypass_active():
        return dict(runtime_payload.get("proof_pool_metadata") or {}), False

    bridge = runtime_payload.get("section_fec_bridge")
    if isinstance(bridge, dict):
        pa = bridge.get("pa_proof_authority_metadata")
        if isinstance(pa, dict) and pa:
            return dict(pa), True
        return dict(bridge), True

    canonical = runtime_payload.get("canonical_final_evidence_contract")
    if isinstance(canonical, dict):
        return dict(canonical), True

    raise SectionFecBridgePreconditionError(
        "no FEC bridge or canonical FinalEvidenceContract on runtime payload"
    )


def wire_section_fec_bridge_for_lane(
    *,
    artifact_dir: Path,
    section_id: str,
    front_spine: SectionFrontSpineBridge,
    pool: SectionProofPool,
    runtime_payload: dict[str, Any],
) -> SectionFecBridge:
    """Emit front-spine + FEC bridge artifacts and attach bridge to runtime_payload."""
    from apps_rg.runtime.section_front_spine_bridge import emit_section_front_spine_receipts

    emit_section_front_spine_receipts(artifact_dir, front_spine)
    bridge = build_section_fec_bridge(
        section_id=section_id,
        front_spine=front_spine,
        pool=pool,
    )
    emit_section_fec_bridge_artifacts(artifact_dir, bridge)
    runtime_payload["section_fec_bridge"] = bridge.bridge_doc
    runtime_payload["fec_bridge_ref"] = FEC_BRIDGE_ARTIFACT
    runtime_payload["final_evidence_contract_ref"] = FEC_BRIDGE_ARTIFACT
    runtime_payload["c0_fec_bridge_receipt_ref"] = FEC_BRIDGE_RECEIPT
    runtime_payload["raw_proof_pool_direct_to_pa"] = False
    runtime_payload["product_visible"] = bridge.product_visible
    return bridge


def merge_compiled_prompt_artifact_fec_fields(
    base: dict[str, Any],
    runtime_payload: dict[str, Any],
) -> dict[str, Any]:
    """Merge PA FEC consumption proof fields into compiled_prompt_artifact.json body."""
    out = dict(base)
    out.update(pa_consumption_receipt_fields(runtime_payload))
    return out


def pa_consumption_receipt_fields(runtime_payload: dict[str, Any]) -> dict[str, Any]:
    """Fields merged into compiled_prompt_artifact.json."""
    bridge = runtime_payload.get("section_fec_bridge")
    via_fec = isinstance(bridge, dict) and bool(bridge)
    return {
        "fec_bridge_ref": runtime_payload.get("fec_bridge_ref") or FEC_BRIDGE_ARTIFACT,
        "final_evidence_contract_ref": runtime_payload.get("final_evidence_contract_ref")
        or FEC_BRIDGE_ARTIFACT,
        "c0_fec_bridge_receipt_ref": runtime_payload.get("c0_fec_bridge_receipt_ref")
        or FEC_BRIDGE_RECEIPT,
        "evidence_contract_consumed": via_fec
        or bool(runtime_payload.get("canonical_final_evidence_contract")),
        "raw_proof_pool_direct_to_pa": False if via_fec else bool(
            runtime_payload.get("raw_proof_pool_direct_to_pa")
        ),
        "fec_bridge_mode": (
            str(bridge.get("fec_bridge_mode") or FEC_BRIDGE_MODE_SECTION)
            if isinstance(bridge, dict)
            else ""
        ),
        "canonical_c0_5_claimed": False,
    }


__all__ = [
    "FEC_BRIDGE_ARTIFACT",
    "FEC_BRIDGE_MODE_SECTION",
    "FEC_BRIDGE_RECEIPT",
    "OBSERVED_CHAIN_WITH_FEC_BRIDGE",
    "SectionFecBridge",
    "SectionFecBridgePreconditionError",
    "assert_section_pa_fec_preconditions",
    "build_section_fec_bridge",
    "build_section_fec_bridge_receipt",
    "emit_section_fec_bridge_artifacts",
    "fec_bridge_kill_switch_enabled",
    "merge_compiled_prompt_artifact_fec_fields",
    "pa_consumption_receipt_fields",
    "resolve_pa_proof_authority_for_compile",
    "wire_section_fec_bridge_for_lane",
]
