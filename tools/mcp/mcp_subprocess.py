"""
Shared MCP-safe subprocess execution.

MCP servers using stdio transport MUST NOT let child processes inherit
stdin/stdout.  Child processes that read from stdin steal bytes from the
JSON-RPC stream; child processes that write to stdout inject garbage into
the protocol.

This module provides a single function that enforces:
- stdin  = DEVNULL  (never inherit parent stdin)
- stdout = PIPE     (capture, never write to parent stdout)
- stderr = PIPE     (capture, never write to parent stderr)
- timeout required  (constitutional §14)

Root cause reference: GitHub modelcontextprotocol/python-sdk#671

Usage::

    from tools.mcp.mcp_subprocess import safe_run

    result = safe_run(["git", "rev-parse", "--short", "HEAD"], timeout=5)
    if result.returncode == 0:
        sha = result.stdout.strip()
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT: Path = Path(__file__).resolve().parents[2]


def safe_run(
    cmd: list[str],
    *,
    timeout: int = 30,
    cwd: str | Path | None = None,
    text: bool = True,
    env: dict[str, str] | None = None,
    check: bool = False,
) -> subprocess.CompletedProcess[Any]:
    """Run a subprocess safely within an MCP stdio server.

    Forces stdin=DEVNULL, stdout=PIPE, stderr=PIPE to prevent
    the child process from corrupting the MCP JSON-RPC transport.

    Args:
        cmd: Command and arguments as a list
        timeout: Maximum seconds to wait (constitutional §14 — required)
        cwd: Working directory (defaults to repo root)
        text: Decode stdout/stderr as text (default True)
        env: Optional environment overrides (merged with os.environ)
        check: Raise CalledProcessError on non-zero exit

    Returns:
        subprocess.CompletedProcess with captured stdout/stderr

    Raises:
        subprocess.TimeoutExpired: If command exceeds timeout
        subprocess.CalledProcessError: If check=True and returncode != 0
    """
    import os

    run_env = None
    if env is not None:
        run_env = {**os.environ, **env}

    return subprocess.run(
        cmd,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=text,
        timeout=timeout,
        cwd=str(cwd) if cwd else str(REPO_ROOT),
        env=run_env,
        check=check,
    )
