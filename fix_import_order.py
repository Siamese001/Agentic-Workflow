#!/usr/bin/env python3
"""
Fix import order violations using isort
"""
import subprocess
import sys
from pathlib import Path

project_root = Path(__file__).parent
agentic_core = project_root / "agentic_core"

print("="*70)
print("FIXING IMPORT ORDER VIOLATIONS")
print("="*70)

# Check if isort is installed
try:
    result = subprocess.run(["isort", "--version"], capture_output=True, text=True)
    print(f"\n[OK] isort version: {result.stdout.strip()}")
except FileNotFoundError:
    print("\n[!] isort not found. Installing...")
    subprocess.run([sys.executable, "-m", "pip", "install", "isort"], check=True)

# Run isort on agentic_core
print(f"\n[*] Running isort on agentic_core/...")
print("    This will reorder imports to: stdlib → third-party → local")

result = subprocess.run(
    ["isort", str(agentic_core), "--profile", "black", "--line-length", "100"],
    capture_output=True,
    text=True
)

if result.returncode == 0:
    print(f"\n[✓] Import order fixed successfully")
    if result.stdout:
        print(result.stdout)
else:
    print(f"\n[!] isort failed:")
    print(result.stderr)

print(f"\n{'='*70}")
print("Re-run validation to verify:")
print("  python run_agentic_core_validation.py")
print(f"{'='*70}")
