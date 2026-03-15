"""Regenerate ADG and run P0/L6 trace completeness gate."""

import os
import subprocess
import sys

os.chdir(r"C:\Git\Agentic-Workflow")

print("=== Step 1: Regenerate ADG ===")
r1 = subprocess.run([sys.executable, "tools/generate_full_adg.py"], capture_output=True, text=True)
print(r1.stdout[-3000:] if len(r1.stdout) > 3000 else r1.stdout)
if r1.stderr:
    print("STDERR:", r1.stderr[-1000:])
print(f"Exit: {r1.returncode}")

print("\n=== Step 2: Run P0/L6 gate ===")
r2 = subprocess.run(
    [sys.executable, "ops_scripts/ci/_trace_completeness_gate.py"], capture_output=True, text=True
)
print(r2.stdout)
if r2.stderr:
    print("STDERR:", r2.stderr[-500:])
print(f"Exit: {r2.returncode}")

print("\n=== Step 3: Verify P0/L5 gate still passes ===")
r3 = subprocess.run(
    [sys.executable, "ops_scripts/ci/_policy_enforcement_gate.py"], capture_output=True, text=True
)
print(r3.stdout)
if r3.stderr:
    print("STDERR:", r3.stderr[-300:])
print(f"Exit: {r3.returncode}")
