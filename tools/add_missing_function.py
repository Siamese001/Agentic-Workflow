#!/usr/bin/env python3
"""Add missing _get_call_name function to static_scanner.py"""

import re

# Read the file
with open('agentic_core/adg/extraction/static_scanner.py', encoding='utf-8') as f:
    content = f.read()

# Check if function already exists
if 'def _get_call_name' in content:
    print('_get_call_name already exists')
    exit(0)

# Add the function after _sym_of function
new_function = '''

def _get_call_name(node: ast.expr) -> str:
    """Extract full call name from AST expression node."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parts = []
        cur: ast.expr = node
        while isinstance(cur, ast.Attribute):
            parts.append(cur.attr)
            cur = cur.value
        if isinstance(cur, ast.Name):
            parts.append(cur.id)
        return '.'.join(reversed(parts))
    return ''
'''

# Find a good insertion point - after _sym_of function
marker = 'def _sym_of(node: ast.expr) -> str:'
if marker in content:
    # Find end of _sym_of function
    pattern = r'(def _sym_of\(node: ast\.expr\) -> str:.*?return "")'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        insert_pos = match.end()
        content = content[:insert_pos] + new_function + content[insert_pos:]
        with open('agentic_core/adg/extraction/static_scanner.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print('Added _get_call_name function after _sym_of')
    else:
        print('Could not find insertion point')
        exit(1)
else:
    print('Could not find _sym_of function')
    exit(1)
