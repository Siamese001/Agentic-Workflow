#!/usr/bin/env python3
"""
DEPRECATED WRAPPER - Use consolidated location instead

This file is a backward-compatibility wrapper.
The actual implementation has moved to:
  agentic_core/L6_observability/dashboards/scripts/generate_ssot.py

Usage:
  python agentic_core/L6_observability/dashboards/scripts/generate_ssot.py
"""
import subprocess
import sys
from pathlib import Path

print("⚠️  DEPRECATED: This wrapper is for backward compatibility only.")
print("📍 New location: agentic_core/L6_observability/dashboards/scripts/generate_ssot.py")
print()

# Call the new location
new_script = Path(__file__).parent.parent / "agentic_core" / "L6_observability" / "dashboards" / "scripts" / "generate_ssot.py"
result = subprocess.run([sys.executable, str(new_script)], cwd=Path(__file__).parent.parent)
sys.exit(result.returncode)
