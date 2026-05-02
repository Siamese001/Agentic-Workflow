"""Emit one app's end-to-end proof bundle.

Executes `python -m <app>` for one AppSpec, captures real run state,
writes the static DAG proof, the proof bundle, the artifact manifest,
and the run log. All paths are SSOT-routed via tools.certification.apps_e2e.paths.

Usage:
    python -m tools.certification.apps_e2e.emit_proof_bundle --app apps_rg
    python -m tools.certification.apps_e2e.emit_proof_bundle --all
    python -m tools.certification.apps_e2e.emit_proof_bundle --app apps_qna --dry-run

Exit codes:
    0 — every requested bundle emitted (success vs honest-fail-closed
        is in the bundle's `success` field, not the exit code)
    2 — harness-level failure (subprocess crash, filesystem error, etc.)
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
import uuid
from pathlib import Path
from typing import Sequence

from tools.certification.apps_e2e.app_specs import APP_SPECS, AppSpec, find_spec
from tools.certification.apps_e2e.hash_utils import (
    REPO_ROOT, relative_to_repo, utc_now_iso, write_json,
)
from tools.certification.apps_e2e.paths import AppCertPaths
from tools.certification.apps_e2e.proof_bundle import (
    build_artifact_manifest, build_proof_bundle,
)
from tools.certification.apps_e2e.static_dag_inspector import build_static_dag_proof

SUBPROCESS_TIMEOUT_SECONDS = 900


def _run_app(spec: AppSpec, dry_run: bool) -> tuple[int, str, float, float]:
    cmd = [sys.executable, "-m", spec.app_package, *spec.entrypoint_args]
    if dry_run:
        print(f"[dry-run] would execute: {' '.join(cmd)}")
        return (0, "[dry-run] skipped", 0.0, time.time())
    print(f"[proof] running: {' '.join(cmd)}")
    start = time.time()
    try:
        result = subprocess.run(
            cmd, cwd=str(REPO_ROOT),
            capture_output=True, text=True,
            timeout=SUBPROCESS_TIMEOUT_SECONDS, shell=False, check=False,
        )
        end = time.time()
        out = (result.stdout or "") + (result.stderr or "")
        return (result.returncode, out, start, end)
    except subprocess.TimeoutExpired as exc:
        return (124, f"[TIMEOUT after {SUBPROCESS_TIMEOUT_SECONDS}s] {exc}", start, time.time())
    except (OSError, ValueError) as exc:
        return (2, f"[HARNESS_ERROR] {type(exc).__name__}: {exc}", start, time.time())


def emit_one(spec: AppSpec, *, dry_run: bool = False) -> tuple[Path, dict]:
    paths = AppCertPaths(spec.app_name)
    paths.ensure()

    # 1. Static DAG proof — always writeable, fail-closed on absence.
    dag_payload = build_static_dag_proof(
        app_name=spec.app_name, app_package=spec.app_package,
    )
    dag_digest, dag_size = write_json(paths.static_dag_proof, dag_payload)

    # 2. Run the app (or skip if non-runnable).
    harness_run_id = f"{spec.app_name}-e2e-{uuid.uuid4().hex[:16]}"
    start_iso = utc_now_iso()
    if not spec.runnable:
        exit_code = 0
        run_output = f"[skipped] {spec.app_name} is not runnable (skeleton only)"
        run_floor = time.time()
        end_iso = utc_now_iso()
    else:
        exit_code, run_output, run_floor, _end_epoch = _run_app(spec, dry_run)
        end_iso = utc_now_iso()
    paths.run_log.parent.mkdir(parents=True, exist_ok=True)
    paths.run_log.write_text(run_output, encoding="utf-8", errors="replace")

    # 3. Build the proof bundle.
    bundle = build_proof_bundle(
        spec=spec,
        harness_run_id=harness_run_id,
        exit_code=exit_code,
        start_iso=start_iso,
        end_iso=end_iso,
        run_floor_epoch=run_floor,
        run_log_ref=relative_to_repo(paths.run_log),
        static_dag_path=paths.static_dag_proof,
        static_dag_payload=dag_payload,
        proof_bundle_path=paths.proof_bundle,
        static_dag_proof_path=paths.static_dag_proof,
    )

    if not spec.runnable:
        # Override runtime_mode + drop runtime gaps for skeleton apps.
        bundle["runtime_mode"] = "skeleton_only"
        bundle["blocking_gaps"] = ["app_skeleton_only_no_entrypoint"]
        bundle["success"] = False
        bundle["honest_fail_closed"] = True
        bundle["agentic_core_spine_status"] = "spine_unverified"
        bundle["app_overlay_authority_status"] = "overlay_unknown"

    # 4. Artifact manifest (path → sha256 for every referenced ref).
    manifest = build_artifact_manifest(bundle)
    write_json(paths.artifact_manifest, manifest)
    bundle["artifact_manifest_ref"] = relative_to_repo(paths.artifact_manifest)

    # 5. Persist proof bundle.
    digest, size = write_json(paths.proof_bundle, bundle)

    print(f"[proof] {spec.app_name}: wrote {relative_to_repo(paths.proof_bundle)} ({size} B, sha256={digest[:12]}…)")
    print(f"[proof]   exit_code={exit_code}  success={bundle['success']}  gaps={len(bundle['blocking_gaps'])}")
    if bundle["blocking_gaps"]:
        for g in bundle["blocking_gaps"][:8]:
            print(f"            - {g}")
    return (paths.proof_bundle, bundle)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="emit_proof_bundle", add_help=True)
    grp = parser.add_mutually_exclusive_group(required=True)
    grp.add_argument("--app", help="apps_<name> (single)")
    grp.add_argument("--all", action="store_true", help="emit for every spec in APP_SPECS")
    parser.add_argument("--dry-run", action="store_true",
                        help="skip subprocess; emit bundle from on-disk artifacts")
    parser.add_argument("--skip-non-runnable", action="store_true",
                        help="omit AppSpecs where runnable=False")
    args = parser.parse_args(argv)

    if args.app:
        spec = find_spec(args.app)
        if not spec:
            print(f"[error] no AppSpec found for {args.app!r}", file=sys.stderr)
            return 2
        emit_one(spec, dry_run=args.dry_run)
        return 0

    # --all
    for spec in APP_SPECS:
        if args.skip_non_runnable and not spec.runnable:
            continue
        emit_one(spec, dry_run=args.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
