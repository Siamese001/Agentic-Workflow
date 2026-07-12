"""Architecture proof runner — one-command release gate.

The runner composes existing proof suites and derives reviewer-facing app counts
from ``apps_shared.integrations.app_registry.APP_REGISTRY``. It does not carry a
second hard-coded architecture inventory.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


def _bootstrap_repo_root() -> Path:
    repo_root = Path(__file__).resolve().parents[2]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    return repo_root


_REPO_ROOT = _bootstrap_repo_root()
PASS_MARK = "\033[92mPASS\033[0m"
FAIL_MARK = "\033[91mFAIL\033[0m"
SKIP_MARK = "\033[93mSKIP\033[0m"

_SUITES: list[dict[str, Any]] = [
    {
        "id": "S1",
        "label": "Conformance Gate (CONF + EXCF)",
        "cmd": ["ops_scripts/ci/check_governed_app_conformance.py"],
        "description": (
            "Registry-derived structural checks for governed entries and formal exceptions: "
            "runner/callable imports, capability tokens, exception schema, and compensating controls."
        ),
        "skippable": False,
    },
    {
        "id": "S2",
        "label": "Exception Framework Proof",
        "cmd": ["tools/eval/retrieval_benchmark.py", "--exception-framework-proof"],
        "description": (
            "Behavioral proof for registry-governed entries plus formal-exception controls, "
            "including degraded behavior, telemetry, and the zero-ad-hoc gate."
        ),
        "skippable": False,
    },
    {
        "id": "S3",
        "label": "Regression Check",
        "cmd": ["tools/eval/retrieval_benchmark.py", "--regression-check"],
        "description": (
            "Evidence-governance regression baseline for grounding, coverage, disposition, and telemetry."
        ),
        "skippable": True,
    },
]


def _registry_snapshot() -> tuple[list[str], list[str], list[str]]:
    from apps_shared.integrations.app_registry import (  # noqa: PLC0415
        APP_REGISTRY,
        ExceptionAppEntry,
        FormalExceptionEntry,
        GovernedAppEntry,
    )

    governed = sorted(name for name, entry in APP_REGISTRY.items() if isinstance(entry, GovernedAppEntry))
    formal = sorted(name for name, entry in APP_REGISTRY.items() if isinstance(entry, FormalExceptionEntry))
    transient = sorted(
        name
        for name, entry in APP_REGISTRY.items()
        if isinstance(entry, ExceptionAppEntry) and not isinstance(entry, FormalExceptionEntry)
    )
    return governed, formal, transient


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


def _run_suite(suite: dict[str, Any], skip: bool = False) -> tuple[bool, float, str]:
    """Run one proof suite and return passed, elapsed seconds, and output tail."""
    if skip:
        return True, 0.0, "(skipped)"

    resolved_cmd, resolve_error = _resolve_suite_cmd(suite["cmd"])
    if resolve_error is not None or resolved_cmd is None:
        return False, 0.0, resolve_error or "invalid suite command"

    command = [sys.executable, *resolved_cmd]
    started = time.monotonic()
    try:
        result = subprocess.run(
            command,
            cwd=str(_REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=300,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        output = f"{exc.stdout or ''}{exc.stderr or ''}"
        tail = "\n      ".join(output.strip().splitlines()[-8:]) or "TIMEOUT after 300s"
        return False, time.monotonic() - started, tail
    except (OSError, ValueError) as exc:
        return False, time.monotonic() - started, f"launch error: {exc}"

    elapsed = time.monotonic() - started
    output = f"{result.stdout}{result.stderr}"
    tail = "\n      ".join(output.strip().splitlines()[-8:])
    return result.returncode == 0, elapsed, tail


def _print_banner() -> None:
    print("=" * 80)
    print("  ARCHITECTURE PROOF RUNNER")
    print("  Ref: docs/architecture/architecture-proof-pack.md")
    print("  Registry SSOT: apps_shared/integrations/app_registry.py")
    print("=" * 80)
    print()
    print("  Suite map")
    print("  " + "-" * 64)
    for suite in _SUITES:
        skip_note = " [skippable]" if suite["skippable"] else ""
        print(f"  {suite['id']}  {suite['label']}{skip_note}")
        print(f"      {suite['description']}")
    print("  " + "-" * 64)
    print()


def _print_registry_snapshot() -> None:
    try:
        governed, formal, transient = _registry_snapshot()
    except Exception as exc:
        print(f"  ! Registry snapshot unavailable: {exc!r}")
        return

    print("  Registry snapshot")
    print(f"  - governed ({len(governed)}): {', '.join(governed) or '<none>'}")
    print(f"  - formal exceptions ({len(formal)}): {', '.join(formal) or '<none>'}")
    print(f"  - transient candidates ({len(transient)}): {', '.join(transient) or '<none>'}")
    print()


def _print_summary(results: list[tuple[str, str, bool, float, bool]]) -> bool:
    print()
    print("=" * 80)
    print("  ARCHITECTURE PROOF SUMMARY")
    print("=" * 80)
    print(f"  {'Suite':<4}  {'Label':<36}  {'Status':>6}  {'Time':>7}")
    print(f"  {'-' * 4}  {'-' * 36}  {'-' * 6}  {'-' * 7}")

    all_required_pass = True
    for suite_id, label, passed, elapsed, skipped in results:
        if skipped:
            status = SKIP_MARK
            timing = "-"
        elif passed:
            status = PASS_MARK
            timing = f"{elapsed:5.1f}s"
        else:
            status = FAIL_MARK
            timing = f"{elapsed:5.1f}s"
            all_required_pass = False
        print(f"  {suite_id:<4}  {label:<36}  {status:>6}  {timing:>7}")

    total_elapsed = sum(elapsed for _, _, _, elapsed, _ in results)
    verdict = PASS_MARK if all_required_pass else FAIL_MARK
    print()
    print(f"  VERDICT: {verdict}   total time: {total_elapsed:.1f}s")
    print()

    try:
        governed, formal, transient = _registry_snapshot()
    except Exception as exc:
        governed, formal, transient = [], [], []
        print(f"  ! Registry summary unavailable: {exc!r}")

    if all_required_pass:
        print("  + All required architecture proof suites pass.")
        print(
            "  + Registry: "
            f"{len(governed)} governed + {len(formal)} formal exceptions + "
            f"{len(transient)} transient candidates."
        )
        print("  + Governed behavior and formal-exception controls were evaluated by the selected suites.")
    else:
        failed = [suite_id for suite_id, _, passed, _, skipped in results if not passed and not skipped]
        print(f"  - Failed suites: {failed}")
        print("  - Fix the failing suite before merge or release.")
    print("=" * 80)
    return all_required_pass


def run_architecture_proof(
    suites: list[str] | None = None,
    skip_regression: bool = False,
) -> bool:
    """Run selected proof suites and return whether all required suites passed."""
    _print_banner()
    _print_registry_snapshot()

    target_ids = set(suites) if suites else {suite["id"] for suite in _SUITES}
    unknown = target_ids - {suite["id"] for suite in _SUITES}
    if unknown:
        raise ValueError(f"unknown suites: {sorted(unknown)}")

    selected = [suite for suite in _SUITES if suite["id"] in target_ids]
    results: list[tuple[str, str, bool, float, bool]] = []
    for index, suite in enumerate(selected, 1):
        skip = bool(suite["skippable"] and skip_regression)
        print(f"  -- [{index}/{len(selected)}] Running {suite['id']}: {suite['label']}" + (" (skipping)" if skip else ""))
        if not skip:
            print(f"     $ python {' '.join(suite['cmd'])}")
        print()

        passed, elapsed, tail = _run_suite(suite, skip=skip)
        if not skip:
            if tail:
                print(f"      [tail output]\n      {tail}")
            print(f"\n  -- {suite['id']} {'PASS' if passed else 'FAIL'} ({elapsed:.1f}s)\n")
        results.append((suite["id"], suite["label"], passed, elapsed, skip))

    return _print_summary(results)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-regression", action="store_true", help="Skip the skippable S3 regression suite.")
    parser.add_argument("--suite", choices=[suite["id"] for suite in _SUITES], help="Run one suite only.")
    args = parser.parse_args(argv)
    passed = run_architecture_proof(
        suites=[args.suite] if args.suite else None,
        skip_regression=args.skip_regression,
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
