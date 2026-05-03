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

Plan: ``.windsurf/plans/adg-audit-pipeline-integration-7f2c93.md`` W2.
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
    env_note = "ADG_CERTIFICATION_MODE=1 " if certification_mode else ""
    print(f"[audit] Stage-1: {env_note}python tools/generate/generate_full_adg.py {' '.join(extra_args)}")
    import os as _os
    env = _os.environ.copy()
    if certification_mode:
        env["ADG_CERTIFICATION_MODE"] = "1"
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

    # Locate manifests.
    gen_manifest_path = _find_generation_manifest(wall_start)
    gate_manifest_path: Path | None = None
    generation_manifest: dict[str, Any] = {}
    gate_manifest: dict[str, Any] = {}
    runtime_proof_status = "view_absent"
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

    # Cross-check required gates (certification mode only).
    if certification_mode and gate_manifest:
        reasons.extend(_cross_check_required_gates(gate_manifest))

    # Runtime-proof gate.
    if require_runtime_proof and runtime_proof_status != "attested":
        reasons.append(
            f"--require-runtime-proof set but runtime_proof_status={runtime_proof_status!r}"
        )

    # Stage 2 — report, only if we have a snapshot.
    report_rc: int | None = None
    snapshot = generation_manifest.get("sqlite_path") or generation_manifest.get("snapshot_path")
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
