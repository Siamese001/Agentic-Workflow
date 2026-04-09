#!/usr/bin/env python3
"""
post_write_mcp_sync.py — Windsurf post_write_code hook.

Triggered when config/mcp_servers.yaml is written (via file_pattern in hooks.json).
Runs tools/adg/sync_yaml_to_global.py to propagate YAML SSOT changes to the
global Windsurf MCP config (~/.codeium/windsurf/mcp_config.json).

Fail policy: OPEN — sync failure is printed as a warning but never blocks Cascade.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SYNC_SCRIPT = REPO_ROOT / "tools" / "adg" / "sync_yaml_to_global.py"
YAML_SSOT = REPO_ROOT / "config" / "mcp_servers.yaml"


def main() -> int:
    raw = sys.stdin.read()
    if raw.strip():
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            payload = {}
        tool_info = payload.get("tool_info", payload) if isinstance(payload, dict) else {}
        file_path = tool_info.get("file_path", "") if isinstance(tool_info, dict) else ""
        if file_path and "mcp_servers.yaml" not in file_path:
            return 0

    if not SYNC_SCRIPT.exists():
        print(
            f"[post_write_mcp_sync] WARNING: sync script not found at {SYNC_SCRIPT}",
            file=sys.stderr,
        )
        return 0

    if not YAML_SSOT.exists():
        print(
            f"[post_write_mcp_sync] WARNING: YAML SSOT not found at {YAML_SSOT}",
            file=sys.stderr,
        )
        return 0

    print("[post_write_mcp_sync] mcp_servers.yaml changed — syncing to global Windsurf config...")

    try:
        result = subprocess.run(
            [sys.executable, str(SYNC_SCRIPT)],
            shell=False,
            capture_output=False,
            timeout=30,
            check=False,
            cwd=str(REPO_ROOT),
        )
        if result.returncode != 0:
            print(
                f"[post_write_mcp_sync] WARNING: sync exited with code {result.returncode}. "
                "Global config may be stale — run: python tools/adg/sync_yaml_to_global.py",
                file=sys.stderr,
            )
        else:
            print("[post_write_mcp_sync] Global config synced. Restart Windsurf to apply changes.")
    except subprocess.TimeoutExpired:
        print(
            "[post_write_mcp_sync] WARNING: sync timed out (30s). "
            "Run manually: python tools/adg/sync_yaml_to_global.py",
            file=sys.stderr,
        )
    except OSError as exc:
        print(f"[post_write_mcp_sync] WARNING: sync failed: {exc}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
