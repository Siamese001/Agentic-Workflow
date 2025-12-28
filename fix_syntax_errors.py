"""Script to fix corrupted logger.info statements in Python files."""
import re
from pathlib import Path

fixed_count = 0
for p in Path('agentic_core').rglob('*.py'):
    if '__pycache__' in str(p) or 'archives' in str(p):
        continue
    try:
        content = p.read_text(encoding='utf-8', errors='ignore')
        original = content
        
        # Pattern 1: Remove logger.info lines that appear between import statements
        content = re.sub(r'^logger\.info\("\[L6_AUDIT\].*?"\)\n', '', content, flags=re.MULTILINE)
        
        # Pattern 2: Remove logger.info inside parentheses (import blocks)
        content = re.sub(r'^\s+logger\.info\("\[L6_AUDIT\].*?"\)\n', '', content, flags=re.MULTILINE)
        
        if content != original:
            p.write_text(content, encoding='utf-8')
            fixed_count += 1
            print(f'Fixed: {p}')
    except Exception as e:
        print(f'Error in {p}: {e}')

print(f'\nTotal files fixed: {fixed_count}')
