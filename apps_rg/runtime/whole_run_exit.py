"""Whole-run Exit aggregation for apps_rg section-dispatch runtime proof.

Computes a single disposition (X3D_*/X3B_*/X3_BLOCK/X3E_*) from lane rollups, assembly
gates, C0/FEC grounding signals, and X1D policy. Per-lane X3 codes are preserved as evidence
in ``aggregated_from_lane_x3``; they are not overwritten.

This module is apps_rg-local and does not import agentic_core.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

X3D_ALLOW_FINISH = "X3D_ALLOW_FINISH"
X3B_REVIEW = "X3B_REVIEW"
X3_BLOCK = "X3_BLOCK"
X3E_SAFE_ABSTAIN = "X3E_SAFE_ABSTAIN"

RC_JUDGE_PROVIDER_UNAVAILABLE = "JUDGE_PROVIDER_UNAVAILABLE"
RC_JUDGE_QUORUM_NOT_SATISFIED = "JUDGE_QUORUM_NOT_SATISFIED"
RC_JUDGE_EXECUTION_PROVIDER_MISMATCH = "JUDGE_EXECUTION_PROVIDER_MISMATCH"
RC_JUDGE_MODEL_BACKED_QUALITY_FAIL = "JUDGE_MODEL_BACKED_QUALITY_FAIL"
RC_JUDGE_UNKNOWN_RESULT = "JUDGE_UNKNOWN_RESULT"
RC_JUDGE_SCHEMA_OR_PARSER_BLOCK = "JUDGE_SCHEMA_OR_PARSER_BLOCK"
RC_X1D_POLICY_MALFORMED = "X1D_POLICY_MALFORMED"
RC_LANE_X3_MIXED = "LANE_X3_MIXED"
RC_LANE_X3_NON_ALLOW = "LANE_X3_NON_ALLOW"
RC_FINAL_RESUME_X2_FAIL = "FINAL_RESUME_X2_FAIL"
RC_C0_SUPPORT_WEAK = "C0_SUPPORT_WEAK"
RC_PRODUCT_R4_BYPASS_PRELOADED_CONTEXT = "PRODUCT_R4_BYPASS_PRELOADED_CONTEXT"
RC_X1D_AGGREGATE_REVIEW = "X1D_AGGREGATE_REVIEW"


def empty_whole_run_exit_shell() -> dict[str, Any]:
    return {
        "exit_review_packet_ref": "",
        "x1_result_ref": "",
        "x2_result_ref": "",
        "x3_disposition": "",
        "exactly_one_x3": True,
        "aggregated_from_lane_x3": [],
        "blockers": [],
        "warnings": [],
        "unknowns": [],
        "review_reasons": [],
        "block_reasons": [],
        "judge_reasons": [],
        "lane_x3_reasons": [],
        "decisive_reason": "",
    }


def _lower_list(xs: Any) -> list[str]:
    if not isinstance(xs, list):
        return []
    return [str(x) for x in xs]


def _lane_x2_failures_are_judge_only(row: Mapping[str, Any]) -> bool:
    xf = int(row.get("x2_failed") or 0)
    if xf <= 0:
        return True
    fg = _lower_list(row.get("x2_failed_gate_ids")) or _lower_list(row.get("x2_artifact_failed_gates"))
    if not fg:
        return False
    for g in fg:
        gl = g.lower()
        if "x1d" in gl or "judge" in gl:
            continue
        return False
    return True


def _unknown_dominates_section_gates(overall: str) -> bool:
    o = str(overall or "").strip().upper()
    return o in {"", "UNKNOWN"}


def write_exit_review_packet(
    repo_root: Path,
    payload: Mapping[str, Any],
    *,
    filename: str = "apps_rg_whole_run_exit_review_packet.json",
) -> Path:
    out = repo_root / "artifacts" / "ci" / filename
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(dict(payload), indent=2), encoding="utf-8")
    return out


def compute_whole_run_exit(signals: Mapping[str, Any]) -> dict[str, Any]:
    out = empty_whole_run_exit_shell()
    blockers: list[str] = []
    warnings: list[str] = []
    unknowns: list[str] = []
    review_rc: list[str] = []
    block_rc: list[str] = []
    judge_rc: list[str] = []
    lane_x3_rc: list[str] = []

    final_ok = bool(signals.get("final_resume_exists"))
    json_ok = bool(signals.get("final_resume_json_valid"))
    req = bool(signals.get("required_generated_sections_present"))
    locked = bool(signals.get("locked_sections_preserved"))
    xa2 = signals.get("final_resume_x2_all_pass")
    cross = bool(signals.get("cross_app_leakage"))
    mockp = bool(signals.get("mock_provider_pass"))
    l4bypass = bool(signals.get("direct_l4_write_bypass"))
    ground = bool(signals.get("grounding_required"))
    c0_count = int(signals.get("c0_evidence_item_count") or 0)
    c0_support = str(signals.get("c0_support_status") or "").strip().upper()
    pa_c = bool(signals.get("pa_consumed_c0"))
    pa_d = bool(signals.get("pa_evidence_data_only"))
    pa_s = bool(signals.get("pa_schema_bound"))
    x1d = str(signals.get("x1d_overall") or "").strip().upper()
    x2_unknown_lane = bool(signals.get("x2_unknown_lane"))
    lanes: list[dict[str, Any]] = list(signals.get("lane_rows") or [])
    policy_valid = bool(signals.get("x1d_policy_valid", True))
    quorum_sat = bool(signals.get("judge_quorum_satisfied", True))
    product_r4_note = bool(signals.get("product_r4_bypass_documented", False))

    if product_r4_note:
        review_rc.append(RC_PRODUCT_R4_BYPASS_PRELOADED_CONTEXT)
    if c0_support == "WEAK":
        review_rc.append(RC_C0_SUPPORT_WEAK)

    out["aggregated_from_lane_x3"] = [
        {"lane": str(r.get("lane") or ""), "x3_code": str(r.get("x3_code") or "")} for r in lanes
    ]

    if not policy_valid:
        out["x3_disposition"] = X3_BLOCK
        block_rc.append(RC_X1D_POLICY_MALFORMED)
        decisive_reason = "X1D_POLICY_MALFORMED: invalid APPS_RG_E2E_X1D_JUDGES configuration"
        out["blockers"] = [decisive_reason]
        out["warnings"] = warnings
        out["unknowns"] = unknowns
        out["review_reasons"] = review_rc
        out["block_reasons"] = block_rc
        out["judge_reasons"] = judge_rc
        out["lane_x3_reasons"] = lane_x3_rc
        out["decisive_reason"] = decisive_reason
        out["exactly_one_x3"] = True
        return out

    if not quorum_sat:
        judge_rc.append(RC_JUDGE_QUORUM_NOT_SATISFIED)
        judge_rc.append(RC_JUDGE_PROVIDER_UNAVAILABLE)

    if not final_ok:
        blockers.append("final_resume.json missing")
    if not json_ok:
        blockers.append("final_resume.json invalid or unreadable")
    if not req:
        blockers.append("one or more required generated lane sections missing from final_resume")
    if not locked:
        blockers.append("locked deterministic sections missing from final_resume")
    if xa2 is False:
        blockers.append("final_resume_x2 deterministic gates not all_pass")
        block_rc.append(RC_FINAL_RESUME_X2_FAIL)
    if xa2 is None and not blockers:
        unknowns.append("final_resume_x2_all_pass unknown — could not read gate artifact")
    if ground and c0_count <= 0:
        blockers.append("grounding_required but C0/FEC produced zero grounded chroma evidence items")

    for row in lanes:
        lk = str(row.get("lane") or "")
        xf = int(row.get("x2_failed") or 0)
        if xf > 0 and not _lane_x2_failures_are_judge_only(row):
            blockers.append(f"lane {lk}: deterministic X2 failures outside judge gates")

    if cross:
        blockers.append("cross_app_leakage true on C0 verification")
    if mockp:
        blockers.append("mock provider or MOCKED runtime treated as pass-path")
    if l4bypass:
        blockers.append("direct_l4_write_bypass true")

    if x2_unknown_lane:
        unknowns.append("rollup reported zero X2 gates for at least one lane")
    sg_overall = str(signals.get("section_gates_overall") or "")
    if _unknown_dominates_section_gates(sg_overall):
        unknowns.append("section_gates overall UNKNOWN")

    structural_blocked = bool(blockers)

    decisive_reason = ""

    if structural_blocked:
        out["x3_disposition"] = X3_BLOCK
        decisive_reason = "STRUCTURAL_BLOCK: " + "; ".join(blockers[:12])
        out["blockers"] = blockers
        out["warnings"] = warnings
        out["unknowns"] = unknowns
        out["review_reasons"] = review_rc
        out["block_reasons"] = block_rc
        out["judge_reasons"] = judge_rc
        out["lane_x3_reasons"] = lane_x3_rc
        out["decisive_reason"] = decisive_reason
        out["exactly_one_x3"] = True
        return out

    if xa2 is None:
        out["x3_disposition"] = X3E_SAFE_ABSTAIN
        block_rc.append(RC_FINAL_RESUME_X2_FAIL)
        decisive_reason = "SAFE_ABSTAIN: final_resume_x2 gate artifact missing or unreadable"
        out["blockers"] = blockers
        out["warnings"] = warnings + ["do not treat UNKNOWN as runtime PASS"]
        out["unknowns"] = unknowns or ["final_resume_x2_all_pass unknown"]
        out["review_reasons"] = review_rc
        out["block_reasons"] = block_rc
        out["judge_reasons"] = judge_rc
        out["lane_x3_reasons"] = lane_x3_rc
        out["decisive_reason"] = decisive_reason
        out["exactly_one_x3"] = True
        return out

    if not quorum_sat:
        out["x3_disposition"] = X3B_REVIEW
        warnings.append("X1D judge quorum not satisfied — see x1d_judge_policy in artifact")
        decisive_reason = "WHOLE_RUN_REVIEW: judge quorum not satisfied (preflight credentials / config)"
        out["blockers"] = blockers
        out["warnings"] = warnings
        out["unknowns"] = unknowns
        out["review_reasons"] = review_rc
        out["block_reasons"] = block_rc
        out["judge_reasons"] = judge_rc
        out["lane_x3_reasons"] = lane_x3_rc
        out["decisive_reason"] = decisive_reason
        out["exactly_one_x3"] = True
        return out

    if x1d != "PASS":
        out["x3_disposition"] = X3B_REVIEW
        fb = signals.get("x1d_judge_failure_breakdown")
        if not isinstance(fb, dict):
            fb = {}
        if bool(fb.get("x1d_judge_execution_mismatch")):
            judge_rc.append(RC_JUDGE_EXECUTION_PROVIDER_MISMATCH)
        if bool(fb.get("x1d_judge_model_backed_fail")):
            judge_rc.append(RC_JUDGE_MODEL_BACKED_QUALITY_FAIL)
        if bool(fb.get("x1d_judge_unknown_result")):
            judge_rc.append(RC_JUDGE_UNKNOWN_RESULT)
        if bool(fb.get("x1d_judge_schema_or_parser_blocked")):
            judge_rc.append(RC_JUDGE_SCHEMA_OR_PARSER_BLOCK)
        if bool(fb.get("x1d_judge_provider_unavailable_row")):
            judge_rc.append(RC_JUDGE_PROVIDER_UNAVAILABLE)
        if not judge_rc:
            judge_rc.append(RC_X1D_AGGREGATE_REVIEW)
        warnings.append(
            "X1D rollup overall != PASS — see x1d_lane_judge_diagnostics (E2E) or lane x1d artifacts"
        )
        decisive_reason = (
            "WHOLE_RUN_REVIEW: X1D overall != PASS — diagnostics separate mismatch vs quality vs unknown"
        )
        out["blockers"] = blockers
        out["warnings"] = warnings
        out["unknowns"] = unknowns
        out["review_reasons"] = review_rc
        out["block_reasons"] = block_rc
        out["judge_reasons"] = judge_rc
        out["lane_x3_reasons"] = lane_x3_rc
        out["decisive_reason"] = decisive_reason
        out["exactly_one_x3"] = True
        return out

    if x2_unknown_lane:
        out["x3_disposition"] = X3B_REVIEW
        warnings.append("rollup reported zero X2 gates for at least one lane — inspect lane x2_gate_outputs.json")
        decisive_reason = "WHOLE_RUN_REVIEW: rollup X2 gate coverage incomplete for at least one lane"
        out["blockers"] = blockers
        out["warnings"] = warnings
        out["unknowns"] = unknowns
        out["review_reasons"] = review_rc
        out["block_reasons"] = block_rc
        out["judge_reasons"] = judge_rc
        out["lane_x3_reasons"] = lane_x3_rc
        out["decisive_reason"] = decisive_reason
        out["exactly_one_x3"] = True
        return out

    if _unknown_dominates_section_gates(sg_overall):
        out["x3_disposition"] = X3B_REVIEW
        warnings.append("section_gates overall UNKNOWN — do not infer PASS from ambiguous gate rollup")
        decisive_reason = "WHOLE_RUN_REVIEW: section gate summary UNKNOWN"
        out["blockers"] = blockers
        out["warnings"] = warnings
        out["unknowns"] = unknowns
        out["review_reasons"] = review_rc
        out["block_reasons"] = block_rc
        out["judge_reasons"] = judge_rc
        out["lane_x3_reasons"] = lane_x3_rc
        out["decisive_reason"] = decisive_reason
        out["exactly_one_x3"] = True
        return out

    codes = [str(r.get("x3_code") or "").strip() for r in lanes if str(r.get("x3_code") or "").strip()]
    uniq = sorted(set(codes))
    mixed_lanes = len(uniq) > 1 or any(c != "X3_ALLOW" for c in codes)

    if mixed_lanes:
        out["x3_disposition"] = X3B_REVIEW
        if len(uniq) > 1:
            lane_x3_rc.append(RC_LANE_X3_MIXED)
        if any(c != "X3_ALLOW" for c in codes):
            lane_x3_rc.append(RC_LANE_X3_NON_ALLOW)
        decisive_reason = (
            "WHOLE_RUN_REVIEW: per-lane X3 codes differ or non-ALLOW — "
            "single aggregate REVIEW; lane codes preserved in aggregated_from_lane_x3"
        )
        out["blockers"] = blockers
        out["warnings"] = warnings
        out["unknowns"] = unknowns
        out["review_reasons"] = review_rc
        out["block_reasons"] = block_rc
        out["judge_reasons"] = judge_rc
        out["lane_x3_reasons"] = lane_x3_rc
        out["decisive_reason"] = decisive_reason
        out["exactly_one_x3"] = True
        return out

    if not pa_c or not pa_d or not pa_s:
        out["x3_disposition"] = X3B_REVIEW
        if not pa_c:
            warnings.append("compiled_prompt FEC consumption marker missing on one or more lanes")
        if not pa_d:
            warnings.append("evidence-as-data heuristic failed for one or more lanes")
        if not pa_s:
            warnings.append("compiled_prompt schema binding heuristic failed on one or more lanes")
        decisive_reason = "WHOLE_RUN_REVIEW: PA-equivalent prompt checks incomplete"
        out["blockers"] = blockers
        out["warnings"] = warnings
        out["unknowns"] = unknowns
        out["review_reasons"] = review_rc
        out["block_reasons"] = block_rc
        out["judge_reasons"] = judge_rc
        out["lane_x3_reasons"] = lane_x3_rc
        out["decisive_reason"] = decisive_reason
        out["exactly_one_x3"] = True
        return out

    chroma_min = int(signals.get("min_chroma_evidence_items") or 1)
    if c0_count < chroma_min:
        out["x3_disposition"] = X3B_REVIEW
        warnings.append(f"C0 evidence item count {c0_count} below policy minimum {chroma_min}")
        decisive_reason = "WHOLE_RUN_REVIEW: insufficient grounded evidence items for ALLOW_FINISH"
        out["blockers"] = blockers
        out["warnings"] = warnings
        out["unknowns"] = unknowns
        out["review_reasons"] = review_rc
        out["block_reasons"] = block_rc
        out["judge_reasons"] = judge_rc
        out["lane_x3_reasons"] = lane_x3_rc
        out["decisive_reason"] = decisive_reason
        out["exactly_one_x3"] = True
        return out

    out["x3_disposition"] = X3D_ALLOW_FINISH
    decisive_reason = (
        "WHOLE_RUN_ALLOW_FINISH: structural gates PASS, X1D PASS, homogeneous lane X3_ALLOW, "
        "PA and C0 grounding checks satisfied"
    )
    out["blockers"] = blockers
    out["warnings"] = warnings
    out["unknowns"] = unknowns
    out["review_reasons"] = review_rc
    out["block_reasons"] = block_rc
    out["judge_reasons"] = judge_rc
    out["lane_x3_reasons"] = lane_x3_rc
    out["decisive_reason"] = decisive_reason
    out["exactly_one_x3"] = True
    return out
