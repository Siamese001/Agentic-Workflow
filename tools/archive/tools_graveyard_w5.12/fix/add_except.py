#!/usr/bin/env python3
"""Add missing except block in analyze_persistent_memory_opportunities.py"""

import pathlib

p = pathlib.Path("tools/analyze_persistent_memory_opportunities.py")
content = p.read_text(encoding="utf-8")
lines = content.splitlines(True)

# Add except after line 132
for i, line in enumerate(lines):
    if i == 131:  # After line 132 (0-indexed)
        if 'self.analysis["learning_artifacts"]' in line:
            lines.insert(i + 1, "\n")
            lines.insert(i + 2, "            except (ValueError, TypeError, RuntimeError):\n")
            lines.insert(i + 3, "                continue\n")

p.write_text("".join(lines), encoding="utf-8")
print("Added missing except in analyze_persistent_memory_opportunities.py")
