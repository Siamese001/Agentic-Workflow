#!/usr/bin/env python3
"""
pre_user_prompt_deferred_scope_recovery.py — session-start scope-loss surfacing.

Runs on every user prompt. Scans
`artifacts/governance/deferred_scope_capture.jsonl` for unresolved pendings
(entries with kind in pending_no_token / post_*_error that have no later
auto_posted / confirmed_by_receipt record for the same key).

Prints a compact one-line summary to stderr so Cursor Agent sees it at session start.
Silent when no pendings. Does NOT auto-retry — that's
`tools/reports/recover_deferred_scope_pendings.py --apply`.

Rationale: open backlog scope must never hide in a jsonl file indefinitely.
Session-start surfacing makes unresolved pendings impossible to miss.

Fail policy: OPEN — any error → exit 0 silently.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
CAPTURE_LOG = REPO_ROOT / "artifacts" / "governance" / "deferred_scope_capture.jsonl"

PENDING_KINDS = {
    "pending_no_token",
    "post_http_error",
    "post_transport_error",
    "post_decode_error",
}
RESOLVED_KINDS = {"auto_posted", "confirmed_by_receipt", "skipped_recent_duplicate"}


def _marker_key(marker: dict[str, Any]) -> str:
    return (
        f"{marker.get('plan', '?')}|"
        f"{marker.get('wave', '?')}|"
        f"{marker.get('phase', '?')}"
    )


def _scan_unresolved() -> list[dict[str, Any]]:
    if not CAPTURE_LOG.exists():
        return []

    latest_pending: dict[str, dict[str, Any]] = {}
    latest_resolved_ts: dict[str, str] = {}

    try:
        with CAPTURE_LOG.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except (json.JSONDecodeError, ValueError):
                    continue
                marker = rec.get("marker") or {}
                if not marker:
                    continue
                key = _marker_key(marker)
                ts = rec.get("timestamp", "")
                kind = rec.get("kind", "")
                if kind in PENDING_KINDS:
                    if latest_pending.get(key, {}).get("timestamp", "") < ts:
                        latest_pending[key] = rec
                elif kind in RESOLVED_KINDS:
                    if latest_resolved_ts.get(key, "") < ts:
                        latest_resolved_ts[key] = ts
    except OSError:
        return []

    unresolved: list[dict[str, Any]] = []
    for key, rec in latest_pending.items():
        pending_ts = rec.get("timestamp", "")
        resolved_ts = latest_resolved_ts.get(key, "")
        if resolved_ts >= pending_ts:
            continue
        unresolved.append(rec)
    return unresolved


def main() -> int:
    unresolved = _scan_unresolved()
    if not unresolved:
        return 0

    # Compact summary — Cursor Agent sees it in the prompt context
    count = len(unresolved)
    # Show up to 3 oldest by timestamp
    sorted_items = sorted(unresolved, key=lambda r: r.get("timestamp", ""))[:3]
    keys = ", ".join(_marker_key(r.get("marker", {})) for r in sorted_items)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    print(
        f"[deferred_scope_recovery] {count} unresolved pending scope item(s) "
        f"as of {now}: {keys}{'...' if count > 3 else ''} "
        f"-> run: python tools/reports/recover_deferred_scope_pendings.py --apply",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"[deferred_scope_recovery] fail-open: {exc}", file=sys.stderr)
        sys.exit(0)
