"""Per-stage JSON receipts for canonical apps_lic spine runs."""

from __future__ import annotations

import dataclasses
import hashlib
import json
from enum import Enum
from pathlib import Path
from typing import Any, Mapping

STAGE_RECEIPT_SCHEMA_VERSION = "apps_lic.stage_receipt.v1"

FILENAME_INGRESS_RAW = "ingress_raw.json"
FILENAME_U0_RECEIPT = "u0_receipt.json"
FILENAME_L1_PLAN = "l1_plan_contract.json"
FILENAME_ROUTE_CONTRACT = "route_contract.json"
FILENAME_C0_FEC = "c0_final_evidence_contract.json"
FILENAME_FEC_SUMMARY = "fec_summary.json"
FILENAME_C03_SENDER_PROOF = "c03_sender_proof_packet.json"
FILENAME_PA_RECEIPT = "pa_receipt.json"
FILENAME_L3_WORKFLOW = "l3_workflow_receipt.json"
FILENAME_L2_EXECUTION = "l2_execution_receipt.json"
FILENAME_W4_CANDIDATE_BATCH = "w4_candidate_batch.json"
FILENAME_C03_POSTGEN_VALIDATION = "c03_postgen_claim_validation.json"
FILENAME_W5_VALIDATION_EXIT = "w5_validation_exit.json"
FILENAME_EXIT_DISPOSITION = "exit_disposition_receipt.json"
FILENAME_SPINE_MANIFEST = "spine_run_manifest.json"
FILENAME_ROUTE_PRE_RESEARCH = "route_contract_pre_research.json"
FILENAME_RESEARCH_BRIDGE_REQUEST = "research_bridge_request.json"
FILENAME_RESEARCH_BRIDGE_RESPONSE = "research_bridge_response.json"
FILENAME_MOCK_ELIMINATION_PROOF = "mock_elimination_proof.json"

_C0_READINESS_GATE_PREFIX = "c0_readiness:"
_C0_RECIPIENT_CLASS_GATE_PREFIX = "c0_recipient_class:"
_C0_RECIPIENT_CLASS_VALUE_PREFIX = "c0_recipient_class_value:"
_C0_RECIPIENT_CLASS_CONFIDENCE_PREFIX = "c0_recipient_class_confidence:"


def _canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


def _sha256_digest(payload: Any) -> str:
    return "sha256:" + hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


def _digest_for(obj: Any, *, fallback_payload: Any | None = None) -> str:
    for attr in ("deterministic_digest", "compilation_hash", "validated_request_digest", "input_payload_digest", "profile_manifest_digest", "sealed_l2_digest"):
        val = getattr(obj, attr, None)
        if isinstance(val, str) and val:
            return val if val.startswith("sha256:") else f"sha256:{val}" if len(val) == 64 else val
    if fallback_payload is not None:
        return _sha256_digest(fallback_payload)
    return ""


def _serialize_value(obj: Any) -> Any:
    if obj is None:
        return None
    if isinstance(obj, Enum):
        return obj.value
    if dataclasses.is_dataclass(obj):
        return {k: _serialize_value(v) for k, v in dataclasses.asdict(obj).items()}
    if isinstance(obj, (list, tuple)):
        return [_serialize_value(v) for v in obj]
    if isinstance(obj, Mapping):
        return {str(k): _serialize_value(v) for k, v in obj.items()}
    return obj


def stage_receipt_envelope(
    *,
    stage: str,
    request_id: str,
    run_id: str,
    trace_id: str,
    digest: str,
    artifact_ref: str,
    payload: Mapping[str, Any],
    upstream_receipt_refs: tuple[str, ...] = (),
    downstream_receipt_refs: tuple[str, ...] = (),
) -> dict[str, Any]:
    return {
        "schema_version": STAGE_RECEIPT_SCHEMA_VERSION,
        "stage": stage,
        "request_id": request_id,
        "run_id": run_id,
        "trace_id": trace_id,
        "digest": digest,
        "artifact_ref": artifact_ref,
        "upstream_receipt_refs": list(upstream_receipt_refs),
        "downstream_receipt_refs": list(downstream_receipt_refs),
        "payload": dict(payload),
    }


