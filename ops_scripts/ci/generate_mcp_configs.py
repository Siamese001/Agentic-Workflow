#!/usr/bin/env python3
"""
Unified MCP Config Generator

Generates both workspace and user-global configs from a single canonical manifest.
Prevents drift between config locations.

Usage:
  python generate_mcp_configs.py --check    # Validate configs are in sync
  python generate_mcp_configs.py --generate # Regenerate both configs from manifest
"""
import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
MANIFEST_PATH = REPO_ROOT / ".windsurf" / "mcp_manifest.json"
WORKSPACE_CONFIG_PATH = REPO_ROOT / ".windsurf" / "mcp_config.json"
USER_GLOBAL_CONFIG_PATH = Path.home() / ".codeium" / "windsurf" / "mcp_config.json"

# Canonical MCP Manifest - Single Source of Truth
CANONICAL_MANIFEST = {
    "_schema": "mcp-manifest-v1",
    "_comment": "Canonical manifest for generating workspace and user-global configs",
    "mcpServers": {
        "adg_redis": {
            "_type": "local_python",
            "_description": "ADG-aware Redis MCP with HASH/SET/LIST operations",
            "command": "python",
            "args": ["C:\\Git\\Agentic-Workflow\\tools\\adg\\adg_mcp_server.py"],
            "cwd": "C:\\Git\\Agentic-Workflow",
            "disabled": False,
            "env": {
                "ADG_REDIS_URL": "redis://localhost:6379/0",
                "ADG_DIR": "C:\\Git\\Agentic-Workflow\\artifacts\\adg",
                "ADG_MCP_PAGE_SIZE": "500",
                "ADG_MCP_CACHE_META_TTL": "5",
            },
        },
        "memory": {
            "_type": "local_python",
            "_description": "Persistent memory/knowledge graph MCP",
            "command": "python",
            "args": ["C:\\Git\\Agentic-Workflow\\tools\\memory\\adg_memory_server.py"],
            "cwd": "C:\\Git\\Agentic-Workflow",
            "disabled": False,
            "env": {
                "ADG_REDIS_URL": "redis://localhost:6379/0",
                "MEMORY_DB": "C:\\Git\\Agentic-Workflow\\artifacts\\memory\\knowledge_graph.sqlite",
                "PYTHONPATH": "C:\\Git\\Agentic-Workflow",
            },
        },
        "filesystem": {
            "_type": "global_node",
            "_description": "Filesystem MCP with repo-only access",
            "command": "node",
            "args": [
                "C:\\Users\\amita\\AppData\\Roaming\\fnm\\node-versions\\v24.13.0\\installation\\node_modules\\@modelcontextprotocol\\server-filesystem\\dist\\index.js",
                "C:\\Git\\Agentic-Workflow"
            ],
            "disabled": False,
            "env": {"NODE_ENV": "production"},
        },
        "sequential-thinking": {
            "_type": "global_node",
            "_description": "Sequential thinking MCP server",
            "command": "C:\\Users\\amita\\AppData\\Roaming\\fnm\\node-versions\\v24.13.0\\installation\\node.exe",
            "args": [
                "C:\\Users\\amita\\AppData\\Roaming\\fnm\\node-versions\\v24.13.0\\installation\\node_modules\\@modelcontextprotocol\\server-sequential-thinking\\dist\\index.js"
            ],
            "disabled": False,
            "env": {
                "DISABLE_THOUGHT_LOGGING": "true",
                "SEQUENTIAL_THINKING_AUTO_TRIGGER": "true",
                "SEQUENTIAL_THINKING_COMPLEXITY_THRESHOLD": "medium",
                "SEQUENTIAL_THINKING_INTEGRATION_MODE": "adg-aware",
                "SEQUENTIAL_THINKING_MAX_THOUGHTS": "15",
                "SEQUENTIAL_THINKING_PRIORITY": "high",
                "SEQUENTIAL_THINKING_SWE_MODE": "enabled",
                "SEQUENTIAL_THINKING_TOKEN_BUDGET": "30000",
            },
        },
        "brave-search": {
            "_type": "global_node",
            "_description": "Brave Search MCP",
            "command": "node",
            "args": [
                "C:\\Users\\amita\\AppData\\Roaming\\fnm\\node-versions\\v24.13.0\\installation\\node_modules\\@brave\\brave-search-mcp-server\\dist\\index.js"
            ],
            "disabled": False,
            "env": {"BRAVE_API_KEY": "BSAr2wedArAn5uzkoHBpQegHvaEfPxZ"},
        },
        "fetch": {
            "_type": "global_uvx",
            "_description": "Fetch MCP via uvx",
            "command": "uvx",
            "args": ["mcp-server-fetch"],
            "disabled": False,
        },
        "GitKraken": {
            "_type": "global_native",
            "_description": "GitKraken MCP",
            "command": "C:\\Users\\amita\\AppData\\Local\\GitKrakenCLI\\gk.exe",
            "args": ["mcp", "--host=windsurf", "--source=gitlens", "--scheme=windsurf"],
            "disabled": False,
        },
        "deepwiki": {
            "_type": "remote_url",
            "_description": "DeepWiki remote MCP",
            "command": "",
            "disabled": False,
            "url": "https://mcp.deepwiki.com/mcp",
        },
    },
}


