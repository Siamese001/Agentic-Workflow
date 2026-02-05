#!/usr/bin/env python3
"""
Phase 1.1: Rename VALIDATOR files in L5_safety/validators/
Only renames files classified as VALIDATOR that don't already have _validator.py suffix
"""

import json
import subprocess
from pathlib import Path

# Load compliance report
with open("ssot_compliance_report.json", "r") as f:
    report = json.load(f)

# Filter for L5_safety/validators VALIDATOR violations
validators_to_rename = []
for violation in report["violations"]:
    path = violation["path"]
    classification = violation["classification"]

    # Only process VALIDATOR files in L5_safety/validators
    if (
        classification == "VALIDATOR"
        and "L5_safety\\validators" in path
        and not violation["is_naming_compliant"]
    ):
        validators_to_rename.append(path)

print(f"Found {len(validators_to_rename)} VALIDATOR files to rename in L5_safety/validators/")
print("\nFiles to rename:")

renames = []
for old_path in validators_to_rename:
    old_file = Path(old_path)

    # Convert to snake_case and add _validator suffix
    old_name = old_file.stem

    # Convert PascalCase to snake_case
    import re

    snake_name = re.sub(r"(?<!^)(?=[A-Z])", "_", old_name).lower()

    # Add _validator suffix if not present
    if not snake_name.endswith("_validator"):
        new_name = f"{snake_name}_validator.py"
    else:
        new_name = f"{snake_name}.py"

    new_path = old_file.parent / new_name

    renames.append((old_path, str(new_path)))
    print(f"  {old_path}")
    print(f"  -> {new_path}")
    print()

print(f"\nTotal files to rename: {len(renames)}")
print("\nProceed with renaming? (y/n): ", end="")
response = input().strip().lower()

if response == "y":
    print("\nExecuting renames using git mv...")
    for old_path, new_path in renames:
        try:
            result = subprocess.run(
                ["git", "mv", old_path, new_path], capture_output=True, text=True, check=True
            )
            print(f"✓ Renamed: {Path(old_path).name} -> {Path(new_path).name}")
        except subprocess.CalledProcessError as e:
            print(f"✗ Error renaming {old_path}: {e.stderr}")

    print("\n✓ Phase 1.1 complete!")
    print("Next steps:")
    print("1. Run tests: pytest tests/ -v")
    print("2. Check for broken imports")
    print(
        "3. Commit changes: git commit -m 'Phase 1.1: Rename VALIDATOR files in L5_safety/validators'"
    )
else:
    print("\nRename cancelled.")
