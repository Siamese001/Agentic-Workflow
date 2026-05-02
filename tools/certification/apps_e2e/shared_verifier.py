"""Pure verifier — applies §10 fail-closed rules to one proof bundle.

Returns a list of `Violation` records. Empty list = pass. Used by the
shared pytest verifier in tests/runtime/test_apps_e2e_auditability_harness.py
so the rules live in a single SSOT and per-app tests are loops over the
spec list, not duplicated checks.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from tools.certification.apps_e2e.app_specs import AppSpec
from tools.certification.apps_e2e.hash_utils import REPO_ROOT


ALLOWED_BYPASS_REASONS: set[str] = {
    "TERMINAL_SHORTCIRCUIT", "SINGLE_STEP_ROUTE", "FALLBACK_RET",
    "NO_MANAGED_WORKFLOW_REQUIRED",
}

REQUIRED_TOP_FIELDS: tuple[str, ...] = (
    "proof_schema_version", "harness_schema_version", "app_name",
    "app_package", "entrypoint_command", "run_id", "request_id",
    "trace_root", "started_at_utc", "finished_at_utc", "exit_code",
    "git_commit", "git_dirty", "runtime_mode", "mock_mode_detected",
    "fixture_mode_detected", "synthetic_trace_detected", "success",
    "blocking_gaps", "harness_pass", "honest_fail_closed",
    "harness_run_id", "app_overlay_authority_status",
    "agentic_core_spine_status", "static_dag_ref", "static_dag_sha256",
    "runtime_route_contract_ref", "runtime_l3_receipt_ref",
    "runtime_l3_bypass_ref", "runtime_c0_receipt_ref",
    "runtime_prompt_assembly_ref", "runtime_l2_artifact_ref",
    "runtime_exit_disposition_ref", "runtime_exhaust_ref",
    "otel_or_runtime_trace_ref", "artifact_manifest_ref",
    "stage_matrix",
)


@dataclass(frozen=True)
class Violation:
    rule_id: str
    stage: str
    expected: str
    observed: str
    artifact_ref: str | None = None


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _read_json(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _required_runtime_refs(bundle: dict, spec: AppSpec) -> list[str]:
    base = [
        "runtime_route_contract_ref",
        "runtime_l1_plan_ref",
        "runtime_exit_disposition_ref",
        "runtime_exhaust_ref",
        "otel_or_runtime_trace_ref",
    ]
    # L3: route execution_form decides receipt vs bypass
    route_ref = bundle.get("runtime_route_contract_ref")
    if route_ref and (REPO_ROOT / route_ref).exists():
        rd = _read_json(REPO_ROOT / route_ref) or {}
        if rd.get("execution_form") == "MANAGED_WORKFLOW":
            base.append("runtime_l3_receipt_ref")
        else:
            base.append("runtime_l3_bypass_ref")
    if spec.expects_c0_grounding:
        base.append("runtime_c0_receipt_ref")
    if spec.expects_prompt_assembly:
        base.append("runtime_prompt_assembly_ref")
    if spec.expects_l2_execution:
        base.append("runtime_l2_artifact_ref")
    if spec.expects_durable_mutation:
        base.append("runtime_uwg_receipt_ref")
    return base


def verify_bundle(bundle: dict, spec: AppSpec) -> list[Violation]:
    """Return a list of violations. Empty = pass.

    Bundles that honestly declare success=false are NOT a verifier failure;
    they are a real-world failure of the app to be on the spine. The
    verifier only fails if the bundle is INTERNALLY INCONSISTENT — claims
    success without evidence, claims hashes that don't match, etc.
    """
    v: list[Violation] = []

    # 1. Required top-level fields
    for k in REQUIRED_TOP_FIELDS:
        if k not in bundle:
            v.append(Violation(
                rule_id="bundle_missing_required_field",
                stage="schema",
                expected=f"top-level field `{k}` present",
                observed="absent",
            ))

    # 2. App identity sanity
    if bundle.get("app_name") != spec.app_name:
        v.append(Violation(
            rule_id="app_name_mismatch", stage="schema",
            expected=spec.app_name, observed=str(bundle.get("app_name")),
        ))
    if not bundle.get("entrypoint_command", "").startswith(f"python -m {spec.app_package}"):
        v.append(Violation(
            rule_id="entrypoint_command_invalid", stage="schema",
            expected=f"python -m {spec.app_package}",
            observed=str(bundle.get("entrypoint_command")),
        ))

    # 3. Timestamps must be ISO-UTC
    for k in ("started_at_utc", "finished_at_utc"):
        val = bundle.get(k)
        if not (isinstance(val, str) and val.endswith("Z")):
            v.append(Violation(
                rule_id="timestamp_not_iso_utc", stage="schema",
                expected="ISO-8601 UTC ending in Z", observed=repr(val),
            ))

    # 4. harness_pass MUST be True (the emitter ran)
    if not bundle.get("harness_pass"):
        v.append(Violation(
            rule_id="harness_pass_false", stage="schema",
            expected="harness_pass=True (emitter ran)",
            observed=repr(bundle.get("harness_pass")),
        ))

    # 5. Static DAG proof file resolves and hashes match
    static_ref = bundle.get("static_dag_ref")
    static_sha = bundle.get("static_dag_sha256")
    if static_ref:
        p = REPO_ROOT / static_ref
        if not p.exists():
            v.append(Violation(
                rule_id="static_dag_proof_missing_on_disk", stage="static_l3_dag",
                expected=f"file at {static_ref}", observed="absent",
                artifact_ref=static_ref,
            ))
        elif _sha256_file(p) != static_sha:
            v.append(Violation(
                rule_id="static_dag_proof_sha_mismatch", stage="static_l3_dag",
                expected=str(static_sha), observed=_sha256_file(p),
                artifact_ref=static_ref,
            ))

    # 6. run_info artifacts hash check
    run_info = bundle.get("run_info") or {}
    for rec in run_info.get("artifacts") or []:
        ref = rec.get("path")
        declared = rec.get("sha256")
        if not ref:
            continue
        p = REPO_ROOT / ref
        if not p.exists():
            v.append(Violation(
                rule_id="run_artifact_missing", stage="run_info",
                expected=f"file at {ref}", observed="absent",
                artifact_ref=ref,
            ))
            continue
        if _sha256_file(p) != declared:
            v.append(Violation(
                rule_id="run_artifact_sha_mismatch", stage="run_info",
                expected=str(declared), observed=_sha256_file(p),
                artifact_ref=ref,
            ))

    # 7. Stale artifacts
    if run_info.get("stale"):
        v.append(Violation(
            rule_id="stale_artifacts_in_run_dir", stage="run_info",
            expected="no artifacts predating run start",
            observed=f"{len(run_info['stale'])} stale items",
        ))

    # 8. blocking_gaps must be a list of strings
    bg = bundle.get("blocking_gaps")
    if not isinstance(bg, list) or any(not (isinstance(x, str) and x) for x in bg):
        v.append(Violation(
            rule_id="blocking_gaps_malformed", stage="schema",
            expected="list[str] non-empty strings",
            observed=repr(type(bg).__name__),
        ))

    # 9. ANTI-CHEAT: success=true requires every runtime ref present + hash-matching
    if bundle.get("success"):
        required = _required_runtime_refs(bundle, spec)
        run_arts = {rec["path"]: rec for rec in (run_info.get("artifacts") or [])}
        for k in required:
            ref = bundle.get(k)
            if not ref:
                v.append(Violation(
                    rule_id="success_true_missing_runtime_ref", stage=k,
                    expected="non-null ref when success=true",
                    observed="null", artifact_ref=None,
                ))
                continue
            if ref not in run_arts:
                v.append(Violation(
                    rule_id="runtime_ref_not_in_run_info", stage=k,
                    expected="ref present in run_info.artifacts",
                    observed="not listed", artifact_ref=ref,
                ))
                continue
            p = REPO_ROOT / ref
            if not p.exists():
                v.append(Violation(
                    rule_id="runtime_artifact_missing", stage=k,
                    expected=f"file at {ref}", observed="absent",
                    artifact_ref=ref,
                ))
                continue
            if _sha256_file(p) != run_arts[ref]["sha256"]:
                v.append(Violation(
                    rule_id="runtime_artifact_sha_mismatch", stage=k,
                    expected=str(run_arts[ref]["sha256"]),
                    observed=_sha256_file(p), artifact_ref=ref,
                ))

    # 10. Single run_id threading when success=true
    if bundle.get("success"):
        run_id = bundle.get("run_id")
        request_id = bundle.get("request_id")
        trace_root = bundle.get("trace_root")
        for k in _required_runtime_refs(bundle, spec):
            ref = bundle.get(k)
            if not ref:
                continue
            data = _read_json(REPO_ROOT / ref) or {}
            embedded_run = data.get("run_id")
            if embedded_run is not None and embedded_run != run_id:
                v.append(Violation(
                    rule_id="run_id_threading_violation", stage=k,
                    expected=f"run_id={run_id}",
                    observed=f"run_id={embedded_run}", artifact_ref=ref,
                ))
            embedded_req = data.get("request_id")
            if embedded_req is not None and embedded_req != request_id:
                v.append(Violation(
                    rule_id="request_id_threading_violation", stage=k,
                    expected=f"request_id={request_id}",
                    observed=f"request_id={embedded_req}", artifact_ref=ref,
                ))
            embedded_trace = data.get("trace_root")
            if embedded_trace is not None and embedded_trace != trace_root:
                v.append(Violation(
                    rule_id="trace_root_threading_violation", stage=k,
                    expected=f"trace_root={trace_root}",
                    observed=f"trace_root={embedded_trace}", artifact_ref=ref,
                ))

    # 11. MANAGED_WORKFLOW: runtime L3 dag_sha256 must match static
    l3_ref = bundle.get("runtime_l3_receipt_ref")
    if l3_ref and (REPO_ROOT / l3_ref).exists():
        l3 = _read_json(REPO_ROOT / l3_ref) or {}
        if l3.get("execution_form") == "MANAGED_WORKFLOW":
            static_sha_inline = (bundle.get("static_dag_proof_inline_summary") or {}).get("dag_sha256")
            if l3.get("dag_sha256") != static_sha_inline:
                v.append(Violation(
                    rule_id="managed_workflow_dag_sha_mismatch",
                    stage="L3_orchestrate_or_bypass",
                    expected=str(static_sha_inline),
                    observed=str(l3.get("dag_sha256")),
                    artifact_ref=l3_ref,
                ))

    # 12. Bypass receipt: legal reason + matching route_contract_id
    bypass_ref = bundle.get("runtime_l3_bypass_ref")
    route_ref = bundle.get("runtime_route_contract_ref")
    if bypass_ref and (REPO_ROOT / bypass_ref).exists():
        bp = _read_json(REPO_ROOT / bypass_ref) or {}
        if bp.get("l3_bypass_reason") not in ALLOWED_BYPASS_REASONS:
            v.append(Violation(
                rule_id="l3_bypass_reason_not_allowed",
                stage="L3_orchestrate_or_bypass",
                expected=str(ALLOWED_BYPASS_REASONS),
                observed=str(bp.get("l3_bypass_reason")),
                artifact_ref=bypass_ref,
            ))
        if route_ref and (REPO_ROOT / route_ref).exists():
            rt = _read_json(REPO_ROOT / route_ref) or {}
            if bp.get("route_contract_id") != rt.get("route_contract_id"):
                v.append(Violation(
                    rule_id="bypass_route_contract_id_mismatch",
                    stage="L3_orchestrate_or_bypass",
                    expected=str(rt.get("route_contract_id")),
                    observed=str(bp.get("route_contract_id")),
                    artifact_ref=bypass_ref,
                ))

    # 13. Synthetic trace flag must propagate to blocking_gaps
    if bundle.get("synthetic_trace_detected") and bundle.get("success"):
        v.append(Violation(
            rule_id="synthetic_trace_with_success_true",
            stage="otel_or_runtime_trace",
            expected="success=false when synthetic_trace_detected=true",
            observed="success=true",
        ))

    # 14. Exactly one Exit X3 disposition
    exit_ref = bundle.get("runtime_exit_disposition_ref")
    if exit_ref and (REPO_ROOT / exit_ref).exists():
        ed = _read_json(REPO_ROOT / exit_ref) or {}
        if ed.get("x3_disposition") not in {"EXIT_OK", "EXIT_PARTIAL", "EXIT_FAIL", "EXIT_ROLLBACK"}:
            v.append(Violation(
                rule_id="exit_disposition_invalid", stage="Exit_X3",
                expected="one of EXIT_OK/PARTIAL/FAIL/ROLLBACK",
                observed=str(ed.get("x3_disposition")),
                artifact_ref=exit_ref,
            ))

    # 15. L6 exhaust must reference Exit and be observed AFTER it
    exhaust_ref = bundle.get("runtime_exhaust_ref")
    if exhaust_ref and exit_ref and \
       (REPO_ROOT / exhaust_ref).exists() and (REPO_ROOT / exit_ref).exists():
        ex = _read_json(REPO_ROOT / exhaust_ref) or {}
        ed = _read_json(REPO_ROOT / exit_ref) or {}
        if ex.get("exit_review_packet_id") != ed.get("exit_review_packet_id"):
            v.append(Violation(
                rule_id="l6_exhaust_exit_id_mismatch", stage="L6_exhaust",
                expected=str(ed.get("exit_review_packet_id")),
                observed=str(ex.get("exit_review_packet_id")),
                artifact_ref=exhaust_ref,
            ))
        ts_after = ex.get("observed_after_exit_at_utc")
        ts_emit = ed.get("emitted_at_utc")
        if ts_after and ts_emit and ts_after < ts_emit:
            v.append(Violation(
                rule_id="l6_observed_before_exit", stage="L6_exhaust",
                expected=f"observed_after >= emitted_at ({ts_emit})",
                observed=str(ts_after), artifact_ref=exhaust_ref,
            ))

    # 16. App overlay invariant — must not have authority-violation status
    if bundle.get("app_overlay_authority_status") == "overlay_violated" and bundle.get("success"):
        v.append(Violation(
            rule_id="overlay_violated_with_success", stage="overlay",
            expected="overlay_respected when success=true",
            observed="overlay_violated",
        ))

    return v


def format_violation(viol: Violation) -> str:
    parts = [f"[{viol.rule_id}] stage={viol.stage}"]
    parts.append(f"expected={viol.expected}")
    parts.append(f"observed={viol.observed}")
    if viol.artifact_ref:
        parts.append(f"artifact={viol.artifact_ref}")
    return " | ".join(parts)


__all__ = [
    "ALLOWED_BYPASS_REASONS",
    "REQUIRED_TOP_FIELDS",
    "Violation",
    "verify_bundle",
    "format_violation",
]
