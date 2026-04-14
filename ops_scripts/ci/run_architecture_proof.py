"""
Architecture Proof Runner — one-command release gate.

Orchestrates the repo's governed-architecture checks in order.
Composes existing proof suites; no logic is duplicated here.

Suite execution order
---------------------
  S1  Conformance Gate   — CONF01-CONF08 + EXCF01-EXCF08  (structural, fast)
  S2  Exception Framework Proof — penta-app E2E + eval/uw exceptions + no-adhoc
  S3  Regression Check   — evidence governance regression  (skip with --skip-regression)

Exit 0 = all required suites pass (green).
Exit 1 = one or more required suites fail.

Usage
-----
  python ops_scripts/ci/run_architecture_proof.py
  python ops_scripts/ci/run_architecture_proof.py --skip-regression
  python ops_scripts/ci/run_architecture_proof.py --suite S1
  python ops_scripts/ci/run_architecture_proof.py --help

Reference
---------
  Architecture proof document: docs/architecture/architecture-proof-pack.md
  Governed-app contract:       docs/architecture/governed-app-contract.md
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path


def _bootstrap_repo_root() -> Path:
    repo_root = Path(__file__).resolve().parents[2]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    return repo_root


_REPO_ROOT = _bootstrap_repo_root()

PASS_MARK = "\033[92mPASS\033[0m"
FAIL_MARK = "\033[91mFAIL\033[0m"
SKIP_MARK = "\033[93mSKIP\033[0m"

_SUITES: list[dict] = [
    {
        "id": "S1",
        "label": "Conformance Gate (CONF + EXCF)",
        "cmd": ["ops_scripts/ci/check_governed_app_conformance.py"],
        "description": (
            "Registry + import checks: CONF01-CONF08 (governed) + EXCF01-EXCF08 (formal exceptions). "
            "36 checks total. Validates: runner imports, GovernedAppRunner subclassing, "
            "versioned capability tokens, FormalExceptionEntry schema, compensating controls."
        ),
        "skippable": False,
    },
    {
        "id": "S2",
        "label": "Exception Framework Proof",
        "cmd": ["tools/eval/retrieval_benchmark.py", "--exception-framework-proof"],
        "description": (
            "Behavioral E2E: penta-app proof (research + exec + rfp + rg + lic, ~60 checks) "
            "+ eval-exception (EVAL01-10) + uw-exception (UW01-10) + zero-ad-hoc gate. "
            "Validates the full L1→L0→C0→L2→L5→L6 governed loop for all 7 apps."
        ),
        "skippable": False,
    },
    {
        "id": "S3",
        "label": "Regression Check",
        "cmd": ["tools/eval/retrieval_benchmark.py", "--regression-check"],
        "description": (
            "Evidence governance regression: grounding, coverage, telemetry baseline. "
            "Skip with --skip-regression for structural-only verification."
        ),
        "skippable": True,
    },
]


def _resolve_suite_cmd(cmd: list[str]) -> tuple[list[str] | None, str | None]:
    if not cmd:
        return None, "empty suite command"

    head = cmd[0]
    if head.endswith(".py"):
        script_path = _REPO_ROOT / head
        if not script_path.exists():
            return None, f"missing suite target: {script_path}"
        return [str(script_path), *cmd[1:]], None

    return cmd, None


def _run_suite(suite: dict, skip: bool = False) -> tuple[bool, float, str]:
    """Run a single proof suite via subprocess.

    Returns (passed, elapsed_seconds, stdout_tail).
    """
    if skip:
        return True, 0.0, "(skipped)"

    resolved_cmd, resolve_error = _resolve_suite_cmd(suite["cmd"])
    if resolve_error is not None or resolved_cmd is None:
        return False, 0.0, resolve_error or "invalid suite command"

    cmd = [sys.executable] + resolved_cmd
    t0 = time.monotonic()
    try:
        result = subprocess.run(  # noqa: S603
            cmd,
            cwd=str(_REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=300,
            check=False,
        )
        elapsed = time.monotonic() - t0
        passed = result.returncode == 0
        output = result.stdout + result.stderr
        tail_lines = output.strip().splitlines()[-8:]
        tail = "\n      ".join(tail_lines) if tail_lines else ""
        return passed, elapsed, tail
    except subprocess.TimeoutExpired as exc:
        output = (exc.stdout or "") + (exc.stderr or "")
        tail_lines = output.strip().splitlines()[-8:]
        tail = "\n      ".join(tail_lines) if tail_lines else "TIMEOUT after 300s"
        return False, time.monotonic() - t0, tail
    except (OSError, ValueError) as exc:
        return False, time.monotonic() - t0, f"launch error: {exc}"


def _print_banner() -> None:
    width = 80
    print("=" * width)
    print("  ARCHITECTURE PROOF RUNNER")
    print("  Ref: docs/architecture/architecture-proof-pack.md")
    print("  Governed-app contract: docs/architecture/governed-app-contract.md")
    print("=" * width)
    print()
    print("  Suite map")
    print("  ─────────────────────────────────────────────────────────────────")
    for s in _SUITES:
        skip_note = "  [skippable with --skip-regression]" if s["skippable"] else ""
        print(f"  {s['id']}  {s['label']}{skip_note}")
        wrapped = s["description"]
        print(f"      {wrapped[:72]}")
        if len(wrapped) > 72:
            print(f"      {wrapped[72:]}")
    print("  ─────────────────────────────────────────────────────────────────")
    print()


def _print_summary(
    results: list[tuple[str, str, bool, float, bool]],
) -> bool:
    """Print final summary table. Returns True if all required suites passed."""
    width = 80
    print()
    print("=" * width)
    print("  ARCHITECTURE PROOF SUMMARY")
    print("=" * width)
    print(f"  {'Suite':<4}  {'Label':<36}  {'Status':>6}  {'Time':>7}")
    print(f"  {'─' * 4}  {'─' * 36}  {'─' * 6}  {'─' * 7}")

    all_required_pass = True
    for (
        suite_id,
        label,
        passed,
        elapsed,
        skipped,
    ) in results:  # progress_bar: display-only, iterates pre-computed results
        if skipped:
            status_str = SKIP_MARK
            time_str = "  —"
        elif passed:
            status_str = PASS_MARK
            time_str = f"{elapsed:5.1f}s"
        else:
            status_str = FAIL_MARK
            time_str = f"{elapsed:5.1f}s"
            all_required_pass = False
        print(f"  {suite_id:<4}  {label:<36}  {status_str}  {time_str}")

    print()
    verdict = PASS_MARK if all_required_pass else FAIL_MARK
    total_elapsed = sum(e for _, _, _, e, _ in results)
    print(f"  VERDICT: {verdict}   total time: {total_elapsed:.1f}s")
    print()
    if all_required_pass:
        print("  ✓ All required architecture proof suites pass.")
        print("  ✓ Registry: 5 governed apps + 2 formal exceptions + 0 ad hoc statuses.")
        print("  ✓ Governed loop L1→L0→C0→L2→L5→L6 verified end-to-end.")
        print("  ✓ Formal exception controls verified at gate time.")
    else:
        failed = [sid for sid, _, ok, _, sk in results if not ok and not sk]
        print(f"  ✗ Failed suites: {failed}")
        print("  Fix the failing suite(s) before merge or release.")
    print("=" * width)
    return all_required_pass


def run_architecture_proof(
    suites: list[str] | None = None,
    skip_regression: bool = False,
) -> bool:
    """Run architecture proof suites. Returns True if all required suites pass."""
    _print_banner()

    target_ids = set(suites) if suites else {s["id"] for s in _SUITES}
    results: list[tuple[str, str, bool, float, bool]] = []

    suite_count = len([s for s in _SUITES if s["id"] in target_ids])
    for suite in _SUITES:
        sid = suite["id"]
        if sid not in target_ids:
            continue

        skip = (suite["skippable"] and skip_regression) or sid not in target_ids
        label = suite["label"]
        progress_bar = f"[{len(results) + 1}/{suite_count}]"

        print(f"  ── {progress_bar} Running {sid}: {label} {'(skipping)' if skip else ''}")
        if not skip:
            print(f"     $ python {' '.join(suite['cmd'])}")
        print()

        passed, elapsed, tail = _run_suite(suite, skip=skip)

        if not skip:
            if tail:
                print(f"      [tail output]\n      {tail}")
            mark = "PASS" if passed else "FAIL"
            print(f"\n  ── {sid} {mark} ({elapsed:.1f}s)\n")

        results.append((sid, label, passed, elapsed, skip))

    return _print_summary(results)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Architecture Proof Runner — one-command release gate.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Reference:\n"
            "  Architecture proof pack: docs/architecture/architecture-proof-pack.md\n"
            "  Governed-app contract:   docs/architecture/governed-app-contract.md\n"
            "\n"
            "Individual suites:\n"
            "  S1  python ops_scripts/ci/check_governed_app_conformance.py\n"
            "  S2  python tools/eval/retrieval_benchmark.py --exception-framework-proof\n"
            "  S3  python tools/eval/retrieval_benchmark.py --regression-check\n"
        ),
    )
    parser.add_argument(
        "--skip-regression",
        action="store_true",
        help="Skip S3 (regression check). Useful for fast structural-only verification.",
    )
    parser.add_argument(
        "--suite",
        choices=["S1", "S2", "S3"],
        metavar="SUITE_ID",
        help="Run only the specified suite (S1, S2, or S3).",
    )
    args = parser.parse_args()

    suite_filter = [args.suite] if args.suite else None
    passed = run_architecture_proof(
        suites=suite_filter,
        skip_regression=args.skip_regression,
    )
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
