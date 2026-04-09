"""MCP config drift check integration for ADG generation."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def _check_mcp_config_drift() -> None:
    """Check for MCP config drift between repo SSOT and global Windsurf config.

    SSOT: .windsurf/mcp_config.json (mcpServers format)
    Global: ~/.codeium/windsurf/mcp_config.json (Windsurf reads this at startup)
    """
    print("[ADG] Checking MCP config drift...")
    repo_ssot = ROOT / ".windsurf" / "mcp_config.json"
    global_config_path = Path.home() / ".codeium" / "windsurf" / "mcp_config.json"

    if not repo_ssot.exists():
        print(f"[WARNING] Repo SSOT not found: {repo_ssot} — skipping drift check")
        return
    if not global_config_path.exists():
        print(f"[WARNING] Global config not found: {global_config_path} — skipping drift check")
        return

    try:
        repo_cfg = json.loads(repo_ssot.read_text(encoding="utf-8"))
        global_cfg = json.loads(global_config_path.read_text(encoding="utf-8"))

        repo_servers = set(repo_cfg.get("mcpServers", {}).keys())
        global_servers = set(global_cfg.get("mcpServers", {}).keys())

        added = repo_servers - global_servers
        removed = global_servers - repo_servers

        if added or removed:
            print("[WARNING] MCP config drift detected!")
            if added:
                print(f"[WARNING]   In repo SSOT but not global: {sorted(added)}")
            if removed:
                print(f"[WARNING]   In global but not repo SSOT: {sorted(removed)}")
            print("[WARNING]   Edit .windsurf/mcp_config.json and copy to global config.")
            print("[WARNING]   Proceeding with ADG generation...")
        else:
            print(f"[ADG] MCP config in sync ({len(repo_servers)} servers)")
    except (
        json.JSONDecodeError,
        OSError,
    ) as exc:  # guardian: allow-broad-exception -- non-critical: drift check failure must not block ADG generation
        print(f"[WARNING] Could not check MCP config drift: {exc}")
        print("[WARNING]   Proceeding with ADG generation...")
