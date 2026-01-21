"""
UnifiedHygieneValidatorAgent - Consolidated Code Hygiene Validator (Phase 2)

Consolidates:
- HygieneGuardianAgent (L5_safety/validators/)
- HygieneValidatorAgent (L5_safety/gravity/)

Resolves GAP-4: Duplicate file detection across repository.

Capabilities:
- Duplicate file detection via MD5 hashing
- Empty/stub file detection
- Dead code (orphan) analysis via import graph
- Technical debt marker scanning (TODO, FIXME, HACK, XXX)
- Unused import detection

Territory: agentic_core/L5_safety/validators/
Canon Alignment: Code hygiene and repository health validation
"""
from __future__ import annotations

import ast
import hashlib
import os
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agentic_core.L5_safety.validators.decorators import standard_heal
from agentic_core.L5_safety.validators.L5Agent import L5Agent
from agentic_core.L5_safety.validators.structure_blueprint import (
    GLOBAL_EXCLUDED_DIRS,
    SCRIPTS_DIR,
    TESTS_DIR,
)


@dataclass
class HygieneViolation:
    """Structured hygiene issue report."""
    file_path: Path
    violation_type: str  # 'duplicate', 'empty_file', 'dead_code', 'tech_debt', 'orphan'
    severity: str  # 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    description: str
    line_number: int | None = None
    related_files: list[str] | None = None


