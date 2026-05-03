#!/usr/bin/env python3
"""
pre_user_prompt_ag_queue_surface.py — Proactive Author-Gate queue surfacing.

Hook: pre_user_prompt (show_output=true, so Cascade sees the output).

At the start of each user turn, checks the Author-Gate queue state and
emits one line per plan that has pending packets:

    AG_QUEUE_PENDING: plan=<slug> next=<packet_id> depends_on=<id1,id2> title=<short>

Empty queue → no output (silent). Cascade uses this signal to remember
the drain obligation before composing a response.

Constitutional tie-in: §35 (queue drain mandatory).

Fail policy: OPEN. Never blocks the turn. Bypass: AG_QUEUE_SURFACE_BYPASS=1.
"""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
HELPER_PATH = REPO_ROOT / ".windsurf" / "scripts" / "_author_gate_queue.py"


def _load_helper():
    if not HELPER_PATH.exists():
        return None
    try:
        spec = importlib.util.spec_from_file_location("_ag_queue", HELPER_PATH)
        if spec is None or spec.loader is None:
            return None
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    except (OSError, ImportError):
        return None


def main() -> int:
    if os.environ.get("AG_QUEUE_SURFACE_BYPASS") == "1":
        return 0

    helper = _load_helper()
    if helper is None:
        return 0

    try:
        plans = helper.list_plans_with_pending()
    except (OSError, ValueError):
        return 0

    if not plans:
        return 0

    for slug in plans:
        try:
            nxt = helper.next_packet(slug)
        except (OSError, ValueError):
            continue
        if nxt is None:
            continue
        deps = ",".join(nxt.get("depends_on") or []) or "(none)"
        title = nxt.get("title", "(no title)")
        # Bound title length for sanity
        if len(title) > 80:
            title = title[:77] + "..."
        print(
            f"AG_QUEUE_PENDING: plan={slug} next={nxt['id']} "
            f"depends_on={deps} title={title}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
