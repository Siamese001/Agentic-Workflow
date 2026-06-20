"""Shared --apps-e2e-dry-run short-circuit for app entrypoints.

Lets the apps_e2e auditability harness invoke ``python -m <app>
--apps-e2e-dry-run`` without engaging the real run path. Each runnable
app's ``__main__.main()`` calls :func:`maybe_short_circuit` as its very
first statement; if ``--apps-e2e-dry-run`` is in ``sys.argv`` the helper
prints a structured marker line and exits 0.

The flag name is deliberately namespaced (not bare ``--dry-run``) so it
cannot collide with any app's own CLI surface (e.g. apps_qna already has
its own ``--dry-run`` for pack-builder runs).

Plan: .codex/plans/apps-e2e-auditability-harness-7c2a91.md
"""

from __future__ import annotations

import json
import sys

DRY_RUN_FLAG = "--apps-e2e-dry-run"
"""The exact CLI token harness drivers must pass to short-circuit."""

DRY_RUN_MARKER_PREFIX = "APPS_E2E_DRY_RUN: "
"""Stable prefix for the marker line; harness consumers grep for this."""


def maybe_short_circuit(app_name: str) -> None:
    """Print a structured marker and exit 0 if the dry-run flag is present.

    No-op otherwise. Idempotent. Never raises.

    Parameters
    ----------
    app_name:
        The app's canonical name (e.g. ``"apps_lic"``). Goes into the
        marker payload so the harness can correlate.
    """
    if DRY_RUN_FLAG not in sys.argv:
        return
    payload = {
        "apps_e2e_dry_run_marker": True,
        "app_name": app_name,
        "status": "dry_run_short_circuit",
        "note": (
            "App entrypoint short-circuited at __main__.main() before "
            "_adg_bootstrap() and run_main() delegation. No spine engaged."
        ),
        "flag": DRY_RUN_FLAG,
    }
    print(DRY_RUN_MARKER_PREFIX + json.dumps(payload, sort_keys=True))
    sys.exit(0)


__all__ = ["DRY_RUN_FLAG", "DRY_RUN_MARKER_PREFIX", "maybe_short_circuit"]
