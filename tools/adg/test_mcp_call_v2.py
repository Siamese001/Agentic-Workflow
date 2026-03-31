"""Simulate a full MCP tool call and capture stderr logging to diagnose hangs."""
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

def drain_stderr():
    """Read all available stderr."""
    lines = []
    def read_all():
        while True:
            line = server.stderr.readline()
            if not line:
                break
            lines.append(line.rstrip())
    t = threading.Thread(target=read_all)
    t.daemon = True
    t.start()
    t.join(timeout=2)
    return lines

# Step 1: wait a moment for server startup logging
time.sleep(1)
startup_logs = drain_stderr()
print("=== STARTUP STDERR ===", flush=True)
for line in startup_logs:
    print(f"  {line}", flush=True)

# Step 2: initialize
print(f"\n[{time.time():.1f}] Sending initialize...", flush=True)
send({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": {"name": "test", "version": "1.0"}
}})
resp = recv(10)
if resp is None:
    print(f"[{time.time():.1f}] TIMEOUT on initialize", flush=True)
    server.kill()
    for line in drain_stderr():
        print(f"  STDERR: {line}", flush=True)
    sys.exit(1)
print(f"[{time.time():.1f}] initialize OK", flush=True)

# Step 3: initialized notification
send({"jsonrpc": "2.0", "method": "notifications/initialized"})
time.sleep(0.3)

# Step 4: call adg_status
print(f"[{time.time():.1f}] Calling adg_status...", flush=True)
send({"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {
    "name": "adg_status", "arguments": {}
}})
resp = recv(10)

# Drain stderr after the call
time.sleep(0.5)
call_logs = drain_stderr()
print("\n=== TOOL CALL STDERR ===", flush=True)
for line in call_logs:
    print(f"  {line}", flush=True)

if resp is None:
    print(f"\n[{time.time():.1f}] TIMEOUT on adg_status - HUNG!", flush=True)
    server.kill()
    sys.exit(1)

print(f"\n[{time.time():.1f}] adg_status OK", flush=True)
parsed = json.loads(resp)
content = parsed.get("result", {}).get("content", [])
if content:
    text = content[0].get("text", "{}")
    data = json.loads(text)
    print(f"  is_fresh: {data.get('data', {}).get('is_fresh')}", flush=True)
    print(f"  verdict: {data.get('data', {}).get('verdict')}", flush=True)

# Step 5: call adg_meta
print(f"\n[{time.time():.1f}] Calling adg_meta...", flush=True)
send({"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {
    "name": "adg_meta", "arguments": {}
}})
resp = recv(10)
if resp is None:
    print(f"[{time.time():.1f}] TIMEOUT on adg_meta - HUNG!", flush=True)
    server.kill()
    sys.exit(1)
print(f"[{time.time():.1f}] adg_meta OK", flush=True)

server.terminate()
print(f"\n[{time.time():.1f}] ALL TESTS PASSED - server responds correctly", flush=True)
