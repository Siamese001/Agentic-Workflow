"""Validate L6 shadow handoff packets for resume package signoff."""

from __future__ import annotations

from typing import Any, Mapping

from apps_rg.runtime.shadow.l6_handoff_packet import (
    BULLET_LANE_IDS,
    IBM_POOL_SELECTION_POLICY_ID,
    L6_PACKET_TYPE,
    L6_PACKET_VERSION,
    UNIFY_POOL_SELECTION_POLICY_ID,
)


TOP_REQUIRED_SCALAR = frozenset(
    {
        "packet_type",
        "packet_version",
        "section_id",
        "run_id",
        "runtime_generation_status",
        "generated_at_utc",
        "section_output_ref",
        "x1d_judge_outputs_ref",
        "x2_gate_outputs_ref",
        "x3_disposition_ref",
        "final_resume_assembly_ref",
        "docx_render_ref",
        "human_label_required",
        "human_label_status",
        "human_label_ref",
        "benchmark_set_id",
        "calibration_status",
        "calibration_report_ref",
        "recommendation_packet_ref",
        "promotion_allowed",
        "learning_mutation_performed",
        "runtime_approval_authority",
        "current_run_mutation_allowed",
        "prompt_mutation_performed",
        "gate_mutation_performed",
        "judge_mutation_performed",
        "threshold_mutation_performed",
        "generator_metadata",
        "x2_summary",
        "x1d_summary",
        "x3_summary",
    }
)


def _nested_missing(pkt: Mapping[str, Any]) -> list[str]:
    missing: list[str] = []
    absent_scalar = TOP_REQUIRED_SCALAR - set(pkt.keys())
    missing.extend(sorted(absent_scalar))

    gm = pkt.get("generator_metadata")
    if not isinstance(gm, dict):
        if "generator_metadata" not in absent_scalar:
            missing.append("generator_metadata_shape")
    else:
        for k in (
            "generator_provider",
            "generator_model",
            "prompt_id",
            "prompt_hash",
            "temperature",
            "max_tokens",
            "provider_request_ref",
            "provider_response_ref",
        ):
            if k not in gm:
                missing.append(f"generator_metadata.{k}")

    x2s = pkt.get("x2_summary")
    if not isinstance(x2s, dict):
        if "x2_summary" not in absent_scalar:
            missing.append("x2_summary_shape")
    else:
        for k in ("x2_total", "x2_passed", "x2_failed", "failed_gate_ids"):
            if k not in x2s:
                missing.append(f"x2_summary.{k}")

    x1s = pkt.get("x1d_summary")
    if not isinstance(x1s, dict):
        if "x1d_summary" not in absent_scalar:
            missing.append("x1d_summary_shape")
    else:
        for k in (
            "judge_provider_statuses",
            "judge_scores",
            "judge_thresholds",
            "normalized_scores",
            "normalized_thresholds",
            "decisive_failures",
            "soft_failed_judges",
            "blocked_judges",
            "mocked_judges",
        ):
            if k not in x1s:
                missing.append(f"x1d_summary.{k}")

    x3s = pkt.get("x3_summary")
    if not isinstance(x3s, dict):
        if "x3_summary" not in absent_scalar:
            missing.append("x3_summary_shape")
    else:
        for k in ("x3_code", "authorization_scope", "proceed_to_runtime", "pass", "decisive_reason"):
            if k not in x3s:
                missing.append(f"x3_summary.{k}")

    # review_reason optional inside x3_summary
    return sorted(set(missing))


def _truthy_checks(pkt: Mapping[str, Any]) -> tuple[dict[str, bool], bool]:
    out: dict[str, bool] = {}
    fatal = False

    hl_ok = pkt.get("human_label_status") == "MISSING"
    out["x3_l6_human_label_status_valid"] = hl_ok

    cal_ok = pkt.get("calibration_status") == "NOT_CALIBRATED"
    out["x3_l6_calibration_status_valid"] = cal_ok

    hlr_req = pkt.get("human_label_required") is True
    out["x3_l6_human_label_required_true"] = hlr_req
    fatal |= not hlr_req

    out["x3_l6_benchmark_set_id_null"] = pkt.get("benchmark_set_id") is None
    out["x3_l6_recommendation_packet_ref_null"] = pkt.get("recommendation_packet_ref") is None

    rauth = pkt.get("runtime_approval_authority")
    auth_ok = rauth == "NONE"
    out["x3_l6_no_runtime_approval_authority"] = auth_ok
    fatal |= not auth_ok

    promo_ok = pkt.get("promotion_allowed") is False
    out["x3_l6_promotion_not_allowed"] = promo_ok
    fatal |= not promo_ok

    learn_ok = pkt.get("learning_mutation_performed") is False
    out["x3_l6_no_learning_mutation"] = learn_ok
    fatal |= not learn_ok

    cr_ok = pkt.get("current_run_mutation_allowed") is False
    out["x3_l6_current_run_no_mutation"] = cr_ok
    fatal |= not cr_ok

    pm_ok = pkt.get("prompt_mutation_performed") is False
    gm_ok = pkt.get("gate_mutation_performed") is False
    jm_ok = pkt.get("judge_mutation_performed") is False
    tm_ok = pkt.get("threshold_mutation_performed") is False
    out["x3_l6_no_mutation_flags"] = pm_ok and gm_ok and jm_ok and tm_ok and cr_ok
    fatal |= not (pm_ok and gm_ok and jm_ok and tm_ok)

    return out, fatal


