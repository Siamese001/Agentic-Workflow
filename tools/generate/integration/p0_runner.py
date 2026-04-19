"""P0 two-pass gate runner integration for ADG generation."""

from __future__ import annotations

import sys
from importlib import import_module
from pathlib import Path


def _run_p0_two_pass_runner(sqlite_path: Path | None, plan_path: Path | None = None) -> None:
    """Execute P0 two-pass gates against the generated ADG SQLite snapshot.

    Fail-closed when the runner reports blocked gates or internal runner errors.
    """
    if sqlite_path is None or not sqlite_path.exists():
        print("[ERROR] P0 runner blocked: no production SQLite snapshot found")
        if plan_path is not None and Path(plan_path).exists():
            print(f"[ERROR] See remediation wave plan: {plan_path}")
        sys.exit(1)

    module = import_module("ops_scripts.ci.adg_gates.p0_runner")
    run_p0_two_pass = getattr(module, "run_p0_two_pass")

    print("[ADG] Running P0 two-pass runner on committed artifacts...")
    runner_rc = run_p0_two_pass(
        sqlite_path=sqlite_path,
        modified_files=[],
        emit_artifacts=True,
        skip_preflight=False,
    )

    if runner_rc == 0:
        print("[ADG] P0 two-pass runner: PASSED")
        return

    if runner_rc == 1:
        print("[ERROR] P0 two-pass runner BLOCKED — ADG generation halted")
        if plan_path is not None and Path(plan_path).exists():
            print(f"[ERROR] See remediation wave plan: {plan_path}")
        sys.exit(1)

    print(f"[ERROR] P0 two-pass runner failed with unexpected exit code: {runner_rc}")
    if plan_path is not None and Path(plan_path).exists():
        print(f"[ERROR] See remediation wave plan: {plan_path}")
    sys.exit(1)
