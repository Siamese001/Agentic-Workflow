#!/usr/bin/env python3
"""
check_agents_mcp_coverage.py — CI gate: every MCP server in mcp_config.json
must be documented in the AGENTS.md MCP Quick Reference table.

Exit 0: all servers covered.
Exit 1: one or more servers missing from AGENTS.md.

Usage:
    python ops_scripts/ci/check_agents_mcp_coverage.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MCP_CONFIG = REPO_ROOT / ".windsurf" / "mcp_config.json"
AGENTS_MD = REPO_ROOT / "AGENTS.md"

# Matches `server: `<name>`` patterns used in the AGENTS.md Quick Reference table
_SERVER_REF_RE = re.compile(r"server:\s*`([^`]+)`")


def load_registered_servers(config_path: Path) -> list[str]:
    data = json.loads(config_path.read_text(encoding="utf-8"))
    return list(data.get("mcpServers", {}).keys())


def load_documented_servers(agents_path: Path) -> set[str]:
    text = agents_path.read_text(encoding="utf-8")
    return set(_SERVER_REF_RE.findall(text))


def main() -> int:
    if not MCP_CONFIG.exists():
        print(f"[agents_mcp_coverage] SKIP: {MCP_CONFIG} not found", flush=True)
        return 0
    if not AGENTS_MD.exists():
        print(f"[agents_mcp_coverage] FAIL: {AGENTS_MD} not found", flush=True)
        return 1

    registered = load_registered_servers(MCP_CONFIG)
    documented = load_documented_servers(AGENTS_MD)

    missing = [s for s in registered if s not in documented]

    if missing:
        print(
            f"[agents_mcp_coverage] FAIL: {len(missing)} MCP server(s) registered in "
            f"mcp_config.json but NOT documented in AGENTS.md Quick Reference:",
            flush=True,
        )
        for name in missing:
            print(f"  MISSING: {name}", flush=True)
        print(
            "[agents_mcp_coverage] Add a row per missing server to the "
            "'## MCP Quick Reference' table in AGENTS.md.",
            flush=True,
        )
        return 1

    print(
        f"[agents_mcp_coverage] OK: all {len(registered)} MCP server(s) documented in AGENTS.md.",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
