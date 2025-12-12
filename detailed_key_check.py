#!/usr/bin/env python3
"""Detailed check of Key 29 and Key 30 status."""

import subprocess
import sys
import json

# Run the validator and capture full output
result = subprocess.run(
    [sys.executable, 'canon_validator.py'],
    capture_output=True,
    text=True,
    errors='replace',
    encoding='utf-8'
)

output = result.stdout
stderr = result.stderr

# Save full output to file for inspection
with open('validator_full_output.txt', 'w', encoding='utf-8', errors='replace') as f:
    f.write(output)
    f.write("\n\n=== STDERR ===\n\n")
    f.write(stderr)

print("Full validator output saved to validator_full_output.txt")
print("\nSearching for Key 29 and Key 30...")

lines = output.split('\n')
for i, line in enumerate(lines):
    if 'Key 29' in line or 'Key 30' in line:
        # Print this line and next 20 lines
        print(f"\nLine {i}: {line}")
        for j in range(1, 21):
            if i + j < len(lines):
                next_line = lines[i + j]
                if next_line.strip() and not next_line.startswith('='):
                    print(f"  {next_line}")
                if next_line.startswith('['):
                    break
