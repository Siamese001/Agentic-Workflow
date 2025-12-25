#!/usr/bin/env python3
"""
Simple wrapper to run the validator and capture output
"""
import sys

import subprocess

result = subprocess.run(
    [sys.executable, "canon_validator_agentic_v2.py", "--target", "agentic_core"],
    cwd=".",
    capture_output=False,
    text=True
)

sys.exit(result.returncode)
