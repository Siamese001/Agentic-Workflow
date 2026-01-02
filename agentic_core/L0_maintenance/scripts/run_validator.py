from __future__ import annotations
"""
Simple wrapper to run the validator and capture output
"""
import subprocess
import sys
from typing import Any
result: Any = subprocess.run([sys.executable, 'canon_validator_agentic_v2.py', '--target', 'agentic_core'], cwd='.', capture_output=False, text=True)
sys.exit(result.returncode)
