#!/usr/bin/env python3
# DEPRECATED: canonical launch path is `python -m tools.adg.mcp.server`
# (configured in .cursor/mcp.json).  This file is retained for
# emergency manual use only.  Do not reference from mcp_config.json.
"""ADG MCP Server — DEPRECATED direct entry point (use -m tools.adg.mcp.server)."""

from __future__ import annotations

import os
import sys
from pathlib import Path


def _repo_root() -> Path:
    """Resolve the repository root from this file location."""
    return Path(__file__).resolve().parents[2]


def _bootstrap_repo() -> Path:
    """Ensure imports and cwd are aligned with the repository root."""
    repo_root = _repo_root()
    repo_root_str = str(repo_root)
    if repo_root_str not in sys.path:
        sys.path.insert(0, repo_root_str)
    os.chdir(repo_root)
    return repo_root


_BOOTSTRAPPED_ROOT = _bootstrap_repo()

# Import and run the actual server
from tools.adg.mcp.server import _init_service, mcp


def _fatal_log_path() -> Path:
    raw = os.getenv("ADG_FATAL_LOG", "~/adg_fatal.log")
    return Path(os.path.expanduser(raw))


def _write_fatal_log(exc: Exception) -> None:
    """Best-effort fatal logging that never masks the original failure."""
    log_path = _fatal_log_path()
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_text(f"FATAL: {type(exc).__name__}: {exc}\n", encoding="utf-8")
    except OSError:
        pass


def main() -> int:
    try:
        _init_service()
        mcp.run(transport="stdio")
        return 0
    except KeyboardInterrupt:
        return 130
    except Exception as exc:  # guardian: allow-broad-exception -- stdio MCP must fail closed and log locally without writing to stderr
        _write_fatal_log(exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
