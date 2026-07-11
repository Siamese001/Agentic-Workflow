#!/usr/bin/env python3
"""afterMcpExecution - PostToolUse relay for MCP-specific completion capture.

Records active-session MCP callability proof after successful required-route
MCP calls. PostToolUse hooks never block.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPT = _REPO_ROOT / ".codex" / "governance" / "scripts" / "post_adg_mcp_callable_proof.py"


def main() -> int:
    try:
        raw = sys.stdin.read()
    except OSError:
        return 0
    if not _SCRIPT.is_file():
        return 0
    try:
        proc = subprocess.run(
            [sys.executable, str(_SCRIPT)],
            input=raw,
            cwd=str(_REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
            env={**os.environ, "PYTHONPATH": str(_REPO_ROOT)},
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        sys.stderr.write(f"after_mcp_execution: capture unreachable ({exc}) - ignoring\n")
        return 0
    if proc.stderr:
        sys.stderr.write(proc.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
