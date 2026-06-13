"""ADG audit pipeline wrapper — the two-stage certification entrypoint.

Stage 1: ``tools/generate/generate_full_adg.py`` — produces the snapshot,
runs preflight/validation/post-ADG gates, emits the gate invocation +
generation manifests.

Stage 2: ``tools/adg/three_bucket_gap_report.py`` — runs the seven-class
reconciliation against the exact snapshot path declared by Stage 1's
generation manifest.

The wrapper is the fail-closed consumer: it reads the manifests, cross-
checks against the required-gate registry, enforces runtime-proof when
requested, and propagates a single aggregate exit code.

Plan: ``docs/archive/windsurf/legacy-tree/plans/adg-audit-pipeline-integration-7f2c93.md`` W2.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
ARTIFACTS_ADG = REPO_ROOT / "artifacts" / "adg"
RECEIPT_PATH = REPO_ROOT / "docs" / "reports" / "adg" / "AUDIT_PIPELINE_RECEIPT.json"


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass
class WrapperResult:
    certification_status: str
    generator_exit_code: int | None
    report_exit_code: int | None
    generation_manifest_path: Path | None
    gate_manifest_path: Path | None
    runtime_proof_status: str
    reasons: list[str]

    @property
    def ok(self) -> bool:
        return self.certification_status == "clean"


def _find_generation_manifest(since_monotonic_start: float) -> Path | None:
    """Return the newest generation manifest created during this run.

    We filter by mtime strictly greater than ``wall_start`` to avoid
    picking up a stale manifest from a prior run. ``latest.json`` is
    NEVER consulted from CI — CI resolves by timestamped filename.
    """
    candidates = sorted(
        ARTIFACTS_ADG.glob("adg_generation_manifest_*.json"),
        key=lambda p: p.stat().st_mtime,
    )
    candidates = [p for p in candidates if p.name != "adg_generation_manifest_latest.json"]
    if not candidates:
        return None
    newest = candidates[-1]
    # We accept any manifest produced during or after the wrapper-start
    # wall clock — with a 2s fudge for clock skew on shared CI runners.
    if newest.stat().st_mtime + 2 < since_monotonic_start:
        return None
    return newest


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _is_generator_run_stamp(value: str) -> bool:
    try:
        datetime.strptime(value, "%m%d%Y_%H%M")
    except ValueError:
        return False
    return True


def _stamp_from_artifact_name(path: Path | None, *, prefix: str, suffix: str) -> str | None:
    if path is None:
        return None
    name = path.name
    if not name.startswith(prefix) or not name.endswith(suffix):
        return None
    stamp = name[len(prefix):-len(suffix)]
    return stamp if _is_generator_run_stamp(stamp) else None


def _derive_adg_run_stamp(
    generation_manifest: dict[str, Any],
    generation_manifest_path: Path | None,
    snapshot_path: Path | None,
) -> str | None:
    manifest_stamp = _stamp_from_artifact_name(
        generation_manifest_path,
        prefix="adg_generation_manifest_",
        suffix=".json",
    )
    if manifest_stamp:
        return manifest_stamp

    snapshot_stamp = _stamp_from_artifact_name(
        snapshot_path,
        prefix="adg_indexed_",
        suffix=".sqlite",
    )
    if snapshot_stamp:
        return snapshot_stamp

    for key in ("sqlite_path", "snapshot_path"):
        raw = generation_manifest.get(key)
        if isinstance(raw, str) and raw:
            snapshot_stamp = _stamp_from_artifact_name(
                Path(raw),
                prefix="adg_indexed_",
                suffix=".sqlite",
            )
            if snapshot_stamp:
                return snapshot_stamp

    return None


def _append_manifest_gate_record(
    gate_manifest_path: Path,
    *,
    name: str,
    status: str,
    exit_code: int,
    message: str,
) -> None:
    try:
        data = _load_json(gate_manifest_path)
    except (OSError, json.JSONDecodeError):
        return
    gates = data.setdefault("gates", [])
    gates.append(
        {
            "name": name,
            "phase": "post-ADG-subprocess",
            "kind": "subprocess",
            "blocking_mode": "hard_fail",
            "status": status,
            "exit_code": exit_code,
            "duration_s": None,
            "started_at_utc": _utcnow_iso(),
            "finished_at_utc": _utcnow_iso(),
            "script_rel": "ops_scripts/ci/run_adg_three_graph_tests.py",
            "message": message,
        }
    )
    gate_manifest_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _run_certification_plane2(
    *,
    gate_manifest_path: Path | None,
    snapshot: Path,
) -> list[str]:
    from tools.generate.integration.certification_plane2 import run_plane2_manifest_quick  # noqa: PLC0415

    reasons: list[str] = []
    rc, _rollup = run_plane2_manifest_quick(sqlite_path=snapshot, suite="quick", strict=True)
    status = "pass" if rc == 0 else "fail"
    if gate_manifest_path and gate_manifest_path.is_file():
        _append_manifest_gate_record(
            gate_manifest_path,
            name="three_bucket_manifest_quick",
            status=status,
            exit_code=rc,
            message=f"suite=quick strict=1 exit={rc}",
        )
    if rc != 0:
        reasons.append(f"three_bucket_manifest_quick exit_code={rc}")
    return reasons


def _cross_check_required_gates(gate_manifest: dict[str, Any]) -> list[str]:
    """Return list of reason strings for any required gate missing or skipped."""
    from tools.generate._required_gates import required_gate_names

    required = required_gate_names()
    recorded = {g["name"]: g for g in gate_manifest.get("gates", [])}
    reasons: list[str] = []
    for name in sorted(required):
        rec = recorded.get(name)
        if rec is None:
            reasons.append(f"required gate '{name}' absent from manifest")
            continue
        status = rec.get("status")
        if status in ("missing_script", "skipped"):
            reasons.append(f"required gate '{name}' status={status}")
        elif status in ("fail", "timed_out"):
            reasons.append(f"required gate '{name}' status={status}")
    return reasons


def _run_generator(
    *,
    extra_args: list[str],
    timeout_s: int,
    certification_mode: bool,
) -> int:
    import os as _os

    env = _os.environ.copy()
    if certification_mode:
        env["ADG_CERTIFICATION_MODE"] = "1"
        # Plane-2 manifest runs in GHA / contract gates after Stage-1 (avoid duplicate).
        env["ADG_SKIP_PLANE2_MANIFEST"] = "1"
        # ADR-079: three-bucket stays off the default regen hot path, but CI
        # certification must populate v_runtime_proof + registry + gap JSON.
        env.setdefault("ADG_THREE_BUCKET", "1")
        env.setdefault("ADG_THREE_BUCKET_SIGN", "1")
    env_bits = []
    if certification_mode:
        env_bits.append("ADG_CERTIFICATION_MODE=1")
    if env.get("ADG_THREE_BUCKET", "").strip().lower() in ("1", "true", "yes"):
        env_bits.append("ADG_THREE_BUCKET=1")
    if env.get("ADG_THREE_BUCKET_SIGN", "").strip().lower() in ("1", "true", "yes"):
        env_bits.append("ADG_THREE_BUCKET_SIGN=1")
    env_note = " ".join(env_bits) + (" " if env_bits else "")
    print(f"[audit] Stage-1: {env_note}python tools/generate/generate_full_adg.py {' '.join(extra_args)}")
    try:
        proc = subprocess.run(  # noqa: S603
            [sys.executable, str(REPO_ROOT / "tools" / "generate" / "generate_full_adg.py"), *extra_args],
            cwd=str(REPO_ROOT),
            timeout=timeout_s,
            env=env,
            shell=False,
            check=False,
        )
    except subprocess.TimeoutExpired:
        print(f"[audit] Stage-1 FAIL — timed out after {timeout_s}s", file=sys.stderr)
        return 124
    return proc.returncode


def _run_report(
    *,
    snapshot: Path,
    fmt: str,
    require_runtime_proof: bool,
    timeout_s: int,
) -> int:
    args = [
        sys.executable,
        str(REPO_ROOT / "tools" / "adg" / "three_bucket_gap_report.py"),
        "--snapshot", str(snapshot),
        "--format", fmt,
    ]
    if require_runtime_proof:
        args.append("--require-runtime-proof")
    print(f"[audit] Stage-2: {' '.join(args[1:])}")
    try:
        proc = subprocess.run(  # noqa: S603
            args,
            cwd=str(REPO_ROOT),
            timeout=timeout_s,
            shell=False,
            check=False,
        )
    except subprocess.TimeoutExpired:
        print(f"[audit] Stage-2 FAIL — timed out after {timeout_s}s", file=sys.stderr)
        return 124
    return proc.returncode


def _write_receipt(result: WrapperResult) -> None:
    RECEIPT_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "timestamp": _utcnow_iso(),
        "certification_status": result.certification_status,
        "generator_exit_code": result.generator_exit_code,
        "report_exit_code": result.report_exit_code,
        "runtime_proof_status": result.runtime_proof_status,
        "generation_manifest_path": (
            str(result.generation_manifest_path) if result.generation_manifest_path else None
        ),
        "gate_manifest_path": (
            str(result.gate_manifest_path) if result.gate_manifest_path else None
        ),
        "reasons": result.reasons,
    }
    RECEIPT_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    try:
        display = RECEIPT_PATH.relative_to(REPO_ROOT)
    except ValueError:
        display = RECEIPT_PATH
    print(f"[audit] wrote receipt: {display}")


def run_audit(
    *,
    mode: str = "certification",
    fmt: str = "both",
    require_runtime_proof: bool = False,
    diagnostic_allow_failed_generator: bool = False,
    continue_on_p0: bool = False,
    generator_timeout_s: int = 1800,
    report_timeout_s: int = 300,
    generator_extra_args: list[str] | None = None,
) -> WrapperResult:
    """Run the audit pipeline. Pure function so tests can drive it."""

    reasons: list[str] = []
    wall_start = time.time()
    ARTIFACTS_ADG.mkdir(parents=True, exist_ok=True)

    extra = list(generator_extra_args or [])
    if continue_on_p0 and "--continue-on-p0" not in extra:
        extra.append("--continue-on-p0")

    certification_mode = mode == "certification"

    # Stage 1 — generator.
    gen_rc = _run_generator(
        extra_args=extra,
        timeout_s=generator_timeout_s,
        certification_mode=certification_mode,
    )
    if gen_rc != 0:
        if certification_mode and not diagnostic_allow_failed_generator:
            reasons.append(f"generator exit_code={gen_rc}")

    # Mandatory burndown markdown (best-effort after Stage-1; full emit is in generate_full_adg).
    try:
        from tools.reports.adg_burndown_report import emit_mandatory_adg_burndown_report  # noqa: PLC0415

        _burndown_rc = emit_mandatory_adg_burndown_report(fail_closed=False)
        if _burndown_rc != 0 and certification_mode:
            reasons.append(f"burndown report emit exit_code={_burndown_rc}")
    except ImportError as _burndown_import_err:
        if certification_mode:
            reasons.append(f"burndown report module unavailable: {_burndown_import_err}")

    # Locate manifests.
    gen_manifest_path = _find_generation_manifest(wall_start)
    gate_manifest_path: Path | None = None
    generation_manifest: dict[str, Any] = {}
    gate_manifest: dict[str, Any] = {}
    runtime_proof_status = "view_absent"
    snapshot_raw: str | None = None
    if gen_manifest_path is None:
        reasons.append("generation manifest missing — generator did not emit or clock skew > 2s")
    else:
        try:
            generation_manifest = _load_json(gen_manifest_path)
            runtime_proof_status = generation_manifest.get("runtime_proof_status", "view_absent")
            gm_raw = generation_manifest.get("gate_manifest_path")
            if gm_raw:
                gate_manifest_path = Path(gm_raw)
                if gate_manifest_path.is_file():
                    gate_manifest = _load_json(gate_manifest_path)
                else:
                    reasons.append(f"gate manifest path declared but missing: {gate_manifest_path}")
        except (OSError, json.JSONDecodeError) as e:
            reasons.append(f"failed to read generation manifest: {e}")

    snapshot_raw = generation_manifest.get("sqlite_path") or generation_manifest.get("snapshot_path")

    # Plane 2 — three-graph manifest (certification; generator skips via env).
    if certification_mode and snapshot_raw and gate_manifest_path:
        snap_path = Path(snapshot_raw)
        if snap_path.is_file():
            reasons.extend(
                _run_certification_plane2(
                    gate_manifest_path=gate_manifest_path,
                    snapshot=snap_path,
                )
            )
            try:
                gate_manifest = _load_json(gate_manifest_path)
            except (OSError, json.JSONDecodeError):
                pass

    # Cross-check required gates (certification mode only).
    if certification_mode and gate_manifest:
        reasons.extend(_cross_check_required_gates(gate_manifest))

    # Plane-3 dispatcher failure (generator records + exits; double-check JSON).
    if certification_mode:
        disp_candidates = sorted(
            ARTIFACTS_ADG.glob("adg_gate_results_*.json"),
            key=lambda p: p.stat().st_mtime,
        )
        if disp_candidates:
            try:
                disp_payload = _load_json(disp_candidates[-1])
                if int(disp_payload.get("overall_exit_code", 0)) != 0:
                    reasons.append(
                        f"adg_gate_dispatcher overall_exit_code={disp_payload.get('overall_exit_code')}"
                    )
            except (OSError, json.JSONDecodeError):
                reasons.append("adg_gate_dispatcher results unreadable")

    # Runtime-proof gate.
    if require_runtime_proof and runtime_proof_status != "attested":
        reasons.append(
            f"--require-runtime-proof set but runtime_proof_status={runtime_proof_status!r}"
        )

    # Stage 2 — report, only if we have a snapshot.
    report_rc: int | None = None
    snapshot = snapshot_raw
    if snapshot:
        snap_path = Path(snapshot)
        if snap_path.is_file():
            # In certification mode with already-known runtime-proof gate failure,
            # still run the report for diagnostic value but propagate the failure.
            report_rc = _run_report(
                snapshot=snap_path,
                fmt=fmt,
                require_runtime_proof=require_runtime_proof,
                timeout_s=report_timeout_s,
            )
            if report_rc != 0:
                reasons.append(f"three_bucket_gap_report exit_code={report_rc}")
        else:
            reasons.append(f"snapshot declared but not found: {snap_path}")
    else:
        reasons.append("snapshot path absent from generation manifest")

    # ADR-081: unified enforcement report (planes 1–3 rollup).
    enforcement_path: Path | None = None
    try:
        from tools.adg.integration.enforcement_report import (  # noqa: PLC0415
            build_enforcement_report,
            write_enforcement_report,
        )

        rollup_path = REPO_ROOT / "docs" / "reports" / "adg" / "three_graph_test_rollup.json"
        disp_candidates = sorted(
            ARTIFACTS_ADG.glob("adg_gate_results_*.json"),
            key=lambda p: p.stat().st_mtime,
        )
        disp_path = disp_candidates[-1] if disp_candidates else None
        snap_path = Path(snapshot) if snapshot else None
        run_ts = _derive_adg_run_stamp(generation_manifest, gen_manifest_path, snap_path)
        report = build_enforcement_report(
            snapshot_path=snap_path if snap_path and snap_path.is_file() else None,
            gate_manifest_path=gate_manifest_path,
            three_graph_rollup_path=rollup_path if rollup_path.is_file() else None,
            dispatcher_results_path=disp_path,
            runtime_proof_status=runtime_proof_status,
            require_runtime_proof=require_runtime_proof,
            ts=run_ts,
        )
        enforcement_path = write_enforcement_report(report, ts=run_ts)
        if certification_mode and report.get("certified_rollup") == "NOT_CERTIFIED":
            reasons.append("enforcement_report certified_rollup=NOT_CERTIFIED")
    except (ImportError, OSError, TypeError, ValueError) as exc:
        if certification_mode:
            reasons.append(f"enforcement_report build failed: {exc}")

    # Classify certification_status.
    if not certification_mode:
        status = "diagnostic_only"
    elif reasons:
        status = "failed"
    else:
        status = "clean"

    result = WrapperResult(
        certification_status=status,
        generator_exit_code=gen_rc,
        report_exit_code=report_rc,
        generation_manifest_path=gen_manifest_path,
        gate_manifest_path=gate_manifest_path,
        runtime_proof_status=runtime_proof_status,
        reasons=reasons,
    )
    _write_receipt(result)
    if enforcement_path is not None:
        print(f"[audit] enforcement report: {enforcement_path}")

    # Render summary.
    print(f"[audit] certification_status={status}")
    print(f"[audit] generator_exit_code={gen_rc}  report_exit_code={report_rc}")
    print(f"[audit] runtime_proof_status={runtime_proof_status}")
    if reasons:
        print("[audit] reasons:")
        for r in reasons:
            print(f"  - {r}")
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("certification", "diagnostic"), default="certification")
    parser.add_argument("--format", choices=("json", "md", "both"), default="both")
    parser.add_argument("--require-runtime-proof", action="store_true")
    parser.add_argument("--diagnostic-allow-failed-generator", action="store_true")
    parser.add_argument("--continue-on-p0", action="store_true")
    parser.add_argument("--generator-timeout-seconds", type=int, default=1800)
    parser.add_argument("--report-timeout-seconds", type=int, default=300)
    parser.add_argument("--generator-arg", action="append", default=[],
                        help="Extra arg to pass through to generate_full_adg.py (repeatable).")
    args = parser.parse_args(argv)

    result = run_audit(
        mode=args.mode,
        fmt=args.format,
        require_runtime_proof=args.require_runtime_proof,
        diagnostic_allow_failed_generator=args.diagnostic_allow_failed_generator,
        continue_on_p0=args.continue_on_p0,
        generator_timeout_s=args.generator_timeout_seconds,
        report_timeout_s=args.report_timeout_seconds,
        generator_extra_args=args.generator_arg,
    )

    if args.mode == "diagnostic":
        # Diagnostic mode: generator failure is tolerated if flag set; otherwise propagate.
        if args.diagnostic_allow_failed_generator:
            return 0
        return 1 if (result.generator_exit_code or 0) != 0 else 0

    # Certification mode: any reason = non-zero.
    return 0 if result.ok else 1


if __name__ == "__main__":
    sys.exit(main())
