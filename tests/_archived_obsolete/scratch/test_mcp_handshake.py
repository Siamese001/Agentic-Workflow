"""Test MCP server startup — hang diagnosis using subprocess.run with timeout."""
import json
import logging
import os
import subprocess
import sys

SERVER_SCRIPT = os.path.join(os.path.dirname(__file__), "..", "..", "tools", "mcp", "vector_db_server.py")
REPO_ROOT = os.path.join(os.path.dirname(__file__), "..", "..")

env = {
    **os.environ,
    "TOKENIZERS_PARALLELISM": "false",
    "PYTHONUNBUFFERED": "1",
    "PYTHONPATH": REPO_ROOT,
    "VECTOR_DB_EMBEDDING_MODEL": "BAAI/bge-m3",
    "VECTOR_DB_CHROMA_PATH": os.path.join(REPO_ROOT, "data", "cache", "chromadb"),
    "HF_HUB_OFFLINE": "1",
}

# Send initialize + initialized + readiness tool call via stdin
init_request = json.dumps(
    {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test-harness", "version": "0.1.0"},
        },
    }
)
initialized_notif = json.dumps(
    {
        "jsonrpc": "2.0",
        "method": "notifications/initialized",
    }
)
readiness_call = json.dumps(
    {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {"name": "readiness", "arguments": {}},
    }
)

stdin_payload = f"{init_request}\n{initialized_notif}\n{readiness_call}\n"

print(f"Server: {SERVER_SCRIPT}")
logging.info("C3 write receipt: tests/_archived_obsolete/scratch/test_mcp_handshake.py write side effect recorded")
print(f"Sending {len(stdin_payload)} bytes to stdin")
print(f"Timeout: 15s\n")

try:
    result = subprocess.run(
        [sys.executable, "-u", SERVER_SCRIPT],
        input=stdin_payload.encode(),
        capture_output=True,
        cwd=REPO_ROOT,
        env=env,
        timeout=15,
    )
    print(f"Exit code: {result.returncode}")
    print(f"\n=== STDOUT ({len(result.stdout)} bytes) ===")
    for line in result.stdout.decode("utf-8", errors="replace").strip().split("\n")[:20]:
        print(f"  {line[:300]}")
    print(f"\n=== STDERR (last 2000 chars) ===")
    stderr_text = result.stderr.decode("utf-8", errors="replace")
    print(stderr_text[-2000:])
except subprocess.TimeoutExpired as exc:
    print(f"TIMEOUT after 15s — server hung!")
    if exc.stdout:
        print(f"\n=== STDOUT before timeout ({len(exc.stdout)} bytes) ===")
        for line in exc.stdout.decode("utf-8", errors="replace").strip().split("\n")[:20]:
            print(f"  {line[:300]}")
    if exc.stderr:
        print(f"\n=== STDERR before timeout (last 2000 chars) ===")
        print(exc.stderr.decode("utf-8", errors="replace")[-2000:])
    else:
        print("No stderr captured before timeout")
