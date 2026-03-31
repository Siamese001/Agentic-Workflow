"""Compare workspace and global MCP configs for adg_redis."""
import json

ws_path = r"C:\Git\Agentic-Workflow\.windsurf\mcp_config.json"
gl_path = r"C:\Users\amita\.codeium\windsurf\mcp_config.json"

ws = json.load(open(ws_path))
gl = json.load(open(gl_path))

ws_adg = ws.get("mcpServers", {}).get("adg_redis", {})
gl_adg = gl.get("mcpServers", {}).get("adg_redis", {})

print("=== Workspace adg_redis ===")
print(f"  disabled: {ws_adg.get('disabled')}")
print(f"  command: {ws_adg.get('command')}")
print(f"  args: {ws_adg.get('args')}")

print()
print("=== Global adg_redis ===")
print(f"  disabled: {gl_adg.get('disabled')}")
print(f"  command: {gl_adg.get('command')}")
print(f"  args: {gl_adg.get('args')}")

if ws_adg == gl_adg:
    print("\nCONFIGS MATCH")
else:
    print("\nCONFIGS DIFFER!")
    for k in set(list(ws_adg.keys()) + list(gl_adg.keys())):
        if ws_adg.get(k) != gl_adg.get(k):
            print(f"  {k}: WS={ws_adg.get(k)} vs GL={gl_adg.get(k)}")

# Also check server ordering — IDE assigns prefixes by order
print("\n=== Server order in global config ===")
for i, name in enumerate(gl.get("mcpServers", {}).keys()):
    disabled = gl["mcpServers"][name].get("disabled", False)
    status = "DISABLED" if disabled else "active"
    print(f"  mcp{i}_ = {name} ({status})")
