#!/usr/bin/env python3
# DEPRECATED: canonical launch path is `python -m tools.adg.mcp.server`
# (configured in .windsurf/mcp_config.json).  This file is retained for
# emergency manual use only.  Do not reference from mcp_config.json.
"""ADG MCP Server launcher — DEPRECATED thin wrapper (use -m tools.adg.mcp.server)."""

import logging
import os
import sys
from pathlib import Path

logging.basicConfig(
    filename=os.path.expanduser("~/adg_mcp_launcher.log"),
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
)
_fallback_log = logging.getLogger("adg_mcp.launcher")


def _resolve_repo_root() -> Path:
    """Resolve the repository root from this launcher path."""
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "tools" / "adg" / "mcp" / "server.py").exists():
            return parent
    raise RuntimeError(f"Could not resolve repository root from {here}")


def _bootstrap_repo() -> Path:
    repo_root = _resolve_repo_root()
    os.chdir(repo_root)
    repo_root_str = str(repo_root)
    if repo_root_str not in sys.path:
        sys.path.insert(0, repo_root_str)
    return repo_root


def main() -> int:
    """Run the deprecated launcher in the safest way possible."""
    try:
        repo_root = _bootstrap_repo()
        from tools.adg.mcp.server import _init_service, _log, mcp

        _log.warning("Starting deprecated adg_mcp launcher from %s", repo_root)
        _init_service()
    except Exception as exc:  # guardian: allow-broad-exception -- emergency launcher must log and exit cleanly on bootstrap failure
        _fallback_log.exception("FATAL: Could not initialize ADGService from deprecated launcher: %s", exc)
        return 1

    mcp.run(transport="stdio")
    _log.info("Server exited")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
