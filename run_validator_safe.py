#!/usr/bin/env python3
"""Run validator with safe output handling."""

import sys
import os

# Set UTF-8 encoding for stdout
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Now import and run the validator
os.chdir('c:/Git/Agentic-Workflow')
sys.path.insert(0, 'c:/Git/Agentic-Workflow')

# Import validator module
import canon_validator

# Run all checks and collect results
canon_validator.results = {}
canon_validator.main()
