"""Canonical fresh E2E preflight with mandatory failure closeout."""

from __future__ import annotations

import json
import os
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from apps_rg.runtime.e2e_baseline import validate_pinned_baseline
from apps_rg.runtime.e2e_stage_ledger import E2EStageLedger

E2E_PREFLIGHT_RECEIPT_FILENAME = "e2e_preflight_receipt.json"
ROUTE_SIGNING_PREFLIGHT_GATE_ID = "APPS_RG_ROUTE_SIGNING_PREFLIGHT"


@dataclass(frozen=True, slots=True)
class FreshE2EPreflightOutcome:
    passed: bool
    exit_code: int
    receipt: dict[str, Any]
    result: dict[str, Any]
    bootstrap_receipt: dict[str, Any] | None


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write_receipt(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _redact_error(exc: BaseException, environ: Mapping[str, str]) -> str:
    text = str(exc).strip() or type(exc).__name__
    for key, raw_value in environ.items():
        key_upper = str(key).upper()
        value = str(raw_value or "")
        if (
            value
            and len(value) >= 8
            and any(marker in key_upper for marker in ("KEY", "TOKEN", "SECRET", "PASSWORD"))
        ):
            text = text.replace(value, "[REDACTED]")
    return text[:1000]


def run_fresh_e2e_preflight(
    *,
    artifact_dir: Path,
    e2e_run_id: str,
    repo_root: Path,
    baseline_ref: Path,
    environ: Mapping[str, str] | None = None,
    runtime_check: Callable[[], Any] | None = None,
    bootstrap: Callable[[], Any] | None = None,
) -> FreshE2EPreflightOutcome:
    """Run all non-retriable checks before research and close out failures in-run."""
    root = Path(artifact_dir).resolve()
    repo = Path(repo_root).resolve()
    env = environ if environ is not None else os.environ
    ledger = E2EStageLedger.create(artifact_dir=root, e2e_run_id=e2e_run_id)
    secret_present = bool(str(env.get("APPS_RG_ROUTE_HMAC_SECRET") or "").strip())
    key_id = str(env.get("APPS_RG_ROUTE_HMAC_KEY_ID") or "").strip()
    missing = []
    if not secret_present:
        missing.append("APPS_RG_ROUTE_HMAC_SECRET")
    if not key_id:
        missing.append("APPS_RG_ROUTE_HMAC_KEY_ID")
    baseline: dict[str, str] = {}
    failure_code = ""
    failure_detail = ""
    if missing:
        failure_code = "APPS_RG_ROUTE_SIGNING_CONFIGURATION_REQUIRED"
        failure_detail = "Required route-signing environment variables were absent at process ingestion."
    else:
        try:
            baseline = validate_pinned_baseline(repo, Path(baseline_ref))
        except RuntimeError as exc:
            failure_code = "PINNED_BASELINE_PREFLIGHT_FAILED"
            failure_detail = _redact_error(exc, env)
    if not failure_code and runtime_check is not None:
        try:
            runtime_check()
        except Exception as exc:  # Guardian: converted to typed preflight receipt and mandatory RCA.
            failure_code = "PRODUCTION_RUNTIME_PREFLIGHT_FAILED"
            failure_detail = _redact_error(exc, env)
    bootstrap_receipt: dict[str, Any] | None = None
    if not failure_code and bootstrap is not None:
        try:
            raw_bootstrap = bootstrap()
            bootstrap_receipt = raw_bootstrap if isinstance(raw_bootstrap, dict) else {}
            if (
                str(bootstrap_receipt.get("status") or "PASS").upper() != "PASS"
                or int(bootstrap_receipt.get("exit_code") or 0) != 0
            ):
                failure_code = "FACT_VECTOR_BOOTSTRAP_PREFLIGHT_FAILED"
                failure_detail = "Fresh E2E fact-vector bootstrap did not return a passing receipt."
        except Exception as exc:  # Guardian: converted to typed preflight receipt and mandatory RCA.
            failure_code = "FACT_VECTOR_BOOTSTRAP_PREFLIGHT_FAILED"
            failure_detail = _redact_error(exc, env)

    receipt = {
        "schema_version": "apps_rg.e2e_preflight.v1",
        "gate_id": ROUTE_SIGNING_PREFLIGHT_GATE_ID,
        "status": "BLOCKED" if failure_code else "PASS",
        "failure_code": failure_code,
        "failure_detail": failure_detail,
        "route_signing_secret_present": secret_present,
        "route_signing_key_id_present": bool(key_id),
        "route_signing_key_id": key_id,
        "missing_environment_variables": missing,
        "baseline_ref": str(Path(baseline_ref).resolve()),
        "baseline": baseline,
        "retry_policy": "NON_RETRIABLE_CONFIGURATION" if failure_code else "NOT_APPLICABLE",
        "research_attempt_count": 0,
        "generation_attempt_count": 0,
        "judge_attempt_count": 0,
        "research_artifact_dir": "NOT_REACHED:PREFLIGHT",
        "research_briefing_path": "NOT_REACHED:PREFLIGHT",
        "research_company_brief_path": "NOT_REACHED:PREFLIGHT",
        "research_envelope_path": "NOT_REACHED:PREFLIGHT",
        "apps_eval_record_ref": "NOT_REACHED:PREFLIGHT",
        "l6_shadow_bridge_ref": "NOT_REACHED:PREFLIGHT",
        "l7_audit_status": "NOT_REACHED:PREFLIGHT",
        "bootstrap_receipt": bootstrap_receipt or {},
        "created_at_utc": _utc_now(),
    }
    receipt_path = root / E2E_PREFLIGHT_RECEIPT_FILENAME
    _write_receipt(receipt_path, receipt)
    if not failure_code:
        ledger.record(
            stage_id="PREFLIGHT",
            status="PASS",
            reason_code="ALL_NON_RETRIABLE_PREFLIGHT_CHECKS_PASSED",
            output_refs={"preflight_receipt": E2E_PREFLIGHT_RECEIPT_FILENAME},
        )
        return FreshE2EPreflightOutcome(True, 0, receipt, {}, bootstrap_receipt)

    ledger.record(
        stage_id="PREFLIGHT",
        status="BLOCKED",
        reason_code=failure_code,
        output_refs={"preflight_receipt": E2E_PREFLIGHT_RECEIPT_FILENAME},
    )
    operational_failure = {
        "stage_id": "PREFLIGHT",
        "gate_id": ROUTE_SIGNING_PREFLIGHT_GATE_ID,
        "failure_code": failure_code,
        "failure_detail": failure_detail,
        "missing_environment_variables": missing,
        "preflight_receipt": str(receipt_path),
        "baseline_ref": str(Path(baseline_ref).resolve()),
        "retry_policy": receipt["retry_policy"],
        "research_attempt_count": 0,
        "generation_attempt_count": 0,
        "judge_attempt_count": 0,
        "research_artifact_dir": "NOT_REACHED:PREFLIGHT",
        "research_briefing_path": "NOT_REACHED:PREFLIGHT",
        "research_company_brief_path": "NOT_REACHED:PREFLIGHT",
        "research_envelope_path": "NOT_REACHED:PREFLIGHT",
        "apps_eval_record_ref": "NOT_REACHED:PREFLIGHT",
        "l6_shadow_bridge_ref": "NOT_REACHED:PREFLIGHT",
        "l7_audit_status": "NOT_REACHED:PREFLIGHT",
    }
    result = {
        "exit_status": "error",
        "execution_status": "failed",
        "outcome_authorized": False,
        "x3_disposition": "PRE_RUN:PREFLIGHT",
        "completion_status": "BLOCKED",
        "completion_fault": failure_code,
        "fault": failure_code,
        "artifact_dir": str(root),
        "run_id": e2e_run_id,
        "operational_failure": operational_failure,
        "research_artifact_dir": "NOT_REACHED:PREFLIGHT",
        "research_briefing_path": "NOT_REACHED:PREFLIGHT",
        "research_company_brief_path": "NOT_REACHED:PREFLIGHT",
        "research_envelope_path": "NOT_REACHED:PREFLIGHT",
        "apps_eval_record_ref": "NOT_REACHED:PREFLIGHT",
        "l6_shadow_bridge_ref": "NOT_REACHED:PREFLIGHT",
        "l7_audit_status": "NOT_REACHED:PREFLIGHT",
    }
    from apps_rg.runtime.mandatory_run_outputs import emit_mandatory_run_outputs

    emitted = emit_mandatory_run_outputs(root, repo_root=repo, result=result)
    gate = emitted.get("mandatory_output_gate") or {}
    result.update(
        {
            "mandatory_run_output_json": str(emitted.get("json_path") or ""),
            "mandatory_run_output_md": str(emitted.get("markdown_path") or ""),
            "bcg_executive_output_md": str(emitted.get("bcg_markdown_path") or ""),
            "mandatory_output_hard_stop": gate,
        }
    )
    closeout_pass = gate.get("pass") is True
    ledger.record(
        stage_id="CLOSEOUT",
        status="PASS" if closeout_pass else "FAIL",
        reason_code=(
            "FAILED_RUN_REPORTED"
            if closeout_pass
            else str(gate.get("failure_reason") or "MANDATORY_OUTPUT_CLOSEOUT_FAILED")
        ),
        output_refs={"mandatory_run_output_json": str(emitted.get("json_path") or "")},
    )
    return FreshE2EPreflightOutcome(False, 2, receipt, result, bootstrap_receipt)


__all__ = [
    "E2E_PREFLIGHT_RECEIPT_FILENAME",
    "FreshE2EPreflightOutcome",
    "ROUTE_SIGNING_PREFLIGHT_GATE_ID",
    "run_fresh_e2e_preflight",
]
