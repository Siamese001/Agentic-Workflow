#!/usr/bin/env python3
"""
MCP Config Windows npx Gate — CI Pre-commit Gate

Blocks commits that introduce bare 'npx' as a command in config/mcp_servers.yaml.
On Windows, bare 'npx' is not resolvable — 'npx.cmd' is required.

This prevents the silent hang where Windsurf cannot start npx-based MCP servers.

Exit codes:
    0 = no bare npx found (or not Windows)
    1 = bare npx found in mcp_servers.yaml (blocks commit)
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
YAML_PATH = REPO_ROOT / "config" / "mcp_servers.yaml"


def check_npx_commands() -> int:
    if not YAML_PATH.exists():
        print(f"[SKIP] {YAML_PATH} not found")
        return 0

    content = YAML_PATH.read_text(encoding="utf-8")
    violations: list[str] = []

    for i, line in enumerate(content.splitlines(), start=1):
        stripped = line.strip()
        # Match: command: "npx" or command: npx (bare, not npx.cmd)
        if stripped in ('command: "npx"', "command: npx", "command: 'npx'"):
            violations.append(f"  Line {i}: {line.rstrip()}")

    if violations:
        print("[FAIL] Bare 'npx' command found in config/mcp_servers.yaml")
        print("       On Windows, 'npx' is not executable — use 'npx.cmd' instead.")
        print("       This causes silent MCP hangs in Windsurf.\n")
        for v in violations:
            print(v)
        print("\n[FIX]  Replace 'command: \"npx\"' with 'command: \"npx.cmd\"' in mcp_servers.yaml")
        print("       Then run: python tools/adg/sync_yaml_to_global.py")
        return 1

    print(f"[OK] No bare npx commands in {YAML_PATH.name}")
    return 0


if __name__ == "__main__":
    sys.exit(check_npx_commands())
