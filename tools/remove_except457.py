#!/usr/bin/env python3
"""Remove orphaned except at line 457"""

import pathlib

p = pathlib.Path('tools/analyze_persistent_memory_opportunities.py')
content = p.read_text(encoding='utf-8')
lines = content.splitlines(True)

# Remove orphaned except at line 457 and the continue after it
if len(lines) > 456:
    del lines[456]  # Line 457 (0-indexed)
if len(lines) > 456:
    del lines[456]  # Line 458 (now at 456)

p.write_text(''.join(lines), encoding='utf-8')
print('Removed orphaned except at line 457')
