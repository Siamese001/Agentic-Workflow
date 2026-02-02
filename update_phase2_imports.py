#!/usr/bin/env python3
"""Update imports for Phase 2 renamed TYPES files"""
import json
import re
from pathlib import Path

with open('ssot_compliance_report.json', 'r') as f:
    report = json.load(f)

def to_snake_case(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

# Build renames map from TYPES violations
renames = {}
for v in report['violations']:
    if v['classification'] != 'TYPES':
        continue
    if v['is_naming_compliant']:
        continue
    path = v['path']
    if 'archives' in path.lower():
        continue
    stem = Path(path).stem
    if stem.endswith('_types'):
        continue
    snake = to_snake_case(stem)
    new_name = f"{snake}_types" if not snake.endswith('_types') else snake
    renames[stem] = new_name

print(f"Import patterns to update: {len(renames)}")

def update_file(fp):
    try:
        content = fp.read_text(encoding='utf-8')
        orig = content
        for old, new in renames.items():
            content = re.sub(rf'(from\s+\S+\.){re.escape(old)}(\s+import)', rf'\g<1>{new}\2', content)
            content = re.sub(rf'(import\s+\S+\.){re.escape(old)}(\s|$)', rf'\g<1>{new}\2', content)
        if content != orig:
            fp.write_text(content, encoding='utf-8')
            return True
        return False
    except:
        return False

updated = 0
for py in Path('.').rglob('*.py'):
    if 'phase' in py.name.lower() or 'update_' in py.name:
        continue
    if update_file(py):
        updated += 1

print(f"\n✓ Updated {updated} files")
