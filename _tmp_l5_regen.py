"""Regenerate ADG and run P0/L5 policy enforcement gate."""

import os
import subprocess
import sys

os.chdir(r"C:\Git\Agentic-Workflow")

print("=== Regenerating ADG ===")
r = subprocess.run([sys.executable, "tools/generate_full_adg.py"], capture_output=False)
print(f"ADG regen done (exit {r.returncode})")

print("\n=== Running P0/L5 CI Gate ===")
r2 = subprocess.run([sys.executable, "ops_scripts/ci/_policy_enforcement_gate.py"], capture_output=False)

print("\n=== Also verifying P0/L4 gate still passes ===")
r3 = subprocess.run([sys.executable, "ops_scripts/ci/_state_authority_gate.py"], capture_output=False)

print("\n=== Also verifying P0/L3 gate still passes ===")
r4 = subprocess.run([sys.executable, "ops_scripts/ci/_orchestration_topology_gate.py"], capture_output=False)

sys.exit(0 if r2.returncode == 0 and r3.returncode == 0 and r4.returncode == 0 else 1)
