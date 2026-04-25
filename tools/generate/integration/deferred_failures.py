"""Shared deferred-failure registry for ADG generation gates.

Plan adg-cascading-ratchet-defer-exit-a41828 (Wave B): generalises the W8
defer-exit pattern from `p0_runner.py` so every Tier-2 gate that ordinarily
calls `sys.exit(1)` on hard-fail can opt into the same defer-and-exit-at-
end semantics. When the user sets `--continue-on-p0` (CLI flag) or
``ADG_CONTINUE_ON_P0=1`` (env var), each opting-in gate records its failure
into this module-level registry and returns instead of terminating the run;
``main()`` then reads the registry at the end of the pipeline and exits
with the first recorded non-zero rc.

This module is intentionally tiny and dependency-free so it can be imported
from gates that may run very early in the pipeline.

Public API:

- ``is_failure_deferred() -> bool``
    Any opting-in gate has recorded a failure this run.

- ``deferred_exit_code() -> int``
    First non-zero rc from the registry, in registration order. Returns 0
    when no failures are recorded.

- ``deferred_failure_summary() -> list[dict[str, object]]``
    Snapshot of all recorded failures in registration order. Each entry has
    keys: ``gate_name``, ``rc``, ``message``, ``plan_path``.

- ``record_or_exit(gate_name, rc, *, message=None, plan_path=None,
                  defer_exit=None) -> None``
    Records the failure if defer-exit is active; otherwise calls
    ``sys.exit(rc)``. ``defer_exit=None`` means: read the
    ``ADG_CONTINUE_ON_P0`` env var; explicit ``True``/``False`` overrides
    the env.

- ``reset_for_tests() -> None``
    Clear the registry. Tests only — production callers MUST NOT call this.
"""

from __future__ import annotations

import os
import sys
from typing import Final

# Deferred-failure registry. Ordered by insertion order (Python dict
# preserves insertion order since 3.7). Keys are gate names; values are
# {"rc": int, "message": str | None, "plan_path": str | None}.
_DEFERRED_FAILURES: dict[str, dict[str, object]] = {}

_DEFER_ENV_VAR: Final[str] = "ADG_CONTINUE_ON_P0"
_DEFER_ENV_TRUTHY: Final[frozenset[str]] = frozenset({"1", "true", "yes", "on"})


def _resolve_defer_flag(defer_exit: bool | None) -> bool:
    """Resolve the defer-exit flag from arg → env → default.

    The env var is named ``ADG_CONTINUE_ON_P0`` for back-compat with the
    original W8 implementation. Despite the "P0" suffix in the name, it
    governs ALL opting-in gates (P0/P1/SC-1/agentic-antipattern/dead-prod
    imports). The name is preserved to avoid breaking downstream tooling
    and CI scripts that already set it.
    """
    if defer_exit is not None:
        return defer_exit
    raw = os.environ.get(_DEFER_ENV_VAR, "").strip().lower()
    return raw in _DEFER_ENV_TRUTHY


def is_failure_deferred() -> bool:
    """Return True when any opting-in gate has recorded a failure this run."""
    return bool(_DEFERRED_FAILURES)


def deferred_exit_code() -> int:
    """Return the first recorded non-zero rc, or 0 if no failures recorded.

    Uses dict-insertion order (Python 3.7+) so the result is deterministic
    and matches the order gates ran in.
    """
    for entry in _DEFERRED_FAILURES.values():
        rc = int(entry.get("rc", 0))  # type: ignore[arg-type]
        if rc != 0:
            return rc
    return 0


def deferred_failure_summary() -> list[dict[str, object]]:
    """Snapshot of all recorded failures in registration order.

    Returned list is a fresh copy; mutating it has no effect on the
    registry. Each entry has keys: ``gate_name``, ``rc``, ``message``,
    ``plan_path``.
    """
    out: list[dict[str, object]] = []
    for gate_name, entry in _DEFERRED_FAILURES.items():
        out.append(
            {
                "gate_name": gate_name,
                "rc": entry.get("rc", 1),
                "message": entry.get("message"),
                "plan_path": entry.get("plan_path"),
            }
        )
    return out


def record_failure(
    gate_name: str,
    rc: int,
    *,
    message: str | None = None,
    plan_path: str | None = None,
) -> None:
    """Record a failure into the registry without consulting the defer flag.

    Used by callers that have already decided to defer (e.g. the existing
    ``p0_runner._run_p0_two_pass_runner`` which has its own logic for
    when to defer). Re-recording the same gate name overwrites the prior
    entry's rc/message but preserves its registration order.
    """
    _DEFERRED_FAILURES[gate_name] = {
        "rc": int(rc),
        "message": message,
        "plan_path": plan_path,
    }


def record_or_exit(
    gate_name: str,
    rc: int,
    *,
    message: str | None = None,
    plan_path: str | None = None,
    defer_exit: bool | None = None,
) -> None:
    """Record the failure if deferred is active; otherwise ``sys.exit(rc)``.

    This is the primary entry point for new callers. Replaces an inline
    ``sys.exit(rc)`` in a gate body. When the run is configured to defer
    (env var or explicit kwarg), this returns and the caller continues
    naturally; otherwise it terminates the process.
    """
    if rc == 0:
        # Don't pollute the registry with PASS rows. Callers should only
        # invoke this on actual failures.
        return
    if not _resolve_defer_flag(defer_exit):
        if message:
            print(f"[ERROR] {gate_name} hard-fail: {message}")
        sys.exit(rc)
    record_failure(gate_name, rc, message=message, plan_path=plan_path)
    if message:
        print(f"[WARN] {gate_name} BLOCKED (deferred — ADG_CONTINUE_ON_P0 set): {message}")


def reset_for_tests() -> None:
    """Clear the registry. Tests only.

    Production callers MUST NOT invoke this; the registry is meant to
    accumulate across the entire run.
    """
    _DEFERRED_FAILURES.clear()


__all__ = [
    "is_failure_deferred",
    "deferred_exit_code",
    "deferred_failure_summary",
    "record_failure",
    "record_or_exit",
    "reset_for_tests",
]
