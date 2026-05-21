"""Resume-wide package disposition (offline rollup): **not** Exit X3 / integrated spine proof."""

from __future__ import annotations

if __name__ == "__main__":
    raise ImportError(
        "This module is not an operator CLI entrypoint. "
        "Use: python -m apps_rg or python -m apps_rg --section <lane>"
    )

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from apps_rg.runtime.package.resume_package_manifest import (
    RUNTIME_PROOFS,
    ResumePackageProofPaths,
    build_resume_package_manifest,
    load_json,
    repo_root_default,
    resolve_resume_package_paths,
)
from apps_rg.runtime.package.apps_rg_full_resume_x3_eligibility import (
    evaluate_apps_rg_full_success_eligibility,
)
from apps_rg.runtime.internal.generated_lane_rollup import GENERATED_LANES

from apps_rg.runtime.package.resume_package_l6_audit import audit_l6_shadow_packet_for_lane

X3_ALLOW_CODE = "X3_ALLOW"
X3_BLOCKED_DETERMINISTIC = "X3_BLOCKED_DETERMINISTIC_GATES"
X3_BLOCK_L6_HANDOFF_INCOMPLETE = "X3_BLOCK_L6_HANDOFF_INCOMPLETE"
X3_REVIEW_SECTION = "X3_REVIEW_SECTION_JUDGE_STATUS"

CONSTRUCTOR_MODULE = "apps_rg.runtime.internal.resume_package_disposition"


def _utc_now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


def _resolve_repo_path(rr: Path, raw: Any) -> Path | None:
    if raw is None or not isinstance(raw, str) or not raw.strip():
        return None
    p = Path(raw)
    return p.resolve() if p.is_absolute() else (rr / raw).resolve()


def _x2_all_pass(blob: Mapping[str, Any]) -> tuple[bool, list[str]]:
    if blob.get("all_pass") is True and not blob.get("failed_gate_ids"):
        return True, []
    fg: list[str] = []
    if isinstance(blob.get("failed_gate_ids"), list) and blob["failed_gate_ids"]:
        fg = [str(x) for x in blob["failed_gate_ids"]]
    elif isinstance(blob.get("failed_gates"), list) and blob["failed_gates"]:
        fg = [str(x) for x in blob["failed_gates"]]
    else:
        for g in blob.get("gates") or []:
            if isinstance(g, dict) and g.get("pass") is False:
                fg.append(str(g.get("gate_id") or "unknown_gate"))
    xf = blob.get("x2_failed")
    if isinstance(xf, int) and xf > 0 and not fg:
        fg = ["<x2_failed_counter_nonzero_without_gate_ids>"]
    return len(fg) == 0, fg


def _rollup_x2_failed_int(raw: Any) -> int | None:
    if isinstance(raw, bool):
        return None
    if isinstance(raw, int):
        return raw
    try:
        return int(str(raw))
    except (ValueError, TypeError):  # guardian: allow-return-none-swallow -- P2 burndown: fail-soft optional boundary
        return None


def _repo_rel(rr: Path, path: Path | None) -> str | None:
    if path is None:
        return None
    try:
        return path.relative_to(rr).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def _merge_non_generation_guarantees(
    *,
    final_resume_manifest: Mapping[str, Any],
    docx_manifest: Mapping[str, Any],
    docx_render_manifest: Mapping[str, Any],
) -> tuple[bool, dict[str, Any]]:
    fm_calls = final_resume_manifest.get("calls") or {}
    dm_g = docx_manifest.get("guarantees") or {}
    dr_v = docx_render_manifest.get("verification") or {}
    keys = ("provider_calls_made", "qwen_calls_made", "judge_calls_made")
    fused: dict[str, bool | None] = {k: None for k in keys}
    contradiction = False

    def _consume(label: str, blob: Mapping[str, Any]) -> None:
        nonlocal contradiction
        for k in keys:
            if k not in blob:
                continue
            v = blob[k]
            if v is not False and v is not True:
                contradiction = True
                continue
            b = bool(v)
            prev = fused[k]
            if prev is None:
                fused[k] = b
            elif prev != b:
                contradiction = True

    _consume("final_resume_manifest.calls", fm_calls)
    _consume("docx_manifest.guarantees", dm_g)
    _consume("docx_render_manifest.verification", dr_v)

    missing = contradiction or any(fused[k] is None for k in keys)
    all_report_no_calls = (
        fused["provider_calls_made"] is False
        and fused["qwen_calls_made"] is False  # noqa: E721
        and fused["judge_calls_made"] is False
    )
    ok = (not contradiction) and (not missing) and all_report_no_calls
    fused_out = {str(k): fused[k] for k in fused}
    return ok, fused_out


