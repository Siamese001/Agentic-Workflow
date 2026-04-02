#!/usr/bin/env python3
"""Remove orphaned except at line 201 in check_adg_persistence.py"""

import pathlib

p = pathlib.Path('tools/check_adg_persistence.py')
content = p.read_text(encoding='utf-8')
lines = content.splitlines(True)

# Remove orphaned except at line 201
if len(lines) > 200:
    del lines[200]  # Line 201 (0-indexed)

p.write_text(''.join(lines), encoding='utf-8')
print('Removed orphaned except at line 201 in check_adg_persistence.py')
