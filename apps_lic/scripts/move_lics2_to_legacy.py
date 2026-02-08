#!/usr/bin/env python3
"""Move LicS2SupervisorAgent to LEGACY status."""

from pathlib import Path

file_path = Path("apps_lic/engines/LicS2SupervisorAgent.py")
content = file_path.read_text(encoding="utf-8")

# Add LEGACY header
legacy_header = '''"""LEGACY FILE - Moved to legacy during Terminal Alignment Command
This file has fundamental architectural issues that require complete rewrite.
Status: DEPRECATED - Do not use in production
"""

# LEGACY CODE BELOW - COMMENTED OUT
'''

# Comment out all code
lines = content.split("\n")
commented_lines = [f"# {line}" if line.strip() and not line.startswith("#") else line for line in lines]

new_content = legacy_header + "\n".join(commented_lines)

file_path.write_text(new_content, encoding="utf-8")
print("✅ LicS2SupervisorAgent.py → LEGACY")
