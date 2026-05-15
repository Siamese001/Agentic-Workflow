#!/usr/bin/env python3
"""MCP editor parity gate — Cursor SSOT vs Windsurf mirror.

Ensures both editor configs declare the same canonical MCP fleet (14 servers)
with only documented per-editor deltas (GitKraken host flags, Playwright id,
filesystem launcher path).

Bypass: MCP_EDITOR_PARITY_BYPASS=1
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

_CI_DIR = Path(__file__).resolve().parent
if str(_CI_DIR) not in sys.path:
    sys.path.insert(0, str(_CI_DIR))

from _mcp_ci_common import (  # noqa: E402
    CURSOR_MCP_PATH,
    MCP_PROFILES,
    WINDSURF_MCP_PATH,
    canonical_server_set,
    load_mcp_json,
    profile_config_path,
)


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

    if not CURSOR_MCP_PATH.exists():
        print(f"[check_mcp_editor_parity] FAIL: missing {CURSOR_MCP_PATH}", file=sys.stderr)
        return 1
    if not WINDSURF_MCP_PATH.exists():
        print(f"[check_mcp_editor_parity] FAIL: missing {WINDSURF_MCP_PATH}", file=sys.stderr)
        return 1

    cursor_servers = _load_servers(CURSOR_MCP_PATH)
    windsurf_servers = _load_servers(WINDSURF_MCP_PATH)

    cursor_canon = canonical_server_set(cursor_servers)
    windsurf_canon = canonical_server_set(windsurf_servers)

    issues: list[str] = []

    if len(cursor_servers) != len(windsurf_servers):
        issues.append(
            f"server count mismatch: cursor={len(cursor_servers)} windsurf={len(windsurf_servers)}"
        )

    only_cursor = cursor_canon - windsurf_canon
    only_windsurf = windsurf_canon - cursor_canon
    if only_cursor:
        issues.append(f"canonical servers only in Cursor config: {sorted(only_cursor)}")
    if only_windsurf:
        issues.append(f"canonical servers only in Windsurf config: {sorted(only_windsurf)}")

    for profile, required in MCP_PROFILES.items():
        path = profile_config_path(profile)
        present = set(_load_servers(path))
        missing_required = required - present
        if missing_required:
            issues.append(
                f"{profile}: missing required servers: {sorted(missing_required)}"
            )

    if issues:
        print("[check_mcp_editor_parity] FAIL:", file=sys.stderr)
        for issue in issues:
            print(f"  - {issue}", file=sys.stderr)
        print(
            "[check_mcp_editor_parity] Fix: align .cursor/mcp.json (Cursor SSOT) and "
            ".windsurf/mcp_config.json (mirror); run python .cursor/scripts/sync_mcp_config.py",
            file=sys.stderr,
        )
        return 1

    print(
        "[check_mcp_editor_parity] OK: Cursor and Windsurf MCP configs share "
        f"{len(cursor_canon)} canonical servers."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
