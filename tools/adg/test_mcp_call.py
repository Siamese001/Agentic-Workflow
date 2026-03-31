"""Simulate a full MCP tool call against adg_mcp_server.py to diagnose hangs."""
import subprocess
import json
import sys
import time
import threading

server = subprocess.Popen(
    [sys.executable, "tools/adg/adg_mcp_server.py"],
    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    text=True, cwd=r"C:\Git\Agentic-Workflow"
)

def send(msg):
    server.stdin.write(json.dumps(msg) + "\n")
    server.stdin.flush()

def recv(timeout=10):
    result = [None]
    def read():
        result[0] = server.stdout.readline()
    t = threading.Thread(target=read)
    t.start()
    t.join(timeout=timeout)
    if t.is_alive():
        return None  # timeout
    return result[0]

# Step 1: initialize
print(f"[{time.time():.1f}] Sending initialize...", flush=True)
send({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": {"name": "test", "version": "1.0"}
}})
resp = recv(10)
if resp is None:
    print(f"[{time.time():.1f}] TIMEOUT on initialize", flush=True)
    server.kill()
    sys.exit(1)
print(f"[{time.time():.1f}] initialize OK ({len(resp)} bytes)", flush=True)

# Step 2: initialized notification
print(f"[{time.time():.1f}] Sending initialized notification...", flush=True)
send({"jsonrpc": "2.0", "method": "notifications/initialized"})
time.sleep(0.5)
print(f"[{time.time():.1f}] Notification sent", flush=True)

# Step 3: call adg_status
print(f"[{time.time():.1f}] Calling adg_status...", flush=True)
send({"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {
    "name": "adg_status", "arguments": {}
}})
resp = recv(10)
if resp is None:
    print(f"[{time.time():.1f}] TIMEOUT on adg_status - HUNG!", flush=True)
    # Capture stderr
    server.kill()
    stderr = server.stderr.read()
    if stderr:
        print(f"STDERR:\n{stderr[:500]}", flush=True)
    sys.exit(1)

print(f"[{time.time():.1f}] adg_status OK", flush=True)
parsed = json.loads(resp)
content = parsed.get("result", {}).get("content", [])
if content:
    print(json.dumps(json.loads(content[0].get("text", "{}")), indent=2)[:500], flush=True)

server.terminate()
print(f"[{time.time():.1f}] Done - server responded correctly", flush=True)
