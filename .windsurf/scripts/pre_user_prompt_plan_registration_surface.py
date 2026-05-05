#!/usr/bin/env python3
"""
pre_user_prompt_plan_registration_surface.py — Surface unregistered plans.

Hook: pre_user_prompt (show_output=true, so Cascade sees the output).

At the start of each user turn, emits one line per plan in the registration
queue that still has ``registered=False``::

    PLAN_REGISTRATION_PENDING: slug=<slug> path=<path> status=<declared> captured=<iso>

Empty queue → no output (silent). Cascade uses the signal to post the
matching Notion Plans DB row before proceeding with wave work.

Constitutional tie-in: §36.

Fail policy: OPEN. Never blocks the turn. Bypass: PLAN_REGISTRATION_SURFACE_BYPASS=1.
"""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
HELPER_PATH = REPO_ROOT / ".windsurf" / "scripts" / "_plan_registration.py"

MAX_LINES = 20


def _load_helper():
    if not HELPER_PATH.exists():
        return None
    mod_name = "_plan_registration"
    if mod_name in sys.modules:
        return sys.modules[mod_name]
    try:
        spec = importlib.util.spec_from_file_location(mod_name, HELPER_PATH)
        if spec is None or spec.loader is None:
            return None
        mod = importlib.util.module_from_spec(spec)
        sys.modules[mod_name] = mod
        try:
            spec.loader.exec_module(mod)
        except Exception:
            sys.modules.pop(mod_name, None)
            raise
        return mod
    except (OSError, ImportError):
        return None


def main() -> int:
    if os.environ.get("PLAN_REGISTRATION_SURFACE_BYPASS") == "1":
        return 0

    helper = _load_helper()
    if helper is None:
        return 0

    try:
        pending = helper.pending_registrations()
    except (OSError, ValueError):
        return 0

    if not pending:
        return 0

    for row in pending[:MAX_LINES]:
        slug = row.get("slug", "?")
        path = row.get("path", "?")
        status = row.get("declared_status", "Not Started")
        captured = row.get("captured_at", "?")
        print(
            f"PLAN_REGISTRATION_PENDING: slug={slug} path={path} "
            f"status={status} captured={captured}"
        )

    if len(pending) > MAX_LINES:
        print(
            f"PLAN_REGISTRATION_PENDING: ... {len(pending) - MAX_LINES} more "
            f"(see .windsurf/state/plan_registration_queue.jsonl)"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
