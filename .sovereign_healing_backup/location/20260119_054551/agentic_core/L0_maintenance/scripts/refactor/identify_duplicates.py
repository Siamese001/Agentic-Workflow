"""
Identify the exact 7 duplicate files to remove for 287 baseline.
"""
import json
from pathlib import Path
from agentic_core.utils.file_utils import safe_read_file, safe_write_file

report_path = Path('deduplication_report.json')
with open(report_path) as f:
    report = json.load(f)

print("="*80)
print("IDENTIFYING 7 DUPLICATES TO REMOVE")
print("="*80)
print()

# Find legacy duplicates
legacy_duplicates = [
    a for a in report['duplicate_analyses'] 
    if a['verdict'] == 'legacy_duplicate'
]

# Find true duplicates
true_duplicates = [
    a for a in report['duplicate_analyses'] 
    if a['verdict'] == 'true_duplicate'
]

print(f"Legacy duplicates found: {len(legacy_duplicates)}")
print(f"True duplicates found: {len(true_duplicates)}")
print()

files_to_remove = []

# Extract legacy files
print("LEGACY DUPLICATES (Remove legacy versions):")
for dup in legacy_duplicates:
    print(f"\n{dup['agent_name']}:")
    for loc in dup['locations']:
        if loc['is_legacy']:
            print(f"  [REMOVE] {loc['path']}")
            files_to_remove.append(loc['path'])
        else:
            print(f"  [KEEP]   {loc['path']}")

print()
print("="*80)
print("TRUE DUPLICATES (Keep one, remove others):")
for dup in true_duplicates:
    print(f"\n{dup['agent_name']}:")
    locations = dup['locations']
    # Keep first, remove rest
    for i, loc in enumerate(locations):
        if i == 0:
            print(f"  [KEEP]   {loc['path']}")
        else:
            print(f"  [REMOVE] {loc['path']}")
            files_to_remove.append(loc['path'])

print()
print("="*80)
print(f"TOTAL FILES TO REMOVE: {len(files_to_remove)}")
print("="*80)

for f in files_to_remove:
    print(f"  - {f}")

# Save to file for surgical deduplication script
output = {
    "files_to_remove": files_to_remove,
    "count": len(files_to_remove),
    "expected_result": 294 - len(files_to_remove)
}

with open('duplicates_to_remove.json', 'w') as f:
    json.dump(output, f, indent=2)

print()
print(f"Expected agent count after removal: {output['expected_result']}")
print("Saved to: duplicates_to_remove.json")
