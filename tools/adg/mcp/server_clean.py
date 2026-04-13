#!/usr/bin/env python3
"""ADG MCP Server launcher - clean stdio version."""

import logging
import os
import sys
from pathlib import Path

# Redirect logs to file instead of stderr
log_file = os.path.expanduser("~/adg_mcp.log")
logging.basicConfig(filename=log_file, level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")
_log = logging.getLogger("adg_mcp.clean")


def _resolve_repo_root() -> Path:
    """Resolve the repository root without relying on a machine-specific path."""
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
    """Initialize and run the MCP server over stdio."""
    try:
        repo_root = _bootstrap_repo()
        _log.info("Bootstrapped repository root: %s", repo_root)
        from tools.adg.mcp.server import _init_service, mcp

        _init_service()
    except Exception as exc:  # guardian: allow-broad-exception -- emergency launcher must fail closed with durable logs
        _log.exception("FATAL during clean launcher startup: %s", exc)
        return 1

    mcp.run(transport="stdio")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
