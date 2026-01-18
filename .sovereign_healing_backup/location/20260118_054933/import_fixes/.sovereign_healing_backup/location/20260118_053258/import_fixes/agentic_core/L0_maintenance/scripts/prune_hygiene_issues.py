from __future__ import annotations
#!/usr/bin/env python3
"""
Hygiene Pruner - Interactive Dead Code and Duplicate Cleanup
Safely removes orphaned files and duplicates with user confirmation
"""
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from agentic_core.L0_maintenance.scripts.hygiene_validator import HygieneValidatorAgent

from agentic_core.L5_safety.validators.structure_blueprint_2 import (
    AGENT_DISCOVERY_JSON,
    AGENT_DISCOVERY_MANIFEST_JSON,
    AGENTIC_CORE_DIR,
    SCRIPTS_DIR,
    TESTS_DIR,
    DASHBOARD_DIR,
    L0_MAINTENANCE_DIR,
    L1_COGNITION_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    L5_SAFETY_DIR,
    L6_OBSERVABILITY_DIR,
    get_validated_project_root,
)


def prompt_user(question, default="no"):
    """Ask a yes/no question via input() and return their answer."""
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == "":
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' (or 'y'/'n').\n")


class HygienePruner:
    """Interactive cleanup tool for dead code and duplicates."""

    def __init__(self, root_path):
        self.root_path = Path(root_path)
        self.validator = HygieneValidatorAgent(str(root_path))
        print(f"Scanning {root_path} for hygiene issues...")
        self.validator.scan()
        self.deleted_count = 0
        self.skipped_count = 0

    def handle_duplicates(self):
        """Interactively resolve duplicate files."""
        print("\n" + "=" * 70)
        print("PHASE 1: DUPLICATE RESOLUTION")
        print("=" * 70)

        duplicates = [
            (fhash, paths)
            for fhash, paths in self.validator.file_hashes.items()
            if len(paths) > 1
        ]

        # Filter out __init__.py duplicates (often legitimately empty)
        duplicates = [
            (fhash, paths)
            for fhash, paths in duplicates
            if not all(p.endswith("__init__.py") for p in paths)
        ]

        if not duplicates:
            print("No duplicates found. Excellent.")
            return

        print(f"Found {len(duplicates)} sets of duplicate files.")

        for i, (fhash, paths) in enumerate(duplicates, 1):
            print(f"\nSet {i}/{len(duplicates)} (Hash: {fhash[:8]}...)")
            for idx, p in enumerate(paths):
                file_size = os.path.getsize(self.root_path / p)
                print(f"  [{idx}] {p} ({file_size} bytes)")

            try:
                choice = input(
                    f"Enter the index of the file to KEEP (0-{len(paths)-1}), or 's' to skip: "
                )
                if choice.lower() == "s":
                    print("Skipping...")
                    self.skipped_count += len(paths) - 1
                    continue

                keep_idx = int(choice)
                if 0 <= keep_idx < len(paths):
                    survivor = paths[keep_idx]
                    # Delete the others
                    for idx, p in enumerate(paths):
                        if idx != keep_idx:
                            self._delete_file(p)
                    print(f"  -> Kept: {survivor}")
                else:
                    print("Invalid index. Skipping.")
                    self.skipped_count += len(paths) - 1
            except ValueError:
                print("Invalid input. Skipping.")
                self.skipped_count += len(paths) - 1

    def handle_orphans(self):
        """Interactively remove orphaned files."""
        print("\n" + "=" * 70)
        print("PHASE 2: ORPHAN REMOVAL")
        print("=" * 70)

        orphans = self.validator.get_orphans_raw()

        if not orphans:
            print("No orphaned files found.")
            return

        print(f"Found {len(orphans)} potential orphaned files (never imported).")
        print("WARNING: Static analysis may miss dynamic imports (e.g. importlib, string refs).")
        print("Review carefully before deleting.")
        print()

        # Group orphans by directory for easier review
        from collections import defaultdict

        orphans_by_dir = defaultdict(list)
        for path in orphans:
            dir_name = os.path.dirname(path)
            orphans_by_dir[dir_name].append(path)

        # Process directory by directory
        for dir_name in sorted(orphans_by_dir.keys()):
            files = orphans_by_dir[dir_name]
            print(f"\nDirectory: {dir_name or '(root)'} ({len(files)} orphans)")

            # Offer bulk delete for directory
            if len(files) > 5:
                if prompt_user(f"Delete all {len(files)} orphans in this directory?", default="no"):
                    for path in files:
                        self._delete_file(path)
                    continue

            # Individual file review
            for path in files:
                file_size = os.path.getsize(self.root_path / path)
                if prompt_user(f"Delete orphan '{path}' ({file_size} bytes)?", default="no"):
                    self._delete_file(path)
                else:
                    print("  -> Skipped.")
                    self.skipped_count += 1

    def _delete_file(self, rel_path):
        """Delete a file and report the action."""
        full_path = self.root_path / rel_path
        try:
            os.remove(full_path)
            print(f"  [DELETED] {rel_path}")
            self.deleted_count += 1
        except OSError as e:
            print(f"  [ERROR] Could not delete {rel_path}: {e}")

    def print_summary(self):
        """Print summary of cleanup actions."""
        print("\n" + "=" * 70)
        print("HYGIENE PRUNING SUMMARY")
        print("=" * 70)
        print(f"Files deleted: {self.deleted_count}")
        print(f"Files skipped: {self.skipped_count}")
        print(f"Total reviewed: {self.deleted_count + self.skipped_count}")


if __name__ == "__main__":
    # Default to agentic_core directory
    if len(sys.argv) > 1:
        target_dir = sys.argv[1]
    else:
        # Default to agentic_core from project root
        script_dir = Path(__file__).parent
        target_dir = script_dir.parent.parent.parent  # Go up to project root
        target_dir = target_dir / AGENTIC_CORE_DIR

    target_dir = Path(target_dir).resolve()

    # Safety check
    if not target_dir.exists():
        print(f"Error: Directory '{target_dir}' does not exist.")
        sys.exit(1)

    print(f"Target directory: {target_dir}")
    print("This script will help you clean up dead code and duplicates.")
    print("You will be prompted before any files are deleted.")
    print()

    if not prompt_user("Continue with hygiene pruning?", default="yes"):
        print("Aborted by user.")
        sys.exit(0)

    pruner = HygienePruner(target_dir)
    pruner.handle_duplicates()
    pruner.handle_orphans()
    pruner.print_summary()

    print("\n=== HYGIENE PRUNING COMPLETE ===")
