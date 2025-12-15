#!/usr/bin/env python3
"""
Test runner for apps_cv test suite
Bypasses parent conftest.py conflicts
"""

import sys
import os
import subprocess

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set test mode environment variable to force full validation flow
os.environ["CANON_TEST_MODE"] = "TRUE"

# Run pytest with specific configuration
cmd = [
    sys.executable, "-m", "pytest",
    "--confcutdir=.",  # Only use conftest.py in current directory
    "-v",
    "--tb=short",
    "."
]

print("Running apps_cv test suite...")
print("Test Mode: CANON_TEST_MODE=TRUE")
print("Command:", " ".join(cmd))
print("-" * 60)

result = subprocess.run(cmd, capture_output=False)

print("-" * 60)
if result.returncode == 0:
    print("✅ All apps_cv tests passed!")
else:
    print("❌ Some tests failed. Check output above.")
    sys.exit(result.returncode)