def _merge_l6_package_checks(per_lane: Mapping[str, Mapping[str, Any]]) -> tuple[dict[str, bool], bool]:
    """Merge per-lane L6 verifier checks into one aggregate; unify/ibm lane-only checks scoped."""
    agg: dict[str, bool] = {}
    fatal_bundle = False
    for lk in GENERATED_LANES:
        rec_raw = per_lane.get(lk)
        if rec_raw is None:
            fatal_bundle = True
            continue
        fatal_bundle |= bool(rec_raw.get("fatal"))
        checks_raw = rec_raw.get("checks") or {}
        if not isinstance(checks_raw, dict):
            fatal_bundle = True
            continue
        for ck, val in checks_raw.items():
            if not isinstance(val, bool):
                continue
            if str(ck).startswith("x3_l6_unify_") and lk != "unify_bullets":
                continue
            if str(ck).startswith("x3_l6_ibm_") and lk != "ibm_bullets":
                continue
            agg[ck] = bool(agg.get(ck, True)) and bool(val)
    return agg, fatal_bundle


def _load_optional_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        return raw if isinstance(raw, dict) else None
    except (OSError, json.JSONDecodeError):  # guardian: allow-return-none-swallow -- P2 burndown: fail-soft optional boundary
        return None


def evaluate_resume_package(
    *,
    paths: ResumePackageProofPaths,
    rollup: Mapping[str, Any],
    locked_x2: Mapping[str, Any],
    final_manifest: Mapping[str, Any],
    final_x2: Mapping[str, Any],
    docx_manifest: Mapping[str, Any],
    docx_manifest_x2: Mapping[str, Any],
    docx_render_manifest: Mapping[str, Any],
    docx_render_x2: Mapping[str, Any],
    assembly_receipt: Mapping[str, Any] | None = None,
    review_lane_policy: Mapping[str, Any] | None = None,
    cross_section_x2: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    rr = paths.repo_root
    block_notes: list[str] = []

    deterministic_failed_ids: dict[str, list[str]] = {
        "generated_lane_x2": [],
        "locked_copy_x2": [],
        "final_resume_x2": [],
        "docx_manifest_x2": [],
        "docx_render_x2": [],
        "apps_rg_l2_product_w3": [],
        "deterministic_gate_failures_aggregate": [],
    }

    lanes = rollup.get("lanes")
    if not isinstance(lanes, dict):
        block_notes.append("rollup_missing_or_invalid_lanes_dict")
        lanes = {}

    lane_rows: list[dict[str, Any]] = []
    for lane_key in GENERATED_LANES:
        row_raw = lanes.get(lane_key)
        if not isinstance(row_raw, dict):
            deterministic_failed_ids["generated_lane_x2"].append(f"missing_lane_row:{lane_key}")
            lane_rows.append(
                {
                    "lane_key": lane_key,
                    "runtime_generation_status": None,
                    "x2_failed": None,
                    "x3_code_from_rollup": None,
                    "x3_recorded": False,
                    "x3_record_path_repo_relative": None,
                    "x3_code_from_artifact": None,
                    "x3_codes_match": None,
                    "artifact_load_error": "missing_lane_in_rollup_or_wrong_shape",
                }
            )
            continue
        rg = row_raw.get("runtime_generation_status")
        x2f = row_raw.get("x2_failed")
        x3_rollup = row_raw.get("x3_code")
        refs_raw = row_raw.get("artifact_refs")
        refs = refs_raw if isinstance(refs_raw, dict) else {}
        xp = refs.get("x3_disposition.json")
        x_path = _resolve_repo_path(rr, xp)
        artifact_code: str | None = None
        codes_match: bool | None = None
        recorded = False
        load_err: str | None = None
        if x_path is None or not x_path.is_file():
            load_err = "x3_disposition_missing_or_unreadable_path"
            block_notes.append(f"{lane_key}:x3_record_missing")
        else:
            recorded = True
            try:
                raw_x3 = load_json(x_path)
                artifact_code = str(raw_x3.get("x3_code")) if isinstance(raw_x3, dict) else None
            except OSError:
                artifact_code = None
                load_err = "x3_disposition_os_error"
                block_notes.append(f"{lane_key}:x3_file_os_error")
                recorded = False
            except json.JSONDecodeError:
                artifact_code = None
                load_err = "x3_disposition_invalid_json"
                block_notes.append(f"{lane_key}:x3_invalid_json")
                recorded = False

        codes_match = None
        if artifact_code is not None and isinstance(x3_rollup, str):
            codes_match = artifact_code == x3_rollup
            if codes_match is False:
                deterministic_failed_ids["generated_lane_x2"].append(f"x3_code_mismatch:{lane_key}")
                block_notes.append(f"{lane_key}:x3_code_mismatch_rollup_vs_artifact")

        if rg != "REAL_LLM":
            deterministic_failed_ids["generated_lane_x2"].append(
                f"runtime_generation_not_real_llm:{lane_key}:{rg!s}"
            )
            block_notes.append(f"{lane_key}:runtime_generation_status_not_REAL_LLM")
        xf_int = _rollup_x2_failed_int(x2f)
        refs_x2_raw = refs.get("x2_gate_outputs.json")
        refs_x2 = _resolve_repo_path(rr, refs_x2_raw)
        if refs_x2 is None or not refs_x2.is_file():
            deterministic_failed_ids["generated_lane_x2"].append(f"missing_lane_x2_artifact_refs:{lane_key}")
            block_notes.append(f"{lane_key}:missing_x2_gate_outputs_file")
        else:
            try:
                lx2 = load_json(refs_x2)
                if isinstance(lx2, Mapping):
                    ok_x2, fids = _x2_all_pass(lx2)
                    if not ok_x2:
                        deterministic_failed_ids["generated_lane_x2"].extend(
                            [f"{lane_key}:{fid}" for fid in fids]
                        )
                        block_notes.append(f"{lane_key}:lane_x2_not_all_pass:{','.join(fids)}")
            except (json.JSONDecodeError, OSError):
                deterministic_failed_ids["generated_lane_x2"].append(f"lane_x2_unreadable:{lane_key}")
                block_notes.append(f"{lane_key}:lane_x2_unreadable")

        if isinstance(xf_int, int) and xf_int > 0:
            deterministic_failed_ids["generated_lane_x2"].append(
                f"rollup_reports_x2_failed_nonzero:{lane_key}:{xf_int}"
            )

        lane_rows.append(
            {
                "lane_key": lane_key,
                "runtime_generation_status": rg,
                "rollup_x2_failed": xf_int,
                "rollup_x3_code": x3_rollup,
                "x3_recorded": recorded,
                "x3_record_path_repo_relative": _repo_rel(rr, x_path) if recorded and x_path else None,
                "x3_code_from_artifact": artifact_code,
                "x3_codes_match": codes_match,
                "artifact_load_error": load_err,
            }
        )

    lanes_nav_dict = lanes if isinstance(lanes, dict) else {}
    per_lane_l6_audit: dict[str, dict[str, Any]] = {}
    for lane_key in GENERATED_LANES:
        lr = lanes_nav_dict.get(lane_key)
        l6pkt: dict[str, Any] | None = None
        l6_repo_rel: str | None = None
        if isinstance(lr, dict):
            refs_m = lr.get("artifact_refs") if isinstance(lr.get("artifact_refs"), dict) else {}
            rp = refs_m.get("l6_shadow_eval_package.json")
            px = _resolve_repo_path(rr, rp)
            if px is not None and px.is_file():
                l6_repo_rel = _repo_rel(rr, px)
                try:
                    raw_l6 = load_json(px)
                    if isinstance(raw_l6, dict):
                        l6pkt = raw_l6
                except (OSError, json.JSONDecodeError):
                    l6pkt = None
        audit_row = audit_l6_shadow_packet_for_lane(lane_key=lane_key, packet=l6pkt)
        audit_row["l6_shadow_eval_ref_repo_relative"] = l6_repo_rel
        if isinstance(l6pkt, dict):
            audit_row["observed_human_label_status"] = l6pkt.get("human_label_status")
            audit_row["observed_calibration_status"] = l6pkt.get("calibration_status")
            audit_row["observed_runtime_approval_authority"] = l6pkt.get("runtime_approval_authority")
        per_lane_l6_audit[lane_key] = audit_row

    ok_lc, fid_lc = _x2_all_pass(locked_x2)
    if not ok_lc:
        deterministic_failed_ids["locked_copy_x2"].extend(fid_lc)
        block_notes.append(f"locked_copy_x2_fail:{','.join(fid_lc)}")

    ok_fr, fid_fr = _x2_all_pass(final_x2)
    if not ok_fr:
        deterministic_failed_ids["final_resume_x2"].extend(fid_fr)
        block_notes.append(f"final_resume_x2_fail:{','.join(fid_fr)}")

    ok_dm, fid_dm = _x2_all_pass(docx_manifest_x2)
    if not ok_dm:
        deterministic_failed_ids["docx_manifest_x2"].extend(fid_dm)
        block_notes.append(f"docx_manifest_x2_fail:{','.join(fid_dm)}")

    ok_dr, fid_dr = _x2_all_pass(docx_render_x2)
    if not ok_dr:
        deterministic_failed_ids["docx_render_x2"].extend(fid_dr)
        block_notes.append(f"docx_render_x2_fail:{','.join(fid_dr)}")

    agg_det: list[str] = []
    for layer, items in deterministic_failed_ids.items():
        if layer == "deterministic_gate_failures_aggregate":
            continue
        for item in items:
            agg_det.append(f"{layer}:{item}")
    deterministic_failed_ids["deterministic_gate_failures_aggregate"] = sorted(set(agg_det))

    guarantees_ok, merged_calls = _merge_non_generation_guarantees(
        final_resume_manifest=final_manifest,
        docx_manifest=docx_manifest,
        docx_render_manifest=docx_render_manifest,
    )
    if not guarantees_ok:
        block_notes.append("non_generation_guarantee_merge_failed_or_missing_sources")

    out_docx_repo = docx_render_manifest.get("output_docx")
    if not isinstance(out_docx_repo, str) or not out_docx_repo.strip():
        block_notes.append("docx_render_manifest_missing_output_docx")
        docx_abs: Path | None = None
    else:
        docx_abs = (rr / out_docx_repo.strip()).resolve()
    docx_ok = docx_abs is not None and docx_abs.is_file()
    if not docx_ok:
        block_notes.append("rendered_docx_absent_on_disk")

    apps_rg_w3_enforced = False
    apps_rg_w3_eligible = True
    apps_rg_w3_reasons: list[str] = []
    apps_rg_manifest_rel: str | None = None
    am_path = paths.apps_rg_output_manifest_json
    if am_path.is_file():
        apps_rg_w3_enforced = True
        apps_rg_manifest_rel = _repo_rel(rr, am_path)
        try:
            am_blob = load_json(am_path)
            if not isinstance(am_blob, dict):
                apps_rg_w3_eligible = False
                apps_rg_w3_reasons.append("apps_rg_output_manifest_not_object")
            else:
                run_root = am_path.parent.resolve()
                apps_rg_w3_eligible, apps_rg_w3_reasons = evaluate_apps_rg_full_success_eligibility(
                    manifest=am_blob,
                    run_root=run_root,
                )
        except (OSError, json.JSONDecodeError) as exc:
            apps_rg_w3_eligible = False
            apps_rg_w3_reasons.append(f"apps_rg_output_manifest_unreadable:{exc}")
        if not apps_rg_w3_eligible:
            deterministic_failed_ids["apps_rg_l2_product_w3"].extend(apps_rg_w3_reasons)
            block_notes.append(
                "apps_rg_w3_full_resume_product_ineligible:" + ";".join(apps_rg_w3_reasons)
            )

    prev_agg = list(deterministic_failed_ids["deterministic_gate_failures_aggregate"])
    extra = [f"apps_rg_l2_product_w3:{r}" for r in deterministic_failed_ids["apps_rg_l2_product_w3"]]
    deterministic_failed_ids["deterministic_gate_failures_aggregate"] = sorted(set(prev_agg + extra))

    deterministic_blocked = (
        any(
            deterministic_failed_ids[k]
            for k in (
                "generated_lane_x2",
                "locked_copy_x2",
                "final_resume_x2",
                "docx_manifest_x2",
                "docx_render_x2",
                "apps_rg_l2_product_w3",
            )
        )
        or not guarantees_ok
        or not docx_ok
    )

    rollup_x3_allow = []
    rollup_x3_non_allow = []
    for row in lane_rows:
        lk = row.get("lane_key")
        code = row.get("rollup_x3_code") or ""
        code_s = str(code)
        if code_s == X3_ALLOW_CODE:
            rollup_x3_allow.append(lk)
        else:
            rollup_x3_non_allow.append({"lane_key": lk, "x3_code": code_s})

    all_sections_x3_allow = len(GENERATED_LANES) == len(rollup_x3_allow)

    rlp_summary_early: dict[str, Any] = {}
    if isinstance(review_lane_policy, Mapping):
        raw_sum = review_lane_policy.get("summary")
        if isinstance(raw_sum, Mapping):
            rlp_summary_early = dict(raw_sum)
    asm_early = assembly_receipt if isinstance(assembly_receipt, Mapping) else {}
    product_review_required = bool(
        asm_early.get("product_review_required") or rlp_summary_early.get("product_review_required")
    )

    agg_l6_checks, fatal_l6 = _merge_l6_package_checks(per_lane_l6_audit)
    l6_handoff_blocked = fatal_l6

    if deterministic_blocked:
        final_code = X3_BLOCKED_DETERMINISTIC
    elif l6_handoff_blocked:
        final_code = X3_BLOCK_L6_HANDOFF_INCOMPLETE
    elif all_sections_x3_allow and not product_review_required:
        final_code = X3_ALLOW_CODE
    else:
        final_code = X3_REVIEW_SECTION
    if product_review_required and all_sections_x3_allow:
        block_notes.append("product_review_required:review_or_mock_lanes_present")

    disposition = {
        "disposition_family": "resume_package_x3",
        "evaluated_at_utc": _utc_now_iso(),
        "constructor_module": CONSTRUCTOR_MODULE,
        "final_x3_code": final_code,
        "deterministic_blocked": deterministic_blocked,
        "deterministic_failed_ids_by_layer": {k: v for k, v in deterministic_failed_ids.items() if k != "deterministic_gate_failures_aggregate"},
        "deterministic_gate_failure_ids_aggregate": deterministic_failed_ids["deterministic_gate_failures_aggregate"],
        "block_notes_sorted_unique": sorted(set(block_notes)),
        "rollup_summary": rollup.get("summary") or rollup.get("status"),
        "section_level_x3": {
            "generated_lane_coverage": list(GENERATED_LANES),
            "lanes_detail": lane_rows,
            "rollup_x3_allow_lane_keys": rollup_x3_allow,
            "rollup_x3_non_allow": rollup_x3_non_allow,
            "all_generated_lane_x3_allow": bool(all_sections_x3_allow),
        },
        "non_generation_stage_guarantees": merged_calls,
        "non_generation_stage_guarantees_all_false": guarantees_ok,
        "docx_path_repo_relative_observed_from_render_manifest": out_docx_repo if isinstance(out_docx_repo, str) else None,
        "rendered_docx_exists_on_disk": docx_ok,
        "explicit_waiver_policy_path": None,
        "waivers_loaded": [],
        "metadata_confirmation": {
            "registry_changes_in_this_packaging_task": False,
            "v1_prompt_edits_in_this_packaging_task": False,
            "agentic_core_edits_in_this_packaging_task": False,
        },
        "l6_shadow_handoff_audit": {
            "per_lane": {
                lk: {
                    "fatal": per_lane_l6_audit[lk]["fatal"],
                    "l6_shadow_eval_ref_repo_relative": per_lane_l6_audit[lk].get(
                        "l6_shadow_eval_ref_repo_relative"
                    ),
                    "incomplete_field_paths_sorted": per_lane_l6_audit[lk].get("incomplete_field_paths_sorted"),
                    "checks": per_lane_l6_audit[lk].get("checks") or {},
                    "observed_human_label_status": per_lane_l6_audit[lk].get("observed_human_label_status"),
                    "observed_calibration_status": per_lane_l6_audit[lk].get("observed_calibration_status"),
                    "observed_runtime_approval_authority": per_lane_l6_audit[lk].get(
                        "observed_runtime_approval_authority"
                    ),
                }
                for lk in GENERATED_LANES
            },
            "aggregate_checks": agg_l6_checks,
            "l6_handoff_blocked": l6_handoff_blocked,
        },
    }

    disposition["deterministic_proof_summary"] = {
        "generated_lanes_RUNTIME_LLM_gate": sum(
            1 for r in lane_rows if r.get("runtime_generation_status") == "REAL_LLM"
        )
        == len(GENERATED_LANES),
        "generated_lane_rollup_x2_zero_failures_via_rollup_counters": sum(
            1 for r in lane_rows if isinstance(r.get("rollup_x2_failed"), int) and int(r["rollup_x2_failed"]) == 0
        )
        == len(GENERATED_LANES),
        "every_lane_x3_disposition_recorded": all(bool(r.get("x3_recorded")) for r in lane_rows),
        "locked_copy_x2_all_pass": ok_lc,
        "final_resume_x2_all_pass": ok_fr,
        "docx_manifest_x2_all_pass": ok_dm,
        "docx_render_x2_all_pass": ok_dr,
        "docx_file_exists_observed_disk": docx_ok,
        "non_generation_no_provider_no_qwen_no_judge_aggregate": guarantees_ok,
        "every_lane_l6_handoff_audited": len(per_lane_l6_audit) == len(GENERATED_LANES),
        "l6_handoff_agg_checks_all_true": len(agg_l6_checks) > 0 and all(agg_l6_checks.values()),
        "l6_handoff_hard_pass_aggregate": bool(not l6_handoff_blocked),
        "apps_rg_l2_product_w3_enforced": apps_rg_w3_enforced,
        "apps_rg_l2_product_w3_eligible": apps_rg_w3_eligible,
    }

    disposition["deterministic_blocked_explain_if_true"] = {
        k: deterministic_failed_ids[k]
        for k in (
            "generated_lane_x2",
            "locked_copy_x2",
            "final_resume_x2",
            "docx_manifest_x2",
            "docx_render_x2",
            "apps_rg_l2_product_w3",
        )
        if deterministic_failed_ids[k]
    }

    disposition["aggregate_pass_under_policy_no_waivers_yet"] = final_code == X3_ALLOW_CODE
    disposition["explicit_waiver_needed_for_allow_when_section_review"] = (
        deterministic_blocked is False and not l6_handoff_blocked and not all_sections_x3_allow
    )

    disposition["apps_rg_full_resume_product_gate"] = {
        "w3_enforced": apps_rg_w3_enforced,
        "eligible_for_package_x3_allow": apps_rg_w3_eligible,
        "reasons": list(apps_rg_w3_reasons),
        "manifest_path_repo_relative": apps_rg_manifest_rel,
    }
    disposition["apps_rg_full_resume_outcome_authorized"] = bool(final_code == X3_ALLOW_CODE)
    if final_code == X3_ALLOW_CODE:
        apps_rg_prod_terminal = "SUCCESS"
    elif final_code == X3_BLOCKED_DETERMINISTIC:
        apps_rg_prod_terminal = "BLOCKED"
    elif final_code == X3_BLOCK_L6_HANDOFF_INCOMPLETE:
        apps_rg_prod_terminal = "BLOCKED"
    else:
        apps_rg_prod_terminal = "FAILURE"
    disposition["apps_rg_product_terminal_class"] = apps_rg_prod_terminal
    disposition["apps_rg_package_x3_disposition"] = final_code
    disposition["apps_rg_full_resume_decisive_reason"] = (
        "; ".join(apps_rg_w3_reasons) if apps_rg_w3_reasons else None
    )

    disposition["prior_final_resume_manifest_rollups_rollforward_note"] = final_manifest.get(
        "rollup_id_source"
    )

    asm = asm_early
    rlp = review_lane_policy if isinstance(review_lane_policy, Mapping) else {}
    warn_blob: dict[str, Any] = {}
    if isinstance(cross_section_x2, Mapping):
        raw_warn = cross_section_x2.get("warn_policy")
        if isinstance(raw_warn, Mapping):
            warn_blob = dict(raw_warn)

    assembly_product_allow = bool(asm.get("product_allow_claimed"))
    cross_product_pass = bool(asm.get("cross_section_x2_product_pass"))
    structural_x2_pass = bool(asm.get("structural_x2_all_pass") and ok_fr)
    cross_structural_pass = bool(asm.get("cross_section_x2_structural_only") or asm.get("cross_section_x2_all_pass"))

    aggregate_coherence_pass = False
    coherence_rel = str(asm.get("full_resume_llm_coherence_review_json") or "").strip()
    if coherence_rel:
        coh_path = _resolve_repo_path(rr, coherence_rel)
        coh_blob = _load_optional_json(coh_path) if coh_path is not None else None
        aggregate_coherence_pass = bool(
            coh_blob and coh_blob.get("full_resume_coherence_pass") is True
        )

    package_product_allow_claimed = (
        assembly_product_allow
        and structural_x2_pass
        and cross_product_pass
        and aggregate_coherence_pass
        and not deterministic_blocked
        and final_code == X3_ALLOW_CODE
    )

    from apps_rg.runtime.non_product_proof_stamp import package_rollup_non_product_stamp

    package_x3_allow = final_code == X3_ALLOW_CODE
    disposition.update(package_rollup_non_product_stamp(package_x3_allow=package_x3_allow))

    disposition["aggregation_product_proof"] = {
        "assembly_receipt_v2_present": bool(asm),
        "structural_x2_all_pass": structural_x2_pass,
        "cross_section_x2_structural_pass": cross_structural_pass,
        "cross_section_x2_product_pass": cross_product_pass,
        "aggregation_receipt_v2_complete": bool(asm.get("receipt_id") == "final_resume_assembly_receipt_v2"),
        "aggregate_full_resume_coherence_pass": aggregate_coherence_pass,
        "product_review_required": product_review_required,
        "product_allow_claimed": False,
        "package_rollup_product_allow_claimed": package_product_allow_claimed,
        "review_lane_policy_summary": rlp_summary_early,
        "warn_policy": warn_blob,
        "explicit_non_claims": list(asm.get("explicit_non_claims") or []) + list(rlp.get("explicit_non_claims") or []),
    }
    disposition["block_notes_sorted_unique"] = sorted(set(block_notes))

    return disposition


def _lane_l6_manifest_extras(rollup_blob: Mapping[str, Any], rr: Path) -> dict[str, Any]:
    refs: dict[str, str | None] = {}
    sha_map: dict[str, str | None] = {}
    lanes_d = rollup_blob.get("lanes") if isinstance(rollup_blob.get("lanes"), dict) else {}
    for lk in GENERATED_LANES:
        row = lanes_d.get(lk)
        rel: str | None = None
        if isinstance(row, dict):
            ar = row.get("artifact_refs") if isinstance(row.get("artifact_refs"), dict) else {}
            raw = ar.get("l6_shadow_eval_package.json")
            p = _resolve_repo_path(rr, raw)
            if p is not None and p.is_file():
                try:
                    rel = p.relative_to(rr.resolve()).as_posix()
                except ValueError:
                    rel = str(p).replace("\\", "/")
                sha_map[lk] = hashlib.sha256(p.read_bytes()).hexdigest()
            else:
                sha_map[lk] = None
        refs[lk] = rel
    return {
        "lane_l6_shadow_eval_package_refs": refs,
        "lane_l6_shadow_eval_sha256_hex": sha_map,
    }


def emit_resume_package_artifacts(
    paths: ResumePackageProofPaths | None = None,
) -> dict[str, Any]:
    p = paths or resolve_resume_package_paths()

    rollup = load_json(p.rollup_json)
    lc_x2 = load_json(p.locked_copy_x2_json)
    fr_m = load_json(p.final_resume_manifest_json)
    fr_x2 = load_json(p.final_resume_x2_json)
    dm = load_json(p.docx_manifest_json)
    dm_x2 = load_json(p.docx_manifest_x2_json)
    drm = load_json(p.docx_render_manifest_json)
    dr_x2 = load_json(p.docx_render_x2_json)

    assembly_dir = p.final_resume_json.parent
    assembly_receipt = _load_optional_json(assembly_dir / "final_resume_receipt.json")
    review_lane_policy = _load_optional_json(assembly_dir / "review_lane_policy.json")
    cross_section_x2 = _load_optional_json(assembly_dir / "cross_section_x2_gate_outputs.json")

    out_doc = drm.get("output_docx") if isinstance(drm, Mapping) else None
    if not isinstance(out_doc, str):
        out_doc = f"{RUNTIME_PROOFS}/docx/amit_ayer_resume_v1.docx"

    l6_manifest_extras = _lane_l6_manifest_extras(rollup, p.repo_root)
    manifest = build_resume_package_manifest(
        paths=p,
        docx_emit_path_relative=out_doc,
        rollup_blob=rollup,
        extras=l6_manifest_extras,
    )
    disposition = evaluate_resume_package(
        paths=p,
        rollup=rollup,
        locked_x2=lc_x2,
        final_manifest=fr_m,
        final_x2=fr_x2,
        docx_manifest=dm,
        docx_manifest_x2=dm_x2,
        docx_render_manifest=drm,
        docx_render_x2=dr_x2,
        assembly_receipt=assembly_receipt,
        review_lane_policy=review_lane_policy,
        cross_section_x2=cross_section_x2,
    )

    p.output_dir.mkdir(parents=True, exist_ok=True)
    mf_path = p.package_manifest_json()
    x3_path = p.package_x3_json()
    rc_path = p.package_receipt_json()

    mf_path.write_text(json.dumps(manifest, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    x3_path.write_text(json.dumps(disposition, indent=2, sort_keys=False) + "\n", encoding="utf-8")

    rr = p.repo_root
    receipt = {
        "receipt_id": "resume_package_receipt_v1",
        "emitted_at_utc": disposition["evaluated_at_utc"],
        "resume_package_manifest_json": str(manifest["aggregated_proof_outputs"]["resume_package_manifest_json"]),
        "resume_package_x3_disposition_json": str(manifest["aggregated_proof_outputs"]["resume_package_x3_disposition_json"]),
        "final_x3_code": disposition["final_x3_code"],
        "deterministic_blocked": disposition["deterministic_blocked"],
        "deterministic_aggregate_failures_nonempty": len(disposition["deterministic_gate_failure_ids_aggregate"]) > 0,
        "deterministic_aggregate_failures_sorted": disposition["deterministic_gate_failure_ids_aggregate"],
        "rollup_id": rollup.get("rollup_id"),
        "repo_relative_package_dir": p.output_dir.relative_to(rr).as_posix(),
    }
    rr_note = disposition.get("section_level_x3") or {}
    receipt["lanes_all_x3_allow"] = bool(rr_note.get("all_generated_lane_x3_allow"))
    agg_proof = disposition.get("aggregation_product_proof") or {}
    receipt["product_allow_claimed"] = False
    receipt["package_rollup_product_allow_claimed"] = bool(agg_proof.get("package_rollup_product_allow_claimed"))
    receipt.update(
        {
            k: disposition[k]
            for k in (
                "package_disposition_classification",
                "proof_classification",
                "package_x3_allow",
                "exit_x3_disposition",
                "eligible_for_l7_certification",
            )
            if k in disposition
        }
    )
    receipt["product_review_required"] = bool(agg_proof.get("product_review_required"))
    receipt["review_lane_policy_json"] = _repo_rel(rr, assembly_dir / "review_lane_policy.json")
    receipt["coherent_rollup_policy_json"] = _repo_rel(rr, assembly_dir / "coherent_rollup_policy.json")
    rc_path.write_text(json.dumps(receipt, indent=2, sort_keys=False) + "\n", encoding="utf-8")

    return {
        "resume_package_manifest": manifest,
        "resume_package_disposition": disposition,
        "resume_package_receipt": receipt,
        "paths": p,
        "resume_package_manifest_path": mf_path,
        "resume_package_x3_disposition_path": x3_path,
        "resume_package_receipt_path": rc_path,
    }


