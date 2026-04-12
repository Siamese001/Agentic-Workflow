#!/usr/bin/env python3
"""Configure ADG SQLite MCP server in Windsurf."""

import json
import sys

MCP_CONFIG_PATH = r"C:\Users\amita\.codeium\windsurf\mcp_config.json"


def main():
    print(f"Reading MCP config from: {MCP_CONFIG_PATH}")

    # Read existing config
    try:
        with open(MCP_CONFIG_PATH) as f:
            config = json.load(f)
    except FileNotFoundError:
        print("Config file not found. Creating new one.")
        config = {"mcpServers": {}}
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        sys.exit(1)

    # Ensure mcpServers exists
    if "mcpServers" not in config:
        config["mcpServers"] = {}

    # Add adg_sqlite server
    config["mcpServers"]["adg_sqlite"] = {
        "command": "python",
        "args": ["-m", "tools.adg.mcp.server"],
        "cwd": r"C:\Git\Agentic-Workflow",
        "disabled": False,
    }

    # Disable old adg_redis if present
    if "adg_redis" in config["mcpServers"]:
        config["mcpServers"]["adg_redis"]["disabled"] = True
        print("Disabled old adg_redis server")

    # Write config back
    with open(MCP_CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)

    print("✅ MCP config updated successfully!")
    print("\nConfigured servers:")
    for name, server in config["mcpServers"].items():
        status = "enabled" if not server.get("disabled", False) else "disabled"
        print(f"  - {name}: {status}")

    print("\n⚠️  IMPORTANT: Restart Windsurf completely for changes to take effect!")


if __name__ == "__main__":
    main()
