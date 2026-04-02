import json

d = json.load(open('artifacts/collection_safety_phase1.json'))
missing_files = [f for f in d['files'] if f['status'] == 'missing']

# Count missing modules
missing_modules = {}
for f in missing_files:
    for issue in f['issues']:
        module = issue.split(': ')[1]
        missing_modules[module] = missing_modules.get(module, 0) + 1

print('Top 20 missing modules by frequency:')
for module, count in sorted(missing_modules.items(), key=lambda x: -x[1])[:20]:
    print(f"  {module}: {count} files")

print('\nTop 10 files with missing imports:')
for f in missing_files[:10]:
    print(f"  {f['file']}: {len(f['issues'])} issues")
    for issue in f['issues'][:3]:
        print(f"    {issue}")