def write_stage_receipt(path: Path, envelope: dict[str, Any]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(envelope, indent=2, sort_keys=True, default=str), encoding="utf-8")
    return str(path)


def build_u0_receipt(
    validated_request: Any,
    reflection: Any,
    *,
    upstream_receipt_refs: tuple[str, ...] = (FILENAME_INGRESS_RAW,),
    downstream_receipt_refs: tuple[str, ...] = (FILENAME_L1_PLAN,),
) -> dict[str, Any]:
    reflection_dict = _serialize_value(reflection)
    body = {
        "pass_status": reflection_dict.get("pass_status") if reflection_dict else True,
        "validated_request_digest": reflection_dict.get("validated_request_digest", ""),
        "input_payload_digest": reflection_dict.get("input_payload_digest", ""),
        "pointers_total": reflection_dict.get("pointers_total", 0),
        "app_id": validated_request.app_id,
        "task_class": (validated_request.app_payload or {}).get("transport", {}).get("task_class", ""),
    }
    digest = (
        reflection_dict.get("validated_request_digest")
        or _digest_for(validated_request, fallback_payload=body)
    )
    return stage_receipt_envelope(
        stage="U0",
        request_id=validated_request.request_id,
        run_id=validated_request.run_id,
        trace_id=validated_request.trace_id,
        digest=str(digest),
        artifact_ref=FILENAME_U0_RECEIPT,
        payload=body,
        upstream_receipt_refs=upstream_receipt_refs,
        downstream_receipt_refs=downstream_receipt_refs,
    )


def build_l1_receipt(
    l1: Any,
    *,
    upstream_receipt_refs: tuple[str, ...] = (FILENAME_U0_RECEIPT,),
    downstream_receipt_refs: tuple[str, ...] = (FILENAME_ROUTE_CONTRACT,),
) -> dict[str, Any]:
    payload = _serialize_value(l1)
    digest = _digest_for(l1, fallback_payload=payload)
    return stage_receipt_envelope(
        stage="L1",
        request_id=l1.request_id,
        run_id=l1.run_id,
        trace_id=l1.trace_id,
        digest=digest,
        artifact_ref=FILENAME_L1_PLAN,
        payload=payload,
        upstream_receipt_refs=upstream_receipt_refs,
        downstream_receipt_refs=downstream_receipt_refs,
    )


def build_route_receipt(
    route: Any,
    route_payload: Mapping[str, Any],
    *,
    upstream_receipt_refs: tuple[str, ...] = (FILENAME_L1_PLAN,),
    downstream_receipt_refs: tuple[str, ...] = (),
) -> dict[str, Any]:
    digest = getattr(route, "l5_certification_ref", "") or _sha256_digest(route_payload)
    return stage_receipt_envelope(
        stage="L0",
        request_id=route.request_id,
        run_id=route.run_id,
        trace_id=route.trace_id,
        digest=str(digest),
        artifact_ref=FILENAME_ROUTE_CONTRACT,
        payload=dict(route_payload),
        upstream_receipt_refs=upstream_receipt_refs,
        downstream_receipt_refs=downstream_receipt_refs,
    )


def build_c0_receipt(
    fec: Any,
    *,
    upstream_receipt_refs: tuple[str, ...] = (FILENAME_ROUTE_CONTRACT,),
    downstream_receipt_refs: tuple[str, ...] = (FILENAME_PA_RECEIPT,),
) -> dict[str, Any]:
    payload = _serialize_value(fec)
    digest = _digest_for(fec, fallback_payload={"compilation_hash": fec.compilation_hash, "item_count": len(fec.evidence_items)})
    return stage_receipt_envelope(
        stage="C0",
        request_id=fec.request_id,
        run_id=fec.run_id,
        trace_id=fec.trace_id,
        digest=digest,
        artifact_ref=FILENAME_C0_FEC,
        payload=payload,
        upstream_receipt_refs=upstream_receipt_refs,
        downstream_receipt_refs=downstream_receipt_refs,
    )


