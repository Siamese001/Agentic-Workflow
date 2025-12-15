#!/usr/bin/env python3
"""
Test runner for apps_cv test suite
Bypasses parent conftest.py conflicts
"""

import os
import subprocess
import sys

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

# print("Running apps_cv test suite...")  # [Security Fix]
# print("Test Mode: CANON_TEST_MODE=TRUE")  # [Security Fix]
# print("Command:", " ".join(cmd))  # [Security Fix]
# print("-" * 60)  # [Security Fix]

result = subprocess.run(cmd, capture_output=False)

# print("-" * 60)  # [Security Fix]
if result.returncode == 0:
    # print("✅ All apps_cv tests passed!")  # [Security Fix]
else:
    # print("❌ Some tests failed. Check output above.")  # [Security Fix]
    sys.exit(result.returncode)

