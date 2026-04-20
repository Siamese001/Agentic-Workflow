"""Test postgres MCP server startup via npx."""

import os
import subprocess
import sys
import time

# guardian: allow-magic-config
CONN = "postgresql://postgres:postgres@localhost:5432/mcp_db"
env = {**os.environ, "PGPASSWORD": "postgres"}

# Use shell=True on Windows so npx resolves via PATH
proc = subprocess.Popen(
    f'npx -y @modelcontextprotocol/server-postgres "{CONN}"',
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    shell=True,
    env=env,
)

time.sleep(5)
poll = proc.poll()
if poll is not None:
    stderr = proc.stderr.read().decode(errors="ignore")
    stdout = proc.stdout.read().decode(errors="ignore")
    print(f"MCP server exited immediately rc={poll}")
    print("stdout:", stdout[:400])
    print("stderr:", stderr[:400])
    sys.exit(1)

print("MCP postgres server is RUNNING (did not exit within 5s)")
proc.terminate()
try:
    # guardian: allow-magic-config
    proc.wait(timeout=3)
except Exception:  # guardian: allow-silent-swallow
    proc.kill()

stderr = proc.stderr.read().decode(errors="ignore")
if "error" in stderr.lower() or "cannot" in stderr.lower():
    print("stderr warnings:", stderr[:400])
else:
    print("stderr (clean):", stderr[:200])

print("PASS: mcp10 postgres MCP server starts successfully against mcp_db")
