"""APPS-DRYRUN CI gate — verify `python -m apps_rg --dry-run` exits 0 with
minimal canonical inputs.

Per plan apps-rg-runtime-wiring-completion-d4e8a1 W6 (DoD discipline).

This gate prevents the c8b3e1 failure mode: a plan was marked Completed
without ever exercising the ingress path end-to-end. A `--dry-run` with
plausible inputs forces argparse → ingress payload construction →
AppsRgIngressPayload.__post_init__ validation. If any of those fail,
the plan is provably non-functional regardless of test counts.

Uses `APPS_RG_L2_FORCE_STUB=1` so this gate never depends on a running
Qwen vLLM container. The gate verifies the ingress + dry-run path only;
real LLM E2E is verified by W5 smoke runs, not by CI.

Exit 0 → dry-run reaches "DRY RUN: Ingress payload validated" and exits 0.
Exit 1 → dry-run failed (advisory by default, fail-closed via
APPS_RG_DRYRUN_GATE_FAIL_CLOSED=1).
Bypass: APPS_RG_DRYRUN_GATE_BYPASS=1.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_REPORT_PATH = _REPO_ROOT / "artifacts" / "ci" / "apps_rg_dryrun_gate.json"
_TIMEOUT_S = 30

# Canonical minimal-but-valid input set. These don't need to point at real
# files — `--dry-run` only validates payload construction, not file content.
_CANONICAL_ARGS: list[str] = [
    "--target-company", "CI-Probe-Co",
    "--target-role", "CI-Probe-Role",
    "--source-resume", "ci-probe-resume.json",
    "--jd", "ci-probe-jd.json",
    "--dry-run",
]


def _emit_report(status: str, exit_code: int, stdout: str, stderr: str) -> None:
    _REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    _REPORT_PATH.write_text(
        json.dumps(
            {
                "gate": "APPS-DRYRUN",
                "status": status,
                "subprocess_exit_code": exit_code,
                "stdout_tail": stdout[-2000:],
                "stderr_tail": stderr[-2000:],
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    _ = argv
    if os.environ.get("APPS_RG_DRYRUN_GATE_BYPASS", "").strip() in ("1", "true", "yes"):
        print("[APPS-DRYRUN] BYPASS — APPS_RG_DRYRUN_GATE_BYPASS=1")
        _emit_report("bypassed", 0, "", "")
        return 0

    fail_closed = os.environ.get("APPS_RG_DRYRUN_GATE_FAIL_CLOSED", "").strip() in (
        "1",
        "true",
        "yes",
    )

    env = os.environ.copy()
    env["APPS_RG_L2_FORCE_STUB"] = "1"  # never touch the network from CI

    try:
        completed = subprocess.run(
            [sys.executable, "-m", "apps_rg", *_CANONICAL_ARGS],
            cwd=_REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=_TIMEOUT_S,
            check=False,
            env=env,
        )
    except subprocess.TimeoutExpired:
        msg = f"`python -m apps_rg --dry-run ...` timed out after {_TIMEOUT_S}s"
        print(f"[APPS-DRYRUN] FAIL — {msg}")
        _emit_report("timeout", -1, "", msg)
        return 1 if fail_closed else 0
    except OSError as exc:
        msg = f"could not invoke subprocess: {exc}"
        print(f"[APPS-DRYRUN] FAIL — {msg}")
        _emit_report("subprocess_error", -1, "", str(exc))
        return 1 if fail_closed else 0

    if completed.returncode == 0 and "DRY RUN" in completed.stdout:
        print("[APPS-DRYRUN] OK — dry-run exit 0 with payload echoed")
        _emit_report("pass", 0, completed.stdout, completed.stderr)
        return 0

    if completed.returncode == 0:
        print(
            "[APPS-DRYRUN] FAIL — exit 0 but stdout missing 'DRY RUN' marker "
            "(payload validation may have been skipped)"
        )
        _emit_report("missing_marker", 0, completed.stdout, completed.stderr)
        return 1 if fail_closed else 0

    print(f"[APPS-DRYRUN] FAIL — exit {completed.returncode}")
    print(f"  stderr tail:\n{completed.stderr[-1000:]}")
    _emit_report("fail", completed.returncode, completed.stdout, completed.stderr)
    return 1 if fail_closed else 0


if __name__ == "__main__":
    sys.exit(main())
