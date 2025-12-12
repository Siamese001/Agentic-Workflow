#!/usr/bin/env python3
"""Check current status of all validator keys."""

import subprocess
import sys

result = subprocess.run(
    [sys.executable, 'canon_validator.py'],
    capture_output=True,
    text=True,
    errors='replace'
)

lines = result.stdout.split('\n')

# Find pass count
for line in lines:
    if 'KEYS PASSED' in line:
        print(line)
        print()

# Extract all PASS/FAIL status
print("KEY STATUS SUMMARY:")
print("="*70)

passing = []
failing = []

for line in lines:
    if line.strip().startswith('[PASS]') or line.strip().startswith('[FAIL]'):
        # Clean up the line
        clean_line = line.replace('\u2713', 'OK').replace('\u26a0', '!')
        if '[PASS]' in line:
            passing.append(clean_line.strip())
        else:
            failing.append(clean_line.strip())

print(f"\nPASSING KEYS ({len(passing)}):")
for p in passing[:10]:
    print(f"  {p[:80]}")
if len(passing) > 10:
    print(f"  ... and {len(passing) - 10} more")

print(f"\nFAILING KEYS ({len(failing)}):")
for f in failing[:15]:
    print(f"  {f[:80]}")
if len(failing) > 15:
    print(f"  ... and {len(failing) - 15} more")

print("\n" + "="*70)
