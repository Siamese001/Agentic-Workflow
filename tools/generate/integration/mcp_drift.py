"""MCP config drift check integration for ADG generation."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def _check_mcp_config_drift() -> None:
    """Check for MCP config drift between YAML and global config."""
    print("[ADG] Checking MCP config drift...")
    yaml_config_path = ROOT / "config" / "mcp_servers.yaml"
    global_config_path = Path.home() / ".codeium" / "windsurf" / "mcp_config.json"

    if yaml_config_path.exists() and global_config_path.exists():
        try:
            from agentic_core.config.mcp_loader import MCPLoader

            loader = MCPLoader(yaml_config_path)
            yaml_config = loader.load()
            yaml_count = len([s for s in yaml_config.servers.values() if s.enabled])

            with open(global_config_path, encoding="utf-8") as f:
                global_config = json.load(f)
            global_count = len(global_config.get("mcpServers", {}))

            if yaml_count != global_count:
                print("[WARNING] MCP config drift detected!")
                print(f"[WARNING]   YAML enabled servers: {yaml_count}")
                print(f"[WARNING]   Global enabled servers: {global_count}")
                print("[WARNING]   Run: python tools/adg/sync_yaml_to_global.py")
                print("[WARNING]   Proceeding with ADG generation...")
            else:
                print("[ADG] MCP config is in sync")
        except Exception as e:  # guardian: allow-broad-exception -- non-critical: MCP config drift check failure should not block ADG generation
            print(f"[WARNING] Could not check MCP config drift: {e}")
            print("[WARNING]   Proceeding with ADG generation...")
    else:
        print("[WARNING] MCP config files not found, skipping drift check")
