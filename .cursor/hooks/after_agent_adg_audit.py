"""afterAgentResponse — ADG-first grep-for-deps audit (delegates to post_cursor_agent_adg_audit)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ADG_AUDIT = REPO_ROOT / ".cursor" / "scripts" / "post_cursor_agent_adg_audit.py"


def main() -> int:
    if sys.stdin.isatty():
        return 0
    raw = sys.stdin.read()
    if not raw.strip():
        return 0
    if not ADG_AUDIT.is_file():
        return 0
    try:
        proc = subprocess.run(
            [sys.executable, str(ADG_AUDIT)],
            input=raw,
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
            env={
                **dict(__import__("os").environ),
                "PYTHONPATH": str(REPO_ROOT),
            },
        )
        if proc.stderr:
            sys.stderr.write(proc.stderr)
            if not proc.stderr.endswith("\n"):
                sys.stderr.write("\n")
        return proc.returncode
    except (subprocess.TimeoutExpired, OSError):
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
