"""One-spine section certification receipts — runtime artifact chain proof (Wave 8).

Certification and proof eligibility are derived only from on-disk spine artifacts and
inspected fields. Clean X3_ALLOW is separate from chain completeness.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from apps_rg.runtime.spine.front_contracts import fixture_dev_bypass_active
from apps_rg.runtime.section_spine_terminology import is_spine_final_evidence_contract

ONE_SPINE_CERTIFICATION_RECEIPT_ARTIFACT = "one_spine_certification_receipt.json"
PROOF_ELIGIBILITY_RECEIPT_ARTIFACT = "proof_eligibility_receipt.json"
PRODUCT_CERTIFICATION_RECEIPT_ARTIFACT = "product_certification_receipt.json"

CHAIN_ARTIFACTS: tuple[str, ...] = (
    "validated_request.json",
    "l1_plan_contract.json",
    "route_contract.json",
    "final_evidence_contract_bridge.json",
    "compiled_prompt_artifact.json",
    "l2_execution_packet.json",
    "sealed_l2_artifact.json",
    "exit_disposition_receipt.json",
    "runtime_exhaust_bundle.json",
)

CANONICAL_FEC_ALTERNATIVE = "final_evidence_contract.json"


class SectionOneSpineCertificationPreconditionError(RuntimeError):
    """Raised when certification is claimed without required chain artifacts."""


def certification_kill_switch_enabled() -> bool:
    return os.environ.get("APPS_RG_SECTION_ONE_SPINE_CERT_KILL_SWITCH", "1").strip() not in (
        "0",
        "false",
        "no",
    )


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
        return doc if isinstance(doc, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def _fec_present(artifact_dir: Path) -> tuple[bool, str]:
    """Spine SSOT ``final_evidence_contract.json`` first; legacy bridge basename accepted."""
    for name in (CANONICAL_FEC_ALTERNATIVE, "final_evidence_contract_bridge.json"):
        path = artifact_dir / name
        if not path.is_file():
            continue
        if name == CANONICAL_FEC_ALTERNATIVE:
            doc = _load_json(path)
            if doc and not is_spine_final_evidence_contract(doc):
                # FEC compose may store bridge-shaped doc at spine path — still counts.
                if not isinstance(doc, dict):
                    continue
        return True, name
    return False, ""


def inspect_one_spine_chain(artifact_dir: Path) -> dict[str, Any]:
    """Inspect required chain artifacts and upstream refs."""
    fec_ok, fec_name = _fec_present(artifact_dir)
    artifact_status: list[dict[str, Any]] = []
    for name in CHAIN_ARTIFACTS:
        if name == "final_evidence_contract_bridge.json":
            present = fec_ok
            path_name = fec_name or name
        else:
            present = (artifact_dir / name).is_file()
            path_name = name
        artifact_status.append({"artifact": path_name, "present": present})

    route = _load_json(artifact_dir / "route_contract.json")
    fec = _load_json(artifact_dir / (fec_name or "final_evidence_contract_bridge.json"))
    compiled = _load_json(artifact_dir / "compiled_prompt_artifact.json")
    l2_pkt = _load_json(artifact_dir / "l2_execution_packet.json")
    sealed = _load_json(artifact_dir / "sealed_l2_artifact.json")
    edr = _load_json(artifact_dir / "exit_disposition_receipt.json")
    exhaust = _load_json(artifact_dir / "runtime_exhaust_bundle.json")
    validated = _load_json(artifact_dir / "validated_request.json")
    l1 = _load_json(artifact_dir / "l1_plan_contract.json")

    ref_checks: list[dict[str, Any]] = []

    def chk(label: str, ok: bool, expected: str, actual: str) -> None:
        ref_checks.append({
            "check": label,
            "ok": ok,
            "expected": expected,
            "actual": actual,
        })

    chk(
        "fec_refs_route",
        fec.get("route_contract_ref") == "route_contract.json" if fec else False,
        "route_contract.json",
        str(fec.get("route_contract_ref")),
    )
    chk(
        "compiled_refs_fec_mode",
        bool(compiled.get("fec_bridge_mode") == "section_fec_bridge" or compiled.get("evidence_contract_consumed")),
        "section_fec_bridge consumed",
        f"{compiled.get('fec_bridge_mode')}/{compiled.get('evidence_contract_consumed')}",
    )
    chk(
        "l2_pkt_refs_route",
        l2_pkt.get("route_contract_ref") == "route_contract.json",
        "route_contract.json",
        str(l2_pkt.get("route_contract_ref")),
    )
    chk(
        "l2_pkt_refs_compiled",
        l2_pkt.get("compiled_prompt_artifact_ref") == "compiled_prompt_artifact.json",
        "compiled_prompt_artifact.json",
        str(l2_pkt.get("compiled_prompt_artifact_ref")),
    )
    chk(
        "sealed_refs_l2_pkt",
        sealed.get("l2_execution_packet_ref") == "l2_execution_packet.json",
        "l2_execution_packet.json",
        str(sealed.get("l2_execution_packet_ref")),
    )
    chk(
        "exit_refs_sealed",
        edr.get("sealed_l2_artifact_ref") == "sealed_l2_artifact.json",
        "sealed_l2_artifact.json",
        str(edr.get("sealed_l2_artifact_ref")),
    )
    chk(
        "exhaust_refs_exit",
        exhaust.get("exit_disposition_receipt_ref") == "exit_disposition_receipt.json",
        "exit_disposition_receipt.json",
        str(exhaust.get("exit_disposition_receipt_ref")),
    )
    chk(
        "validated_contract",
        validated.get("contract_type") == "ValidatedRequest" or bool(validated),
        "ValidatedRequest or non-empty",
        str(validated.get("contract_type")),
    )
    chk(
        "l1_contract",
        l1.get("contract_type") == "L1PlanContract" or bool(l1),
        "L1PlanContract or non-empty",
        str(l1.get("contract_type")),
    )

    all_present = all(a["present"] for a in artifact_status)
    all_refs_valid = all(r["ok"] for r in ref_checks)
    required_chain_complete = all_present and all_refs_valid

    return {
        "artifact_status": artifact_status,
        "ref_checks": ref_checks,
        "all_required_artifacts_present": all_present,
        "all_required_refs_valid": all_refs_valid,
        "required_chain_complete": required_chain_complete,
        "fec_artifact_used": fec_name or "",
    }


def _uwg_artifacts_present(artifact_dir: Path) -> bool:
    for name in (
        "uwg_commit_receipt.json",
        "r1b_uwg_receipt.json",
        "durable_write_receipt.json",
    ):
        if (artifact_dir / name).is_file():
            return True
    return False


def _classify_provider(
    *,
    runtime_generation_status: str,
    proof_bundle: dict[str, Any],
) -> tuple[str, bool]:
    rgs = str(runtime_generation_status or "")
    real_llm = rgs == "REAL_LLM" and not bool(proof_bundle.get("test_only_mock_provider"))
    if proof_bundle.get("test_only_mock_provider"):
        return "mock_provider", False
    if rgs == "OFFLINE_CONTRACT_STUB":
        return "offline_contract_stub", False
    if rgs == "REAL_LLM":
        return "real_llm", True
    return rgs.lower() or "unknown", real_llm


def _derive_proof_eligible(
    *,
    chain: dict[str, Any],
    proof_bundle: dict[str, Any],
    runtime_generation_status: str,
    fixture_dev: bool,
) -> tuple[bool, str]:
    if fixture_dev:
        return False, "fixture_dev_bypass_active"
    if not chain.get("required_chain_complete"):
        return False, "required_chain_incomplete"
    provider_class, real_llm = _classify_provider(
        runtime_generation_status=runtime_generation_status,
        proof_bundle=proof_bundle,
    )
    if not real_llm:
        return False, f"provider_classification={provider_class}"
    if proof_bundle.get("test_only_mock_judges"):
        return False, "test_only_mock_judges"
    if proof_bundle.get("test_only_mock_provider"):
        return False, "test_only_mock_provider"
    lane_pe = bool(proof_bundle.get("proof_eligible"))
    if not lane_pe:
        return False, str(proof_bundle.get("proof_closeout_note") or "lane_proof_bundle_not_eligible")
    return True, "chain_complete_and_lane_proof_bundle_eligible"


def build_one_spine_certification_receipt(
    *,
    section_id: str,
    runtime_payload: dict[str, Any],
    artifact_dir: Path,
    chain: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": "one_spine_certification_receipt_v1",
        "generated_at_utc": _utc_now(),
        "contract_type": "OneSpineCertificationReceipt",
        "plan_slug": "one-canonical-spine",
        "wave": "8",
        "section_id": section_id,
        "run_id": str(runtime_payload.get("run_id") or ""),
        "required_chain_complete": bool(chain.get("required_chain_complete")),
        "all_required_artifacts_present": bool(chain.get("all_required_artifacts_present")),
        "all_required_refs_valid": bool(chain.get("all_required_refs_valid")),
        "chain_artifacts_inspected": list(CHAIN_ARTIFACTS),
        "artifact_status": chain.get("artifact_status"),
        "ref_checks": chain.get("ref_checks"),
        "fec_artifact_used": chain.get("fec_artifact_used"),
        "certification_status": "PASS" if chain.get("required_chain_complete") else "FAIL",
        "x3_allow_required_for_chain": False,
        "explicit_non_claims": [
            "chain completeness does not require X3_ALLOW",
            "not full tests/_apps_contract suite certification",
        ],
    }


def build_proof_eligibility_receipt(
    *,
    section_id: str,
    runtime_payload: dict[str, Any],
    chain: dict[str, Any],
    proof_bundle: dict[str, Any],
    runtime_generation_status: str,
    x3_code: str,
) -> dict[str, Any]:
    fixture_dev = bool(fixture_dev_bypass_active())
    non_product = fixture_dev or bool(proof_bundle.get("test_only_mock_provider"))
    provider_class, real_llm = _classify_provider(
        runtime_generation_status=runtime_generation_status,
        proof_bundle=proof_bundle,
    )
    proof_eligible, reason = _derive_proof_eligible(
        chain=chain,
        proof_bundle=proof_bundle,
        runtime_generation_status=runtime_generation_status,
        fixture_dev=fixture_dev,
    )
    return {
        "schema_version": "proof_eligibility_receipt_v1",
        "generated_at_utc": _utc_now(),
        "contract_type": "ProofEligibilityReceipt",
        "section_id": section_id,
        "run_id": str(runtime_payload.get("run_id") or ""),
        "proof_eligible": proof_eligible,
        "proof_eligibility_reason": reason,
        "provider_classification": provider_class,
        "real_llm_used": real_llm,
        "fixture_dev_only": fixture_dev,
        "non_product_certified": non_product,
        "x3_code": x3_code,
        "x3_allow_is_separate_from_chain": True,
        "exit_disposition_receipt_ref": "exit_disposition_receipt.json",
        "runtime_exhaust_bundle_ref": "runtime_exhaust_bundle.json",
        "lane_proof_bundle_proof_eligible": bool(proof_bundle.get("proof_eligible")),
        "product_certification": "NOT_CLAIMED",
    }


def build_product_certification_receipt(
    *,
    section_id: str,
    runtime_payload: dict[str, Any],
    chain: dict[str, Any],
    proof_bundle: dict[str, Any],
    runtime_generation_status: str,
    x3_code: str,
    artifact_dir: Path,
    full_apps_contract_suite_passed: bool = False,
) -> dict[str, Any]:
    fixture_dev = bool(fixture_dev_bypass_active())
    proof_eligible, proof_reason = _derive_proof_eligible(
        chain=chain,
        proof_bundle=proof_bundle,
        runtime_generation_status=runtime_generation_status,
        fixture_dev=fixture_dev,
    )
    uwg_ran = _uwg_artifacts_present(artifact_dir)
    durable_write_certified = uwg_ran and bool(
        _load_json(artifact_dir / "uwg_commit_receipt.json").get("durable_commit_occurred")
        or _load_json(artifact_dir / "r1b_uwg_receipt.json").get("commit_occurred")
    )

    chain_ok = bool(chain.get("required_chain_complete"))
    can_certify = (
        chain_ok
        and proof_eligible
        and not fixture_dev
        and not bool(proof_bundle.get("test_only_mock_provider"))
    )
    product_cert = "ONE_SPINE_SECTION_CERTIFIED" if can_certify else "NOT_CLAIMED"
    if not chain_ok:
        cert_reason = "required_chain_incomplete"
    elif fixture_dev:
        cert_reason = "fixture_dev_bypass"
    elif not proof_eligible:
        cert_reason = proof_reason
    elif can_certify:
        cert_reason = "chain_artifacts_and_proof_eligibility_pass"
    else:
        cert_reason = "policy_blocked"

    return {
        "schema_version": "product_certification_receipt_v1",
        "generated_at_utc": _utc_now(),
        "contract_type": "ProductCertificationReceipt",
        "section_id": section_id,
        "run_id": str(runtime_payload.get("run_id") or ""),
        "product_certification": product_cert,
        "product_certification_reason": cert_reason,
        "required_chain_complete": chain_ok,
        "all_required_artifacts_present": bool(chain.get("all_required_artifacts_present")),
        "all_required_refs_valid": bool(chain.get("all_required_refs_valid")),
        "proof_eligible": proof_eligible,
        "x3_code": x3_code,
        "x3_allow_not_required_for_chain": True,
        "durable_write_certified": durable_write_certified,
        "full_apps_contract_suite_certified": bool(full_apps_contract_suite_passed),
        "fixture_dev_only": fixture_dev,
        "non_product_certified": fixture_dev or not can_certify,
        "explicit_non_claims": [
            "not release signoff unless separately scoped",
            "full_apps_contract_suite_certified only when full suite ran and passed",
            "durable_write_certified only when UWG artifacts prove commit",
        ],
    }


def assert_certification_preconditions(
    runtime_payload: dict[str, Any],
    artifact_dir: Path,
    *,
    chain: dict[str, Any],
    product_certification: str,
) -> None:
    if fixture_dev_bypass_active():
        return
    if not certification_kill_switch_enabled():
        return
    if runtime_payload.get("certification_bypass_without_chain") is True:
        raise SectionOneSpineCertificationPreconditionError(
            "certification bypass without chain is forbidden in product-visible mode"
        )
    if product_certification == "ONE_SPINE_SECTION_CERTIFIED" and not chain.get("required_chain_complete"):
        raise SectionOneSpineCertificationPreconditionError(
            "cannot claim ONE_SPINE_SECTION_CERTIFIED when required_chain_complete is false"
        )


def emit_section_one_spine_certification_artifacts(
    artifact_dir: Path,
    *,
    section_id: str,
    runtime_payload: dict[str, Any],
    proof_bundle: dict[str, Any],
    runtime_generation_status: str,
    full_apps_contract_suite_passed: bool = False,
) -> dict[str, Path]:
    """Write Wave 8 certification receipts after full spine chain + L6 handoff exist."""
    artifact_dir.mkdir(parents=True, exist_ok=True)
    chain = inspect_one_spine_chain(artifact_dir)
    edr = _load_json(artifact_dir / "exit_disposition_receipt.json")
    x3_code = str(
        edr.get("x3_code")
        or (edr.get("x3_disposition") or {}).get("x3_code")
        or _load_json(artifact_dir / "x3_disposition.json").get("x3_code")
        or "UNKNOWN"
    )

    cert = build_one_spine_certification_receipt(
        section_id=section_id,
        runtime_payload=runtime_payload,
        artifact_dir=artifact_dir,
        chain=chain,
    )
    p_cert = artifact_dir / ONE_SPINE_CERTIFICATION_RECEIPT_ARTIFACT
    p_cert.write_text(json.dumps(cert, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    pe = build_proof_eligibility_receipt(
        section_id=section_id,
        runtime_payload=runtime_payload,
        chain=chain,
        proof_bundle=proof_bundle,
        runtime_generation_status=runtime_generation_status,
        x3_code=x3_code,
    )
    p_pe = artifact_dir / PROOF_ELIGIBILITY_RECEIPT_ARTIFACT
    p_pe.write_text(json.dumps(pe, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    pc = build_product_certification_receipt(
        section_id=section_id,
        runtime_payload=runtime_payload,
        chain=chain,
        proof_bundle=proof_bundle,
        runtime_generation_status=runtime_generation_status,
        x3_code=x3_code,
        full_apps_contract_suite_passed=full_apps_contract_suite_passed,
        artifact_dir=artifact_dir,
    )
    assert_certification_preconditions(
        runtime_payload,
        artifact_dir,
        chain=chain,
        product_certification=str(pc.get("product_certification")),
    )
    p_pc = artifact_dir / PRODUCT_CERTIFICATION_RECEIPT_ARTIFACT
    p_pc.write_text(json.dumps(pc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    runtime_payload["one_spine_certification_receipt_ref"] = ONE_SPINE_CERTIFICATION_RECEIPT_ARTIFACT
    runtime_payload["proof_eligibility_receipt_ref"] = PROOF_ELIGIBILITY_RECEIPT_ARTIFACT
    runtime_payload["product_certification_receipt_ref"] = PRODUCT_CERTIFICATION_RECEIPT_ARTIFACT

    return {
        "one_spine_certification_receipt": p_cert,
        "proof_eligibility_receipt": p_pe,
        "product_certification_receipt": p_pc,
    }


__all__ = [
    "CHAIN_ARTIFACTS",
    "ONE_SPINE_CERTIFICATION_RECEIPT_ARTIFACT",
    "PRODUCT_CERTIFICATION_RECEIPT_ARTIFACT",
    "PROOF_ELIGIBILITY_RECEIPT_ARTIFACT",
    "SectionOneSpineCertificationPreconditionError",
    "build_one_spine_certification_receipt",
    "build_product_certification_receipt",
    "build_proof_eligibility_receipt",
    "certification_kill_switch_enabled",
    "emit_section_one_spine_certification_artifacts",
    "inspect_one_spine_chain",
]