def build_c0_summary(fec: Any) -> dict[str, Any]:
    gate_refs = tuple(str(ref) for ref in getattr(fec, "gate_verdict_refs", ()))
    audit_refs = tuple(str(ref) for ref in getattr(fec, "audit_refs", ()))

    def _gate_value(prefix: str, default: str = "") -> str:
        for ref in gate_refs:
            if ref.startswith(prefix):
                return ref.removeprefix(prefix)
        return default

    def _audit_value(prefix: str, default: str = "") -> str:
        for ref in audit_refs:
            if ref.startswith(prefix):
                return ref.removeprefix(prefix)
        return default

    return {
        "compilation_hash": fec.compilation_hash,
        "item_count": len(fec.evidence_items),
        "support_status": fec.support_status,
        "evidence_sufficiency_score": fec.evidence_sufficiency_score,
        "readiness_status": _gate_value(
            _C0_READINESS_GATE_PREFIX,
            "C0_OPPORTUNITY_INGESTION_REQUIRED",
        ),
        "recipient_class_status": _gate_value(
            _C0_RECIPIENT_CLASS_GATE_PREFIX,
            "C0_OPPORTUNITY_INGESTION_REQUIRED",
        ),
        "derived_recipient_class": _gate_value(
            _C0_RECIPIENT_CLASS_VALUE_PREFIX,
            "UNKNOWN",
        ),
        "recipient_class_confidence": _gate_value(
            _C0_RECIPIENT_CLASS_CONFIDENCE_PREFIX,
            "0.000",
        ),
        "recipient_class_reason_codes": [
            code
            for code in _audit_value("c0_recipient_class_reason_codes:").split(",")
            if code
        ],
        "recipient_class_contradiction_status": _audit_value(
            "c0_recipient_class_contradiction_status:",
        ),
        "recipient_class_hitl_required": (
            _audit_value("c0_recipient_class_hitl_required:", "true") == "true"
        ),
        "u0_recipient_class_hint": _audit_value("c0_u0_recipient_class_hint:"),
        "u0_recipient_class_hint_authority": _audit_value(
            "c0_u0_recipient_class_hint_authority:",
            "false",
        ),
        "source_snapshot_ids": list(getattr(fec, "snapshot_refs", ()) or ()),
        "freshness_receipts": list(getattr(fec, "freshness_receipts", ()) or ()),
        "gate_verdict_refs": list(gate_refs),
        "audit_refs": list(audit_refs),
        "request_id": fec.request_id,
        "run_id": fec.run_id,
        "trace_id": fec.trace_id,
        "upstream_receipt_ref": FILENAME_C0_FEC,
    }


def build_c03_receipt(
    c03: Any,
    *,
    upstream_receipt_refs: tuple[str, ...] = (FILENAME_C0_FEC, FILENAME_FEC_SUMMARY),
    downstream_receipt_refs: tuple[str, ...] = (FILENAME_PA_RECEIPT,),
) -> dict[str, Any]:
    payload = c03.to_receipt_payload()
    digest = payload.get("proof_packet_id") or _sha256_digest(payload)
    return stage_receipt_envelope(
        stage="C0.3",
        request_id=c03.request_id,
        run_id=c03.run_id,
        trace_id=c03.trace_id,
        digest=str(digest),
        artifact_ref=FILENAME_C03_SENDER_PROOF,
        payload=payload,
        upstream_receipt_refs=upstream_receipt_refs,
        downstream_receipt_refs=downstream_receipt_refs,
    )


def build_pa_receipt(
    prompt: Any,
    *,
    upstream_receipt_refs: tuple[str, ...] = (
        FILENAME_C03_SENDER_PROOF,
        FILENAME_C0_FEC,
        FILENAME_L1_PLAN,
    ),
    downstream_receipt_refs: tuple[str, ...] = (FILENAME_L3_WORKFLOW,),
) -> dict[str, Any]:
    payload = _serialize_value(prompt)
    digest = _digest_for(prompt, fallback_payload=payload)
    return stage_receipt_envelope(
        stage="PA",
        request_id=prompt.request_id,
        run_id=prompt.run_id,
        trace_id=prompt.trace_id,
        digest=digest,
        artifact_ref=FILENAME_PA_RECEIPT,
        payload=payload,
        upstream_receipt_refs=upstream_receipt_refs,
        downstream_receipt_refs=downstream_receipt_refs,
    )


