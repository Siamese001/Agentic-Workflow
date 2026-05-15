"""afterAgentResponse — advisory Notion Plans/Backlog status canonicalization audit (SSOT auditor)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
AUDITOR = REPO_ROOT / "tools" / "notion" / "unified_notion_status_auditor.py"


def main() -> int:
    if sys.stdin.isatty():
        return 0
    raw = sys.stdin.read()
    if not raw.strip():
        return 0
    if not AUDITOR.is_file():
        return 0
    env = {**__import__("os").environ, "PYTHONPATH": str(REPO_ROOT)}
    env.setdefault("NOTION_STATUS_VIOLATIONS_VENDOR", "cursor")
    try:
        proc = subprocess.run(
            [sys.executable, str(AUDITOR)],
            input=raw,
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=90,
            check=False,
            env=env,
        )
        if proc.stderr:
            sys.stderr.write(proc.stderr)
            if not proc.stderr.endswith("\n"):
                sys.stderr.write("\n")
        return 0
    except (subprocess.TimeoutExpired, OSError):
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
