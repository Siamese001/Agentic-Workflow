"""Analyze skipped modules from P0 wiring campaign."""
import csv
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SKIP_PATTERNS = {
    "_constants.py",
    "conftest.py",
    "structure_blueprint_config.py",
    "ssot_tier_constants.py",
    "path_constants.py",
    "lifecycle_trace_contract.py",
}

# Read deficit modules
deficit_csv = PROJECT_ROOT / "runtime_gaps" / "trace_deficit_modules.csv"
with open(deficit_csv) as f:
    deficit_modules = list(csv.DictReader(f))

# Find modules matching skip patterns
skipped = []
for module in deficit_modules:
    path = module['source_file']
    for pattern in SKIP_PATTERNS:
        if pattern in path:
            skipped.append((path, pattern))
            break

print(f"Total deficit modules: {len(deficit_modules)}")
print(f"Modules matching skip patterns: {len(skipped)}")
print("\nSkipped modules by pattern:")
print("=" * 80)

for pattern in sorted(SKIP_PATTERNS):
    matching = [s for s in skipped if s[1] == pattern]
    if matching:
        print(f"\n{pattern}: {len(matching)} modules")
        for path, _ in sorted(matching):
            print(f"  {path}")
