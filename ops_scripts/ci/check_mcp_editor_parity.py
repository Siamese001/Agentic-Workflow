#!/usr/bin/env python3
"""MCP editor parity gate — Cursor SSOT plus optional compatibility copy.

Ensures the Cursor config declares the canonical MCP fleet. A deprecated
Windsurf compatibility copy is checked only when it exists.

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
    cursor_servers = _load_servers(CURSOR_MCP_PATH)

    cursor_canon = canonical_server_set(cursor_servers)

    issues: list[str] = []

    for profile, required in MCP_PROFILES.items():
        path = profile_config_path(profile)
        if not path.exists():
            if profile == "windsurf":
                continue
            issues.append(f"{profile}: missing config path {path}")
            continue
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
            "[check_mcp_editor_parity] Fix: align .cursor/mcp.json (Cursor SSOT); "
            "deprecated compatibility copies are non-authoritative.",
            file=sys.stderr,
        )
        return 1

    print(
        "[check_mcp_editor_parity] OK: Cursor MCP config declares "
        f"{len(cursor_canon)} canonical servers."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
