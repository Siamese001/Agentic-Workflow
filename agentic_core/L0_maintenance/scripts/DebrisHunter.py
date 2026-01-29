r"""
File: scripts/DebrisHunter.py
Path: C:\Git\Agentic-Workflow\scripts/DebrisHunter.py
Status: Post-Migration Utility
Rationale:
    Identifies and cleans up:
    1. "Split-Brain" files (snake_case.py existing alongside PascalCase.py).
    2. The redundant legacy fixer script in agentic_core.
    3. __temp_ artifacts if any rename operations were interrupted.
"""

import os
import sys
from pathlib import Path

# SSOT Integration
try:
    from agentic_core.L5_safety.validators.structure_blueprint import get_python_files
except ImportError:

    def get_python_files(root: Path):
        return list(root.rglob("*.py"))


class DebrisHunter:
    def __init__(self, root: Path, dry_run: bool = True):
        self.root = root
        self.dry_run = dry_run
        self.debris_found = []

    def scan_for_collisions(self):
        """
        Finds directories containing both 'snake_case.py' and 'PascalCase.py'
        where one is likely the ancestor of the other.
        """
        print(f"Scanning for collision debris in {self.root}...")

        # Walk manually to group by directory
        for dirpath, _, filenames in os.walk(self.root):
            # Skip .git, __pycache__, archives
            if any(skip in dirpath for skip in [".git", "__pycache__", "archives", "node_modules"]):
                continue

            py_files = [f for f in filenames if f.endswith(".py")]

            # Map lowercase -> actual_name
            lowermap = {f.lower(): f for f in py_files}

            for f in py_files:
                # If current file is snake_case (has underscores, starts lower)
                if "_" in f and f[0].islower():
                    # Check if a "clean" PascalCase version exists
                    pascal_guess = f.replace("_", "").lower()

                    if pascal_guess in lowermap:
                        partner = lowermap[pascal_guess]
                        # Heuristic: If partner is MixedCase/PascalCase, we have a collision
                        if "_" not in partner and partner[0].isupper():
                            self.debris_found.append(Path(dirpath) / f)
                            print(f"[DEBRIS] Found ghost file: {f} (Shadowed by {partner})")

    def scan_for_known_redundancies(self):
        """Targeted cleanup for known migration artifacts."""
        legacy_fixer = (
            self.root
            / "agentic_core"
            / "L0_maintenance"
            / "scripts"
            / "pascal_sovereignty_fixer.py"
        )
        if legacy_fixer.exists():
            self.debris_found.append(legacy_fixer)
            print(f"[REDUNDANT] Found legacy fixer: {legacy_fixer}")

    def scan_for_temp_files(self):
        """Finds stuck __temp_ artifacts from interrupted renames."""
        for path in self.root.rglob("__temp_*.py"):
            if ".git" not in str(path) and "__pycache__" not in str(path):
                self.debris_found.append(path)
                print(f"[TEMP] Found interrupted rename artifact: {path.name}")

    def execute_cleanup(self):
        if not self.debris_found:
            print("\n✅ No debris found. System clean.")
            return 0

        print(f"\n⚠️  Found {len(self.debris_found)} items to remove.")

        if self.dry_run:
            print("[DRY RUN] Use --force to delete files.")
            return len(self.debris_found)

        deleted = 0
        for path in self.debris_found:
            try:
                os.remove(path)
                print(f"[DELETED] {path.name}")
                deleted += 1
            except Exception as e:
                print(f"[ERROR] Could not delete {path.name}: {e}")

        print(f"\n✅ Cleanup complete. Deleted {deleted} files.")
        return 0


if __name__ == "__main__":
    dry_run = "--force" not in sys.argv
    root = Path(__file__).parent.parent

    print("=" * 60)
    print("SOVEREIGNTY DEBRIS HUNTER")
    print("=" * 60)
    print(f"Mode: {'DRY RUN' if dry_run else 'EXECUTE'}")
    print(f"Root: {root}")
    print("=" * 60)

    hunter = DebrisHunter(root, dry_run=dry_run)
    hunter.scan_for_collisions()
    hunter.scan_for_known_redundancies()
    hunter.scan_for_temp_files()
    sys.exit(hunter.execute_cleanup())
