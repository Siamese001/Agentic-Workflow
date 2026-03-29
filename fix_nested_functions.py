import os
import re

def fix_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Pattern: nested def test_placeholder_execution inside another test function
    # Find and remove the nested function definition
    pattern = r'def test_placeholder_execution\(mod\):\s*"""[^"]*"""\s*'
    
    new_content = re.sub(pattern, '', content, flags=re.DOTALL)
    
    # Also fix duplicate ), "Result should be a common type"), "Result should be a common type"
    new_content = new_content.replace('), "Result should be a common type"), "Result should be a common type"', '), "Result should be a common type"')
    
    if new_content != content:
        with open(filepath, 'w') as f:
            f.write(new_content)
        return True
    return False

# Fix all files
test_dir = 'tests/unit/agentic_core'
fixed = 0
for root, dirs, files in os.walk(test_dir):
    for f in files:
        if f.endswith('_adg.py'):
            filepath = os.path.join(root, f)
            if fix_file(filepath):
                fixed += 1
                print(f'Fixed: {filepath}')

print(f'\nTotal fixed: {fixed}')
