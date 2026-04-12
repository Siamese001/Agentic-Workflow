#!/usr/bin/env python3
"""Add outer except for try at line 431"""

import pathlib

p = pathlib.Path("tools/analyze_persistent_memory_opportunities.py")
content = p.read_text(encoding="utf-8")
lines = content.splitlines(True)

# Add outer except after line 458
if len(lines) > 458:
    lines.insert(459, "            except (ValueError, TypeError, RuntimeError):\n")
    lines.insert(460, "                continue\n")

p.write_text("".join(lines), encoding="utf-8")
print("Added outer except for try at line 431")
