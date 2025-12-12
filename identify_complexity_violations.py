#!/usr/bin/env python3
"""Identify Key 29 (function length) and Key 30 (nesting depth) violations."""

import subprocess
import sys
import re

def extract_violations():
    """Run validator and extract Key 29 and Key 30 violations."""
    result = subprocess.run(
        [sys.executable, 'canon_validator.py'],
        capture_output=True,
        text=True,
        errors='replace'
    )
    
    lines = result.stdout.split('\n')
    
    key29_violations = []
    key30_violations = []
    
    in_key29 = False
    in_key30 = False
    
    for i, line in enumerate(lines):
        # Detect Key 29 section
        if 'Key 29' in line and 'FAIL' in line:
            in_key29 = True
            in_key30 = False
            continue
        
        # Detect Key 30 section
        if 'Key 30' in line and 'FAIL' in line:
            in_key30 = True
            in_key29 = False
            continue
        
        # Stop at next key
        if line.startswith('[') and ('Key' in line or 'PASS' in line or 'FAIL' in line):
            in_key29 = False
            in_key30 = False
            continue
        
        # Collect violations
        if in_key29 and line.strip() and not line.startswith('='):
            key29_violations.append(line.strip())
        
        if in_key30 and line.strip() and not line.startswith('='):
            key30_violations.append(line.strip())
    
    return key29_violations, key30_violations

def main():
    print("="*70)
    print("COMPLEXITY DEBT VIOLATIONS - Key 29 & Key 30")
    print("="*70)
    
    key29, key30 = extract_violations()
    
    print(f"\n[KEY 29] Function Length Violations (>100 lines): {len(key29)}")
    print("-"*70)
    for v in key29:
        print(f"  {v}")
    
    print(f"\n[KEY 30] Nesting Depth Violations (>5): {len(key30)}")
    print("-"*70)
    for v in key30:
        print(f"  {v}")
    
    print("\n" + "="*70)
    print(f"TOTAL VIOLATIONS: {len(key29) + len(key30)}")
    print("="*70)

if __name__ == "__main__":
    main()
