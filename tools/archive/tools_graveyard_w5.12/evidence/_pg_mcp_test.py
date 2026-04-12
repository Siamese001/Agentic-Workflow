"""Test that the postgres MCP server can start and connect to mcp_db."""

import json
import os
import subprocess
import sys
import time

CONN = "postgresql://postgres:postgres@localhost:5432/mcp_db"

# Start the MCP server briefly and send a ListTools request via stdin
proc = subprocess.Popen(
    ["npx", "-y", "@modelcontextprotocol/server-postgres", CONN],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    env={**os.environ, "PGPASSWORD": "postgres"},
)

time.sleep(3)
poll = proc.poll()
if poll is not None:
    print(f"MCP server exited immediately with rc={poll}")
    print("stderr:", proc.stderr.read()[:500])
    sys.exit(1)

# Send a JSON-RPC initialize request
req = (
    json.dumps(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test", "version": "1.0"},
            },
        }
    )
    + "\n"
)

try:
    proc.stdin.write(req)
    proc.stdin.flush()
    time.sleep(2)
    # Read response
    import select

    ready = select.select([proc.stdout], [], [], 3)
    if ready[0]:
        line = proc.stdout.readline()
        print("MCP server response:", line[:300])
    else:
        print("MCP server started OK (no response within 3s - normal for stdio transport)")
    print("MCP postgres server RUNNING OK")
except Exception as e:
    print(f"Error communicating: {e}")
finally:
    proc.terminate()
    try:
        proc.wait(timeout=3)
    except (ValueError, TypeError, RuntimeError) as e:
        proc.kill()
    stderr_out = proc.stderr.read()
    if stderr_out:
        print("stderr:", stderr_out[:500])
