"""Guarded verification for a recorded modular R4 proof run directory (artifacts only).

Used before/when declaring SSOT flips in ``r4_generation_route``. No providers, no network.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Final

from apps_rg.l2_recipe.r4_generation_mode import MODE_MODULAR_SECTION_LANES
from apps_rg.runtime.locked_copy.locked_copy_manifest import find_repo_root
from apps_rg.runtime.internal.generated_lane_rollup import GENERATED_LANES

R4_RECORDED_MODULAR_PROOF_RUN_ID: Final[str] = "cli_e6a9b9d74b09"

_TOP_LEVEL_ENVELOPE_SCAN: Final[tuple[str, ...]] = (
    "runtime_trace_snapshot.json",
    "validated_request.json",
    "exit_review_packet.json",
    "runtime_exhaust_bundle.json",
)


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def verify_recorded_modular_r4_proof_bundle(
    *,
    repo_root: Path | None = None,
    run_id: str | None = None,
) -> list[str]:
    """Return **error strings**; empty list means all checks passed.

    Parameters
    ----------
    repo_root:
        Repository root (defaults to ``find_repo_root()``).
    run_id:
        Run folder name under ``artifacts/apps_rg/runs/`` (defaults to
        ``R4_RECORDED_MODULAR_PROOF_RUN_ID``).
    """
    rid = (run_id or R4_RECORDED_MODULAR_PROOF_RUN_ID).strip()
    repo = (repo_root or find_repo_root()).resolve()
    run_dir = (repo / "artifacts" / "apps_rg" / "runs" / rid).resolve()
    errs: list[str] = []

    if not run_dir.is_dir():
        return [f"missing_proof_run_dir:{run_dir.as_posix()}"]

    for rel in _TOP_LEVEL_ENVELOPE_SCAN:
        p = run_dir / rel
        if p.is_file() and "run_apps_rg_l2_envelope" in p.read_text(encoding="utf-8", errors="replace"):
            errs.append(f"legacy_l2_envelope_artifact_evidence:{rel}")

    man_path = run_dir / "r4_run_manifest.json"
    if not man_path.is_file():
        errs.append("missing_r4_run_manifest.json")
    else:
        man = _read_json(man_path)
        if not isinstance(man, dict):
            errs.append("r4_run_manifest_not_object")
        else:
            if str(man.get("x3_disposition") or "") != "X3D":
                errs.append(f"x3_disposition_expected_X3D_got:{man.get('x3_disposition')!r}")
            if str(man.get("l2_fault") or "") != "":
                errs.append(f"expected_empty_l2_fault_got:{man.get('l2_fault')!r}")

    if not (run_dir / "outputs/generated_resume.json").is_file():
        errs.append("missing:outputs/generated_resume.json")

    out_man = run_dir / "apps_rg_output_manifest.json"
    outcome_ok = False
    if not out_man.is_file():
        errs.append("missing_apps_rg_output_manifest.json")
    else:
        om = _read_json(out_man)
        if not isinstance(om, dict):
            errs.append("apps_rg_output_manifest_not_object")
        else:
            req = om.get("required_artifacts")
            if not isinstance(req, dict):
                errs.append("required_artifacts_missing")
            elif req.get("generated_resume_json") != "verified":
                errs.append("generated_resume_json_not_verified")
            outcome_ok = bool(
                om.get("apps_rg_generation_status") == "REAL_RESUME"
                and om.get("full_resume_generated") is True
                and isinstance(om.get("required_artifacts"), dict)
                and om["required_artifacts"].get("generated_resume_json") == "verified",
            )

    erp = run_dir / "exit_review_packet.json"
    if erp.is_file():
        er = _read_json(erp)
        if isinstance(er, dict):
            pay = er.get("payload")
            if isinstance(pay, dict):
                if str(pay.get("x3_disposition") or "") != "X3D":
                    errs.append(f"exit_review_x3_expected_X3D_got:{pay.get('x3_disposition')!r}")
                if str(pay.get("l2_fault") or "") != "":
                    errs.append(f"exit_review_expected_empty_l2_fault_got:{pay.get('l2_fault')!r}")

    if not outcome_ok and "missing_apps_rg_output_manifest.json" not in errs:
        errs.append("outcome_authorized_proxy_failed:manifest_not_REAL_RESUME_verified")

    _silent_markers = ('"silent_provider_fallback": true', '"silent_fallback_detected": true')
    for rel in ("runtime_trace_snapshot.json", "runtime_exhaust_bundle.json"):
        p = run_dir / rel
        if not p.is_file():
            continue
        blob = p.read_text(encoding="utf-8", errors="replace")
        if any(m in blob for m in _silent_markers):
            errs.append(f"silent_fallback_marker_in:{rel}")

    gen_rc = run_dir / "modular_r4" / "generate_resume_step_receipt.json"
    if not gen_rc.is_file():
        errs.append("missing_modular_r4/generate_resume_step_receipt.json")
    else:
        gr = _read_json(gen_rc)
        if not isinstance(gr, dict):
            errs.append("generate_resume_step_receipt_not_object")
        elif str(gr.get("apps_rg_r4_generation_mode") or "") != MODE_MODULAR_SECTION_LANES:
            errs.append(f"generate_receipt_mode_not_modular:{gr.get('apps_rg_r4_generation_mode')!r}")
        elif str(gr.get("decisive_status") or "") != "PASS":
            errs.append(f"generate_receipt_decisive_not_PASS:{gr.get('decisive_status')!r}")
        elif gr.get("final_schema_valid") is not True:
            errs.append("generate_receipt_final_schema_invalid")
        elif str(gr.get("failure_reason") or "") != "":
            errs.append(f"generate_receipt_failure_reason_non_empty:{gr.get('failure_reason')!r}")

    calls_path = run_dir / "modular_r4" / "section_provider_calls.json"
    if not calls_path.is_file():
        errs.append("missing_modular_r4/section_provider_calls.json")
    else:
        raw_calls = _read_json(calls_path)
        if not isinstance(raw_calls, dict):
            errs.append("section_provider_calls_not_object")
        else:
            if raw_calls.get("locked_sections_provider_calls_detected") is True:
                errs.append("full_resume_provider_lane_detected")
            if raw_calls.get("real_lane_invocation_attempted") is not True:
                errs.append("real_lane_invocation_attempted_not_true")
            recs = raw_calls.get("records")
            if not isinstance(recs, list) or len(recs) != len(GENERATED_LANES):
                errs.append(f"section_lane_record_count_expected_{len(GENERATED_LANES)}")
            else:
                lanes = {str(r.get("section_lane")) for r in recs if isinstance(r, dict)}
                if lanes != set(GENERATED_LANES):
                    errs.append(f"section_lane_set_mismatch:{sorted(lanes)!r}")
                mocked = sum(
                    1 for r in recs if isinstance(r, dict) and str(r.get("generation_status") or "") == "MOCKED"
                )
                if mocked != 0:
                    errs.append(f"MOCKED_lane_count_nonzero:{mocked}")
                for r in recs:
                    if not isinstance(r, dict):
                        continue
                    if r.get("provider_call_attempted") is not True:
                        errs.append(f"provider_call_attempted_false:{r.get('section_lane')}")
                    if str(r.get("section_lane") or "") == "full_resume":
                        errs.append("unexpected_full_resume_section_lane")

            sch = str(raw_calls.get("schema_version") or "")
            if "phase1.v2" in sch:
                rlp = raw_calls.get("recipe_lane_policy")
                if not isinstance(rlp, dict):
                    errs.append("section_calls_missing_recipe_lane_policy")
                elif str(raw_calls.get("decisive_status") or "") == "PASS" and rlp.get("fatal_lane_failures"):
                    errs.append("section_calls_PASS_with_fatal_lane_failures")

    merge_path = run_dir / "modular_r4" / "outputs" / "rg_output_merge_receipt.json"
    if not merge_path.is_file():
        errs.append("missing_modular_r4/outputs/rg_output_merge_receipt.json")
    else:
        mr = _read_json(merge_path)
        if not isinstance(mr, dict):
            errs.append("rg_output_merge_receipt_not_object")
        elif mr.get("schema_valid") is not True or mr.get("ok") is not True:
            errs.append("rg_output_merge_receipt_not_ok")

    schema_path = run_dir / "modular_r4" / "rg_output_schema_validation_receipt.json"
    if not schema_path.is_file():
        errs.append("missing_modular_r4/rg_output_schema_validation_receipt.json")
    else:
        sr = _read_json(schema_path)
        if not isinstance(sr, dict):
            errs.append("rg_output_schema_validation_receipt_not_object")
        elif sr.get("final_schema_valid") is not True:
            errs.append("final_schema_valid_not_true")

    return errs


__all__ = [
    "R4_RECORDED_MODULAR_PROOF_RUN_ID",
    "verify_recorded_modular_r4_proof_bundle",
]
