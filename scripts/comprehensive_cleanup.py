#!/usr/bin/env python3
"""
Comprehensive cleanup of runaway refactoring across the entire repository.

This script:
1. Identifies shim chains (files that only re-export)
2. Preserves legitimate split implementations
3. Cleans up directory by directory
4. Provides detailed reporting
import logging

logger = logging.getLogger(__name__)

"""

import os
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional

class RepositoryCleaner:
    """Cleans up runaway refactoring artifacts."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.stats = {
            "directories_processed": 0,
            "shim_chains_found": 0,
            "shim_files_deleted": 0,
            "files_updated": 0,
            "errors": []
        }

    def is_shim_file(self, file_path: Path) -> bool:
        """Determine if a file is a shim (only re-exports)."""
        if not file_path.exists():
            return False

        # Check file size
        if file_path.stat().st_size > 2000:
            return False

        try:
            content = file_path.read_text(encoding='utf-8')

            # Check for explicit shim signature
            if "Backward compatibility shim" in content:
                return True

            # Check for simple re-export pattern
            lines = [l.strip() for l in content.split('\n') if l.strip()]

            # If file has mostly comments and one import, it's likely a shim
            code_lines = [l for l in lines if not l.startswith('#') and not l.startswith('"""') and not l.startswith("'''")]

            if len(code_lines) <= 2:
                # Check if it's just importing from another file
                for line in code_lines:
                    if line.startswith('from .') and 'import *' in line:
                        return True

        except Exception as e:
            self.stats["errors"].append(f"Error reading {file_path}: {e}")

        return False

    def has_real_implementation(self, file_path: Path) -> bool:
        """Check if file contains actual implementation code."""
        try:
            content = file_path.read_text(encoding='utf-8')

            # Look for implementation indicators
            impl_patterns = [
                r'def\s+\w+\s*\(',      # Functions
                r'class\s+\w+\s*:',     # Classes
                r'@\w+',                 # Decorators
                r'=\s*lambda',           # Lambdas
                r'if\s+__name__',        # Main blocks
            ]

            for pattern in impl_patterns:
                if re.search(pattern, content):
                    return True

        except Exception:
            pass

        return False

    def find_shim_chains(self, directory: Path) -> Dict[str, List[Path]]:
        """Find shim chains in a directory."""
        chains = {}
        processed = set()

        # Get all Python files
        py_files = [f for f in directory.rglob("*.py") if f.name != "__init__.py"]

        # Group by base name pattern
        base_groups = {}
        for file_path in py_files:
            # Match patterns like: name_impl.py, name_impl_impl.py, etc.
            match = re.match(r'^(.+?)(?:_impl(?:_impl)*)?\.py$', file_path.name)
            if match:
                base = match.group(1)
                if base not in base_groups:
                    base_groups[base] = []
                base_groups[base].append(file_path)

        # Identify chains
        for base, files in base_groups.items():
            if len(files) > 1:
                # Sort by number of _impl suffixes
                files.sort(key=lambda f: f.name.count('_impl'))

                # Check if this is a shim chain
                # All but possibly the last should be shims
                all_but_last_are_shims = all(self.is_shim_file(f) for f in files[:-1])

                if all_but_last_are_shims:
                    chains[base] = files
                    processed.update(files)

        return chains

    def clean_shim_chain(self, chain: List[Path]) -> bool:
        """Clean a single shim chain."""
        if len(chain) < 2:
            return False

        # Find the real implementation (last non-shim file)
        implementation = None
        for file_path in reversed(chain):
            if self.has_real_implementation(file_path):
                implementation = file_path
                break

        if not implementation:
            # If no clear implementation, use the last file
            implementation = chain[-1]

        # Update the root shim to import directly
        root_shim = chain[0]
        try:
            content = root_shim.read_text(encoding='utf-8')

            # Replace the import
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('from .') and 'import *' in line:
                    lines[i] = f"from .{implementation.stem} import *"
                    break

            root_shim.write_text('\n'.join(lines), encoding='utf-8')
            self.stats["files_updated"] += 1

        except Exception as e:
            self.stats["errors"].append(f"Error updating {root_shim}: {e}")
            return False

        # Delete intermediate shims
        for shim in chain[1:]:
            if shim != implementation:  # Don't delete the real implementation
                try:
                    shim.unlink()
                    self.stats["shim_files_deleted"] += 1
                except Exception as e:
                    self.stats["errors"].append(f"Error deleting {shim}: {e}")

        return True

    def clean_directory(self, directory: Path) -> Dict[str, int]:
        """Clean all shim chains in a directory."""
        logger.info(f"\nCleaning {directory.name}...")

        chains = self.find_shim_chains(directory)
        dir_stats = {
            "chains_found": len(chains),
            "chains_cleaned": 0,
            "files_deleted": 0,
            "files_updated": 0
        }

        if chains:
            logger.info(f"  Found {len(chains)} shim chains")

            for base, chain in chains.items():
                logger.info(f"    - {base}: {len(chain)} files")
                if self.clean_shim_chain(chain):
                    dir_stats["chains_cleaned"] += 1

        else:
            logger.info(f"  No shim chains found")

        # Update global stats
        self.stats["shim_chains_found"] += dir_stats["chains_found"]
        self.stats["directories_processed"] += 1

        return dir_stats

    def clean_all(self, exclude_dirs: Optional[Set[str]] = None):
        """Clean the entire repository."""
        if exclude_dirs is None:
            exclude_dirs = {
                '.git', '__pycache__', '.pytest_cache',
                'node_modules', '.venv', '.vscode',
                '.workflow_state', 'output', 'data'
            }

        logger.info("=" * 80)
        logger.info("COMPREHENSIVE REPOSITORY CLEANUP")
        logger.info("Cleaning runaway refactoring artifacts...")
        logger.info("=" * 80)

        # Process all top-level directories
        total_results = {}

        for item in self.repo_root.iterdir():
            if item.is_dir() and item.name not in exclude_dirs:
                result = self.clean_directory(item)
                total_results[item.name] = result

        # Print summary
        self.print_summary(total_results)

        return total_results

    def print_summary(self, results: Dict[str, Dict[str, int]]):
        """Print cleanup summary."""
        logger.info("\n" + "=" * 80)
        logger.info("CLEANUP SUMMARY")
        logger.info("=" * 80)

        total_chains = sum(r["chains_found"] for r in results.values())
        total_cleaned = sum(r["chains_cleaned"] for r in results.values())

        logger.info(f"\nDirectories processed: {self.stats['directories_processed']}")
        logger.info(f"Shim chains found: {total_chains}")
        logger.info(f"Shim chains cleaned: {total_cleaned}")
        logger.info(f"Shim files deleted: {self.stats['shim_files_deleted']}")
        logger.info(f"Files updated: {self.stats['files_updated']}")

        if self.stats["errors"]:
            logger.info(f"\nErrors encountered: {len(self.stats['errors'])}")
            for error in self.stats["errors"][:5]:  # Show first 5
                logger.info(f"  - {error}")
            if len(self.stats["errors"]) > 5:
                logger.info(f"  ... and {len(self.stats['errors']) - 5} more")

        # Show per-directory details
        logger.info("\nPer-directory details:")
        for dir_name, result in results.items():
            if result["chains_found"] > 0:
                logger.info(f"  {dir_name}:")
                logger.info(f"    Chains: {result['chains_found']} found, {result['chains_cleaned']} cleaned")

        logger.info("\n" + "=" * 80)

def main():
    """Main entry point."""
    repo_root = Path(__file__).parent.parent
    cleaner = RepositoryCleaner(repo_root)

    # Run cleanup
    results = cleaner.clean_all()

    logger.info("\nCleanup complete!")

if __name__ == "__main__":
    main()
