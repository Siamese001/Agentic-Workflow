#!/usr/bin/env python3
"""append_marker.py — Append a single decision marker to the local capture queue.

Used by Cursor Agent as a `run_command` invocation at the end of any refactor-class
response, to record DECISION_CAPTURED / DEFERRED_SCOPE / NEXT_STEP markers
without depending on the Windsurf post-cursor-agent hook chain.

Usage:
    python tools/capture/append_marker.py --marker "DECISION_CAPTURED: type=..., ..."
    echo "DECISION_CAPTURED: ..." | python tools/capture/append_marker.py --stdin

Behavior:
    - Validates the marker matches one of the three known prefixes
    - Appends a single JSONL row to artifacts/capture/markers.jsonl
    - Each row contains: {received_at, marker_type, raw, session_hint}
    - Fail policy: OPEN — exits 0 on success, 0 with WARN on validation failure,
      non-zero only on filesystem permission errors.

The drain step (queue_to_ledger.py) consumes this queue and writes structured
rows into the canonical SQLite decision ledger.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path

# In-process serialization for concurrent append_marker calls. Windows file
# IO does not provide POSIX-style atomic-append-under-PIPE_BUF, so we serialize
# explicitly. For multi-process atomicity the OS append-mode write is enough
# in practice (one process per run_command invocation), but if Cursor Agent ever
# fans out concurrent run_commands a portalocker-style file lock would be
# the next step.
_APPEND_LOCK = threading.Lock()

REPO_ROOT = Path(__file__).resolve().parents[2]
QUEUE_DIR = REPO_ROOT / "artifacts" / "capture"
QUEUE_FILE = QUEUE_DIR / "markers.jsonl"

# Recognized marker prefixes. Each maps to its required-field regex used to
# light-validate before appending. Validation is intentionally lenient — the
# drain step does the strict parse against the canonical capture-hook regex.
_MARKER_PATTERNS: dict[str, re.Pattern[str]] = {
    "DECISION_CAPTURED": re.compile(r"^DECISION_CAPTURED:\s*type=[\w_]+\s*,"),
    "DEFERRED_SCOPE": re.compile(r"^DEFERRED_SCOPE:\s*plan="),
    "NEXT_STEP": re.compile(r"^NEXT_STEP:\s*plan="),
    # Wave 1 P1.2 addition (plan apps-eval-qwen32b-rollout-b7c4d9): judge
    # surface emits a distinct marker type so drain consumers can route
    # judge rows to the judge-calibration ledger without colliding with
    # the router / decision ledgers. Shape mirrors DECISION_CAPTURED:
    # ``JUDGE_DECISION: type=judge_decision, <kv-pairs>``.
    "JUDGE_DECISION": re.compile(r"^JUDGE_DECISION:\s*type=judge_decision\s*,"),
    # plan author-gate-hardening-a3b8f2 W1.P1.2 — outcome writer marker.
    # Shape: DECISION_OUTCOME: decision_id=dec_xxx, execution_completed=1,
    #        tests_passed=1, regression_found=0, rollback_required=0,
    #        promote_to_pattern=0[, followup_decision_id=...][, notes=...]
    "DECISION_OUTCOME": re.compile(r"^DECISION_OUTCOME:\s*decision_id=dec_[a-z0-9]+"),
}


def classify_marker(line: str) -> str | None:
    """Return the matched marker type, or None if the line is not a marker."""
    line = line.strip()
    for label, pat in _MARKER_PATTERNS.items():
        if pat.match(line):
            return label
    return None


def append_marker(raw: str, session_hint: str | None = None) -> tuple[bool, str]:
    """Append a single marker to the queue. Returns (ok, message)."""
    raw = raw.strip()
    if not raw:
        return False, "empty input"
    mtype = classify_marker(raw)
    if mtype is None:
        return False, (
            f"unrecognized marker (must start with DECISION_CAPTURED:|"
            f"DEFERRED_SCOPE:|NEXT_STEP:). got: {raw[:80]!r}"
        )

    QUEUE_DIR.mkdir(parents=True, exist_ok=True)
    row = {
        "received_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "marker_type": mtype,
        "raw": raw,
        "session_hint": session_hint or os.environ.get("WINDSURF_SESSION_ID", ""),
        "pid": os.getpid(),
    }
    line = json.dumps(row, ensure_ascii=False)
    # Serialize in-process appends. POSIX guarantees atomic append-under-PIPE_BUF
    # but Windows does not; the lock makes concurrent threads safe regardless.
    with _APPEND_LOCK:
        with QUEUE_FILE.open("ab") as f:
            f.write(line.encode("utf-8") + b"\n")
    return True, f"appended {mtype} to {QUEUE_FILE}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument(
        "--marker",
        help="The full marker line as a single string. Multiple --marker flags allowed.",
        action="append",
        default=[],
    )
    src.add_argument(
        "--stdin",
        action="store_true",
        help="Read marker line(s) from stdin, one marker per line.",
    )
    parser.add_argument(
        "--session",
        help="Optional session identifier for cross-row correlation.",
        default=None,
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress success messages on stdout (errors still print to stderr).",
    )
    args = parser.parse_args(argv)

    lines: list[str] = []
    if args.stdin:
        # Stdin may contain prose; extract any complete marker lines.
        if sys.stdin.isatty():
            print("[append_marker] error: --stdin given but stdin is a TTY", file=sys.stderr)
            return 2
        text = sys.stdin.read()
        for ln in text.splitlines():
            if classify_marker(ln) is not None:
                lines.append(ln.strip())
    else:
        lines = [m.strip() for m in args.marker if m.strip()]

    if not lines:
        print("[append_marker] WARN: no recognizable markers found", file=sys.stderr)
        return 0  # fail-open; caller (Cursor Agent) shouldn't see this as fatal

    ok_count = 0
    for ln in lines:
        ok, msg = append_marker(ln, session_hint=args.session)
        if not ok:
            print(f"[append_marker] WARN: {msg}", file=sys.stderr)
            continue
        ok_count += 1
        if not args.quiet:
            print(f"[append_marker] {msg}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
