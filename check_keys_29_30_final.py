#!/usr/bin/env python3
"""Check final status of Key 29 and Key 30."""

import subprocess
import sys

def main():
    """Run validator and extract Key 29 and Key 30 status."""
    try:
        result = subprocess.run(
            [sys.executable, "canon_validator.py"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        output = result.stdout + result.stderr
        lines = output.split('\n')
        
        print("\n" + "="*80)
        print("KEY 29 AND KEY 30 FINAL STATUS")
        print("="*80)
        
        for i, line in enumerate(lines):
            if 'Key 29' in line or 'Key 30' in line:
                print(line)
                # Print next 20 lines for context if FAIL
                if 'FAIL' in line:
                    for j in range(i+1, min(i+21, len(lines))):
                        if lines[j].strip() and not lines[j].startswith('['):
                            print(lines[j])
                        elif lines[j].startswith('['):
                            break
        
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        
        key_29_pass = any('Key 29' in line and 'PASS' in line for line in lines)
        key_30_pass = any('Key 30' in line and 'PASS' in line for line in lines)
        
        print(f"Key 29 (Function Length): {'✅ PASSING' if key_29_pass else '❌ FAILING'}")
        print(f"Key 30 (Nesting Depth): {'✅ PASSING' if key_30_pass else '❌ FAILING'}")
        
        if key_29_pass and key_30_pass:
            print("\n🎉 100% COMPLEXITY COMPLIANCE ACHIEVED!")
        else:
            print(f"\n⚠️  Remaining violations to fix")
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
