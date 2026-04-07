#!/usr/bin/env python3
"""Clean up dummy _emit_reads_through calls from static_scanner.py"""

import re

filepath = r'c:\Git\Agentic-Workflow\agentic_core\adg\extraction\static_scanner.py'

with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

# Remove all lines matching _emit_reads_through("l4", "static_scanner", "urg_read_...")
pattern = r'^_emit_reads_through\("l4", "static_scanner", "urg_read_\d+"\)\s*$'
lines = content.split('\n')
filtered_lines = [line for line in lines if not re.match(pattern, line)]

removed_count = len(lines) - len(filtered_lines)
print(f'Removed {removed_count} dummy _emit_reads_through lines')

with open(filepath, 'w', encoding='utf-8') as f:
    f.write('\n'.join(filtered_lines))

print('File cleaned successfully')
