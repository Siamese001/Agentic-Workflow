#!/usr/bin/env python3
"""Fix memory MCP and check sequential-thinking"""

import json

with open(r"C:\Users\amita\.codeium\windsurf\mcp_config.json", "r") as f:
    config = json.load(f)

# Fix memory MCP
if "memory" in config.get("mcpServers", {}):
    memory = config["mcpServers"]["memory"]
    if "cwd" not in memory:
        memory["cwd"] = r"C:\Git\Agentic-Workflow"
        print("Added cwd to memory MCP")
    else:
        print("memory already has cwd:", memory["cwd"])
else:
    print("memory MCP not found")

# Check sequential-thinking
if "sequential-thinking" in config.get("mcpServers", {}):
    st = config["mcpServers"]["sequential-thinking"]
    print("sequential-thinking: cwd=" + st.get("cwd", "MISSING"))

# Write back
with open(r"C:\Users\amita\.codeium\windsurf\mcp_config.json", "w") as f:
    json.dump(config, f, indent=2)

print("Config updated")