def _bullet_audit(lane_key: str, pkt: Mapping[str, Any]) -> tuple[dict[str, bool], bool]:
    incomplete = False
    out: dict[str, bool] = {}
    brm = pkt.get("bullet_evidence_map") or pkt.get("bullet_rewrite_map")
    bullet_meta_ok = (
        pkt.get("selection_policy_id") is not None
        and isinstance(brm, list)
        and len(brm) > 0
    )

    if lane_key == "unify_bullets":
        pol_ok = pkt.get("selection_policy_id") == UNIFY_POOL_SELECTION_POLICY_ID
        if not pol_ok:
            incomplete = True
        out["x3_l6_unify_pool_selection_policy"] = pol_ok
        if not pol_ok:
            incomplete = True

        unify_prot = False
        if isinstance(brm, list):
            for row in brm:
                if isinstance(row, dict) and str(row.get("bullet_id")) == "bul_unify_006":
                    unify_prot = bool(row.get("metrics_preserved") is True)
                    break
        out["x3_l6_unify_protects_bul_unify_006"] = unify_prot
        if not unify_prot:
            incomplete = True

    elif lane_key == "ibm_bullets":
        pol_ok = pkt.get("selection_policy_id") == IBM_POOL_SELECTION_POLICY_ID
        if not pol_ok:
            incomplete = True
        out["x3_l6_ibm_pool_selection_policy"] = pol_ok
        if not pol_ok:
            incomplete = True

    if lane_key in BULLET_LANE_IDS and not bullet_meta_ok:
        incomplete = True

    if lane_key not in BULLET_LANE_IDS:
        out["x3_l6_bullet_rewrite_metadata_present_for_bullet_lanes"] = True
    else:
        out["x3_l6_bullet_rewrite_metadata_present_for_bullet_lanes"] = bullet_meta_ok and not incomplete

    return out, incomplete


def audit_l6_shadow_packet_for_lane(*, lane_key: str, packet: Mapping[str, Any] | None) -> dict[str, Any]:
    pkt = packet if isinstance(packet, dict) else {}
    nm = _nested_missing(pkt)

    type_ok = pkt.get("packet_type") == L6_PACKET_TYPE
    ver_ok = pkt.get("packet_version") == L6_PACKET_VERSION

    truth_checks, fatal_truth = _truthy_checks(pkt)
    bullet_checks, bullet_incomplete = _bullet_audit(lane_key, pkt)

    gm = pkt.get("generator_metadata")
    x2s = pkt.get("x2_summary")
    x1s = pkt.get("x1d_summary")
    x3s = pkt.get("x3_summary")

    semantic_ok = len(nm) == 0
    checks: dict[str, bool] = {
        "x3_l6_shadow_packets_present": bool(pkt),
        "x3_l6_shadow_refs_complete": semantic_ok,
        "x3_l6_packet_type_version": type_ok and ver_ok,
        "x3_l6_generator_metadata_present": isinstance(gm, dict),
        "x3_l6_x2_summary_present": isinstance(x2s, dict),
        "x3_l6_x1d_summary_present": isinstance(x1s, dict),
        "x3_l6_x3_summary_present": isinstance(x3s, dict),
        **truth_checks,
        **bullet_checks,
    }

    fatal = not checks["x3_l6_shadow_packets_present"] or not semantic_ok or not type_ok or not ver_ok
    fatal |= fatal_truth
    fatal |= bullet_incomplete and lane_key in BULLET_LANE_IDS

    checks["x3_l6_shadow_packets_hard_pass"] = not fatal

    return {
        "lane_key": lane_key,
        "checks": checks,
        "fatal": fatal,
        "incomplete_field_paths_sorted": nm,
        "truth_violations_present": fatal_truth,
        "bullet_lane_incomplete": bullet_incomplete and lane_key in BULLET_LANE_IDS,
    }


__all__ = ["audit_l6_shadow_packet_for_lane", "TOP_REQUIRED_SCALAR"]