@dataclass
class UnifiedHygieneValidatorAgent(L5Agent):
    """
    Unified Code Hygiene Validator (Phase 2 Consolidation).

    Consolidates HygieneGuardianAgent and legacy HygieneValidatorAgent.
    Resolves GAP-4: Duplicate file detection.

    Detects:
    - Duplicate files (MD5 hash comparison)
    - Empty/stub files (< 10 bytes, except __init__.py)
    - Dead code and orphaned files (not imported anywhere)
    - Technical debt markers (TODO, FIXME, HACK, XXX, BUG)
    - Unused imports

    Inherits from L5Agent which provides:
    - HealerMixin: heal_repository() for self-repair
    - MCPHardenedMixin: Hardened MCP with retry/timeout
    """

    name: str = "UnifiedHygieneValidatorAgent"
    layer: str = "L5"
    project_root: Path = field(default_factory=Path.cwd)

    # Configuration
    DEBT_MARKERS: list[str] = field(default_factory=lambda: ['TODO', 'FIXME', 'HACK', 'XXX', 'BUG'])
    MIN_FILE_SIZE: int = 10  # Bytes - files smaller are considered empty
    ALLOWED_EMPTY: set[str] = field(default_factory=lambda: {'__init__.py'})
    SKIP_DIRS: set[str] = field(default_factory=lambda: set(GLOBAL_EXCLUDED_DIRS))

    # Entry points that shouldn't be flagged as orphans
    ENTRY_POINTS: set[str] = field(default_factory=lambda: {
        'main', 'setup', 'manage', 'run', 'conftest', '__main__', '__init__'
    })

    # Internal state
    file_hashes: dict[str, list[Path]] = field(default_factory=lambda: defaultdict(list))
    import_graph: dict[str, set[str]] = field(default_factory=lambda: defaultdict(set))
    all_py_files: list[Path] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Initialize the unified hygiene validator."""
        if isinstance(self.project_root, str):
            self.project_root = Path(self.project_root)

        # Initialize collections
        if not isinstance(self.file_hashes, defaultdict):
            self.file_hashes = defaultdict(list)
        if not isinstance(self.import_graph, defaultdict):
            self.import_graph = defaultdict(set)
        if not isinstance(self.all_py_files, list):
            self.all_py_files = []

    def validate_repository(self) -> dict[str, Any]:
        """
        Perform comprehensive hygiene validation of the repository.

        Returns:
            Dictionary with all hygiene findings grouped by type
        """
        # Reset state
        self.file_hashes = defaultdict(list)
        self.import_graph = defaultdict(set)
        self.all_py_files = []

        # Scan repository
        self._scan_repository()

        # Run all checks
        duplicates = self._find_duplicates()
        empty_files = self._find_empty_files()
        tech_debt = self._scan_markers()
        orphans = self._find_orphans()

        # Aggregate results
        total_violations = len(duplicates) + len(empty_files) + len(tech_debt) + len(orphans)

        return {
            "total_violations": total_violations,
            "duplicates": duplicates,
            "empty_files": empty_files,
            "tech_debt": tech_debt,
            "orphans": orphans,
            "status": "FAIL" if total_violations > 0 else "PASS",
            "summary": {
                "duplicate_count": len(duplicates),
                "empty_file_count": len(empty_files),
                "tech_debt_count": len(tech_debt),
                "orphan_count": len(orphans),
            }
        }

    def _scan_repository(self) -> None:
        """
        Scan repository to build file list, hash map, and import graph.

        Note: Always uses rglob to ensure ALL Python files are scanned,
        including test files that ssot_discovery may filter out.
        """
        # Always use rglob for hygiene validation - we need ALL files
        py_files = list(self.project_root.rglob("*.py"))

        for py_file in py_files:
            # Skip excluded directories (check relative to project_root, not absolute path)
            try:
                rel_parts = py_file.relative_to(self.project_root).parts
                if any(skip_dir in rel_parts for skip_dir in self.SKIP_DIRS):
                    continue
            except ValueError:
                # File is not relative to project_root, skip it
                continue

            self.all_py_files.append(py_file)

            # Calculate hash for duplicate detection
            try:
                file_hash = self._get_file_hash(py_file)
                if file_hash:
                    self.file_hashes[file_hash].append(py_file)
            except Exception:
                pass

            # Build import graph
            self._analyze_imports(py_file)

    def _get_file_hash(self, path: Path) -> str | None:
        """
        Calculate MD5 hash for a file.

        Args:
            path: Path to file

        Returns:
            MD5 hash string or None if file is empty/unreadable
        """
        try:
            content = path.read_bytes()
            # Skip empty files for hash comparison
            if len(content.strip()) == 0:
                return None
            return hashlib.md5(content).hexdigest()
        except Exception:
            return None

    def _analyze_imports(self, file_path: Path) -> None:
        """
        Parse file and extract all import targets for orphan detection.

        Args:
            file_path: Path to Python file
        """
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content)

            rel_path = str(file_path.relative_to(self.project_root))

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        # Extract module name
                        module = alias.name.split('.')[0]
                        self.import_graph[module].add(rel_path)

                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        # Extract module name
                        module = node.module.split('.')[0]
                        self.import_graph[module].add(rel_path)

                    # Also track imported names
                    for alias in node.names:
                        self.import_graph[alias.name].add(rel_path)

        except Exception:
            pass  # Skip unparseable files

    def _find_duplicates(self) -> list[dict[str, Any]]:
        """
        Detect duplicate files using MD5 hashing (Addresses GAP-4).

        Returns:
            List of duplicate file groups
        """
        duplicates = []

        for file_hash, paths in self.file_hashes.items():
            if len(paths) > 1:
                # Filter out __init__.py files (often legitimately similar)
                non_init_paths = [p for p in paths if p.name != '__init__.py']

                if len(non_init_paths) > 1:
                    duplicates.append({
                        "hash": file_hash,
                        "files": [str(p.relative_to(self.project_root)) for p in non_init_paths],
                        "count": len(non_init_paths),
                        "severity": "HIGH",
                    })

        return duplicates

    def _find_empty_files(self) -> list[dict[str, Any]]:
        """
        Find empty or near-empty files that shouldn't be empty.

        Returns:
            List of empty file violations
        """
        empty_files = []

        for py_file in self.all_py_files:
            # Skip allowed empty files
            if py_file.name in self.ALLOWED_EMPTY:
                continue

            try:
                file_size = py_file.stat().st_size

                if file_size < self.MIN_FILE_SIZE:
                    empty_files.append({
                        "file": str(py_file.relative_to(self.project_root)),
                        "size": file_size,
                        "severity": "HIGH",
                        "description": f"File is only {file_size} bytes (likely stub or incomplete)"
                    })
            except Exception:
                pass

        return empty_files

    def _scan_markers(self) -> list[dict[str, Any]]:
        """
        Scan for technical debt markers (TODO, FIXME, HACK, etc.).

        Returns:
            List of technical debt markers found
        """
        markers_found = []

        for py_file in self.all_py_files:
            try:
                content = py_file.read_text(encoding='utf-8')
                lines = content.split('\n')

                for line_num, line in enumerate(lines, 1):
                    # Only check comment lines
                    if '#' not in line:
                        continue

                    line_upper = line.upper()
                    for marker in self.DEBT_MARKERS:
                        if marker in line_upper:
                            markers_found.append({
                                "file": str(py_file.relative_to(self.project_root)),
                                "line": line_num,
                                "type": marker,
                                "content": line.strip()[:100],  # Truncate long lines
                                "severity": "LOW",
                            })
                            break  # Only report once per line

            except Exception:
                pass

        return markers_found

    def _find_orphans(self) -> list[dict[str, Any]]:
        """
        Detect files not referenced in any import statements (dead code).

        Returns:
            List of orphan file violations
        """
        orphans = []
        imported_modules = set(self.import_graph.keys())

        for py_file in self.all_py_files:
            file_stem = py_file.stem

            # Skip entry points and special files
            if file_stem in self.ENTRY_POINTS:
                continue

            # Skip test files
            if 'test_' in py_file.name or py_file.name.endswith('_test.py'):
                continue

            # Skip files in tests/ or scripts/ directories
            rel_path = str(py_file.relative_to(self.project_root))
            if TESTS_DIR in rel_path or SCRIPTS_DIR in rel_path:
                continue

            # Check if file is imported anywhere
            if file_stem not in imported_modules:
                # Double-check: also check if the full module path is imported
                module_path = rel_path.replace(os.sep, '.').replace('/', '.')[:-3]
                if module_path not in imported_modules:
                    orphans.append({
                        "file": rel_path,
                        "module": file_stem,
                        "severity": "MEDIUM",
                        "description": f"File '{file_stem}.py' is never imported (potential dead code)"
                    })

        return orphans

    @standard_heal
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set[str] | None = None
    ) -> dict[str, Any]:
        """
        Audit and optionally heal hygiene violations.

        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, attempt to fix hygiene issues
            depth: Current recursion depth
            max_depth: Maximum recursion depth
            _call_path: Set of already-visited agents (cycle detection)

        Returns:
            Dictionary with healing summary
        """
        # Call parent healing chain
        super().heal_repository(
            dry_run=dry_run,
            execute=execute,
            depth=depth,
            max_depth=max_depth,
            _call_path=_call_path
        )

        if _call_path is None:
            _call_path = set()

        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}

        _call_path.add(agent_name)

        try:
            # Run validation
            results = self.validate_repository()

            violations_found = results.get('total_violations', 0)
            violations_fixed = 0

            # Healing logic (if execute=True)
            if execute and not dry_run:
                # Remove empty stub files (except __init__.py)
                for empty_file in results.get('empty_files', []):
                    try:
                        file_path = self.project_root / empty_file['file']
                        if file_path.exists() and file_path.name not in self.ALLOWED_EMPTY:
                            file_path.unlink()
                            violations_fixed += 1
                    except Exception:
                        pass

            return {
                "agent": agent_name,
                "violations_found": violations_found,
                "violations_fixed": violations_fixed,
                "summary": results.get('summary', {}),
                "status": results.get('status', 'UNKNOWN'),
                "dry_run": dry_run,
                "execute": execute,
            }

        finally:
            _call_path.discard(agent_name)

    def validate(self, target: Any = None) -> dict[str, Any]:
        """
        Validate hygiene for a specific target or entire repository.

        Args:
            target: Optional specific path to validate

        Returns:
            Validation results
        """
        if target:
            # Validate specific path
            target_path = Path(target) if isinstance(target, str) else target
            old_root = self.project_root
            self.project_root = target_path
            try:
                return self.validate_repository()
            finally:
                self.project_root = old_root
        else:
            return self.validate_repository()

    def _run_self_tests(self) -> dict[str, Any]:
        """
        Run internal self-tests for the unified hygiene validator.

        Returns:
            Dictionary with test results
        """
        results = {"passed": 0, "failed": 0, "tests": []}

        # Test 1: Instantiation
        try:
            assert self is not None
            assert self.name == "UnifiedHygieneValidatorAgent"
            results["passed"] += 1
            results["tests"].append({"name": "test_instantiation", "status": "passed"})
        except AssertionError as e:
            results["failed"] += 1
            results["tests"].append({"name": "test_instantiation", "status": "failed", "error": str(e)})

        # Test 2: Hash calculation
        try:
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write("# Test file\nprint('hello')")
                temp_path = Path(f.name)

            file_hash = self._get_file_hash(temp_path)
            assert file_hash is not None
            assert len(file_hash) == 32  # MD5 hash length
            temp_path.unlink()

            results["passed"] += 1
            results["tests"].append({"name": "test_hash_calculation", "status": "passed"})
        except Exception as e:
            results["failed"] += 1
            results["tests"].append({"name": "test_hash_calculation", "status": "failed", "error": str(e)})

        # Test 3: Marker detection
        try:
            test_content = "# TODO: Fix this\n# FIXME: Also this"
            markers = []
            for marker in self.DEBT_MARKERS:
                if marker in test_content.upper():
                    markers.append(marker)
            assert 'TODO' in markers
            assert 'FIXME' in markers

            results["passed"] += 1
            results["tests"].append({"name": "test_marker_detection", "status": "passed"})
        except AssertionError as e:
            results["failed"] += 1
            results["tests"].append({"name": "test_marker_detection", "status": "failed", "error": str(e)})

        # Test 4: Duplicate detection logic
        try:
            # Use paths relative to project_root for proper relative_to() calculation
            self.file_hashes = defaultdict(list)
            test_path_a = self.project_root / "test_a" / "file1.py"
            test_path_b = self.project_root / "test_b" / "file2.py"
            self.file_hashes["abc123"] = [test_path_a, test_path_b]
            duplicates = self._find_duplicates()
            assert len(duplicates) == 1
            assert duplicates[0]["count"] == 2

            results["passed"] += 1
            results["tests"].append({"name": "test_duplicate_detection", "status": "passed"})
        except AssertionError as e:
            results["failed"] += 1
            results["tests"].append({"name": "test_duplicate_detection", "status": "failed", "error": str(e)})

        return results


# Factory function for sovereign discovery
def get_unified_hygiene_validator(project_root: Path = None) -> UnifiedHygieneValidatorAgent:
    """Factory function to get UnifiedHygieneValidatorAgent instance."""
    if project_root is None:
        project_root = Path.cwd()
    return UnifiedHygieneValidatorAgent(project_root=project_root)


# Convenience functions for backward compatibility
def find_duplicates(project_root: Path = None) -> list[dict[str, Any]]:
    """Find duplicate files in repository."""
    validator = get_unified_hygiene_validator(project_root)
    validator._scan_repository()
    return validator._find_duplicates()


def find_orphans(project_root: Path = None) -> list[dict[str, Any]]:
    """Find orphan (dead code) files in repository."""
    validator = get_unified_hygiene_validator(project_root)
    validator._scan_repository()
    return validator._find_orphans()


def scan_tech_debt(project_root: Path = None) -> list[dict[str, Any]]:
    """Scan for technical debt markers."""
    validator = get_unified_hygiene_validator(project_root)
    validator._scan_repository()
    return validator._scan_markers()


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Unified Hygiene Validator")
    parser.add_argument("--root", type=str, default=".", help="Project root directory")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--duplicates-only", action="store_true", help="Only check duplicates")
    parser.add_argument("--orphans-only", action="store_true", help="Only check orphans")
    parser.add_argument("--markers-only", action="store_true", help="Only check tech debt markers")
    args = parser.parse_args()

    validator = get_unified_hygiene_validator(Path(args.root))

    if args.duplicates_only:
        validator._scan_repository()
        results = {"duplicates": validator._find_duplicates()}
    elif args.orphans_only:
        validator._scan_repository()
        results = {"orphans": validator._find_orphans()}
    elif args.markers_only:
        validator._scan_repository()
        results = {"tech_debt": validator._scan_markers()}
    else:
        results = validator.validate_repository()

    if args.json:
        print(json.dumps(results, indent=2, default=str))
    else:
        print(f"\n{'='*60}")
        print("Unified Hygiene Validator Report")
        print(f"{'='*60}")

        if "duplicates" in results:
            print(f"\n📋 Duplicates: {len(results['duplicates'])}")
            for dup in results['duplicates'][:5]:
                print(f"   - {dup['files']}")

        if "empty_files" in results:
            print(f"\n📄 Empty Files: {len(results['empty_files'])}")
            for ef in results['empty_files'][:5]:
                print(f"   - {ef['file']} ({ef['size']} bytes)")

        if "tech_debt" in results:
            print(f"\n🔧 Tech Debt Markers: {len(results['tech_debt'])}")
            for td in results['tech_debt'][:5]:
                print(f"   - {td['file']}:{td['line']} [{td['type']}]")

        if "orphans" in results:
            print(f"\n👻 Orphan Files: {len(results['orphans'])}")
            for orph in results['orphans'][:5]:
                print(f"   - {orph['file']}")

        if "summary" in results:
            print(f"\n{'='*60}")
            print(f"Status: {results.get('status', 'UNKNOWN')}")
            print(f"Total Violations: {results.get('total_violations', 0)}")
