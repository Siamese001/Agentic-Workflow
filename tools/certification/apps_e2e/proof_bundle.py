"""Proof bundle assembler — builds the AppE2EProofBundle for one app run.

Pure function `build_proof_bundle()` takes the AppSpec, runtime metadata,
and observed artifacts; produces the canonical bundle dict. It does NOT
write to disk and does NOT execute anything — wiring is in
`emit_proof_bundle.py`.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from tools.certification.apps_e2e import (
    HARNESS_SCHEMA_VERSION,
    PROOF_SCHEMA_VERSION,
)
from tools.certification.apps_e2e.app_specs import AppSpec
from tools.certification.apps_e2e.hash_utils import (
    REPO_ROOT, detect_mock_or_fixture_mode, git_head, relative_to_repo, sha256_file,
)
from tools.certification.apps_e2e.spine_signals import any_signal_fires, scan_app
from tools.certification.apps_e2e.stage_collectors import (
    collect_run_artifacts, detect_synthetic_trace, find_stage_artifact,
    latest_adg_snapshot, latest_run_dir, read_spine_ids,
)


_ALLOWED_BYPASS_REASONS: set[str] = {
    "TERMINAL_SHORTCIRCUIT", "SINGLE_STEP_ROUTE", "FALLBACK_RET",
    "NO_MANAGED_WORKFLOW_REQUIRED",
}


def _build_stage_matrix(
    *, spec: AppSpec, static_dag_present: bool,
    intake: dict | None, l1: dict | None, route: dict | None,
    l3_recv: dict | None, l3_bypass: dict | None, c0: dict | None,
    pa: dict | None, l2: dict | None, ex: dict | None,
    exhaust: dict | None, otel: dict | None, uwg: dict | None,
) -> list[dict[str, Any]]:
    def row(stage: str, static_req: bool, runtime_req: bool, present: bool, ref: str | None) -> dict[str, Any]:
        gap = None
        if (static_req or runtime_req) and not present:
            gap = f"{stage}_artifact_missing"
        return {
            "stage": stage,
            "static_required": static_req,
            "runtime_required": runtime_req,
            "present": present,
            "artifact": ref,
            "pass": present or not (static_req or runtime_req),
            "gap": gap,
        }

    return [
        row("static_l3_dag", spec.expects_static_dag, False, static_dag_present, None),
        row("U0_intake", False, True, intake is not None, (intake or {}).get("path")),
        row("L1_plan", False, True, l1 is not None, (l1 or {}).get("path")),
        row("L0_route", False, True, route is not None, (route or {}).get("path")),
        row(
            "L3_orchestrate_or_bypass", False, True,
            (l3_recv is not None) or (l3_bypass is not None),
            (l3_recv or l3_bypass or {}).get("path"),
        ),
        row(
            "C0_retrieval", False, spec.expects_c0_grounding,
            c0 is not None, (c0 or {}).get("path"),
        ),
        row(
            "prompt_assembly", False, spec.expects_prompt_assembly,
            pa is not None, (pa or {}).get("path"),
        ),
        row(
            "L2_execute", False, spec.expects_l2_execution,
            l2 is not None, (l2 or {}).get("path"),
        ),
        row("Exit_X3", False, True, ex is not None, (ex or {}).get("path")),
        row("L6_exhaust", False, True, exhaust is not None, (exhaust or {}).get("path")),
        row(
            "otel_or_runtime_trace", False, True,
            otel is not None, (otel or {}).get("path"),
        ),
        row(
            "UWG_L4_durable_write", False, spec.expects_durable_mutation,
            uwg is not None, (uwg or {}).get("path"),
        ),
    ]


def _classify_overlay(spine_scan: dict, signals_fire: bool) -> str:
    """app_overlay_authority_status — does the app respect the overlay rule?

    Heuristic: the app's __main__ must use either direct contracts or a
    governed_run adapter. If neither, the app may be acting as an
    alternate runtime — flag for review.
    """
    if signals_fire:
        return "overlay_respected"
    return "overlay_violated"


def _classify_spine(
    *, route: dict | None, l1: dict | None,
    l3_recv: dict | None, l3_bypass: dict | None, ex: dict | None,
) -> str:
    if route and l1 and (l3_recv or l3_bypass) and ex:
        return "spine_active"
    if route or l1 or l3_recv or l3_bypass:
        return "spine_partial"
    return "spine_bypassed"


def build_proof_bundle(
    *,
    spec: AppSpec,
    harness_run_id: str,
    exit_code: int,
    start_iso: str,
    end_iso: str,
    run_floor_epoch: float,
    run_log_ref: str | None,
    static_dag_path: Path | None,
    static_dag_payload: dict[str, Any] | None,
    proof_bundle_path: Path,
    static_dag_proof_path: Path,
) -> dict[str, Any]:
    commit, dirty = git_head()
    mock_mode, fixture_mode = detect_mock_or_fixture_mode(spec.app_name)
    runs_root = REPO_ROOT / "artifacts" / spec.app_name / "runs"
    run_dir = latest_run_dir(runs_root)
    run_info = collect_run_artifacts(run_dir, run_floor_epoch)
    spine_scan = scan_app(spec.app_package)
    signals_fire = any_signal_fires(spine_scan)
    adg_snap = latest_adg_snapshot()

    arts = run_info["artifacts"]
    intake = find_stage_artifact(arts, "intake")
    l1 = find_stage_artifact(arts, "l1")
    route = find_stage_artifact(arts, "route")
    l3_recv = find_stage_artifact(arts, "l3_receipt")
    l3_bypass = find_stage_artifact(arts, "l3_bypass")
    c0 = find_stage_artifact(arts, "c0")
    pa = find_stage_artifact(arts, "prompt")
    l2 = find_stage_artifact(arts, "l2")
    ex = find_stage_artifact(arts, "exit")
    exhaust = find_stage_artifact(arts, "exhaust")
    otel = find_stage_artifact(arts, "otel")
    uwg = find_stage_artifact(arts, "uwg")

    static_dag_present = bool(static_dag_payload and static_dag_payload.get("present"))
    synthetic_trace = detect_synthetic_trace(otel)

    # Compute blocking gaps (drives success boolean)
    blocking: list[str] = []
    if spec.expects_static_dag and not static_dag_present:
        blocking.append("static_l3_dag_missing")
    if route is None:
        blocking.append("no_runtime_route_contract_emitted")
    if l1 is None:
        blocking.append("no_runtime_l1_plan_contract_emitted")
    if l3_recv is None and l3_bypass is None:
        blocking.append("no_l3_orchestration_receipt_or_bypass_receipt")
    if ex is None:
        blocking.append("no_exit_review_packet_or_x3_disposition")
    if exhaust is None:
        blocking.append("no_runtime_exhaust_bundle")
    if otel is None:
        blocking.append("no_runtime_otel_trace_artifact")
    if synthetic_trace:
        blocking.append("otel_trace_contains_synthetic_spans")
    if not signals_fire:
        blocking.append(f"{spec.app_name}_does_not_import_runtime_spine_contract")
    if run_info["stale"]:
        blocking.append("stale_artifacts_detected_in_run_dir")
    if spec.expects_c0_grounding and c0 is None:
        blocking.append("c0_required_but_missing")
    if spec.expects_prompt_assembly and pa is None:
        blocking.append("prompt_assembly_required_but_missing")
    if spec.expects_l2_execution and l2 is None:
        blocking.append("l2_execution_required_but_missing")
    if spec.expects_durable_mutation and uwg is None:
        blocking.append("uwg_durable_mutation_required_but_missing")

    # Verify route_form invariant when expected
    if route is not None and l3_recv is None and l3_bypass is None:
        blocking.append("route_present_but_no_l3_receipt_or_bypass")

    success = exit_code == 0 and not blocking

    embedded_run, embedded_req, embedded_trace = read_spine_ids(route)
    bundle_run_id = embedded_run or harness_run_id
    bundle_request_id = embedded_req or harness_run_id
    bundle_trace_root = embedded_trace or harness_run_id

    spine_status = _classify_spine(
        route=route, l1=l1, l3_recv=l3_recv, l3_bypass=l3_bypass, ex=ex,
    )
    overlay_status = _classify_overlay(spine_scan, signals_fire)

    runtime_mode = "governed_spine_active" if spine_status == "spine_active" \
        else ("standalone_orchestrator_pre_spine" if spine_status != "spine_active" else "fail_closed")

    return {
        "proof_schema_version": PROOF_SCHEMA_VERSION,
        "harness_schema_version": HARNESS_SCHEMA_VERSION,
        "app_name": spec.app_name,
        "app_package": spec.app_package,
        "entrypoint_command": spec.entrypoint_command,
        "run_id": bundle_run_id,
        "request_id": bundle_request_id,
        "trace_root": bundle_trace_root,
        "started_at_utc": start_iso,
        "finished_at_utc": end_iso,
        "exit_code": exit_code,
        "git_commit": commit,
        "git_dirty": dirty,
        "runtime_mode": runtime_mode,
        "mock_mode_detected": mock_mode,
        "fixture_mode_detected": fixture_mode,
        "synthetic_trace_detected": synthetic_trace,
        "success": success,
        "blocking_gaps": blocking,
        "harness_pass": True,
        "honest_fail_closed": not success,
        "harness_run_id": harness_run_id,
        "app_overlay_authority_status": overlay_status,
        "agentic_core_spine_status": spine_status,
        "static_dag_ref": relative_to_repo(static_dag_proof_path) if static_dag_present else (
            relative_to_repo(static_dag_proof_path) if static_dag_proof_path.exists() else None
        ),
        "static_dag_sha256": sha256_file(static_dag_proof_path) if static_dag_proof_path.exists() else None,
        "runtime_intake_ref": (intake or {}).get("path"),
        "runtime_l1_plan_ref": (l1 or {}).get("path"),
        "runtime_route_contract_ref": (route or {}).get("path"),
        "runtime_l3_receipt_ref": (l3_recv or {}).get("path"),
        "runtime_l3_bypass_ref": (l3_bypass or {}).get("path"),
        "runtime_c0_receipt_ref": (c0 or {}).get("path"),
        "runtime_prompt_assembly_ref": (pa or {}).get("path"),
        "runtime_l2_artifact_ref": (l2 or {}).get("path"),
        "runtime_exit_disposition_ref": (ex or {}).get("path"),
        "runtime_exhaust_ref": (exhaust or {}).get("path"),
        "otel_or_runtime_trace_ref": (otel or {}).get("path"),
        "runtime_uwg_receipt_ref": (uwg or {}).get("path"),
        "artifact_manifest_ref": None,  # filled by caller after bundle write
        "verifier_result_ref": None,
        "run_log_ref": run_log_ref,
        "run_info": run_info,
        "spine_signals": spine_scan,
        "static_dag_proof_inline_summary": (
            {
                "present": static_dag_payload.get("present"),
                "fail_reasons": static_dag_payload.get("fail_reasons", []),
                "dag_id": static_dag_payload.get("dag_id"),
                "dag_sha256": static_dag_payload.get("dag_sha256"),
            } if static_dag_payload else None
        ),
        "adg_snapshot_ref": relative_to_repo(adg_snap),
        "adg_snapshot_sha256": sha256_file(adg_snap) if adg_snap else None,
        "stage_matrix": _build_stage_matrix(
            spec=spec, static_dag_present=static_dag_present,
            intake=intake, l1=l1, route=route,
            l3_recv=l3_recv, l3_bypass=l3_bypass,
            c0=c0, pa=pa, l2=l2, ex=ex, exhaust=exhaust,
            otel=otel, uwg=uwg,
        ),
        "notes": (
            f"Honest fail-closed proof bundle for {spec.app_name}. The harness "
            f"executed `{spec.entrypoint_command}` and recorded real artifacts + real "
            f"SHA256 hashes. It refused to synthesize spine contracts that the run did "
            f"not emit. To flip success=true, integrate {spec.app_name} with the "
            f"governed runtime spine and emit OTEL spans bound to the same run_id."
        ),
    }


def build_artifact_manifest(bundle: dict[str, Any]) -> dict[str, Any]:
    """Build the per-app manifest mapping every referenced ref to its sha256."""
    manifest: dict[str, Any] = {
        "app_name": bundle["app_name"],
        "harness_run_id": bundle["harness_run_id"],
        "run_id": bundle["run_id"],
        "trace_root": bundle["trace_root"],
        "items": [],
    }
    ref_keys = (
        "static_dag_ref", "runtime_intake_ref", "runtime_l1_plan_ref",
        "runtime_route_contract_ref", "runtime_l3_receipt_ref",
        "runtime_l3_bypass_ref", "runtime_c0_receipt_ref",
        "runtime_prompt_assembly_ref", "runtime_l2_artifact_ref",
        "runtime_exit_disposition_ref", "runtime_exhaust_ref",
        "otel_or_runtime_trace_ref", "runtime_uwg_receipt_ref",
        "run_log_ref", "adg_snapshot_ref",
    )
    for k in ref_keys:
        ref = bundle.get(k)
        if not ref:
            manifest["items"].append({"key": k, "ref": None, "sha256": None, "present": False})
            continue
        p = REPO_ROOT / ref
        manifest["items"].append({
            "key": k, "ref": ref,
            "sha256": sha256_file(p),
            "present": p.exists(),
        })
    return manifest


__all__ = ["build_proof_bundle", "build_artifact_manifest"]
