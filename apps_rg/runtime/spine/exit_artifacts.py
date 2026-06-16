"""One-spine section Exit receipts — SealedL2Artifact → ExitDispositionReceipt (Wave 6).

Section ``x3_disposition.json`` remains mirror/input only. Canonical exit authority is
``exit_disposition_receipt.json``. Not spine RuntimeExhaustBundle, product certification, or UWG.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from apps_rg.runtime.spine.front_contracts import fixture_dev_bypass_active
from apps_rg.runtime.section_l2_spine_receipt import (
    L2_EXECUTION_PACKET_ARTIFACT,
    SEALED_L2_ARTIFACT,
)
from apps_rg.runtime.disposition_authority import DISPOSITION_AUTHORITY_LANE
from apps_rg.runtime.section_spine_terminology import CANONICAL_SPINE_CHAIN

EXIT_REVIEW_PACKET_ARTIFACT = "exit_review_packet.json"
SECTION_EXIT_X1_RESULT_ARTIFACT = "section_exit_x1_result.json"
SECTION_EXIT_X2_RESULT_ARTIFACT = "section_exit_x2_result.json"
EXIT_DISPOSITION_RECEIPT_ARTIFACT = "exit_disposition_receipt.json"
EXIT_SPINE_RECEIPT_ARTIFACT = "exit_spine_receipt.json"

SECTION_X3_DISPOSITION_ARTIFACT = "x3_disposition.json"
X2_GATE_OUTPUTS_ARTIFACT = "x2_gate_outputs.json"
X1D_JUDGE_OUTPUTS_ARTIFACT = "x1d_llm_judge_outputs.json"
LANE_X3_MIRROR_AUTHORITY_SCOPE = "apps_rg_lane_x3_mirror_not_core_exit_authority"
APP_X2_QUALITY_AUTHORITY_SCOPE = "apps_rg_section_product_quality_not_core_exit_matrix"
CORE_EXIT_AUTHORITY_SCOPE = "agentic_core_exit_disposition_receipt"

OBSERVED_CHAIN_WITH_EXIT_RECEIPTS: tuple[str, ...] = (
    "CLI",
    "apps_rg_spine_run",
    "U0",
    "L1",
    "L0",
    "c0_retrieve_apps_rg",
    "pa_compose_apps_rg",
    "l2_execute_apps_rg",
    "ExitEvalPipeline",
    "exit_disposition_receipt",
    "section_L6_shadow",
)


class SectionExitSpinePreconditionError(RuntimeError):
    """Raised when product-visible Exit runs without SealedL2Artifact."""


def exit_spine_kill_switch_enabled() -> bool:
    return os.environ.get("APPS_RG_SECTION_EXIT_SPINE_KILL_SWITCH", "1").strip() not in (
        "0",
        "false",
        "no",
    )


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _artifact_exists(artifact_dir: Path, name: str) -> bool:
    return bool(name) and (artifact_dir / name).is_file()


def _load_json(artifact_dir: Path, name: str) -> dict[str, Any]:
    path = artifact_dir / name
    if not path.is_file():
        return {}
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
        return doc if isinstance(doc, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def assert_section_exit_spine_preconditions(
    runtime_payload: dict[str, Any],
    artifact_dir: Path,
    *,
    product_visible: bool | None = None,
    fixture_dev_only_bypass: bool = False,
    non_product_certified: bool = False,
) -> None:
    """Fail closed before Exit in product-visible mode."""
    if fixture_dev_only_bypass or fixture_dev_bypass_active():
        return
    if non_product_certified:
        return
    pv = product_visible if product_visible is not None else bool(
        runtime_payload.get("product_visible", True)
    )
    if not pv:
        return
    if not exit_spine_kill_switch_enabled():
        return

    sealed_ref = str(runtime_payload.get("sealed_l2_artifact_ref") or SEALED_L2_ARTIFACT)
    if not _artifact_exists(artifact_dir, sealed_ref):
        raise SectionExitSpinePreconditionError(
            f"product-visible section Exit requires {sealed_ref} before ExitReviewPacket"
        )
    if runtime_payload.get("exit_bypass_without_sealed_l2") is True:
        raise SectionExitSpinePreconditionError(
            "Exit without SealedL2Artifact is forbidden in product-visible mode"
        )


def build_exit_review_packet_for_section(
    *,
    section_id: str,
    runtime_payload: dict[str, Any],
    artifact_dir: Path,
) -> dict[str, Any]:
    """Apps_rg-local ExitReviewPacket binding SealedL2 + section X3 mirror."""
    sealed_ref = str(runtime_payload.get("sealed_l2_artifact_ref") or SEALED_L2_ARTIFACT)
    l2_packet_ref = str(runtime_payload.get("l2_execution_packet_ref") or L2_EXECUTION_PACKET_ARTIFACT)
    compiled_ref = str(runtime_payload.get("compiled_prompt_artifact_ref") or "compiled_prompt_artifact.json")
    fec_ref = str(
        runtime_payload.get("fec_bridge_ref")
        or runtime_payload.get("final_evidence_contract_ref")
        or "final_evidence_contract.json"
        or "final_evidence_contract_bridge.json"
    )
    section_x3 = _load_json(artifact_dir, SECTION_X3_DISPOSITION_ARTIFACT)
    return {
        "schema_version": "section_exit_review_packet_v1",
        "generated_at_utc": _utc_now(),
        "contract_type": "ExitReviewPacket",
        "producer_stage": "L2",
        "consumer_stage": "Exit",
        "section_id": section_id,
        "run_id": str(runtime_payload.get("run_id") or ""),
        "sealed_l2_artifact_ref": sealed_ref,
        "l2_execution_packet_ref": l2_packet_ref,
        "compiled_prompt_artifact_ref": compiled_ref,
        "fec_bridge_ref": fec_ref,
        "section_x3_disposition_ref": SECTION_X3_DISPOSITION_ARTIFACT,
        "section_x3_authority_scope": LANE_X3_MIRROR_AUTHORITY_SCOPE,
        "section_x3_authoritative": False,
        "section_x3_mirror_only": True,
        "disposition_authority": DISPOSITION_AUTHORITY_LANE,
        "spine_x3_claimed": False,
        "x3_disposition_snapshot": dict(section_x3) if section_x3 else {},
        "direct_l4_write_allowed": False,
        "canonical_exit_claimed": False,
        "product_certification": "NOT_CLAIMED",
        "explicit_non_claims": [
            "section x3_disposition.json is input mirror only until ExitDispositionReceipt",
            "not RuntimeExhaustBundle",
        ],
    }


def build_section_exit_x1_result(
    *,
    section_id: str,
    artifact_dir: Path,
) -> dict[str, Any]:
    """Section-adapted X1 checkout rollup from lane X1D artifacts."""
    x1d_doc = _load_json(artifact_dir, X1D_JUDGE_OUTPUTS_ARTIFACT)
    judges = x1d_doc.get("judges") if isinstance(x1d_doc.get("judges"), list) else []
    if not judges and isinstance(x1d_doc.get("judge_results"), list):
        judges = x1d_doc["judge_results"]
    blocked = [j for j in judges if isinstance(j, dict) and j.get("provider_blocked")]
    mocked = [j for j in judges if isinstance(j, dict) and j.get("evaluator_mode") == "MOCKED"]
    return {
        "schema_version": "section_exit_x1_result_v1",
        "generated_at_utc": _utc_now(),
        "contract_type": "X1CheckoutResult",
        "section_id": section_id,
        "adaptation": "section_lane_mirror",
        "authority_scope": "apps_rg_x1d_judge_preflight_not_core_x1_gate",
        "x1d_judge_outputs_ref": X1D_JUDGE_OUTPUTS_ARTIFACT if _artifact_exists(artifact_dir, X1D_JUDGE_OUTPUTS_ARTIFACT) else None,
        "judge_count": len(judges),
        "blocked_judge_count": len(blocked),
        "mocked_judge_count": len(mocked),
        "checkout_status": "PASS" if judges and not blocked else ("PARTIAL" if judges else "UNKNOWN"),
        "product_certification": "NOT_CLAIMED",
    }


def build_section_exit_x2_result(
    *,
    section_id: str,
    artifact_dir: Path,
) -> dict[str, Any]:
    """Section-adapted X2 aggregation from lane x2_gate_outputs.json."""
    path = artifact_dir / X2_GATE_OUTPUTS_ARTIFACT
    gates: list[dict[str, Any]] = []
    if path.is_file():
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(raw, list):
                gates = [g for g in raw if isinstance(g, dict)]
            elif isinstance(raw, dict) and isinstance(raw.get("gates"), list):
                gates = [g for g in raw["gates"] if isinstance(g, dict)]
        except (json.JSONDecodeError, OSError):
            gates = []
    failed = [str(g.get("gate_id") or g.get("id") or "") for g in gates if g.get("pass") is False]
    return {
        "schema_version": "section_exit_x2_result_v1",
        "generated_at_utc": _utc_now(),
        "contract_type": "X2AggregationResult",
        "section_id": section_id,
        "adaptation": "section_lane_mirror",
        "authority_scope": APP_X2_QUALITY_AUTHORITY_SCOPE,
        "core_x2_matrix_authority": False,
        "x2_gate_outputs_ref": X2_GATE_OUTPUTS_ARTIFACT if path.is_file() else None,
        "gate_count": len(gates),
        "failed_gate_ids": [f for f in failed if f],
        "aggregation_status": "PASS" if gates and not failed else ("FAIL" if failed else "UNKNOWN"),
        "product_certification": "NOT_CLAIMED",
    }


def build_exit_disposition_receipt_for_section(
    *,
    section_id: str,
    runtime_payload: dict[str, Any],
    artifact_dir: Path,
    exit_review_packet_ref: str = EXIT_REVIEW_PACKET_ARTIFACT,
) -> dict[str, Any]:
    """Canonical section-lane ExitDispositionReceipt — exactly one x3_disposition."""
    section_x3 = _load_json(artifact_dir, SECTION_X3_DISPOSITION_ARTIFACT)
    if not section_x3:
        section_x3 = {"x3_code": "UNKNOWN", "decisive_reason": "missing section x3 mirror"}
    x3_single = dict(section_x3)
    sealed_ref = str(runtime_payload.get("sealed_l2_artifact_ref") or SEALED_L2_ARTIFACT)
    return {
        "schema_version": "section_exit_disposition_receipt_v1",
        "generated_at_utc": _utc_now(),
        "contract_type": "ExitDispositionReceipt",
        "producer_stage": "Exit",
        "consumer_stage": "optional_UWG",
        "section_id": section_id,
        "run_id": str(runtime_payload.get("run_id") or ""),
        "exit_review_packet_ref": exit_review_packet_ref,
        "sealed_l2_artifact_ref": sealed_ref,
        "l2_execution_packet_ref": str(
            runtime_payload.get("l2_execution_packet_ref") or L2_EXECUTION_PACKET_ARTIFACT
        ),
        "section_x3_disposition_ref": SECTION_X3_DISPOSITION_ARTIFACT,
        "section_x3_authority_scope": LANE_X3_MIRROR_AUTHORITY_SCOPE,
        "section_x3_authoritative": False,
        "section_x3_mirror_only": True,
        "disposition_authority": DISPOSITION_AUTHORITY_LANE,
        "spine_x3_claimed": False,
        "x3_disposition": x3_single,
        "x3_code": str(x3_single.get("x3_code") or "UNKNOWN"),
        "canonical_exit_claimed": True,
        "canonical_exit_authority": "exit_disposition_receipt",
        "canonical_exit_authority_scope": CORE_EXIT_AUTHORITY_SCOPE,
        "durable_commit_occurred": False,
        "uwg_commit_occurred": False,
        "runtime_exhaust_bundle_claimed": False,
        "product_certification": "NOT_CLAIMED",
        "explicit_non_claims": [
            "not product certification or release signoff",
            "not spine RuntimeExhaustBundle",
            "no durable L4 write unless uwg_commit_occurred is true",
        ],
    }


def build_exit_spine_receipt(
    *,
    section_id: str,
    runtime_payload: dict[str, Any],
    artifact_dir: Path,
) -> dict[str, Any]:
    """Master receipt for section Exit spine alignment."""
    fixture_dev = bool(fixture_dev_bypass_active())
    sealed_ref = str(runtime_payload.get("sealed_l2_artifact_ref") or SEALED_L2_ARTIFACT)
    precond_ok = _artifact_exists(artifact_dir, sealed_ref) and _artifact_exists(
        artifact_dir, EXIT_DISPOSITION_RECEIPT_ARTIFACT
    )
    exit_doc = _load_json(artifact_dir, EXIT_DISPOSITION_RECEIPT_ARTIFACT)
    return {
        "schema_version": "exit_spine_receipt_v1",
        "generated_at_utc": _utc_now(),
        "plan_slug": "one-canonical-spine",
        "wave": "6",
        "lane": section_id,
        "section_id": section_id,
        "run_id": str(runtime_payload.get("run_id") or ""),
        "product_visible": bool(runtime_payload.get("product_visible", True)),
        "fixture_dev_only": fixture_dev,
        "non_product_certified": fixture_dev,
        "spine_mode": "section_lane_modular",
        "exit_alignment_mode": "section_exit_spine_receipt",
        "exit_spine_status": "PASS" if precond_ok else "FAIL",
        "exit_review_packet_ref": EXIT_REVIEW_PACKET_ARTIFACT,
        "section_exit_x1_result_ref": SECTION_EXIT_X1_RESULT_ARTIFACT,
        "section_exit_x2_result_ref": SECTION_EXIT_X2_RESULT_ARTIFACT,
        "exit_disposition_receipt_ref": EXIT_DISPOSITION_RECEIPT_ARTIFACT,
        "sealed_l2_artifact_ref": sealed_ref,
        "section_x3_disposition_ref": SECTION_X3_DISPOSITION_ARTIFACT,
        "section_x3_authority_scope": LANE_X3_MIRROR_AUTHORITY_SCOPE,
        "section_x3_authoritative": False,
        "canonical_exit_authority_ref": EXIT_DISPOSITION_RECEIPT_ARTIFACT,
        "canonical_exit_authority_scope": CORE_EXIT_AUTHORITY_SCOPE,
        "canonical_exit_claimed_on_exit_receipt": bool(exit_doc.get("canonical_exit_claimed")),
        "canonical_exit_claimed_on_sealed_l2": False,
        "durable_commit_occurred": False,
        "runtime_exhaust_bundle_claimed": False,
        "product_certification": "NOT_CLAIMED",
        "exit_spine_kill_switch_enabled": exit_spine_kill_switch_enabled(),
        "observed_chain": list(OBSERVED_CHAIN_WITH_EXIT_RECEIPTS),
        "canonical_spine_target": list(CANONICAL_SPINE_CHAIN),
        "explicit_non_claims": [
            "not product certification",
            "not RuntimeExhaustBundle",
            "not durable write / UWG",
        ],
    }


def emit_section_exit_spine_artifacts(
    artifact_dir: Path,
    *,
    section_id: str,
    runtime_payload: dict[str, Any],
) -> dict[str, Path]:
    """Write all Wave 6 Exit artifacts after SealedL2Artifact exists."""
    artifact_dir.mkdir(parents=True, exist_ok=True)
    assert_section_exit_spine_preconditions(runtime_payload, artifact_dir)

    erp = build_exit_review_packet_for_section(
        section_id=section_id,
        runtime_payload=runtime_payload,
        artifact_dir=artifact_dir,
    )
    p_erp = artifact_dir / EXIT_REVIEW_PACKET_ARTIFACT
    p_erp.write_text(json.dumps(erp, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    x1 = build_section_exit_x1_result(section_id=section_id, artifact_dir=artifact_dir)
    p_x1 = artifact_dir / SECTION_EXIT_X1_RESULT_ARTIFACT
    p_x1.write_text(json.dumps(x1, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    x2 = build_section_exit_x2_result(section_id=section_id, artifact_dir=artifact_dir)
    p_x2 = artifact_dir / SECTION_EXIT_X2_RESULT_ARTIFACT
    p_x2.write_text(json.dumps(x2, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    edr = build_exit_disposition_receipt_for_section(
        section_id=section_id,
        runtime_payload=runtime_payload,
        artifact_dir=artifact_dir,
    )
    p_edr = artifact_dir / EXIT_DISPOSITION_RECEIPT_ARTIFACT
    p_edr.write_text(json.dumps(edr, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    receipt = build_exit_spine_receipt(
        section_id=section_id,
        runtime_payload=runtime_payload,
        artifact_dir=artifact_dir,
    )
    p_receipt = artifact_dir / EXIT_SPINE_RECEIPT_ARTIFACT
    p_receipt.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    runtime_payload["exit_review_packet_ref"] = EXIT_REVIEW_PACKET_ARTIFACT
    runtime_payload["exit_disposition_receipt_ref"] = EXIT_DISPOSITION_RECEIPT_ARTIFACT
    runtime_payload["exit_spine_receipt_ref"] = EXIT_SPINE_RECEIPT_ARTIFACT
    runtime_payload["canonical_exit_authority_ref"] = EXIT_DISPOSITION_RECEIPT_ARTIFACT
    runtime_payload["canonical_exit_authority_scope"] = CORE_EXIT_AUTHORITY_SCOPE
    runtime_payload["section_x3_authoritative"] = False
    runtime_payload["section_x3_authority_scope"] = LANE_X3_MIRROR_AUTHORITY_SCOPE

    return {
        "exit_review_packet": p_erp,
        "section_exit_x1_result": p_x1,
        "section_exit_x2_result": p_x2,
        "exit_disposition_receipt": p_edr,
        "exit_spine_receipt": p_receipt,
    }


__all__ = [
    "EXIT_DISPOSITION_RECEIPT_ARTIFACT",
    "APP_X2_QUALITY_AUTHORITY_SCOPE",
    "CORE_EXIT_AUTHORITY_SCOPE",
    "EXIT_REVIEW_PACKET_ARTIFACT",
    "EXIT_SPINE_RECEIPT_ARTIFACT",
    "OBSERVED_CHAIN_WITH_EXIT_RECEIPTS",
    "SECTION_EXIT_X1_RESULT_ARTIFACT",
    "SECTION_EXIT_X2_RESULT_ARTIFACT",
    "LANE_X3_MIRROR_AUTHORITY_SCOPE",
    "SectionExitSpinePreconditionError",
    "assert_section_exit_spine_preconditions",
    "build_exit_disposition_receipt_for_section",
    "build_exit_review_packet_for_section",
    "build_exit_spine_receipt",
    "build_section_exit_x1_result",
    "build_section_exit_x2_result",
    "emit_section_exit_spine_artifacts",
    "exit_spine_kill_switch_enabled",
]
