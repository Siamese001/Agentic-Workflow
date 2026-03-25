#!/usr/bin/env python3
"""Fix orphaned except in check_adg_persistence.py"""

import pathlib

p = pathlib.Path('tools/check_adg_persistence.py')
content = p.read_text(encoding='utf-8')
lines = content.splitlines(True)

# Remove orphaned except at line 181
if len(lines) > 180:
    del lines[180]  # Line 181 (0-indexed)

p.write_text(''.join(lines), encoding='utf-8')
print('Removed orphaned except in check_adg_persistence.py')
