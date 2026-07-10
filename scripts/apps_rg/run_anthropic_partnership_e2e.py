"""Bounded launcher for the pinned Anthropic partnership fresh E2E."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Sequence

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from apps_rg.runtime.e2e_stage_ledger import (  # noqa: E402
    emit_e2e_launch_receipt,
    validate_cached_e2e_completion,
)

DEFAULT_OUTPUT_ROOT = Path(
    "artifacts/apps_rg/runs/on_demand_anthropic_partnership_fresh_s2e"
)
DEFAULT_BASELINE_REF = Path(
    "apps_rg/config/e2e_baselines/anthropic_partnership.v1.json"
)
JD_REF = Path(
    "apps_rg/config/targeting/anthropic_manager_applied_ai_architecture_partnerships_jd.txt"
)
_RUN_DIR_PATTERN = re.compile(r"^FRESH_E2E_ARTIFACT_DIR\s+.*\brun_dir=(.+?)\s+route_flag=")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_pinned_baseline(repo_root: Path, baseline_ref: Path) -> dict[str, str]:
    ref = baseline_ref if baseline_ref.is_absolute() else repo_root / baseline_ref
    try:
        payload = json.loads(ref.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"PINNED_BASELINE_UNREADABLE:{ref}:{exc}") from exc
    if not isinstance(payload, dict) or payload.get("schema_version") != "apps_rg.e2e_baseline.v1":
        raise RuntimeError(f"PINNED_BASELINE_SCHEMA_INVALID:{ref}")
    run_dir_text = str(payload.get("baseline_run_dir") or "").strip()
    expected_digest = str(payload.get("mandatory_output_sha256") or "").strip().lower()
    git_commit = str(payload.get("git_commit") or "").strip().lower()
    baseline_id = str(payload.get("baseline_id") or "").strip()
    target_company = str(payload.get("target_company") or "").strip()
    target_role = str(payload.get("target_role") or "").strip()
    expected_exit = str(payload.get("expected_exit_status") or "").strip().lower()
    expected_authorized = payload.get("expected_outcome_authorized")
    expected_x3 = str(payload.get("expected_x3_disposition") or "").strip()
    if not (
        run_dir_text
        and baseline_id
        and target_company
        and target_role
        and re.fullmatch(r"[0-9a-f]{40}", git_commit)
        and re.fullmatch(r"[0-9a-f]{64}", expected_digest)
        and expected_exit == "success"
        and expected_authorized is True
        and expected_x3
    ):
        raise RuntimeError(f"PINNED_BASELINE_IDENTITY_INVALID:{ref}")
    run_dir = (repo_root / run_dir_text).resolve()
    mandatory = run_dir / "APPS_RG_MANDATORY_RUN_OUTPUT.json"
    if not mandatory.is_file():
        raise RuntimeError(f"PINNED_BASELINE_ARTIFACT_MISSING:{mandatory}")
    observed_digest = _sha256(mandatory)
    if observed_digest != expected_digest:
        raise RuntimeError(
            f"PINNED_BASELINE_DIGEST_MISMATCH:expected={expected_digest}:observed={observed_digest}"
        )
    try:
        mandatory_payload = json.loads(mandatory.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"PINNED_BASELINE_MANDATORY_INVALID:{mandatory}:{exc}") from exc
    summary = (
        mandatory_payload.get("result_summary")
        if isinstance(mandatory_payload, dict)
        and isinstance(mandatory_payload.get("result_summary"), dict)
        else {}
    )
    observed_exit = str(summary.get("exit_status") or "").lower()
    observed_authorized = summary.get("outcome_authorized") is True
    observed_x3 = str(summary.get("x3_disposition") or "")
    if not (
        observed_exit == expected_exit
        and observed_authorized is expected_authorized
        and observed_x3 == expected_x3
    ):
        raise RuntimeError(
            "PINNED_BASELINE_EXPECTATION_MISMATCH:"
            f"exit={observed_exit}:authorized={observed_authorized}:x3={observed_x3}"
        )
    return {
        "baseline_id": baseline_id,
        "baseline_ref": str(ref.resolve()),
        "baseline_run_dir": str(run_dir),
        "mandatory_output_sha256": observed_digest,
        "git_commit": git_commit,
        "target_company": target_company,
        "target_role": target_role,
    }


def extract_exact_run_dir(stdout: str, output_root: Path) -> Path:
    matches = [match.group(1).strip() for line in stdout.splitlines() if (match := _RUN_DIR_PATTERN.match(line))]
    if len(matches) != 1:
        raise RuntimeError(f"FRESH_E2E_ARTIFACT_DIR_COUNT_INVALID:{len(matches)}")
    root = output_root.resolve()
    run_dir = Path(matches[0]).resolve()
    try:
        run_dir.relative_to(root)
    except ValueError as exc:
        raise RuntimeError(f"FRESH_E2E_ARTIFACT_DIR_OUTSIDE_ROOT:{run_dir}") from exc
    if not run_dir.is_dir():
        raise RuntimeError(f"FRESH_E2E_ARTIFACT_DIR_MISSING:{run_dir}")
    return run_dir


def build_command(*, output_root: Path) -> list[str]:
    return [
        sys.executable,
        "-m",
        "apps_rg",
        "--fresh-e2e",
        "--target-company",
        "Anthropic",
        "--target-role",
        "Manager of Applied AI Architecture, Partnerships",
        "--target-level",
        "Manager",
        "--jd",
        JD_REF.as_posix(),
        "--artifact-dir",
        str(output_root),
    ]


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--baseline-ref", type=Path, default=DEFAULT_BASELINE_REF)
    parser.add_argument("--timeout-seconds", type=int, default=7200)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    repo_root = args.repo_root.resolve()
    output_root = (
        args.output_root.resolve()
        if args.output_root.is_absolute()
        else (repo_root / args.output_root).resolve()
    )
    route_secret = str(os.environ.get("APPS_RG_ROUTE_HMAC_SECRET") or "").strip()
    route_key_id = str(os.environ.get("APPS_RG_ROUTE_HMAC_KEY_ID") or "").strip()
    if not route_secret:
        raise SystemExit("APPS_RG_ROUTE_HMAC_SECRET_REQUIRED")
    if not route_key_id:
        raise SystemExit("APPS_RG_ROUTE_HMAC_KEY_ID_REQUIRED")
    baseline = validate_pinned_baseline(repo_root, args.baseline_ref)
    output_root.mkdir(parents=True, exist_ok=True)
    command = build_command(output_root=output_root)
    env = dict(os.environ)
    env["APPS_RG_ENABLE_MANAGED_WORKFLOW_L0"] = "1"
    env["APPS_RG_E2E_BASELINE_REF"] = baseline["baseline_ref"]
    try:
        completed = subprocess.run(
            command,
            cwd=repo_root,
            env=env,
            capture_output=True,
            text=True,
            shell=False,
            timeout=max(30, int(args.timeout_seconds)),
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        print(str(exc.stdout or ""), end="")
        print(str(exc.stderr or ""), end="", file=sys.stderr)
        print("E2E_LAUNCH_TIMEOUT", file=sys.stderr)
        return 124
    print(completed.stdout, end="")
    print(completed.stderr, end="", file=sys.stderr)
    try:
        run_dir = extract_exact_run_dir(completed.stdout, output_root)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    launch_path = emit_e2e_launch_receipt(
        output_root=output_root,
        run_dir=run_dir,
        e2e_run_id=run_dir.name,
        command=command,
        route_signing_key_id=route_key_id,
        baseline_ref=baseline["baseline_ref"],
    )
    completion = validate_cached_e2e_completion(
        run_dir,
        require_research_execution=True,
    )
    result_payload = {
        "schema_version": "apps_rg.e2e_launcher_result.v1",
        "run_dir": str(run_dir),
        "process_exit_code": completed.returncode,
        "launch_receipt": str(launch_path),
        "baseline": baseline,
        "completion_valid": completion.valid,
        "completion_errors": list(completion.errors),
    }
    (run_dir / "e2e_launcher_result.json").write_text(
        json.dumps(result_payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        "E2E_LAUNCH_RESULT "
        f"run_dir={run_dir} process_exit_code={completed.returncode} "
        f"completion_valid={completion.valid}",
        flush=True,
    )
    return 0 if completed.returncode == 0 and completion.valid else 2


if __name__ == "__main__":
    raise SystemExit(main())
