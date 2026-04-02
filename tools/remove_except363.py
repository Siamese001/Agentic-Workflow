#!/usr/bin/env python3
"""Remove orphaned except at line 363"""

import pathlib

p = pathlib.Path('tools/analyze_persistent_memory_opportunities.py')
content = p.read_text(encoding='utf-8')
lines = content.splitlines(True)

# Remove orphaned except at line 363 and the continue after it
if len(lines) > 362:
    del lines[362]  # Line 363 (0-indexed)
if len(lines) > 362:
    del lines[362]  # Line 364 (now at 362)

p.write_text(''.join(lines), encoding='utf-8')
print('Removed orphaned except at line 363')
