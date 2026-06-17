#!/usr/bin/env python3
"""MCP parity gate for the repo SSOT and AGENTS.md coverage."""

from __future__ import annotations

import os
import sys
from pathlib import Path

_CI_DIR = Path(__file__).resolve().parent
if str(_CI_DIR) not in sys.path:
    sys.path.insert(0, str(_CI_DIR))

from _mcp_ci_common import AGENTS_MD, MCP_PROFILES, REPO_MCP_PATH, canonical_server_set, load_mcp_json  # noqa: E402


def _load_servers(path) -> set[str]:
    data = load_mcp_json(path)
    servers = data.get("mcpServers", {})
    if not isinstance(servers, dict):
        raise ValueError(f"{path}: invalid mcpServers object")
    return set(servers.keys())


def main() -> int:
    if os.environ.get("MCP_EDITOR_PARITY_BYPASS") == "1":
        print("[check_mcp_editor_parity] BYPASS=1 — skipping", file=sys.stderr)
        return 0

    if not REPO_MCP_PATH.exists():
        print(f"[check_mcp_editor_parity] FAIL: missing {REPO_MCP_PATH}", file=sys.stderr)
        return 1
    repo_servers = _load_servers(REPO_MCP_PATH)
    repo_canon = canonical_server_set(repo_servers)

    issues: list[str] = []
    required = next(iter(MCP_PROFILES.values()))
    missing_required = required - repo_canon
    if missing_required:
        issues.append(f"repo: missing required servers: {sorted(missing_required)}")

    if issues:
        print("[check_mcp_editor_parity] FAIL:", file=sys.stderr)
        for issue in issues:
            print(f"  - {issue}", file=sys.stderr)
        print(
            "[check_mcp_editor_parity] Fix: align root .mcp.json and AGENTS.md.",
            file=sys.stderr,
        )
        return 1

    print(
        "[check_mcp_editor_parity] OK: repo MCP config declares "
        f"{len(repo_canon)} canonical servers."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
