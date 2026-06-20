#!/usr/bin/env python3
"""
check_agents_mcp_coverage.py — CI gate: every MCP server in root .mcp.json
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

_CI_DIR = Path(__file__).resolve().parent
if str(_CI_DIR) not in sys.path:
    sys.path.insert(0, str(_CI_DIR))

from _mcp_ci_common import AGENTS_MD, REPO_MCP_PATH  # noqa: E402

# Matches the first backtick-quoted cell of each Quick Reference table row:
#   | `GitKraken` | Git operations ... |
_SERVER_REF_RE = re.compile(r"^\|\s*`([^`]+)`\s*\|", re.MULTILINE)


def load_registered_servers(config_path: Path) -> list[str]:
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"could not read {config_path}: {exc}") from exc

    servers = data.get("mcpServers", {})
    if not isinstance(servers, dict):
        raise RuntimeError(f"{config_path} has invalid mcpServers payload (expected object)")
    return sorted(servers.keys())


def load_documented_servers(agents_path: Path) -> set[str]:
    try:
        text = agents_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise RuntimeError(f"could not read {agents_path}: {exc}") from exc
    return set(_SERVER_REF_RE.findall(text))


def _check_config(
    label: str,
    config_path: Path,
    documented: set[str],
    *,
    required: bool = True,
) -> list[str]:
    if not config_path.exists():
        return [f"{label} config missing at {config_path}"] if required else []
    registered = load_registered_servers(config_path)
    return [name for name in registered if name not in documented]


def main() -> int:
    if not AGENTS_MD.exists():
        print(f"[agents_mcp_coverage] FAIL: {AGENTS_MD} not found", flush=True)
        return 1

    try:
        documented = load_documented_servers(AGENTS_MD)
    except RuntimeError as exc:
        print(f"[agents_mcp_coverage] FAIL: {exc}", flush=True)
        return 1

    missing_repo = _check_config("repo", REPO_MCP_PATH, documented)

    if missing_repo:
        print(
            f"[agents_mcp_coverage] FAIL: {len(missing_repo)} repo MCP server(s) "
            "registered in .mcp.json but NOT documented in AGENTS.md:",
            flush=True,
        )
        for name in missing_repo:
            print(f"  MISSING: {name}", flush=True)
        print(
            "[agents_mcp_coverage] Run: python .codex/governance/scripts/sync_mcp_config.py",
            flush=True,
        )
        return 1

    root_count = len(load_registered_servers(REPO_MCP_PATH))
    print(
        f"[agents_mcp_coverage] OK: all {root_count} repo MCP server(s) documented in AGENTS.md.",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
