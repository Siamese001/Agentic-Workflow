#!/usr/bin/env python3
"""Check Key 29 and Key 30 status by running checks directly."""

import sys
import os
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

# Import validator functions
from canon_validator import (
    check_key_29_function_length_limits,
    check_key_30_nesting_depth_limits,
    results
)

print("="*70)
print("CHECKING KEY 29 & KEY 30 STATUS")
print("="*70)

# Clear results
results.clear()

# Run Key 29 check
print("\n[Running Key 29 check...]")
try:
    check_key_29_function_length_limits()
    if 29 in results:
        passed, message = results[29]
        status = "PASS" if passed else "FAIL"
        print(f"Key 29: {status}")
        print(f"Message: {message[:200]}")
    else:
        print("Key 29: No result recorded")
except Exception as e:
    print(f"Key 29: ERROR - {e}")

# Run Key 30 check
print("\n[Running Key 30 check...]")
try:
    check_key_30_nesting_depth_limits()
    if 30 in results:
        passed, message = results[30]
        status = "PASS" if passed else "FAIL"
        print(f"Key 30: {status}")
        print(f"Message: {message[:200]}")
    else:
        print("Key 30: No result recorded")
except Exception as e:
    print(f"Key 30: ERROR - {e}")

print("\n" + "="*70)
