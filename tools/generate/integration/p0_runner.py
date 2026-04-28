"""P0 two-pass gate runner integration for ADG generation."""

from __future__ import annotations

import os
import sys
from importlib import import_module
from pathlib import Path


# W8 (plan adg-pipeline-simplification-e2e-9b4c27): cross-call signal so
# main() can detect a deferred P0 failure after the rest of the pipeline
# has run and exit with the correct non-zero code at the end. Set by
# `_run_p0_two_pass_runner` when invoked with `defer_exit=True` and the
# runner reports blocked gates. Tested via `is_p0_failure_deferred()`.
_DEFERRED_P0_FAILURE: dict[str, object] = {"failed": False, "rc": 0, "plan_path": None}


def is_p0_failure_deferred() -> bool:
    """Return True when a P0 failure was deferred and the run must still exit non-zero."""
    return bool(_DEFERRED_P0_FAILURE["failed"])


def deferred_p0_exit_code() -> int:
    """Return the deferred P0 exit code (0 if no failure was deferred)."""
    return int(_DEFERRED_P0_FAILURE["rc"]) if _DEFERRED_P0_FAILURE["failed"] else 0  # type: ignore[arg-type]


def deferred_p0_plan_path() -> Path | None:
    """Return the deferred P0 remediation plan path, if any."""
    pp = _DEFERRED_P0_FAILURE["plan_path"]
    return Path(pp) if pp else None  # type: ignore[arg-type]


def _run_p0_two_pass_runner(
    sqlite_path: Path | None,
    plan_path: Path | None = None,
    *,
    defer_exit: bool | None = None,
) -> None:
    """Execute P0 two-pass gates against the generated ADG SQLite snapshot.

    Fail-closed when the runner reports blocked gates or internal runner errors.

    W8 (plan adg-pipeline-simplification-e2e-9b4c27): when ``defer_exit`` is
    True (or env ``ADG_CONTINUE_ON_P0=1`` is set), a P0 failure is recorded
    in module-level state instead of calling ``sys.exit`` directly. The
    rest of the pipeline (P4/P5 watchlists, zip archive, skip summary,
    parallel post-ADG gates) then has a chance to run, and main() exits
    with the recorded non-zero code at the very end. The default
    behaviour (``defer_exit=False`` and env unset) is unchanged: P0
    failure halts the pipeline immediately. This was added to let authors
    iterate on pipeline output without first having to remediate every
    architectural P0 violation in the codebase.
    """
    # Resolve the defer-exit flag from arg → env → default.
    # Plan adg-fail-aggregating-gate-chain-9d4e1f W3.2: delegate to the
    # shared resolver so both legacy ADG_CONTINUE_ON_P0 and canonical
    # ADG_CONTINUE_ON_GATE_FAILURE activate defer consistently across
    # every gate. Preserves back-compat for the legacy flag.
    if defer_exit is None:
        from tools.generate.integration.deferred_failures import (  # noqa: PLC0415
            _resolve_defer_flag,
        )

        defer_exit = _resolve_defer_flag(None)

    if sqlite_path is None or not sqlite_path.exists():
        print("[ERROR] P0 runner blocked: no production SQLite snapshot found")
        if plan_path is not None and Path(plan_path).exists():
            print(f"[ERROR] See remediation wave plan: {plan_path}")
        # No SQLite means downstream stages have nothing to read; cannot defer.
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

    # P0 failed. Either halt now (default) or record + continue.
    fail_msg_prefix = (
        "[WARN] P0 two-pass runner BLOCKED (deferred — ADG_CONTINUE_ON_P0 set)"
        if defer_exit
        else "[ERROR] P0 two-pass runner BLOCKED — ADG generation halted"
    )
    print(
        fail_msg_prefix
        if runner_rc == 1
        else f"[{'WARN' if defer_exit else 'ERROR'}] P0 two-pass runner failed with unexpected exit code: {runner_rc}"
    )
    if plan_path is not None and Path(plan_path).exists():
        print(f"[{'WARN' if defer_exit else 'ERROR'}] See remediation wave plan: {plan_path}")

    if defer_exit:
        _DEFERRED_P0_FAILURE["failed"] = True
        _DEFERRED_P0_FAILURE["rc"] = runner_rc if runner_rc != 0 else 1
        _DEFERRED_P0_FAILURE["plan_path"] = str(plan_path) if plan_path else None
        print(
            "[ADG] Pipeline continues so post-P0 stages (P4/P5 watchlists, zip, "
            "skip summary, parallel gates) can run; final exit will be non-zero."
        )
        return

    sys.exit(runner_rc if runner_rc != 0 else 1)
