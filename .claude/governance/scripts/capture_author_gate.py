#!/usr/bin/env python3
"""In-response DECISION_CAPTURED marker capture helper.

Bypass for the Cursor 2.0.67 bug where ``post_cursor_agent_response`` hooks
silently stop firing mid-session. When the heartbeat log shows the hook
chain is dark, Cursor Agent invokes this script directly via ``run_command``
in the same response that emits the marker — guaranteeing the Author-Gate
ledger captures the decision without depending on the broken hook channel.

This script is an exact analog of ``.claude/governance/scripts/defer.py`` for the
DEFERRED_SCOPE capture path: it wraps each marker in the Cursor payload
shape and invokes ``post_cursor_agent_author_gate_capture.py`` directly.

USAGE
-----
    # Single marker as CLI arg:
    python .claude/governance/scripts/capture_author_gate.py "DECISION_CAPTURED: type=refactor_scope, repo_area=.cursor, selected=W1, outcome=executed, confidence=0.92, gap=0.18"

    # From a file (one or more markers, one per line):
    python .claude/governance/scripts/capture_author_gate.py --file markers.txt

    # From stdin:
    echo "DECISION_CAPTURED: ..." | python .claude/governance/scripts/capture_author_gate.py --stdin

EXIT CODES
----------
    0 all markers captured successfully
    1 at least one marker failed
    2 invalid input (no markers found, unreadable file)

CONSTITUTIONAL
    - No PowerShell; subprocess.run(argv, shell=False, timeout=120)
    - UTF-8 stdio
    - Specific exceptions: subprocess.TimeoutExpired, FileNotFoundError
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
HOOK_SCRIPT = REPO_ROOT / ".claude" / "governance/scripts" / "post_cursor_agent_author_gate_capture.py"
MARKER_RE = re.compile(r"^\s*DECISION_CAPTURED:\s.+$", re.MULTILINE)
TIMEOUT_SECONDS = 120


def _extract_markers(text: str) -> list[str]:
    return [m.group(0).strip() for m in MARKER_RE.finditer(text)]


def _invoke_hook(marker: str) -> tuple[int, str]:
    """Invoke the capture hook with ``marker`` wrapped in the Cursor payload shape."""
    payload = json.dumps({"tool_info": {"response": marker}})
    try:
        result = subprocess.run(
            [sys.executable, str(HOOK_SCRIPT)],
            cwd=str(REPO_ROOT),
            input=payload,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=TIMEOUT_SECONDS,
            shell=False,
            check=False,
        )
        tail = (result.stderr or result.stdout or "").strip().splitlines()
        summary = tail[-1] if tail else "(no output)"
        return result.returncode, summary
    except subprocess.TimeoutExpired:
        return 124, "TIMEOUT"
    except FileNotFoundError as exc:
        return 127, f"FileNotFoundError: {exc}"


def _read_input(args: argparse.Namespace) -> str:
    if args.file:
        path = Path(args.file)
        if not path.exists():
            print(f"[capture_author_gate] file not found: {path}", file=sys.stderr)
            sys.exit(2)
        return path.read_text(encoding="utf-8")
    if args.stdin:
        if sys.stdin.isatty():
            print("[capture_author_gate] --stdin requires piped input.", file=sys.stderr)
            sys.exit(2)
        return sys.stdin.read()
    if args.marker:
        return " ".join(args.marker)
    print(
        "[capture_author_gate] supply a marker as arg, --file PATH, or --stdin.",
        file=sys.stderr,
    )
    sys.exit(2)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Inline DECISION_CAPTURED bypass for Cursor 2.0.67 hook-dark window."
    )
    parser.add_argument("marker", nargs="*", help="DECISION_CAPTURED marker text")
    parser.add_argument("--file", help="Read markers from file (one per line)")
    parser.add_argument("--stdin", action="store_true", help="Read markers from stdin")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    if not HOOK_SCRIPT.exists():
        print(f"[capture_author_gate] hook script missing: {HOOK_SCRIPT}", file=sys.stderr)
        return 2

    text = _read_input(args)
    markers = _extract_markers(text)
    if not markers:
        print("[capture_author_gate] no DECISION_CAPTURED markers found in input.", file=sys.stderr)
        return 2

    failures = 0
    for i, marker in enumerate(markers, 1):
        rc, summary = _invoke_hook(marker)
        if rc != 0:
            failures += 1
            print(f"[capture_author_gate] marker {i}/{len(markers)} FAILED rc={rc}: {summary}", file=sys.stderr)
            continue
        if args.verbose:
            print(f"[capture_author_gate] marker {i}/{len(markers)} OK: {summary}", file=sys.stderr)

    if args.verbose or failures:
        print(
            f"[capture_author_gate] captured {len(markers) - failures}/{len(markers)} marker(s).",
            file=sys.stderr,
        )
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
