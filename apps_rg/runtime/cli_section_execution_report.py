"""Structured CLI reporting for ``python -m apps_rg --section <lane>``.

Separates CLI/runtime execution success from product disposition (X3), process exit
policy, and proof eligibility. Does not alter gates, X3 aggregation, or exit codes.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Final

from apps_rg.runtime.section_cli_defaults import (
    CLI_PROVIDER_RESOLUTION_DEV_DEFAULT_MOCK,
    CLI_PROVIDER_RESOLUTION_TEST_MOCK,
)

_CLI_SUMMARY_LINE_RE: Final[re.Pattern[str]] = re.compile(
    r"^(?P<key>[A-Z]{3,}[A-Z0-9_]*):\s*(?P<value>.+)$",
)

CLI_SECTION_EXECUTION_REPORT_FILE: Final[str] = "cli_section_execution_report.json"
_X3_DISPOSITION_REF: Final[str] = "x3_disposition.json"
_RUN_MANIFEST_REF: Final[str] = "run_manifest.json"

__all__ = [
    "CLI_SECTION_EXECUTION_REPORT_FILE",
    "build_section_cli_execution_report_lines",
    "build_section_cli_execution_report_payload",
    "emit_cli_section_execution_summary",
    "parse_cli_execution_summary_block",
    "persist_cli_section_execution_report",
    "section_lane_process_exit_code",
]


def section_lane_process_exit_code(
    *,
    result: dict[str, Any],
    allow_non_allow_exit_zero_effective: bool,
) -> int:
    """Match ``apps_rg.__main__`` section-only exit policy (no mutation of X3)."""
    if allow_non_allow_exit_zero_effective:
        return 0
    status = str(result.get("exit_status") or "unknown")
    authorized = bool(result.get("outcome_authorized"))
    if status != "success" or not authorized:
        return 1
    return 0


def _load_json(path: Path) -> dict[str, Any]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        return raw if isinstance(raw, dict) else {}
    except (OSError, json.JSONDecodeError, TypeError):
        return {}


def _cli_path_passes(*, result: dict[str, Any], artifact_dir: Path) -> bool:
    fault = str(result.get("fault") or "").strip()
    if fault == "temperature_range":
        return False
    if not artifact_dir.is_dir():
        return False
    return (artifact_dir / "x3_disposition.json").is_file() or (
        artifact_dir / "run_manifest.json"
    ).is_file()


def _product_status_value(
    *,
    cli_path_pass: bool,
    result: dict[str, Any],
    x3_loaded: dict[str, Any],
) -> str:
    """Product disposition label — prefer on-disk X3 code (never plain PASS for review runs)."""
    if not cli_path_pass:
        return "FAIL"
    code = str(x3_loaded.get("x3_code") or result.get("x3_disposition") or "").strip()
    return code if code else "UNKNOWN"


def _product_quality_status(artifact_dir: Path | None) -> str:
    if artifact_dir is None or not artifact_dir.is_dir():
        return "UNKNOWN"
    x3 = _load_json(artifact_dir / "x3_disposition.json")
    pq = x3.get("product_quality_status")
    if pq is not None and str(pq).strip():
        return str(pq).strip()
    return "UNKNOWN"


def _proof_eligible(
    artifact_dir: Path | None,
    *,
    lane_provider_resolution_source: str | None,
    outcome_authorized: bool,
) -> bool:
    if artifact_dir is None or not artifact_dir.is_dir():
        return False

    manifest = artifact_dir / "run_manifest.json"
    if manifest.is_file():
        data = _load_json(manifest)
        if "proof_eligible" in data:
            return bool(data["proof_eligible"])

    src = str(lane_provider_resolution_source or "").strip()
    if src in {CLI_PROVIDER_RESOLUTION_DEV_DEFAULT_MOCK, CLI_PROVIDER_RESOLUTION_TEST_MOCK}:
        return False

    x3 = _load_json(artifact_dir / "x3_disposition.json")
    x2_failed = x3.get("x2_failed_gates")
    if isinstance(x2_failed, list) and len(x2_failed) > 0:
        return False
    if not outcome_authorized:
        return False
    return True


def _expected_nonzero_exit(
    *,
    outcome_authorized: bool,
    allow_non_allow_exit_zero_effective: bool,
) -> bool:
    return (not outcome_authorized) and (not allow_non_allow_exit_zero_effective)


def build_section_cli_execution_report_payload(
    *,
    result: dict[str, Any],
    lane_provider_resolution_source: str | None,
    allow_non_allow_exit_zero_effective: bool,
    process_exit_code: int,
    allow_non_allow_cli_flag: bool = False,
) -> dict[str, Any]:
    """Single source of truth for stdout lines and ``cli_section_execution_report.json``."""
    ad_raw = str(result.get("artifact_dir") or "").strip()
    artifact_dir: Path | None = Path(ad_raw).resolve() if ad_raw else None
    cli_path_pass = artifact_dir is not None and _cli_path_passes(
        result=result,
        artifact_dir=artifact_dir,
    )
    cli_path = "PASS" if cli_path_pass else "FAIL"

    outcome_authorized = bool(result.get("outcome_authorized"))

    manifest_loaded: dict[str, Any] = {}
    readiness_loaded: dict[str, Any] = {}
    clean_rr = ""

    if artifact_dir is not None and artifact_dir.is_dir():
        manifest_loaded = _load_json(artifact_dir / "run_manifest.json")
        p_ready = artifact_dir / "clean_x3_allow_readiness.json"
        if p_ready.is_file():
            readiness_loaded = _load_json(p_ready)
            clean_rr = "clean_x3_allow_readiness.json"

    x3_loaded: dict[str, Any] = {}
    if artifact_dir is not None and artifact_dir.is_dir() and cli_path_pass:
        x3_loaded = _load_json(artifact_dir / "x3_disposition.json")

    product_status = _product_status_value(cli_path_pass=cli_path_pass, result=result, x3_loaded=x3_loaded)

    pq = _product_quality_status(artifact_dir) if cli_path_pass else "UNKNOWN"
    proof_eligible = _proof_eligible(
        artifact_dir,
        lane_provider_resolution_source=lane_provider_resolution_source,
        outcome_authorized=outcome_authorized,
    )

    expected_nz = _expected_nonzero_exit(
        outcome_authorized=outcome_authorized,
        allow_non_allow_exit_zero_effective=allow_non_allow_exit_zero_effective,
    )

    l2_present = artifact_dir is not None and (artifact_dir / "l2_output.json").is_file()
    readiness_present = artifact_dir is not None and (artifact_dir / "clean_x3_allow_readiness.json").is_file()

    proof_scope_loaded = ""
    manifest_ps = manifest_loaded.get("proof_scope")
    readiness_ps = readiness_loaded.get("proof_scope")
    if isinstance(manifest_ps, str) and manifest_ps.strip():
        proof_scope_loaded = manifest_ps.strip()
    elif isinstance(readiness_ps, str) and readiness_ps.strip():
        proof_scope_loaded = readiness_ps.strip()

    decisive_label = ""
    mf_dec = manifest_loaded.get("decisive_accounting_label")
    if isinstance(mf_dec, str) and mf_dec.strip():
        decisive_label = mf_dec.strip()

    gc = manifest_loaded.get("generation_class")
    jc = manifest_loaded.get("judge_class")
    pc_class = manifest_loaded.get("proof_class")
    cc_class = manifest_loaded.get("certification_class")

    generation_class_o = gc if isinstance(gc, str) and gc.strip() else "unknown"
    judge_class_o = jc if isinstance(jc, str) and jc.strip() else "unknown"
    proof_class_o = pc_class if isinstance(pc_class, str) and pc_class.strip() else "unknown"
    certification_class_o = cc_class if isinstance(cc_class, str) and cc_class.strip() else "unknown"

    x3_code_s = str(x3_loaded.get("x3_code") or "") if x3_loaded else ""

    command_execution_status = "PASS" if cli_path_pass else "FAIL"
    command_status = command_execution_status

    lane_section = str(manifest_loaded.get("section_id") or "").strip().lower()
    ibm_reads_readiness = lane_section == "ibm_narrative"
    core_artifacts_ok = bool(cli_path_pass and l2_present)
    artifact_collection_status = (
        "PASS"
        if core_artifacts_ok and (readiness_present or not ibm_reads_readiness)
        else ("FAIL" if artifact_dir is not None and artifact_dir.is_dir() else "UNKNOWN")
    )
    product_x3_status = x3_code_s if x3_code_s else "UNKNOWN"

    authorized_x3_allow = outcome_authorized and x3_code_s == "X3_ALLOW"
    if authorized_x3_allow:
        runtime_authorization_status = "AUTHORIZED_PRODUCT_X3_ALLOW"
    elif x3_code_s == "X3_BLOCK":
        runtime_authorization_status = "BLOCKED"
    elif x3_code_s.startswith("X3_REVIEW"):
        runtime_authorization_status = "REVIEW"
    elif x3_loaded:
        runtime_authorization_status = "UNKNOWN"
    else:
        runtime_authorization_status = "UNKNOWN"

    product_authorized_mf = manifest_loaded.get("product_authorized")
    product_auth_out = (
        bool(product_authorized_mf) if isinstance(product_authorized_mf, bool) else outcome_authorized
    )

    if isinstance(manifest_loaded.get("shell_exit_overridden_for_inspection"), bool):
        shell_exit_overridden_eff = bool(manifest_loaded.get("shell_exit_overridden_for_inspection"))
    else:
        shell_exit_overridden_eff = bool(allow_non_allow_cli_flag)

    inspection_exit_override_used = bool(allow_non_allow_exit_zero_effective)

    mock_note = ""
    if bool(manifest_loaded.get("test_only_mock_judges")) or str(
        manifest_loaded.get("x1d_runtime_status") or ""
    ).upper() == "MOCKED":
        mock_note = "Mocked judges cannot satisfy clean X3 ALLOW."

    proof_status_val = manifest_loaded.get("proof_status")
    proof_status = (
        str(proof_status_val).strip()
        if isinstance(proof_status_val, str) and str(proof_status_val).strip()
        else ("PROOF_ELIGIBLE" if proof_eligible else "NOT_PROOF_ELIGIBLE")
    )

    if not cli_path_pass:
        composite_status = "COMMAND_FAIL"
    elif proof_eligible and outcome_authorized and x3_code_s == "X3_ALLOW":
        composite_status = "COMMAND_PASS_PROOF_ELIGIBLE_ALLOW"
    elif outcome_authorized:
        composite_status = "COMMAND_PASS_OUTCOME_AUTHORIZED_NON_PROOF"
    else:
        composite_status = "COMMAND_PASS_PRODUCT_REVIEW_OR_BLOCK"

    runtime_generation_status_report = ""
    if isinstance(manifest_loaded.get("runtime_generation_status"), str):
        runtime_generation_status_report = manifest_loaded["runtime_generation_status"].strip()
    if (
        not runtime_generation_status_report
        and artifact_dir is not None
        and (artifact_dir / "l2_output.json").is_file()
    ):
        l2_side = _load_json(artifact_dir / "l2_output.json")
        rgs_l2 = str(l2_side.get("runtime_generation_status") or "").strip()
        if rgs_l2:
            runtime_generation_status_report = rgs_l2
    if not runtime_generation_status_report:
        runtime_generation_status_report = "unknown"

    if (
        lane_section == "headline"
        and proof_eligible
        and outcome_authorized
        and cli_path_pass
        and x3_loaded
        and x3_code_s == "X3_ALLOW"
        and bool(x3_loaded.get("pass"))
        and runtime_generation_status_report == "REAL_LLM"
        and not (x3_loaded.get("mocked_judges") or [])
        and not (x3_loaded.get("blocked_judges") or [])
        and str(manifest_loaded.get("runtime_certification") or "") == "SIGNED_OFF"
    ):
        if not decisive_label or decisive_label == "unknown":
            decisive_label = "X3_ALLOW_REAL_LLM_ALL_JUDGES_MODEL_BACKED_PASS"
        if not generation_class_o or generation_class_o == "unknown":
            generation_class_o = "REAL_LLM"
        if not judge_class_o or judge_class_o == "unknown":
            judge_class_o = "ALL_REQUIRED_MODEL_BACKED_PASS"
        if not proof_class_o or proof_class_o == "unknown":
            proof_class_o = "PROOF_ELIGIBLE"
        if not certification_class_o or certification_class_o == "unknown":
            certification_class_o = "SIGNED_OFF"

    if not cli_path_pass:
        runtime_proof_row_status = "FAIL_CLI_ARTIFACT_COLLECTION"
    elif proof_eligible:
        runtime_proof_row_status = "PASS_RUNTIME_PROOF_ELIGIBLE"
    else:
        runtime_proof_row_status = "PASS_NONCERTIFYING_RUNTIME_PROOF"

    runtime_proof_cross_surface_note = (
        "STATUS is artifact-collection vs certification eligibility (proof_eligible), not X3 ALLOW alone. "
        "PRODUCT_STATUS is X3 disposition (runtime authorization). PRODUCT_QUALITY_STATUS is deterministic X2 only. "
        "RUNTIME_GENERATION_STATUS classifies generator plumbing (run_manifest / l2_output). "
        f"Lane command surface (legacy composite): {composite_status}."
    )

    return {
        "status": runtime_proof_row_status,
        "lane_command_surface_status": composite_status,
        "runtime_generation_status_report": runtime_generation_status_report,
        "runtime_proof_cross_surface_note": runtime_proof_cross_surface_note,
        "command_status": command_status,
        "proof_status": proof_status,
        "inspection_exit_override_used": inspection_exit_override_used,
        "cli_path_status": cli_path,
        "product_status": product_status,
        "process_exit_code": int(process_exit_code),
        "expected_nonzero_exit": bool(expected_nz),
        "product_quality_status": pq,
        "x2_product_quality_status": pq,
        "x3_pass": bool(x3_loaded.get("pass")) if x3_loaded else None,
        "x3_code": str(x3_loaded.get("x3_code") or "") if x3_loaded else "",
        "x3_product_allow_pass": bool(x3_loaded.get("pass")) if x3_loaded else None,
        "authorization_scope": str(x3_loaded.get("authorization_scope") or "") if x3_loaded else "",
        "product_quality_semantics_note": (
            "product_quality_status / x2_product_quality_status mirror x3_disposition.product_quality_status "
            "(deterministic X2 gates only). x3_product_allow_pass reflects x3_disposition.pass (runtime authorization)."
        ),
        "proof_eligible": bool(proof_eligible),
        "proof_scope": proof_scope_loaded or "unknown",
        "command_execution_status": command_execution_status,
        "artifact_collection_status": artifact_collection_status,
        "product_x3_status": product_x3_status,
        "runtime_authorization_status": runtime_authorization_status,
        "decisive_accounting_label": decisive_label if decisive_label else "unknown",
        "generation_class": generation_class_o,
        "judge_class": judge_class_o,
        "proof_class": proof_class_o,
        "certification_class": certification_class_o,
        "shell_exit_overridden_for_inspection": bool(shell_exit_overridden_eff),
        "product_authorized": bool(product_auth_out),
        "x3_json_source_of_truth": True,
        "not_release_signoff": True,
        "clean_x3_allow_readiness_ref": clean_rr or None,
        "mock_judge_accounting_note": mock_note or None,
        "x3_disposition_ref": _X3_DISPOSITION_REF,
        "run_manifest_ref": _RUN_MANIFEST_REF,
    }


def _payload_to_stdout_lines(payload: dict[str, Any]) -> list[str]:
    base = [
        f"STATUS: {payload['status']}",
        f"LANE_COMMAND_SURFACE_STATUS: {payload['lane_command_surface_status']}",
        f"RUNTIME_GENERATION_STATUS: {payload['runtime_generation_status_report']}",
        f"COMMAND_STATUS: {payload['command_status']}",
        f"PROOF_STATUS: {payload['proof_status']}",
        f"INSPECTION_EXIT_OVERRIDE_USED: {str(payload['inspection_exit_override_used']).lower()}",
        f"CLI_PATH_STATUS: {payload['cli_path_status']}",
        f"PRODUCT_STATUS: {payload['product_status']}",
        f"COMMAND_EXECUTION_STATUS: {payload['command_execution_status']}",
        f"ARTIFACT_COLLECTION_STATUS: {payload['artifact_collection_status']}",
        f"PRODUCT_X3_STATUS: {payload['product_x3_status']}",
        f"RUNTIME_AUTHORIZATION_STATUS: {payload['runtime_authorization_status']}",
        f"DECISIVE_ACCOUNTING_LABEL: {payload['decisive_accounting_label']}",
        f"PROOF_SCOPE: {payload['proof_scope']}",
        f"PROOF_ELIGIBLE: {str(payload['proof_eligible']).lower()}",
        f"SHELL_EXIT_OVERRIDDEN_FOR_INSPECTION: {str(payload['shell_exit_overridden_for_inspection']).lower()}",
        f"PRODUCT_AUTHORIZED: {str(payload['product_authorized']).lower()}",
        f"X3_JSON_SOURCE_OF_TRUTH: {str(payload['x3_json_source_of_truth']).lower()}",
        f"NOT_RELEASE_SIGNOFF: {str(payload['not_release_signoff']).lower()}",
        f"GENERATION_CLASS: {payload['generation_class']}",
        f"JUDGE_CLASS: {payload['judge_class']}",
        f"PROOF_CLASS: {payload['proof_class']}",
        f"CERTIFICATION_CLASS: {payload['certification_class']}",
        f"PROCESS_EXIT_CODE: {int(payload['process_exit_code'])}",
        f"EXPECTED_NONZERO_EXIT: {str(payload['expected_nonzero_exit']).lower()}",
        f"PRODUCT_QUALITY_STATUS: {payload['product_quality_status']}",
        f"RUNTIME_PROOF_SEMANTICS_NOTE: {payload['runtime_proof_cross_surface_note']}",
    ]
    note = payload.get("mock_judge_accounting_note")
    if isinstance(note, str) and note.strip():
        base.append(f"MOCK_JUDGES_ACCOUNTING_NOTE: {note.strip()}")
    return base


def build_section_cli_execution_report_lines(
    *,
    result: dict[str, Any],
    lane_provider_resolution_source: str | None,
    allow_non_allow_exit_zero_effective: bool,
    process_exit_code: int,
    allow_non_allow_cli_flag: bool = False,
) -> list[str]:
    """Build ``KEY: value`` lines (same values as persisted JSON)."""
    payload = build_section_cli_execution_report_payload(
        result=result,
        lane_provider_resolution_source=lane_provider_resolution_source,
        allow_non_allow_exit_zero_effective=allow_non_allow_exit_zero_effective,
        process_exit_code=process_exit_code,
        allow_non_allow_cli_flag=allow_non_allow_cli_flag,
    )
    return _payload_to_stdout_lines(payload)


def persist_cli_section_execution_report(
    artifact_dir: Path | None,
    payload: dict[str, Any],
) -> None:
    """Write ``cli_section_execution_report.json`` when ``artifact_dir`` is a directory."""
    if artifact_dir is None or not artifact_dir.is_dir():
        return
    out = artifact_dir / CLI_SECTION_EXECUTION_REPORT_FILE
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def emit_cli_section_execution_summary(
    *,
    result: dict[str, Any],
    lane_provider_resolution_source: str | None,
    allow_non_allow_exit_zero_effective: bool,
    allow_non_allow_cli_flag: bool,
    process_exit_code: int,
) -> None:
    """Print the structured summary to stdout and persist JSON under the run artifact dir."""
    import sys

    payload = build_section_cli_execution_report_payload(
        result=result,
        lane_provider_resolution_source=lane_provider_resolution_source,
        allow_non_allow_exit_zero_effective=allow_non_allow_exit_zero_effective,
        process_exit_code=process_exit_code,
        allow_non_allow_cli_flag=allow_non_allow_cli_flag,
    )
    # allow_non_allow_cli_flag flows into manifest fallbacks via build_section_cli_execution_report_payload.
    ad_raw = str(result.get("artifact_dir") or "").strip()
    artifact_dir: Path | None = Path(ad_raw).resolve() if ad_raw else None
    persist_cli_section_execution_report(artifact_dir, payload)

    for ln in _payload_to_stdout_lines(payload):
        print(ln, flush=True)
    sys.stdout.flush()


def parse_cli_execution_summary_block(stdout: str) -> dict[str, str]:
    """Parse trailing ``KEY: value`` block from CLI stdout (tests / harness)."""
    out: dict[str, str] = {}
    for raw in (stdout or "").splitlines():
        line = raw.strip()
        m = _CLI_SUMMARY_LINE_RE.match(line)
        if not m:
            continue
        key = m.group("key")
        out[key] = m.group("value").strip()
    return out
