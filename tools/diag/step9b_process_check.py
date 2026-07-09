"""Step 9B: Find running vector_db MCP subprocess."""
import logging
import subprocess
import sys

r = subprocess.run(
    [
        "wmic",
        "process",
        "where",
        "CommandLine like '%vector_db_server%'",
        "get",
        "ProcessId,CommandLine",
        "/format:list",
    ],
    capture_output=True,
    text=True,
    timeout=10,
)
logging.info("C3 write receipt: tools/diag/step9b_process_check.py write side effect recorded")
lines = [ln.strip() for ln in r.stdout.splitlines() if ln.strip()]
if not lines:
    print("No vector_db_server process found")
    print("FAIL — MCP subprocess not running")
    sys.exit(1)

print("Found vector_db_server process(es):")
for ln in lines:
    print(f"  {ln}")

# Count distinct PIDs
pids = [ln.split("=")[1] for ln in lines if ln.startswith("ProcessId=")]
cmds = [ln.split("=", 1)[1] for ln in lines if ln.startswith("CommandLine=")]

print(f"\nPID count: {len(pids)}")
for i, (pid, cmd) in enumerate(zip(pids, cmds)):
    print(f"  [{i + 1}] PID={pid}")
    print(f"      CMD={cmd}")

if len(pids) == 1:
    print("\nPASS — exactly 1 vector_db_server process running")
elif len(pids) > 1:
    print(f"\nWARN — {len(pids)} vector_db_server processes running")
else:
    print("\nFAIL — no PID extracted")
