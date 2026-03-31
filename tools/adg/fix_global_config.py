"""Fix global mcp_config.json: add missing cwd to adg_redis, remove stale minimal-test."""
import json

gl_path = r"C:\Users\amita\.codeium\windsurf\mcp_config.json"

with open(gl_path, "r", encoding="utf-8") as f:
    config = json.load(f)

servers = config.get("mcpServers", {})

# Fix 1: Add cwd to adg_redis
if "adg_redis" in servers:
    servers["adg_redis"]["cwd"] = r"C:\Git\Agentic-Workflow"
    print("[fix] Added cwd to adg_redis")

# Fix 2: Remove stale minimal-test server
if "minimal-test" in servers:
    del servers["minimal-test"]
    print("[fix] Removed stale minimal-test server")

# Fix 3: Ensure memory server has cwd too (for consistency)
if "memory" in servers and "cwd" not in servers["memory"]:
    servers["memory"]["cwd"] = r"C:\Git\Agentic-Workflow"
    print("[fix] Added cwd to memory")

with open(gl_path, "w", encoding="utf-8") as f:
    json.dump(config, f, indent=2)
    f.write("\n")

print("[done] Global config updated. Restart Windsurf to pick up changes.")

# Verify
with open(gl_path, "r", encoding="utf-8") as f:
    verify = json.load(f)
adg = verify["mcpServers"]["adg_redis"]
print(f"\nVerification:")
print(f"  adg_redis.cwd = {adg.get('cwd')}")
print(f"  adg_redis.disabled = {adg.get('disabled')}")
print(f"  minimal-test present = {'minimal-test' in verify['mcpServers']}")
