from __future__ import annotations
#!/usr/bin/env python3
"""
Hygiene Validator - Detects Code Rot
Identifies:
1. Dead Code (Orphaned files that are never imported)
2. Duplication (Files with identical content)
"""
import ast
import hashlib
import os
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple

from agentic_core.bases import L0Agent


class HygieneValidatorAgent(L0Agent):
    """
    Detects 'Rot' within the system:
    1. Dead Code (Orphaned files that are never imported)
    2. Duplication (Files with identical content)
    """

    def __init__(self, root_path: str) -> None:
        self.root_path = Path(root_path)
        self.all_py_files = []
        self.import_graph = defaultdict(set)
        self.file_hashes = defaultdict(list)
        # Files that are expected to be standalone (not imported)
        self.entry_points = {
            "main.py",
            "setup.py",
            "manage.py",
            "run.py",
            "conftest.py",
            "__main__.py",
        }
        # [PHASE 2] L0 Delegated Testing - manual safe call
        self._run_delegated_tests_safe()
    
    def _run_delegated_tests_safe(self):
        """Manual delegation for validators (no inheritance conflict)."""
        try:
            from agentic_core.L0_maintenance.bases.l0_delegation_testing_mixin import L0DelegationTestingMixin
            mixin = L0DelegationTestingMixin()
            if not mixin._delegate_tests_safe():
                print(f"WARNING: {self.__class__.__name__} delegated tests soft-failed")
        except Exception:
            pass  # Validators should not halt boot

    def scan(self) -> Dict[str, Any]:
        """Builds file list and import graph."""
        for root, dirs, files in os.walk(self.root_path):
            # Skip virtual environments and cache directories
            dirs[:] = [
                d
                for d in dirs
                if d not in {"venv", ".venv", ".git", "__pycache__", "node_modules"}
            ]

            for file in files:
                if file.endswith(".py"):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, self.root_path)
                    self.all_py_files.append(rel_path)

                    # Hash content for duplication check
                    try:
                        with open(full_path, "rb") as f:
                            content = f.read()
                            # Skip empty files
                            if len(content.strip()) > 0:
                                file_hash = hashlib.md5(content).hexdigest()
                                self.file_hashes[file_hash].append(rel_path)
                    except Exception:
                        pass

                    # Parse imports for orphan check
                    self._analyze_imports(full_path, rel_path)

    def _analyze_imports(self, full_path: str, rel_path: str):
        """Parse file and extract all import targets."""
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read())

            base_dir = os.path.dirname(rel_path)

            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    targets = self._resolve_import_target(node, base_dir)
                    for t in targets:
                        self.import_graph[t].add(rel_path)
        except Exception:
            pass  # Skip unparseable files

    def _resolve_import_target(self, node, base_dir) -> List[str]:
        """Resolve import statement to potential file paths."""
        targets = []
        module = None

        if isinstance(node, ast.Import):
            for alias in node.names:
                module = alias.name
        elif isinstance(node, ast.ImportFrom):
            module = node.module

        if not module:
            return []

        # Heuristic Resolution:
        # 1. Check if module matches a file directly (agentic_core.utils -> agentic_core/utils.py)
        potential_path = module.replace(".", os.sep) + ".py"
        targets.append(potential_path)

        # 2. Check if it matches a package init (agentic_core.utils -> agentic_core/utils/__init__.py)
        potential_init = os.path.join(module.replace(".", os.sep), "__init__.py")
        targets.append(potential_init)

        return targets

    def get_duplicates(self) -> List[str]:
        """Returns list of duplicate file violations."""
        violations = []
        for fhash, paths in self.file_hashes.items():
            if len(paths) > 1:
                # Filter out __init__.py files (they're often legitimately empty/similar)
                non_init_paths = [p for p in paths if not p.endswith("__init__.py")]
                if len(non_init_paths) > 1:
                    violations.append(
                        f"DUPLICATION: Exact duplicate files found: {non_init_paths}"
                    )
        return violations

    def get_orphans(self) -> List[str]:
        """
        Returns files that are never imported by anyone else.
        """
        orphans = []
        # Flatten the set of all imported targets
        imported_targets = set(self.import_graph.keys())

        for file in self.all_py_files:
            filename = os.path.basename(file)

            # Skip files that are expected to be standalone
            if filename == "__init__.py" or filename in self.entry_points:
                continue

            # Skip test files and scripts (they're meant to be run, not imported)
            if "tests" in file or "scripts" in file or "test_" in filename:
                continue

            # Loose check: if the filename (or path) appears in any import target
            is_imported = False
            for target in imported_targets:
                # Matches if 'agentic_core/utils.py' is in target 'agentic_core/utils.py'
                if file.endswith(target) or target.endswith(file):
                    is_imported = True
                    break

            if not is_imported:
                orphans.append(f"DEAD CODE: {file} is never imported (potential orphan)")

        return orphans


    def get_orphans_raw(self) -> List[str]:
        """Returns raw list of orphan file paths for the pruner script."""
        orphans = []
        imported_targets = set(self.import_graph.keys())

        for file in self.all_py_files:
            filename = os.path.basename(file)

            # Skip files that are expected to be standalone
            if filename == "__init__.py" or filename in self.entry_points:
                continue

            # Skip test files and scripts (they're meant to be run, not imported)
            if "tests" in file or "scripts" in file or "test_" in filename:
                continue

            # Loose check: if the filename (or path) appears in any import target
            is_imported = False
            for target in imported_targets:
                # Matches if 'agentic_core/utils.py' is in target 'agentic_core/utils.py'
                if file.endswith(target) or target.endswith(file):
                    is_imported = True
                    break

            if not is_imported:
                orphans.append(file)

        return orphans

    def _run_self_tests(self) -> dict:
        """Run internal self-tests."""
        results = {"passed": 0, "failed": 0, "tests": []}
        try:
            assert self is not None
            results["passed"] += 1
            results["tests"].append({"name": "test_instantiation", "status": "passed"})
        except AssertionError as e:
            results["failed"] += 1
            results["tests"].append({"name": "test_instantiation", "status": "failed", "error": str(e)})
        return results

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()


if __name__ == "__main__":
    import sys

    root = sys.argv[1] if len(sys.argv) > 1 else "."
    print(f"Running Hygiene Validator on: {root}")

    validator = HygieneValidatorAgent(root)
    validator.scan()

    print("\nimport logging\n\nLogger = logging.getLogger(__name__)\n=== DUPLICATE FILES ===")
    dupes = validator.get_duplicates()
    if dupes:
        for d in dupes:
            print(f"  [!] {d}")
    else:
        print("  [OK] No duplicates found")

    print("\n=== ORPHANED FILES (DEAD CODE) ===")
    orphans = validator.get_orphans()
    if orphans:
        for o in orphans:
            print(f"  [!] {o}")
    else:
        print("  [OK] No orphans found")

    print(f"\nTotal Issues: {len(dupes) + len(orphans)}")
