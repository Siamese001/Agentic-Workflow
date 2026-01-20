"""
Canon Key Semantic Renaming Tool.

Phase 8: Zombie Key Cleanup

This script renames validator methods from `check_key_X_name` to `check_name`,
removing the legacy numeric key prefixes that are now meaningless.

Usage:
    python refactor_canon_renaming.py --dry-run
    python refactor_canon_renaming.py --apply
"""
import os
import re
import sys
from typing import List, Tuple

# Configuration
TARGET_DIR = "agentic_core/L5_safety/validators"
PATTERN = r"def (check)_key_\d+_([a-zA-Z0-9_]+)\(self"
REPLACEMENT = r"def \1_\2(self"

# Files to explicitly target (Safety filter)
TARGET_FILES = [
    "CanonDependencySentinelAgent.py",
    "StructuralEngineerAgent.py",
    "CodeJanitorAgent.py",
    "TypeMechanicAgent.py",
    "SystemArchitectAgent.py",
    "DocumentationAgent.py",
]


def get_files(directory: str) -> List[str]:
    """Find target Python files in the directory."""
    found_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py") and file in TARGET_FILES:
                found_files.append(os.path.join(root, file))
    return found_files


def process_file(filepath: str, apply: bool = False) -> int:
    """
    Process a single file, renaming check_key_X_ methods.
    
    Returns the number of changes made.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find all matches
    matches = re.findall(PATTERN, content)
    if not matches:
        return 0

    print(f"Processing {filepath}...")
    new_content = content
    
    # 1. Rename Definitions
    # Pattern: def check_key_10_syntax(self -> def check_syntax(self
    new_content = re.sub(PATTERN, REPLACEMENT, new_content)

    # 2. Rename Calls (Heuristic: self.check_key_10_syntax -> self.check_syntax)
    call_pattern = r"(self\.|super\(\)\.)(check)_key_\d+_([a-zA-Z0-9_]+)"
    call_replacement = r"\1\2_\3"
    new_content = re.sub(call_pattern, call_replacement, new_content)

    changes = 0
    if content != new_content:
        for line in new_content.splitlines():
            if "def check_" in line and "check_key_" not in line:
                print(f"  [Proposed] {line.strip()}")
                changes += 1
        
        if apply:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"  ✅ Updated {filepath}")
        else:
            print(f"  ⚠️ Dry Run: {changes} method renames identified (not applied)")
    else:
        print(f"  No changes needed for {filepath}")
    
    return changes


def main():
    args = sys.argv[1:]
    apply = "--apply" in args
    
    print("=== Canon Key Semantic Renaming Tool ===")
    print(f"Target Directory: {TARGET_DIR}")
    print(f"Mode: {'APPLYING CHANGES' if apply else 'DRY RUN'}")
    print()
    
    files = get_files(TARGET_DIR)
    if not files:
        print("No target files found.")
        return

    total_changes = 0
    for filepath in files:
        total_changes += process_file(filepath, apply)
    
    print()
    print(f"Total changes: {total_changes}")
    if not apply and total_changes > 0:
        print("\nDry Run complete. Run with --apply to apply changes.")


if __name__ == "__main__":
    main()
