"""Diagnose test collection errors — captures both stdout and stderr."""

import re
import subprocess

ROOT = r"C:\Git\Agentic-Workflow"

r = subprocess.run(
    ["python", "-m", "pytest", "tests/", "--co", "-q", "-p", "no:logging", "--tb=short"],
    capture_output=True,
    text=True,
    cwd=ROOT,
    timeout=120,
)

# Combine stdout + stderr and strip ANSI
output = r.stdout + "\n" + r.stderr
clean = re.sub(r"\x1b\[[0-9;]*m", "", output)

# Find ERROR collecting lines
error_collecting = []
error_messages = []
lines = clean.split("\n")
for i, line in enumerate(lines):
    if "ERROR collecting" in line or "ERROR tests/" in line:
        error_collecting.append(line.strip())
    if line.strip().startswith("E   ") and (
        "Error" in line or "cannot import" in line or "No module" in line
    ):
        error_messages.append(line.strip()[:200])

# Deduplicate error messages
seen = set()
unique_errors = []
for msg in error_messages:
    if msg not in seen:
        seen.add(msg)
        unique_errors.append(msg)

print(f"=== {len(error_collecting)} ERROR collecting lines ===")
for e in error_collecting[:20]:
    print(f"  {e[:200]}")

print(f"\n=== {len(unique_errors)} unique error messages ===")
for e in unique_errors[:40]:
    print(f"  {e}")

# Last 5 lines
print("\n=== Last 5 lines ===")
for line in lines[-5:]:
    print(f"  {line.strip()}")
