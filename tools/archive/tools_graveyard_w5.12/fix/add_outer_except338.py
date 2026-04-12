#!/usr/bin/env python3
"""Add outer except for try at line 338"""

import pathlib

p = pathlib.Path("tools/analyze_persistent_memory_opportunities.py")
content = p.read_text(encoding="utf-8")
lines = content.splitlines(True)

# Add outer except after line 363
if len(lines) > 363:
    lines.insert(364, "            except (ValueError, TypeError, RuntimeError):\n")
    lines.insert(365, "                continue\n")

p.write_text("".join(lines), encoding="utf-8")
print("Added outer except for try at line 338")
