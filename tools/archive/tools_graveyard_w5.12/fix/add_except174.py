#!/usr/bin/env python3
"""Add except for try at line 174"""

import pathlib

p = pathlib.Path("tools/analyze_persistent_memory_opportunities.py")
content = p.read_text(encoding="utf-8")
lines = content.splitlines(True)

# Find the end of the try block and add except
for i in range(175, len(lines)):
    if "}" in lines[i] and "patterns_found" in lines[i]:
        # Add except after this line
        lines.insert(i + 1, "\n")
        lines.insert(i + 2, "            except (ValueError, TypeError, RuntimeError):\n")
        lines.insert(i + 3, "                continue\n")
        break

p.write_text("".join(lines), encoding="utf-8")
print("Added except for try at line 174")