def build_l3_receipt(
    l3_receipt: Any,
    step: Any,
    *,
    upstream_receipt_refs: tuple[str, ...] = (FILENAME_PA_RECEIPT, FILENAME_ROUTE_CONTRACT),
    downstream_receipt_refs: tuple[str, ...] = (FILENAME_L2_EXECUTION,),
) -> dict[str, Any]:
    payload = {
        "orchestration_receipt": _serialize_value(l3_receipt),
        "step_contract": _serialize_value(step),
    }
    digest = _digest_for(l3_receipt, fallback_payload=payload)
    return stage_receipt_envelope(
        stage="L3",
        request_id=l3_receipt.request_id,
        run_id=l3_receipt.run_id,
        trace_id=l3_receipt.trace_root,
        digest=digest,
        artifact_ref=FILENAME_L3_WORKFLOW,
        payload=payload,
        upstream_receipt_refs=upstream_receipt_refs,
        downstream_receipt_refs=downstream_receipt_refs,
    )


def build_l2_receipt(
    l2: Any,
    *,
    upstream_receipt_refs: tuple[str, ...] = (FILENAME_L3_WORKFLOW,),
    downstream_receipt_refs: tuple[str, ...] = (FILENAME_W4_CANDIDATE_BATCH,),
) -> dict[str, Any]:
    payload = _serialize_value(l2)
    digest = _digest_for(l2, fallback_payload=payload)
    return stage_receipt_envelope(
        stage="L2",
        request_id=l2.request_id,
        run_id=l2.run_id,
        trace_id=l2.trace_id,
        digest=digest,
        artifact_ref=FILENAME_L2_EXECUTION,
        payload=payload,
        upstream_receipt_refs=upstream_receipt_refs,
        downstream_receipt_refs=downstream_receipt_refs,
    )


def build_w4_candidate_batch_receipt(
    result: Any,
    *,
    upstream_receipt_refs: tuple[str, ...] = (FILENAME_L2_EXECUTION,),
    downstream_receipt_refs: tuple[str, ...] = (FILENAME_C03_POSTGEN_VALIDATION,),
) -> dict[str, Any]:
    payload = result.to_receipt_payload()
    digest = payload.get("l2_generated_content_digest") or _sha256_digest(payload)
    return stage_receipt_envelope(
        stage="W4.CANDIDATES",
        request_id=result.request_id,
        run_id=result.run_id,
        trace_id=result.trace_id,
        digest=str(digest),
        artifact_ref=FILENAME_W4_CANDIDATE_BATCH,
        payload=payload,
        upstream_receipt_refs=upstream_receipt_refs,
        downstream_receipt_refs=downstream_receipt_refs,
    )


def build_c03_postgen_receipt(
    result: Any,
    *,
    upstream_receipt_refs: tuple[str, ...] = (FILENAME_W4_CANDIDATE_BATCH,),
    downstream_receipt_refs: tuple[str, ...] = (FILENAME_W5_VALIDATION_EXIT,),
) -> dict[str, Any]:
    payload = result.to_receipt_payload()
    digest = payload.get("l2_generated_content_digest") or _sha256_digest(payload)
    return stage_receipt_envelope(
        stage="C0.3.POSTGEN",
        request_id=result.request_id,
        run_id=result.run_id,
        trace_id=result.trace_id,
        digest=str(digest),
        artifact_ref=FILENAME_C03_POSTGEN_VALIDATION,
        payload=payload,
        upstream_receipt_refs=upstream_receipt_refs,
        downstream_receipt_refs=downstream_receipt_refs,
    )


