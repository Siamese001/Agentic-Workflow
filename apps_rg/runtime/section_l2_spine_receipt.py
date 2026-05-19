"""One-spine section L2 receipts — PA → L2ExecutionPacket → SealedL2Artifact (Wave 5B).

Product-visible section lanes emit apps_rg-local L2-shaped receipts binding to FEC bridge and
compiled prompt. Not canonical spine Exit, RuntimeExhaustBundle, or durable L4 write.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from apps_rg.runtime.section_fec_bridge import FEC_BRIDGE_ARTIFACT
from apps_rg.runtime.section_front_spine_bridge import fixture_dev_bypass_active
from apps_rg.runtime.section_spine_terminology import CANONICAL_SPINE_CHAIN

L2_EXECUTION_PACKET_ARTIFACT = "l2_execution_packet.json"
SEALED_L2_ARTIFACT = "sealed_l2_artifact.json"
L2_SPINE_RECEIPT_ARTIFACT = "l2_spine_receipt.json"

COMPILED_PROMPT_ARTIFACT = "compiled_prompt_artifact.json"
ROUTE_CONTRACT_ARTIFACT = "route_contract.json"

OBSERVED_CHAIN_WITH_L2_RECEIPTS: tuple[str, ...] = (
    "CLI",
    "canonical_dispatch.section_branch",
    "section_front_spine_bridge",
    "U0",
    "L1",
    "L0",
    "proof_pool_resolver",
    "section_fec_bridge",
    "section_PA",
    "section_L2_execution_packet",
    "section_L2_provider",
    "section_L2_sealed",
    "section_X2",
    "section_X1D",
    "section_X3",
    "section_L6_shadow",
)


class SectionL2SpinePreconditionError(RuntimeError):
    """Raised when product-visible L2 runs without compiled prompt + FEC bridge."""


def l2_spine_kill_switch_enabled() -> bool:
    return os.environ.get("APPS_RG_SECTION_L2_SPINE_KILL_SWITCH", "1").strip() not in (
        "0",
        "false",
        "no",
    )


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _fec_ref(runtime_payload: dict[str, Any]) -> str:
    ref = str(runtime_payload.get("fec_bridge_ref") or "").strip()
    if ref:
        return ref
    ref = str(runtime_payload.get("final_evidence_contract_ref") or "").strip()
    if ref:
        return ref
    return FEC_BRIDGE_ARTIFACT


def _route_ref(runtime_payload: dict[str, Any]) -> str:
    bridge = runtime_payload.get("section_fec_bridge")
    if isinstance(bridge, dict):
        rr = str(bridge.get("route_contract_ref") or "").strip()
        if rr:
            return rr
    return ROUTE_CONTRACT_ARTIFACT


def _artifact_exists(artifact_dir: Path, name: str) -> bool:
    return bool(name) and (artifact_dir / name).is_file()


def assert_section_l2_spine_preconditions(
    runtime_payload: dict[str, Any],
    artifact_dir: Path,
    *,
    product_visible: bool | None = None,
    fixture_dev_only_bypass: bool = False,
    non_product_certified: bool = False,
) -> None:
    """Fail closed before provider/L2 in product-visible mode."""
    if fixture_dev_only_bypass or fixture_dev_bypass_active():
        return
    if non_product_certified:
        return
    pv = product_visible if product_visible is not None else bool(
        runtime_payload.get("product_visible", True)
    )
    if not pv:
        return
    if not l2_spine_kill_switch_enabled():
        return

    compiled_ref = str(runtime_payload.get("compiled_prompt_artifact_ref") or COMPILED_PROMPT_ARTIFACT)
    fec_ref = _fec_ref(runtime_payload)
    if not _artifact_exists(artifact_dir, compiled_ref):
        raise SectionL2SpinePreconditionError(
            f"product-visible section L2 requires {compiled_ref} before L2ExecutionPacket"
        )
    fec_ok = _artifact_exists(artifact_dir, fec_ref) or bool(
        runtime_payload.get("canonical_final_evidence_contract")
    )
    if not fec_ok and not runtime_payload.get("section_fec_bridge"):
        raise SectionL2SpinePreconditionError(
            "product-visible section L2 requires FEC bridge or canonical FinalEvidenceContract"
        )
    if runtime_payload.get("l2_bypass_without_packet") is True:
        raise SectionL2SpinePreconditionError(
            "direct provider/L2 without L2ExecutionPacket is forbidden in product-visible mode"
        )


def build_l2_execution_packet_for_section(
    *,
    section_id: str,
    runtime_payload: dict[str, Any],
    provider_lane: str,
    model_lane: str | None = None,
    producer_stage: str = "section_runtime_adapter",
) -> dict[str, Any]:
    """Build apps_rg-local L2ExecutionPacket (not spine transport envelope)."""
    route_ref = _route_ref(runtime_payload)
    fec_ref = _fec_ref(runtime_payload)
    compiled_ref = str(
        runtime_payload.get("compiled_prompt_artifact_ref") or COMPILED_PROMPT_ARTIFACT
    )
    pa_ref = str(runtime_payload.get("l2_execution_packet_ref") or L2_EXECUTION_PACKET_ARTIFACT)
    run_id = str(runtime_payload.get("run_id") or "")
    cpa = runtime_payload.get("compiled_prompt_artifact_summary")
    if not isinstance(cpa, dict):
        cpa = {}
    return {
        "schema_version": "section_l2_execution_packet_v1",
        "generated_at_utc": _utc_now(),
        "contract_type": "L2ExecutionPacket",
        "producer_stage": producer_stage,
        "consumer_stage": "L2",
        "section_id": section_id,
        "execution_lane": section_id,
        "provider_lane": provider_lane,
        "model_lane": model_lane or str(cpa.get("model") or ""),
        "run_id": run_id,
        "route_contract_ref": route_ref,
        "fec_bridge_ref": fec_ref,
        "final_evidence_contract_ref": fec_ref,
        "compiled_prompt_artifact_ref": compiled_ref,
        "capability_scope": "section_lane_generation",
        "capability_token": "section_lane_generation",
        "sandbox_envelope": "apps_rg_section_lane_no_durable_write",
        "sandbox_scope": "apps_rg_section_lane_no_durable_write",
        "direct_l4_write_allowed": False,
        "product_certification": "NOT_CLAIMED",
        "canonical_exit_claimed": False,
        "fec_bridge_mode": str(
            (runtime_payload.get("section_fec_bridge") or {}).get("fec_bridge_mode")
            if isinstance(runtime_payload.get("section_fec_bridge"), dict)
            else runtime_payload.get("fec_bridge_mode")
            or ""
        ),
        "evidence_contract_consumed": bool(
            runtime_payload.get("evidence_contract_consumed")
            or (isinstance(runtime_payload.get("section_fec_bridge"), dict))
        ),
        "explicit_non_claims": [
            "not canonical spine L2 transport-only execution",
            "not canonical ExitDispositionReceipt",
            "not RuntimeExhaustBundle",
        ],
    }


def build_sealed_l2_artifact_for_section(
    *,
    section_id: str,
    runtime_payload: dict[str, Any],
    artifact_dir: Path,
    provider_request_ref: str = "provider_request.json",
    provider_response_ref: str = "provider_response.json",
    l2_output_ref: str = "l2_output.json",
    section_output_ref: str | None = None,
    x2_gate_outputs_ref: str = "x2_gate_outputs.json",
    x3_disposition_ref: str = "x3_disposition.json",
) -> dict[str, Any]:
    """Build apps_rg-local SealedL2Artifact receipt (section mirror, not spine Exit input)."""
    fec_ref = _fec_ref(runtime_payload)
    compiled_ref = str(
        runtime_payload.get("compiled_prompt_artifact_ref") or COMPILED_PROMPT_ARTIFACT
    )
    l2_packet_ref = str(runtime_payload.get("l2_execution_packet_ref") or L2_EXECUTION_PACKET_ARTIFACT)
    sec_out = section_output_ref or l2_output_ref

    def ref_if_present(name: str) -> str | None:
        return name if _artifact_exists(artifact_dir, name) else None

    return {
        "schema_version": "section_sealed_l2_artifact_v1",
        "generated_at_utc": _utc_now(),
        "contract_type": "SealedL2Artifact",
        "producer_stage": "L2",
        "consumer_stage": "Exit",
        "section_id": section_id,
        "l2_execution_packet_ref": l2_packet_ref,
        "compiled_prompt_artifact_ref": compiled_ref,
        "fec_bridge_ref": fec_ref,
        "final_evidence_contract_ref": fec_ref,
        "provider_request_ref": ref_if_present(provider_request_ref),
        "provider_response_ref": ref_if_present(provider_response_ref),
        "l2_output_ref": ref_if_present(l2_output_ref),
        "section_output_ref": ref_if_present(sec_out),
        "x2_gate_outputs_ref": ref_if_present(x2_gate_outputs_ref),
        "x3_disposition_ref": ref_if_present(x3_disposition_ref),
        "durable_commit_occurred": False,
        "proposed_state_diff_ref": None,
        "canonical_exit_claimed": False,
        "runtime_exhaust_bundle_claimed": False,
        "product_certification": "NOT_CLAIMED",
        "x3_section_mirror_only": True,
        "explicit_non_claims": [
            "x3_disposition_ref is section-local mirror only, not canonical Exit",
            "no durable UWG/L4 commit from this artifact",
        ],
    }


def build_l2_spine_receipt(
    *,
    section_id: str,
    runtime_payload: dict[str, Any],
    artifact_dir: Path,
    provider_request_ref: str = "provider_request.json",
    provider_response_ref: str = "provider_response.json",
    l2_output_ref: str = "l2_output.json",
) -> dict[str, Any]:
    """Master receipt for section L2 spine alignment."""
    fixture_dev = bool(fixture_dev_bypass_active())
    fec_ref = _fec_ref(runtime_payload)
    compiled_ref = str(
        runtime_payload.get("compiled_prompt_artifact_ref") or COMPILED_PROMPT_ARTIFACT
    )
    precond_ok = _artifact_exists(artifact_dir, compiled_ref) and (
        _artifact_exists(artifact_dir, fec_ref) or runtime_payload.get("section_fec_bridge")
    )
    return {
        "schema_version": "l2_spine_receipt_v1",
        "generated_at_utc": _utc_now(),
        "plan_slug": "one-canonical-spine",
        "wave": "5B",
        "lane": section_id,
        "section_id": section_id,
        "run_id": str(runtime_payload.get("run_id") or ""),
        "product_visible": bool(runtime_payload.get("product_visible", True)),
        "fixture_dev_only": fixture_dev,
        "non_product_certified": fixture_dev,
        "spine_mode": "section_lane_modular",
        "l2_alignment_mode": "section_l2_spine_receipt",
        "l2_spine_status": "PASS" if precond_ok else "FAIL",
        "precondition_status": "PASS" if precond_ok else "FAIL",
        "l2_execution_packet_ref": L2_EXECUTION_PACKET_ARTIFACT,
        "sealed_l2_artifact_ref": SEALED_L2_ARTIFACT,
        "compiled_prompt_artifact_ref": compiled_ref,
        "fec_bridge_ref": fec_ref,
        "route_contract_ref": _route_ref(runtime_payload),
        "provider_request_ref": provider_request_ref
        if _artifact_exists(artifact_dir, provider_request_ref)
        else "",
        "provider_response_ref": provider_response_ref
        if _artifact_exists(artifact_dir, provider_response_ref)
        else "",
        "l2_output_ref": l2_output_ref if _artifact_exists(artifact_dir, l2_output_ref) else "",
        "direct_l4_write_allowed": False,
        "durable_commit_occurred": False,
        "canonical_exit_claimed": False,
        "runtime_exhaust_bundle_claimed": False,
        "product_certification": "NOT_CLAIMED",
        "l2_spine_kill_switch_enabled": l2_spine_kill_switch_enabled(),
        "observed_chain": list(OBSERVED_CHAIN_WITH_L2_RECEIPTS),
        "canonical_spine_target": list(CANONICAL_SPINE_CHAIN),
        "explicit_non_claims": [
            "not canonical ExitDispositionReceipt",
            "not RuntimeExhaustBundle",
            "not product certification",
            "not durable write / UWG",
        ],
    }


def emit_l2_execution_packet_artifact(artifact_dir: Path, packet: dict[str, Any]) -> Path:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    path = artifact_dir / L2_EXECUTION_PACKET_ARTIFACT
    path.write_text(json.dumps(packet, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def emit_section_l2_spine_receipt_artifacts(
    artifact_dir: Path,
    *,
    section_id: str,
    runtime_payload: dict[str, Any],
    provider_request_ref: str = "provider_request.json",
    provider_response_ref: str = "provider_response.json",
    l2_output_ref: str = "l2_output.json",
    section_output_ref: str | None = None,
) -> dict[str, Path]:
    """Write sealed_l2_artifact.json and l2_spine_receipt.json after L2 output exists."""
    artifact_dir.mkdir(parents=True, exist_ok=True)
    sealed = build_sealed_l2_artifact_for_section(
        section_id=section_id,
        runtime_payload=runtime_payload,
        artifact_dir=artifact_dir,
        provider_request_ref=provider_request_ref,
        provider_response_ref=provider_response_ref,
        l2_output_ref=l2_output_ref,
        section_output_ref=section_output_ref,
    )
    p_sealed = artifact_dir / SEALED_L2_ARTIFACT
    p_sealed.write_text(json.dumps(sealed, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    receipt = build_l2_spine_receipt(
        section_id=section_id,
        runtime_payload=runtime_payload,
        artifact_dir=artifact_dir,
        provider_request_ref=provider_request_ref,
        provider_response_ref=provider_response_ref,
        l2_output_ref=l2_output_ref,
    )
    p_receipt = artifact_dir / L2_SPINE_RECEIPT_ARTIFACT
    p_receipt.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    runtime_payload["sealed_l2_artifact_ref"] = SEALED_L2_ARTIFACT
    runtime_payload["l2_spine_receipt_ref"] = L2_SPINE_RECEIPT_ARTIFACT
    return {
        "sealed_l2_artifact": p_sealed,
        "l2_spine_receipt": p_receipt,
    }


__all__ = [
    "COMPILED_PROMPT_ARTIFACT",
    "L2_EXECUTION_PACKET_ARTIFACT",
    "L2_SPINE_RECEIPT_ARTIFACT",
    "OBSERVED_CHAIN_WITH_L2_RECEIPTS",
    "SEALED_L2_ARTIFACT",
    "SectionL2SpinePreconditionError",
    "assert_section_l2_spine_preconditions",
    "build_l2_execution_packet_for_section",
    "build_l2_spine_receipt",
    "build_sealed_l2_artifact_for_section",
    "emit_l2_execution_packet_artifact",
    "emit_section_l2_spine_receipt_artifacts",
    "l2_spine_kill_switch_enabled",
]
