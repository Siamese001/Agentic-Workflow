#!/usr/bin/env python3
"""
Automated script to clean up shim chains across the repository.

This script detects chains of backward compatibility shims with repetitive
_impl suffixes and cleans them up by:
1. Identifying shim chains
2. Finding the actual implementation at the end
3. Updating the root shim to import directly
4. Deleting intermediate shim files
import logging

logger = logging.getLogger(__name__)

"""

import os
import re
import ast
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Set

class ShimChainCleaner:
    """Detects and cleans up shim chains."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.shim_pattern = re.compile(r'^(.+)_impl(?:_impl)*\.py$')
        self.import_pattern = re.compile(r'from \.(\w+_impl(?:_impl)*) import \*')
        self.deleted_files = []
        self.updated_files = []
        self.errors = []

    def is_shim_file(self, file_path: Path) -> bool:
        """Check if a file is likely a shim based on size and content."""
        if not file_path.is_file():
            return False

        # Check file size (shims are typically small)
        if file_path.stat().st_size > 2000:  # Larger than 2KB is likely real code
            return False

        try:
            content = file_path.read_text(encoding='utf-8')

            # Check for shim signature
            if "Backward compatibility shim" in content and "re-export all components" in content:
                return True

            # Check for simple import pattern
            if self.import_pattern.search(content):
                lines = content.strip().split('\n')
                # If file has mostly comments and one import, it's a shim
                code_lines = [l for l in lines if l.strip() and not l.strip().startswith('#')]
                if len(code_lines) <= 3:
                    return True

        except Exception:
            pass

        return False

    def find_shim_chains(self, directory: Path) -> List[List[Path]]:
        """Find all shim chains in a directory."""
        chains = []
        processed = set()

        # Get all Python files
        py_files = list(directory.rglob("*.py"))

        # Group files by base name
        base_groups = {}
        for file_path in py_files:
            if file_path.name == "__init__.py":
                continue

            # Extract base name (remove _impl suffixes)
            match = re.match(r'^(.+?)(?:_impl(?:_impl)*)?\.py$', file_path.name)
            if match:
                base = match.group(1)
                if base not in base_groups:
                    base_groups[base] = []
                base_groups[base].append(file_path)

        # Find chains in each group
        for base, files in base_groups.items():
            if len(files) > 1:
                # Sort by number of _impl suffixes
                files.sort(key=lambda f: f.name.count('_impl'))

                # Check if it's a chain (all are shims except possibly the last)
                if all(self.is_shim_file(f) for f in files[:-1]):
                    chains.append(files)
                    processed.update(files)

        return chains

    def trace_chain_to_implementation(self, chain: List[Path]) -> Optional[Path]:
        """Follow the chain to find the actual implementation."""
        current = chain[0]
        visited = set()

        while current and current not in visited:
            visited.add(current)

            try:
                content = current.read_text(encoding='utf-8')
                match = self.import_pattern.search(content)

                if match:
                    imported_name = match.group(1) + '.py'
                    next_file = current.parent / imported_name

                    if next_file.exists():
                        # Check if this is the real implementation
                        if not self.is_shim_file(next_file):
                            return next_file
                        current = next_file
                        continue
                    else:
                        # Try to find the file in subdirectories
                        for candidate in current.parent.rglob(imported_name):
                            if not self.is_shim_file(candidate):
                                return candidate
                        current = current.parent / imported_name
                else:
                    break

            except Exception as e:
                self.errors.append(f"Error reading {current}: {e}")
                break

        return None

    def check_external_imports(self, file_path: Path) -> bool:
        """Check if any files outside the directory import this file."""
        file_name = file_path.stem
        parent_dir = file_path.parent

        # Search for imports of this file
        pattern = re.compile(rf'from [^.]*(?:{file_name})|import [^.]*(?:{file_name})')

        for py_file in self.repo_root.rglob("*.py"):
            # Skip files in the same directory
            if py_file.parent == parent_dir:
                continue

            try:
                content = py_file.read_text(encoding='utf-8')
                if pattern.search(content):
                    return True
            except Exception:
                pass

        return False

    def clean_chain(self, chain: List[Path]) -> bool:
        """Clean a single shim chain."""
        if len(chain) < 2:
            return False

        # Find the actual implementation
        implementation = self.trace_chain_to_implementation(chain)
        if not implementation:
            self.errors.append(f"Could not find implementation for chain starting with {chain[0]}")
            return False

        # Update the root shim to import directly
        root_shim = chain[0]
        try:
            content = root_shim.read_text(encoding='utf-8')

            # Replace the import
            new_import = f"from .{implementation.stem} import *"
            content = re.sub(r'from \.\w+_impl(?:_impl)* import \*', new_import, content)

            # Write back
            root_shim.write_text(content, encoding='utf-8')
            self.updated_files.append(root_shim)

        except Exception as e:
            self.errors.append(f"Error updating {root_shim}: {e}")
            return False

        # Delete intermediate shims
        for shim in chain[1:]:
            # Check if anything external imports this
            if not self.check_external_imports(shim):
                try:
                    shim.unlink()
                    self.deleted_files.append(shim)
                except Exception as e:
                    self.errors.append(f"Error deleting {shim}: {e}")
            else:
                self.errors.append(f"Skipping {shim} - imported externally")

        return True

    def clean_directory(self, directory: Path) -> Dict[str, int]:
        """Clean all shim chains in a directory."""
        chains = self.find_shim_chains(directory)

        results = {
            "chains_found": len(chains),
            "chains_cleaned": 0,
            "files_deleted": 0,
            "files_updated": 0,
            "errors": 0
        }

        for chain in chains:
            if self.clean_chain(chain):
                results["chains_cleaned"] += 1

        results["files_deleted"] = len(self.deleted_files)
        results["files_updated"] = len(self.updated_files)
        results["errors"] = len(self.errors)

        return results

    def clean_all(self, exclude_dirs: Optional[Set[str]] = None) -> Dict[str, Dict[str, int]]:
        """Clean all directories in the repository."""
        if exclude_dirs is None:
            exclude_dirs = {'.git', '__pycache__', '.pytest_cache', 'node_modules'}

        results = {}

        for item in self.repo_root.iterdir():
            if item.is_dir() and item.name not in exclude_dirs:
                logger.info(f"\nCleaning directory: {item.name}")
                results[item.name] = self.clean_directory(item)

                # Reset counters for next directory
                self.deleted_files = []
                self.updated_files = []
                self.errors = []

        return results

def main():
    """Main entry point."""
    repo_root = Path(__file__).parent.parent
    cleaner = ShimChainCleaner(repo_root)

    logger.info("Scanning for shim chains...")
    logger.info("=" * 60)

    # Get directories to check
    dirs_to_check = []
    for item in repo_root.iterdir():
        if item.is_dir() and item.name not in {'.git', '__pycache__', '.pytest_cache', 'node_modules'}:
            dirs_to_check.append(item.name)

    logger.info(f"Found {len(dirs_to_check)} directories to check")

    # Clean all directories
    results = cleaner.clean_all()

    # Print summary
    logger.info("\n" + "=" * 60)
    logger.info("CLEANUP SUMMARY")
    logger.info("=" * 60)

    total_chains = 0
    total_cleaned = 0
    total_deleted = 0
    total_updated = 0
    total_errors = 0

    for dir_name, result in results.items():
        if result["chains_found"] > 0:
            logger.info(f"\n{dir_name}:")
            logger.info(f"  Chains found: {result['chains_found']}")
            logger.info(f"  Chains cleaned: {result['chains_cleaned']}")
            logger.info(f"  Files deleted: {result['files_deleted']}")
            logger.info(f"  Files updated: {result['files_updated']}")
            if result['errors'] > 0:
                logger.info(f"  Errors: {result['errors']}")

            total_chains += result['chains_found']
            total_cleaned += result['chains_cleaned']
            total_deleted += result['files_deleted']
            total_updated += result['files_updated']
            total_errors += result['errors']

    logger.info("\n" + "=" * 60)
    logger.info("TOTALS:")
    logger.info(f"  Total chains found: {total_chains}")
    logger.info(f"  Total chains cleaned: {total_cleaned}")
    logger.info(f"  Total files deleted: {total_deleted}")
    logger.info(f"  Total files updated: {total_updated}")
    logger.info(f"  Total errors: {total_errors}")

    if cleaner.errors:
        logger.info("\nERRORS:")
        for error in cleaner.errors:
            logger.info(f"  - {error}")

if __name__ == "__main__":
    main()