def build_w5_validation_exit_receipt(
    result: Any,
    *,
    upstream_receipt_refs: tuple[str, ...] = (FILENAME_C03_POSTGEN_VALIDATION,),
    downstream_receipt_refs: tuple[str, ...] = (FILENAME_EXIT_DISPOSITION,),
) -> dict[str, Any]:
    payload = result.to_receipt_payload()
    digest = payload.get("proof_packet_id") or _sha256_digest(payload)
    return stage_receipt_envelope(
        stage="W5.VALIDATION_EXIT",
        request_id=result.request_id,
        run_id=result.run_id,
        trace_id=result.trace_id,
        digest=str(digest),
        artifact_ref=FILENAME_W5_VALIDATION_EXIT,
        payload=payload,
        upstream_receipt_refs=upstream_receipt_refs,
        downstream_receipt_refs=downstream_receipt_refs,
    )


def build_exit_receipt(
    x3: Any,
    *,
    x3_disposition: str,
    exit_status: str,
    outcome_authorized: bool,
    upstream_receipt_refs: tuple[str, ...] = (FILENAME_L2_EXECUTION,),
    downstream_receipt_refs: tuple[str, ...] = (FILENAME_SPINE_MANIFEST,),
) -> dict[str, Any]:
    payload = {
        "x3_disposition": x3_disposition,
        "exit_status": exit_status,
        "outcome_authorized": outcome_authorized,
        "eval_score": x3.eval_score,
        "sealed_l2_digest": x3.sealed_l2_digest,
        "gate_verdict_refs": list(x3.gate_verdict_refs),
        "l5_certification_ref": x3.l5_certification_ref,
        "final_output": _serialize_value(dict(x3.final_output) if x3.final_output else {}),
    }
    digest = x3.l5_certification_ref or _sha256_digest(payload)
    return stage_receipt_envelope(
        stage="EXIT",
        request_id=x3.request_id,
        run_id=x3.run_id,
        trace_id=x3.trace_id,
        digest=str(digest),
        artifact_ref=FILENAME_EXIT_DISPOSITION,
        payload=payload,
        upstream_receipt_refs=upstream_receipt_refs,
        downstream_receipt_refs=downstream_receipt_refs,
    )


def managed_workflow_downstream_refs(
    *,
    c0_invoked: bool,
    c03_invoked: bool = False,
    pa_invoked: bool,
    w4_candidate_invoked: bool = False,
    c03_postgen_invoked: bool = False,
    w5_validation_exit_invoked: bool = False,
) -> tuple[str, ...]:
    refs: list[str] = []
    if c0_invoked:
        refs.append(FILENAME_C0_FEC)
    if c03_invoked:
        refs.append(FILENAME_C03_SENDER_PROOF)
    if pa_invoked:
        refs.append(FILENAME_PA_RECEIPT)
    refs.extend((FILENAME_L3_WORKFLOW, FILENAME_L2_EXECUTION))
    if w4_candidate_invoked:
        refs.append(FILENAME_W4_CANDIDATE_BATCH)
    if c03_postgen_invoked:
        refs.append(FILENAME_C03_POSTGEN_VALIDATION)
    if w5_validation_exit_invoked:
        refs.append(FILENAME_W5_VALIDATION_EXIT)
    refs.append(FILENAME_EXIT_DISPOSITION)
    return tuple(refs)


