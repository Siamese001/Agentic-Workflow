#!/usr/bin/env python3
"""Audit all MCPs in user-global config for missing cwd parameter"""
import json

with open(r'C:\Users\amita\.codeium\windsurf\mcp_config.json') as f:
    config = json.load(f)

print("=" * 70)
print("MCP CONFIG AUDIT - Checking for 'cwd' parameter")
print("=" * 70)

mcp_servers = config.get('mcpServers', {})

# Categorize MCPs
local_python_mcps = []  # Python-based, local files
node_mcps = []  # Node.js-based
remote_mcps = []  # URL-based
other_mcps = []

for name, mcp in mcp_servers.items():
    if mcp.get('disabled', False):
        continue

    cmd = mcp.get('command', '')
    args = mcp.get('args', [])
    has_cwd = 'cwd' in mcp

    # Check if it's a local Python file
    is_local_python = (
        cmd == 'python' and
        args and
        args[0].endswith('.py') and
        not args[0].startswith('http')
    )

    # Check if it's a Node.js MCP with local file
    is_local_node = (
        cmd in ['node', 'npx', 'uvx'] and
        args and
        any('.js' in str(a) or 'node_modules' in str(a) for a in args)
    )

    info = {
        'name': name,
        'command': cmd,
        'args': args[:2] if args else [],
        'has_cwd': has_cwd,
        'cwd': mcp.get('cwd', 'MISSING')
    }

    if is_local_python:
        local_python_mcps.append(info)
    elif is_local_node:
        node_mcps.append(info)
    elif 'url' in mcp:
        remote_mcps.append(info)
    else:
        other_mcps.append(info)

print("\n--- LOCAL PYTHON MCPS (cwd recommended) ---")
needs_cwd = []
for mcp in local_python_mcps:
    status = "✅" if mcp['has_cwd'] else "❌ MISSING"
    print(f"  {status} {mcp['name']}")
    print(f"      Command: {mcp['command']} {mcp['args'][0] if mcp['args'] else 'N/A'}")
    print(f"      CWD: {mcp['cwd']}")
    if not mcp['has_cwd']:
        needs_cwd.append(mcp['name'])

print("\n--- NODE.JS MCPS (cwd may be needed) ---")
for mcp in node_mcps:
    status = "✅" if mcp['has_cwd'] else "⚠️  NO CWD"
    print(f"  {status} {mcp['name']}")
    if not mcp['has_cwd']:
        print(f"      Command: {mcp['command']}")
        print(f"      Args: {mcp['args']}")

print("\n--- REMOTE MCPS (cwd not applicable) ---")
for mcp in remote_mcps:
    print(f"  ℹ️  {mcp['name']} (URL-based)")

print("\n--- OTHER MCPS ---")
for mcp in other_mcps:
    status = "✅" if mcp['has_cwd'] else "ℹ️  NO CWD"
    print(f"  {status} {mcp['name']}")
    print(f"      Command: {mcp['command']}")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
if needs_cwd:
    print(f"❌ MCPs MISSING 'cwd' parameter: {', '.join(needs_cwd)}")
    print("\nThese may fail to resolve imports when run from default directory.")
else:
    print("✅ All local Python MCPs have 'cwd' parameter set.")
