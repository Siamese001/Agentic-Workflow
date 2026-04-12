#!/usr/bin/env python3
"""Add continue after except at line 348"""

import pathlib

p = pathlib.Path("tools/analyze_persistent_memory_opportunities.py")
content = p.read_text(encoding="utf-8")
lines = content.splitlines(True)

# Add continue after line 348
if len(lines) > 347:
    lines.insert(348, "                    continue\n")

p.write_text("".join(lines), encoding="utf-8")
print("Added continue after except at line 348")
