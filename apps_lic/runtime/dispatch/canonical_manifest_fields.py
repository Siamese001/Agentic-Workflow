"""Manifest field shapers for the canonical apps_lic spine."""

from __future__ import annotations

from typing import Any


def w4_manifest_fields(w4: Any | None) -> dict[str, Any]:
    if w4 is None:
        return {
            "w4_candidate_invoked": False,
            "w4_candidate_status": "",
            "w4_expected_candidate_count": 0,
            "w4_candidate_count_materialized": 0,
            "w4_selected_candidate_id": "",
            "w4_rejected_candidate_ids": [],
            "w4_blocking_reasons": [],
            "w4_proof_packet_id": "",
            "w4_model_call_refs": [],
            "w4_provider_receipts": [],
        }
    return {
        "w4_candidate_invoked": True,
        "w4_candidate_status": w4.status,
        "w4_expected_candidate_count": w4.expected_candidate_count,
        "w4_candidate_count_materialized": w4.candidate_count_materialized,
        "w4_selected_candidate_id": w4.selected_candidate_id,
        "w4_rejected_candidate_ids": list(w4.rejected_candidate_ids),
        "w4_blocking_reasons": list(w4.blocking_reasons),
        "w4_proof_packet_id": w4.proof_packet_id,
        "w4_model_call_refs": list(w4.model_call_refs),
        "w4_provider_receipts": list(w4.provider_receipts),
    }


def w5_manifest_fields(w5: Any | None) -> dict[str, Any]:
    if w5 is None:
        return {
            "w5_validation_exit_invoked": False,
            "w5_validation_exit_status": "",
            "w5_validation_exit_disposition": "",
            "w5_exit_reason": "",
            "w5_review_required_reason": "",
            "w5_final_user_visible_draft_id": "",
            "w5_proof_packet_id": "",
            "w5_prompt_contract_id": "",
            "w5_no_send_receipt": "",
            "w5_no_durable_write_receipt": "",
            "w5_x2_status": "",
            "w5_x2_failed_gate_ids": [],
            "w5_x2_reason_codes": [],
            "w5_x1d_status": "",
            "w5_x1d_required_depth": "",
            "w5_x1d_required_judge_ids": [],
            "w5_x1d_missing_judge_ids": [],
            "w5_x1d_reason_codes": [],
            "w5_x1d_judge_result_count": 0,
            "w5_x1d_regeneration_attempted": False,
            "w5_x1d_regeneration_iteration_count": 0,
            "w5_x1d_regeneration_stop_reason": "",
            "w5_x1d_repair_effective": False,
            "w5_x1d_repair_resolved_issue_ids": [],
            "w5_x1d_repair_unresolved_issue_ids": [],
            "w5_repair_candidate_sanitization_passed": False,
        }
    proof = w5.exit_proof_bundle
    regeneration_packet = w5.x1d_regeneration.to_packet() if w5.x1d_regeneration else {}
    return {
        "w5_validation_exit_invoked": True,
        "w5_validation_exit_status": proof.status,
        "w5_validation_exit_disposition": proof.disposition,
        "w5_exit_reason": proof.exit_reason,
        "w5_review_required_reason": proof.review_required_reason,
        "w5_final_user_visible_draft_id": proof.final_user_visible_draft_id,
        "w5_proof_packet_id": proof.proof_packet_id,
        "w5_prompt_contract_id": proof.prompt_contract_id,
        "w5_no_send_receipt": proof.no_send_receipt,
        "w5_no_durable_write_receipt": w5.request.no_durable_write_receipt,
        "w5_x2_status": proof.x2_result.status,
        "w5_x2_failed_gate_ids": list(proof.x2_result.failed_gate_ids),
        "w5_x2_reason_codes": list(proof.x2_result.reason_codes),
        "w5_x1d_status": proof.x1d_result.status,
        "w5_x1d_required_depth": proof.x1d_result.required_depth,
        "w5_x1d_required_judge_ids": [
            profile.judge_id for profile in proof.x1d_result.required_profiles
        ],
        "w5_x1d_missing_judge_ids": list(proof.x1d_result.missing_judge_ids),
        "w5_x1d_reason_codes": list(proof.x1d_result.reason_codes),
        "w5_x1d_judge_result_count": len(proof.x1d_result.judge_results),
        "w5_x1d_regeneration_attempted": bool(
            w5.x1d_regeneration and w5.x1d_regeneration.attempted
        ),
        "w5_x1d_regeneration_iteration_count": (
            w5.x1d_regeneration.iteration_count if w5.x1d_regeneration else 0
        ),
        "w5_x1d_regeneration_stop_reason": (
            w5.x1d_regeneration.stop_reason if w5.x1d_regeneration else ""
        ),
        "w5_x1d_repair_effective": bool(
            regeneration_packet.get("x1d_repair_effective", False)
        ),
        "w5_x1d_repair_resolved_issue_ids": list(
            regeneration_packet.get("x1d_repair_resolved_issue_ids", [])
        ),
        "w5_x1d_repair_unresolved_issue_ids": list(
            regeneration_packet.get("x1d_repair_unresolved_issue_ids", [])
        ),
        "w5_repair_candidate_sanitization_passed": bool(
            regeneration_packet.get("repair_candidate_sanitization_passed", False)
        ),
    }
