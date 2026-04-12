#!/usr/bin/env python3
"""Add outer except for try at line 220"""

import pathlib

p = pathlib.Path("tools/analyze_persistent_memory_opportunities.py")
content = p.read_text(encoding="utf-8")
lines = content.splitlines(True)

# Add outer except after line 247
if len(lines) > 247:
    lines.insert(248, "            except (ValueError, TypeError, RuntimeError):\n")
    lines.insert(249, "                continue\n")

p.write_text("".join(lines), encoding="utf-8")
print("Added outer except for try at line 220")
