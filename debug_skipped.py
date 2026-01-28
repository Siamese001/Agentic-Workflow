from pathlib import Path

PROJECT_ROOT = Path('.')
skipped_files = set()

with open(PROJECT_ROOT / 'migration_execution.log', 'r') as f:
    for line in f:
        if 'SKIP: Source missing' in line:
            if 'C:\\Git\\Agentic-Workflow\\' in line:
                abs_path = line.split('SKIP: Source missing ')[1].strip()
                rel_path = abs_path.replace('C:\\Git\\Agentic-Workflow\\', '').replace('\\', '/')
                skipped_files.add(rel_path)

print('Skipped files (first 10):')
for f in sorted(skipped_files)[:10]:
    print(f'  "{f}"')

print()
print('Target files:')
targets = ['tests/fixtures/__init__.py', 'tests/unit/__init__.py', 'tests/unit/apps_lic/__init__.py']
for t in targets:
    print(f'  "{t}" in skipped: {t in skipped_files}')
    if t in skipped_files:
        print(f'    MATCH FOUND!')
