"""Bounded launcher for the pinned Anthropic partnership fresh E2E."""

from __future__ import annotations

import argparse
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

from apps_rg.runtime.e2e_baseline import (  # noqa: E402,F401
    validate_pinned_baseline as validate_pinned_baseline,
)
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
    route_key_id = str(os.environ.get("APPS_RG_ROUTE_HMAC_KEY_ID") or "").strip()
    baseline_ref = (
        args.baseline_ref.resolve()
        if args.baseline_ref.is_absolute()
        else (repo_root / args.baseline_ref).resolve()
    )
    output_root.mkdir(parents=True, exist_ok=True)
    command = build_command(output_root=output_root)
    env = dict(os.environ)
    env["APPS_RG_ENABLE_MANAGED_WORKFLOW_L0"] = "1"
    env["APPS_RG_E2E_BASELINE_REF"] = str(baseline_ref)
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
        baseline_ref=str(baseline_ref),
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
        "baseline": {
            "baseline_ref": str(baseline_ref),
            "validated_by": "canonical_child_preflight",
        },
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
