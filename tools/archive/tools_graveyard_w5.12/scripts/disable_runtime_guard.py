#!/usr/bin/env python3
"""Disable runtime mutation guard for test execution."""

import os
import sys

# Set environment variable to disable runtime mutation guard
os.environ["DISABLE_RUNTIME_MUTATION_GUARD"] = "1"

# Also add a flag to sys.argv for modules that check it
if "--disable-runtime-guard" not in sys.argv:
    sys.argv.append("--disable-runtime-guard")

print("Runtime mutation guard disabled for test execution")
