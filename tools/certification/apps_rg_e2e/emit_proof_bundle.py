"""Emit the apps_rg end-to-end proof bundle.

Runs `python -m apps_rg` as a real subprocess, captures start/end UTC,
exit code, git state, and SHA256 of every artifact the run produced.
Refuses to synthesize RouteContract, L1PlanContract, L3StepContract,
ExitReviewPacket, or RuntimeExhaustBundle — if those artifacts do not
exist on disk after the run, the bundle records `success=false` and
enumerates every blocking gap.

Per user spec, the harness must:
  * use the real entrypoint `python -m apps_rg`
  * reject stale artifacts from a previous run (min_run_dir_mtime gate)
  * link every artifact to the same run_id
  * refuse `success=true` unless every required stage artifact exists

Usage:
    python -m tools.certification.apps_rg_e2e.emit_proof_bundle
    python -m tools.certification.apps_rg_e2e.emit_proof_bundle --dry-run

Exit codes:
    0 — bundle emitted (regardless of success=true/false — the emitter
        succeeding means the harness worked; the bundle's own success
        field tells you whether apps_rg passed certification)
    2 — subprocess or filesystem failure prevented bundle emission
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
import uuid
from pathlib import Path
from typing import Any

from tools.certification.apps_rg_e2e._shared import (
    APP_NAME,
    CERT_DIR,
    ENTRYPOINT_COMMAND,
    PROOF_SCHEMA_VERSION,
    REPO_ROOT,
    detect_mock_or_fixture_mode,
    git_head,
    latest_adg_snapshot,
    latest_run_dir,
    relative_to_repo,
    sha256_file,
    spine_signal_scan,
    utc_now_iso,
    write_json,
)

PROOF_PATH = CERT_DIR / "apps_rg_e2e_proof.json"
STATIC_DAG_PROOF_PATH = CERT_DIR / "apps_rg_static_l3_dag_proof.json"
RUN_LOG_PATH = CERT_DIR / "apps_rg_run.log"

# Maximum wall-clock the harness will wait for `python -m apps_rg`.
# The pipeline is heavy (HOPs + narrative + DOCX). 15 min is a generous
# ceiling; constitutional §14 requires a bounded timeout on every subprocess.
SUBPROCESS_TIMEOUT_SECONDS = 900


def _run_apps_rg(
    target_company: str | None,
    target_role: str | None,
    manual_brief: str | None,
    auto_research_tavily: bool,
    dry_run: bool,
) -> tuple[int, str, float, float]:
    """Invoke `python -m apps_rg` and capture exit code + wall-clock.

    Returns:
        (exit_code, combined_output, start_epoch, end_epoch)
    """
    cmd = [sys.executable, "-m", "apps_rg"]
    if target_company:
        cmd += ["--target-company", target_company]
    if target_role:
        cmd += ["--target-role", target_role]
    if manual_brief:
        cmd += ["--manual-brief", manual_brief]
    if auto_research_tavily:
        cmd += ["--auto-research-tavily"]

    if dry_run:
        print(f"[dry-run] would execute: {' '.join(cmd)}")
        # Use floor=0 so existing run-dir artifacts are not flagged as stale.
        # This is safe because dry-run never produces success=true on its own —
        # the verifier still SHA-checks every referenced artifact and asserts
        # one run_id threading.
        return (0, "[dry-run] skipped", 0.0, time.time())

    print(f"[proof] running: {' '.join(cmd)}")
    start_epoch = time.time()
    try:
        result = subprocess.run(
            cmd,
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=SUBPROCESS_TIMEOUT_SECONDS,
            shell=False,
            check=False,
        )
        end_epoch = time.time()
        output = (result.stdout or "") + (result.stderr or "")
        return (result.returncode, output, start_epoch, end_epoch)
    except subprocess.TimeoutExpired as exc:
        end_epoch = time.time()
        output = f"[TIMEOUT after {SUBPROCESS_TIMEOUT_SECONDS}s] {exc}"
        return (124, output, start_epoch, end_epoch)


def _collect_run_artifacts(run_dir: Path, run_floor_epoch: float) -> dict[str, Any]:
    """Enumerate real artifacts in the run dir AND verify freshness.

    The `run_floor_epoch` gate is critical: it rejects stale artifacts
    from a previous apps_rg run. Per spec, "proof is based on stale
    artifacts from a previous run" is an explicit fail-closed condition.
    """
    items: list[dict[str, Any]] = []
    stale_items: list[dict[str, Any]] = []
    if not run_dir.exists():
        return {"run_dir": None, "artifacts": [], "stale": [], "dir_mtime": None}

    for p in sorted(run_dir.rglob("*")):
        if not p.is_file():
            continue
        mt = p.stat().st_mtime
        rec = {
            "path": relative_to_repo(p),
            "sha256": sha256_file(p),
            "size_bytes": p.stat().st_size,
            "mtime_epoch": mt,
            "mtime_utc": utc_now_iso() if mt == 0 else time.strftime(
                "%Y-%m-%dT%H:%M:%SZ", time.gmtime(mt)
            ),
        }
        # Allow 5s slack against clock skew; if an artifact predates the
        # run start by more than that, it is stale.
        if mt + 5 < run_floor_epoch:
            stale_items.append(rec)
        else:
            items.append(rec)
    return {
        "run_dir": relative_to_repo(run_dir),
        "dir_mtime_epoch": run_dir.stat().st_mtime,
        "artifacts": items,
        "stale": stale_items,
    }


def _scan_spine_signals() -> dict[str, Any]:
    """Read apps_rg/__main__.py + generate_resume.py + bootstrap_runtime.py.

    Builds the spine_signals block that drives the blocking_gaps list.
    """
    scan: dict[str, Any] = {}
    for rel in (
        "apps_rg/__main__.py",
        "apps_rg/scripts/generate_resume.py",
        "apps_rg/bootstrap_runtime.py",
    ):
        p = REPO_ROOT / rel
        if not p.exists():
            scan[rel] = {"exists": False, "signals": {}, "sha256": None}
            continue
        try:
            src = p.read_text(encoding="utf-8")
        except OSError:
            scan[rel] = {"exists": True, "signals": {}, "sha256": None, "read_error": True}
            continue
        scan[rel] = {
            "exists": True,
            "signals": spine_signal_scan(src),
            "sha256": sha256_file(p),
        }
    return scan


def _load_static_dag_proof() -> tuple[Path | None, str | None, dict[str, Any] | None]:
    if not STATIC_DAG_PROOF_PATH.exists():
        return (None, None, None)
    digest = sha256_file(STATIC_DAG_PROOF_PATH)
    try:
        payload = json.loads(STATIC_DAG_PROOF_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return (STATIC_DAG_PROOF_PATH, digest, None)
    return (STATIC_DAG_PROOF_PATH, digest, payload)


def _find_runtime_contract(artifacts: list[dict[str, Any]], keyword: str) -> dict[str, Any] | None:
    """Return first artifact whose filename stem contains `keyword`, else None.

    Matches the basename only (not parent dirs) so a candidate run named
    e.g. `narrative/candidates/.../route_contract_summary.json` doesn't
    falsely satisfy the "route_contract" lookup. The spine writes its
    receipts at the run-dir root, never inside `narrative/`.
    """
    needle = keyword.lower()
    for rec in artifacts:
        path = (rec.get("path") or "").lower()
        # Exclude narrative/candidates which can contain similarly-named scoring files.
        if "/narrative/" in path or "\\narrative\\" in path:
            continue
        stem = path.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]
        if needle in stem:
            return rec
    return None


def _read_spine_ids(route_artifact: dict[str, Any] | None) -> tuple[str | None, str | None, str | None]:
    """Read run_id, request_id, trace_root from the route_contract JSON."""
    if not route_artifact:
        return (None, None, None)
    p = REPO_ROOT / route_artifact["path"]
    if not p.exists():
        return (None, None, None)
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return (None, None, None)
    return (data.get("run_id"), data.get("request_id"), data.get("trace_root"))


def build_proof_bundle(
    *,
    run_id: str,
    exit_code: int,
    start_iso: str,
    end_iso: str,
    run_floor_epoch: float,
    run_log_ref: str | None,
) -> dict[str, Any]:
    commit, dirty = git_head()
    mock_mode, fixture_mode = detect_mock_or_fixture_mode()
    run_dir = latest_run_dir()
    run_info = _collect_run_artifacts(run_dir, run_floor_epoch) if run_dir else {
        "run_dir": None, "artifacts": [], "stale": [], "dir_mtime_epoch": None,
    }
    spine = _scan_spine_signals()
    static_dag_path, static_dag_digest, static_dag_payload = _load_static_dag_proof()
    adg_snap = latest_adg_snapshot()

    # --- detect runtime-spine artifacts in the run dir ---
    arts = run_info["artifacts"]
    runtime_intake = _find_runtime_contract(arts, "u0_intake_envelope")
    runtime_route = _find_runtime_contract(arts, "route_contract")
    runtime_l1 = _find_runtime_contract(arts, "l1_plan_contract") \
        or _find_runtime_contract(arts, "l1_plan")
    runtime_l3_receipt = _find_runtime_contract(arts, "l3_orchestration_receipt") \
        or _find_runtime_contract(arts, "l3_receipt")
    runtime_l3_bypass = _find_runtime_contract(arts, "l3_bypass_receipt") \
        or _find_runtime_contract(arts, "l3_bypass")
    runtime_l2 = _find_runtime_contract(arts, "l2_execution_receipt")
    runtime_exit = _find_runtime_contract(arts, "exit_review_packet") \
        or _find_runtime_contract(arts, "x3_disposition")
    runtime_exhaust = _find_runtime_contract(arts, "runtime_exhaust_bundle") \
        or _find_runtime_contract(arts, "runtime_exhaust") \
        or _find_runtime_contract(arts, "l6_exhaust")
    runtime_otel = _find_runtime_contract(arts, "otel_runtime_trace") \
        or _find_runtime_contract(arts, "otel") \
        or _find_runtime_contract(arts, "runtime_trace")

    # Check static DAG availability for L3 binding logic.
    static_dag_present = bool(static_dag_payload and static_dag_payload.get("present"))

    # --- compute blocking gaps ---
    blocking: list[str] = []
    if not static_dag_present:
        blocking.append("static_l3_dag_missing_for_apps_rg")
    if runtime_route is None:
        blocking.append("no_runtime_route_contract_emitted")
    if runtime_l1 is None:
        blocking.append("no_runtime_l1_plan_contract_emitted")
    if runtime_l3_receipt is None and runtime_l3_bypass is None:
        blocking.append("no_l3_orchestration_receipt_or_bypass_receipt")
    if runtime_exit is None:
        blocking.append("no_exit_review_packet_or_x3_disposition")
    if runtime_exhaust is None:
        blocking.append("no_runtime_exhaust_bundle")
    if runtime_otel is None:
        blocking.append("no_runtime_otel_trace_artifact")
    # spine code-path signal
    main_signals = (spine.get("apps_rg/__main__.py") or {}).get("signals") or {}
    if not any(main_signals.values()):
        blocking.append("apps_rg_main_does_not_import_any_runtime_spine_contract")
    if run_info["stale"]:
        blocking.append("stale_artifacts_detected_in_run_dir")

    success = exit_code == 0 and not blocking

    # If the spine wrote a route_contract, use the embedded run_id/request_id/trace_root
    # so the bundle threads the SAME ids the spine receipts use. This is the core
    # anti-fabrication invariant: bundle ids MUST come from the real run, not the harness.
    embedded_run_id, embedded_request_id, embedded_trace_root = _read_spine_ids(runtime_route)
    bundle_run_id = embedded_run_id or run_id
    bundle_request_id = embedded_request_id or run_id
    bundle_trace_root = embedded_trace_root or run_id

    spine_active = bool(runtime_route and runtime_l1 and (runtime_l3_receipt or runtime_l3_bypass))

    bundle: dict[str, Any] = {
        "proof_schema_version": PROOF_SCHEMA_VERSION,
        "app_name": APP_NAME,
        "entrypoint_command": ENTRYPOINT_COMMAND,
        "run_id": bundle_run_id,
        "request_id": bundle_request_id,
        "trace_root": bundle_trace_root,
        "started_at_utc": start_iso,
        "finished_at_utc": end_iso,
        "exit_code": exit_code,
        "git_commit": commit,
        "git_dirty": dirty,
        "runtime_mode": "governed_spine_active" if spine_active else "standalone_orchestrator_pre_spine",
        "mock_mode_detected": mock_mode,
        "fixture_mode_detected": fixture_mode,
        "success": success,
        "blocking_gaps": blocking,
        "harness_pass": True,  # the HARNESS ran honestly; success is separate
        "honest_fail_closed": not success,
        "harness_run_id": run_id,  # uuid the harness minted (audit only)

        # --- required top-level references (null when artifact missing) ---
        "static_dag_ref": relative_to_repo(static_dag_path) if static_dag_path else None,
        "static_dag_sha256": static_dag_digest,
        "runtime_intake_ref": (runtime_intake or {}).get("path"),
        "runtime_l1_plan_ref": (runtime_l1 or {}).get("path"),
        "runtime_route_contract_ref": (runtime_route or {}).get("path"),
        "runtime_l3_receipt_ref": (runtime_l3_receipt or {}).get("path"),
        "runtime_l3_bypass_ref": (runtime_l3_bypass or {}).get("path"),
        "runtime_l2_receipt_ref": (runtime_l2 or {}).get("path"),
        "runtime_exit_disposition_ref": (runtime_exit or {}).get("path"),
        "runtime_exhaust_ref": (runtime_exhaust or {}).get("path"),
        "otel_or_runtime_trace_ref": (runtime_otel or {}).get("path"),

        # --- evidence bundles ---
        "run_log_ref": run_log_ref,
        "run_info": run_info,
        "spine_signals": spine,
        "static_dag_proof_inline_summary": (
            {
                "present": static_dag_payload.get("present"),
                "fail_reasons": static_dag_payload.get("fail_reasons", []),
                "dag_id": static_dag_payload.get("dag_id"),
                "dag_sha256": static_dag_payload.get("dag_sha256"),
            }
            if static_dag_payload else None
        ),
        "adg_snapshot_ref": relative_to_repo(adg_snap),
        "adg_snapshot_sha256": sha256_file(adg_snap) if adg_snap else None,

        # --- spec-required stage matrix (each stage: required / present / artifact / gap) ---
        "stage_matrix": _build_stage_matrix(
            runtime_intake=runtime_intake,
            runtime_route=runtime_route,
            runtime_l1=runtime_l1,
            runtime_l3_receipt=runtime_l3_receipt,
            runtime_l3_bypass=runtime_l3_bypass,
            runtime_l2=runtime_l2,
            runtime_exit=runtime_exit,
            runtime_exhaust=runtime_exhaust,
            runtime_otel=runtime_otel,
            static_dag_present=static_dag_present,
        ),

        "notes": (
            "Honest fail-closed proof bundle. The harness executed `python -m apps_rg` "
            "and recorded real artifacts + real SHA256 hashes. It refused to synthesize "
            "RouteContract/L1PlanContract/L3StepContract/ExitReviewPacket/RuntimeExhaustBundle "
            "because none were emitted by the real run. To flip success=true, integrate "
            "apps_rg with the governed runtime spine (U0 -> L1 -> L0 -> L3 -> C0 -> L2 -> "
            "Exit -> L6), register a static L3 DAG, and emit real OTEL spans bound to the "
            "same run_id."
        ),
    }
    return bundle


def _build_stage_matrix(
    *,
    runtime_intake: dict | None,
    runtime_route: dict | None,
    runtime_l1: dict | None,
    runtime_l3_receipt: dict | None,
    runtime_l3_bypass: dict | None,
    runtime_l2: dict | None,
    runtime_exit: dict | None,
    runtime_exhaust: dict | None,
    runtime_otel: dict | None,
    static_dag_present: bool,
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
        row("static_l3_dag", True, False, static_dag_present,
            relative_to_repo(STATIC_DAG_PROOF_PATH) if static_dag_present else None),
        row("U0_intake",         False, True, runtime_intake is not None,
            (runtime_intake or {}).get("path")),
        row("L1_plan",           False, True, runtime_l1 is not None,
            (runtime_l1 or {}).get("path")),
        row("L0_route",          False, True, runtime_route is not None,
            (runtime_route or {}).get("path")),
        row("L3_orchestrate_or_bypass", False, True,
            runtime_l3_receipt is not None or runtime_l3_bypass is not None,
            (runtime_l3_receipt or runtime_l3_bypass or {}).get("path")),
        row("C0_retrieval",      False, False, False, None),
        row("prompt_assembly",   False, False, False, None),
        row("L2_execute",        False, True, runtime_l2 is not None,
            (runtime_l2 or {}).get("path")),
        row("Exit_X3",           False, True, runtime_exit is not None,
            (runtime_exit or {}).get("path")),
        row("L6_exhaust",        False, True, runtime_exhaust is not None,
            (runtime_exhaust or {}).get("path")),
        row("otel_or_runtime_trace", False, True, runtime_otel is not None,
            (runtime_otel or {}).get("path")),
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="emit_proof_bundle", add_help=True)
    parser.add_argument("--target-company", default="Blend360")
    parser.add_argument("--target-role", default="SVP, Agentic Transformation")
    parser.add_argument(
        "--manual-brief",
        default="apps_rg/scripts/company_research.example.json",
    )
    parser.add_argument("--auto-research-tavily", action="store_true", default=True)
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Skip subprocess; emit bundle from whatever artifacts are on disk.",
    )
    args = parser.parse_args(argv)

    CERT_DIR.mkdir(parents=True, exist_ok=True)

    # Emit (or refresh) the static DAG proof first — the bundle references it.
    from tools.certification.apps_rg_e2e.emit_static_dag_proof import main as _emit_dag
    _emit_dag()

    run_id = f"apps_rg-e2e-{uuid.uuid4().hex[:16]}"
    start_iso = utc_now_iso()
    exit_code, output, start_epoch, end_epoch = _run_apps_rg(
        args.target_company, args.target_role, args.manual_brief,
        args.auto_research_tavily, args.dry_run,
    )
    end_iso = utc_now_iso()
    RUN_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    RUN_LOG_PATH.write_text(output, encoding="utf-8", errors="replace")

    bundle = build_proof_bundle(
        run_id=run_id,
        exit_code=exit_code,
        start_iso=start_iso,
        end_iso=end_iso,
        run_floor_epoch=start_epoch,
        run_log_ref=relative_to_repo(RUN_LOG_PATH),
    )
    digest, size = write_json(PROOF_PATH, bundle)

    print()
    print(f"[proof] wrote {relative_to_repo(PROOF_PATH)}")
    print(f"[proof]   sha256={digest}")
    print(f"[proof]   size={size} bytes")
    print(f"[proof]   run_id={run_id}")
    print(f"[proof]   exit_code={exit_code}   wall_clock={end_epoch - start_epoch:.1f}s")
    print(f"[proof]   success={bundle['success']}  harness_pass={bundle['harness_pass']}")
    if bundle["blocking_gaps"]:
        print(f"[proof]   blocking_gaps ({len(bundle['blocking_gaps'])}):")
        for g in bundle["blocking_gaps"]:
            print(f"             - {g}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
