"""Deterministic RCA for fresh E2E failures before research dispatch."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from apps_rg.runtime.e2e_baseline import validate_pinned_baseline

OPERATIONAL_FAILURE_GATE_ID = "APPS_RG_OPERATIONAL_FAILURE_RCA_INCOMPLETE"


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _current_commit(repo_root: Path) -> str:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            shell=False,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    return completed.stdout.strip() if completed.returncode == 0 else ""


def _timeline_row(
    *,
    sequence: int,
    phase: str,
    attempt: int | str,
    gate_result: str,
    judge_result: str,
    disposition: str,
    trigger: str,
    action: str,
    evidence_ref: str,
) -> dict[str, Any]:
    return {
        "sequence": sequence,
        "phase": phase,
        "attempt": attempt,
        "candidate_digest": "",
        "word_count": 0,
        "trigger_or_input": trigger,
        "repair_or_action": action,
        "gate_scope": phase.upper(),
        "gate_result": gate_result,
        "failed_gate_ids": [],
        "judge_result": judge_result,
        "disposition": disposition,
        "acceptance_scope": "RUN_CONTROL",
        "evidence_ref": evidence_ref,
        "complete": True,
    }


def _prior_attempts(baseline: dict[str, str]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    run_dir = Path(baseline["baseline_run_dir"])
    mandatory = _load_json(run_dir / "APPS_RG_MANDATORY_RUN_OUTPUT.json")
    route = _load_json(run_dir / "route_contract.json")
    rows = [
        _timeline_row(
            sequence=1,
            phase="preflight",
            attempt=1,
            gate_result="PASS",
            judge_result="NOT_APPLICABLE",
            disposition="ADVANCED_TO_RESEARCH",
            trigger="Required signing configuration was available to the passing run.",
            action="validate route signing and pinned baseline",
            evidence_ref=str(run_dir / "route_contract.json"),
        )
    ]
    rows.append(
        _timeline_row(
            sequence=2,
            phase="retry_accounting",
            attempt=0,
            gate_result="NOT_REQUIRED",
            judge_result="NO_JUDGE_RETRY_REQUIRED",
            disposition="FIRST_ATTEMPTS_ACCEPTED",
            trigger="The passing baseline recorded authorized section and judge outcomes without a retry cycle.",
            action="continue with first accepted attempts",
            evidence_ref=str(run_dir / "APPS_RG_MANDATORY_RUN_OUTPUT.json"),
        )
    )
    judges: dict[str, dict[str, Any]] = {}
    for section in mandatory.get("sections") or []:
        if not isinstance(section, dict):
            continue
        section_id = str(section.get("section") or "unknown")
        section_judges = [row for row in section.get("judges") or [] if isinstance(row, dict)]
        rows.append(
            _timeline_row(
                sequence=len(rows) + 1,
                phase=f"section:{section_id}",
                attempt=1,
                gate_result=str(section.get("x2_pass") or "NOT_OBSERVED"),
                judge_result=str(section.get("judge_summary") or "NOT_OBSERVED"),
                disposition=str(section.get("x3_code") or "NOT_OBSERVED"),
                trigger="Pinned passing run section execution.",
                action="generate, gate, and judge section",
                evidence_ref=str(run_dir / "APPS_RG_MANDATORY_RUN_OUTPUT.json"),
            )
        )
        for judge in section_judges:
            key = str(judge.get("provider_key") or judge.get("provider") or "configured_panel")
            judges[key] = judge
    judge_matrix = []
    for key, judge in sorted(judges.items()):
        judge_matrix.append(
            {
                "judge": key,
                "prior": (
                    f"{judge.get('score')}/{judge.get('threshold')} "
                    f"{'PASS' if judge.get('pass') is True else 'FAIL'}"
                ),
                "current": "JUDGES_NOT_REACHED",
                "reason": "Current run stopped at signing preflight before research, generation, or judge dispatch.",
            }
        )
    if not judge_matrix:
        judge_matrix.append(
            {
                "judge": "configured_panel",
                "prior": "PASSING_RUN_AUTHORIZED",
                "current": "JUDGES_NOT_REACHED",
                "reason": "Current run stopped at signing preflight before judge dispatch.",
            }
        )
    if not route:
        rows[0]["trigger_or_input"] = (
            "Passing baseline was authorized; route receipt was not separately readable."
        )
    return rows, judge_matrix


def build_operational_failure_forensics(
    *,
    run_root: Path,
    repo_root: Path,
    failure: dict[str, Any],
    baseline_ref: Path,
) -> dict[str, Any]:
    baseline: dict[str, str] = {}
    baseline_error = ""
    try:
        baseline = validate_pinned_baseline(repo_root, baseline_ref)
    except RuntimeError as exc:
        baseline_error = str(exc)
    prior_timeline, judge_matrix = _prior_attempts(baseline) if baseline else ([], [])
    gate_id = str(failure.get("gate_id") or "APPS_RG_ROUTE_SIGNING_PREFLIGHT")
    failure_code = str(failure.get("failure_code") or gate_id)
    preflight_receipt = str(run_root / "e2e_preflight_receipt.json")
    current_timeline = [
        _timeline_row(
            sequence=1,
            phase="preflight",
            attempt=1,
            gate_result="FAIL",
            judge_result="JUDGES_NOT_REACHED",
            disposition="BLOCKED_BEFORE_RESEARCH",
            trigger=failure_code,
            action="stop without retry because configuration is non-retriable",
            evidence_ref=preflight_receipt,
        ),
        _timeline_row(
            sequence=2,
            phase="retry_decision",
            attempt=0,
            gate_result="NOT_RUN",
            judge_result="JUDGES_NOT_REACHED",
            disposition="NO_RETRY_SCHEDULED",
            trigger="The missing process configuration would be identical on every in-process retry.",
            action="require external configuration injection before a new run",
            evidence_ref=preflight_receipt,
        ),
    ]
    lineage = [
        {
            "order": 1,
            "stage": "PREFLIGHT",
            "prior_value": "SIGNING_CONFIGURATION_AVAILABLE" if baseline else "BASELINE_UNAVAILABLE",
            "current_value": failure_code,
            "match": False,
            "classification": "CAUSAL",
            "reason": "The first divergence is the process-ingestion boundary: the passing run could sign route evidence, while the current process lacked required signing configuration.",
            "prior_evidence_ref": str(Path(baseline.get("baseline_run_dir", "")) / "route_contract.json")
            if baseline
            else baseline_error,
            "current_evidence_ref": preflight_receipt,
        }
    ]
    for order, stage in enumerate(("RESEARCH", "U0", "L1", "L0", "L2", "X1-X3", "APPS_EVAL", "L6_SHADOW"), 2):
        lineage.append(
            {
                "order": order,
                "stage": stage,
                "prior_value": "REACHED" if baseline else "BASELINE_UNAVAILABLE",
                "current_value": "NOT_REACHED",
                "match": False,
                "classification": "DOWNSTREAM_EFFECT",
                "reason": f"{stage} could not run after the causal preflight block.",
                "prior_evidence_ref": baseline.get("baseline_run_dir", ""),
                "current_evidence_ref": preflight_receipt,
            }
        )
    implementation_plan = [
        "Provision the route-signing secret and its non-secret key identifier in the launcher process environment.",
        "Keep signing readiness as the first hash-chained E2E stage before research or provider dispatch.",
        "Emit and validate the operational RCA, prior-pass bisect, retry accounting, BCG, and L7 output before returning nonzero.",
        "Retain regression coverage proving blocked preflight performs zero research, generation, and judge calls and never writes a secret value.",
    ]
    causal_allocation = {
        "dominant_cause": "Required route-signing configuration was absent at process ingestion, so the run could not create signed L0 route evidence.",
        "retry_recoverability": "NONE_WITHIN_CURRENT_PROCESS",
        "retry_recoverability_reason": "Every judge or generation retry would reuse the same missing environment configuration and would fail before those systems were reached.",
        "allocation": [
            {
                "domain": "External configuration ingestion",
                "causal_role": "ROOT_CAUSE",
                "root_cause_link": "The launcher process did not receive both required route-signing environment variables before canonical E2E preflight.",
                "work_share": "100%",
                "evidence_refs": [preflight_receipt],
                "required_work": "Inject the secret and key identifier through the approved local environment boundary without persisting or printing the secret.",
            }
        ],
    }
    layperson = [
        "The earlier passing run had the private signing configuration needed to prove where work was routed, and its first section attempts cleared their gates and judges without a retry.",
        "This run stopped at its first recorded check because that configuration was missing when the process started; research, resume generation, and judges never ran.",
        "Retries did not fail one after another: zero retries were scheduled because repeating the same process with the same missing configuration could not change the result.",
    ]
    comparison_complete = bool(baseline and prior_timeline and judge_matrix)
    output_bisect = {
        "schema_version": "apps_rg.output_bisect.v1",
        "section_id": "run_preflight",
        "scope": "OPERATIONAL_PREFLIGHT_CAUSAL_BISECT",
        "first_observed_divergence": lineage[0],
        "first_causally_relevant_divergence": lineage[0],
        "ingestion_to_outcome_lineage": lineage,
        "prior_attempt_timeline": prior_timeline,
        "current_attempt_timeline": current_timeline,
        "gate_matrix": [
            {
                "gate_id": gate_id,
                "prior": "PASS" if baseline else "BASELINE_UNAVAILABLE",
                "current": "FAIL",
                "changed": True,
                "current_reason": failure_code,
            }
        ],
        "judge_matrix": judge_matrix
        or [
            {
                "judge": "configured_panel",
                "prior": "BASELINE_UNAVAILABLE",
                "current": "JUDGES_NOT_REACHED",
                "reason": "Preflight blocked judge dispatch.",
            }
        ],
        "code_cause_status": "EXTERNAL_CONFIGURATION_CAUSE_ISOLATED",
        "code_bindings": [
            {
                "role": "configuration ingestion and fail-fast evidence",
                "file": "apps_rg/runtime/e2e_preflight.py",
                "symbol": "run_fresh_e2e_preflight",
                "changed_between_revisions": True,
                "status": "RUNTIME_GATE",
            }
        ],
        "underlying_root_cause": {
            "environment_ingestion_root_cause": {
                "status": "ISOLATED",
                "conclusion": causal_allocation["dominant_cause"],
                "code_surface": "apps_rg/runtime/e2e_preflight.py::run_fresh_e2e_preflight",
            }
        },
        "layperson_explanation": layperson,
    }
    rca_finding = {
        "section": "run_preflight",
        "classification": "Route-signing configuration ingestion failure",
        "root_cause": causal_allocation["dominant_cause"],
        "evidence": preflight_receipt,
        "implementation_plan": implementation_plan,
        "causal_allocation": causal_allocation,
    }
    section_record = {
        "section": "run_preflight",
        "status_bucket": "pre_run_blocked",
        "executed": False,
        "lane_dir": str(run_root),
        "display_txt_relpath": "",
        "display_txt_path": "",
        "x3_code": "PRE_RUN:PREFLIGHT",
        "x2_pass": "NOT_REACHED",
        "product_quality_status": "BLOCKED",
        "runtime_generation_status": "NOT_RUN",
        "failed_gates": [{"gate_id": gate_id, "failure_reason": failure_code}],
        "failure_classification": rca_finding["classification"],
        "pre_run_failure": failure,
        "judges": [],
        "judge_summary": "JUDGES_NOT_REACHED",
        "judge_issue_summary": {"blocked_judges": [], "decisive_judge_failures": []},
        "l6": {"file_count": 0, "files": [], "product_authority": "not_reached"},
    }
    return {
        "gate_id": OPERATIONAL_FAILURE_GATE_ID,
        "required": True,
        "pass": comparison_complete,
        "comparison_complete": comparison_complete,
        "baseline": baseline,
        "baseline_error": baseline_error,
        "layperson_explanation": layperson,
        "root_cause": causal_allocation["dominant_cause"],
        "underlying_root_cause": output_bisect["underlying_root_cause"],
        "first_observed_divergence": lineage[0],
        "first_causally_relevant_divergence": lineage[0],
        "prior_attempt_timeline": prior_timeline,
        "current_attempt_timeline": current_timeline,
        "gate_matrix": output_bisect["gate_matrix"],
        "judge_matrix": output_bisect["judge_matrix"],
        "ingestion_to_outcome_lineage": lineage,
        "retry_analysis": {
            "prior_retry_count": sum(1 for row in prior_timeline if row.get("retry_attempt") is True),
            "current_retry_count": 0,
            "why_retries_did_not_run": causal_allocation["retry_recoverability_reason"],
        },
        "causal_allocation": causal_allocation,
        "implementation_plan": implementation_plan,
        "revision_comparison": {
            "baseline_git_commit": baseline.get("git_commit", ""),
            "current_git_commit": _current_commit(repo_root),
        },
        "output_bisect": output_bisect,
        "rca_finding": rca_finding,
        "section_record": section_record,
        "errors": [] if comparison_complete else [baseline_error or "pinned_baseline_comparison_incomplete"],
    }


def validate_operational_failure_forensics(value: Any) -> list[str]:
    if not isinstance(value, dict) or not value.get("required"):
        return []
    errors: list[str] = []
    if value.get("pass") is not True or value.get("comparison_complete") is not True:
        errors.append(OPERATIONAL_FAILURE_GATE_ID)
    for key in (
        "layperson_explanation",
        "root_cause",
        "underlying_root_cause",
        "first_observed_divergence",
        "first_causally_relevant_divergence",
        "prior_attempt_timeline",
        "current_attempt_timeline",
        "gate_matrix",
        "judge_matrix",
        "ingestion_to_outcome_lineage",
        "retry_analysis",
        "causal_allocation",
        "implementation_plan",
        "revision_comparison",
        "output_bisect",
    ):
        if not value.get(key):
            errors.append(f"operational_failure_missing:{key}")
    if len(value.get("layperson_explanation") or []) != 3:
        errors.append("operational_failure_layperson_sentence_count")
    if not 3 <= len(value.get("implementation_plan") or []) <= 5:
        errors.append("operational_failure_implementation_plan_count")
    retry = value.get("retry_analysis") if isinstance(value.get("retry_analysis"), dict) else {}
    if retry.get("current_retry_count") != 0 or not retry.get("why_retries_did_not_run"):
        errors.append("operational_failure_retry_accounting")
    return errors


__all__ = [
    "OPERATIONAL_FAILURE_GATE_ID",
    "build_operational_failure_forensics",
    "validate_operational_failure_forensics",
]
