"""One-spine no-two-path runtime inspection (Wave 9).

Derives ordering and authority preconditions from on-disk spine artifacts only.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from apps_rg.runtime.section_one_spine_certification import inspect_one_spine_chain


def _load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
        return doc if isinstance(doc, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def inspect_no_two_path_lane(artifact_dir: Path) -> dict[str, Any]:
    """Inspect one lane artifact dir for no-two-path preconditions."""
    chain = inspect_one_spine_chain(artifact_dir)
    validated = _load_json(artifact_dir / "validated_request.json")
    route = _load_json(artifact_dir / "route_contract.json")
    fec = _load_json(artifact_dir / "final_evidence_contract_bridge.json")
    if not fec:
        fec = _load_json(artifact_dir / "final_evidence_contract.json")
    compiled = _load_json(artifact_dir / "compiled_prompt_artifact.json")
    l2_pkt = _load_json(artifact_dir / "l2_execution_packet.json")
    sealed = _load_json(artifact_dir / "sealed_l2_artifact.json")
    edr = _load_json(artifact_dir / "exit_disposition_receipt.json")
    exhaust = _load_json(artifact_dir / "runtime_exhaust_bundle.json")
    l6_handoff = _load_json(artifact_dir / "l6_shadow_handoff_receipt.json")
    l6_pkg = _load_json(artifact_dir / "l6_shadow_eval_package.json")
    cert = _load_json(artifact_dir / "one_spine_certification_receipt.json")
    pe = _load_json(artifact_dir / "proof_eligibility_receipt.json")
    pc = _load_json(artifact_dir / "product_certification_receipt.json")
    fec_receipt = _load_json(artifact_dir / "c0_fec_bridge_receipt.json")

    proof_pool_after_front_spine = (
        all(
            (artifact_dir / n).is_file()
            for n in ("validated_request.json", "l1_plan_contract.json", "route_contract.json")
        )
        and bool(route)
        and (
            (artifact_dir / "final_evidence_contract_bridge.json").is_file()
            or (artifact_dir / "final_evidence_contract.json").is_file()
        )
    )

    pa_evidence_consumed = bool(
        compiled.get("evidence_contract_consumed")
        or fec.get("fec_bridge_mode") == "section_fec_bridge"
        or fec_receipt.get("fec_bridge_mode") == "section_fec_bridge"
    )
    raw_pool_direct = bool(
        compiled.get("raw_proof_pool_direct_to_pa")
        or fec.get("raw_proof_pool_direct_to_pa")
        or fec_receipt.get("raw_proof_pool_direct_to_pa")
    )

    l2_refs_compiled_fec = (
        l2_pkt.get("compiled_prompt_artifact_ref") == "compiled_prompt_artifact.json"
        and bool(
            l2_pkt.get("route_contract_ref") == "route_contract.json"
            or compiled.get("fec_bridge_mode") == "section_fec_bridge"
        )
    )
    exit_refs_sealed = edr.get("sealed_l2_artifact_ref") == "sealed_l2_artifact.json"
    exhaust_refs_exit = exhaust.get("exit_disposition_receipt_ref") == "exit_disposition_receipt.json"
    l6_post_runtime_only = (
        l6_handoff.get("handoff_phase") == "post_runtime_exhaust_only"
        and l6_handoff.get("consumed_after_runtime_exhaust_bundle") is True
        and l6_handoff.get("consumed_after_exit_disposition") is True
        and l6_handoff.get("l6_can_change_exit_disposition") is False
    )
    if (artifact_dir / "l6_shadow_eval_package.json").is_file():
        l6_post_runtime_only = l6_post_runtime_only and (
            l6_pkg.get("offline_only") is True or str(l6_pkg.get("offline_only")).lower() == "true"
        )
    section_x3_mirror_only = (
        edr.get("section_x3_authoritative") is False
        or exhaust.get("section_x3_authoritative") is False
    )
    fixture_dev = pe.get("fixture_dev_only") is True or pc.get("fixture_dev_only") is True
    fixture_blocks_cert = fixture_dev or pc.get("product_certification") != "ONE_SPINE_SECTION_CERTIFIED"

    uwg_ran = any(
        (artifact_dir / n).is_file()
        for n in ("uwg_commit_receipt.json", "r1b_uwg_receipt.json")
    )
    durable_write_certified = bool(pc.get("durable_write_certified")) and uwg_ran

    checks = {
        "proof_pool_after_front_spine": proof_pool_after_front_spine,
        "pa_evidence_contract_consumed": pa_evidence_consumed,
        "raw_proof_pool_direct_to_pa": raw_pool_direct,
        "l2_refs_compiled_prompt_and_fec": l2_refs_compiled_fec,
        "exit_refs_sealed_l2": exit_refs_sealed,
        "exhaust_refs_exit_disposition": exhaust_refs_exit,
        "l6_post_runtime_only": l6_post_runtime_only,
        "section_x3_mirror_not_authoritative": section_x3_mirror_only,
        "required_chain_complete": bool(chain.get("required_chain_complete")),
        "certification_required_chain_complete": bool(cert.get("required_chain_complete")),
        "fixture_dev_only": fixture_dev,
        "fixture_dev_blocks_product_cert": fixture_blocks_cert if fixture_dev else True,
        "durable_write_certified": durable_write_certified,
        "full_apps_contract_suite_certified": bool(pc.get("full_apps_contract_suite_certified")),
    }
    no_two_path_preconditions_pass = all(
        [
            checks["proof_pool_after_front_spine"],
            checks["pa_evidence_contract_consumed"],
            not checks["raw_proof_pool_direct_to_pa"],
            checks["l2_refs_compiled_prompt_and_fec"],
            checks["exit_refs_sealed_l2"],
            checks["exhaust_refs_exit_disposition"],
            checks["l6_post_runtime_only"],
            checks["section_x3_mirror_not_authoritative"],
            checks["required_chain_complete"],
        ]
    )

    return {
        "no_two_path_preconditions_pass": no_two_path_preconditions_pass,
        "checks": checks,
        "chain": {
            "required_chain_complete": chain.get("required_chain_complete"),
            "all_required_artifacts_present": chain.get("all_required_artifacts_present"),
            "all_required_refs_valid": chain.get("all_required_refs_valid"),
        },
        "product_certification": pc.get("product_certification"),
        "proof_eligible": pe.get("proof_eligible"),
        "x3_code": pe.get("x3_code") or edr.get("x3_code"),
        "validated_request_contract": validated.get("contract_type"),
        "exit_section_x3_authoritative": edr.get("section_x3_authoritative"),
        "exhaust_canonical_exit_authority_ref": exhaust.get("canonical_exit_authority_ref"),
    }


__all__ = ["inspect_no_two_path_lane"]
