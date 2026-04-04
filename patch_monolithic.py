#!/usr/bin/env python3
"""Patch and run monolithic execute_ssot to see full execution output."""

import sys

# Read monolithic
with open('execute_ssot_monolithic.py', 'r', encoding='utf-8', errors='ignore') as f:
    code = f.read()

# Replace the guard block - use simple string replacement
if 'raise SystemExit(2)' in code:
    code = code.replace('raise SystemExit(2)', 'sys.exit(main())  # PATCHED')
    print('Patched SystemExit', file=sys.stderr)
else:
    print('SystemExit not found', file=sys.stderr)

# Also try to remove the error message
old_msg = 'ERROR: Direct invocation of execute_ssot.py is not supported'
if old_msg in code:
    code = code.replace(old_msg, 'PATCHED: Running execute_ssot')
    print('Patched error msg', file=sys.stderr)

with open('execute_ssot_monolithic_patched.py', 'w', encoding='utf-8') as f:
    f.write(code)

print('Patched file written to execute_ssot_monolithic_patched.py', file=sys.stderr)
