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
_DEFER_ENV_VAR_NEW: Final[str] = "ADG_CONTINUE_ON_GATE_FAILURE"
_DEFER_ENV_TRUTHY: Final[frozenset[str]] = frozenset({"1", "true", "yes", "on"})


def _resolve_defer_flag(defer_exit: bool | None) -> bool:
    """Resolve the defer-exit flag from arg → env → default.

    Plan adg-fail-aggregating-gate-chain-9d4e1f W3.2: the canonical env
    var is ``ADG_CONTINUE_ON_GATE_FAILURE`` because defer governs ALL
    opting-in gates (P0/P1/P2/P3/SC/agentic-antipattern/dead-prod-imports/
    witness/integrity), not just P0. The legacy ``ADG_CONTINUE_ON_P0``
    name is preserved as an alias for back-compat with downstream tooling
    and CI scripts. Either flag activates defer mode; both being set is
    equivalent to either being set.
    """
    if defer_exit is not None:
        return defer_exit
    raw_new = os.environ.get(_DEFER_ENV_VAR_NEW, "").strip().lower()
    if raw_new in _DEFER_ENV_TRUTHY:
        return True
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


def format_summary_table() -> str:
    """Return a human-readable markdown table of all deferred failures.

    Rendered at the end of an ADG generation run so operators see every
    gate's outcome in one place instead of grep-ing the full build log.
    Returns the empty string when no failures are recorded.

    Plan adg-fail-aggregating-gate-chain-9d4e1f W3.1.
    """
    if not _DEFERRED_FAILURES:
        return ""
    rows = deferred_failure_summary()
    # Determine column widths based on content (with sensible minimums).
    name_w = max(10, max(len(str(r["gate_name"])) for r in rows))
    msg_w = max(20, min(80, max(len(str(r.get("message") or "")) for r in rows)))
    sep = f"+{'-' * (name_w + 2)}+----+{'-' * (msg_w + 2)}+"
    lines = [
        "",
        "=" * 78,
        "[ADG] DEFERRED FAILURE SUMMARY",
        "=" * 78,
        sep,
        f"| {'gate_name'.ljust(name_w)} | rc | {'message'.ljust(msg_w)} |",
        sep,
    ]
    for r in rows:
        name = str(r["gate_name"]).ljust(name_w)
        rc = str(r["rc"]).rjust(2)
        msg = str(r.get("message") or "")[:msg_w].ljust(msg_w)
        lines.append(f"| {name} | {rc} | {msg} |")
    lines.append(sep)
    # Surface remediation plan paths separately so the table stays clean.
    plan_paths = [r for r in rows if r.get("plan_path")]
    if plan_paths:
        lines.append("")
        lines.append("Remediation plans:")
        for r in plan_paths:
            lines.append(f"  - {r['gate_name']}: {r['plan_path']}")
    lines.append("")
    lines.append(f"Total deferred failures: {len(rows)}  |  Final exit code: {deferred_exit_code()}")
    lines.append("=" * 78)
    return "\n".join(lines)


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
