"""Regenerate ADG and run P0/L4 state authority gate."""

import os
import subprocess
import sys

os.chdir(r"C:\Git\Agentic-Workflow")

print("=== Regenerating ADG ===")
r = subprocess.run(
    [sys.executable, "tools/generate_full_adg.py"], capture_output=True, text=True, timeout=300
)
lines = r.stdout.strip().splitlines()
for l in lines[-15:]:
    print(" ", l)
if r.returncode != 0 and "UnicodeEncodeError" not in r.stderr:
    print("STDERR:", r.stderr[-1000:])
    print(f"ADG regen exit code: {r.returncode} (may be unicode-only error, continuing)")
else:
    print(f"ADG regen done (exit {r.returncode})")

print("\n=== Running P0/L4 CI Gate ===")
r2 = subprocess.run(
    [sys.executable, "ops_scripts/ci/_state_authority_gate.py"], capture_output=True, text=True, timeout=60
)
print(r2.stdout)
if r2.returncode != 0 and r2.stderr:
    print("STDERR:", r2.stderr[-500:])
print(f"Gate exit code: {r2.returncode}")

print("\n=== Also verifying P0/L3 gate still passes ===")
r3 = subprocess.run(
    [sys.executable, "ops_scripts/ci/_orchestration_topology_gate.py"],
    capture_output=True,
    text=True,
    timeout=60,
)
print(r3.stdout)
print(f"L3 Gate exit code: {r3.returncode}")
