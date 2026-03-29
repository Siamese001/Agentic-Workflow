#!/usr/bin/env python3
"""Verify MCP config fix"""
import json

with open(r'C:\Users\amita\.codeium\windsurf\mcp_config.json', 'r') as f:
    config = json.load(f)

adg = config.get('mcpServers', {}).get('adg_redis', {})
print('=== adg_redis config (user-global) ===')
print(f"command: {adg.get('command')}")
print(f"cwd: {adg.get('cwd')}")
print(f"disabled: {adg.get('disabled')}")
print(f"env ADG_REDIS_URL: {adg.get('env', {}).get('ADG_REDIS_URL')}")

if adg.get('cwd') == r'C:\Git\Agentic-Workflow':
    print("\n✅ FIX VERIFIED: cwd parameter correctly set!")
else:
    print("\n❌ FIX FAILED: cwd parameter missing or incorrect")
