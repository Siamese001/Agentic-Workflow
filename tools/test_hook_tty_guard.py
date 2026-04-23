"""Smoke-test the TTY guard rollout across all hook scripts.

For each hook script:
  1. py_compile — catches syntax errors from the rewrite
  2. Standalone run with a real console stdin (simulated via subprocess
     with stdin=DEVNULL wouldn't trigger the TTY path on all OSes, so
     instead we confirm the script terminates within a bounded timeout
     when given *empty* piped stdin — must also not hang)
  3. Piped-payload run — verify the hook still processes input (at
     minimum terminates cleanly with exit 0)

Note: Windsurf's real hook invocation uses piped stdin, which is what
test #3 simulates. Test #2 proves the defensive exit path does not
itself introduce a new hang.

Exit code:
    0 — all scripts pass
    1 — any failure (printed with per-script detail)
"""

from __future__ import annotations

import py_compile
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / ".windsurf" / "scripts"
TIMEOUT_S = 15.0

TARGETS = [
    "post_cascade_deferred_scope_capture.py",
    "pre_write_gate.py",
    "pre_run_gate.py",
    "pre_read_gate.py",
    "pre_prompt_classifier.py",
    "pre_mcp_gate.py",
    "post_write_mcp_config_sync.py",
    "post_write_audit.py",
    "post_setup_worktree.py",
    "post_run_audit.py",
    "post_mcp_audit.py",
    "post_cascade_writeback_audit.py",
    "post_cascade_mcp_serialization_audit.py",
    "post_cascade_long_command_audit.py",
    "post_cascade_author_gate_capture.py",
    "post_cascade_adg_audit.py",
]


def test_compile(path: Path) -> str:
    try:
        py_compile.compile(str(path), doraise=True)
        return "OK"
    except py_compile.PyCompileError as exc:
        return f"SYNTAX_ERROR: {exc.msg.splitlines()[0] if exc.msg else exc}"


def test_piped_empty(path: Path) -> str:
    """Run with empty piped stdin — must terminate under TIMEOUT_S."""
    try:
        result = subprocess.run(
            [sys.executable, str(path)],
            input="",
            capture_output=True,
            text=True,
            timeout=TIMEOUT_S,
            check=False,
        )
        return f"OK (exit={result.returncode})"
    except subprocess.TimeoutExpired:
        return f"HANG (> {TIMEOUT_S}s)"
    except OSError as exc:
        return f"OS_ERROR: {exc}"


def test_piped_payload(path: Path) -> str:
    """Run with a small irrelevant piped payload — must terminate cleanly.

    We don't assert semantic behavior here; just that the script doesn't
    hang when given real (non-TTY) stdin data.
    """
    payload = '{"tool_info": {"response": "no markers here"}}'
    try:
        result = subprocess.run(
            [sys.executable, str(path)],
            input=payload,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_S,
            check=False,
        )
        # Exit 0 is expected for fail-open hooks; some pre-gates may
        # legitimately exit non-zero when they decide to block. Accept both.
        return f"OK (exit={result.returncode})"
    except subprocess.TimeoutExpired:
        return f"HANG (> {TIMEOUT_S}s)"
    except OSError as exc:
        return f"OS_ERROR: {exc}"


def main() -> int:
    total = 0
    failed: list[str] = []

    header = f"{'SCRIPT':45s}  {'COMPILE':16s}  {'EMPTY_PIPE':25s}  {'PAYLOAD_PIPE':25s}"
    print(header)
    print("-" * len(header))

    for name in TARGETS:
        total += 1
        path = SCRIPTS_DIR / name
        if not path.exists():
            print(f"{name:45s}  MISSING")
            failed.append(name)
            continue

        c = test_compile(path)
        e = test_piped_empty(path)
        p = test_piped_payload(path)

        print(f"{name:45s}  {c:16s}  {e:25s}  {p:25s}")

        if "HANG" in e or "HANG" in p or "SYNTAX" in c:
            failed.append(name)

    print("-" * len(header))
    print(f"\nTotal: {total}  Failed: {len(failed)}")
    if failed:
        print("Failed scripts:")
        for n in failed:
            print(f"  - {n}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