def standard_stage_receipt_refs(
    *,
    terminal_r5: bool,
    c0_invoked: bool,
    c03_invoked: bool = False,
    pa_invoked: bool,
    w4_candidate_invoked: bool = False,
    c03_postgen_invoked: bool = False,
    w5_validation_exit_invoked: bool = False,
    l3_participated: bool,
) -> tuple[str, ...]:
    refs = [
        FILENAME_INGRESS_RAW,
        FILENAME_U0_RECEIPT,
        FILENAME_L1_PLAN,
        FILENAME_ROUTE_CONTRACT,
    ]
    if terminal_r5:
        refs.append(FILENAME_EXIT_DISPOSITION)
        refs.append(FILENAME_SPINE_MANIFEST)
        return tuple(refs)
    if c0_invoked:
        refs.append(FILENAME_C0_FEC)
        refs.append(FILENAME_FEC_SUMMARY)
    if c03_invoked:
        refs.append(FILENAME_C03_SENDER_PROOF)
    if pa_invoked:
        refs.append(FILENAME_PA_RECEIPT)
    if l3_participated:
        refs.append(FILENAME_L3_WORKFLOW)
        refs.append(FILENAME_L2_EXECUTION)
        if w4_candidate_invoked:
            refs.append(FILENAME_W4_CANDIDATE_BATCH)
        if c03_postgen_invoked:
            refs.append(FILENAME_C03_POSTGEN_VALIDATION)
        if w5_validation_exit_invoked:
            refs.append(FILENAME_W5_VALIDATION_EXIT)
    refs.extend(
        (
            FILENAME_EXIT_DISPOSITION,
            FILENAME_SPINE_MANIFEST,
        )
    )
    return tuple(refs)


def c0_block_stage_receipt_refs() -> tuple[str, ...]:
    return (
        FILENAME_INGRESS_RAW,
        FILENAME_U0_RECEIPT,
        FILENAME_L1_PLAN,
        FILENAME_ROUTE_CONTRACT,
        FILENAME_C0_FEC,
        FILENAME_FEC_SUMMARY,
        FILENAME_SPINE_MANIFEST,
    )


def c03_block_stage_receipt_refs() -> tuple[str, ...]:
    return (
        FILENAME_INGRESS_RAW,
        FILENAME_U0_RECEIPT,
        FILENAME_L1_PLAN,
        FILENAME_ROUTE_CONTRACT,
        FILENAME_C0_FEC,
        FILENAME_FEC_SUMMARY,
        FILENAME_C03_SENDER_PROOF,
        FILENAME_SPINE_MANIFEST,
    )


def c03_postgen_block_stage_receipt_refs() -> tuple[str, ...]:
    return (
        FILENAME_INGRESS_RAW,
        FILENAME_U0_RECEIPT,
        FILENAME_L1_PLAN,
        FILENAME_ROUTE_CONTRACT,
        FILENAME_C0_FEC,
        FILENAME_FEC_SUMMARY,
        FILENAME_C03_SENDER_PROOF,
        FILENAME_PA_RECEIPT,
        FILENAME_L3_WORKFLOW,
        FILENAME_L2_EXECUTION,
        FILENAME_W4_CANDIDATE_BATCH,
        FILENAME_C03_POSTGEN_VALIDATION,
        FILENAME_SPINE_MANIFEST,
    )


def w5_validation_exit_block_stage_receipt_refs() -> tuple[str, ...]:
    return (
        FILENAME_INGRESS_RAW,
        FILENAME_U0_RECEIPT,
        FILENAME_L1_PLAN,
        FILENAME_ROUTE_CONTRACT,
        FILENAME_C0_FEC,
        FILENAME_FEC_SUMMARY,
        FILENAME_C03_SENDER_PROOF,
        FILENAME_PA_RECEIPT,
        FILENAME_L3_WORKFLOW,
        FILENAME_L2_EXECUTION,
        FILENAME_W4_CANDIDATE_BATCH,
        FILENAME_C03_POSTGEN_VALIDATION,
        FILENAME_W5_VALIDATION_EXIT,
        FILENAME_EXIT_DISPOSITION,
        FILENAME_SPINE_MANIFEST,
    )


def w4_candidate_block_stage_receipt_refs() -> tuple[str, ...]:
    return (
        FILENAME_INGRESS_RAW,
        FILENAME_U0_RECEIPT,
        FILENAME_L1_PLAN,
        FILENAME_ROUTE_CONTRACT,
        FILENAME_C0_FEC,
        FILENAME_FEC_SUMMARY,
        FILENAME_C03_SENDER_PROOF,
        FILENAME_PA_RECEIPT,
        FILENAME_L3_WORKFLOW,
        FILENAME_L2_EXECUTION,
        FILENAME_W4_CANDIDATE_BATCH,
        FILENAME_SPINE_MANIFEST,
    )
