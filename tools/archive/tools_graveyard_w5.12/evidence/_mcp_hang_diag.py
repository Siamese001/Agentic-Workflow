"""
Diagnose MCP server hang issues.
Tests:
1. Is sequential-thinking node process running?
2. Can it respond to a basic JSON-RPC initialize in <3s?
3. Is mcp10 postgres server responding?
4. Check all npx MCP server startup times
"""

import json
import os
import subprocess
import threading
import time


# guardian: allow-magic-config
def test_mcp_server(name, cmd, timeout=8):
    """Start MCP server, send initialize, measure response time."""
    env = {**os.environ}
    if "postgres" in name:
        env["PGPASSWORD"] = "postgres"

    try:
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            env=env,
            text=True,
            bufsize=1,
        )

        init_req = (
            json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "clientInfo": {"name": "diag", "version": "1"},
                    },
                },
            )
            + "\n"
        )

        result = {"response": None, "elapsed": None, "error": None}

        def send_and_recv():
            try:
                t0 = time.time()
                proc.stdin.write(init_req)
                proc.stdin.flush()
                line = proc.stdout.readline()
                result["elapsed"] = round(time.time() - t0, 2)
                result["response"] = line.strip()[:200]
            # guardian: allow-silent-swallow
            except Exception as e:
                result["error"] = str(e)

        t = threading.Thread(target=send_and_recv, daemon=True)
        t.start()
        t.join(timeout=timeout)

        proc.terminate()
        try:
            # guardian: allow-magic-config
            proc.wait(timeout=2)
        # guardian: allow-silent-swallow
        except Exception:
            proc.kill()

        stderr = proc.stderr.read()[:300]

        if result["response"]:
            return f"OK  ({result['elapsed']}s) | {result['response'][:80]}"
        elif result["error"]:
            return f"ERR ({result['error'][:80]})"
        elif stderr:
            return f"HANG/ERR | stderr: {stderr[:120]}"
        else:
            return f"HANG (no response in {timeout}s)"

    # guardian: allow-silent-swallow
    except Exception as e:
        return f"FAIL: {e}"


tests = [
    ("sequential-thinking", "npx -y @modelcontextprotocol/server-sequential-thinking"),
    (
        "postgres-mcp",
        # guardian: allow-magic-config
        "npx -y @modelcontextprotocol/server-postgres postgresql://postgres:postgres@localhost:5432/mcp_db",
    ),
    ("redis-mcp", "npx -y @modelcontextprotocol/server-redis"),
    ("brave-search", "npx -y @modelcontextprotocol/server-brave-search"),
    ("filesystem", r'npx -y @modelcontextprotocol/server-filesystem "c:\Git\Agentic-Workflow"'),
    ("memory", "npx -y @modelcontextprotocol/server-memory"),
]

print("=" * 65)
print("MCP SERVER HANG DIAGNOSTICS")
print("=" * 65)
for name, cmd in tests:
    print(f"\nTesting: {name}")
    print(f"  cmd: {cmd[:70]}")
    # guardian: allow-magic-config
    result = test_mcp_server(name, cmd, timeout=15)
    status = "✅" if result.startswith("OK") else "❌" if result.startswith("ERR") else "⏱️"
    print(f"  {status} {result}")

print("\n" + "=" * 65)
print("Done.")
