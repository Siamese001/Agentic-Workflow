"""Load spine contracts from section artifact dir envelopes (W8 follow-up)."""
from __future__ import annotations

import json
from dataclasses import fields
from pathlib import Path
from typing import Any

from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest
from agentic_core.runtime.contracts.final_evidence_contract import (
    SUPPORT_STATUS_PASS,
    EvidenceItem,
    FinalEvidenceContract,
)
from agentic_core.runtime.contracts.l1_plan_contract import L1PlanContract
from agentic_core.runtime.contracts.route_contract import RouteContract
from apps_rg.runtime.spine.validated_request_contract import load_validated_request_contract


def _payload_from_contract_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    doc = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(doc.get("payload"), dict):
        return dict(doc["payload"])
    return dict(doc) if isinstance(doc, dict) else {}


def _filter_dataclass_kwargs(cls: type, body: dict[str, Any]) -> dict[str, Any]:
    allowed = {f.name for f in fields(cls)}
    return {k: v for k, v in body.items() if k in allowed}


def load_route_from_artifact_dir(artifact_dir: Path) -> RouteContract | None:
    body = _payload_from_contract_json(artifact_dir / "route_contract.json")
    if not body.get("request_id"):
        return None
    return RouteContract(**_filter_dataclass_kwargs(RouteContract, body))


def load_l1_plan_from_artifact_dir(artifact_dir: Path) -> L1PlanContract | None:
    body = _payload_from_contract_json(artifact_dir / "l1_plan_contract.json")
    if not body.get("request_id"):
        return None
    return L1PlanContract(**_filter_dataclass_kwargs(L1PlanContract, body))


def load_validated_request_from_artifact_dir(artifact_dir: Path) -> ValidatedRequest | None:
    path = artifact_dir / "validated_request.json"
    if not path.is_file():
        return None
    return load_validated_request_contract(path)


def fec_from_section_bridge_doc(bridge_doc: dict[str, Any]) -> FinalEvidenceContract | None:
    snap = bridge_doc.get("final_evidence_contract")
    if not isinstance(snap, dict):
        snap = bridge_doc.get("final_evidence_contract_snapshot")
    if not isinstance(snap, dict):
        snap = {}
    items_raw = list(bridge_doc.get("evidence_items") or snap.get("evidence_items") or ())
    evidence_items: list[EvidenceItem] = []
    for idx, row in enumerate(items_raw):
        if not isinstance(row, dict):
            continue
        evidence_items.append(
            EvidenceItem(
                source=str(row.get("source_fact_id") or row.get("source") or f"ev-{idx}"),
                content=str(row.get("content") or row.get("claim_text") or f"[{idx}]"),
                source_type=str(row.get("source_class") or row.get("source_type") or "proof_pool"),
            )
        )
    support = str(bridge_doc.get("support_status") or snap.get("support_status") or SUPPORT_STATUS_PASS)
    request_id = str(snap.get("request_id") or bridge_doc.get("request_id") or "")
    if not request_id and not evidence_items:
        return None
    return FinalEvidenceContract(
        request_id=request_id or "section-fec",
        run_id=str(snap.get("run_id") or bridge_doc.get("run_id") or ""),
        app_id=str(snap.get("app_id") or "apps_rg"),
        trace_id=str(snap.get("trace_id") or ""),
        l5_certification_ref=str(
            snap.get("l5_certification_ref") or bridge_doc.get("l5_certification_ref") or "test:valid:w6"
        ),
        support_status=support if support else SUPPORT_STATUS_PASS,
        support_target_met=support in (SUPPORT_STATUS_PASS, "PASS", "SUPPORTED"),
        final_evidence_digest=str(snap.get("final_evidence_digest") or "")[:64] or "0" * 64,
        evidence_items=tuple(evidence_items) if evidence_items else (),
    )


def load_spine_contracts_for_section(
    artifact_dir: Path,
    runtime_payload: dict[str, Any],
) -> tuple[RouteContract, L1PlanContract, FinalEvidenceContract, ValidatedRequest] | None:
    """Resolve spine contracts from in-memory bridge or artifact dir envelopes."""
    front = runtime_payload.get("_section_front_spine")
    bridge_doc = runtime_payload.get("section_fec_bridge")
    route = getattr(front, "route", None) if front is not None else None
    plan = getattr(front, "l1_plan", None) if front is not None else None
    vr = getattr(front, "validated_request", None) if front is not None else None
    if route is None:
        route = load_route_from_artifact_dir(artifact_dir)
    if plan is None:
        plan = load_l1_plan_from_artifact_dir(artifact_dir)
    if vr is None:
        vr = load_validated_request_from_artifact_dir(artifact_dir)
    fec: FinalEvidenceContract | None = None
    if isinstance(bridge_doc, dict):
        fec = fec_from_section_bridge_doc(bridge_doc)
    if route is None or plan is None or vr is None or fec is None:
        return None
    return route, plan, fec, vr


__all__ = [
    "fec_from_section_bridge_doc",
    "load_l1_plan_from_artifact_dir",
    "load_route_from_artifact_dir",
    "load_spine_contracts_for_section",
    "load_validated_request_from_artifact_dir",
]
