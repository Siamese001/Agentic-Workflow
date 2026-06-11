"""Step 9A: Compare global vs repo MCP vector_db entries."""

import json
import re
import sys


def load_json_lenient(path: str) -> dict:
    """Load JSON with trailing commas removed."""
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    # Remove trailing commas before } or ]
    text = re.sub(r",\s*([}\]])", r"\1", text)
    return json.loads(text)


global_path = r"C:\Users\amita\.codeium\windsurf\mcp_config.json"
repo_path = r".mcp.json"

g = load_json_lenient(global_path)
r = load_json_lenient(repo_path)

gv = g.get("mcpServers", {}).get("vector_db", {})
rv = r.get("mcpServers", {}).get("vector_db", {})

g_norm = json.dumps(gv, sort_keys=True)
r_norm = json.dumps(rv, sort_keys=True)

if g_norm == r_norm:
    print("RESULT: EXACT MATCH")
    print("PASS — global and repo vector_db configs are identical")
else:
    print("RESULT: MISMATCH")
    # Show diffs
    all_keys = sorted(set(list(gv.keys()) + list(rv.keys())))
    for k in all_keys:
        gval = json.dumps(gv.get(k), sort_keys=True)
        rval = json.dumps(rv.get(k), sort_keys=True)
        if gval != rval:
            print(f"  DIFF key={k}:")
            print(f"    global: {gval}")
            print(f"    repo:   {rval}")
    # Also check env keys
    g_env = gv.get("env", {})
    r_env = rv.get("env", {})
    env_keys = sorted(set(list(g_env.keys()) + list(r_env.keys())))
    for ek in env_keys:
        if g_env.get(ek) != r_env.get(ek):
            print(f"  ENV DIFF {ek}:")
            print(f"    global: {g_env.get(ek)}")
            print(f"    repo:   {r_env.get(ek)}")
    print("FAIL — configs differ")
