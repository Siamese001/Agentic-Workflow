"""In-response DEFERRED_SCOPE capture helper.

Bypass for Windsurf 2.0.67 bug where `post_cascade_response` hooks silently
stop firing mid-session. Cascade invokes this directly via `run_command`
in the same response that emits DEFERRED_SCOPE markers, guaranteeing
capture without depending on the broken hook channel.

Usage
-----
    # From CLI args (one marker):
    python .windsurf/scripts/defer.py "DEFERRED_SCOPE: plan=foo-abc123 wave=W1 phase=W1.A layer=L0 fan_in=5 surface=None coverage_gap_pct=10.0 est_tokens=100 reason=test"

    # From stdin (one or more markers, one per line):
    echo "DEFERRED_SCOPE: ..." | python .windsurf/scripts/defer.py --stdin

    # From a file:
    python .windsurf/scripts/defer.py --file markers.txt

Under the hood
--------------
Wraps each marker in the Windsurf payload shape
`{"tool_info": {"response": "<marker>"}}` and invokes
`post_cascade_deferred_scope_capture.py` — same code path the hook chain
would run. Result: same Notion row, same scorer, same JSONL log, same
snapshot regeneration. Zero drift from the hook-triggered path.

Exit codes
----------
0  all markers captured successfully
1  at least one marker failed
2  invalid input (no markers found, unreadable file)
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
HOOK_SCRIPT = REPO_ROOT / ".windsurf" / "scripts" / "post_cascade_deferred_scope_capture.py"
MARKER_RE = re.compile(r"^\s*DEFERRED_SCOPE:\s.+$", re.MULTILINE)
TIMEOUT_SECONDS = 120


def _extract_markers(text: str) -> list[str]:
    return [m.group(0).strip() for m in MARKER_RE.finditer(text)]


def _invoke_hook(marker: str) -> tuple[int, str]:
    payload = json.dumps({"tool_info": {"response": marker}})
    try:
        result = subprocess.run(  # noqa: S603
            [sys.executable, str(HOOK_SCRIPT)],
            cwd=str(REPO_ROOT),
            input=payload,
            capture_output=True,
            text=True,
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
            print(f"[defer] file not found: {path}", file=sys.stderr)
            sys.exit(2)
        return path.read_text(encoding="utf-8")
    if args.stdin:
        if sys.stdin.isatty():
            print("[defer] --stdin requires piped input.", file=sys.stderr)
            sys.exit(2)
        return sys.stdin.read()
    if args.marker:
        return " ".join(args.marker)
    print("[defer] supply a marker, --stdin, or --file.", file=sys.stderr)
    sys.exit(2)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument(
        "marker",
        nargs="*",
        help="DEFERRED_SCOPE marker string (quote it).",
    )
    src = parser.add_mutually_exclusive_group()
    src.add_argument("--stdin", action="store_true", help="Read markers from stdin.")
    src.add_argument("--file", help="Read markers from this file.")
    args = parser.parse_args()

    text = _read_input(args)
    markers = _extract_markers(text)
    if not markers:
        print("[defer] no DEFERRED_SCOPE markers found in input.", file=sys.stderr)
        return 2

    print(f"[defer] capturing {len(markers)} marker(s)")
    failed = 0
    for i, marker in enumerate(markers, start=1):
        phase = next(
            (tok.split("=", 1)[1] for tok in marker.split() if tok.startswith("phase=")),
            "?",
        )
        rc, summary = _invoke_hook(marker)
        status = "OK" if rc == 0 else f"FAIL rc={rc}"
        print(f"  [{i}/{len(markers)}] phase={phase:<15} {status:<10} {summary}")
        if rc != 0:
            failed += 1

    if failed:
        print(f"[defer] {failed} marker(s) failed. Check stderr above.", file=sys.stderr)
        return 1
    print("[defer] all markers captured.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
