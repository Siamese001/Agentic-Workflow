#!/usr/bin/env python3
"""Verify config subfolder compliance with SSOT"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from agentic_core.config.blueprint_sovereign.structure_blueprint import CORE_SUBFOLDER_MAP

config_dir = Path(__file__).parent / "agentic_core" / "config"

print("="*70)
print("CONFIG SUBFOLDER COMPLIANCE CHECK")
print("="*70)

# Get allowed subfolders from SSOT
allowed = set(CORE_SUBFOLDER_MAP['config'])
print(f"\nAllowed subfolders (from SSOT):")
for folder in sorted(allowed):
    print(f"  ✓ {folder}")

# Get actual subfolders
actual = {d.name for d in config_dir.iterdir() if d.is_dir() and not d.name.startswith('.')}
print(f"\nActual subfolders (on disk):")
for folder in sorted(actual):
    status = "✓" if folder in allowed else "✗"
    print(f"  {status} {folder}")

# Check for violations
violations = actual - allowed
missing = allowed - actual

print("\n" + "="*70)
print("COMPLIANCE SUMMARY")
print("="*70)

if violations:
    print(f"\n❌ VIOLATIONS: {len(violations)} unauthorized subfolder(s)")
    for v in sorted(violations):
        print(f"  • {v}")
else:
    print(f"\n✅ No violations - all subfolders are authorized")

if missing:
    print(f"\n⚠️  MISSING: {len(missing)} expected subfolder(s) not found")
    for m in sorted(missing):
        print(f"  • {m}")
else:
    print(f"\n✅ All expected subfolders present")

print(f"\n{'✅ FULL COMPLIANCE' if not violations and not missing else '❌ NON-COMPLIANT'}")
