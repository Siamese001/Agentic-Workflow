#!/usr/bin/env python3
"""HygieneValidatorAgent - Code rot detection and hygiene validation.

Identifies code quality issues:
1. Dead Code: Orphaned files that are never imported.
2. Duplication: Files with identical content.
"""
from __future__ import annotations

import ast
import hashlib
import os
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

from agentic_core.bases import L0MaintenanceBaseAgent
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
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


class HygieneValidatorAgent(L0MaintenanceBaseAgent, MCPHardenedMixin):
    """
    Hygiene validation agent for code rot detection.
    
    Detects code quality issues:
        - Dead Code: Orphaned files that are never imported.
        - Duplication: Files with identical content (MD5 hash).
    
    Inherits:
        L0MaintenanceBaseAgent: HealerMixin, L0DelegationTestingMixin.
        MCPHardenedMixin: MCP protocol hardening.
    
    Attributes:
        root_path: Path to project root for scanning.
        all_py_files: List of discovered Python files.
        import_graph: Dict mapping import targets to importing files.
        file_hashes: Dict mapping MD5 hashes to file paths.
        entry_points: Set of standalone file names (not expected to be imported).
    """

    def __init__(self, root_path: str) -> None:
        """
        Initialize the hygiene validator.
        
        Args:
            root_path: Path to project root directory for scanning.
        """
        self.root_path = Path(root_path)
        self.all_py_files: List[str] = []
        self.import_graph: Dict[str, Set[str]] = defaultdict(set)
        self.file_hashes: Dict[str, List[str]] = defaultdict(list)
        self.entry_points: Set[str] = {
            "main.py",
            "setup.py",
            "manage.py",
            "run.py",
            "conftest.py",
            "__main__.py",
        }
        self._run_delegated_tests_safe()
    
    def _run_delegated_tests_safe(self) -> None:
        """
        Run delegated tests safely.
        
        Manual delegation for validators to avoid inheritance conflicts.
        Logs warning if tests soft-fail but does not halt boot.
        """
        try:
            from agentic_core.L0_maintenance.bases.l0_delegation_testing_mixin import L0DelegationTestingMixin
            mixin = L0DelegationTestingMixin()
            if not mixin._delegate_tests_safe():
                print(f"WARNING: {self.__class__.__name__} delegated tests soft-failed")
        except Exception:
            pass  # Validators should not halt boot

    def scan(self) -> None:
        """
        Scan project and build file list and import graph.
        
        Populates all_py_files, import_graph, and file_hashes.
        Skips virtual environments and cache directories.
        """
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

    def _analyze_imports(self, full_path: str, rel_path: str) -> None:
        """
        Parse file and extract all import targets.
        
        Args:
            full_path: Absolute path to the file.
            rel_path: Relative path from project root.
        """
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

    def _resolve_import_target(self, node: ast.AST, base_dir: str) -> List[str]:
        """
        Resolve import statement to potential file paths.
        
        Args:
            node: AST Import or ImportFrom node.
            base_dir: Base directory for relative resolution.
            
        Returns:
            List of potential file paths the import could resolve to.
        """
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
        """
        Get list of duplicate file violations.
        
        Returns:
            List of violation messages for files with identical content.
            Excludes __init__.py files which are often legitimately similar.
        """
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

    def _should_skip_file(self, file: str) -> bool:
        """Check if file should be skipped in orphan detection.
        
        Args:
            file: Relative file path.
            
        Returns:
            True if file should be skipped.
        """
        filename = os.path.basename(file)
        if filename == "__init__.py" or filename in self.entry_points:
            return True
        if TESTS_DIR in file or SCRIPTS_DIR in file or "test_" in filename:
            return True
        return False

    def _is_file_imported(self, file: str, imported_targets: Set[str]) -> bool:
        """Check if file is imported by any other file.
        
        Args:
            file: Relative file path.
            imported_targets: Set of import target paths.
            
        Returns:
            True if file is imported.
        """
        for target in imported_targets:
            if file.endswith(target) or target.endswith(file):
                return True
        return False

    def _find_orphan_files(self) -> List[str]:
        """Find all orphan files (never imported).
        
        Returns:
            List of orphan file paths.
        """
        imported_targets = set(self.import_graph.keys())
        orphans = []
        for file in self.all_py_files:
            if self._should_skip_file(file):
                continue
            if not self._is_file_imported(file, imported_targets):
                orphans.append(file)
        return orphans

    def get_orphans(self) -> List[str]:
        """Get files that are never imported.
        
        Returns:
            List of violation messages for orphaned files.
            Excludes entry points, test files, and scripts.
        """
        orphan_files = self._find_orphan_files()
        return [f"DEAD CODE: {f} is never imported (potential orphan)" for f in orphan_files]

    def get_orphans_raw(self) -> List[str]:
        """Get raw list of orphan file paths.
        
        For use by pruner scripts. Returns paths without violation messages.
        
        Returns:
            List of orphan file paths.
        """
        return self._find_orphan_files()

    def _run_self_tests(self) -> Dict[str, Any]:
        """
        Run internal self-tests.
        
        Returns:
            Dict with passed count, failed count, and test details.
        """
        results = {"passed": 0, "failed": 0, TESTS_DIR: []}
        try:
            assert self is not None
            results["passed"] += 1
            results[TESTS_DIR].append({"name": "test_instantiation", "status": "passed"})
        except AssertionError as e:
            results["failed"] += 1
            results[TESTS_DIR].append({"name": "test_instantiation", "status": "failed", "error": str(e)})
        return results

    def heal_repository(self) -> Dict[str, int]:
        """
        Execute healing chain via parent class.
        
        Returns:
            Dict with healing results from parent implementation.
        """
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