def strip_internal_fields(config: dict) -> dict:
    """Remove internal-only fields (starting with _) from output config."""
    result = {}
    for key, value in config.items():
        if key.startswith("_"):
            continue
        if isinstance(value, dict):
            result[key] = strip_internal_fields(value)
        else:
            result[key] = value
    return result


def generate_configs() -> tuple[dict, dict]:
    """Generate workspace and user-global configs from manifest."""
    workspace_config = {"mcpServers": {}}
    user_global_config = {"mcpServers": {}}

    for name, server in CANONICAL_MANIFEST["mcpServers"].items():
        clean = strip_internal_fields(server)

        # Both get the same content
        workspace_config["mcpServers"][name] = clean
        user_global_config["mcpServers"][name] = clean

    return workspace_config, user_global_config


def check_configs() -> bool:
    """Check if current configs match the canonical manifest."""
    workspace_match = True
    user_global_match = True

    expected_workspace, expected_user_global = generate_configs()

    # Check workspace config
    if WORKSPACE_CONFIG_PATH.exists():
        with open(WORKSPACE_CONFIG_PATH, encoding="utf-8") as f:
            actual = json.load(f)
        if actual != expected_workspace:
            workspace_match = False
            print(f"[MISMATCH] Workspace config differs from manifest")
    else:
        workspace_match = False
        print(f"[MISSING] Workspace config not found: {WORKSPACE_CONFIG_PATH}")

    # Check user-global config
    if USER_GLOBAL_CONFIG_PATH.exists():
        with open(USER_GLOBAL_CONFIG_PATH, encoding="utf-8") as f:
            actual = json.load(f)
        if actual != expected_user_global:
            user_global_match = False
            print(f"[MISMATCH] User-global config differs from manifest")
    else:
        user_global_match = False
        print(f"[MISSING] User-global config not found: {USER_GLOBAL_CONFIG_PATH}")

    if workspace_match and user_global_match:
        print("[OK] Both configs match canonical manifest")
        return True
    return False


def write_configs() -> None:
    """Write generated configs to disk."""
    workspace, user_global = generate_configs()

    # Ensure directories exist
    WORKSPACE_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    USER_GLOBAL_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Write workspace config
    with open(WORKSPACE_CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(workspace, f, indent=2)
    print(f"[WRITE] {WORKSPACE_CONFIG_PATH}")

    # Write user-global config
    with open(USER_GLOBAL_CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(user_global, f, indent=2)
    print(f"[WRITE] {USER_GLOBAL_CONFIG_PATH}")

    # Also write the manifest for reference
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(CANONICAL_MANIFEST, f, indent=2)
    print(f"[WRITE] {MANIFEST_PATH}")


def main() -> int:
    parser = argparse.ArgumentParser(description="MCP Config Generator")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check if configs match manifest (exit 1 if drift detected)",
    )
    parser.add_argument(
        "--generate",
        action="store_true",
        help="Generate and write configs from canonical manifest",
    )
    args = parser.parse_args()

    print("=" * 70)
    print("UNIFIED MCP CONFIG GENERATOR")
    print("=" * 70)
    print(f"Manifest: {MANIFEST_PATH}")
    print(f"Workspace: {WORKSPACE_CONFIG_PATH}")
    print(f"User-global: {USER_GLOBAL_CONFIG_PATH}")
    print()

    if args.check:
        if check_configs():
            return 0
        return 1

    if args.generate:
        write_configs()
        print("\n[OK] Configs generated successfully")
        return 0

    # Default: show status
    print("Use --check to validate or --generate to regenerate")
    check_configs()
    return 0


if __name__ == "__main__":
    sys.exit(main())
