"""Quick subprocess probe: spawn each MCP server, wait 3s, check if still alive."""
import subprocess
import sys
import time
from pathlib import Path

PYTHON = sys.executable
REPO = str(Path(__file__).resolve().parents[2])

SERVERS = [
    ("adg_sqlite",    Path(REPO) / "tools" / "adg" / "mcp" / "server.py"),
    ("redis_mcp",     Path(REPO) / "tools" / "mcp" / "redis_mcp_server.py"),
    ("enhanced_http", Path(REPO) / "tools" / "mcp" / "enhanced_http_server.py"),
    ("pytest_mcp",    Path(REPO) / "tools" / "mcp" / "pytest_server.py"),
    ("vector_db",     Path(REPO) / "tools" / "mcp" / "vector_db_server.py"),
    ("otel_mcp",      Path(REPO) / "tools" / "otel" / "otel_mcp_server.py"),
    ("memory_mcp",    Path(REPO) / "tools" / "memory" / "adg_memory_server.py"),
]

WAIT = 3  # seconds to wait before checking

results = []
procs = []

for name, script in SERVERS:
    cmd = [PYTHON, str(script)]
    try:
        p = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=REPO,
            stdin=subprocess.PIPE,  # MCP reads from stdin — provide pipe so it doesn't inherit terminal
        )
        procs.append((name, p))
    except Exception as e:
        results.append((name, "LAUNCH_ERROR", str(e), ""))

time.sleep(WAIT)

for name, p in procs:
    rc = p.poll()
    p.kill()
    stdout, stderr = p.communicate()
    err = stderr.decode("utf-8", errors="replace").strip()
    out = stdout.decode("utf-8", errors="replace").strip()

    if rc is None:
        # Still running after WAIT seconds = good, server is up waiting for MCP handshake
        # Show first meaningful stderr line (log output)
        first_err = err.splitlines()[0] if err else "(no stderr)"
        results.append((name, "OK - running", "", first_err))
    else:
        # Crashed immediately
        last_err = "\n".join((err or out).splitlines()[-5:])
        results.append((name, f"CRASHED rc={rc}", last_err, ""))

print(f"\n{'SERVER':<16} {'STATUS':<20} DETAIL")
print("-" * 80)
for name, status, err, log in results:
    detail = err or log or ""
    detail = detail.replace("\n", " | ")[:100]
    print(f"{name:<16} {status:<20} {detail}")
